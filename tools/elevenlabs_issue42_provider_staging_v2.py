#!/usr/bin/env python3
"""BODYSHOP Voice PoC #42 — authorized isolated provider staging V2.

Authorized boundary:
- create or safely recover one zero-live ElevenLabs branch from the exact
  accepted Main version;
- stage only the V2 Operator workshop/install semantic correction;
- publish only that isolated branch;
- exact readback of the isolated result;
- GET-only merge preview into Main with force=false.

This executable CANNOT merge to provider Main. It exposes no merge mutation
method and rejects any write outside the exact branch-create / Procedure-draft /
isolated-publish allowlist.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import elevenlabs_issue42_workshop_installation_alignment_v2 as planner

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
BRANCH_NAME = "bodyshop-workshop-installation-issue-42"
BRANCH_DESCRIPTION = "BODYSHOP #42 workshop/install semantic alignment staging"
VERSION_DESCRIPTION = "BODYSHOP #42 publish workshop/install semantic alignment"
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class Issue42StagingError(RuntimeError):
    pass


def _safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise Issue42StagingError(f"Invalid {label}")
    return urllib.parse.quote(value, safe="")


class Issue42ProviderClient:
    """GET plus three exact write operations. No Main merge capability."""

    def __init__(self, api_key: str, base_url: str = API_BASE):
        self.api_key = api_key
        self.base_url = base_url

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if method not in {"GET", "POST", "PATCH"}:
            raise Issue42StagingError(f"Unsupported method {method}")

        if method == "POST":
            if not re.fullmatch(
                r"/v1/convai/agents/[A-Za-z0-9_-]+/branches",
                path,
            ):
                raise Issue42StagingError("POST outside authorized branch-create boundary")
        elif method == "PATCH":
            draft_ok = bool(
                re.fullmatch(
                    r"/v1/convai/agents/[A-Za-z0-9_-]+/branches/"
                    r"[A-Za-z0-9_-]+/procedures/[A-Za-z0-9_-]+/draft",
                    path,
                )
            )
            publish_ok = bool(
                re.fullmatch(r"/v1/convai/agents/[A-Za-z0-9_-]+", path)
                and isinstance(query, dict)
                and set(query) == {"branch_id"}
                and isinstance(query.get("branch_id"), str)
                and query.get("branch_id")
            )
            if not (draft_ok or publish_ok):
                raise Issue42StagingError("PATCH outside authorized isolated boundary")

        qs = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}" + (f"?{qs}" if qs else "")
        data = None
        headers = {
            "accept": "application/json",
            "xi-api-key": self.api_key,
            "user-agent": "bodyshop-voice-poc-issue42-provider-staging-v2/1",
        }
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["content-type"] = "application/json"

        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise Issue42StagingError(
                f"ElevenLabs {method} failed: HTTP {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise Issue42StagingError(
                f"ElevenLabs {method} failed due to a network error"
            ) from exc

        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise Issue42StagingError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise Issue42StagingError(
                "ElevenLabs returned an unexpected non-object response"
            )
        return parsed

    def get(self, path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
        return self._request("GET", path, query=query)

    # Read interface required by planner.collect_live_main.
    def list_agents(self, name: str, cursor: str | None = None) -> dict[str, Any]:
        query = {"page_size": "100", "search": name, "archived": "false"}
        if cursor:
            query["cursor"] = cursor
        return self.get("/v1/convai/agents", query)

    def get_agent(self, agent_id: str, branch_id: str | None = None) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        query = {"branch_id": branch_id} if branch_id else None
        return self.get(f"/v1/convai/agents/{aid}", query)

    def list_branches(
        self,
        agent_id: str,
        include_archived: bool = False,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        return self.get(
            f"/v1/convai/agents/{aid}/branches",
            {
                "include_archived": "true" if include_archived else "false",
                "include_commit_status": "true",
                "limit": "100",
            },
        )

    def get_branch(self, agent_id: str, branch_id: str) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        bid = _safe_identifier(branch_id, "branch_id")
        return self.get(f"/v1/convai/agents/{aid}/branches/{bid}")

    def get_procedure(
        self,
        agent_id: str,
        branch_id: str,
        procedure_id: str,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        bid = _safe_identifier(branch_id, "branch_id")
        pid = _safe_identifier(procedure_id, "procedure_id")
        return self.get(
            f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}"
        )

    def get_procedure_draft(
        self,
        agent_id: str,
        branch_id: str,
        procedure_id: str,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        bid = _safe_identifier(branch_id, "branch_id")
        pid = _safe_identifier(procedure_id, "procedure_id")
        return self.get(
            f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}/draft"
        )

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        tid = _safe_identifier(tool_id, "tool_id")
        return self.get(f"/v1/convai/tools/{tid}")

    def get_merge_preview(
        self,
        agent_id: str,
        source_branch_id: str,
        target_branch_id: str,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        sid = _safe_identifier(source_branch_id, "source_branch_id")
        return self.get(
            f"/v1/convai/agents/{aid}/branches/{sid}/merge-preview",
            {
                "target_branch_id": target_branch_id,
                "force": "false",
            },
        )

    # Exact write operations 1, 3 and 4 from the authorized write-set.
    def create_isolated_branch(
        self,
        agent_id: str,
        *,
        parent_version_id: str,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        return self._request(
            "POST",
            f"/v1/convai/agents/{aid}/branches",
            body={
                "parent_version_id": parent_version_id,
                "name": BRANCH_NAME,
                "description": BRANCH_DESCRIPTION,
                "include_draft": False,
            },
        )

    def update_operator_draft(
        self,
        agent_id: str,
        branch_id: str,
        procedure_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        bid = _safe_identifier(branch_id, "branch_id")
        pid = _safe_identifier(procedure_id, "procedure_id")
        return self._request(
            "PATCH",
            f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}/draft",
            body=payload,
        )

    def publish_isolated_branch(
        self,
        agent_id: str,
        branch_id: str,
    ) -> dict[str, Any]:
        aid = _safe_identifier(agent_id, "agent_id")
        _safe_identifier(branch_id, "branch_id")
        return self._request(
            "PATCH",
            f"/v1/convai/agents/{aid}",
            body={"version_description": VERSION_DESCRIPTION},
            query={"branch_id": branch_id},
        )


def _load_object(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Issue42StagingError(f"Unable to load JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise Issue42StagingError("JSON root must be an object")
    return value


def _parent_branch_id(branch: dict[str, Any]) -> str | None:
    direct = branch.get("parent_branch_id")
    if isinstance(direct, str) and direct:
        return direct
    nested = branch.get("parent_branch")
    if isinstance(nested, dict):
        value = nested.get("id")
        return value if isinstance(value, str) and value else None
    return None


def _verify_branch_meta(
    branch: dict[str, Any],
    *,
    main_branch_id: str,
    require_ahead: bool,
) -> None:
    if branch.get("name") != BRANCH_NAME:
        raise Issue42StagingError("Isolated branch name mismatch")
    if branch.get("description") != BRANCH_DESCRIPTION:
        raise Issue42StagingError("Isolated branch description mismatch")
    if _parent_branch_id(branch) != main_branch_id:
        raise Issue42StagingError("Isolated branch parent is not exact Main")
    if branch.get("current_live_percentage") not in (0, 0.0):
        raise Issue42StagingError("Isolated branch unexpectedly has live traffic")
    if bool(branch.get("is_archived", False)):
        raise Issue42StagingError("Isolated branch is archived")

    behind = branch.get("commits_behind")
    if behind not in (0, None):
        raise Issue42StagingError("Isolated branch is behind Main")

    ahead = branch.get("commits_ahead")
    if require_ahead:
        if not isinstance(ahead, int) or ahead <= 0:
            raise Issue42StagingError("Isolated branch has no published change")
    elif ahead not in (0, None):
        raise Issue42StagingError(
            "Unmodified/recovery branch contains unexpected published commits"
        )


def _branch_status_by_id(
    client: Issue42ProviderClient,
    agent_id: str,
    branch_id: str,
) -> dict[str, Any]:
    """Read branch-list status fields with include_commit_status=true.

    ElevenLabs exposes draft_exists / commits_ahead / commits_behind on the
    branch LIST surface, not on GET /branches/{branch_id}. Keep those schemas
    separate and fail closed if the branch is not found exactly once.
    """
    results = client.list_branches(agent_id, include_archived=True).get("results", [])
    if not isinstance(results, list):
        raise Issue42StagingError("Branch listing omitted results")
    matches = [
        row
        for row in results
        if isinstance(row, dict) and row.get("id") == branch_id
    ]
    if len(matches) != 1:
        raise Issue42StagingError(
            "Target branch status was not found exactly once in branch listing"
        )
    return matches[0]


def _combined_branch_state(
    client: Issue42ProviderClient,
    agent_id: str,
    branch_id: str,
) -> dict[str, Any]:
    """Combine documented single-branch detail with list-only status fields."""
    detail = client.get_branch(agent_id, branch_id)
    summary = _branch_status_by_id(client, agent_id, branch_id)

    for field in (
        "name",
        "description",
        "current_live_percentage",
        "is_archived",
    ):
        if summary.get(field) != detail.get(field):
            raise Issue42StagingError(
                f"Branch detail/list disagreement at {field}"
            )

    detail_parent = _parent_branch_id(detail)
    summary_parent = summary.get("parent_branch_id")
    if detail_parent != summary_parent:
        raise Issue42StagingError("Branch detail/list parent disagreement")

    combined = dict(detail)
    for field in (
        "parent_branch_id",
        "draft_exists",
        "draft_created_at",
        "draft_is_behind_tip",
        "commits_ahead",
        "commits_behind",
        "merged_into_branch_id",
    ):
        combined[field] = summary.get(field)
    return combined


def _find_target_branch(
    client: Issue42ProviderClient,
    agent_id: str,
) -> dict[str, Any] | None:
    results = client.list_branches(agent_id, include_archived=True).get("results", [])
    if not isinstance(results, list):
        raise Issue42StagingError("Branch listing omitted results")
    matches = [
        row
        for row in results
        if isinstance(row, dict) and row.get("name") == BRANCH_NAME
    ]
    if len(matches) > 1:
        raise Issue42StagingError("Target branch name exists more than once")
    return matches[0] if matches else None


def _procedure_by_name(
    client: Issue42ProviderClient,
    branch_agent: dict[str, Any],
    branch_id: str,
    name: str,
) -> tuple[str, dict[str, Any]]:
    effective = branch_agent.get("procedures")
    if not isinstance(effective, dict) or len(effective) != 2:
        raise Issue42StagingError(
            "Branch effective Procedure map must contain exactly two Procedures"
        )
    matches = [
        pid
        for pid, meta in effective.items()
        if isinstance(pid, str)
        and isinstance(meta, dict)
        and meta.get("name") == name
    ]
    if len(matches) != 1:
        raise Issue42StagingError(
            f"Expected exactly one effective Procedure named {name!r}"
        )
    pid = matches[0]
    return pid, client.get_procedure(branch_agent["agent_id"], branch_id, pid)


def _fingerprint(item: dict[str, Any]) -> dict[str, Any]:
    try:
        return planner.staging.semantic_procedure_fingerprint(item)
    except planner.staging.StagingError as exc:
        raise Issue42StagingError(str(exc)) from exc


def _target_operator_fingerprint(
    expected_v2: dict[str, Any],
    tool_id: str,
) -> dict[str, Any]:
    target = planner.materialize_operator(expected_v2, tool_id)
    fp = _fingerprint({**target, "version_id": "expected"})
    fp["version_present"] = True
    return fp


def _same_semantics(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    left = dict(actual)
    right = dict(expected)
    left.pop("version_present", None)
    right.pop("version_present", None)
    return left == right


def _diff_paths(left: Any, right: Any, path: str = "$") -> list[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        out: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}"
            if key not in left or key not in right:
                out.append(child)
            else:
                out.extend(_diff_paths(left[key], right[key], child))
        return out
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return [path]
        out: list[str] = []
        for index, (lvalue, rvalue) in enumerate(zip(left, right)):
            out.extend(_diff_paths(lvalue, rvalue, f"{path}[{index}]"))
        return out
    return [] if left == right else [path]


def _verify_static_retention(
    main_agent: dict[str, Any],
    branch_agent: dict[str, Any],
) -> None:
    if branch_agent.get("name") != main_agent.get("name"):
        raise Issue42StagingError("Isolated agent name changed")
    if branch_agent.get("conversation_config") != main_agent.get("conversation_config"):
        raise Issue42StagingError("Isolated conversation_config changed")
    if branch_agent.get("platform_settings") != main_agent.get("platform_settings"):
        raise Issue42StagingError("Isolated platform_settings changed")


def _verify_published_branch(
    client: Issue42ProviderClient,
    *,
    main_live: dict[str, Any],
    main_agent: dict[str, Any],
    branch_id: str,
    expected_v2: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    raw = main_live["raw"]
    safe = main_live["safe"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    tool_id = raw["tool_id"]

    branch = _combined_branch_state(client, agent_id, branch_id)
    _verify_branch_meta(
        branch,
        main_branch_id=main_branch_id,
        require_ahead=True,
    )
    if bool(branch.get("draft_exists", False)):
        raise Issue42StagingError("Isolated branch still has a Procedure draft")

    branch_agent = client.get_agent(agent_id, branch_id)
    _verify_static_retention(main_agent, branch_agent)

    operator_id, operator = _procedure_by_name(
        client,
        branch_agent,
        branch_id,
        "Operator breakdown",
    )
    technician_id, technician = _procedure_by_name(
        client,
        branch_agent,
        branch_id,
        "Technician pre-close",
    )

    operator_fp = _fingerprint(operator)
    target_fp = _target_operator_fingerprint(expected_v2, tool_id)
    if operator_fp != target_fp:
        raise Issue42StagingError(
            "Published Operator breakdown does not match exact V2 target"
        )

    technician_fp = _fingerprint(technician)
    if technician_fp != safe["technician"]:
        raise Issue42StagingError("Technician pre-close changed unexpectedly")

    try:
        planner.staging.verify_tool_contract(client.get_tool(tool_id), tool_payload)
    except planner.staging.StagingError as exc:
        raise Issue42StagingError(str(exc)) from exc

    main_workflow = main_agent.get("workflow")
    branch_workflow = branch_agent.get("workflow")
    workflow_paths = _diff_paths(main_workflow, branch_workflow)
    if not workflow_paths:
        raise Issue42StagingError(
            "Published V2 did not produce an observable Operator compiled-workflow delta"
        )

    operator_token = "__xi_procedure__" + operator_id + "/"
    technician_token = "__xi_procedure__" + technician_id + "/"
    if any(operator_token not in path for path in workflow_paths):
        raise Issue42StagingError(
            "Compiled workflow delta escaped the Operator procedure namespace"
        )
    if any(technician_token in path for path in workflow_paths):
        raise Issue42StagingError(
            "Compiled workflow delta touched Technician procedure namespace"
        )

    version_id = branch_agent.get("version_id")
    if not isinstance(version_id, str) or not version_id:
        raise Issue42StagingError("Published isolated branch omitted version_id")
    if planner.staging.safe_id_fingerprint(version_id) == safe["version_id_sha256"]:
        raise Issue42StagingError("Isolated branch version did not advance from Main")

    return {
        "raw": {
            "branch_id": branch_id,
            "version_id": version_id,
            "operator_procedure_id": operator_id,
            "technician_procedure_id": technician_id,
        },
        "safe": {
            "branch_id_sha256": planner.staging.safe_id_fingerprint(branch_id),
            "version_id_sha256": planner.staging.safe_id_fingerprint(version_id),
            "parent_main_branch_id_sha256": safe["main_branch_id_sha256"],
            "current_live_percentage": branch.get("current_live_percentage"),
            "draft_exists": bool(branch.get("draft_exists", False)),
            "is_archived": bool(branch.get("is_archived", False)),
            "commits_ahead": branch.get("commits_ahead"),
            "commits_behind": branch.get("commits_behind"),
            "operator_procedure_id_sha256": planner.staging.safe_id_fingerprint(
                operator_id
            ),
            "technician_procedure_id_sha256": planner.staging.safe_id_fingerprint(
                technician_id
            ),
            "operator": operator_fp,
            "technician": technician_fp,
            "workflow_diff_count": len(workflow_paths),
            "workflow_diff_only_in_operator_namespace": True,
            "workflow_diff_touches_technician_namespace": False,
            "tool_id_sha256": safe["tool_id_sha256"],
            "tool_name": safe["tool_name"],
        },
        "agent": branch_agent,
    }


def _verify_merge_preview(
    preview: dict[str, Any],
    source_agent: dict[str, Any],
) -> dict[str, Any]:
    conflicts = preview.get("conflicts") or []
    overridden = preview.get("overridden_fields") or []
    if not isinstance(conflicts, list) or not isinstance(overridden, list):
        raise Issue42StagingError("Merge-preview conflict metadata is malformed")
    if conflicts:
        raise Issue42StagingError("Merge-preview contains conflicts")
    if overridden:
        raise Issue42StagingError("Merge-preview contains overridden fields")

    if preview.get("name") != source_agent.get("name"):
        raise Issue42StagingError("Merge-preview agent name differs from source")
    if preview.get("conversation_config") != source_agent.get("conversation_config"):
        raise Issue42StagingError("Merge-preview conversation_config differs from source")
    if preview.get("procedures") != source_agent.get("procedures"):
        raise Issue42StagingError("Merge-preview Procedures differ from source")
    for field in ("platform_settings", "workflow"):
        if field in preview and preview.get(field) != source_agent.get(field):
            raise Issue42StagingError(
                f"Merge-preview differs from source at {field}"
            )

    return {
        "conflicts_count": 0,
        "overridden_fields_count": 0,
        "preview_matches_verified_source": True,
        "force": False,
    }


def _raw_ids(evidence_source: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for value in evidence_source.values():
        if isinstance(value, str) and value:
            out.append(value)
    return out


def execute_authorized_staging(
    client: Issue42ProviderClient,
    expected_v1: dict[str, Any],
    expected_v2: dict[str, Any],
    tool_payload: dict[str, Any],
) -> dict[str, Any]:
    planner.validate_expected_delta(expected_v1, expected_v2)
    try:
        planner.staging.validate_tool_create_payload(tool_payload)
    except planner.staging.StagingError as exc:
        raise Issue42StagingError(str(exc)) from exc

    # Exact Main re-read immediately before any provider write.
    try:
        main_before = planner.collect_live_main(client, tool_payload, expected_v1)
    except (
        planner.AlignmentError,
        planner.staging.StagingError,
    ) as exc:
        raise Issue42StagingError(str(exc)) from exc

    raw = main_before["raw"]
    agent_id = raw["agent_id"]
    main_branch_id = raw["main_branch_id"]
    main_version_id = raw["version_id"]
    tool_id = raw["tool_id"]
    main_agent = client.get_agent(agent_id)

    target_fp = _target_operator_fingerprint(expected_v2, tool_id)
    source_fp = main_before["safe"]["operator"]

    existing = _find_target_branch(client, agent_id)
    branch_created = False
    if existing is None:
        created = client.create_isolated_branch(
            agent_id,
            parent_version_id=main_version_id,
        )
        branch_id = created.get("created_branch_id")
        created_version_id = created.get("created_version_id")
        if not isinstance(branch_id, str) or not branch_id:
            raise Issue42StagingError(
                "Create branch response omitted created_branch_id"
            )
        if not isinstance(created_version_id, str) or not created_version_id:
            raise Issue42StagingError(
                "Create branch response omitted created_version_id"
            )
        branch_created = True
    else:
        branch_id = existing.get("id")
        if not isinstance(branch_id, str) or not branch_id:
            raise Issue42StagingError("Existing target branch omitted id")

    branch = _combined_branch_state(client, agent_id, branch_id)
    branch_agent = client.get_agent(agent_id, branch_id)
    _verify_static_retention(main_agent, branch_agent)

    operator_id, operator = _procedure_by_name(
        client,
        branch_agent,
        branch_id,
        "Operator breakdown",
    )
    _, technician = _procedure_by_name(
        client,
        branch_agent,
        branch_id,
        "Technician pre-close",
    )
    operator_fp = _fingerprint(operator)
    technician_fp = _fingerprint(technician)
    if technician_fp != main_before["safe"]["technician"]:
        raise Issue42StagingError("Inherited Technician pre-close moved")

    already_published = operator_fp == target_fp and not bool(
        branch.get("draft_exists", False)
    )

    draft_action = "NONE"
    publish_action = "NONE"

    if already_published:
        _verify_branch_meta(
            branch,
            main_branch_id=main_branch_id,
            require_ahead=True,
        )
    else:
        if operator_fp != source_fp:
            raise Issue42StagingError(
                "Existing isolated Operator is neither exact Gate-2 V1 nor exact V2"
            )
        _verify_branch_meta(
            branch,
            main_branch_id=main_branch_id,
            require_ahead=False,
        )

        target_payload = planner.materialize_operator(expected_v2, tool_id)

        if bool(branch.get("draft_exists", False)):
            draft = client.get_procedure_draft(agent_id, branch_id, operator_id)
            if not _same_semantics(_fingerprint(draft), target_fp):
                raise Issue42StagingError(
                    "Existing Procedure draft does not match exact V2 target"
                )
            draft_action = "RECOVERED_EXISTING_EXACT_V2_DRAFT"
        else:
            updated = client.update_operator_draft(
                agent_id,
                branch_id,
                operator_id,
                target_payload,
            )
            if not _same_semantics(_fingerprint(updated), target_fp):
                raise Issue42StagingError(
                    "Draft PATCH response does not match exact V2 target"
                )
            draft = client.get_procedure_draft(agent_id, branch_id, operator_id)
            if not _same_semantics(_fingerprint(draft), target_fp):
                raise Issue42StagingError(
                    "Draft GET readback does not match exact V2 target"
                )
            draft_action = "PATCHED_AND_VERIFIED"

        # Main must still be the exact accepted Gate-2 version immediately
        # before publishing the isolated draft.
        try:
            main_pre_publish = planner.collect_live_main(
                client,
                tool_payload,
                expected_v1,
            )
        except (
            planner.AlignmentError,
            planner.staging.StagingError,
        ) as exc:
            raise Issue42StagingError(str(exc)) from exc
        if main_pre_publish["safe"] != main_before["safe"]:
            raise Issue42StagingError("Provider Main moved before isolated publish")

        published = client.publish_isolated_branch(agent_id, branch_id)
        published_branch_id = published.get("branch_id")
        if published_branch_id not in (None, branch_id):
            raise Issue42StagingError("Publish response returned a different branch")
        published_version = published.get("version_id")
        if not isinstance(published_version, str) or not published_version:
            raise Issue42StagingError("Publish response omitted version_id")
        publish_action = "PUBLISHED_ISOLATED_V2"

    # Operation 5: exact isolated readback.
    staged = _verify_published_branch(
        client,
        main_live=main_before,
        main_agent=main_agent,
        branch_id=branch_id,
        expected_v2=expected_v2,
        tool_payload=tool_payload,
    )

    # Main still must be unchanged before operation 6.
    try:
        main_pre_preview = planner.collect_live_main(
            client,
            tool_payload,
            expected_v1,
        )
    except (
        planner.AlignmentError,
        planner.staging.StagingError,
    ) as exc:
        raise Issue42StagingError(str(exc)) from exc
    if main_pre_preview["safe"] != main_before["safe"]:
        raise Issue42StagingError("Provider Main moved before merge-preview")

    # Operation 6: GET-only, force=false.
    preview = client.get_merge_preview(
        agent_id,
        branch_id,
        main_branch_id,
    )
    preview_safe = _verify_merge_preview(preview, staged["agent"])

    # Re-read both sides after preview; no merge is allowed here.
    try:
        main_after_preview = planner.collect_live_main(
            client,
            tool_payload,
            expected_v1,
        )
    except (
        planner.AlignmentError,
        planner.staging.StagingError,
    ) as exc:
        raise Issue42StagingError(str(exc)) from exc
    if main_after_preview["safe"] != main_before["safe"]:
        raise Issue42StagingError("Provider Main moved after merge-preview")

    staged_after_preview = _verify_published_branch(
        client,
        main_live=main_before,
        main_agent=main_agent,
        branch_id=branch_id,
        expected_v2=expected_v2,
        tool_payload=tool_payload,
    )
    if staged_after_preview["safe"] != staged["safe"]:
        raise Issue42StagingError("Isolated branch moved after merge-preview")

    evidence = {
        "schema_version": 2,
        "mode": "ISSUE42_AUTHORIZED_ISOLATED_STAGING_EXECUTED",
        "provider": "ElevenLabs",
        "issue": 42,
        "main": {
            "version_id_sha256": main_before["safe"]["version_id_sha256"],
            "main_branch_id_sha256": main_before["safe"]["main_branch_id_sha256"],
            "operator": main_before["safe"]["operator"],
            "technician": main_before["safe"]["technician"],
            "provider_main_modified": False,
        },
        "isolated": {
            "branch_name": BRANCH_NAME,
            "branch_description": BRANCH_DESCRIPTION,
            "branch_created_this_run": branch_created,
            "draft_action": draft_action,
            "publish_action": publish_action,
            **staged["safe"],
        },
        "target": {
            "expected_state": "GATE3_WORKSHOP_INSTALLATION_EXPECTED_PROVIDER_CONFIGURATION_V2",
            "operator": target_fp,
            "changed_step_indexes": [1, 3],
        },
        "merge_preview": {
            "target_main_branch_id_sha256": main_before["safe"][
                "main_branch_id_sha256"
            ],
            **preview_safe,
        },
        "provider_write_operations_authorized": [1, 2, 3, 4, 5, 6],
        "provider_main_merge_performed": False,
        "provider_main_merge_authorized": False,
        "next_gate": "STOP_FOR_ALBERT_PROVIDER_MAIN_MERGE_AUTHORIZATION",
    }

    encoded = planner.staging.canonical_json(evidence)
    secrets = _raw_ids(main_before["raw"]) + _raw_ids(staged["raw"])
    for secret in secrets:
        if secret and secret in encoded:
            raise Issue42StagingError("Sanitized evidence leaked a raw provider identifier")
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-v1", required=True)
    parser.add_argument("--expected-v2", required=True)
    parser.add_argument("--tool-config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--execute-authorized-staging", action="store_true")
    args = parser.parse_args(argv)

    if not args.execute_authorized_staging:
        print(
            "ERROR: --execute-authorized-staging is required; no provider write performed",
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
        evidence = execute_authorized_staging(
            Issue42ProviderClient(key),
            expected_v1,
            expected_v2,
            tool_payload,
        )
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print("BODYSHOP_ISSUE42_PROVIDER_STAGING=PASS")
        print("PROVIDER_MAIN_MODIFIED=NO")
        print("PROVIDER_MAIN_MERGE_PERFORMED=NO")
        print(f"NEXT_GATE={evidence['next_gate']}")
    except (
        Issue42StagingError,
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
