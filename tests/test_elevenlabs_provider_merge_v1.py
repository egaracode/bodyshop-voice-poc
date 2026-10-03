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
    "gate_c", TOOLS / "elevenlabs_provider_merge_v1.py"
)
gate_c = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate_c)

import elevenlabs_provider_reconciliation_v1 as planner


def load_expected():
    return json.loads(
        (ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json").read_text(
            encoding="utf-8"
        )
    )


class FakeMergeClient:
    def __init__(self):
        self.calls = []

    def get(self, path, query=None):
        self.calls.append(("GET", path, None, query))
        if path.endswith("/merge-preview"):
            return {
                "conversation_config": {
                    "agent": {
                        "prompt": {"prompt": load_expected()["agent"]["system_prompt"]}
                    },
                    "tts": {"voice_id": "eric_RAW"},
                },
                "procedures": {
                    "op_RAW": {
                        "procedure_id": "op_RAW",
                        "version_id": "opv_RAW",
                        "name": "Operator breakdown",
                        "type": "deterministic",
                    },
                    "tech_RAW": {
                        "procedure_id": "tech_RAW",
                        "version_id": "techv_RAW",
                        "name": "Technician pre-close",
                        "type": "free_form",
                    },
                },
                "overridden_fields": [],
                "conflicts": [],
            }
        raise AssertionError(f"unexpected GET {path}")

    def post_with_query(self, path, body, query):
        self.calls.append(("POST", path, body, query))
        return {}


class GateCUnitTests(unittest.TestCase):
    def test_required_flag_is_fail_closed(self):
        output = ROOT / "never-created-gate-c.json"
        if output.exists():
            output.unlink()
        rc = gate_c.main(
            [
                "--expected",
                str(ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"),
                "--output",
                str(output),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(output.exists())

    def test_merge_constants_are_non_force_and_archive_source(self):
        self.assertFalse(gate_c.MERGE_FORCE)
        self.assertTrue(gate_c.MERGE_ARCHIVE_SOURCE)

    def test_preview_rejects_conflicts(self):
        expected = load_expected()
        target = planner.derive_expected_target(expected)
        preview = {
            "conversation_config": {
                "agent": {"prompt": {"prompt": expected["agent"]["system_prompt"]}},
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
            "overridden_fields": ["conversation_config.tts.voice_id"],
            "conflicts": [{"field": "conversation_config.tts.voice_id"}],
        }
        with self.assertRaises(gate_c.ProviderMergeError):
            gate_c._verify_preview(
                preview,
                target,
                "eric_RAW",
                {"op_RAW": "opv_RAW", "tech_RAW": "techv_RAW"},
            )

    def test_preview_accepts_exact_conflict_free_target(self):
        expected = load_expected()
        target = planner.derive_expected_target(expected)
        preview = {
            "conversation_config": {
                "agent": {"prompt": {"prompt": expected["agent"]["system_prompt"]}},
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
            "overridden_fields": [],
            "conflicts": [],
        }
        gate_c._verify_preview(
            preview,
            target,
            "eric_RAW",
            {"op_RAW": "opv_RAW", "tech_RAW": "techv_RAW"},
        )

    def test_source_requires_zero_behind_and_positive_ahead(self):
        branch = {
            "id": "source_RAW",
            "name": gate_c.STAGING_BRANCH_NAME,
            "parent_branch_id": "main_RAW",
            "description": gate_c.STAGING_DESCRIPTION,
            "current_live_percentage": 0,
            "draft_exists": False,
            "is_archived": False,
            "commits_behind": 1,
            "commits_ahead": 3,
        }
        client = mock.Mock()
        client.list_branches.return_value = {"results": [branch]}
        with self.assertRaises(gate_c.ProviderMergeError):
            gate_c._find_isolated_branch(client, "agent_RAW", "main_RAW")

        branch["commits_behind"] = 0
        branch["commits_ahead"] = 0
        with self.assertRaises(gate_c.ProviderMergeError):
            gate_c._find_isolated_branch(client, "agent_RAW", "main_RAW")

        branch["commits_ahead"] = 3
        self.assertEqual(
            "source_RAW",
            gate_c._find_isolated_branch(client, "agent_RAW", "main_RAW")["id"],
        )

    def test_effective_target_allows_historical_procedure_identities(self):
        target = {"placeholder": True}
        agent = {"procedures": {"op_RAW": {}, "tech_RAW": {}}}
        historical = [{}, {}, {}, {}]
        refs = {"op_RAW": "opv_RAW", "tech_RAW": "techv_RAW"}
        operator_fp = {"name": "Operator breakdown"}
        technician_fp = {"name": "Technician pre-close"}

        with mock.patch.object(
            gate_c,
            "_select_staged_refs",
            return_value=(refs, operator_fp, technician_fp),
        ) as select, mock.patch.object(
            gate_c,
            "_verify_final_readback",
        ) as verify:
            result = gate_c._verify_effective_target(
                agent,
                historical,
                target,
                "eric_RAW",
            )

        select.assert_called_once_with(historical, target)
        verify.assert_called_once_with(agent, target, "eric_RAW", refs)
        self.assertEqual((refs, operator_fp, technician_fp), result)

    def test_source_does_not_require_historical_procedure_list_to_equal_two(self):
        source = (TOOLS / "elevenlabs_provider_merge_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("if len(source_procedures) != 2", source)
        self.assertNotIn("if len(procedures) != 2", source)

    def test_source_file_pins_preview_and_merge_target_and_force_false(self):
        source = (TOOLS / "elevenlabs_provider_merge_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"target_branch_id": main_branch_id', source)
        self.assertIn('"force": "false"', source)
        self.assertIn('"force": MERGE_FORCE', source)
        self.assertIn('"archive_source_branch": MERGE_ARCHIVE_SOURCE', source)

    def test_source_file_has_post_merge_v2_verification(self):
        source = (TOOLS / "elevenlabs_provider_merge_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("compat_v2.collect_provider_snapshot", source)
        self.assertIn("source_branch_archived", source)
        self.assertIn('"provider_main_modified": True', source)
        self.assertIn(
            '"next_gate": "POST_WRITE_RECONCILIATION_COMPLETE_STOP_BEFORE_GATE_3"',
            source,
        )

    def test_merge_client_posts_query_without_force_override(self):
        class Capture(gate_c.ProviderMergeClient):
            def __init__(self):
                pass

            def _request(self, method, path, body=None, query=None):
                self.captured = (method, path, body, query)
                return {}

        client = Capture()
        client.post_with_query(
            "/merge",
            {"archive_source_branch": True, "force": False},
            {"target_branch_id": "main_RAW"},
        )
        self.assertEqual(
            (
                "POST",
                "/merge",
                {"archive_source_branch": True, "force": False},
                {"target_branch_id": "main_RAW"},
            ),
            client.captured,
        )


if __name__ == "__main__":
    unittest.main()
