#!/usr/bin/env python3
"""BODYSHOP #40 — merge verified Gate-2 ElevenLabs branch into provider Main.

Authorized scope:
- exact A5 Main stale-write guard;
- exact Gate-2 isolated source verification;
- GET merge preview with explicit Main target and force=false;
- one non-force merge with source archival;
- exact post-merge Main/source readback;
- sanitized evidence only.

No Gate-3 conversation execution, Supabase, Production, or lifecycle mutation.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any

import elevenlabs_client_tool_staging_v1 as staging
import elevenlabs_issue40_compiled_artifact_classifier_v1 as classifier

MERGE_FORCE = False
MERGE_ARCHIVE_SOURCE = True
ISSUE = 40


class ProviderMainMergeError(RuntimeError):
    pass


class ProviderMainMergeClient(staging.ProviderClient):
    """Narrow merge client: inherited GET plus POST with explicit query."""

    def post_with_query(
        self,
        path: str,
        body: dict[str, Any],
        query: dict[str, str],
    ) -> dict[str, Any]:
        return self._request("POST", path, body=body, query=query)


def _validate_source_branch_meta(
    branch: dict[str, Any],
    *,
    main_branch_id: str,
) -> None:
    if branch.get("name") != staging.STAGING_BRANCH_NAME:
        raise ProviderMainMergeError("Source branch name mismatch")
    if branch.get("description") != staging.STAGING_DESCRIPTION:
        raise ProviderMainMergeError("Source branch description mismatch")
    parent = branch.get("parent_branch_id")
    if not isinstance(parent, str):
        nested = branch.get("parent_branch")
        parent = nested.get("id") if isinstance(nested, dict) else None
    if parent != main_branch_id:
        raise ProviderMainMergeError("Source branch parent is not exact Main")
    if branch.get("current_live_percentage") not in (0, 0.0):
        raise ProviderMainMergeError("Source branch unexpectedly has live traffic")
    if bool(branch.get("draft_exists", False)):
        raise ProviderMainMergeError("Source branch unexpectedly has a draft")
    if bool(branch.get("is_archived", False)):
        raise ProviderMainMergeError("Source branch is already archived")
    if branch.get("commits_behind") != 0:
        raise ProviderMainMergeError("Source branch is behind Main")
    ahead = branch.get("commits_ahead")
    if not isinstance(ahead, int) or ahead <= 0:
        raise ProviderMainMergeError("Source branch has no mergeable changes")


def _effective_tool_ids(agent: dict[str, Any]) -> list[str]:
    prompt = (
        agent.get("conversation_config", {})
        .get("agent", {})
        .get("prompt", {})
    )
    if not isinstance(prompt, dict):
        raise ProviderMainMergeError("Agent prompt config is malformed")
    tool_ids = prompt.get("tool_ids", [])
    if tool_ids is None:
        return []
    if not isinstance(tool_ids, list) or any(not isinstance(x, str) for x in tool_ids):
        raise ProviderMainMergeError("Agent tool_ids is malformed")
    return tool_ids


def _verify_compiled_artifact_classification(
    compiled: dict[str, Any],
) -> dict[str, Any]:
    if compiled.get("classification") != "EXPECTED_PROVIDER_COMPILED_ARTIFACTS_ONLY":
        raise ProviderMainMergeError(
            "Source branch provider-compiled artifact classification is unresolved"
        )
    if compiled.get("provider_main_write_performed") is not False:
        raise ProviderMainMergeError("Classifier reported an impossible provider Main write")
    if compiled.get("prompt_tool_expected_subset_diff") != []:
        raise ProviderMainMergeError("Materialized prompt.tools differs from expected Client Tool")
    if compiled.get("conversation_config_residual_diff_after_tool_materialization_normalization") != []:
        raise ProviderMainMergeError("Unexpected residual conversation_config differences remain")
    if compiled.get("workflow_diff_only_in_operator_compiled_namespace") is not True:
        raise ProviderMainMergeError("Workflow diff is not isolated to Operator compiled namespace")
    if compiled.get("workflow_diff_touches_technician_namespace") is not False:
        raise ProviderMainMergeError("Workflow diff touches Technician compiled namespace")
    if compiled.get("platform_settings_diff") != []:
        raise ProviderMainMergeError("Source branch contains unexpected platform_settings changes")

    return {
        "classification": compiled["classification"],
        "main_branch_id_sha256": compiled.get("main_branch_id_sha256"),
        "source_branch_id_sha256": compiled.get("source_branch_id_sha256"),
        "tool_id_sha256": compiled.get("tool_id_sha256"),
        "operator_procedure_id_sha256": compiled.get("operator_procedure_id_sha256"),
        "technician_procedure_id_sha256": compiled.get("technician_procedure_id_sha256"),
        "source_prompt_tools_count": compiled.get("source_prompt_tools_count"),
        "workflow_diff_count": compiled.get("workflow_diff_count"),
        "workflow_diff_only_in_operator_compiled_namespace": compiled.get(
            "workflow_diff_only_in_operator_compiled_namespace"
        ),
        "workflow_diff_touches_technician_namespace": compiled.get(
            "workflow_diff_touches_technician_namespace"
        ),
    }


def _preflight(
    client: staging.ProviderClient,
    expected: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    """Verify the exact pre-merge Main and source state without writing."""
    staging.validate_expected_state(expected)
    staging.validate_tool_create_payload(tool_payload)

    main = staging.assert_main_baseline(client)
    raw = main["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]

    source_meta = staging.find_exact_existing_branch(client, agent_id)
    _validate_source_branch_meta(source_meta, main_branch_id=main_branch_id)
    source_branch_id = source_meta.get("id")
    if not isinstance(source_branch_id, str) or not source_branch_id:
        raise ProviderMainMergeError("Source branch omitted id")

    tool = staging.find_exact_existing_tool(client)
    tool_id = tool.get("id")
    if not isinstance(tool_id, str) or not tool_id:
        raise ProviderMainMergeError("Client Tool omitted id")
    staging.verify_tool_contract(tool, tool_payload)

    main_agent = client.get_agent(agent_id)
    source_agent = client.get_agent(agent_id, source_branch_id)
    source_version_id = source_agent.get("version_id")
    if not isinstance(source_version_id, str) or not source_version_id:
        raise ProviderMainMergeError("Source agent omitted version_id")

    source_safe = staging.verify_isolated_final(
        client,
        agent_id=agent_id,
        branch_id=source_branch_id,
        tool_id=tool_id,
        tool_payload=tool_payload,
        expected=expected,
        baseline_technician=main["safe"]["technician"],
    )

    if _effective_tool_ids(source_agent) != [tool_id]:
        raise ProviderMainMergeError("Source branch does not contain exactly the Client Tool")

    compiled = classifier.collect(client, tool_payload, expected)
    compiled_safe = _verify_compiled_artifact_classification(compiled)

    return {
        "raw": {
            "agent_id": agent_id,
            "main_branch_id": main_branch_id,
            "source_branch_id": source_branch_id,
            "source_version_id": source_version_id,
            "tool_id": tool_id,
        },
        "safe": {
            "main": main["safe"],
            "source": source_safe,
            "source_branch_id_sha256": staging.safe_id_fingerprint(source_branch_id),
            "source_version_id_sha256": staging.safe_id_fingerprint(source_version_id),
            "tool_id_sha256": staging.safe_id_fingerprint(tool_id),
            "commits_ahead": source_meta.get("commits_ahead"),
            "commits_behind": source_meta.get("commits_behind"),
            "compiled_artifacts": compiled_safe,
        },
        "source_agent": source_agent,
    }


def _preflight_signature(value: dict[str, Any]) -> str:
    return staging.sha256_text(staging.canonical_json(value["safe"]))


def _verify_preview(
    preview: dict[str, Any],
    source_agent: dict[str, Any],
) -> None:
    overridden = preview.get("overridden_fields") or []
    conflicts = preview.get("conflicts") or []
    if not isinstance(overridden, list) or not isinstance(conflicts, list):
        raise ProviderMainMergeError("Merge preview conflict metadata is malformed")
    if overridden:
        raise ProviderMainMergeError("Merge preview contains overridden fields")
    if conflicts:
        raise ProviderMainMergeError("Merge preview contains conflicts")

    if preview.get("name") != source_agent.get("name"):
        raise ProviderMainMergeError("Merge preview agent name differs from source")

    if preview.get("conversation_config") != source_agent.get("conversation_config"):
        raise ProviderMainMergeError("Merge preview conversation_config differs from source")
    if preview.get("procedures") != source_agent.get("procedures"):
        raise ProviderMainMergeError("Merge preview Procedures differ from source")
    for field in ("platform_settings", "workflow"):
        if field in preview and preview.get(field) != source_agent.get(field):
            raise ProviderMainMergeError(f"Merge preview differs from source at {field}")


def _verify_post_merge_main(
    client: staging.ProviderClient,
    preflight: dict[str, Any],
    expected: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    raw = preflight["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    tool_id = raw["tool_id"]
    source_agent = preflight["source_agent"]

    agent = client.get_agent(agent_id)
    if agent.get("branch_id") != main_branch_id or agent.get("main_branch_id") != main_branch_id:
        raise ProviderMainMergeError("Post-merge current branch is not exact Main")

    version_id = agent.get("version_id")
    if not isinstance(version_id, str) or not version_id:
        raise ProviderMainMergeError("Post-merge Main omitted version_id")
    if staging.safe_id_fingerprint(version_id) == staging.BASELINE["version_id_sha256"]:
        raise ProviderMainMergeError("Post-merge Main version did not advance")

    cfg = agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise ProviderMainMergeError("Post-merge conversation_config is malformed")
    acfg = cfg.get("agent")
    tts = cfg.get("tts")
    if not isinstance(acfg, dict) or not isinstance(tts, dict):
        raise ProviderMainMergeError("Post-merge agent/tts config is malformed")
    pcfg = acfg.get("prompt")
    if not isinstance(pcfg, dict):
        raise ProviderMainMergeError("Post-merge prompt config is malformed")

    prompt = staging.normalize_text(pcfg.get("prompt"))
    if not isinstance(prompt, str):
        raise ProviderMainMergeError("Post-merge System Prompt is missing")
    if staging.sha256_text(prompt) != staging.BASELINE["system_prompt_sha256"]:
        raise ProviderMainMergeError("Post-merge System Prompt fingerprint changed")
    if len(prompt) != staging.BASELINE["system_prompt_length"]:
        raise ProviderMainMergeError("Post-merge System Prompt length changed")
    if acfg.get("language") != staging.BASELINE["language"]:
        raise ProviderMainMergeError("Post-merge language changed")
    if pcfg.get("llm") != staging.BASELINE["llm_id"]:
        raise ProviderMainMergeError("Post-merge LLM changed")
    if staging.dynamic_variable_names(agent) != staging.BASELINE["dynamic_variable_names"]:
        raise ProviderMainMergeError("Post-merge dynamic variables changed")
    if staging.safe_id_fingerprint(tts.get("voice_id")) != staging.BASELINE["voice_id_sha256"]:
        raise ProviderMainMergeError("Post-merge voice changed")
    if _effective_tool_ids(agent) != [tool_id]:
        raise ProviderMainMergeError("Post-merge Main does not contain exactly the Client Tool")

    for field in ("conversation_config", "platform_settings", "workflow", "procedures"):
        if agent.get(field) != source_agent.get(field):
            raise ProviderMainMergeError(f"Post-merge Main differs from verified source at {field}")

    operator = staging._procedure_by_name(client, agent, main_branch_id, "Operator breakdown")
    technician = staging._procedure_by_name(client, agent, main_branch_id, "Technician pre-close")
    materialized = staging.materialize_operator(expected, tool_id)
    wanted_operator = staging.semantic_procedure_fingerprint(
        {**materialized, "version_id": "expected"}
    )
    wanted_operator["version_present"] = True
    actual_operator = staging.semantic_procedure_fingerprint(operator)
    if actual_operator != wanted_operator:
        raise ProviderMainMergeError("Post-merge Operator breakdown fingerprint mismatch")

    actual_technician = staging.semantic_procedure_fingerprint(technician)
    if actual_technician != preflight["safe"]["main"]["technician"]:
        raise ProviderMainMergeError("Post-merge Technician pre-close changed")

    staging.verify_tool_contract(staging.find_exact_existing_tool(client), tool_payload)

    platform = agent.get("platform_settings")
    if not isinstance(platform, dict):
        raise ProviderMainMergeError("Post-merge platform_settings unavailable")
    auth = platform.get("auth")
    if not isinstance(auth, dict) or auth.get("enable_auth") is not False:
        raise ProviderMainMergeError("Post-merge auth classification changed")

    return {
        "version_id_sha256": staging.safe_id_fingerprint(version_id),
        "main_branch_id_sha256": staging.safe_id_fingerprint(main_branch_id),
        "tool_id_sha256": staging.safe_id_fingerprint(tool_id),
        "tool_name": staging.TOOL_NAME,
        "tool_attached": True,
        "auth_enable_auth": False,
        "operator": actual_operator,
        "technician": actual_technician,
        "system_prompt_sha256": staging.sha256_text(prompt),
        "system_prompt_length": len(prompt),
        "voice_id_sha256": staging.safe_id_fingerprint(tts.get("voice_id")),
    }


def _verify_archived_source(
    client: staging.ProviderClient,
    agent_id: str,
    source_branch_id: str,
) -> dict[str, Any]:
    results = client.list_branches(agent_id, include_archived=True).get("results", [])
    if not isinstance(results, list):
        raise ProviderMainMergeError("Post-merge branch listing omitted results")
    matches = [
        item for item in results
        if isinstance(item, dict) and item.get("id") == source_branch_id
    ]
    if len(matches) != 1:
        raise ProviderMainMergeError("Post-merge source branch not found exactly once")
    source = matches[0]
    if not bool(source.get("is_archived", False)):
        raise ProviderMainMergeError("Source branch was not archived")
    if source.get("current_live_percentage") not in (0, 0.0):
        raise ProviderMainMergeError("Archived source branch still has live traffic")
    return source


def execute_provider_main_merge(
    read_client: staging.ProviderClient,
    merge_client: ProviderMainMergeClient,
    expected: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    pre = _preflight(read_client, expected, tool_payload)
    raw = pre["raw"]

    aid = staging.safe_identifier(raw["agent_id"], "agent_id")
    sid = staging.safe_identifier(raw["source_branch_id"], "source_branch_id")
    preview = merge_client.get(
        f"/v1/convai/agents/{aid}/branches/{sid}/merge-preview",
        {
            "target_branch_id": raw["main_branch_id"],
            "force": "false",
        },
    )
    _verify_preview(preview, pre["source_agent"])

    pre_after_preview = _preflight(read_client, expected, tool_payload)
    if _preflight_signature(pre_after_preview) != _preflight_signature(pre):
        raise ProviderMainMergeError("Provider state moved after merge preview")

    merge_client.post_with_query(
        f"/v1/convai/agents/{aid}/branches/{sid}/merge",
        {
            "archive_source_branch": MERGE_ARCHIVE_SOURCE,
            "force": MERGE_FORCE,
        },
        {"target_branch_id": raw["main_branch_id"]},
    )

    post_main = _verify_post_merge_main(
        read_client,
        pre,
        expected,
        tool_payload,
    )
    archived = _verify_archived_source(
        read_client,
        raw["agent_id"],
        raw["source_branch_id"],
    )

    return {
        "schema_version": 1,
        "mode": "GATE2_PROVIDER_MAIN_MERGE_EXECUTED",
        "provider": "ElevenLabs",
        "issue": ISSUE,
        "merge": {
            "source_branch_name": staging.STAGING_BRANCH_NAME,
            "source_branch_id_sha256": staging.safe_id_fingerprint(raw["source_branch_id"]),
            "target_main_branch_id_sha256": staging.safe_id_fingerprint(raw["main_branch_id"]),
            "force": MERGE_FORCE,
            "archive_source_branch": MERGE_ARCHIVE_SOURCE,
            "preview_overridden_fields_count": len(preview.get("overridden_fields") or []),
            "preview_conflicts_count": len(preview.get("conflicts") or []),
        },
        "pre_merge": pre["safe"],
        "post_merge_main": post_main,
        "source_branch_archived": bool(archived.get("is_archived", False)),
        "provider_main_modified": True,
        "provider_main_merge_performed": True,
        "runtime_risk": expected.get("runtime_risk"),
        "next_gate": "STOP_BEFORE_GATE_3_RUNTIME_CONVERSATION",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-provider-main-merge", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_provider_main_merge:
        print(
            "ERROR: --execute-provider-main-merge is required; no provider merge performed",
            file=sys.stderr,
        )
        return 2

    key = os.getenv(staging.API_KEY_ENV)
    if not key:
        print(f"ERROR: {staging.API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        expected = staging.load_object(args.expected)
        tool_payload = staging.load_object(args.tool_config)
        evidence = execute_provider_main_merge(
            staging.ProviderClient(key),
            ProviderMainMergeClient(key),
            expected,
            tool_payload,
        )
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (
        staging.StagingError,
        ProviderMainMergeError,
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
