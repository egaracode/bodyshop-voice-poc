#!/usr/bin/env python3
"""ElevenLabs provider compatibility probe V2.

Read-only by construction. The only network operations are GET requests to
current documented ElevenLabs endpoints. Output is sanitized and deliberately
does not emit a DRIFT verdict against historical A5 expected state.
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


class ProbeError(RuntimeError):
    pass


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ProbeError(f"Expected text, got {type(value).__name__}")
    return value.replace("\r\n", "\n").replace("\r", "\n")


def safe_identifier(value: Any, label: str, reserved: set[str] | None = None) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise ProbeError(f"Invalid {label}")
    if reserved and value in reserved:
        raise ProbeError(f"Reserved token cannot be used as {label}")
    return urllib.parse.quote(value, safe="")


def safe_id_fingerprint(value: Any) -> str | None:
    return sha256_text(value) if isinstance(value, str) and value else None


def content_shape(value: Any) -> tuple[str, str]:
    text = normalize_text(value)
    if text is None:
        raise ProbeError("Procedure content is missing")
    if text == "":
        return "EMPTY", ""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return "TEXT", text
    if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
        canonical = json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return "JSON_STEPS", canonical
    canonical = json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
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
                "user-agent": "bodyshop-voice-poc-elevenlabs-readonly-v2/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise ProbeError(f"ElevenLabs GET failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ProbeError("ElevenLabs GET failed due to a network error") from exc
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ProbeError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise ProbeError("ElevenLabs returned an unexpected non-object response")
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
            {"include_archived": "false", "include_commit_status": "true", "limit": "100"},
        )

    def list_procedures(self, agent_id: str, branch_id: str, agent_version_id: str | None) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        query = {"agent_version_id": agent_version_id} if agent_version_id else None
        return self._get(f"/v1/convai/agents/{aid}/branches/{bid}/procedures", query)

    def get_procedure(self, agent_id: str, branch_id: str, procedure_id: str, agent_version_id: str | None) -> dict[str, Any]:
        aid = safe_identifier(agent_id, "agent_id")
        bid = safe_identifier(branch_id, "branch_id")
        pid = safe_identifier(procedure_id, "procedure_id", {"compile", "draft"})
        query = {"agent_version_id": agent_version_id} if agent_version_id else None
        return self._get(f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}", query)

    def get_voice(self, voice_id: str) -> dict[str, Any]:
        vid = safe_identifier(voice_id, "voice_id", {"settings"})
        return self._get(f"/v1/voices/{vid}")


def find_exact_agent(client: ApiClient, name: str) -> dict[str, Any]:
    cursor = None
    matches: list[dict[str, Any]] = []
    while True:
        page = client.list_agents(name, cursor)
        agents = page.get("agents", [])
        if not isinstance(agents, list):
            raise ProbeError("Agent listing omitted agents list")
        for item in agents:
            if isinstance(item, dict) and item.get("name") == name and not item.get("archived", False):
                matches.append(item)
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
        if not isinstance(cursor, str) or not cursor:
            raise ProbeError("Agent pagination advertised has_more without next_cursor")
    if len(matches) != 1:
        raise ProbeError(f"Expected exactly one non-archived agent named {name!r}; found {len(matches)}")
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
        raise ProbeError("dynamic_variable_placeholders is not an object")
    return sorted(str(k) for k in node)


def branch_snapshot(client: ApiClient, agent_id: str, selected_branch_id: str) -> dict[str, Any]:
    page = client.list_branches(agent_id)
    results = page.get("results", [])
    if not isinstance(results, list):
        raise ProbeError("Branch listing omitted results list")
    matches = [item for item in results if isinstance(item, dict) and item.get("id") == selected_branch_id]
    if len(matches) != 1:
        raise ProbeError("Current agent branch_id was not found exactly once in branch listing")
    branch = matches[0]
    return {
        "name": branch.get("name"),
        "is_archived": bool(branch.get("is_archived", False)),
        "draft_exists": branch.get("draft_exists"),
        "commits_ahead": branch.get("commits_ahead"),
        "commits_behind": branch.get("commits_behind"),
        "id_sha256": safe_id_fingerprint(selected_branch_id),
        "parent_branch_id_sha256": safe_id_fingerprint(branch.get("parent_branch_id")),
    }


def collect_procedures(client: ApiClient, agent_id: str, branch_id: str, version_id: str | None) -> list[dict[str, Any]]:
    listing = client.list_procedures(agent_id, branch_id, version_id)
    raw_items = listing.get("procedures", [])
    if not isinstance(raw_items, list):
        raise ProbeError("Procedure listing omitted procedures list")

    seen_names: set[str] = set()
    output: list[dict[str, Any]] = []
    for meta in raw_items:
        if not isinstance(meta, dict):
            raise ProbeError("Procedure listing contains a non-object item")
        pid = meta.get("procedure_id")
        if not isinstance(pid, str) or not pid:
            raise ProbeError("Procedure listing omitted procedure_id")
        full = client.get_procedure(agent_id, branch_id, pid, version_id)
        name = full.get("name", meta.get("name"))
        if not isinstance(name, str) or not name:
            raise ProbeError("Procedure has no valid name")
        if name in seen_names:
            raise ProbeError(f"Provider contains duplicate Procedure name {name!r}")
        seen_names.add(name)

        raw_type = full.get("type", meta.get("type"))
        if raw_type not in CURRENT_PROCEDURE_TYPES:
            raise ProbeError(f"Unknown current Procedure API type: {raw_type!r}")

        shape, canonical_content = content_shape(full.get("content"))
        trigger = normalize_text(full.get("trigger", meta.get("trigger", "")))
        if trigger is None:
            trigger = ""

        warnings: list[str] = []
        if raw_type == "deterministic" and shape != "JSON_STEPS":
            warnings.append("DETERMINISTIC_WITHOUT_JSON_STEPS")
        if raw_type == "free_form" and shape == "JSON_STEPS":
            warnings.append("FREE_FORM_WITH_JSON_STEPS")
        if raw_type == "folder" and shape not in {"EMPTY", "TEXT"}:
            warnings.append("FOLDER_WITH_STRUCTURED_CONTENT_SHAPE")

        output.append({
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
            "warnings": warnings,
        })

    output.sort(key=lambda item: item["name"])
    return output


def collect_provider_snapshot(client: ApiClient, agent_name: str) -> dict[str, Any]:
    listed = find_exact_agent(client, agent_name)
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise ProbeError("Matched agent omitted agent_id")

    agent = client.get_agent(agent_id)
    branch_id = agent.get("branch_id")
    if not isinstance(branch_id, str) or not branch_id:
        raise ProbeError("Provider did not expose current branch_id")
    version_id = agent.get("version_id")
    if version_id is not None and not isinstance(version_id, str):
        raise ProbeError("Provider exposed invalid version_id")

    cfg = agent.get("conversation_config", {})
    if not isinstance(cfg, dict):
        raise ProbeError("conversation_config is not an object")
    acfg = cfg.get("agent", {})
    if not isinstance(acfg, dict):
        raise ProbeError("conversation_config.agent is not an object")
    pcfg = acfg.get("prompt", {})
    if not isinstance(pcfg, dict):
        raise ProbeError("conversation_config.agent.prompt is not an object")
    tts = cfg.get("tts", {})
    if not isinstance(tts, dict):
        raise ProbeError("conversation_config.tts is not an object")

    voice_id = tts.get("voice_id")
    voice = client.get_voice(voice_id) if isinstance(voice_id, str) and voice_id else {}
    if not isinstance(voice, dict):
        raise ProbeError("Voice response is not an object")

    first_message = normalize_text(acfg.get("first_message"))
    system_prompt = normalize_text(pcfg.get("prompt"))

    return {
        "schema_version": 2,
        "probe": {
            "provider": "ElevenLabs",
            "mode": "READ_ONLY_GET_ONLY",
            "procedure_api_types": sorted(CURRENT_PROCEDURE_TYPES),
            "drift_verdict": "NOT_EMITTED_BY_V2_COMPATIBILITY_PROBE",
        },
        "agent": {
            "name": agent.get("name"),
            "language": acfg.get("language"),
            "llm_id": pcfg.get("llm"),
            "first_message_sha256": sha256_text(first_message) if isinstance(first_message, str) else None,
            "first_message_length": len(first_message) if isinstance(first_message, str) else None,
            "system_prompt_sha256": sha256_text(system_prompt) if isinstance(system_prompt, str) else None,
            "system_prompt_length": len(system_prompt) if isinstance(system_prompt, str) else None,
            "dynamic_variable_names": dynamic_variable_names(agent),
            "agent_id_sha256": safe_id_fingerprint(agent_id),
            "version_id_sha256": safe_id_fingerprint(version_id),
            "main_branch_id_sha256": safe_id_fingerprint(agent.get("main_branch_id")),
        },
        "branch": branch_snapshot(client, agent_id, branch_id),
        "voice": {
            "name": voice.get("name") if isinstance(voice.get("name"), str) else None,
            "voice_id_sha256": safe_id_fingerprint(voice_id),
            "tts_model_id": tts.get("model_id"),
            "stability": tts.get("stability"),
            "speed": tts.get("speed"),
            "similarity_boost": tts.get("similarity_boost"),
        },
        "procedures": collect_procedures(
            client,
            agent_id,
            branch_id,
            version_id if isinstance(version_id, str) else None,
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--agent-name", default="AI Control")
    args = parser.parse_args(argv)

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        snapshot = collect_provider_snapshot(ApiClient(key), args.agent_name)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(snapshot, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (ProbeError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
