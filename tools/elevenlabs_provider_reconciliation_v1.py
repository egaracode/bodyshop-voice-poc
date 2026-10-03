#!/usr/bin/env python3
"""ElevenLabs provider reconciliation planner V1.

Phase A is deliberately read-only. It validates the exact provider baseline,
the GitHub-owned A5 target, and the target voice identity, then emits a
sanitized ordered plan for the future controlled-write phase.

There are no POST, PATCH, PUT, or DELETE network methods in this planner.
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
from typing import Any

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")
CURRENT_PROCEDURE_TYPES = {"free_form", "deterministic", "folder"}

TARGET_VOICE_NAME = "Eric - Smooth, Trustworthy"
TARGET_VOICE_ID_SHA256 = "1e0c5d7793b1296cb88ddddf08040c9e901c241640ff7e88fcad1c31c7392bc9"

CURRENT_PROVIDER_GUARD_V1 = {
    "agent": {
        "name": "AI Control",
        "language": "es",
        "llm_id": "qwen35-397b-a17b",
        "first_message_sha256": "2c17109f7fc5d2b15a2a9a51d8c31232917d9f56db7b473976b490c8b88a9480",
        "first_message_length": 58,
        "system_prompt_sha256": "05a9d7a959e1a7b27c720d084c14f8505a80a11532b20eedd154f3bc904d8e1f",
        "system_prompt_length": 3108,
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
        "agent_id_sha256": "b9849ffbf0f27a2f16dca71dcf8adce41c0f7e6d09c27a9934fcdf7747d3789d",
        "version_id_sha256": "89dc96c3c0c3f05594643420a06af9a2fed62e78de7cfe74ec8e5bfeb1ab78e1",
        "main_branch_id_sha256": "a15d1399a8e6bc5c778fffe2dc9587f2dc1bef57ed4b856d56e878640f40b3e5",
    },
    "branch": {
        "name": "Main",
        "is_archived": False,
        "draft_exists": False,
        "commits_ahead": 0,
        "commits_behind": 0,
        "id_sha256": "a15d1399a8e6bc5c778fffe2dc9587f2dc1bef57ed4b856d56e878640f40b3e5",
    },
    "voice": {
        "name": "Will - Relaxed Optimist",
        "voice_id_sha256": "21d370a4c53dd9bbf57129b556361793ec4fb427eb7ff0b8c535f6fdee2bcf9a",
        "tts_model_id": "eleven_flash_v2_5",
        "stability": 0.5,
        "speed": 0.9,
        "similarity_boost": 0.8,
    },
    "procedures": [
        {
            "name": "Element identification",
            "raw_api_type": "free_form",
            "content_shape": "TEXT",
            "trigger_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "trigger_length": 0,
            "content_sha256": "6f9e1adcb990b147684f9124e81f720b943102ea84fa3cf32a498efca0939053",
            "content_length": 1738,
            "has_draft": False,
            "version_present": True,
            "procedure_id_sha256": "f069b7a92ad0cac0d3e8e496050f2b6122d04d27e0965688e84bf9f3d51bbd17",
        },
        {
            "name": "Operator breakdown",
            "raw_api_type": "free_form",
            "content_shape": "TEXT",
            "trigger_sha256": "a9d4e877a406bb79089fdf67f1566d80a212af53bbc9d72c8203f280defb4976",
            "trigger_length": 68,
            "content_sha256": "a349726ecd8842e212f78a959eebff984c46befc428a03c223c6ed3408b6f134",
            "content_length": 4997,
            "has_draft": False,
            "version_present": True,
            "procedure_id_sha256": "b20798cbbad928db10c9326b6d8c44875efaac6d37959212777e22439bcc63e1",
        },
        {
            "name": "Technician pre-close",
            "raw_api_type": "free_form",
            "content_shape": "TEXT",
            "trigger_sha256": "c13b299291047126ba7cb943d44b65b2114f3e7856e8df2870d32fa3fc79f73e",
            "trigger_length": 111,
            "content_sha256": "5f9ea898f4c6ad795aab241c1c6d223be35f4a0d6330c3abea7e00452dd5bd8f",
            "content_length": 1769,
            "has_draft": False,
            "version_present": True,
            "procedure_id_sha256": "b9c3cc30919a66654bf3b5bfe0e458de8cfcc87b89171ba3cc431013dd23fe40",
        },
    ],
}

EXPECTED_A5_TARGET_FINGERPRINTS_V1 = {
    "system_prompt_sha256": "7e53fa089edbe9ae5da4af97e1f2fbb36833fffa504eb033d710b107d89972f2",
    "system_prompt_length": 2305,
    "voice_name": TARGET_VOICE_NAME,
    "voice_id_sha256": TARGET_VOICE_ID_SHA256,
    "procedures": {
        "Operator breakdown": {
            "target_api_type": "deterministic",
            "trigger_sha256": "92006c2f29cbba1efa4df86c8cf5b18093c9f43139b96904d4baa1b9354ed380",
            "trigger_length": 108,
            "content_sha256": "f0370537fa7e74e286405a0dd38a551bea4882f8410f1f262973822200d7e791",
            "content_length": 1753,
        },
        "Technician pre-close": {
            "target_api_type": "free_form",
            "trigger_sha256": "36e9ff5743d2c980808909bf745f93a8be0dbfa43c70d0c64758c602fd963778",
            "trigger_length": 93,
            "content_sha256": "c8238704959494ea15c8e7897cd4b18420b23b99a56a8ad4236662f1f180fae2",
            "content_length": 588,
        },
    },
}


class PlannerError(RuntimeError):
    pass


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise PlannerError(f"Expected text, got {type(value).__name__}")
    return value.replace("\r\n", "\n").replace("\r", "\n")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise PlannerError(f"Invalid {label}")
    return urllib.parse.quote(value, safe="")


def safe_id_fingerprint(value: Any) -> str | None:
    return sha256_text(value) if isinstance(value, str) and value else None


def content_shape(value: Any) -> tuple[str, str]:
    text = normalize_text(value)
    if text is None:
        raise PlannerError("Procedure content is missing")
    if text == "":
        return "EMPTY", ""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return "TEXT", text
    canonical = canonical_json(parsed)
    if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
        return "JSON_STEPS", canonical
    return "INVALID_JSON_STEPS", canonical


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
                "user-agent": "bodyshop-voice-poc-elevenlabs-reconcile-plan-v1/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise PlannerError(f"ElevenLabs GET failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise PlannerError("ElevenLabs GET failed due to a network error") from exc
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise PlannerError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise PlannerError("ElevenLabs returned an unexpected non-object response")
        return parsed

    def list_agents(self, name: str, cursor: str | None = None) -> dict[str, Any]:
        query = {"page_size": "100", "search": name, "archived": "false"}
        if cursor:
            query["cursor"] = cursor
        return self._get("/v1/convai/agents", query)

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        return self._get(f"/v1/convai/agents/{safe_identifier(agent_id, 'agent_id')}")

    def list_branches(self, agent_id: str) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        return self._get(
            f"/v1/convai/agents/{aid}/branches",
            {"include_archived": "false", "include_commit_status": "true", "limit": "100"},
        )

    def list_procedures(
        self, agent_id: str, branch_id: str, agent_version_id: str | None
    ) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        query = {"agent_version_id": agent_version_id} if agent_version_id else None
        return self._get(f"/v1/convai/agents/{aid}/branches/{bid}/procedures", query)

    def get_procedure(
        self,
        agent_id: str,
        branch_id: str,
        procedure_id: str,
        agent_version_id: str | None,
    ) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        pid = safe_identifier(procedure_id, "procedure_id")
        query = {"agent_version_id": agent_version_id} if agent_version_id else None
        return self._get(
            f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}", query
        )

    def get_voice(self, voice_id: str) -> dict[str, Any]:
        return self._get(f"/v1/voices/{safe_identifier(voice_id, 'voice_id')}")

    def search_voices(
        self, search: str, next_page_token: str | None = None
    ) -> dict[str, Any]:
        query = {"search": search, "page_size": "100", "include_total_count": "false"}
        if next_page_token:
            query["next_page_token"] = next_page_token
        return self._get("/v2/voices", query)


def find_exact_agent(client: ApiClient, name: str) -> dict[str, Any]:
    cursor = None
    matches: list[dict[str, Any]] = []
    while True:
        page = client.list_agents(name, cursor)
        agents = page.get("agents", [])
        if not isinstance(agents, list):
            raise PlannerError("Agent listing omitted agents list")
        for item in agents:
            if isinstance(item, dict) and item.get("name") == name and not item.get(
                "archived", False
            ):
                matches.append(item)
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
        if not isinstance(cursor, str) or not cursor:
            raise PlannerError("Agent pagination advertised has_more without next_cursor")
    if len(matches) != 1:
        raise PlannerError(
            f"Expected exactly one non-archived agent named {name!r}; found {len(matches)}"
        )
    return matches[0]


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
        raise PlannerError("dynamic_variable_placeholders is not an object")
    return sorted(str(key) for key in node)


def collect_current_procedures(
    client: ApiClient, agent_id: str, branch_id: str, version_id: str
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    listing = client.list_procedures(agent_id, branch_id, version_id)
    items = listing.get("procedures", [])
    if not isinstance(items, list):
        raise PlannerError("Procedure listing omitted procedures list")

    safe_items: list[dict[str, Any]] = []
    raw_ids_by_name: dict[str, str] = {}
    seen: set[str] = set()

    for meta in items:
        if not isinstance(meta, dict):
            raise PlannerError("Procedure listing contains non-object item")
        pid = meta.get("procedure_id")
        if not isinstance(pid, str) or not pid:
            raise PlannerError("Procedure listing omitted procedure_id")
        full = client.get_procedure(agent_id, branch_id, pid, version_id)
        name = full.get("name", meta.get("name"))
        if not isinstance(name, str) or not name:
            raise PlannerError("Procedure has no valid name")
        if name in seen:
            raise PlannerError(f"Duplicate Procedure name {name!r}")
        seen.add(name)
        raw_ids_by_name[name] = pid

        raw_type = full.get("type", meta.get("type"))
        if raw_type not in CURRENT_PROCEDURE_TYPES:
            raise PlannerError(f"Unknown current Procedure API type: {raw_type!r}")
        shape, canonical_content = content_shape(full.get("content"))
        trigger = normalize_text(full.get("trigger", meta.get("trigger", "")))
        if trigger is None:
            trigger = ""

        safe_items.append(
            {
                "name": name,
                "raw_api_type": raw_type,
                "content_shape": shape,
                "trigger_sha256": sha256_text(trigger),
                "trigger_length": len(trigger),
                "content_sha256": sha256_text(canonical_content),
                "content_length": len(canonical_content),
                "has_draft": bool(meta.get("has_draft", False)),
                "version_present": bool(full.get("version_id") or meta.get("version_id")),
                "procedure_id_sha256": safe_id_fingerprint(pid),
            }
        )

    safe_items.sort(key=lambda item: item["name"])
    return safe_items, raw_ids_by_name


def collect_live_state(client: ApiClient, agent_name: str) -> dict[str, Any]:
    listed = find_exact_agent(client, agent_name)
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise PlannerError("Matched agent omitted agent_id")

    agent = client.get_agent(agent_id)
    branch_id = agent.get("branch_id")
    version_id = agent.get("version_id")
    main_branch_id = agent.get("main_branch_id")
    for label, value in (
        ("branch_id", branch_id),
        ("version_id", version_id),
        ("main_branch_id", main_branch_id),
    ):
        if not isinstance(value, str) or not value:
            raise PlannerError(f"Provider omitted {label}")

    branches = client.list_branches(agent_id).get("results", [])
    if not isinstance(branches, list):
        raise PlannerError("Branch listing omitted results list")
    matches = [
        item for item in branches if isinstance(item, dict) and item.get("id") == branch_id
    ]
    if len(matches) != 1:
        raise PlannerError("Current branch not found exactly once")
    branch = matches[0]
    if branch_id != main_branch_id:
        raise PlannerError("Current provider branch is not the main branch")

    procedures, procedure_ids_by_name = collect_current_procedures(
        client, agent_id, branch_id, version_id
    )

    cfg = agent.get("conversation_config", {})
    if not isinstance(cfg, dict):
        raise PlannerError("conversation_config is not an object")
    acfg = cfg.get("agent", {})
    tts = cfg.get("tts", {})
    if not isinstance(acfg, dict) or not isinstance(tts, dict):
        raise PlannerError("conversation_config agent/tts is malformed")
    pcfg = acfg.get("prompt", {})
    if not isinstance(pcfg, dict):
        raise PlannerError("conversation_config.agent.prompt is malformed")

    first_message = normalize_text(acfg.get("first_message"))
    system_prompt = normalize_text(pcfg.get("prompt"))
    voice_id = tts.get("voice_id")
    voice = client.get_voice(voice_id) if isinstance(voice_id, str) and voice_id else {}
    if not isinstance(voice, dict):
        raise PlannerError("Voice response is not an object")

    safe_guard = {
        "agent": {
            "name": agent.get("name"),
            "language": acfg.get("language"),
            "llm_id": pcfg.get("llm"),
            "first_message_sha256": (
                sha256_text(first_message) if isinstance(first_message, str) else None
            ),
            "first_message_length": (
                len(first_message) if isinstance(first_message, str) else None
            ),
            "system_prompt_sha256": (
                sha256_text(system_prompt) if isinstance(system_prompt, str) else None
            ),
            "system_prompt_length": (
                len(system_prompt) if isinstance(system_prompt, str) else None
            ),
            "dynamic_variable_names": dynamic_variable_names(agent),
            "agent_id_sha256": safe_id_fingerprint(agent_id),
            "version_id_sha256": safe_id_fingerprint(version_id),
            "main_branch_id_sha256": safe_id_fingerprint(main_branch_id),
        },
        "branch": {
            "name": branch.get("name"),
            "is_archived": bool(branch.get("is_archived", False)),
            "draft_exists": bool(branch.get("draft_exists", False)),
            "commits_ahead": branch.get("commits_ahead"),
            "commits_behind": branch.get("commits_behind"),
            "id_sha256": safe_id_fingerprint(branch_id),
        },
        "voice": {
            "name": voice.get("name") if isinstance(voice.get("name"), str) else None,
            "voice_id_sha256": safe_id_fingerprint(voice_id),
            "tts_model_id": tts.get("model_id"),
            "stability": tts.get("stability"),
            "speed": tts.get("speed"),
            "similarity_boost": tts.get("similarity_boost"),
        },
        "procedures": procedures,
    }

    return {
        "safe_guard": safe_guard,
        "raw": {
            "agent_id": agent_id,
            "branch_id": branch_id,
            "version_id": version_id,
            "main_branch_id": main_branch_id,
            "procedure_ids_by_name": procedure_ids_by_name,
        },
        "conversation_config": cfg,
    }


def assert_current_provider_guard(
    actual: dict[str, Any], expected: dict[str, Any] = CURRENT_PROVIDER_GUARD_V1
) -> None:
    if actual != expected:
        raise PlannerError(
            "Provider baseline moved since the classified V2 snapshot; refusing to plan writes"
        )


def derive_expected_target(expected: dict[str, Any]) -> dict[str, Any]:
    agent = expected.get("agent", {})
    if not isinstance(agent, dict):
        raise PlannerError("Expected agent configuration is malformed")

    prompt = normalize_text(agent.get("system_prompt"))
    if not isinstance(prompt, str):
        raise PlannerError("Expected System Prompt is not pinned")

    voice = agent.get("voice", {})
    if not isinstance(voice, dict):
        raise PlannerError("Expected voice configuration is malformed")

    procedures = expected.get("procedures", [])
    if not isinstance(procedures, list):
        raise PlannerError("Expected Procedures must be a list")

    by_name: dict[str, dict[str, Any]] = {}
    for item in procedures:
        if not isinstance(item, dict):
            raise PlannerError("Expected Procedure is not an object")
        name = item.get("name")
        if not isinstance(name, str) or not name or name in by_name:
            raise PlannerError("Expected Procedure names must be unique")
        by_name[name] = item

    if set(by_name) != {"Operator breakdown", "Technician pre-close"}:
        raise PlannerError("A5 expected Procedure set changed")

    operator = by_name["Operator breakdown"]
    technician = by_name["Technician pre-close"]
    if operator.get("type") != "structured":
        raise PlannerError("Historical Operator breakdown is no longer structured")
    if technician.get("type") != "free_form":
        raise PlannerError("Historical Technician pre-close is no longer free_form")

    operator_trigger = normalize_text(operator.get("trigger"))
    technician_trigger = normalize_text(technician.get("trigger"))
    technician_content = normalize_text(technician.get("content"))
    if not all(
        isinstance(value, str)
        for value in (operator_trigger, technician_trigger, technician_content)
    ):
        raise PlannerError("Expected Procedure trigger/content is malformed")

    operator_content = canonical_json(operator.get("content"))

    target = {
        "system_prompt_sha256": sha256_text(prompt),
        "system_prompt_length": len(prompt),
        "voice_name": voice.get("name"),
        "voice_id_sha256": voice.get("id_sha256"),
        "procedures": {
            "Operator breakdown": {
                "target_api_type": "deterministic",
                "trigger_sha256": sha256_text(operator_trigger),
                "trigger_length": len(operator_trigger),
                "content_sha256": sha256_text(operator_content),
                "content_length": len(operator_content),
            },
            "Technician pre-close": {
                "target_api_type": "free_form",
                "trigger_sha256": sha256_text(technician_trigger),
                "trigger_length": len(technician_trigger),
                "content_sha256": sha256_text(technician_content),
                "content_length": len(technician_content),
            },
        },
    }

    if target != EXPECTED_A5_TARGET_FINGERPRINTS_V1:
        raise PlannerError("GitHub-owned A5 expected target changed; explicit review required")
    return target


def resolve_target_voice(client: ApiClient) -> dict[str, Any]:
    token = None
    matching_ids: list[str] = []
    seen_tokens: set[str] = set()

    while True:
        page = client.search_voices(TARGET_VOICE_NAME, token)
        voices = page.get("voices", [])
        if not isinstance(voices, list):
            raise PlannerError("Voice search omitted voices list")
        for voice in voices:
            if not isinstance(voice, dict):
                continue
            if voice.get("name") != TARGET_VOICE_NAME:
                continue
            voice_id = voice.get("voice_id")
            if isinstance(voice_id, str) and voice_id:
                matching_ids.append(voice_id)

        if not page.get("has_more"):
            break
        token = page.get("next_page_token")
        if not isinstance(token, str) or not token or token in seen_tokens:
            raise PlannerError("Voice pagination is malformed")
        seen_tokens.add(token)

    fingerprint_matches = [
        voice_id
        for voice_id in matching_ids
        if sha256_text(voice_id) == TARGET_VOICE_ID_SHA256
    ]
    if len(fingerprint_matches) != 1:
        raise PlannerError(
            "Expected Eric voice identity is unavailable or ambiguous by fingerprint"
        )

    voice_id = fingerprint_matches[0]
    full = client.get_voice(voice_id)
    if full.get("name") != TARGET_VOICE_NAME:
        raise PlannerError("Voice GET did not confirm expected Eric name")

    return {
        "raw_voice_id": voice_id,
        "safe": {
            "name": TARGET_VOICE_NAME,
            "voice_id_sha256": TARGET_VOICE_ID_SHA256,
            "same_name_candidates": len(matching_ids),
        },
    }


def ensure_provider_branch_name_available(
    client: ApiClient, agent_id: str, provider_branch_name: str
) -> None:
    results = client.list_branches(agent_id).get("results", [])
    if not isinstance(results, list):
        raise PlannerError("Branch listing omitted results list")
    for item in results:
        if isinstance(item, dict) and item.get("name") == provider_branch_name:
            raise PlannerError(
                f"Provider branch {provider_branch_name!r} already exists; refusing ambiguous reuse"
            )


def build_sanitized_plan(
    live: dict[str, Any],
    target: dict[str, Any],
    target_voice: dict[str, Any],
    provider_branch_name: str,
) -> dict[str, Any]:
    raw = live["raw"]
    tech_pid = raw["procedure_ids_by_name"].get("Technician pre-close")
    if not isinstance(tech_pid, str) or not tech_pid:
        raise PlannerError("Technician pre-close raw Procedure identity is missing")

    operator_target = target["procedures"]["Operator breakdown"]
    tech_target = target["procedures"]["Technician pre-close"]

    return {
        "schema_version": 1,
        "mode": "PLAN_READ_ONLY",
        "provider": "ElevenLabs",
        "issue": 34,
        "source_guard": live["safe_guard"],
        "target": {
            "agent": {
                "name": "AI Control",
                "system_prompt_sha256": target["system_prompt_sha256"],
                "system_prompt_length": target["system_prompt_length"],
                "voice": target_voice["safe"],
            },
            "effective_procedure_names": [
                "Operator breakdown",
                "Technician pre-close",
            ],
            "procedures": target["procedures"],
        },
        "provider_branch": {
            "name": provider_branch_name,
            "source_agent_version_id_sha256": safe_id_fingerprint(raw["version_id"]),
            "source_main_branch_id_sha256": safe_id_fingerprint(raw["main_branch_id"]),
            "expected_live_percentage": 0,
        },
        "planned_operations": [
            {
                "order": 1,
                "method": "POST",
                "endpoint": "/v1/convai/agents/{agent_id}/branches",
                "purpose": "create isolated provider branch from exact Main version",
                "body_safe": {
                    "parent_version_id_sha256": safe_id_fingerprint(raw["version_id"]),
                    "name": provider_branch_name,
                    "description": "BODYSHOP #34 isolated A5 reconciliation staging",
                    "include_draft": False,
                },
                "approval_gate": "EXACT_WRITE_SET_APPROVAL_REQUIRED",
            },
            {
                "order": 2,
                "method": "GET",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{isolated_branch_id}",
                "purpose": "verify isolated provider branch before Procedure mutation",
                "expected_safe": {
                    "parent_branch_id_sha256": safe_id_fingerprint(raw["main_branch_id"]),
                    "current_live_percentage": 0,
                },
                "approval_gate": "READ_ONLY",
            },
            {
                "order": 3,
                "method": "POST",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{isolated_branch_id}/procedures",
                "purpose": "create replacement structured Operator breakdown",
                "body_safe": {
                    "name": "Operator breakdown",
                    "type": "deterministic",
                    "trigger_sha256": operator_target["trigger_sha256"],
                    "trigger_length": operator_target["trigger_length"],
                    "content_sha256": operator_target["content_sha256"],
                    "content_length": operator_target["content_length"],
                },
                "approval_gate": "EXACT_WRITE_SET_APPROVAL_REQUIRED",
            },
            {
                "order": 4,
                "method": "PATCH",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{isolated_branch_id}/procedures/{procedure_id}/draft",
                "purpose": "restore Technician pre-close draft",
                "body_safe": {
                    "procedure_id_sha256": safe_id_fingerprint(tech_pid),
                    "name": "Technician pre-close",
                    "type": "free_form",
                    "trigger_sha256": tech_target["trigger_sha256"],
                    "trigger_length": tech_target["trigger_length"],
                    "content_sha256": tech_target["content_sha256"],
                    "content_length": tech_target["content_length"],
                },
                "approval_gate": "EXACT_WRITE_SET_APPROVAL_REQUIRED",
            },
            {
                "order": 5,
                "method": "PATCH",
                "endpoint": "/v1/convai/agents/{agent_id}?branch_id={isolated_branch_id}",
                "purpose": "publish isolated Procedure drafts so current version_ids can be read",
                "body_safe": {
                    "procedures": "OMITTED_TO_USE_UNPUBLISHED_DRAFTS",
                    "version_description": "BODYSHOP #34 stage Procedure versions",
                },
                "approval_gate": "EXACT_WRITE_SET_APPROVAL_REQUIRED",
            },
            {
                "order": 6,
                "method": "GET",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{isolated_branch_id}/procedures",
                "purpose": "resolve isolated Procedure version refs and verify hashes",
                "approval_gate": "READ_ONLY",
            },
            {
                "order": 7,
                "method": "PATCH",
                "endpoint": "/v1/convai/agents/{agent_id}?branch_id={isolated_branch_id}",
                "purpose": "publish exact reconciled isolated branch configuration",
                "body_safe": {
                    "system_prompt_sha256": target["system_prompt_sha256"],
                    "system_prompt_length": target["system_prompt_length"],
                    "voice_name": target_voice["safe"]["name"],
                    "voice_id_sha256": target_voice["safe"]["voice_id_sha256"],
                    "procedures": "EXACT_TWO_VERSION_REFS_RESOLVED_AT_RUNTIME",
                    "effective_procedure_names": [
                        "Operator breakdown",
                        "Technician pre-close",
                    ],
                    "version_description": "BODYSHOP #34 reconcile ElevenLabs provider to A5",
                },
                "approval_gate": "EXACT_WRITE_SET_APPROVAL_REQUIRED",
            },
            {
                "order": 8,
                "method": "GET",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge-preview",
                "purpose": "preview isolated branch merge into Main and inspect conflicts",
                "query_safe": {
                    "target_branch_id_sha256": safe_id_fingerprint(raw["main_branch_id"]),
                    "force": False,
                },
                "approval_gate": "READ_ONLY",
            },
            {
                "order": 9,
                "method": "POST",
                "endpoint": "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge",
                "purpose": "merge reconciled provider branch into Main",
                "query_safe": {
                    "target_branch_id_sha256": safe_id_fingerprint(raw["main_branch_id"]),
                },
                "body_safe": {"archive_source_branch": True, "force": False},
                "approval_gate": "SEPARATE_PROVIDER_MAIN_MERGE_APPROVAL_REQUIRED",
            },
        ],
        "prohibited": [
            "force provider branch merge",
            "provider Main mutation before merge approval",
            "DELETE draft as committed Procedure removal",
            "raw API key in output",
            "raw provider IDs in output",
            "raw System Prompt in output",
            "raw Procedure trigger/content in output",
            "Supabase or Production mutation",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--agent-name", default="AI Control")
    parser.add_argument(
        "--provider-branch-name", default="bodyshop-a5-reconcile-issue-34"
    )
    args = parser.parse_args(argv)

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        with open(args.expected, encoding="utf-8") as handle:
            expected = json.load(handle)
        target = derive_expected_target(expected)
        client = ApiClient(key)
        live = collect_live_state(client, args.agent_name)
        assert_current_provider_guard(live["safe_guard"])
        ensure_provider_branch_name_available(
            client, live["raw"]["agent_id"], args.provider_branch_name
        )
        target_voice = resolve_target_voice(client)
        plan = build_sanitized_plan(
            live, target, target_voice, args.provider_branch_name
        )
        encoded = json.dumps(plan, ensure_ascii=False, indent=2)
        forbidden_raw_values = [
            live["raw"]["agent_id"],
            live["raw"]["branch_id"],
            live["raw"]["version_id"],
            live["raw"]["main_branch_id"],
            target_voice["raw_voice_id"],
            *live["raw"]["procedure_ids_by_name"].values(),
        ]
        for forbidden in forbidden_raw_values:
            if forbidden and forbidden in encoded:
                raise PlannerError("Sanitized plan leaked a raw provider identifier")
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.write("\n")
    except (PlannerError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
