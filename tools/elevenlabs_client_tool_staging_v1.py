#!/usr/bin/env python3
"""BODYSHOP #38 — isolated ElevenLabs Client Tool + operator staging V1.

Authorized scope:
- exact current Main read guard;
- create one zero-live isolated branch;
- create one workspace Client Tool;
- update the inherited Operator breakdown Procedure draft on the isolated branch;
- attach the tool and publish the isolated branch;
- exact GET readback;
- prove Main agent configuration stayed unchanged.

This tool has no provider branch merge operation and cannot touch Production or BODYSHOP.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from elevenlabs_client_tool_contract_v1 import (
    TOOL_NAME,
    validate_tool_create_payload,
)

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")

ISSUE = 38
AGENT_NAME = "AI Control"
STAGING_BRANCH_NAME = "bodyshop-client-tool-issue-38"
STAGING_DESCRIPTION = "BODYSHOP #38 isolated Client Tool + operator contract staging"
TOOL_ATTACH_VERSION_DESCRIPTION = "BODYSHOP #38 attach confirmed-intake Client Tool on isolated branch"\nOPERATOR_VERSION_DESCRIPTION = "BODYSHOP #38 publish aligned Operator breakdown on isolated branch"

BASELINE = {
    "agent_id_sha256": "b9849ffbf0f27a2f16dca71dcf8adce41c0f7e6d09c27a9934fcdf7747d3789d",
    "main_branch_id_sha256": "a15d1399a8e6bc5c778fffe2dc9587f2dc1bef57ed4b856d56e878640f40b3e5",
    "version_id_sha256": "5e2b5d563b06570f3e186dceb56e55075794e07d85ed8d5893668b0ad5c0a212",
    "system_prompt_sha256": "7e53fa089edbe9ae5da4af97e1f2fbb36833fffa504eb033d710b107d89972f2",
    "system_prompt_length": 2305,
    "voice_id_sha256": "1e0c5d7793b1296cb88ddddf08040c9e901c241640ff7e88fcad1c31c7392bc9",
    "language": "es",
    "llm_id": "qwen35-397b-a17b",
    "dynamic_variable_names": [
        "activation_verified",
        "active_breakdown_count",
        "breakdown_ref",
        "caller_role",
        "channel_mode",
        "flow_stage",
        "known_identity",
        "known_installation",
        "known_model",
        "known_operation",
    ],
    "operator": {
        "name": "Operator breakdown",
        "raw_api_type": "deterministic",
        "trigger_sha256": "92006c2f29cbba1efa4df86c8cf5b18093c9f43139b96904d4baa1b9354ed380",
        "trigger_length": 108,
        "content_sha256": "f0370537fa7e74e286405a0dd38a551bea4882f8410f1f262973822200d7e791",
        "content_length": 1753,
    },
    "technician": {
        "name": "Technician pre-close",
        "raw_api_type": "free_form",
        "trigger_sha256": "36e9ff5743d2c980808909bf745f93a8be0dbfa43c70d0c64758c602fd963778",
        "trigger_length": 93,
        "content_sha256": "c8238704959494ea15c8e7897cd4b18420b23b99a56a8ad4236662f1f180fae2",
        "content_length": 588,
    },
}


class StagingError(RuntimeError):
    pass


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_id_fingerprint(value: Any) -> str | None:
    return sha256_text(value) if isinstance(value, str) and value else None


def safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise StagingError(f"Invalid {label}")
    return urllib.parse.quote(value, safe="")


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise StagingError(f"Expected text, got {type(value).__name__}")
    return value.replace("\r\n", "\n").replace("\r", "\n")


def load_object(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StagingError(f"Unable to load JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise StagingError("JSON root must be an object")
    return value


def dynamic_variable_names(agent: dict[str, Any]) -> list[str] | None:
    node = (
        agent.get("conversation_config", {})
        .get("agent", {})
        .get("dynamic_variables", {})
        .get("dynamic_variable_placeholders")
    )
    if node is None:
        return None
    if not isinstance(node, dict):
        raise StagingError("dynamic_variable_placeholders is not an object")
    return sorted(str(key) for key in node)


def semantic_procedure_fingerprint(item: dict[str, Any]) -> dict[str, Any]:
    name = item.get("name")
    raw_type = item.get("type")
    trigger = normalize_text(item.get("trigger", "")) or ""
    content = normalize_text(item.get("content"))
    if content is None:
        raise StagingError("Procedure content is missing")

    if raw_type == "deterministic":
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise StagingError("Deterministic Procedure content is not JSON") from exc
        if not isinstance(parsed, dict) or not isinstance(parsed.get("steps"), list):
            raise StagingError("Deterministic Procedure content has no steps")
        parsed = dict(parsed)
        # Provider may duplicate the trigger into deterministic content.
        parsed.pop("trigger", None)
        canonical_content = canonical_json(parsed)
    else:
        canonical_content = content

    return {
        "name": name,
        "raw_api_type": raw_type,
        "trigger_sha256": sha256_text(trigger),
        "trigger_length": len(trigger),
        "content_sha256": sha256_text(canonical_content),
        "content_length": len(canonical_content),
        "version_present": bool(item.get("version_id")),
    }


class ProviderClient:
    """Narrow ElevenLabs client. Only GET/POST/PATCH exist in this block."""

    def __init__(self, api_key: str, base_url: str = API_BASE):
        self.api_key = api_key
        self.base_url = base_url

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if method not in {"GET", "POST", "PATCH"}:
            raise StagingError(f"Unsupported method {method}")
        qs = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}" + (f"?{qs}" if qs else "")
        data = None
        headers = {
            "accept": "application/json",
            "xi-api-key": self.api_key,
            "user-agent": "bodyshop-voice-poc-issue38-staging-v1/1",
        }
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["content-type"] = "application/json"
        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise StagingError(f"ElevenLabs {method} failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise StagingError(f"ElevenLabs {method} failed due to a network error") from exc
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise StagingError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise StagingError("ElevenLabs returned an unexpected non-object response")
        return parsed

    def get(self, path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
        return self._request("GET", path, query=query)

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, body=body)

    def patch(
        self,
        path: str,
        body: dict[str, Any],
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self._request("PATCH", path, body=body, query=query)

    def list_agents(self, name: str, cursor: str | None = None) -> dict[str, Any]:
        query = {"page_size": "100", "search": name, "archived": "false"}
        if cursor:
            query["cursor"] = cursor
        return self.get("/v1/convai/agents", query)

    def get_agent(self, agent_id: str, branch_id: str | None = None) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        query = {"branch_id": branch_id} if branch_id else None
        return self.get(f"/v1/convai/agents/{aid}", query)

    def list_branches(self, agent_id: str, include_archived: bool = False) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        return self.get(
            f"/v1/convai/agents/{aid}/branches",
            {
                "include_archived": "true" if include_archived else "false",
                "include_commit_status": "true",
                "limit": "100",
            },
        )

    def get_branch(self, agent_id: str, branch_id: str) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        return self.get(f"/v1/convai/agents/{aid}/branches/{bid}")

    def list_procedures(self, agent_id: str, branch_id: str) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        return self.get(f"/v1/convai/agents/{aid}/branches/{bid}/procedures")

    def get_procedure(
        self, agent_id: str, branch_id: str, procedure_id: str
    ) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        pid = safe_identifier(procedure_id, "procedure_id")
        return self.get(
            f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}"
        )

    def list_tools(self, search: str, cursor: str | None = None) -> dict[str, Any]:
        query = {
            "page_size": "100",
            "search": search,
            "sort_by": "name",
            "sort_direction": "asc",
        }
        if cursor:
            query["cursor"] = cursor
        return self.get("/v1/convai/tools", query)

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        tid = safe_identifier(tool_id, "tool_id")
        return self.get(f"/v1/convai/tools/{tid}")


def find_exact_agent(client: ProviderClient) -> dict[str, Any]:
    cursor = None
    matches: list[dict[str, Any]] = []
    while True:
        page = client.list_agents(AGENT_NAME, cursor)
        agents = page.get("agents", [])
        if not isinstance(agents, list):
            raise StagingError("Agent listing omitted agents")
        matches.extend(
            item
            for item in agents
            if isinstance(item, dict)
            and item.get("name") == AGENT_NAME
            and not item.get("archived", False)
        )
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
        if not isinstance(cursor, str) or not cursor:
            raise StagingError("Agent pagination omitted next_cursor")
    if len(matches) != 1:
        raise StagingError(
            f"Expected exactly one non-archived agent named {AGENT_NAME!r}; found {len(matches)}"
        )
    return matches[0]


def _effective_procedure_rows(
    client: ProviderClient,
    agent: dict[str, Any],
    branch_id: str,
) -> dict[str, dict[str, Any]]:
    effective = agent.get("procedures")
    if not isinstance(effective, dict) or len(effective) != 2:
        raise StagingError("Effective Procedure map must contain exactly two Procedures")

    rows: dict[str, dict[str, Any]] = {}
    for pid, meta in effective.items():
        if not isinstance(pid, str) or not pid or not isinstance(meta, dict):
            raise StagingError("Effective Procedure map is malformed")
        row = client.get_procedure(agent["agent_id"], branch_id, pid)
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise StagingError("Effective Procedure omitted name")
        if name in rows:
            raise StagingError(f"Duplicate effective Procedure name {name!r}")
        rows[name] = row
    if set(rows) != {"Operator breakdown", "Technician pre-close"}:
        raise StagingError("Effective Procedure names changed")
    return rows


def assert_main_baseline(client: ProviderClient) -> dict[str, Any]:
    listed = find_exact_agent(client)
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise StagingError("Matched agent omitted agent_id")
    if sha256_text(agent_id) != BASELINE["agent_id_sha256"]:
        raise StagingError("Agent identity fingerprint moved")

    agent = client.get_agent(agent_id)
    branch_id = agent.get("branch_id")
    main_branch_id = agent.get("main_branch_id")
    version_id = agent.get("version_id")
    for label, value in (
        ("branch_id", branch_id),
        ("main_branch_id", main_branch_id),
        ("version_id", version_id),
    ):
        if not isinstance(value, str) or not value:
            raise StagingError(f"Provider omitted {label}")
    if branch_id != main_branch_id:
        raise StagingError("Current provider branch is not Main")
    if sha256_text(main_branch_id) != BASELINE["main_branch_id_sha256"]:
        raise StagingError("Main branch fingerprint moved")
    if sha256_text(version_id) != BASELINE["version_id_sha256"]:
        raise StagingError("Main version fingerprint moved")

    cfg = agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise StagingError("Main conversation_config is malformed")
    acfg = cfg.get("agent")
    tts = cfg.get("tts")
    if not isinstance(acfg, dict) or not isinstance(tts, dict):
        raise StagingError("Main agent/tts config is malformed")
    pcfg = acfg.get("prompt")
    if not isinstance(pcfg, dict):
        raise StagingError("Main prompt config is malformed")

    prompt = normalize_text(pcfg.get("prompt"))
    if not isinstance(prompt, str):
        raise StagingError("Main System Prompt is missing")
    if sha256_text(prompt) != BASELINE["system_prompt_sha256"]:
        raise StagingError("Main System Prompt fingerprint moved")
    if len(prompt) != BASELINE["system_prompt_length"]:
        raise StagingError("Main System Prompt length moved")
    if acfg.get("language") != BASELINE["language"]:
        raise StagingError("Main language moved")
    if pcfg.get("llm") != BASELINE["llm_id"]:
        raise StagingError("Main LLM moved")
    if dynamic_variable_names(agent) != BASELINE["dynamic_variable_names"]:
        raise StagingError("Main dynamic-variable set moved")

    voice_id = tts.get("voice_id")
    if safe_id_fingerprint(voice_id) != BASELINE["voice_id_sha256"]:
        raise StagingError("Main voice fingerprint moved")

    tool_ids = pcfg.get("tool_ids", [])
    if tool_ids is None:
        tool_ids = []
    if tool_ids != []:
        raise StagingError("Main tool_ids must still be empty")

    platform = agent.get("platform_settings")
    if not isinstance(platform, dict):
        raise StagingError("Main platform_settings unavailable")
    auth = platform.get("auth")
    if not isinstance(auth, dict) or auth.get("enable_auth") is not False:
        raise StagingError("Main auth classification moved from public")

    branches = client.list_branches(agent_id, include_archived=False).get("results", [])
    if not isinstance(branches, list):
        raise StagingError("Main branch listing omitted results")
    current = [b for b in branches if isinstance(b, dict) and b.get("id") == main_branch_id]
    if len(current) != 1:
        raise StagingError("Main branch not found exactly once")
    main_meta = current[0]
    if main_meta.get("name") != "Main":
        raise StagingError("Main branch name moved")
    if bool(main_meta.get("is_archived", False)):
        raise StagingError("Main branch is archived")
    if bool(main_meta.get("draft_exists", False)):
        raise StagingError("Main branch unexpectedly has a draft")
    if main_meta.get("commits_ahead") not in (0, None):
        raise StagingError("Main branch unexpectedly has commits_ahead")
    if main_meta.get("commits_behind") not in (0, None):
        raise StagingError("Main branch unexpectedly has commits_behind")

    rows = _effective_procedure_rows(client, agent, main_branch_id)
    operator_fp = semantic_procedure_fingerprint(rows["Operator breakdown"])
    technician_fp = semantic_procedure_fingerprint(rows["Technician pre-close"])
    for actual, key in ((operator_fp, "operator"), (technician_fp, "technician")):
        expected = dict(BASELINE[key])
        expected["version_present"] = True
        if actual != expected:
            raise StagingError(f"Main {key} Procedure fingerprint moved")

    return {
        "raw": {
            "agent_id": agent_id,
            "main_branch_id": main_branch_id,
            "version_id": version_id,
            "operator_procedure_id": rows["Operator breakdown"].get("procedure_id"),
            "technician_procedure_id": rows["Technician pre-close"].get("procedure_id"),
        },
        "safe": {
            "agent_id_sha256": sha256_text(agent_id),
            "main_branch_id_sha256": sha256_text(main_branch_id),
            "version_id_sha256": sha256_text(version_id),
            "system_prompt_sha256": sha256_text(prompt),
            "voice_id_sha256": safe_id_fingerprint(voice_id),
            "tool_count": 0,
            "auth_enable_auth": False,
            "operator": operator_fp,
            "technician": technician_fp,
        },
    }


def ensure_branch_name_available(client: ProviderClient, agent_id: str) -> None:
    results = client.list_branches(agent_id, include_archived=True).get("results", [])
    if not isinstance(results, list):
        raise StagingError("Branch listing omitted results")
    if any(
        isinstance(item, dict) and item.get("name") == STAGING_BRANCH_NAME
        for item in results
    ):
        raise StagingError(f"Provider branch name {STAGING_BRANCH_NAME!r} already exists")


def ensure_tool_name_available(client: ProviderClient) -> None:
    cursor = None
    matches = 0
    while True:
        page = client.list_tools(TOOL_NAME, cursor)
        tools = page.get("tools", [])
        if not isinstance(tools, list):
            raise StagingError("Tool listing omitted tools")
        matches += sum(
            1
            for item in tools
            if isinstance(item, dict)
            and isinstance(item.get("tool_config"), dict)
            and item["tool_config"].get("name") == TOOL_NAME
        )
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
        if not isinstance(cursor, str) or not cursor:
            raise StagingError("Tool pagination omitted next_cursor")
    if matches:
        raise StagingError(f"Workspace already contains {matches} tool(s) named {TOOL_NAME!r}")


def validate_expected_state(expected: dict[str, Any]) -> None:
    if expected.get("schema_version") != 1:
        raise StagingError("Expected-state schema_version must be 1")
    authority = expected.get("authority")
    if not isinstance(authority, dict) or authority.get("issue") != ISSUE:
        raise StagingError("Expected-state authority is not Issue #38")
    tool = expected.get("client_tool")
    if not isinstance(tool, dict):
        raise StagingError("Expected-state client_tool is missing")
    if tool.get("name") != TOOL_NAME or tool.get("expects_response") is not True:
        raise StagingError("Expected-state Client Tool identity changed")
    proc = expected.get("operator_procedure")
    if not isinstance(proc, dict):
        raise StagingError("Expected operator Procedure is missing")
    if proc.get("name") != "Operator breakdown" or proc.get("type") != "deterministic":
        raise StagingError("Expected operator Procedure identity/type changed")
    content = proc.get("content_template")
    if not isinstance(content, dict) or not isinstance(content.get("steps"), list):
        raise StagingError("Expected operator content_template is malformed")
    tool_refs = [
        step.get("tool_ref")
        for step in content["steps"]
        if isinstance(step, dict) and step.get("type") == "tool_call"
    ]
    if tool_refs != [TOOL_NAME]:
        raise StagingError("Expected operator must contain exactly one symbolic Client Tool call")


def materialize_operator(expected: dict[str, Any], tool_id: str) -> dict[str, Any]:
    validate_expected_state(expected)
    tid = safe_identifier(tool_id, "tool_id")
    if not tid:
        raise StagingError("Tool id is empty")

    proc = expected["operator_procedure"]
    content = copy.deepcopy(proc["content_template"])
    calls = 0
    for step in content["steps"]:
        if not isinstance(step, dict):
            raise StagingError("Operator step is not an object")
        if step.get("type") == "tool_call":
            if step.get("tool_ref") != TOOL_NAME:
                raise StagingError("Unexpected symbolic tool_ref")
            step.pop("tool_ref", None)
            step["tool_id"] = tool_id
            step["tool_name"] = TOOL_NAME
            calls += 1
    if calls != 1:
        raise StagingError("Materialized operator must contain exactly one Client Tool call")

    return {
        "name": proc["name"],
        "type": proc["type"],
        "trigger": proc["trigger"],
        "content": canonical_json(content),
    }


def verify_tool_contract(actual: dict[str, Any], expected_payload: dict[str, Any]) -> None:
    actual_cfg = actual.get("tool_config")
    expected_cfg = expected_payload.get("tool_config")
    if not isinstance(actual_cfg, dict) or not isinstance(expected_cfg, dict):
        raise StagingError("Tool config readback is malformed")
    for field in ("type", "name", "description", "expects_response"):
        if actual_cfg.get(field) != expected_cfg.get(field):
            raise StagingError(f"Tool readback mismatch for {field}")
    if actual_cfg.get("parameters") != expected_cfg.get("parameters"):
        raise StagingError("Tool parameter schema readback mismatch")


def _branch_parent_id(branch: dict[str, Any]) -> str | None:
    parent = branch.get("parent_branch")
    if isinstance(parent, dict) and isinstance(parent.get("id"), str):
        return parent["id"]
    value = branch.get("parent_branch_id")
    return value if isinstance(value, str) else None


def verify_isolated_branch(
    branch: dict[str, Any],
    *,
    main_branch_id: str,
) -> None:
    if branch.get("name") != STAGING_BRANCH_NAME:
        raise StagingError("Isolated branch name mismatch")
    if branch.get("description") != STAGING_DESCRIPTION:
        raise StagingError("Isolated branch description mismatch")
    if _branch_parent_id(branch) != main_branch_id:
        raise StagingError("Isolated branch parent does not match Main")
    if branch.get("current_live_percentage") not in (0, 0.0):
        raise StagingError("Isolated branch unexpectedly has live traffic")
    if bool(branch.get("is_archived", False)):
        raise StagingError("Isolated branch is archived")


def _procedure_by_name(
    client: ProviderClient,
    branch_agent: dict[str, Any],
    branch_id: str,
    name: str,
) -> dict[str, Any]:
    effective = branch_agent.get("procedures")
    if not isinstance(effective, dict):
        raise StagingError("Branch effective Procedure map is malformed")
    matches = [
        pid
        for pid, meta in effective.items()
        if isinstance(pid, str)
        and isinstance(meta, dict)
        and meta.get("name") == name
    ]
    if len(matches) != 1:
        raise StagingError(f"Expected exactly one effective Procedure named {name!r}")
    return client.get_procedure(branch_agent["agent_id"], branch_id, matches[0])


def verify_isolated_final(
    client: ProviderClient,
    *,
    agent_id: str,
    branch_id: str,
    tool_id: str,
    tool_payload: dict[str, Any],
    expected: dict[str, Any],
    baseline_technician: dict[str, Any],
) -> dict[str, Any]:
    branch = client.get_branch(agent_id, branch_id)
    verify_isolated_branch(branch, main_branch_id=client.get_agent(agent_id)["main_branch_id"])
    if bool(branch.get("draft_exists", False)):
        raise StagingError("Isolated branch still has a Procedure draft after publish")

    agent = client.get_agent(agent_id, branch_id)
    cfg = agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise StagingError("Isolated final conversation_config is malformed")
    acfg = cfg.get("agent")
    tts = cfg.get("tts")
    if not isinstance(acfg, dict) or not isinstance(tts, dict):
        raise StagingError("Isolated final agent/tts config is malformed")
    pcfg = acfg.get("prompt")
    if not isinstance(pcfg, dict):
        raise StagingError("Isolated final prompt config is malformed")

    prompt = normalize_text(pcfg.get("prompt"))
    if not isinstance(prompt, str):
        raise StagingError("Isolated final System Prompt missing")
    if sha256_text(prompt) != BASELINE["system_prompt_sha256"]:
        raise StagingError("Isolated staging unexpectedly changed System Prompt")
    if acfg.get("language") != BASELINE["language"]:
        raise StagingError("Isolated staging unexpectedly changed language")
    if pcfg.get("llm") != BASELINE["llm_id"]:
        raise StagingError("Isolated staging unexpectedly changed LLM")
    if dynamic_variable_names(agent) != BASELINE["dynamic_variable_names"]:
        raise StagingError("Isolated staging unexpectedly changed dynamic variables")
    if safe_id_fingerprint(tts.get("voice_id")) != BASELINE["voice_id_sha256"]:
        raise StagingError("Isolated staging unexpectedly changed voice")

    if pcfg.get("tool_ids") != [tool_id]:
        raise StagingError("Isolated final tool_ids does not contain exactly the staged Client Tool")

    effective = agent.get("procedures")
    if not isinstance(effective, dict) or len(effective) != 2:
        raise StagingError("Isolated final effective Procedure count is not exactly two")
    names = sorted(
        meta.get("name")
        for meta in effective.values()
        if isinstance(meta, dict)
    )
    if names != ["Operator breakdown", "Technician pre-close"]:
        raise StagingError("Isolated final effective Procedure names changed unexpectedly")

    operator = _procedure_by_name(client, agent, branch_id, "Operator breakdown")
    technician = _procedure_by_name(client, agent, branch_id, "Technician pre-close")
    materialized = materialize_operator(expected, tool_id)
    expected_operator_item = {
        **materialized,
        "version_id": "expected",
    }
    actual_operator_fp = semantic_procedure_fingerprint(operator)
    wanted_operator_fp = semantic_procedure_fingerprint(expected_operator_item)
    wanted_operator_fp["version_present"] = True
    if actual_operator_fp != wanted_operator_fp:
        raise StagingError("Isolated final Operator breakdown fingerprint mismatch")

    actual_technician_fp = semantic_procedure_fingerprint(technician)
    if actual_technician_fp != baseline_technician:
        raise StagingError("Isolated staging unexpectedly changed Technician pre-close")

    verify_tool_contract(client.get_tool(tool_id), tool_payload)

    version_id = agent.get("version_id")
    if not isinstance(version_id, str) or not version_id:
        raise StagingError("Isolated final version_id is missing")

    return {
        "branch_id_sha256": safe_id_fingerprint(branch_id),
        "version_id_sha256": safe_id_fingerprint(version_id),
        "current_live_percentage": branch.get("current_live_percentage"),
        "tool_id_sha256": safe_id_fingerprint(tool_id),
        "tool_name": TOOL_NAME,
        "tool_attached": True,
        "operator": actual_operator_fp,
        "technician": actual_technician_fp,
    }


def execute_isolated_staging(
    client: ProviderClient,
    expected: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    validate_expected_state(expected)
    validate_tool_create_payload(tool_payload)

    main_before = assert_main_baseline(client)
    raw = main_before["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    version_id = raw["version_id"]

    ensure_branch_name_available(client, agent_id)
    ensure_tool_name_available(client)

    aid = safe_identifier(agent_id, "agent_id")
    created_branch = client.post(
        f"/v1/convai/agents/{aid}/branches",
        {
            "parent_version_id": version_id,
            "name": STAGING_BRANCH_NAME,
            "description": STAGING_DESCRIPTION,
            "include_draft": False,
        },
    )
    branch_id = created_branch.get("created_branch_id")
    if not isinstance(branch_id, str) or not branch_id:
        raise StagingError("Create branch response omitted created_branch_id")

    branch = client.get_branch(agent_id, branch_id)
    verify_isolated_branch(branch, main_branch_id=main_branch_id)

    created_tool = client.post("/v1/convai/tools", tool_payload)
    tool_id = created_tool.get("id")
    if not isinstance(tool_id, str) or not tool_id:
        raise StagingError("Create Tool response omitted id")
    verify_tool_contract(created_tool, tool_payload)
    verify_tool_contract(client.get_tool(tool_id), tool_payload)

    isolated_before = client.get_agent(agent_id, branch_id)
    operator_before = _procedure_by_name(
        client, isolated_before, branch_id, "Operator breakdown"
    )
    technician_before = _procedure_by_name(
        client, isolated_before, branch_id, "Technician pre-close"
    )
    if semantic_procedure_fingerprint(operator_before) != main_before["safe"]["operator"]:
        raise StagingError("Inherited Operator baseline mismatch on isolated branch")
    if semantic_procedure_fingerprint(technician_before) != main_before["safe"]["technician"]:
        raise StagingError("Inherited Technician baseline mismatch on isolated branch")

    operator_pid = operator_before.get("procedure_id")
    if not isinstance(operator_pid, str) or not operator_pid:
        raise StagingError("Inherited Operator breakdown omitted procedure_id")

    # Attach the Client Tool first and verify that isolated branch version.
    branch_agent = client.get_agent(agent_id, branch_id)
    cfg = branch_agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise StagingError("Isolated conversation_config is malformed")
    tool_cfg = copy.deepcopy(cfg)
    agent_cfg = tool_cfg.get("agent")
    if not isinstance(agent_cfg, dict):
        raise StagingError("Isolated conversation_config.agent is malformed")
    prompt_cfg = agent_cfg.get("prompt")
    if not isinstance(prompt_cfg, dict):
        raise StagingError("Isolated prompt config is malformed")
    inherited_tool_ids = prompt_cfg.get("tool_ids", [])
    if inherited_tool_ids is None:
        inherited_tool_ids = []
    if inherited_tool_ids != []:
        raise StagingError("Isolated branch unexpectedly inherited tool ids")
    prompt_cfg["tool_ids"] = [tool_id]

    attached = client.patch(
        f"/v1/convai/agents/{aid}",
        {
            "conversation_config": tool_cfg,
            "version_description": TOOL_ATTACH_VERSION_DESCRIPTION,
        },
        {"branch_id": branch_id},
    )
    attached_version_id = attached.get("version_id")
    if not isinstance(attached_version_id, str) or not attached_version_id:
        raise StagingError("Tool-attach response omitted version_id")
    attached_agent = client.get_agent(agent_id, branch_id)
    attached_prompt = (
        attached_agent.get("conversation_config", {})
        .get("agent", {})
        .get("prompt", {})
    )
    if not isinstance(attached_prompt, dict) or attached_prompt.get("tool_ids") != [tool_id]:
        raise StagingError("Client Tool was not attached exactly before Procedure staging")

    # Only after tool attachment is visible do we create the Procedure draft that references it.
    materialized = materialize_operator(expected, tool_id)
    bid = safe_identifier(branch_id, "branch_id")
    opid = safe_identifier(operator_pid, "operator_procedure_id")
    client.patch(
        f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{opid}/draft",
        materialized,
    )

    published = client.patch(
        f"/v1/convai/agents/{aid}",
        {
            "version_description": OPERATOR_VERSION_DESCRIPTION,
        },
        {"branch_id": branch_id},
    )
    staged_version_id = published.get("version_id")
    if not isinstance(staged_version_id, str) or not staged_version_id:
        raise StagingError("Operator publish response omitted version_id")

    isolated_safe = verify_isolated_final(
        client,
        agent_id=agent_id,
        branch_id=branch_id,
        tool_id=tool_id,
        tool_payload=tool_payload,
        expected=expected,
        baseline_technician=main_before["safe"]["technician"],
    )

    main_after = assert_main_baseline(client)
    if main_after["safe"] != main_before["safe"]:
        raise StagingError("Main safe snapshot changed during isolated staging")

    return {
        "schema_version": 1,
        "mode": "GATE2_CLIENT_TOOL_ISOLATED_STAGING_EXECUTED",
        "provider": "ElevenLabs",
        "issue": ISSUE,
        "source_main": main_before["safe"],
        "isolated_branch": {
            "name": STAGING_BRANCH_NAME,
            "description": STAGING_DESCRIPTION,
            "parent_main_branch_id_sha256": main_before["safe"]["main_branch_id_sha256"],
            **isolated_safe,
        },
        "workspace_tool": {
            "created": True,
            "name": TOOL_NAME,
            "tool_id_sha256": isolated_safe["tool_id_sha256"],
            "config_sha256": sha256_text(canonical_json(tool_payload)),
        },
        "provider_main_agent_modified": False,
        "workspace_tool_created": True,
        "provider_main_merge_performed": False,
        "runtime_risk": expected.get("runtime_risk"),
        "next_gate": "REPOSITORY_READY_DECISION_AND_SEPARATE_PROVIDER_MAIN_MERGE_DECISION_REQUIRED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-isolated-staging", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_isolated_staging:
        print(
            "ERROR: --execute-isolated-staging is required; no provider write performed",
            file=sys.stderr,
        )
        return 2

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        expected = load_object(args.expected)
        tool_payload = load_object(args.tool_config)
        evidence = execute_isolated_staging(ProviderClient(key), expected, tool_payload)
        encoded = json.dumps(evidence, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.write("\n")
    except (StagingError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
