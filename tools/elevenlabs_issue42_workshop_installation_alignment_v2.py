#!/usr/bin/env python3
"""BODYSHOP Voice PoC #42 — GET-only workshop/install alignment planner V2.

This module cannot mutate ElevenLabs. Its network client exposes GET only.

It verifies the exact adopted Gate-2 provider Main state, proves that the live
Operator breakdown still matches the GitHub-owned V1 source state, validates
the bounded V1 -> V2 semantic delta, and emits a sanitized future provider
write-set. The emitted POST/PATCH operations are data only; this executable
contains no POST/PATCH network method and cannot execute them.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import elevenlabs_client_tool_staging_v1 as staging

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
AGENT_NAME = "AI Control"
ISSUE = 42
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")

BASELINE = {
    "agent_id_sha256": "b9849ffbf0f27a2f16dca71dcf8adce41c0f7e6d09c27a9934fcdf7747d3789d",
    "main_branch_id_sha256": "a15d1399a8e6bc5c778fffe2dc9587f2dc1bef57ed4b856d56e878640f40b3e5",
    "version_id_sha256": "385966c4b272957579f8ceb9a468cff544ef84ffa10f575c792bf5e043522069",
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
    "tool_id_sha256": "499b58650429949fd28d126855f283492fd57262431e42fb20b01ed27e980a50",
    "operator": {
        "name": "Operator breakdown",
        "raw_api_type": "deterministic",
        "trigger_sha256": "92006c2f29cbba1efa4df86c8cf5b18093c9f43139b96904d4baa1b9354ed380",
        "trigger_length": 108,
        "content_sha256": "edbfdae062d20f858ab163bbb7d4e5efcd335d0f4cf37be5e4cea3236cd083b9",
        "content_length": 3466,
        "version_present": True,
    },
    "technician": {
        "name": "Technician pre-close",
        "raw_api_type": "free_form",
        "trigger_sha256": "36e9ff5743d2c980808909bf745f93a8be0dbfa43c70d0c64758c602fd963778",
        "trigger_length": 93,
        "content_sha256": "c8238704959494ea15c8e7897cd4b18420b23b99a56a8ad4236662f1f180fae2",
        "content_length": 588,
        "version_present": True,
    },
}


class AlignmentError(RuntimeError):
    pass


def load_object(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AlignmentError(f"Unable to load JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AlignmentError("JSON root must be an object")
    return value


def safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise AlignmentError(f"Invalid {label}")
    return urllib.parse.quote(value, safe="")


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
        raise AlignmentError("dynamic_variable_placeholders is not an object")
    return sorted(str(key) for key in node)


class ReadOnlyProviderClient:
    """Narrow ElevenLabs client with GET only."""

    def __init__(self, api_key: str, base_url: str = API_BASE):
        self.api_key = api_key
        self.base_url = base_url

    def _get(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        qs = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}" + (f"?{qs}" if qs else "")
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "accept": "application/json",
                "xi-api-key": self.api_key,
                "user-agent": "bodyshop-voice-poc-issue42-get-only-v2/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise AlignmentError(f"ElevenLabs GET failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise AlignmentError("ElevenLabs GET failed due to a network error") from exc
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise AlignmentError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise AlignmentError("ElevenLabs returned an unexpected non-object response")
        return parsed

    def list_agents(self, name: str, cursor: str | None = None) -> dict[str, Any]:
        query = {"page_size": "100", "search": name, "archived": "false"}
        if cursor:
            query["cursor"] = cursor
        return self._get("/v1/convai/agents", query)

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        return self._get(f"/v1/convai/agents/{aid}")

    def list_branches(self, agent_id: str) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        return self._get(
            f"/v1/convai/agents/{aid}/branches",
            {
                "include_archived": "false",
                "include_commit_status": "true",
                "limit": "100",
            },
        )

    def get_procedure(
        self,
        agent_id: str,
        branch_id: str,
        procedure_id: str,
    ) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        pid = safe_identifier(procedure_id, "procedure_id")
        return self._get(
            f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}"
        )

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        tid = safe_identifier(tool_id, "tool_id")
        return self._get(f"/v1/convai/tools/{tid}")


def find_exact_agent(client: ReadOnlyProviderClient) -> dict[str, Any]:
    cursor = None
    matches: list[dict[str, Any]] = []
    while True:
        page = client.list_agents(AGENT_NAME, cursor)
        agents = page.get("agents", [])
        if not isinstance(agents, list):
            raise AlignmentError("Agent listing omitted agents")
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
            raise AlignmentError("Agent pagination omitted next_cursor")
    if len(matches) != 1:
        raise AlignmentError(
            f"Expected exactly one non-archived agent named {AGENT_NAME!r}; found {len(matches)}"
        )
    return matches[0]


def procedure_rows(
    client: ReadOnlyProviderClient,
    agent: dict[str, Any],
    branch_id: str,
) -> dict[str, dict[str, Any]]:
    effective = agent.get("procedures")
    if not isinstance(effective, dict) or len(effective) != 2:
        raise AlignmentError("Effective Procedure map must contain exactly two Procedures")
    rows: dict[str, dict[str, Any]] = {}
    for procedure_id, meta in effective.items():
        if (
            not isinstance(procedure_id, str)
            or not procedure_id
            or not isinstance(meta, dict)
        ):
            raise AlignmentError("Effective Procedure map is malformed")
        row = client.get_procedure(agent["agent_id"], branch_id, procedure_id)
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise AlignmentError("Procedure readback omitted name")
        if name in rows:
            raise AlignmentError(f"Duplicate effective Procedure name {name!r}")
        rows[name] = row
    if set(rows) != {"Operator breakdown", "Technician pre-close"}:
        raise AlignmentError("Effective Procedure names changed")
    return rows


def materialize_operator(expected: dict[str, Any], tool_id: str) -> dict[str, Any]:
    procedure = expected.get("operator_procedure")
    if not isinstance(procedure, dict):
        raise AlignmentError("Expected operator Procedure missing")
    content = copy.deepcopy(procedure.get("content_template"))
    if not isinstance(content, dict) or not isinstance(content.get("steps"), list):
        raise AlignmentError("Expected operator content_template malformed")

    calls = 0
    for step in content["steps"]:
        if not isinstance(step, dict):
            raise AlignmentError("Operator step is not an object")
        if step.get("type") == "tool_call":
            if step.get("tool_ref") != "bodyshop_resolve_confirmed_intake":
                raise AlignmentError("Unexpected symbolic Client Tool reference")
            step.pop("tool_ref", None)
            step["tool_id"] = tool_id
            step["tool_name"] = "bodyshop_resolve_confirmed_intake"
            calls += 1
    if calls != 1:
        raise AlignmentError("Expected exactly one Client Tool call")

    return {
        "name": procedure.get("name"),
        "type": procedure.get("type"),
        "trigger": procedure.get("trigger"),
        "content": staging.canonical_json(content),
    }


def validate_expected_delta(
    v1: dict[str, Any],
    v2: dict[str, Any],
) -> dict[str, Any]:
    if v1.get("schema_version") != 1:
        raise AlignmentError("Gate-2 V1 expected-state schema moved")
    if v2.get("schema_version") != 2:
        raise AlignmentError("Issue #42 V2 expected-state schema must be 2")

    authority = v2.get("authority")
    if (
        not isinstance(authority, dict)
        or authority.get("issue") != ISSUE
        or authority.get("extends_without_rewriting")
        != "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1"
    ):
        raise AlignmentError("Issue #42 V2 authority metadata is invalid")

    if v2.get("client_tool") != v1.get("client_tool"):
        raise AlignmentError("V2 must retain the Gate-2 Client Tool contract reference")

    p1 = v1.get("operator_procedure")
    p2 = v2.get("operator_procedure")
    if not isinstance(p1, dict) or not isinstance(p2, dict):
        raise AlignmentError("Operator Procedure metadata missing")
    for key in ("name", "type", "trigger"):
        if p2.get(key) != p1.get(key):
            raise AlignmentError(f"V2 unexpectedly changed Operator {key}")

    c1 = p1.get("content_template")
    c2 = p2.get("content_template")
    if not isinstance(c1, dict) or not isinstance(c2, dict):
        raise AlignmentError("Operator content template missing")
    s1 = c1.get("steps")
    s2 = c2.get("steps")
    if not isinstance(s1, list) or not isinstance(s2, list) or len(s1) != len(s2):
        raise AlignmentError("Operator step count changed")

    changed: list[int] = []
    for index, (old, new) in enumerate(zip(s1, s2)):
        if staging.canonical_json(old) != staging.canonical_json(new):
            changed.append(index)
    if changed != [1, 3]:
        raise AlignmentError(
            f"V2 may change only workshop/install Ask steps [1, 3]; found {changed}"
        )

    workshop = s2[1]
    installation = s2[3]
    if workshop.get("type") != "ask" or installation.get("type") != "ask":
        raise AlignmentError("Workshop and installation steps must remain Ask")

    workshop_text = str(workshop.get("instruction", ""))
    installation_text = str(installation.get("instruction", ""))
    required_workshop_fragments = (
        "¿De qué taller BODYSHOP llamas?",
        "not the installation",
        "does not satisfy this step",
        "Do not advance",
    )
    required_installation_fragments = (
        "¿Qué instalación?",
        "distinct from workshop/Taller",
        "Do not reuse",
        "Do not advance",
    )
    if any(fragment not in workshop_text for fragment in required_workshop_fragments):
        raise AlignmentError("Workshop Ask lacks an explicit semantic/exit boundary")
    if any(fragment not in installation_text for fragment in required_installation_fragments):
        raise AlignmentError("Installation Ask lacks an explicit semantic/exit boundary")

    encoded = staging.canonical_json(v2)
    for duplicated_catalog_value in (
        "Taller 1",
        "Taller 2",
        "Taller 3",
        "Autobastidor",
        "Mascarón",
        "LAT-IZQ",
        "T01",
        "AUT",
    ):
        if duplicated_catalog_value in encoded:
            raise AlignmentError(
                f"V2 must not duplicate canonical catalog value {duplicated_catalog_value!r}"
            )

    return {
        "changed_step_indexes": changed,
        "workshop_instruction": workshop_text,
        "installation_instruction": installation_text,
    }


def collect_live_main(
    client: ReadOnlyProviderClient,
    tool_payload: dict[str, Any],
    expected_v1: dict[str, Any],
) -> dict[str, Any]:
    listed = find_exact_agent(client)
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise AlignmentError("Matched agent omitted agent_id")
    if staging.sha256_text(agent_id) != BASELINE["agent_id_sha256"]:
        raise AlignmentError("Agent identity fingerprint moved")

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
            raise AlignmentError(f"Provider omitted {label}")
    if branch_id != main_branch_id:
        raise AlignmentError("Current provider branch is not Main")
    if staging.sha256_text(main_branch_id) != BASELINE["main_branch_id_sha256"]:
        raise AlignmentError("Main branch fingerprint moved")
    if staging.sha256_text(version_id) != BASELINE["version_id_sha256"]:
        raise AlignmentError("Main version fingerprint moved")

    cfg = agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise AlignmentError("Main conversation_config malformed")
    acfg = cfg.get("agent")
    tts = cfg.get("tts")
    if not isinstance(acfg, dict) or not isinstance(tts, dict):
        raise AlignmentError("Main agent/tts config malformed")
    pcfg = acfg.get("prompt")
    if not isinstance(pcfg, dict):
        raise AlignmentError("Main prompt config malformed")

    prompt = staging.normalize_text(pcfg.get("prompt"))
    if not isinstance(prompt, str):
        raise AlignmentError("Main System Prompt missing")
    if staging.sha256_text(prompt) != BASELINE["system_prompt_sha256"]:
        raise AlignmentError("Main System Prompt fingerprint moved")
    if len(prompt) != BASELINE["system_prompt_length"]:
        raise AlignmentError("Main System Prompt length moved")
    if acfg.get("language") != BASELINE["language"]:
        raise AlignmentError("Main language moved")
    if pcfg.get("llm") != BASELINE["llm_id"]:
        raise AlignmentError("Main LLM moved")
    if dynamic_variable_names(agent) != BASELINE["dynamic_variable_names"]:
        raise AlignmentError("Main dynamic-variable set moved")
    if staging.safe_id_fingerprint(tts.get("voice_id")) != BASELINE["voice_id_sha256"]:
        raise AlignmentError("Main voice fingerprint moved")

    platform = agent.get("platform_settings")
    auth = platform.get("auth") if isinstance(platform, dict) else None
    if not isinstance(auth, dict) or auth.get("enable_auth") is not False:
        raise AlignmentError("Main auth classification moved")

    tool_ids = pcfg.get("tool_ids", [])
    if not isinstance(tool_ids, list) or len(tool_ids) != 1:
        raise AlignmentError("Main must contain exactly one attached Client Tool")
    tool_id = tool_ids[0]
    if not isinstance(tool_id, str) or not tool_id:
        raise AlignmentError("Attached Client Tool id malformed")
    if staging.safe_id_fingerprint(tool_id) != BASELINE["tool_id_sha256"]:
        raise AlignmentError("Client Tool fingerprint moved")
    staging.verify_tool_contract(client.get_tool(tool_id), tool_payload)

    branches = client.list_branches(agent_id).get("results", [])
    if not isinstance(branches, list):
        raise AlignmentError("Branch listing omitted results")
    current = [
        item
        for item in branches
        if isinstance(item, dict) and item.get("id") == main_branch_id
    ]
    if len(current) != 1:
        raise AlignmentError("Main branch not found exactly once")
    meta = current[0]
    if meta.get("name") != "Main":
        raise AlignmentError("Main branch name moved")
    if bool(meta.get("is_archived", False)):
        raise AlignmentError("Main branch is archived")
    if bool(meta.get("draft_exists", False)):
        raise AlignmentError("Main branch unexpectedly has a Procedure draft")

    rows = procedure_rows(client, agent, main_branch_id)
    live_operator = staging.semantic_procedure_fingerprint(rows["Operator breakdown"])
    live_technician = staging.semantic_procedure_fingerprint(rows["Technician pre-close"])
    if live_operator != BASELINE["operator"]:
        raise AlignmentError("Live Operator breakdown fingerprint moved")
    if live_technician != BASELINE["technician"]:
        raise AlignmentError("Live Technician pre-close fingerprint moved")

    expected_operator = staging.semantic_procedure_fingerprint(
        {**materialize_operator(expected_v1, tool_id), "version_id": "expected"}
    )
    expected_operator["version_present"] = True
    if live_operator != expected_operator:
        raise AlignmentError(
            "Live Operator breakdown no longer matches GitHub-owned Gate-2 V1"
        )

    operator_id = rows["Operator breakdown"].get("procedure_id")
    technician_id = rows["Technician pre-close"].get("procedure_id")
    if not isinstance(operator_id, str) or not operator_id:
        raise AlignmentError("Operator Procedure id missing")
    if not isinstance(technician_id, str) or not technician_id:
        raise AlignmentError("Technician Procedure id missing")

    return {
        "raw": {
            "agent_id": agent_id,
            "main_branch_id": main_branch_id,
            "version_id": version_id,
            "tool_id": tool_id,
            "operator_procedure_id": operator_id,
            "technician_procedure_id": technician_id,
        },
        "safe": {
            "agent_id_sha256": staging.sha256_text(agent_id),
            "main_branch_id_sha256": staging.sha256_text(main_branch_id),
            "version_id_sha256": staging.sha256_text(version_id),
            "system_prompt_sha256": staging.sha256_text(prompt),
            "system_prompt_length": len(prompt),
            "language": acfg.get("language"),
            "llm_id": pcfg.get("llm"),
            "dynamic_variable_names": dynamic_variable_names(agent),
            "voice_id_sha256": staging.safe_id_fingerprint(tts.get("voice_id")),
            "auth_enable_auth": False,
            "tool_id_sha256": staging.safe_id_fingerprint(tool_id),
            "tool_name": "bodyshop_resolve_confirmed_intake",
            "operator_procedure_id_sha256": staging.safe_id_fingerprint(operator_id),
            "technician_procedure_id_sha256": staging.safe_id_fingerprint(technician_id),
            "operator": live_operator,
            "technician": live_technician,
            "main_draft_exists": False,
        },
    }


def build_sanitized_plan(
    live: dict[str, Any],
    expected_v1: dict[str, Any],
    expected_v2: dict[str, Any],
) -> dict[str, Any]:
    delta = validate_expected_delta(expected_v1, expected_v2)
    raw = live["raw"]
    target_item = {
        **materialize_operator(expected_v2, raw["tool_id"]),
        "version_id": "expected",
    }
    target_fp = staging.semantic_procedure_fingerprint(target_item)
    target_fp["version_present"] = True

    current_fp = live["safe"]["operator"]
    for field in ("name", "raw_api_type", "trigger_sha256", "trigger_length"):
        if target_fp[field] != current_fp[field]:
            raise AlignmentError(f"V2 target unexpectedly changes Operator {field}")
    if target_fp["content_sha256"] == current_fp["content_sha256"]:
        raise AlignmentError("V2 target does not change Operator content")

    branch = expected_v2.get("provider_staging")
    if not isinstance(branch, dict):
        raise AlignmentError("V2 provider_staging metadata missing")
    branch_name = branch.get("branch_name")
    branch_description = branch.get("branch_description")
    if not isinstance(branch_name, str) or not branch_name:
        raise AlignmentError("V2 staging branch name missing")
    if not isinstance(branch_description, str) or not branch_description:
        raise AlignmentError("V2 staging branch description missing")
    if branch.get("required_live_percentage") != 0:
        raise AlignmentError("V2 staging branch must remain zero-live")
    if branch.get("provider_main_merge_authorized") is not False:
        raise AlignmentError("V2 must not authorize provider Main merge")

    plan = {
        "schema_version": 2,
        "mode": "ISSUE42_GET_ONLY_ALIGNMENT_PLAN",
        "provider": "ElevenLabs",
        "issue": ISSUE,
        "provider_write_performed": False,
        "live_main": live["safe"],
        "diagnosis": {
            "classification": "RAW_PROVIDER_MATCHES_GATE2_V1_RUNTIME_SEMANTIC_DRIFT",
            "gate2_v1_source_match": True,
            "canonical_domain_change_required": False,
            "client_tool_contract_change_required": False,
            "historical_gate2_v1_rewritten": False,
        },
        "expected_state_delta": {
            "source": "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1",
            "target": "GATE3_WORKSHOP_INSTALLATION_EXPECTED_PROVIDER_CONFIGURATION_V2",
            "changed_step_indexes": delta["changed_step_indexes"],
            "workshop_instruction": delta["workshop_instruction"],
            "installation_instruction": delta["installation_instruction"],
            "source_operator_content_sha256": current_fp["content_sha256"],
            "source_operator_content_length": current_fp["content_length"],
            "target_operator_content_sha256": target_fp["content_sha256"],
            "target_operator_content_length": target_fp["content_length"],
            "trigger_sha256": target_fp["trigger_sha256"],
        },
        "planned_provider_operations": [
            {
                "order": 1,
                "method": "POST",
                "endpoint": "/v1/convai/agents/{agent_id}/branches",
                "authorized_now": False,
                "purpose": "create zero-live isolated branch from exact current Main version",
                "request_safe": {
                    "parent_version_id_sha256": live["safe"]["version_id_sha256"],
                    "name": branch_name,
                    "description": branch_description,
                    "include_draft": False,
                },
            },
            {
                "order": 2,
                "method": "GET",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}",
                "authorized_now": True,
                "purpose": "verify exact parent, zero-live state, no archive and no unexpected draft",
            },
            {
                "order": 3,
                "method": "PATCH",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/procedures/{operator_procedure_id}/draft",
                "authorized_now": False,
                "purpose": "stage only the V2 Operator breakdown semantic correction",
                "request_safe": {
                    "name": "Operator breakdown",
                    "type": "deterministic",
                    "trigger_sha256": target_fp["trigger_sha256"],
                    "content_sha256": target_fp["content_sha256"],
                    "content_length": target_fp["content_length"],
                    "changed_step_indexes": delta["changed_step_indexes"],
                },
            },
            {
                "order": 4,
                "method": "PATCH",
                "endpoint": "/v1/convai/agents/{agent_id}?branch_id={source_branch_id}",
                "authorized_now": False,
                "purpose": "publish the isolated Procedure draft as a new isolated branch version",
                "request_safe": {
                    "version_description": "BODYSHOP #42 publish workshop/install semantic alignment"
                },
            },
            {
                "order": 5,
                "method": "GET",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/procedures/{operator_procedure_id}",
                "authorized_now": True,
                "purpose": "verify exact V2 Operator fingerprint and unchanged retained state",
            },
            {
                "order": 6,
                "method": "GET",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge-preview",
                "authorized_now": True,
                "purpose": "preview isolated branch merge into Main with force=false",
                "query_safe": {
                    "target_branch_id_sha256": live["safe"]["main_branch_id_sha256"],
                    "force": "false",
                },
            },
            {
                "order": 7,
                "method": "BLOCKED_DECISION",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge",
                "authorized_now": False,
                "purpose": "provider Main merge requires separate Albert authorization after preview",
                "request_safe": {
                    "archive_source_branch": True,
                    "force": False,
                },
            },
        ],
        "next_gate": "STOP_FOR_ALBERT_PROVIDER_WRITE_SET_AUTHORIZATION",
    }

    encoded = staging.canonical_json(plan)
    for secret_value in raw.values():
        if isinstance(secret_value, str) and secret_value and secret_value in encoded:
            raise AlignmentError("Sanitized plan leaked a raw provider identifier")
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-v1", required=True)
    parser.add_argument("--expected-v2", required=True)
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        expected_v1 = load_object(args.expected_v1)
        expected_v2 = load_object(args.expected_v2)
        tool_payload = load_object(args.tool_config)
        staging.validate_tool_create_payload(tool_payload)
        validate_expected_delta(expected_v1, expected_v2)
        live = collect_live_main(
            ReadOnlyProviderClient(key),
            tool_payload,
            expected_v1,
        )
        plan = build_sanitized_plan(live, expected_v1, expected_v2)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(plan, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print("BODYSHOP_ISSUE42_GET_ONLY_PLAN=PASS")
        print(f"OUTPUT={args.output}")
        print("PROVIDER_WRITE_PERFORMED=NO")
        print(f"NEXT_GATE={plan['next_gate']}")
    except (
        AlignmentError,
        staging.StagingError,
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
