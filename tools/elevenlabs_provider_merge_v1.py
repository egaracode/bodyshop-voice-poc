#!/usr/bin/env python3
"""Controlled ElevenLabs Gate C merge executor for BODYSHOP #34.

Gate C only:
1) revalidate provider Main against the exact pre-reconciliation guard;
2) revalidate the isolated branch exact A5 target and zero live traffic;
3) GET merge-preview into explicit Main with force=false;
4) require zero merge conflicts/overrides and exact preview target state;
5) POST merge into explicit Main with archive_source_branch=true, force=false;
6) run a fresh GET-only V2 provider snapshot;
7) verify Main exactly matches the A5-compatible target and the source branch is archived.

This tool does not touch repository Ready/merge, Supabase, Production or lifecycle state.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import elevenlabs_provider_compat_v2 as compat_v2
from elevenlabs_provider_final_config_v1 import (
    FinalConfigError,
    _get_branch_agent,
    _get_branch_procedures,
    _select_staged_refs,
    _verify_final_readback,
)
from elevenlabs_provider_reconciliation_v1 import (
    API_KEY_ENV,
    CURRENT_PROVIDER_GUARD_V1,
    PlannerError,
    ApiClient,
    assert_current_provider_guard,
    collect_live_state,
    derive_expected_target,
    dynamic_variable_names,
    find_exact_agent,
    normalize_text,
    resolve_target_voice,
    safe_id_fingerprint,
    safe_identifier,
    sha256_text,
)
from elevenlabs_provider_staging_v1 import (
    STAGING_BRANCH_NAME,
    STAGING_DESCRIPTION,
    StagingClient,
    StagingError,
    expected_procedure_fingerprint,
    procedure_fingerprint,
)

MERGE_ARCHIVE_SOURCE = True
MERGE_FORCE = False


class ProviderMergeError(RuntimeError):
    pass


class ProviderMergeClient(StagingClient):
    """Gate-C client: GET plus POST with explicit query parameters."""

    def post_with_query(
        self,
        path: str,
        body: dict[str, Any],
        query: dict[str, str],
    ) -> dict[str, Any]:
        return self._request("POST", path, body=body, query=query)


def _find_isolated_branch(
    client: ApiClient,
    agent_id: str,
    main_branch_id: str,
) -> dict[str, Any]:
    results = client.list_branches(agent_id).get("results", [])
    if not isinstance(results, list):
        raise ProviderMergeError("Branch listing omitted results list")
    matches = [
        item
        for item in results
        if isinstance(item, dict) and item.get("name") == STAGING_BRANCH_NAME
    ]
    if len(matches) != 1:
        raise ProviderMergeError(
            f"Expected exactly one isolated provider branch, found {len(matches)}"
        )
    branch = matches[0]
    if branch.get("parent_branch_id") != main_branch_id:
        raise ProviderMergeError("Isolated branch parent does not match exact Main")
    if branch.get("description") != STAGING_DESCRIPTION:
        raise ProviderMergeError("Isolated branch description mismatch")
    if branch.get("current_live_percentage") != 0:
        raise ProviderMergeError("Isolated branch unexpectedly has live traffic")
    if bool(branch.get("draft_exists", False)):
        raise ProviderMergeError("Isolated branch unexpectedly has a draft")
    if bool(branch.get("is_archived", False)):
        raise ProviderMergeError("Isolated branch is already archived")
    if branch.get("commits_behind") != 0:
        raise ProviderMergeError("Isolated branch is behind Main; refusing stale merge")
    if not isinstance(branch.get("commits_ahead"), int) or branch.get("commits_ahead") <= 0:
        raise ProviderMergeError("Isolated branch has no mergeable changes")
    return branch


def _verify_preview(
    preview: dict[str, Any],
    target: dict[str, Any],
    target_voice_id: str,
    selected_refs: dict[str, str],
) -> None:
    overridden = preview.get("overridden_fields") or []
    conflicts = preview.get("conflicts") or []
    if not isinstance(overridden, list) or not isinstance(conflicts, list):
        raise ProviderMergeError("Merge preview conflict metadata is malformed")
    if overridden:
        raise ProviderMergeError("Merge preview contains overridden fields")
    if conflicts:
        raise ProviderMergeError("Merge preview contains conflicts")
    _verify_final_readback(preview, target, target_voice_id, selected_refs)


def _verify_effective_target(
    agent: dict[str, Any],
    all_branch_procedures: list[dict[str, Any]],
    target: dict[str, Any],
    target_voice_id: str,
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    """Verify effective two-Procedure config while allowing historical Procedure identities."""
    selected_refs, operator_fp, technician_fp = _select_staged_refs(
        all_branch_procedures,
        target,
    )
    _verify_final_readback(
        agent,
        target,
        target_voice_id,
        selected_refs,
    )
    return selected_refs, operator_fp, technician_fp


def _verify_post_merge_main(
    client: ApiClient,
    expected: dict[str, Any],
    target_voice_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    target = derive_expected_target(expected)
    listed = find_exact_agent(client, "AI Control")
    agent_id = listed.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise ProviderMergeError("Post-merge agent omitted agent_id")

    agent = client.get_agent(agent_id)
    branch_id = agent.get("branch_id")
    main_branch_id = agent.get("main_branch_id")
    if not isinstance(branch_id, str) or not isinstance(main_branch_id, str):
        raise ProviderMergeError("Post-merge provider omitted branch identity")
    if branch_id != main_branch_id:
        raise ProviderMergeError("Post-merge current branch is not Main")

    cfg = agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise ProviderMergeError("Post-merge conversation_config is malformed")
    acfg = cfg.get("agent")
    tts = cfg.get("tts")
    if not isinstance(acfg, dict) or not isinstance(tts, dict):
        raise ProviderMergeError("Post-merge agent/tts config is malformed")
    pcfg = acfg.get("prompt")
    if not isinstance(pcfg, dict):
        raise ProviderMergeError("Post-merge prompt config is malformed")

    retained = CURRENT_PROVIDER_GUARD_V1["agent"]
    if agent.get("name") != retained["name"]:
        raise ProviderMergeError("Post-merge agent name changed unexpectedly")
    if acfg.get("language") != retained["language"]:
        raise ProviderMergeError("Post-merge language changed unexpectedly")
    if pcfg.get("llm") != retained["llm_id"]:
        raise ProviderMergeError("Post-merge LLM changed unexpectedly")
    if dynamic_variable_names(agent) != retained["dynamic_variable_names"]:
        raise ProviderMergeError("Post-merge dynamic-variable set changed unexpectedly")

    prompt = normalize_text(pcfg.get("prompt"))
    if not isinstance(prompt, str):
        raise ProviderMergeError("Post-merge System Prompt is missing")
    if sha256_text(prompt) != target["system_prompt_sha256"]:
        raise ProviderMergeError("Post-merge System Prompt fingerprint mismatch")
    if len(prompt) != target["system_prompt_length"]:
        raise ProviderMergeError("Post-merge System Prompt length mismatch")

    voice_id = tts.get("voice_id")
    if voice_id != target_voice_id:
        raise ProviderMergeError("Post-merge voice identity mismatch")

    procedures = _get_branch_procedures(client, agent_id, main_branch_id)
    selected_refs, operator_fp, technician_fp = _verify_effective_target(
        agent,
        procedures,
        target,
        target_voice_id,
    )

    snapshot = compat_v2.collect_provider_snapshot(
        compat_v2.ApiClient(client.api_key, client.base_url),
        "AI Control",
    )
    if snapshot.get("agent", {}).get("system_prompt_sha256") != target["system_prompt_sha256"]:
        raise ProviderMergeError("Post-merge V2 snapshot System Prompt mismatch")
    if snapshot.get("voice", {}).get("voice_id_sha256") != safe_id_fingerprint(target_voice_id):
        raise ProviderMergeError("Post-merge V2 snapshot voice mismatch")
    snap_procs = snapshot.get("procedures")
    if not isinstance(snap_procs, list) or len(snap_procs) != 2:
        raise ProviderMergeError("Post-merge V2 snapshot Procedure count mismatch")
    if {p.get("name") for p in snap_procs} != {
        "Operator breakdown",
        "Technician pre-close",
    }:
        raise ProviderMergeError("Post-merge V2 snapshot Procedure names mismatch")
    if any(p.get("warnings") for p in snap_procs):
        raise ProviderMergeError("Post-merge V2 snapshot contains Procedure warnings")

    safe = {
        "agent": {
            "name": snapshot["agent"].get("name"),
            "language": snapshot["agent"].get("language"),
            "llm_id": snapshot["agent"].get("llm_id"),
            "system_prompt_sha256": snapshot["agent"].get("system_prompt_sha256"),
            "system_prompt_length": snapshot["agent"].get("system_prompt_length"),
            "dynamic_variable_names": snapshot["agent"].get("dynamic_variable_names"),
            "version_id_sha256": snapshot["agent"].get("version_id_sha256"),
            "main_branch_id_sha256": snapshot["agent"].get("main_branch_id_sha256"),
        },
        "branch": snapshot.get("branch"),
        "voice": snapshot.get("voice"),
        "procedures": [
            {
                "name": p.get("name"),
                "raw_api_type": p.get("raw_api_type"),
                "content_shape": p.get("content_shape"),
                "trigger_sha256": p.get("trigger_sha256"),
                "trigger_length": p.get("trigger_length"),
                "version_present": p.get("version_present"),
                "procedure_id_sha256": p.get("procedure_id_sha256"),
                "warnings": p.get("warnings"),
            }
            for p in snap_procs
        ],
    }
    return agent, safe


def _verify_archived_source(
    client: ProviderMergeClient,
    agent_id: str,
    source_branch_id: str,
) -> dict[str, Any]:
    aid = safe_identifier(agent_id, "agent_id")
    page = client.get(
        f"/v1/convai/agents/{aid}/branches",
        {
            "include_archived": "true",
            "include_commit_status": "true",
            "limit": "100",
        },
    )
    results = page.get("results", [])
    if not isinstance(results, list):
        raise ProviderMergeError("Post-merge branch listing omitted results")
    matches = [
        b for b in results
        if isinstance(b, dict) and b.get("id") == source_branch_id
    ]
    if len(matches) != 1:
        raise ProviderMergeError("Post-merge source branch not found exactly once")
    source = matches[0]
    if not bool(source.get("is_archived", False)):
        raise ProviderMergeError("Source branch was not archived after merge")
    if source.get("current_live_percentage") not in (0, 0.0):
        raise ProviderMergeError("Archived source branch still has live traffic")
    return source


def execute_provider_merge(
    read_client: ApiClient,
    merge_client: ProviderMergeClient,
    expected: dict[str, Any],
) -> dict[str, Any]:
    target = derive_expected_target(expected)

    # Exact stale-write guard immediately before preview/merge.
    main_before = collect_live_state(read_client, "AI Control")
    assert_current_provider_guard(main_before["safe_guard"], CURRENT_PROVIDER_GUARD_V1)
    raw = main_before["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]

    source = _find_isolated_branch(read_client, agent_id, main_branch_id)
    source_branch_id = source.get("id")
    if not isinstance(source_branch_id, str) or not source_branch_id:
        raise ProviderMergeError("Isolated branch omitted id")

    source_agent = _get_branch_agent(read_client, agent_id, source_branch_id)
    source_procedures = _get_branch_procedures(read_client, agent_id, source_branch_id)
    voice = resolve_target_voice(read_client)
    target_voice_id = voice["raw_voice_id"]
    selected_refs, operator_fp, technician_fp = _verify_effective_target(
        source_agent,
        source_procedures,
        target,
        target_voice_id,
    )

    aid = safe_identifier(agent_id, "agent_id")
    sid = safe_identifier(source_branch_id, "source_branch_id")
    preview = merge_client.get(
        f"/v1/convai/agents/{aid}/branches/{sid}/merge-preview",
        {
            "target_branch_id": main_branch_id,
            "force": "false",
        },
    )
    _verify_preview(preview, target, target_voice_id, selected_refs)

    # Re-read Main after preview to close the TOCTOU window as far as the API allows.
    main_after_preview = collect_live_state(read_client, "AI Control")
    assert_current_provider_guard(
        main_after_preview["safe_guard"],
        CURRENT_PROVIDER_GUARD_V1,
    )

    merge_client.post_with_query(
        f"/v1/convai/agents/{aid}/branches/{sid}/merge",
        {
            "archive_source_branch": MERGE_ARCHIVE_SOURCE,
            "force": MERGE_FORCE,
        },
        {"target_branch_id": main_branch_id},
    )

    post_agent, safe_snapshot = _verify_post_merge_main(
        read_client,
        expected,
        target_voice_id,
    )
    archived_source = _verify_archived_source(
        merge_client,
        agent_id,
        source_branch_id,
    )

    post_version_id = post_agent.get("version_id")
    if not isinstance(post_version_id, str) or not post_version_id:
        raise ProviderMergeError("Post-merge Main version_id is missing")

    return {
        "schema_version": 1,
        "mode": "GATE_C_PROVIDER_MAIN_MERGE_EXECUTED",
        "provider": "ElevenLabs",
        "issue": 34,
        "merge": {
            "source_branch_name": STAGING_BRANCH_NAME,
            "source_branch_id_sha256": safe_id_fingerprint(source_branch_id),
            "target_main_branch_id_sha256": safe_id_fingerprint(main_branch_id),
            "force": MERGE_FORCE,
            "archive_source_branch": MERGE_ARCHIVE_SOURCE,
            "preview_overridden_fields_count": len(preview.get("overridden_fields") or []),
            "preview_conflicts_count": len(preview.get("conflicts") or []),
        },
        "target": {
            "system_prompt_sha256": target["system_prompt_sha256"],
            "system_prompt_length": target["system_prompt_length"],
            "voice_name": voice["safe"]["name"],
            "voice_id_sha256": voice["safe"]["voice_id_sha256"],
            "effective_procedure_names": [
                "Operator breakdown",
                "Technician pre-close",
            ],
        },
        "procedures": {
            "Operator breakdown": operator_fp,
            "Technician pre-close": technician_fp,
        },
        "post_merge_main": {
            "version_id_sha256": safe_id_fingerprint(post_version_id),
            "v2_snapshot": safe_snapshot,
        },
        "source_branch_archived": bool(archived_source.get("is_archived", False)),
        "provider_main_modified": True,
        "next_gate": "POST_WRITE_RECONCILIATION_COMPLETE_STOP_BEFORE_GATE_3",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-provider-merge", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_provider_merge:
        print(
            "ERROR: --execute-provider-merge is required; no provider merge performed",
            file=sys.stderr,
        )
        return 2

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        with open(args.expected, encoding="utf-8") as handle:
            expected = json.load(handle)
        read_client = ApiClient(key)
        merge_client = ProviderMergeClient(key)
        evidence = execute_provider_merge(read_client, merge_client, expected)
        encoded = json.dumps(evidence, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.write("\n")
    except (
        PlannerError,
        StagingError,
        FinalConfigError,
        ProviderMergeError,
        compat_v2.ProbeError,
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
