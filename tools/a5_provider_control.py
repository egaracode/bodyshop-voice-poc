#!/usr/bin/env python3
"""A5 ElevenLabs provider-control reader/diff.

Read-only by construction: every provider request is GET and endpoint paths are allowlisted.
No API key, provider resource ID, dynamic-variable value, prompt text, procedure body,
personal data, or raw provider response is written to output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
ALLOWED_PATH_PREFIXES = (
    "/v1/convai/agents",
    "/v1/voices/",
)


class HarnessError(RuntimeError):
    pass


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise HarnessError(f"Expected text, got {type(value).__name__}")
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def canonical_structured_content(value: Any) -> str:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise HarnessError("Structured Procedure content is not valid JSON") from exc
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass
class ApiClient:
    api_key: str
    base_url: str = API_BASE

    def get(self, path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
        if not path.startswith(ALLOWED_PATH_PREFIXES):
            raise HarnessError(f"Endpoint is not allowlisted for A5 read-only access: {path}")
        query_string = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}"
        if query_string:
            url = f"{url}?{query_string}"
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "accept": "application/json",
                "xi-api-key": self.api_key,
                "user-agent": "bodyshop-voice-poc-a5-read-only/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            safe_body = ""
            try:
                safe_body = exc.read().decode("utf-8")[:500]
            except Exception:
                pass
            raise HarnessError(f"ElevenLabs GET failed: HTTP {exc.code}; {safe_body}") from exc
        except urllib.error.URLError as exc:
            raise HarnessError(f"ElevenLabs GET failed: {exc.reason}") from exc
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise HarnessError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise HarnessError("ElevenLabs returned an unexpected non-object response")
        return parsed


def find_exact_agent(client: ApiClient, name: str) -> dict[str, Any]:
    cursor: str | None = None
    matches: list[dict[str, Any]] = []
    while True:
        query = {"page_size": "100", "search": name, "archived": "false"}
        if cursor:
            query["cursor"] = cursor
        page = client.get("/v1/convai/agents", query)
        for item in page.get("agents", []):
            if isinstance(item, dict) and item.get("name") == name and not item.get("archived", False):
                matches.append(item)
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
        if not cursor:
            raise HarnessError("Agent pagination advertised has_more without next_cursor")
    if len(matches) != 1:
        raise HarnessError(
            f"Expected exactly one non-archived agent named {name!r}; found {len(matches)}"
        )
    return matches[0]


def safe_id_fingerprint(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return sha256_text(value)


def extract_dynamic_variable_names(agent: dict[str, Any]) -> list[str] | None:
    node = (
        agent.get("conversation_config", {})
        .get("agent", {})
        .get("dynamic_variables", {})
        .get("dynamic_variable_placeholders")
    )
    if node is None:
        return None
    if not isinstance(node, dict):
        raise HarnessError("dynamic_variable_placeholders is not an object")
    return sorted(str(key) for key in node.keys())


def get_voice_name(client: ApiClient, voice_id: Any) -> str | None:
    if not isinstance(voice_id, str) or not voice_id:
        return None
    voice = client.get(f"/v1/voices/{urllib.parse.quote(voice_id, safe='')}")
    name = voice.get("name")
    return name if isinstance(name, str) else None


def collect_procedures(
    client: ApiClient,
    agent_id: str,
    branch_id: Any,
    agent_version_id: Any,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    if not isinstance(branch_id, str) or not branch_id:
        return None, "Provider did not expose branch_id; Procedures API requires branch_id."
    base = (
        f"/v1/convai/agents/{urllib.parse.quote(agent_id, safe='')}"
        f"/branches/{urllib.parse.quote(branch_id, safe='')}/procedures"
    )
    query: dict[str, str] = {}
    if isinstance(agent_version_id, str) and agent_version_id:
        query["agent_version_id"] = agent_version_id
    listing = client.get(base, query or None)
    normalized: list[dict[str, Any]] = []
    for meta in listing.get("procedures", []):
        if not isinstance(meta, dict):
            continue
        procedure_id = meta.get("procedure_id")
        if not isinstance(procedure_id, str) or not procedure_id:
            raise HarnessError("Procedure listing omitted procedure_id")
        full = client.get(
            f"{base}/{urllib.parse.quote(procedure_id, safe='')}",
            query or None,
        )
        p_type = full.get("type", meta.get("type", "free_form"))
        raw_content = full.get("content", "")
        if p_type == "structured":
            canonical = canonical_structured_content(raw_content)
        else:
            canonical = normalize_text(raw_content)
            if canonical is None:
                canonical = ""
        trigger = normalize_text(full.get("trigger", meta.get("trigger", ""))) or ""
        normalized.append(
            {
                "name": full.get("name", meta.get("name")),
                "type": p_type,
                "trigger": trigger,
                "content_canonical": canonical,
                "content_sha256": sha256_text(canonical),
                "has_draft": bool(meta.get("has_draft", False)),
                "procedure_version_present": bool(full.get("version_id") or meta.get("version_id")),
            }
        )
    normalized.sort(key=lambda item: str(item.get("name")))
    return normalized, None


def collect_provider_state(client: ApiClient, agent_name: str) -> dict[str, Any]:
    listed = find_exact_agent(client, agent_name)
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise HarnessError("Matched agent omitted agent_id")
    agent = client.get(f"/v1/convai/agents/{urllib.parse.quote(agent_id, safe='')}")
    config = agent.get("conversation_config", {})
    agent_cfg = config.get("agent", {})
    prompt_cfg = agent_cfg.get("prompt", {})
    tts_cfg = config.get("tts", {})
    branch_id = agent.get("branch_id")
    version_id = agent.get("version_id")
    procedures, procedures_gap = collect_procedures(
        client, agent_id, branch_id, version_id
    )
    first_message = normalize_text(agent_cfg.get("first_message"))
    system_prompt = normalize_text(prompt_cfg.get("prompt"))
    voice_name = get_voice_name(client, tts_cfg.get("voice_id"))
    return {
        "agent": {
            "name": agent.get("name"),
            "language": agent_cfg.get("language"),
            "first_message": first_message,
            "system_prompt": system_prompt,
            "llm": prompt_cfg.get("llm"),
            "voice_name": voice_name,
            "dynamic_variable_names": extract_dynamic_variable_names(agent),
        },
        "procedures": procedures,
        "procedures_gap": procedures_gap,
        "provider_metadata": {
            "version_present": isinstance(version_id, str) and bool(version_id),
            "branch_present": isinstance(branch_id, str) and bool(branch_id),
            "main_branch_present": isinstance(agent.get("main_branch_id"), str)
            and bool(agent.get("main_branch_id")),
            "version_id_sha256": safe_id_fingerprint(version_id),
            "branch_id_sha256": safe_id_fingerprint(branch_id),
            "main_branch_id_sha256": safe_id_fingerprint(agent.get("main_branch_id")),
        },
    }


def result(
    field: str,
    status: str,
    expected: Any = None,
    actual: Any = None,
    note: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"field": field, "status": status}
    if expected is not None:
        item["expected"] = expected
    if actual is not None:
        item["actual"] = actual
    if note:
        item["note"] = note
    return item


def compare_expected(expected: dict[str, Any], actual: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    exp_agent = expected["agent"]
    act_agent = actual["agent"]

    scalar_fields = {
        "agent.name": (exp_agent.get("name"), act_agent.get("name")),
        "agent.language": (exp_agent.get("language"), act_agent.get("language")),
        "agent.llm": (exp_agent.get("llm"), act_agent.get("llm")),
        "agent.voice.name": (
            exp_agent.get("voice", {}).get("name"),
            act_agent.get("voice_name"),
        ),
    }
    for field, (exp_value, act_value) in scalar_fields.items():
        if act_value is None:
            results.append(result(field, "UNVERIFIABLE", expected=exp_value))
        else:
            results.append(
                result(
                    field,
                    "NO_DRIFT" if exp_value == act_value else "DRIFT",
                    expected=exp_value,
                    actual=act_value,
                )
            )

    for field, key in (
        ("agent.first_message", "first_message"),
        ("agent.system_prompt", "system_prompt"),
    ):
        exp_text = normalize_text(exp_agent.get(key))
        act_text = normalize_text(act_agent.get(key))
        if act_text is None:
            results.append(
                {
                    "field": field,
                    "status": "UNVERIFIABLE",
                    "expected_sha256": sha256_text(exp_text or ""),
                    "expected_length": len(exp_text or ""),
                }
            )
            continue
        results.append(
            {
                "field": field,
                "status": "NO_DRIFT" if exp_text == act_text else "DRIFT",
                "expected_sha256": sha256_text(exp_text or ""),
                "actual_sha256": sha256_text(act_text),
                "expected_length": len(exp_text or ""),
                "actual_length": len(act_text),
            }
        )

    exp_vars = sorted(exp_agent.get("dynamic_variable_names", []))
    act_vars = act_agent.get("dynamic_variable_names")
    if act_vars is None:
        results.append(result("agent.dynamic_variable_names", "UNVERIFIABLE", expected=exp_vars))
    else:
        results.append(
            result(
                "agent.dynamic_variable_names",
                "NO_DRIFT" if exp_vars == sorted(act_vars) else "DRIFT",
                expected=exp_vars,
                actual=sorted(act_vars),
            )
        )

    exp_procs = {p["name"]: p for p in expected.get("procedures", [])}
    act_procs_raw = actual.get("procedures")
    if act_procs_raw is None:
        note = actual.get("procedures_gap") or "Procedures unavailable"
        for name in sorted(exp_procs):
            results.append(result(f"procedures.{name}", "UNVERIFIABLE", note=note))
        return results

    act_procs = {p.get("name"): p for p in act_procs_raw if p.get("name")}
    for name in sorted(set(exp_procs) | set(act_procs)):
        exp = exp_procs.get(name)
        act = act_procs.get(name)
        if exp is None:
            results.append(result(f"procedures.{name}", "DRIFT", note="Unexpected provider Procedure"))
            continue
        if act is None:
            results.append(result(f"procedures.{name}", "DRIFT", note="Expected Procedure missing"))
            continue
        results.append(
            result(
                f"procedures.{name}.type",
                "NO_DRIFT" if exp.get("type") == act.get("type") else "DRIFT",
                expected=exp.get("type"),
                actual=act.get("type"),
            )
        )
        exp_trigger = normalize_text(exp.get("trigger")) or ""
        act_trigger = normalize_text(act.get("trigger")) or ""
        results.append(
            {
                "field": f"procedures.{name}.trigger",
                "status": "NO_DRIFT" if exp_trigger == act_trigger else "DRIFT",
                "expected_sha256": sha256_text(exp_trigger),
                "actual_sha256": sha256_text(act_trigger),
            }
        )
        if exp.get("type") == "structured":
            exp_content = canonical_structured_content(exp.get("content"))
        else:
            exp_content = normalize_text(exp.get("content")) or ""
        act_content = act.get("content_canonical")
        if not isinstance(act_content, str):
            results.append(result(f"procedures.{name}.content", "UNVERIFIABLE"))
        else:
            results.append(
                {
                    "field": f"procedures.{name}.content",
                    "status": "NO_DRIFT" if exp_content == act_content else "DRIFT",
                    "expected_sha256": sha256_text(exp_content),
                    "actual_sha256": sha256_text(act_content),
                    "expected_length": len(exp_content),
                    "actual_length": len(act_content),
                }
            )
        if act.get("has_draft"):
            results.append(
                result(
                    f"procedures.{name}.has_draft",
                    "DRIFT",
                    actual=True,
                    note="Provider reports unpublished draft changes for this Procedure.",
                )
            )
    return results


def sanitized_snapshot(actual: dict[str, Any]) -> dict[str, Any]:
    agent = actual["agent"]
    safe: dict[str, Any] = {
        "agent": {
            "name": agent.get("name"),
            "language": agent.get("language"),
            "llm": agent.get("llm"),
            "voice_name": agent.get("voice_name"),
            "dynamic_variable_names": agent.get("dynamic_variable_names"),
            "first_message_sha256": sha256_text(agent["first_message"])
            if isinstance(agent.get("first_message"), str)
            else None,
            "first_message_length": len(agent["first_message"])
            if isinstance(agent.get("first_message"), str)
            else None,
            "system_prompt_sha256": sha256_text(agent["system_prompt"])
            if isinstance(agent.get("system_prompt"), str)
            else None,
            "system_prompt_length": len(agent["system_prompt"])
            if isinstance(agent.get("system_prompt"), str)
            else None,
        },
        "provider_metadata": actual["provider_metadata"],
        "procedures_gap": actual.get("procedures_gap"),
        "procedures": [],
    }
    if actual.get("procedures") is not None:
        for p in actual["procedures"]:
            safe["procedures"].append(
                {
                    "name": p.get("name"),
                    "type": p.get("type"),
                    "trigger_sha256": sha256_text(p.get("trigger", "")),
                    "content_sha256": p.get("content_sha256"),
                    "content_length": len(p.get("content_canonical", "")),
                    "has_draft": p.get("has_draft"),
                    "procedure_version_present": p.get("procedure_version_present"),
                }
            )
    return safe


def overall_status(results: list[dict[str, Any]]) -> str:
    statuses = {r["status"] for r in results}
    if "DRIFT" in statuses:
        return "DRIFT"
    if "UNVERIFIABLE" in statuses:
        return "UNVERIFIABLE"
    return "NO_DRIFT"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True, help="Path to A5 expected configuration JSON")
    parser.add_argument("--agent-name", default="AI Control")
    parser.add_argument("--output", help="Optional sanitized JSON output path")
    args = parser.parse_args(argv)

    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        print(
            f"ERROR: {API_KEY_ENV} is not set. Do not paste the secret into chat or commit it.",
            file=sys.stderr,
        )
        return 2

    with open(args.expected, "r", encoding="utf-8") as handle:
        expected = json.load(handle)

    try:
        actual = collect_provider_state(ApiClient(api_key), args.agent_name)
        results = compare_expected(expected, actual)
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = {
        "schema_version": 1,
        "authority": expected.get("authority", {}).get("name"),
        "overall": overall_status(results),
        "snapshot": sanitized_snapshot(actual),
        "results": results,
        "read_only_invariant": {
            "http_methods": ["GET"],
            "provider_write_performed": False,
            "publish_performed": False,
            "versioning_mutation_performed": False,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered + "\n")
    print(rendered)
    return 0 if report["overall"] == "NO_DRIFT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
