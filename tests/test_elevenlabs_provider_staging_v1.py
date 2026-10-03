import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "staging", TOOLS / "elevenlabs_provider_staging_v1.py"
)
staging = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(staging)

import elevenlabs_provider_reconciliation_v1 as planner


def load_expected():
    return json.loads(
        (ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json").read_text(
            encoding="utf-8"
        )
    )


class FakeWriteClient:
    def __init__(self, expected):
        self.calls = []
        by_name = {item["name"]: item for item in expected["procedures"]}
        self.operator = by_name["Operator breakdown"]
        self.technician = by_name["Technician pre-close"]

    def post(self, path, body):
        self.calls.append(("POST", path, body, None))
        if path.endswith("/branches"):
            return {"created_branch_id": "isolated_RAW", "created_version_id": "v0_RAW"}
        if path.endswith("/procedures"):
            return {"procedure_id": "operator_RAW"}
        raise AssertionError(f"unexpected POST {path}")

    def patch(self, path, body, query=None):
        self.calls.append(("PATCH", path, body, query))
        if path.endswith("/draft"):
            return {
                "procedure_id": "tech_RAW",
                "name": "Technician pre-close",
                "content": self.technician["content"],
                "type": "free_form",
                "trigger": self.technician["trigger"],
            }
        if path.endswith("/agents/agent_RAW"):
            return {"version_id": "staged_RAW"}
        raise AssertionError(f"unexpected PATCH {path}")

    def get(self, path, query=None):
        self.calls.append(("GET", path, None, query))
        if path.endswith("/branches/isolated_RAW"):
            return {
                "id": "isolated_RAW",
                "name": staging.STAGING_BRANCH_NAME,
                "current_live_percentage": 0,
                "parent_branch": {"id": "main_RAW", "name": "Main"},
            }
        if path.endswith("/procedures/operator_RAW"):
            return {
                "procedure_id": "operator_RAW",
                "version_id": "operator_version_RAW",
                "name": "Operator breakdown",
                "content": planner.canonical_json(self.operator["content"]),
                "type": "deterministic",
                "trigger": self.operator["trigger"],
            }
        if path.endswith("/procedures/tech_RAW"):
            return {
                "procedure_id": "tech_RAW",
                "version_id": "tech_version_RAW",
                "name": "Technician pre-close",
                "content": self.technician["content"],
                "type": "free_form",
                "trigger": self.technician["trigger"],
            }
        raise AssertionError(f"unexpected GET {path}")


class StagingUnitTests(unittest.TestCase):
    def test_client_rejects_delete_and_put(self):
        client = staging.StagingClient("x")
        with self.assertRaises(staging.StagingError):
            client._request("DELETE", "/x")
        with self.assertRaises(staging.StagingError):
            client._request("PUT", "/x")

    def test_required_flag_is_fail_closed(self):
        output = ROOT / "never-created.json"
        if output.exists():
            output.unlink()
        rc = staging.main(
            [
                "--expected",
                str(ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"),
                "--output",
                str(output),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(output.exists())

    def test_expected_operator_maps_to_deterministic_json_steps(self):
        target = planner.derive_expected_target(load_expected())
        fp = staging.expected_procedure_fingerprint(target, "Operator breakdown")
        self.assertEqual("deterministic", fp["raw_api_type"])
        self.assertEqual("JSON_STEPS", fp["content_shape"])

    def test_expected_technician_remains_free_form_text(self):
        target = planner.derive_expected_target(load_expected())
        fp = staging.expected_procedure_fingerprint(target, "Technician pre-close")
        self.assertEqual("free_form", fp["raw_api_type"])
        self.assertEqual("TEXT", fp["content_shape"])

    def test_staging_constants_pin_gate_a_scope(self):
        self.assertEqual(
            "bodyshop-a5-reconcile-issue-34", staging.STAGING_BRANCH_NAME
        )
        self.assertIn("staging", staging.STAGING_DESCRIPTION.lower())
        self.assertIn("stage Procedure versions", staging.VERSION_DESCRIPTION)

    def test_source_has_no_merge_or_final_config_operation(self):
        source = (TOOLS / "elevenlabs_provider_staging_v1.py").read_text(encoding="utf-8")
        self.assertNotIn("/merge", source)
        self.assertNotIn("archive_source_branch", source)
        self.assertNotIn("system_prompt_sha256", source)

    def test_execute_staging_uses_only_gate_a_sequence_and_sanitized_evidence(self):
        expected = load_expected()
        writer = FakeWriteClient(expected)
        guarded_live = {
            "safe_guard": json.loads(json.dumps(planner.CURRENT_PROVIDER_GUARD_V1)),
            "raw": {
                "agent_id": "agent_RAW",
                "branch_id": "main_RAW",
                "version_id": "version_RAW",
                "main_branch_id": "main_RAW",
                "procedure_ids_by_name": {
                    "Element identification": "element_RAW",
                    "Operator breakdown": "old_operator_RAW",
                    "Technician pre-close": "tech_RAW",
                },
            },
        }

        with (
            mock.patch.object(staging, "collect_live_state", return_value=guarded_live),
            mock.patch.object(staging, "ensure_provider_branch_name_available"),
        ):
            evidence = staging.execute_staging(object(), writer, expected)

        methods_paths = [(method, path) for method, path, _, _ in writer.calls]
        self.assertEqual(
            [
                ("POST", "/v1/convai/agents/agent_RAW/branches"),
                ("GET", "/v1/convai/agents/agent_RAW/branches/isolated_RAW"),
                (
                    "POST",
                    "/v1/convai/agents/agent_RAW/branches/isolated_RAW/procedures",
                ),
                (
                    "PATCH",
                    "/v1/convai/agents/agent_RAW/branches/isolated_RAW/procedures/tech_RAW/draft",
                ),
                ("PATCH", "/v1/convai/agents/agent_RAW"),
                (
                    "GET",
                    "/v1/convai/agents/agent_RAW/branches/isolated_RAW/procedures/operator_RAW",
                ),
                (
                    "GET",
                    "/v1/convai/agents/agent_RAW/branches/isolated_RAW/procedures/tech_RAW",
                ),
            ],
            methods_paths,
        )

        create_branch = writer.calls[0]
        self.assertEqual("version_RAW", create_branch[2]["parent_version_id"])
        self.assertFalse(create_branch[2]["include_draft"])

        publish = writer.calls[4]
        self.assertEqual({"version_description": staging.VERSION_DESCRIPTION}, publish[2])
        self.assertEqual({"branch_id": "isolated_RAW"}, publish[3])

        encoded = json.dumps(evidence, ensure_ascii=False)
        for forbidden in (
            "agent_RAW",
            "main_RAW",
            "version_RAW",
            "isolated_RAW",
            "operator_RAW",
            "tech_RAW",
            "element_RAW",
            "old_operator_RAW",
            "staged_RAW",
            "operator_version_RAW",
            "tech_version_RAW",
        ):
            self.assertNotIn(forbidden, encoded)

        self.assertFalse(evidence["provider_main_modified"])
        self.assertEqual(
            "FINAL_ISOLATED_CONFIG_APPROVAL_REQUIRED", evidence["next_gate"]
        )

    def test_evidence_contract_declares_main_unmodified(self):
        source = (TOOLS / "elevenlabs_provider_staging_v1.py").read_text(encoding="utf-8")
        self.assertIn('"provider_main_modified": False', source)
        self.assertIn('"next_gate": "FINAL_ISOLATED_CONFIG_APPROVAL_REQUIRED"', source)


if __name__ == "__main__":
    unittest.main()
