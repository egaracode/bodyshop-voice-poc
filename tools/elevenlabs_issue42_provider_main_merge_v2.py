#!/usr/bin/env python3
"""BODYSHOP Voice PoC #42 — fail-closed provider Main merge executor V2.

Authorized boundary:
- revalidate exact provider Main Gate-2 baseline;
- revalidate exact isolated V2 source branch and a fresh force=false merge preview;
- perform exactly one merge POST from that source to provider Main with
  archive_source_branch=true and force=false;
- perform GET-only post-merge readback.

This executable cannot create branches, patch drafts, publish isolated branches,
merge any other source/target, force a merge, or retry an uncertain merge
outcome.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import elevenlabs_issue42_provider_staging_v2 as staging42
import elevenlabs_issue42_workshop_installation_alignment_v2 as planner

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
BRANCH_NAME = staging42.BRANCH_NAME
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class Issue42MainMergeError(RuntimeError):
    pass


class Issue42MergeOutcomeUnknown(Issue42MainMergeError):
    """The merge request may have reached ElevenLabs; never retry blindly."""


def _safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise Issue42MainMergeError(f"Invalid {label}")
    return urllib.parse.quote(value, safe="")


class Issue42MainMergeClient(staging42.Issue42ProviderClient):
    """Read-only API surface plus exactly one branch-merge POST."""

    def __init__(self, api_key: str, base_url: str = API_BASE):
        super().__init__(api_key, base_url)
        self.merge_post_count = 0

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if method == "GET":
            return super()._request(method, path, body=None, query=query)

        merge_match = re.fullmatch(
            r"/v1/convai/agents/[A-Za-z0-9_-]+/branches/"
            r"[A-Za-z0-9_-]+/merge",
            path,
        )
        if method != "POST" or not merge_match:
            raise Issue42MainMergeError(
                "Main-merge executor rejected non-GET / non-merge operation"
            )
        if self.merge_post_count != 0:
            raise Issue42MainMergeError("Second provider Main merge POST is forbidden")
        if not isinstance(query, dict) or set(query) != {"target_branch_id"}:
            raise Issue42MainMergeError("Merge target query is malformed")
        _safe_identifier(query.get("target_branch_id"), "target_branch_id")
        if body != {"archive_source_branch": True, "force": False}:
            raise Issue42MainMergeError("Merge body is not exact authorized body")

        qs = urllib.parse.urlencode(query)
        url = f"{self.base_url}{path}?{qs}"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "xi-api-key": self.api_key,
                "user-agent": "bodyshop-voice-poc-issue42-main-merge-v2/1",
            },
        )

        # Count before network I/O. Any network error is an uncertain outcome
        # and this process must never retry the POST.
        self.merge_post_count += 1
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            # HTTP status proves the server returned a response.
            raise Issue42MainMergeError(
                f"ElevenLabs merge POST failed: HTTP {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise Issue42MergeOutcomeUnknown(
                "Merge POST network outcome is unknown; do not retry. "
                "Run GET-only recovery/readback."
            ) from exc

        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise Issue42MergeOutcomeUnknown(
                "Merge POST returned non-JSON after HTTP success; do not retry. "
                "Run GET-only recovery/readback."
            ) from exc
        if not isinstance(parsed, dict):
            raise Issue42MergeOutcomeUnknown(
                "Merge POST returned unexpected response shape; do not retry. "
                "Run GET-only recovery/readback."
            )
        return parsed

    def merge_once(
        self,
        agent_id: str,
        source_branch_id: str,
        target_branch_id: str,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        sid = _safe_identifier(source_branch_id, "source_branch_id")
        _safe_identifier(target_branch_id, "target_branch_id")
        return self._request(
            "POST",
            f"/v1/convai/agents/{aid}/branches/{sid}/merge",
            query={"target_branch_id": target_branch_id},
            body={"archive_source_branch": True, "force": False},
        )


def _load_object(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Issue42MainMergeError(f"Unable to load JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise Issue42MainMergeError("JSON root must be an object")
    return value


def _source_summary(
    client: Issue42MainMergeClient,
    *,
    main_live: dict[str, Any],
    main_agent: dict[str, Any],
    expected_v2: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    raw = main_live["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]

    source_meta = staging42._find_target_branch(client, agent_id)
    if source_meta is None:
        raise Issue42MainMergeError("Exact Issue #42 source branch not found")
    source_branch_id = source_meta.get("id")
    if not isinstance(source_branch_id, str) or not source_branch_id:
        raise Issue42MainMergeError("Source branch omitted id")

    branch = staging42._combined_branch_state(client, agent_id, source_branch_id)
    staging42._verify_branch_meta(
        branch,
        main_branch_id=main_branch_id,
        require_ahead=True,
    )
    if bool(branch.get("draft_exists", False)):
        raise Issue42MainMergeError("Source branch unexpectedly has a draft")
    if bool(branch.get("is_archived", False)):
        raise Issue42MainMergeError("Source branch is already archived")
    if branch.get("merged_into_branch_id") not in (None, ""):
        raise Issue42MainMergeError("Source branch already records a merge target")

    staged = staging42._verify_published_branch(
        client,
        main_live=main_live,
        main_agent=main_agent,
        branch_id=source_branch_id,
        expected_v2=expected_v2,
        tool_payload=tool_payload,
    )

    preview = client.get_merge_preview(
        agent_id,
        source_branch_id,
        main_branch_id,
    )
    preview_safe = staging42._verify_merge_preview(preview, staged["agent"])

    return {
        "raw": {
            "source_branch_id": source_branch_id,
            "source_version_id": staged["raw"]["version_id"],
        },
        "safe": {
            **staged["safe"],
            "merge_preview": {
                "target_main_branch_id_sha256": main_live["safe"][
                    "main_branch_id_sha256"
                ],
                **preview_safe,
            },
        },
        "agent": staged["agent"],
    }


def _post_merge_readback(
    client: Issue42MainMergeClient,
    *,
    main_before: dict[str, Any],
    source: dict[str, Any],
    expected_v2: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    raw = main_before["raw"]
    safe = main_before["safe"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    tool_id = raw["tool_id"]

    main_agent = client.get_agent(agent_id)
    if main_agent.get("branch_id") != main_branch_id:
        raise Issue42MainMergeError("Post-merge current branch is not exact Main")
    if main_agent.get("main_branch_id") != main_branch_id:
        raise Issue42MainMergeError("Post-merge main_branch_id changed")

    new_version_id = main_agent.get("version_id")
    if not isinstance(new_version_id, str) or not new_version_id:
        raise Issue42MainMergeError("Post-merge Main omitted version_id")
    if planner.staging.safe_id_fingerprint(new_version_id) == safe["version_id_sha256"]:
        raise Issue42MainMergeError("Post-merge Main version did not advance")

    source_agent = source["agent"]
    for field in (
        "name",
        "conversation_config",
        "platform_settings",
        "workflow",
        "procedures",
    ):
        if main_agent.get(field) != source_agent.get(field):
            raise Issue42MainMergeError(
                f"Post-merge Main differs from verified source at {field}"
            )

    operator_id, operator = staging42._procedure_by_name(
        client,
        main_agent,
        main_branch_id,
        "Operator breakdown",
    )
    technician_id, technician = staging42._procedure_by_name(
        client,
        main_agent,
        main_branch_id,
        "Technician pre-close",
    )

    operator_fp = staging42._fingerprint(operator)
    target_fp = staging42._target_operator_fingerprint(expected_v2, tool_id)
    if operator_fp != target_fp:
        raise Issue42MainMergeError("Post-merge Main Operator is not exact V2")

    technician_fp = staging42._fingerprint(technician)
    if technician_fp != safe["technician"]:
        raise Issue42MainMergeError("Post-merge Technician changed unexpectedly")

    try:
        planner.staging.verify_tool_contract(client.get_tool(tool_id), tool_payload)
    except planner.staging.StagingError as exc:
        raise Issue42MainMergeError(str(exc)) from exc

    source_branch_id = source["raw"]["source_branch_id"]
    source_summary = staging42._branch_status_by_id(
        client,
        agent_id,
        source_branch_id,
    )
    source_detail = client.get_branch(agent_id, source_branch_id)

    if source_summary.get("is_archived") is not True:
        raise Issue42MainMergeError("Source branch was not archived after merge")
    if source_detail.get("is_archived") is not True:
        raise Issue42MainMergeError("Source branch detail is not archived after merge")
    if source_summary.get("current_live_percentage") not in (0, 0.0):
        raise Issue42MainMergeError("Archived source branch has live traffic")
    if source_summary.get("draft_exists") is not False:
        raise Issue42MainMergeError("Archived source branch unexpectedly has a draft")
    if source_summary.get("merged_into_branch_id") != main_branch_id:
        raise Issue42MainMergeError(
            "Archived source branch does not identify exact Main as merge target"
        )

    main_branch_summary = staging42._branch_status_by_id(
        client,
        agent_id,
        main_branch_id,
    )
    if main_branch_summary.get("is_archived") is True:
        raise Issue42MainMergeError("Provider Main is unexpectedly archived")
    if main_branch_summary.get("draft_exists") is not False:
        raise Issue42MainMergeError("Provider Main unexpectedly has a draft")

    return {
        "main_branch_id_sha256": planner.staging.safe_id_fingerprint(main_branch_id),
        "previous_main_version_id_sha256": safe["version_id_sha256"],
        "new_main_version_id_sha256": planner.staging.safe_id_fingerprint(
            new_version_id
        ),
        "source_branch_id_sha256": planner.staging.safe_id_fingerprint(
            source_branch_id
        ),
        "source_version_id_sha256": planner.staging.safe_id_fingerprint(
            source["raw"]["source_version_id"]
        ),
        "operator_procedure_id_sha256": planner.staging.safe_id_fingerprint(
            operator_id
        ),
        "technician_procedure_id_sha256": planner.staging.safe_id_fingerprint(
            technician_id
        ),
        "operator": operator_fp,
        "technician": technician_fp,
        "tool_id_sha256": safe["tool_id_sha256"],
        "tool_name": safe["tool_name"],
        "main_matches_verified_source": True,
        "source_archived": True,
        "source_live_percentage": source_summary.get("current_live_percentage"),
        "source_draft_exists": source_summary.get("draft_exists"),
        "source_merged_into_main": True,
        "main_draft_exists": main_branch_summary.get("draft_exists"),
    }


def _raw_values(*objects: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for obj in objects:
        for value in obj.values():
            if isinstance(value, str) and value:
                values.append(value)
    return values


def execute_authorized_main_merge(
    client: Issue42MainMergeClient,
    expected_v1: dict[str, Any],
    expected_v2: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    planner.validate_expected_delta(expected_v1, expected_v2)
    try:
        planner.staging.validate_tool_create_payload(tool_payload)
    except planner.staging.StagingError as exc:
        raise Issue42MainMergeError(str(exc)) from exc

    # Exact Main V1 readback is the first hard precondition.
    try:
        main_before = planner.collect_live_main(client, tool_payload, expected_v1)
    except (
        planner.AlignmentError,
        planner.staging.StagingError,
    ) as exc:
        raise Issue42MainMergeError(str(exc)) from exc

    raw = main_before["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    main_agent = client.get_agent(agent_id)

    source = _source_summary(
        client,
        main_live=main_before,
        main_agent=main_agent,
        expected_v2=expected_v2,
        tool_payload=tool_payload,
    )

    # Re-read exact Main immediately before the single merge POST.
    try:
        main_pre_merge = planner.collect_live_main(
            client,
            tool_payload,
            expected_v1,
        )
    except (
        planner.AlignmentError,
        planner.staging.StagingError,
    ) as exc:
        raise Issue42MainMergeError(str(exc)) from exc
    if main_pre_merge["safe"] != main_before["safe"]:
        raise Issue42MainMergeError("Provider Main moved after merge preview")

    source_pre_merge = _source_summary(
        client,
        main_live=main_before,
        main_agent=main_agent,
        expected_v2=expected_v2,
        tool_payload=tool_payload,
    )
    if source_pre_merge["safe"] != source["safe"]:
        raise Issue42MainMergeError("Verified source moved before merge POST")

    client.merge_once(
        agent_id,
        source["raw"]["source_branch_id"],
        main_branch_id,
    )
    if client.merge_post_count != 1:
        raise Issue42MainMergeError("Expected exactly one provider merge POST")

    post = _post_merge_readback(
        client,
        main_before=main_before,
        source=source,
        expected_v2=expected_v2,
        tool_payload=tool_payload,
    )

    evidence = {
        "schema_version": 2,
        "mode": "ISSUE42_AUTHORIZED_PROVIDER_MAIN_MERGE_EXECUTED",
        "provider": "ElevenLabs",
        "issue": 42,
        "pre_merge": {
            "main_version_id_sha256": main_before["safe"]["version_id_sha256"],
            "main_branch_id_sha256": main_before["safe"]["main_branch_id_sha256"],
            "operator": main_before["safe"]["operator"],
            "technician": main_before["safe"]["technician"],
            "source": source["safe"],
        },
        "merge": {
            "post_count": client.merge_post_count,
            "force": False,
            "archive_source_branch": True,
            "target_main_branch_id_sha256": main_before["safe"][
                "main_branch_id_sha256"
            ],
            "performed": True,
        },
        "post_merge": post,
        "provider_main_merge_performed": True,
        "provider_main_merge_authorized": True,
        "repository_ready_authorized": False,
        "repository_merge_authorized": False,
        "gate3_retry_authorized": False,
        "next_gate": "STOP_FOR_POST_MERGE_AUDIT_AND_ALBERT_REPOSITORY_DECISION",
    }

    encoded = planner.staging.canonical_json(evidence)
    secrets = _raw_values(main_before["raw"], source["raw"])
    for secret in secrets:
        if secret and secret in encoded:
            raise Issue42MainMergeError("Sanitized evidence leaked raw provider identifiers")
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-v1", required=True)
    parser.add_argument("--expected-v2", required=True)
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-authorized-main-merge", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_authorized_main_merge:
        print(
            "ERROR: --execute-authorized-main-merge is required; no provider merge performed",
            file=sys.stderr,
        )
        return 2

    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set", file=sys.stderr)
        return 2

    try:
        expected_v1 = _load_object(args.expected_v1)
        expected_v2 = _load_object(args.expected_v2)
        tool_payload = _load_object(args.tool_config)

        evidence = execute_authorized_main_merge(
            Issue42MainMergeClient(key),
            expected_v1,
            expected_v2,
            tool_payload,
        )
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

        print("BODYSHOP_ISSUE42_PROVIDER_MAIN_MERGE=PASS")
        print("PROVIDER_MAIN_MERGE_PERFORMED=YES")
        print("FORCE=FALSE")
        print("SOURCE_ARCHIVED=YES")
        print(f"NEXT_GATE={evidence['next_gate']}")
    except Issue42MergeOutcomeUnknown as exc:
        print(f"UNCERTAIN_OUTCOME: {exc}", file=sys.stderr)
        print("DO_NOT_RETRY_MERGE_POST=YES", file=sys.stderr)
        return 3
    except (
        Issue42MainMergeError,
        staging42.Issue42StagingError,
        planner.AlignmentError,
        planner.staging.StagingError,
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
