#!/usr/bin/env python3
"""Issue #40 GET-only preflight diff after provider Main merge guard stopped.

Produces sanitized structural differences between provider Main and the exact
isolated Gate-2 branch. It is intentionally incapable of POST/PATCH/PUT/DELETE.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any

import elevenlabs_client_tool_staging_v1 as staging


class DiagnosticError(RuntimeError):
    pass


class ReadOnlyClient(staging.ProviderClient):
    """Hard GET-only client even though the shared parent supports staging writes."""

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if method != "GET":
            raise DiagnosticError(f"GET-only diagnostic rejected method {method}")
        return super()._request(method, path, body=None, query=query)


def safe_summary(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if isinstance(value, (int, float)):
        return {"type": type(value).__name__, "value": value}
    if isinstance(value, str):
        return {
            "type": "str",
            "length": len(value),
            "sha256": staging.sha256_text(value),
        }
    if isinstance(value, list):
        return {"type": "list", "length": len(value)}
    if isinstance(value, dict):
        return {"type": "object", "key_count": len(value)}
    return {"type": type(value).__name__}


def structural_diff(main: Any, source: Any, path: str = "$") -> list[dict[str, Any]]:
    if isinstance(main, dict) and isinstance(source, dict):
        out: list[dict[str, Any]] = []
        for key in sorted(set(main) | set(source)):
            child = f"{path}.{key}"
            if key not in main:
                out.append({
                    "path": child,
                    "kind": "SOURCE_EXTRA_FIELD",
                    "source": safe_summary(source[key]),
                })
            elif key not in source:
                out.append({
                    "path": child,
                    "kind": "SOURCE_MISSING_FIELD",
                    "main": safe_summary(main[key]),
                })
            else:
                out.extend(structural_diff(main[key], source[key], child))
        return out

    if isinstance(main, list) and isinstance(source, list):
        if len(main) != len(source):
            return [{
                "path": path,
                "kind": "LIST_LENGTH_MISMATCH",
                "main": safe_summary(main),
                "source": safe_summary(source),
            }]
        out: list[dict[str, Any]] = []
        for index, (m_value, s_value) in enumerate(zip(main, source)):
            out.extend(structural_diff(m_value, s_value, f"{path}[{index}]"))
        return out

    if type(main) is not type(source):
        return [{
            "path": path,
            "kind": "TYPE_MISMATCH",
            "main": safe_summary(main),
            "source": safe_summary(source),
        }]

    if main != source:
        return [{
            "path": path,
            "kind": "VALUE_MISMATCH",
            "main": safe_summary(main),
            "source": safe_summary(source),
        }]
    return []


def collect(client: ReadOnlyClient) -> dict[str, Any]:
    main = staging.assert_main_baseline(client)
    raw = main["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]

    source_meta = staging.find_exact_existing_branch(client, agent_id)
    source_branch_id = source_meta.get("id")
    if not isinstance(source_branch_id, str) or not source_branch_id:
        raise DiagnosticError("Source branch omitted id")

    source_branch = client.get_branch(agent_id, source_branch_id)
    staging.verify_isolated_branch(source_branch, main_branch_id=main_branch_id)

    main_agent = client.get_agent(agent_id)
    source_agent = client.get_agent(agent_id, source_branch_id)

    main_cfg = copy.deepcopy(main_agent.get("conversation_config"))
    source_cfg = copy.deepcopy(source_agent.get("conversation_config"))
    if not isinstance(main_cfg, dict) or not isinstance(source_cfg, dict):
        raise DiagnosticError("Main/source conversation_config is malformed")

    for cfg in (main_cfg, source_cfg):
        prompt = cfg.get("agent", {}).get("prompt", {})
        if not isinstance(prompt, dict):
            raise DiagnosticError("Main/source prompt config is malformed")
        # Tool attachment is the accepted intended delta, so remove it before
        # classifying any additional conversation_config movement.
        prompt["tool_ids"] = []

    return {
        "schema_version": 1,
        "mode": "ISSUE40_GET_ONLY_PREFLIGHT_DIFF",
        "provider": "ElevenLabs",
        "main_branch_id_sha256": staging.safe_id_fingerprint(main_branch_id),
        "source_branch_id_sha256": staging.safe_id_fingerprint(source_branch_id),
        "source_branch": {
            "name": source_meta.get("name"),
            "current_live_percentage": source_meta.get("current_live_percentage"),
            "draft_exists": source_meta.get("draft_exists"),
            "is_archived": source_meta.get("is_archived"),
            "commits_ahead": source_meta.get("commits_ahead"),
            "commits_behind": source_meta.get("commits_behind"),
        },
        "conversation_config_diff_after_tool_ids_normalization": structural_diff(
            main_cfg, source_cfg, "$.conversation_config"
        ),
        "platform_settings_diff": structural_diff(
            main_agent.get("platform_settings"),
            source_agent.get("platform_settings"),
            "$.platform_settings",
        ),
        "workflow_diff": structural_diff(
            main_agent.get("workflow"),
            source_agent.get("workflow"),
            "$.workflow",
        ),
        "provider_main_write_performed": False,
        "safe_to_rerun_merge_executor": False,
        "next_gate": "REVIEW_GET_ONLY_DIFF_BEFORE_ANY_PROVIDER_WRITE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    key = os.getenv(staging.API_KEY_ENV)
    if not key:
        print(f"ERROR: {staging.API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        evidence = collect(ReadOnlyClient(key))
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (DiagnosticError, staging.StagingError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
