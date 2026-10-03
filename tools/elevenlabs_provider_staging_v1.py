#!/usr/bin/env python3
"""Controlled ElevenLabs provider staging executor for BODYSHOP #34.

Gate A only:
1) re-read and verify exact provider baseline;
2) create isolated provider branch from exact Main version;
3) verify branch parent and current_live_percentage == 0;
4) create replacement deterministic Operator breakdown;
5) update Technician pre-close draft;
6) publish staged Procedure drafts on the isolated branch;
7) read back staged Procedures and verify exact hashes.

This tool cannot publish the final reconciled agent config and cannot merge to Main.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from elevenlabs_provider_reconciliation_v1 import (
    API_BASE,
    API_KEY_ENV,
    CURRENT_PROVIDER_GUARD_V1,
    PlannerError,
    assert_current_provider_guard,
    canonical_json,
    collect_live_state,
    content_shape,
    derive_expected_target,
    ensure_provider_branch_name_available,
    normalize_text,
    safe_id_fingerprint,
    safe_identifier,
    sha256_text,
)

STAGING_BRANCH_NAME = "bodyshop-a5-reconcile-issue-34"
STAGING_DESCRIPTION = "BODYSHOP #34 isolated A5 reconciliation staging"
VERSION_DESCRIPTION = "BODYSHOP #34 stage Procedure versions"


class StagingError(RuntimeError):
    pass


class StagingClient:
    """GET + narrowly-scoped POST/PATCH client for Gate A only."""

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
        q = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}" + (f"?{q}" if q else "")
        payload = None
        headers = {
            "accept": "application/json",
            "xi-api-key": self.api_key,
            "user-agent": "bodyshop-voice-poc-elevenlabs-staging-v1/1",
        }
        if body is not None:
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["content-type"] = "application/json"
        request = urllib.request.Request(url, data=payload, method=method, headers=headers)
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


def get_branch(client: StagingClient, agent_id: str, branch_id: str) -> dict[str, Any]:
    aid = safe_identifier(agent_id, "agent_id")
    bid = safe_identifier(branch_id, "branch_id")
    return client.get(f"/v1/convai/agents/{aid}/branches/{bid}")


def get_procedure(
    client: StagingClient,
    agent_id: str,
    branch_id: str,
    procedure_id: str,
    agent_version_id: str,
) -> dict[str, Any]:
    aid = safe_identifier(agent_id, "agent_id")
    bid = safe_identifier(branch_id, "branch_id")
    pid = safe_identifier(procedure_id, "procedure_id")
    return client.get(
        f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}",
        {"agent_version_id": agent_version_id},
    )


def procedure_fingerprint(item: dict[str, Any]) -> dict[str, Any]:
    name = item.get("name")
    raw_type = item.get("type")
    trigger = normalize_text(item.get("trigger", ""))
    if trigger is None:
        trigger = ""
    shape, canonical_content = content_shape(item.get("content"))
    return {
        "name": name,
        "raw_api_type": raw_type,
        "content_shape": shape,
        "trigger_sha256": sha256_text(trigger),
        "trigger_length": len(trigger),
        "content_sha256": sha256_text(canonical_content),
        "content_length": len(canonical_content),
        "version_present": bool(item.get("version_id")),
    }


def expected_procedure_fingerprint(target: dict[str, Any], name: str) -> dict[str, Any]:
    item = target["procedures"][name]
    return {
        "name": name,
        "raw_api_type": item["target_api_type"],
        "content_shape": "JSON_STEPS" if name == "Operator breakdown" else "TEXT",
        "trigger_sha256": item["trigger_sha256"],
        "trigger_length": item["trigger_length"],
        "content_sha256": item["content_sha256"],
        "content_length": item["content_length"],
        "version_present": True,
    }


def execute_staging(
    read_client: Any,
    write_client: StagingClient,
    expected: dict[str, Any],
    branch_name: str = STAGING_BRANCH_NAME,
) -> dict[str, Any]:
    target = derive_expected_target(expected)

    # Re-read immediately before the first write.
    live = collect_live_state(read_client, "AI Control")
    assert_current_provider_guard(live["safe_guard"], CURRENT_PROVIDER_GUARD_V1)
    ensure_provider_branch_name_available(read_client, live["raw"]["agent_id"], branch_name)

    raw = live["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    source_version_id = raw["version_id"]
    tech_pid = raw["procedure_ids_by_name"].get("Technician pre-close")
    if not isinstance(tech_pid, str) or not tech_pid:
        raise StagingError("Technician pre-close identity missing from guarded baseline")

    aid = safe_identifier(agent_id, "agent_id")

    created = write_client.post(
        f"/v1/convai/agents/{aid}/branches",
        {
            "parent_version_id": source_version_id,
            "name": branch_name,
            "description": STAGING_DESCRIPTION,
            "include_draft": False,
        },
    )
    isolated_branch_id = created.get("created_branch_id")
    if not isinstance(isolated_branch_id, str) or not isolated_branch_id:
        raise StagingError("Create branch response omitted created_branch_id")

    # Mandatory readback before Procedure mutation.
    branch = get_branch(write_client, agent_id, isolated_branch_id)
    parent = branch.get("parent_branch")
    parent_id = parent.get("id") if isinstance(parent, dict) else None
    if parent_id != main_branch_id:
        raise StagingError("Isolated branch parent does not match guarded Main branch")
    if branch.get("current_live_percentage", 0) != 0:
        raise StagingError("Isolated branch unexpectedly has live traffic")
    if branch.get("name") != branch_name:
        raise StagingError("Isolated branch name mismatch")

    operator = expected["procedures"][0]
    technician = expected["procedures"][1]
    by_name = {item["name"]: item for item in expected["procedures"]}
    operator = by_name["Operator breakdown"]
    technician = by_name["Technician pre-close"]

    bid = safe_identifier(isolated_branch_id, "branch_id")

    new_operator = write_client.post(
        f"/v1/convai/agents/{aid}/branches/{bid}/procedures",
        {
            "name": "Operator breakdown",
            "content": canonical_json(operator["content"]),
            "type": "deterministic",
            "trigger": operator["trigger"],
        },
    )
    operator_pid = new_operator.get("procedure_id")
    if not isinstance(operator_pid, str) or not operator_pid:
        raise StagingError("Create Procedure response omitted procedure_id")

    tpid = safe_identifier(tech_pid, "procedure_id")
    write_client.patch(
        f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{tpid}/draft",
        {
            "name": "Technician pre-close",
            "content": technician["content"],
            "type": "free_form",
            "trigger": technician["trigger"],
        },
    )

    published = write_client.patch(
        f"/v1/convai/agents/{aid}",
        {"version_description": VERSION_DESCRIPTION},
        {"branch_id": isolated_branch_id},
    )
    staged_version_id = published.get("version_id")
    if not isinstance(staged_version_id, str) or not staged_version_id:
        raise StagingError("Publish response omitted version_id")

    operator_live = get_procedure(
        write_client, agent_id, isolated_branch_id, operator_pid, staged_version_id
    )
    technician_live = get_procedure(
        write_client, agent_id, isolated_branch_id, tech_pid, staged_version_id
    )

    operator_fp = procedure_fingerprint(operator_live)
    technician_fp = procedure_fingerprint(technician_live)
    expected_operator = expected_procedure_fingerprint(target, "Operator breakdown")
    expected_technician = expected_procedure_fingerprint(target, "Technician pre-close")
    if operator_fp != expected_operator:
        raise StagingError("Staged Operator breakdown failed exact fingerprint verification")
    if technician_fp != expected_technician:
        raise StagingError("Staged Technician pre-close failed exact fingerprint verification")

    return {
        "schema_version": 1,
        "mode": "GATE_A_STAGING_EXECUTED",
        "provider": "ElevenLabs",
        "issue": 34,
        "branch": {
            "name": branch_name,
            "branch_id_sha256": safe_id_fingerprint(isolated_branch_id),
            "parent_branch_id_sha256": safe_id_fingerprint(main_branch_id),
            "current_live_percentage": branch.get("current_live_percentage", 0),
            "staged_version_id_sha256": safe_id_fingerprint(staged_version_id),
        },
        "staged_procedures": {
            "Operator breakdown": {
                **operator_fp,
                "procedure_id_sha256": safe_id_fingerprint(operator_pid),
            },
            "Technician pre-close": {
                **technician_fp,
                "procedure_id_sha256": safe_id_fingerprint(tech_pid),
            },
        },
        "next_gate": "FINAL_ISOLATED_CONFIG_APPROVAL_REQUIRED",
        "provider_main_modified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-staging", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_staging:
        print("ERROR: --execute-staging is required; no provider write performed", file=sys.stderr)
        return 2

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        with open(args.expected, encoding="utf-8") as handle:
            expected = json.load(handle)

        # Import the GET-only client only after execution is explicitly requested.
        from elevenlabs_provider_reconciliation_v1 import ApiClient

        read_client = ApiClient(key)
        write_client = StagingClient(key)
        evidence = execute_staging(read_client, write_client, expected)
        encoded = json.dumps(evidence, ensure_ascii=False, indent=2)

        # Raw provider IDs are never written to evidence.
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.write("\n")
    except (PlannerError, StagingError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
