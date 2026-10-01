#!/usr/bin/env python3
"""Voice Reference Resolution Harness V1.

Offline, provider-neutral and non-authoritative by construction.
It resolves confirmed observation labels only against an explicit local
compatibility fixture. It never calls BODYSHOP, Supabase or a provider and
never invents canonical reference identities.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FIXTURE_AUTHORITY = "NON_CANONICAL_TEST_FIXTURE"
FIXTURE_REFERENCE_PREFIX = "fixture-ref-"
SCHEMA_VERSION = 1
OUTCOMES = ("RESOLVED", "INCOMPLETE", "AMBIGUOUS", "NOT_FOUND")
GRAINS = ("DEVICE", "DEVICE_SUBDEVICE")
REQUIRED_CONTEXT = ("workshop_scope", "model", "installation", "operation", "device")


class HarnessError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResolutionResult:
    outcome: str
    reference_path_id: str | None = None
    grain: str | None = None
    reason: str | None = None
    candidate_count: int | None = None
    missing_fields: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "outcome": self.outcome,
            "reference_path_id": self.reference_path_id,
            "grain": self.grain,
        }
        if self.reason is not None:
            payload["reason"] = self.reason
        if self.candidate_count is not None:
            payload["candidate_count"] = self.candidate_count
        if self.missing_fields:
            payload["missing_fields"] = list(self.missing_fields)
        return payload


def normalize_label(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    folded = unicodedata.normalize("NFKD", value)
    without_marks = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", without_marks.casefold())


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HarnessError(f"{label} must be a non-empty string")
    return value


def _validate_node(node: Any, label: str) -> None:
    if not isinstance(node, dict):
        raise HarnessError(f"{label} must be an object")
    _require_text(node.get("value"), f"{label}.value")
    aliases = node.get("aliases", [])
    if not isinstance(aliases, list) or any(
        not isinstance(alias, str) or not alias.strip() for alias in aliases
    ):
        raise HarnessError(f"{label}.aliases must be a list of non-empty strings")


def _canonical_key(path: dict[str, Any]) -> tuple[str, ...]:
    subdevice = path.get("subdevice")
    return (
        normalize_label(path["workshop"]["value"]),
        normalize_label(path["model"]["value"]),
        normalize_label(path["installation"]["value"]),
        normalize_label(path["operation"]["value"]),
        normalize_label(path["device"]["value"]),
        normalize_label(subdevice["value"]) if isinstance(subdevice, dict) else "",
        path["grain"],
    )


def validate_fixture(fixture: Any) -> None:
    if not isinstance(fixture, dict):
        raise HarnessError("Fixture must be a JSON object")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        raise HarnessError(f"Fixture schema_version must be {SCHEMA_VERSION}")
    if fixture.get("authority") != FIXTURE_AUTHORITY:
        raise HarnessError(
            f"Fixture authority must be {FIXTURE_AUTHORITY!r}; canonical data is not accepted"
        )

    paths = fixture.get("paths")
    if not isinstance(paths, list) or not paths:
        raise HarnessError("Fixture paths must be a non-empty list")

    seen_ids: set[str] = set()
    seen_canonical: set[tuple[str, ...]] = set()
    for index, path in enumerate(paths):
        label = f"paths[{index}]"
        if not isinstance(path, dict):
            raise HarnessError(f"{label} must be an object")

        reference_path_id = _require_text(
            path.get("reference_path_id"), f"{label}.reference_path_id"
        )
        if not reference_path_id.startswith(FIXTURE_REFERENCE_PREFIX):
            raise HarnessError(
                f"{label}.reference_path_id must use non-canonical prefix "
                f"{FIXTURE_REFERENCE_PREFIX!r}"
            )
        if reference_path_id in seen_ids:
            raise HarnessError(f"Duplicate reference_path_id {reference_path_id!r}")
        seen_ids.add(reference_path_id)

        grain = path.get("grain")
        if grain not in GRAINS:
            raise HarnessError(f"{label}.grain must be DEVICE or DEVICE_SUBDEVICE")
        if not isinstance(path.get("active"), bool):
            raise HarnessError(f"{label}.active must be boolean")

        for field in ("workshop", "model", "installation", "operation", "device"):
            _validate_node(path.get(field), f"{label}.{field}")

        subdevice = path.get("subdevice")
        if grain == "DEVICE":
            if subdevice is not None:
                raise HarnessError(f"{label}.subdevice must be null for DEVICE grain")
        else:
            _validate_node(subdevice, f"{label}.subdevice")

        key = _canonical_key(path)
        if key in seen_canonical:
            raise HarnessError(f"Duplicate canonical fixture path at {label}")
        seen_canonical.add(key)


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"Unable to load fixture: {exc}") from exc
    validate_fixture(payload)
    return payload


def _matches(node: dict[str, Any], observed: str) -> bool:
    needle = normalize_label(observed)
    if not needle:
        return False
    values = [node["value"], *node.get("aliases", [])]
    return needle in {normalize_label(value) for value in values}


def _device_context_key(path: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        normalize_label(path[field]["value"])
        for field in ("workshop", "model", "installation", "operation", "device")
    )


def resolve_reference(fixture: dict[str, Any], observation: dict[str, Any]) -> ResolutionResult:
    validate_fixture(fixture)
    if not isinstance(observation, dict):
        raise HarnessError("Observation must be an object")

    missing = tuple(
        field
        for field in REQUIRED_CONTEXT
        if not isinstance(observation.get(field), str) or not observation[field].strip()
    )
    if missing:
        return ResolutionResult(
            outcome="INCOMPLETE",
            reason="required_context_missing",
            missing_fields=missing,
        )

    active = [path for path in fixture["paths"] if path["active"] is True]
    parent_fields = (
        ("workshop", "workshop_scope"),
        ("model", "model"),
        ("installation", "installation"),
        ("operation", "operation"),
    )
    contextual = [
        path
        for path in active
        if all(
            _matches(path[path_field], observation[obs_field])
            for path_field, obs_field in parent_fields
        )
    ]
    if not contextual:
        return ResolutionResult(outcome="NOT_FOUND", reason="parent_context_not_found")

    device_matches = [
        path for path in contextual if _matches(path["device"], observation["device"])
    ]
    if not device_matches:
        return ResolutionResult(outcome="NOT_FOUND", reason="device_not_found")

    device_contexts: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for path in device_matches:
        device_contexts.setdefault(_device_context_key(path), []).append(path)
    if len(device_contexts) > 1:
        return ResolutionResult(
            outcome="AMBIGUOUS",
            reason="multiple_device_candidates",
            candidate_count=len(device_contexts),
        )

    paths_for_device = next(iter(device_contexts.values()))
    subdevice_value = observation.get("subdevice")
    if subdevice_value is not None and not isinstance(subdevice_value, str):
        return ResolutionResult(
            outcome="INCOMPLETE",
            reason="invalid_subdevice_value",
            missing_fields=("subdevice",),
        )
    if isinstance(subdevice_value, str) and subdevice_value.strip():
        child_matches = [
            path
            for path in paths_for_device
            if path["grain"] == "DEVICE_SUBDEVICE"
            and _matches(path["subdevice"], subdevice_value)
        ]
        if not child_matches:
            return ResolutionResult(outcome="NOT_FOUND", reason="subdevice_not_found")

        children: dict[str, list[dict[str, Any]]] = {}
        for path in child_matches:
            children.setdefault(normalize_label(path["subdevice"]["value"]), []).append(path)
        if len(children) > 1:
            return ResolutionResult(
                outcome="AMBIGUOUS",
                reason="multiple_subdevice_candidates",
                candidate_count=len(children),
            )

        paths_for_child = next(iter(children.values()))
        if len(paths_for_child) != 1:
            raise HarnessError("Validated fixture produced duplicate child paths")
        path = paths_for_child[0]
        return ResolutionResult(
            outcome="RESOLVED",
            reference_path_id=path["reference_path_id"],
            grain=path["grain"],
            reason="unique_selectable_path",
        )

    device_paths = [path for path in paths_for_device if path["grain"] == "DEVICE"]
    if len(device_paths) == 1:
        path = device_paths[0]
        return ResolutionResult(
            outcome="RESOLVED",
            reference_path_id=path["reference_path_id"],
            grain=path["grain"],
            reason="unique_selectable_path",
        )
    if len(device_paths) > 1:
        raise HarnessError("Validated fixture produced duplicate device paths")

    if any(path["grain"] == "DEVICE_SUBDEVICE" for path in paths_for_device):
        return ResolutionResult(outcome="INCOMPLETE", reason="subdevice_required")

    return ResolutionResult(outcome="NOT_FOUND", reason="selectable_path_not_found")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--workshop")
    parser.add_argument("--model")
    parser.add_argument("--installation")
    parser.add_argument("--operation")
    parser.add_argument("--device")
    parser.add_argument("--subdevice")
    args = parser.parse_args(argv)

    observation = {
        "workshop_scope": args.workshop,
        "model": args.model,
        "installation": args.installation,
        "operation": args.operation,
        "device": args.device,
        "subdevice": args.subdevice,
    }
    try:
        fixture = load_fixture(args.fixture)
        result = resolve_reference(fixture, observation)
    except HarnessError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2

    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0 if result.outcome == "RESOLVED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
