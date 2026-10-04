#!/usr/bin/env python3
"""Issue #40 GET-only classifier for provider-compiled Gate-2 artifacts.

Confirms whether the source-only prompt.tools/workflow deltas are exactly the
provider materialization of the verified Client Tool + Operator procedure.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any

import elevenlabs_client_tool_staging_v1 as staging
import elevenlabs_issue40_preflight_diff_v1 as diffprobe


class ClassifierError(RuntimeError):
    pass


def _exact_procedure_id(agent: dict[str, Any], name: str) -> str:
    procedures = agent.get("procedures")
    if not isinstance(procedures, dict):
        raise ClassifierError("Procedure map is malformed")
    matches = [
        pid
        for pid, meta in procedures.items()
        if isinstance(pid, str)
        and isinstance(meta, dict)
        and meta.get("name") == name
    ]
    if len(matches) != 1:
        raise ClassifierError(f"Expected exactly one Procedure named {name!r}")
    return matches[0]


def _prompt(agent: dict[str, Any]) -> dict[str, Any]:
    prompt = (
        agent.get("conversation_config", {})
        .get("agent", {})
        .get("prompt", {})
    )
    if not isinstance(prompt, dict):
        raise ClassifierError("Prompt config is malformed")
    return prompt


def _safe_expected_subset_diff(
    expected: Any,
    actual: Any,
    path: str = "$",
) -> list[dict[str, Any]]:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [{
                "path": diffprobe.sanitize_path(path),
                "kind": "TYPE_OR_SHAPE_MISMATCH",
                "expected": diffprobe.safe_summary(expected),
                "actual": diffprobe.safe_summary(actual),
            }]
        out: list[dict[str, Any]] = []
        for key, value in expected.items():
            child = f"{path}.{key}"
            if key not in actual:
                out.append({
                    "path": diffprobe.sanitize_path(child),
                    "kind": "MISSING_EXPECTED_FIELD",
                })
            else:
                out.extend(_safe_expected_subset_diff(value, actual[key], child))
        return out
    if isinstance(expected, list):
        if actual != expected:
            return [{
                "path": diffprobe.sanitize_path(path),
                "kind": "LIST_MISMATCH",
                "expected": diffprobe.safe_summary(expected),
                "actual": diffprobe.safe_summary(actual),
            }]
        return []
    if actual != expected:
        return [{
            "path": diffprobe.sanitize_path(path),
            "kind": "VALUE_MISMATCH",
            "expected": diffprobe.safe_summary(expected),
            "actual": diffprobe.safe_summary(actual),
        }]
    return []


def collect(
    client: diffprobe.ReadOnlyClient,
    tool_payload: dict[str, Any],
    expected: dict[str, Any],
) -> dict[str, Any]:
    main = staging.assert_main_baseline(client)
    raw = main["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]

    source_meta = staging.find_exact_existing_branch(client, agent_id)
    source_branch_id = source_meta.get("id")
    if not isinstance(source_branch_id, str) or not source_branch_id:
        raise ClassifierError("Source branch omitted id")

    source_agent = client.get_agent(agent_id, source_branch_id)
    main_agent = client.get_agent(agent_id)

    tool = staging.find_exact_existing_tool(client)
    tool_id = tool.get("id")
    if not isinstance(tool_id, str) or not tool_id:
        raise ClassifierError("Workspace Client Tool omitted id")
    staging.verify_tool_contract(tool, tool_payload)

    main_prompt = copy.deepcopy(_prompt(main_agent))
    source_prompt = copy.deepcopy(_prompt(source_agent))

    if main_prompt.get("tool_ids", []) not in ([], None):
        raise ClassifierError("Main unexpectedly has attached tools")
    if source_prompt.get("tool_ids") != [tool_id]:
        raise ClassifierError("Source tool_ids is not exactly the verified Client Tool")

    main_tools = main_prompt.get("tools", [])
    source_tools = source_prompt.get("tools", [])
    if main_tools is None:
        main_tools = []
    if source_tools is None:
        source_tools = []
    if not isinstance(main_tools, list) or not isinstance(source_tools, list):
        raise ClassifierError("prompt.tools is malformed")
    if main_tools != []:
        raise ClassifierError("Main prompt.tools is not empty")
    if len(source_tools) != 1 or not isinstance(source_tools[0], dict):
        raise ClassifierError("Source prompt.tools is not exactly one materialized tool")

    expected_cfg = tool_payload.get("tool_config")
    if not isinstance(expected_cfg, dict):
        raise ClassifierError("Expected tool_config is malformed")
    prompt_tool_subset_diff = _safe_expected_subset_diff(
        expected_cfg,
        source_tools[0],
        "$.conversation_config.agent.prompt.tools[0]",
    )

    main_cfg = copy.deepcopy(main_agent.get("conversation_config"))
    source_cfg = copy.deepcopy(source_agent.get("conversation_config"))
    if not isinstance(main_cfg, dict) or not isinstance(source_cfg, dict):
        raise ClassifierError("Main/source conversation_config is malformed")
    for cfg in (main_cfg, source_cfg):
        prompt = cfg.get("agent", {}).get("prompt", {})
        if not isinstance(prompt, dict):
            raise ClassifierError("Main/source prompt config is malformed")
        prompt["tool_ids"] = []
        prompt["tools"] = []

    residual_cfg_diff = diffprobe.structural_diff(
        main_cfg,
        source_cfg,
        "$.conversation_config",
    )

    operator_id = _exact_procedure_id(source_agent, "Operator breakdown")
    technician_id = _exact_procedure_id(source_agent, "Technician pre-close")

    operator = staging._procedure_by_name(
        client, source_agent, source_branch_id, "Operator breakdown"
    )
    technician = staging._procedure_by_name(
        client, source_agent, source_branch_id, "Technician pre-close"
    )

    materialized = staging.materialize_operator(expected, tool_id)
    wanted_operator = staging.semantic_procedure_fingerprint(
        {**materialized, "version_id": "expected"}
    )
    wanted_operator["version_present"] = True
    actual_operator = staging.semantic_procedure_fingerprint(operator)
    if actual_operator != wanted_operator:
        raise ClassifierError("Source Operator breakdown no longer matches Gate-2 target")
    actual_technician = staging.semantic_procedure_fingerprint(technician)
    if actual_technician != main["safe"]["technician"]:
        raise ClassifierError("Source Technician pre-close no longer matches Main baseline")

    workflow_diff = diffprobe.structural_diff(
        main_agent.get("workflow"),
        source_agent.get("workflow"),
        "$.workflow",
    )
    operator_token = "__xi_procedure__" + operator_id + "/"
    technician_token = "__xi_procedure__" + technician_id + "/"

    operator_only = all(
        operator_token in item.get("path", "")
        for item in workflow_diff
    )
    # Paths emitted by structural_diff are sanitized. Recompute the accepted
    # sanitized token for exact namespace classification.
    sanitized_operator_token = "__xi_procedure__agtprc_sha256_" + staging.sha256_text(operator_id)[:12] + "/"
    sanitized_technician_token = "__xi_procedure__agtprc_sha256_" + staging.sha256_text(technician_id)[:12] + "/"
    operator_only = all(
        sanitized_operator_token in item.get("path", "")
        for item in workflow_diff
    )
    technician_touched = any(
        sanitized_technician_token in item.get("path", "")
        for item in workflow_diff
    )

    return {
        "schema_version": 1,
        "mode": "ISSUE40_GET_ONLY_COMPILED_ARTIFACT_CLASSIFIER",
        "provider": "ElevenLabs",
        "main_branch_id_sha256": staging.safe_id_fingerprint(main_branch_id),
        "source_branch_id_sha256": staging.safe_id_fingerprint(source_branch_id),
        "tool_id_sha256": staging.safe_id_fingerprint(tool_id),
        "operator_procedure_id_sha256": staging.safe_id_fingerprint(operator_id),
        "technician_procedure_id_sha256": staging.safe_id_fingerprint(technician_id),
        "source_prompt_tools_count": len(source_tools),
        "prompt_tool_expected_subset_diff": prompt_tool_subset_diff,
        "conversation_config_residual_diff_after_tool_materialization_normalization": residual_cfg_diff,
        "workflow_diff_count": len(workflow_diff),
        "workflow_diff_only_in_operator_compiled_namespace": operator_only,
        "workflow_diff_touches_technician_namespace": technician_touched,
        "platform_settings_diff": diffprobe.structural_diff(
            main_agent.get("platform_settings"),
            source_agent.get("platform_settings"),
            "$.platform_settings",
        ),
        "provider_main_write_performed": False,
        "safe_to_rerun_merge_executor": False,
        "classification": (
            "EXPECTED_PROVIDER_COMPILED_ARTIFACTS_ONLY"
            if not prompt_tool_subset_diff
            and not residual_cfg_diff
            and workflow_diff
            and operator_only
            and not technician_touched
            else "UNRESOLVED_PROVIDER_DELTA"
        ),
        "next_gate": "REVIEW_CLASSIFICATION_BEFORE_ANY_PROVIDER_WRITE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    key = os.getenv(staging.API_KEY_ENV)
    if not key:
        print(f"ERROR: {staging.API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        tool_payload = staging.load_object(args.tool_config)
        expected = staging.load_object(args.expected)
        evidence = collect(diffprobe.ReadOnlyClient(key), tool_payload, expected)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (
        ClassifierError,
        diffprobe.DiagnosticError,
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
