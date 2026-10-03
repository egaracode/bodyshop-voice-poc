import importlib.util
import json
import pathlib
import sys
import unittest

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


class FakeReadClient:
    def __init__(self):
        self.agent_id = "agent_RAW"
        self.main_branch_id = "main_RAW"
        self.version_id = "version_RAW"
        self.tech_pid = "tech_RAW"

    def list_agents(self, name, cursor=None):
        return {"agents": [{"name": name, "agent_id": self.agent_id}], "has_more": False}

    def get_agent(self, agent_id):
        return {
            "name": "AI Control",
            "branch_id": self.main_branch_id,
            "main_branch_id": self.main_branch_id,
            "version_id": self.version_id,
            "conversation_config": {
                "agent": {
                    "language": "es",
                    "first_message": "x",
                    "prompt": {"llm": "qwen35-397b-a17b", "prompt": "x"},
                    "dynamic_variables": {"dynamic_variable_placeholders": {}},
                },
                "tts": {},
            },
        }

    def list_branches(self, agent_id):
        return {
            "results": [
                {
                    "id": self.main_branch_id,
                    "name": "Main",
                    "is_archived": False,
                    "draft_exists": False,
                    "commits_ahead": 0,
                    "commits_behind": 0,
                }
            ]
        }


class FakeWriteClient:
    def __init__(self):
        self.calls = []


class StagingUnitTests(unittest.TestCase):
    def test_client_rejects_delete_and_put(self):
        client = staging.StagingClient("x")
        with self.assertRaises(staging.StagingError):
            client._request("DELETE", "/x")
        with self.assertRaises(staging.StagingError):
            client._request("PUT", "/x")

    def test_required_flag_is_fail_closed(self):
        rc = staging.main(
            [
                "--expected",
                str(ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"),
                "--output",
                str(ROOT / "never-created.json"),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse((ROOT / "never-created.json").exists())

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
        self.assertNotIn("FINAL_ISOLATED_CONFIG_APPROVAL_REQUIRED\",\n                \"approval_gate", source)
        self.assertNotIn("archive_source_branch", source)

    def test_evidence_contract_declares_main_unmodified(self):
        # Contract-level guard: the only success evidence value allowed is False.
        source = (TOOLS / "elevenlabs_provider_staging_v1.py").read_text(encoding="utf-8")
        self.assertIn('"provider_main_modified": False', source)
        self.assertIn('"next_gate": "FINAL_ISOLATED_CONFIG_APPROVAL_REQUIRED"', source)


if __name__ == "__main__":
    unittest.main()
