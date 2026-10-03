#!/usr/bin/env python3
"""Controlled ElevenLabs Gate B executor for BODYSHOP #34.

Gate B only:
1) verify Main still matches the exact guarded baseline;
2) verify the isolated provider branch identity and zero live traffic;
3) verify staged Operator breakdown + Technician pre-close fingerprints;
4) resolve the pinned Eric voice identity;
5) PATCH only the isolated branch with:
   - exact A5 System Prompt,
   - pinned Eric voice,
   - exactly two Procedure version refs;
6) read back the isolated branch and verify the effective configuration;
7) re-read Main and prove it remains unchanged.

This tool cannot merge provider branches.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any

from elevenlabs_provider_reconciliation_v1 import (
    API_KEY_ENV,
    CURRENT_PROVIDER_GUARD_V1,
    PlannerError,
    ApiClient,
    assert_current_provider_guard,
    collect_live_state,
    derive_expected_target,
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

VERSION_DESCRIPTION = "BODYSHOP #34 reconcile ElevenLabs provider to A5"


class FinalConfigError(RuntimeError):
    pass


def _branch_matches(client: ApiClient, agent_id: str, branch_name: str) -> dict[str, Any]:
    results = client.list_branches(agent_id).get("results", [])
    if not isinstance(results, list):
        raise FinalConfigError("Branch listing omitted results list")
    matches = [
        item
        for item in results
        if isinstance(item, dict) and item.get("name") == branch_name
    ]
    if len(matches) != 1:
        raise FinalConfigError(f"Expected exactly one isolated branch, found {len(matches)}")
    return matches[0]


def _get_branch_agent(client: ApiClient, agent_id: str, branch_id: str) -> dict[str, Any]:
    aid = safe_identifier(agent_id, "agent_id")
    return client._get(
        f"/v1/convai/agents/{aid}",
        {"branch_id": branch_id},
    )


def _get_branch_procedures(
    client: ApiClient, agent_id: str, branch_id: str
) -> list[dict[str, Any]]:
    listed = client.list_procedures(agent_id, branch_id, None).get("procedures", [])
    if not isinstance(listed, list):
        raise FinalConfigError("Procedure listing omitted procedures list")
    full: list[dict[str, Any]] = []
    for meta in listed:
        if not isinstance(meta, dict):
            continue
        pid = meta.get("procedure_id")
        if not isinstance(pid, str) or not pid:
            raise FinalConfigError("Procedure listing omitted procedure_id")
        full.append(client.get_procedure(agent_id, branch_id, pid, None))
    return full


def _select_staged_refs(
    procedures: list[dict[str, Any]], target: dict[str, Any]
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    operator = [
        item
        for item in procedures
        if item.get("name") == "Operator breakdown"
        and item.get("type") == "deterministic"
    ]
    technician = [
        item
        for item in procedures
        if item.get("name") == "Technician pre-close"
        and item.get("type") == "free_form"
    ]
    if len(operator) != 1:
        raise FinalConfigError(
            f"Expected exactly one deterministic Operator breakdown, found {len(operator)}"
        )
    if len(technician) != 1:
        raise FinalConfigError(
            f"Expected exactly one Technician pre-close, found {len(technician)}"
        )

    operator_fp = procedure_fingerprint(operator[0])
    technician_fp = procedure_fingerprint(technician[0])
    if operator_fp != expected_procedure_fingerprint(target, "Operator breakdown"):
        raise FinalConfigError("Staged Operator breakdown fingerprint mismatch")
    if technician_fp != expected_procedure_fingerprint(target, "Technician pre-close"):
        raise FinalConfigError("Staged Technician pre-close fingerprint mismatch")

    refs: dict[str, str] = {}
    for item in (operator[0], technician[0]):
        pid = item.get("procedure_id")
        vid = item.get("version_id")
        if not isinstance(pid, str) or not pid:
            raise FinalConfigError("Selected Procedure omitted procedure_id")
        if not isinstance(vid, str) or not vid:
            raise FinalConfigError("Selected Procedure omitted version_id")
        refs[pid] = vid

    return refs, operator_fp, technician_fp


def _build_target_config(
    current: dict[str, Any],
    expected: dict[str, Any],
    target_voice_id: str,
) -> dict[str, Any]:
    cfg = current.get("conversation_config")
    if not isinstance(cfg, dict):
        raise FinalConfigError("Isolated branch conversation_config is malformed")

    result = copy.deepcopy(cfg)
    agent_cfg = result.get("agent")
    tts_cfg = result.get("tts")
    if not isinstance(agent_cfg, dict) or not isinstance(tts_cfg, dict):
        raise FinalConfigError("Isolated branch agent/tts configuration is malformed")
    prompt_cfg = agent_cfg.get("prompt")
    if not isinstance(prompt_cfg, dict):
        raise FinalConfigError("Isolated branch prompt configuration is malformed")

    expected_agent = expected.get("agent")
    if not isinstance(expected_agent, dict):
        raise FinalConfigError("Expected agent configuration is malformed")
    expected_prompt = normalize_text(expected_agent.get("system_prompt"))
    if not isinstance(expected_prompt, str):
        raise FinalConfigError("Expected System Prompt is not pinned")

    prompt_cfg["prompt"] = expected_prompt
    tts_cfg["voice_id"] = target_voice_id
    return result


def _verify_final_readback(
    branch_agent: dict[str, Any],
    expected_target: dict[str, Any],
    target_voice_id: str,
    selected_refs: dict[str, str],
) -> None:
    cfg = branch_agent.get("conversation_config")
    if not isinstance(cfg, dict):
        raise FinalConfigError("Final readback conversation_config is malformed")
    agent_cfg = cfg.get("agent")
    tts = cfg.get("tts")
    if not isinstance(agent_cfg, dict) or not isinstance(tts, dict):
        raise FinalConfigError("Final readback agent/tts is malformed")
    prompt_cfg = agent_cfg.get("prompt")
    if not isinstance(prompt_cfg, dict):
        raise FinalConfigError("Final readback prompt is malformed")

    prompt = normalize_text(prompt_cfg.get("prompt"))
    if not isinstance(prompt, str):
        raise FinalConfigError("Final readback System Prompt is missing")
    if sha256_text(prompt) != expected_target["system_prompt_sha256"]:
        raise FinalConfigError("Final readback System Prompt fingerprint mismatch")
    if len(prompt) != expected_target["system_prompt_length"]:
        raise FinalConfigError("Final readback System Prompt length mismatch")
    if tts.get("voice_id") != target_voice_id:
        raise FinalConfigError("Final readback voice identity mismatch")

    procedures = branch_agent.get("procedures")
    if not isinstance(procedures, dict):
        raise FinalConfigError("Final readback procedures map is malformed")
    if set(procedures) != set(selected_refs):
        raise FinalConfigError("Final readback does not contain exactly two selected Procedures")
    for pid, expected_vid in selected_refs.items():
        item = procedures.get(pid)
        if not isinstance(item, dict):
            raise FinalConfigError("Final readback Procedure entry is malformed")
        if item.get("version_id") != expected_vid:
            raise FinalConfigError("Final readback Procedure version_id mismatch")

    names_types = sorted(
        (item.get("name"), item.get("type"))
        for item in procedures.values()
        if isinstance(item, dict)
    )
    if names_types != [
        ("Operator breakdown", "deterministic"),
        ("Technician pre-close", "free_form"),
    ]:
        raise FinalConfigError("Final readback Procedure names/types mismatch")


def execute_final_config(
    read_client: ApiClient,
    write_client: StagingClient,
    expected: dict[str, Any],
) -> dict[str, Any]:
    target = derive_expected_target(expected)

    main_before = collect_live_state(read_client, "AI Control")
    assert_current_provider_guard(main_before["safe_guard"], CURRENT_PROVIDER_GUARD_V1)
    raw = main_before["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]

    branch = _branch_matches(read_client, agent_id, STAGING_BRANCH_NAME)
    branch_id = branch.get("id")
    if not isinstance(branch_id, str) or not branch_id:
        raise FinalConfigError("Isolated branch omitted id")
    if branch.get("parent_branch_id") != main_branch_id:
        raise FinalConfigError("Isolated branch parent does not match guarded Main")
    if branch.get("description") != STAGING_DESCRIPTION:
        raise FinalConfigError("Isolated branch description mismatch")
    if branch.get("current_live_percentage") != 0:
        raise FinalConfigError("Isolated branch unexpectedly has live traffic")
    if bool(branch.get("is_archived", False)):
        raise FinalConfigError("Isolated branch is archived")
    if bool(branch.get("draft_exists", False)):
        raise FinalConfigError("Isolated branch unexpectedly has a draft")

    current_branch_agent = _get_branch_agent(read_client, agent_id, branch_id)
    procedures = _get_branch_procedures(read_client, agent_id, branch_id)
    selected_refs, operator_fp, technician_fp = _select_staged_refs(procedures, target)

    voice = resolve_target_voice(read_client)
    target_voice_id = voice["raw_voice_id"]
    target_cfg = _build_target_config(current_branch_agent, expected, target_voice_id)

    aid = safe_identifier(agent_id, "agent_id")
    write_client.patch(
        f"/v1/convai/agents/{aid}",
        {
            "conversation_config": target_cfg,
            "version_description": VERSION_DESCRIPTION,
            "procedures": {
                pid: {
                    "procedure_id": pid,
                    "version_id": vid,
                }
                for pid, vid in selected_refs.items()
            },
        },
        {"branch_id": branch_id},
    )

    final_branch_agent = _get_branch_agent(read_client, agent_id, branch_id)
    _verify_final_readback(
        final_branch_agent,
        target,
        target_voice_id,
        selected_refs,
    )

    final_procedures = _get_branch_procedures(read_client, agent_id, branch_id)
    final_operator = [
        p for p in final_procedures
        if p.get("name") == "Operator breakdown" and p.get("type") == "deterministic"
    ]
    final_technician = [
        p for p in final_procedures
        if p.get("name") == "Technician pre-close" and p.get("type") == "free_form"
    ]
    if len(final_operator) != 1 or len(final_technician) != 1:
        raise FinalConfigError("Final Procedure readback count mismatch")
    if procedure_fingerprint(final_operator[0]) != expected_procedure_fingerprint(
        target, "Operator breakdown"
    ):
        raise FinalConfigError("Final Operator breakdown fingerprint mismatch")
    if procedure_fingerprint(final_technician[0]) != expected_procedure_fingerprint(
        target, "Technician pre-close"
    ):
        raise FinalConfigError("Final Technician pre-close fingerprint mismatch")

    main_after = collect_live_state(read_client, "AI Control")
    assert_current_provider_guard(main_after["safe_guard"], CURRENT_PROVIDER_GUARD_V1)

    final_version_id = final_branch_agent.get("version_id")
    if not isinstance(final_version_id, str) or not final_version_id:
        raise FinalConfigError("Final isolated branch version_id is missing")

    return {
        "schema_version": 1,
        "mode": "GATE_B_FINAL_ISOLATED_CONFIG_EXECUTED",
        "provider": "ElevenLabs",
        "issue": 34,
        "branch": {
            "name": STAGING_BRANCH_NAME,
            "branch_id_sha256": safe_id_fingerprint(branch_id),
            "parent_branch_id_sha256": safe_id_fingerprint(main_branch_id),
            "current_live_percentage": branch.get("current_live_percentage"),
            "final_version_id_sha256": safe_id_fingerprint(final_version_id),
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
        "staged_procedures": {
            "Operator breakdown": operator_fp,
            "Technician pre-close": technician_fp,
        },
        "provider_main_modified": False,
        "next_gate": "SEPARATE_PROVIDER_MAIN_MERGE_APPROVAL_REQUIRED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-final-config", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_final_config:
        print(
            "ERROR: --execute-final-config is required; no provider write performed",
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
        write_client = StagingClient(key)
        evidence = execute_final_config(read_client, write_client, expected)
        encoded = json.dumps(evidence, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.write("\n")
    except (
        PlannerError,
        StagingError,
        FinalConfigError,
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
