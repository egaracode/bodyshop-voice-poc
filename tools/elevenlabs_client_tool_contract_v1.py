#!/usr/bin/env python3
"""ElevenLabs confirmed-intake Client Tool contract V1.

Repository-side contract and GET-only access probe for BODYSHOP Voice.
No provider mutation methods exist in the network client.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
TOOL_NAME = "bodyshop_resolve_confirmed_intake"
SOURCE_CHANNEL = "ELEVENLABS_WEB"
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")

REQUIRED_TOOL_FIELDS = (
    "workshop",
    "model",
    "installation",
    "operation",
    "device",
    "description",
    "line_stopped",
)
OPTIONAL_TOOL_FIELDS = ("subdevice",)
ALLOWED_TOOL_FIELDS = set(REQUIRED_TOOL_FIELDS + OPTIONAL_TOOL_FIELDS)
RESULT_STATUSES = {"RESOLVED", "INCOMPLETE", "AMBIGUOUS", "NOT_FOUND", "INVALID"}
FAILURE_STATUSES = RESULT_STATUSES - {"RESOLVED"}
MISSING_FIELDS = {
    "workshop",
    "model",
    "installation",
    "operation",
    "device",
    "subdevice",
    "description",
}

ISOLATED_BRANCH_NAME = "bodyshop-client-tool-issue-36"
ISOLATED_BRANCH_DESCRIPTION = "BODYSHOP #36 isolated Client Tool staging"


class ContractError(RuntimeError):
    pass


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_id_fingerprint(value: Any) -> str | None:
    return sha256_text(value) if isinstance(value, str) and value else None


def safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise ContractError(f"Invalid {label}")
    return urllib.parse.quote(value, safe="")


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"Unable to load JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("JSON root must be an object")
    return value


def _require_nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value.strip()


def validate_tool_create_payload(payload: dict[str, Any]) -> None:
    if set(payload) != {"tool_config"} or not isinstance(payload["tool_config"], dict):
        raise ContractError("Tool payload must contain exactly tool_config")

    cfg = payload["tool_config"]
    if cfg.get("type") != "client":
        raise ContractError("Client Tool type must be client")
    if cfg.get("name") != TOOL_NAME:
        raise ContractError(f"Client Tool name must be {TOOL_NAME!r}")
    _require_nonempty_text(cfg.get("description"), "tool_config.description")
    if cfg.get("expects_response") is not True:
        raise ContractError("Client Tool must wait for and return a response")

    parameters = cfg.get("parameters")
    if not isinstance(parameters, dict) or parameters.get("type") != "object":
        raise ContractError("Client Tool parameters must be an object schema")
    _require_nonempty_text(parameters.get("description"), "parameters.description")

    required = parameters.get("required")
    if required != list(REQUIRED_TOOL_FIELDS):
        raise ContractError("Client Tool required parameter order/set changed")

    properties = parameters.get("properties")
    if not isinstance(properties, dict) or set(properties) != ALLOWED_TOOL_FIELDS:
        raise ContractError("Client Tool property set changed")

    for field in REQUIRED_TOOL_FIELDS:
        node = properties.get(field)
        if not isinstance(node, dict):
            raise ContractError(f"Missing schema for {field}")
        expected_type = "boolean" if field == "line_stopped" else "string"
        if node.get("type") != expected_type:
            raise ContractError(f"{field} must use JSON type {expected_type}")
        _require_nonempty_text(node.get("description"), f"{field}.description")

    subdevice = properties.get("subdevice")
    if not isinstance(subdevice, dict) or subdevice.get("type") != "string":
        raise ContractError("subdevice must be an optional string")
    _require_nonempty_text(subdevice.get("description"), "subdevice.description")


def build_voice_observation(
    parameters: dict[str, Any],
    *,
    observation_id: str,
    timestamp: str,
) -> dict[str, Any]:
    if not isinstance(parameters, dict):
        raise ContractError("Tool parameters must be an object")
    unknown = set(parameters) - ALLOWED_TOOL_FIELDS
    if unknown:
        raise ContractError(f"Unexpected tool parameters: {sorted(unknown)}")

    values: dict[str, Any] = {}
    for field in REQUIRED_TOOL_FIELDS:
        if field not in parameters:
            raise ContractError(f"Missing required tool parameter {field}")
        if field == "line_stopped":
            if type(parameters[field]) is not bool:
                raise ContractError("line_stopped must be boolean")
            values[field] = parameters[field]
        else:
            values[field] = _require_nonempty_text(parameters[field], field)

    subdevice = parameters.get("subdevice")
    if subdevice is None:
        values["subdevice"] = None
    elif isinstance(subdevice, str):
        values["subdevice"] = subdevice.strip() or None
    else:
        raise ContractError("subdevice must be a string when supplied")

    oid = _require_nonempty_text(observation_id, "observation_id")
    ts = _require_nonempty_text(timestamp, "timestamp")

    return {
        "observation_id": oid,
        "source_channel": SOURCE_CHANNEL,
        "occurred_at": ts,
        "recorded_at": ts,
        "confirmed_at": ts,
        "workshop": values["workshop"],
        "model": values["model"],
        "installation": values["installation"],
        "operation": values["operation"],
        "device": values["device"],
        "subdevice": values["subdevice"],
        "description": values["description"],
        "line_stopped": values["line_stopped"],
    }


def _safe_canonical_context(context: Any) -> dict[str, Any]:
    if not isinstance(context, dict):
        raise ContractError("RESOLVED result requires canonical_context")

    def code_name(field: str) -> dict[str, str]:
        node = context.get(field)
        if not isinstance(node, dict):
            raise ContractError(f"canonical_context.{field} must be an object")
        return {
            "code": _require_nonempty_text(node.get("code"), f"{field}.code"),
            "name": _require_nonempty_text(node.get("name"), f"{field}.name"),
        }

    def named(field: str) -> dict[str, str] | None:
        node = context.get(field)
        if node is None:
            return None
        if not isinstance(node, dict):
            raise ContractError(f"canonical_context.{field} must be object or null")
        return {"name": _require_nonempty_text(node.get("name"), f"{field}.name")}

    return {
        "workshop": code_name("workshop"),
        "model": code_name("model"),
        "installation": code_name("installation"),
        "operation": code_name("operation"),
        "device": named("device"),
        "subdevice": named("subdevice"),
    }


def to_agent_safe_result(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ContractError("BODYSHOP result must be an object")
    status = result.get("status")
    if status not in RESULT_STATUSES:
        raise ContractError("BODYSHOP result has unsupported status")

    if status == "RESOLVED":
        _require_nonempty_text(result.get("reference_path_id"), "reference_path_id")
        return {
            "status": "RESOLVED",
            "canonical_context": _safe_canonical_context(result.get("canonical_context")),
        }

    reason = _require_nonempty_text(result.get("reason"), "reason")
    safe: dict[str, Any] = {"status": status, "reason": reason}

    missing = result.get("missing_fields")
    if missing is not None:
        if (
            not isinstance(missing, list)
            or any(not isinstance(item, str) or item not in MISSING_FIELDS for item in missing)
        ):
            raise ContractError("missing_fields contains unsupported values")
        safe["missing_fields"] = list(missing)

    candidate_count = result.get("candidate_count")
    if candidate_count is not None:
        if type(candidate_count) is not int or candidate_count < 0:
            raise ContractError("candidate_count must be a non-negative integer")
        safe["candidate_count"] = candidate_count

    return safe


@dataclass
class ApiClient:
    api_key: str
    base_url: str = API_BASE

    def _get(self, path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
        q = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}" + (f"?{q}" if q else "")
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "accept": "application/json",
                "xi-api-key": self.api_key,
                "user-agent": "bodyshop-voice-poc-client-tool-contract-v1/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise ContractError(f"ElevenLabs GET failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ContractError("ElevenLabs GET failed due to a network error") from exc
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ContractError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise ContractError("ElevenLabs returned an unexpected non-object response")
        return parsed

    def list_agents(self, name: str, cursor: str | None = None) -> dict[str, Any]:
        query = {"page_size": "100", "search": name, "archived": "false"}
        if cursor:
            query["cursor"] = cursor
        return self._get("/v1/convai/agents", query)

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        return self._get(f"/v1/convai/agents/{safe_identifier(agent_id, 'agent_id')}")


def find_exact_agent(client: ApiClient, name: str) -> dict[str, Any]:
    cursor = None
    matches: list[dict[str, Any]] = []
    while True:
        page = client.list_agents(name, cursor)
        agents = page.get("agents", [])
        if not isinstance(agents, list):
            raise ContractError("Agent listing omitted agents")
        matches.extend(
            item
            for item in agents
            if isinstance(item, dict)
            and item.get("name") == name
            and not item.get("archived", False)
        )
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
        if not isinstance(cursor, str) or not cursor:
            raise ContractError("Agent pagination omitted next_cursor")
    if len(matches) != 1:
        raise ContractError(
            f"Expected exactly one non-archived agent named {name!r}; found {len(matches)}"
        )
    return matches[0]


def collect_agent_access_snapshot(client: ApiClient, agent_name: str) -> dict[str, Any]:
    listed = find_exact_agent(client, agent_name)
    agent_id = _require_nonempty_text(listed.get("agent_id"), "agent_id")
    agent = client.get_agent(agent_id)

    platform = agent.get("platform_settings")
    if not isinstance(platform, dict):
        raise ContractError("Agent platform_settings unavailable")
    auth = platform.get("auth")
    if not isinstance(auth, dict) or type(auth.get("enable_auth")) is not bool:
        raise ContractError("Agent auth.enable_auth unavailable")

    cfg = agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise ContractError("Agent conversation_config unavailable")
    prompt = cfg.get("agent", {}).get("prompt", {})
    if not isinstance(prompt, dict):
        raise ContractError("Agent prompt configuration unavailable")
    tool_ids = prompt.get("tool_ids", [])
    if tool_ids is None:
        tool_ids = []
    if not isinstance(tool_ids, list) or any(
        not isinstance(item, str) or not item for item in tool_ids
    ):
        raise ContractError("Agent tool_ids is malformed")

    enable_auth = auth["enable_auth"]
    allowlist = auth.get("allowlist", [])
    if allowlist is None:
        allowlist = []
    if not isinstance(allowlist, list):
        raise ContractError("Agent auth allowlist is malformed")

    return {
        "safe": {
            "agent_name": agent.get("name"),
            "agent_id_sha256": safe_id_fingerprint(agent_id),
            "branch_id_sha256": safe_id_fingerprint(agent.get("branch_id")),
            "version_id_sha256": safe_id_fingerprint(agent.get("version_id")),
            "main_branch_id_sha256": safe_id_fingerprint(agent.get("main_branch_id")),
            "auth_enable_auth": enable_auth,
            "connection_classification": (
                "SIGNED_URL_REQUIRED" if enable_auth else "PUBLIC_AGENT_ID_ALLOWED"
            ),
            "auth_allowlist_count": len(allowlist),
            "auth_require_origin_header": auth.get("require_origin_header"),
            "current_tool_count": len(tool_ids),
            "current_tool_id_sha256": sorted(sha256_text(item) for item in tool_ids),
        },
        "raw": {
            "agent_id": agent_id,
            "branch_id": agent.get("branch_id"),
            "version_id": agent.get("version_id"),
            "main_branch_id": agent.get("main_branch_id"),
            "tool_ids": list(tool_ids),
        },
    }


def build_sanitized_write_set(
    access: dict[str, Any], tool_payload: dict[str, Any]
) -> dict[str, Any]:
    validate_tool_create_payload(tool_payload)
    safe = access.get("safe")
    raw = access.get("raw")
    if not isinstance(safe, dict) or not isinstance(raw, dict):
        raise ContractError("Access snapshot malformed")

    version_id = raw.get("version_id")
    main_branch_id = raw.get("main_branch_id")
    if not isinstance(version_id, str) or not version_id:
        raise ContractError("Current agent version_id unavailable")
    if not isinstance(main_branch_id, str) or not main_branch_id:
        raise ContractError("Current agent main_branch_id unavailable")

    return {
        "schema_version": 1,
        "mode": "GET_ONLY_CLIENT_TOOL_WRITE_SET_PLAN",
        "provider": "ElevenLabs",
        "agent_access": safe,
        "client_tool_contract": {
            "name": TOOL_NAME,
            "create_payload": tool_payload,
            "provider_supplied_fields": list(REQUIRED_TOOL_FIELDS + OPTIONAL_TOOL_FIELDS),
            "client_owned_provenance": [
                "observation_id",
                "source_channel",
                "occurred_at",
                "recorded_at",
                "confirmed_at",
            ],
            "agent_result_excludes": [
                "reference_path_id",
                "canonical object ids",
                "provider ids",
                "secrets",
            ],
        },
        "operator_contract_gap": {
            "gate1_requires_complete_readback_confirmation": True,
            "gate1_requires_line_stopped": True,
            "current_a5_expected_operator_procedure_collects_line_stopped": False,
            "current_a5_expected_operator_procedure_explicitly_requires_complete_readback_confirmation": False,
            "classification": "EXPECTED_STATE_DECISION_REQUIRED",
        },
        "planned_provider_operations": [
            {
                "order": 1,
                "method": "POST",
                "path": "/v1/convai/agents/{agent_id}/branches",
                "body_safe": {
                    "name": ISOLATED_BRANCH_NAME,
                    "description": ISOLATED_BRANCH_DESCRIPTION,
                    "parent_version_id_sha256": sha256_text(version_id),
                },
                "approval_gate": "SEPARATE_PROVIDER_STAGING_WRITE_APPROVAL_REQUIRED",
            },
            {
                "order": 2,
                "method": "GET",
                "path": "/v1/convai/agents/{agent_id}/branches/{branch_id}",
                "expected_safe": {
                    "name": ISOLATED_BRANCH_NAME,
                    "parent_branch_id_sha256": sha256_text(main_branch_id),
                    "current_live_percentage": 0,
                },
            },
            {
                "order": 3,
                "method": "POST",
                "path": "/v1/convai/tools",
                "body_safe": tool_payload,
                "approval_gate": "SEPARATE_PROVIDER_STAGING_WRITE_APPROVAL_REQUIRED",
            },
            {
                "order": 4,
                "method": "GET",
                "path": "/v1/convai/tools/{new_tool_id}",
                "expected_safe": {
                    "type": "client",
                    "name": TOOL_NAME,
                    "expects_response": True,
                },
            },
            {
                "order": 5,
                "method": "PATCH",
                "path": "/v1/convai/agents/{agent_id}",
                "query_safe": {"branch": ISOLATED_BRANCH_NAME},
                "body_safe": {
                    "conversation_config": {
                        "agent": {
                            "prompt": {
                                "tool_ids": {
                                    "retain_existing_id_sha256": safe.get(
                                        "current_tool_id_sha256", []
                                    ),
                                    "append": "PENDING_NEW_TOOL_ID_AFTER_CREATE",
                                }
                            }
                        }
                    }
                },
                "approval_gate": "SEPARATE_PROVIDER_STAGING_WRITE_APPROVAL_REQUIRED",
            },
            {
                "order": 6,
                "method": "BLOCKED_DECISION",
                "reason": (
                    "Gate 1 requires line_stopped plus complete read-back confirmation, "
                    "while the current A5 expected Operator breakdown contract does not. "
                    "Do not change provider behavior until Albert accepts the expected-state delta."
                ),
                "approval_gate": "EXPECTED_STATE_DECISION_REQUIRED",
            },
        ],
        "prohibited": [
            "provider write during this Issue",
            "provider Main merge",
            "force merge",
            "Supabase / Edge Function",
            "SQL / RLS / RPC / Auth",
            "Production",
            "lifecycle mutation",
            "secret in output",
        ],
        "next_gate": "STOP_FOR_EXPECTED_STATE_AND_PROVIDER_WRITE_DECISIONS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--agent-name", default="AI Control")
    args = parser.parse_args(argv)

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        payload = load_json(args.tool_config)
        validate_tool_create_payload(payload)
        access = collect_agent_access_snapshot(ApiClient(key), args.agent_name)
        plan = build_sanitized_write_set(access, payload)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(plan, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (ContractError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
