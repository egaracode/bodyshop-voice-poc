#!/usr/bin/env python3
"""Issue #38 GET-only recovery probe after interrupted staging."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from elevenlabs_client_tool_contract_v1 import (
    API_KEY_ENV,
    ApiClient,
    ContractError,
    find_exact_agent,
    safe_id_fingerprint,
)

BRANCH_NAME = "bodyshop-client-tool-issue-38"
TOOL_NAME = "bodyshop_resolve_confirmed_intake"


class RecoveryError(RuntimeError):
    pass


def schema_diff(expected: Any, actual: Any, path: str = "$") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [{"path": path, "kind": "TYPE_OR_SHAPE_MISMATCH"}]
        for key, value in expected.items():
            child = f"{path}.{key}"
            if key not in actual:
                out.append({"path": child, "kind": "MISSING_IN_PROVIDER_READBACK"})
            else:
                out.extend(schema_diff(value, actual[key], child))
        for key in sorted(set(actual) - set(expected)):
            out.append({
                "path": f"{path}.{key}",
                "kind": "PROVIDER_EXTRA_FIELD",
                "actual": actual[key],
            })
        return out
    if expected != actual:
        out.append({
            "path": path,
            "kind": "VALUE_MISMATCH",
            "expected": expected,
            "actual": actual,
        })
    return out


def exact_branch(client: ApiClient, agent_id: str) -> dict[str, Any] | None:
    page = client._get(
        f"/v1/convai/agents/{agent_id}/branches",
        {
            "include_archived": "true",
            "include_commit_status": "true",
            "limit": "100",
        },
    )
    rows = page.get("results", [])
    if not isinstance(rows, list):
        raise RecoveryError("Branch listing omitted results")
    matches = [
        row for row in rows
        if isinstance(row, dict) and row.get("name") == BRANCH_NAME
    ]
    if len(matches) > 1:
        raise RecoveryError(f"Found {len(matches)} matching branches")
    return matches[0] if matches else None


def exact_tool(client: ApiClient) -> dict[str, Any] | None:
    page = client._get(
        "/v1/convai/tools",
        {
            "page_size": "100",
            "search": TOOL_NAME,
            "sort_by": "name",
            "sort_direction": "asc",
        },
    )
    rows = page.get("tools", [])
    if not isinstance(rows, list):
        raise RecoveryError("Tool listing omitted tools")
    matches = [
        row for row in rows
        if isinstance(row, dict)
        and isinstance(row.get("tool_config"), dict)
        and row["tool_config"].get("name") == TOOL_NAME
    ]
    if len(matches) > 1:
        raise RecoveryError(f"Found {len(matches)} matching tools")
    return matches[0] if matches else None


def safe_agent(agent: dict[str, Any], target_tool_id: str | None) -> dict[str, Any]:
    prompt = (
        agent.get("conversation_config", {})
        .get("agent", {})
        .get("prompt", {})
    )
    if not isinstance(prompt, dict):
        raise RecoveryError("Agent prompt config is malformed")
    tool_ids = prompt.get("tool_ids", []) or []
    if not isinstance(tool_ids, list) or any(not isinstance(x, str) for x in tool_ids):
        raise RecoveryError("Agent tool_ids is malformed")

    procedures = agent.get("procedures", {})
    rows = []
    if isinstance(procedures, dict):
        for pid, meta in procedures.items():
            if isinstance(pid, str) and isinstance(meta, dict):
                rows.append({
                    "name": meta.get("name"),
                    "type": meta.get("type"),
                    "procedure_id_sha256": safe_id_fingerprint(pid),
                    "version_id_sha256": safe_id_fingerprint(meta.get("version_id")),
                })
    rows.sort(key=lambda x: (str(x["name"]), str(x["type"])))
    return {
        "branch_id_sha256": safe_id_fingerprint(agent.get("branch_id")),
        "main_branch_id_sha256": safe_id_fingerprint(agent.get("main_branch_id")),
        "version_id_sha256": safe_id_fingerprint(agent.get("version_id")),
        "tool_count": len(tool_ids),
        "tool_id_sha256": [safe_id_fingerprint(x) for x in tool_ids],
        "target_tool_attached": bool(target_tool_id and target_tool_id in tool_ids),
        "procedures": rows,
    }


def collect(client: ApiClient, expected_tool_payload: dict[str, Any]) -> dict[str, Any]:
    listed = find_exact_agent(client, "AI Control")
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise RecoveryError("Matched agent omitted agent_id")

    main = client.get_agent(agent_id)
    branch = exact_branch(client, agent_id)
    tool = exact_tool(client)

    tool_id = None
    actual_tool = None
    if tool is not None:
        tool_id = tool.get("id")
        if not isinstance(tool_id, str) or not tool_id:
            raise RecoveryError("Matched tool omitted id")
        actual_tool = client._get(f"/v1/convai/tools/{tool_id}")

    branch_safe = None
    isolated_safe = None
    if branch is not None:
        branch_id = branch.get("id")
        if not isinstance(branch_id, str) or not branch_id:
            raise RecoveryError("Matched branch omitted id")
        parent_id = branch.get("parent_branch_id")
        branch_safe = {
            "name": branch.get("name"),
            "description": branch.get("description"),
            "branch_id_sha256": safe_id_fingerprint(branch_id),
            "parent_branch_id_sha256": safe_id_fingerprint(parent_id),
            "current_live_percentage": branch.get("current_live_percentage"),
            "draft_exists": branch.get("draft_exists"),
            "is_archived": branch.get("is_archived"),
            "commits_ahead": branch.get("commits_ahead"),
            "commits_behind": branch.get("commits_behind"),
        }
        isolated_agent = client._get(
            f"/v1/convai/agents/{agent_id}",
            {"branch_id": branch_id},
        )
        isolated_safe = safe_agent(isolated_agent, tool_id)

    expected_cfg = expected_tool_payload.get("tool_config")
    if not isinstance(expected_cfg, dict):
        raise RecoveryError("Expected tool_config malformed")
    expected_parameters = expected_cfg.get("parameters")
    if not isinstance(expected_parameters, dict):
        raise RecoveryError("Expected parameters malformed")

    tool_safe = None
    if actual_tool is not None:
        actual_cfg = actual_tool.get("tool_config")
        if not isinstance(actual_cfg, dict):
            raise RecoveryError("Actual tool_config malformed")
        actual_parameters = actual_cfg.get("parameters")
        if not isinstance(actual_parameters, dict):
            raise RecoveryError("Actual parameters malformed")
        tool_safe = {
            "tool_id_sha256": safe_id_fingerprint(tool_id),
            "core": {
                "type": actual_cfg.get("type"),
                "name": actual_cfg.get("name"),
                "description": actual_cfg.get("description"),
                "expects_response": actual_cfg.get("expects_response"),
            },
            "actual_parameters": actual_parameters,
            "expected_parameters": expected_parameters,
            "parameter_schema_diff": schema_diff(expected_parameters, actual_parameters),
            "provider_extra_tool_config_keys": sorted(set(actual_cfg) - set(expected_cfg)),
        }

    if branch is not None and tool is not None and isolated_safe and isolated_safe["target_tool_attached"]:
        progress = "TOOL_ATTACHED_OR_LATER"
    elif branch is not None and tool is not None:
        progress = "BRANCH_AND_TOOL_CREATED_NOT_ATTACHED"
    elif branch is not None:
        progress = "BRANCH_CREATED_TOOL_NOT_FOUND"
    elif tool is not None:
        progress = "TOOL_CREATED_BRANCH_NOT_FOUND"
    else:
        progress = "NO_PARTIAL_WRITE_OBSERVED"

    return {
        "schema_version": 1,
        "mode": "ISSUE38_GET_ONLY_RECOVERY_PROBE",
        "provider": "ElevenLabs",
        "main": safe_agent(main, tool_id),
        "isolated_branch": branch_safe,
        "isolated_agent": isolated_safe,
        "workspace_tool": tool_safe,
        "write_progress_classification": progress,
        "safe_to_rerun_original_staging": False,
        "next_gate": "REVIEW_RECOVERY_EVIDENCE_BEFORE_ANY_PROVIDER_WRITE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2
    try:
        with open(args.tool_config, encoding="utf-8") as handle:
            expected = json.load(handle)
        evidence = collect(ApiClient(key), expected)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (ContractError, RecoveryError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
