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
    "gate_b", TOOLS / "elevenlabs_provider_final_config_v1.py"
)
gate_b = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate_b)

import elevenlabs_provider_reconciliation_v1 as planner
import elevenlabs_provider_staging_v1 as staging


def load_expected():
    return json.loads(
        (ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json").read_text(
            encoding="utf-8"
        )
    )


class FakeReadClient:
    pass


class FakeWriteClient:
    def __init__(self):
        self.calls = []

    def patch(self, path, body, query=None):
        self.calls.append(("PATCH", path, body, query))
        return {"version_id": "ignored_response_RAW"}


class GateBUnitTests(unittest.TestCase):
    def test_required_flag_is_fail_closed(self):
        output = ROOT / "never-created-gate-b.json"
        if output.exists():
            output.unlink()
        rc = gate_b.main(
            [
                "--expected",
                str(ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"),
                "--output",
                str(output),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(output.exists())

    def test_source_has_no_merge_operation(self):
        source = (TOOLS / "elevenlabs_provider_final_config_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("/merge", source)
        self.assertNotIn("archive_source_branch", source)
        self.assertNotIn("force", source)

    def test_select_staged_refs_requires_exact_target(self):
        expected = load_expected()
        target = planner.derive_expected_target(expected)
        by_name = {item["name"]: item for item in expected["procedures"]}
        op = by_name["Operator breakdown"]
        tech = by_name["Technician pre-close"]

        procedures = [
            {
                "procedure_id": "op_RAW",
                "version_id": "opv_RAW",
                "name": "Operator breakdown",
                "type": "deterministic",
                "trigger": op["trigger"],
                "content": planner.canonical_json(
                    {"steps": op["content"]["steps"], "trigger": op["trigger"]}
                ),
            },
            {
                "procedure_id": "tech_RAW",
                "version_id": "techv_RAW",
                "name": "Technician pre-close",
                "type": "free_form",
                "trigger": tech["trigger"],
                "content": tech["content"],
            },
        ]

        refs, _, _ = gate_b._select_staged_refs(procedures, target)
        self.assertEqual({"op_RAW": "opv_RAW", "tech_RAW": "techv_RAW"}, refs)

    def test_build_target_config_changes_only_prompt_and_voice(self):
        expected = load_expected()
        current = {
            "conversation_config": {
                "agent": {
                    "language": "es",
                    "first_message": "unchanged",
                    "prompt": {"prompt": "old", "llm": "qwen35-397b-a17b"},
                },
                "tts": {
                    "voice_id": "old_voice",
                    "model_id": "eleven_flash_v2_5",
                    "speed": 0.9,
                },
                "conversation": {"max_duration_seconds": 600},
            }
        }
        result = gate_b._build_target_config(current, expected, "eric_RAW")
        self.assertEqual(
            expected["agent"]["system_prompt"],
            result["agent"]["prompt"]["prompt"],
        )
        self.assertEqual("eric_RAW", result["tts"]["voice_id"])
        self.assertEqual("qwen35-397b-a17b", result["agent"]["prompt"]["llm"])
        self.assertEqual(0.9, result["tts"]["speed"])
        self.assertEqual(
            {"max_duration_seconds": 600},
            result["conversation"],
        )
        self.assertEqual("old", current["conversation_config"]["agent"]["prompt"]["prompt"])

    def test_verify_final_readback_requires_exact_two_refs(self):
        expected = load_expected()
        target = planner.derive_expected_target(expected)
        branch_agent = {
            "conversation_config": {
                "agent": {
                    "prompt": {"prompt": expected["agent"]["system_prompt"]}
                },
                "tts": {"voice_id": "eric_RAW"},
            },
            "procedures": {
                "op_RAW": {
                    "version_id": "opv_RAW",
                    "name": "Operator breakdown",
                    "type": "deterministic",
                },
                "tech_RAW": {
                    "version_id": "techv_RAW",
                    "name": "Technician pre-close",
                    "type": "free_form",
                },
            },
        }
        gate_b._verify_final_readback(
            branch_agent,
            target,
            "eric_RAW",
            {"op_RAW": "opv_RAW", "tech_RAW": "techv_RAW"},
        )

        branch_agent["procedures"]["extra_RAW"] = {
            "version_id": "x_RAW",
            "name": "Element identification",
            "type": "free_form",
        }
        with self.assertRaises(gate_b.FinalConfigError):
            gate_b._verify_final_readback(
                branch_agent,
                target,
                "eric_RAW",
                {"op_RAW": "opv_RAW", "tech_RAW": "techv_RAW"},
            )

    def test_gate_b_payload_includes_procedure_id_and_version_id(self):
        source = (TOOLS / "elevenlabs_provider_final_config_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"procedure_id": pid', source)
        self.assertIn('"version_id": vid', source)

    def test_evidence_contract_declares_main_unmodified_and_next_gate(self):
        source = (TOOLS / "elevenlabs_provider_final_config_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"provider_main_modified": False', source)
        self.assertIn(
            '"next_gate": "SEPARATE_PROVIDER_MAIN_MERGE_APPROVAL_REQUIRED"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
