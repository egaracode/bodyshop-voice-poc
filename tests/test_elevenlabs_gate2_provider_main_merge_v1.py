import copy
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
    "gate2_merge", TOOLS / "elevenlabs_gate2_provider_main_merge_v1.py"
)
gate2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate2)


class MergeUnitTests(unittest.TestCase):
    def test_required_flag_is_fail_closed(self):
        output = ROOT / "never-created-gate2-main-merge.json"
        if output.exists():
            output.unlink()
        rc = gate2.main(
            [
                "--expected",
                str(ROOT / "elevenlabs" / "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json"),
                "--tool-config",
                str(ROOT / "elevenlabs" / "CONFIRMED_INTAKE_CLIENT_TOOL_V1.json"),
                "--output",
                str(output),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(output.exists())

    def test_merge_is_non_force_and_archives_source(self):
        self.assertFalse(gate2.MERGE_FORCE)
        self.assertTrue(gate2.MERGE_ARCHIVE_SOURCE)

    def test_source_branch_requires_exact_safe_merge_state(self):
        branch = {
            "name": gate2.staging.STAGING_BRANCH_NAME,
            "description": gate2.staging.STAGING_DESCRIPTION,
            "parent_branch_id": "main_RAW",
            "current_live_percentage": 0,
            "draft_exists": False,
            "is_archived": False,
            "commits_ahead": 3,
            "commits_behind": 0,
        }
        gate2._validate_source_branch_meta(branch, main_branch_id="main_RAW")

        for field, value in (
            ("current_live_percentage", 1),
            ("draft_exists", True),
            ("is_archived", True),
            ("commits_behind", 1),
            ("commits_ahead", 0),
        ):
            moved = copy.deepcopy(branch)
            moved[field] = value
            with self.assertRaises(gate2.ProviderMainMergeError):
                gate2._validate_source_branch_meta(moved, main_branch_id="main_RAW")

    def test_preview_rejects_conflicts_and_overrides(self):
        source = {
            "name": "AI Control",
            "conversation_config": {"agent": {"prompt": {"tool_ids": ["tool_RAW"]}}},
            "procedures": {"op_RAW": {"version_id": "opv_RAW"}},
            "platform_settings": {"auth": {"enable_auth": False}},
            "workflow": None,
        }
        ok = {
            **copy.deepcopy(source),
            "overridden_fields": [],
            "conflicts": [],
        }
        gate2._verify_preview(ok, source)

        conflict = copy.deepcopy(ok)
        conflict["conflicts"] = [{"field": "conversation_config.agent.prompt.tool_ids"}]
        with self.assertRaises(gate2.ProviderMainMergeError):
            gate2._verify_preview(conflict, source)

        overridden = copy.deepcopy(ok)
        overridden["overridden_fields"] = ["conversation_config.agent.prompt.tool_ids"]
        with self.assertRaises(gate2.ProviderMainMergeError):
            gate2._verify_preview(overridden, source)

    def test_preview_rejects_hybrid_target(self):
        source = {
            "name": "AI Control",
            "conversation_config": {"agent": {"prompt": {"tool_ids": ["tool_RAW"]}}},
            "procedures": {"op_RAW": {"version_id": "opv_RAW"}},
        }
        preview = {
            **copy.deepcopy(source),
            "overridden_fields": [],
            "conflicts": [],
        }
        preview["conversation_config"]["agent"]["prompt"]["tool_ids"] = []
        with self.assertRaises(gate2.ProviderMainMergeError):
            gate2._verify_preview(preview, source)

    def test_preflight_signature_changes_on_safe_state_movement(self):
        value = {"safe": {"source_version_id_sha256": "a", "commits_ahead": 3}}
        moved = {"safe": {"source_version_id_sha256": "b", "commits_ahead": 4}}
        self.assertNotEqual(
            gate2._preflight_signature(value),
            gate2._preflight_signature(moved),
        )

    def test_executor_uses_preview_then_non_force_merge_then_post_readback(self):
        pre = {
            "raw": {
                "agent_id": "agent_RAW",
                "main_branch_id": "main_RAW",
                "source_branch_id": "source_RAW",
                "source_version_id": "sourcev_RAW",
                "tool_id": "tool_RAW",
            },
            "safe": {
                "main": {"x": 1},
                "source": {"y": 2},
                "source_branch_id_sha256": "s",
                "source_version_id_sha256": "v",
                "tool_id_sha256": "t",
                "commits_ahead": 3,
                "commits_behind": 0,
            },
            "source_agent": {
                "name": "AI Control",
                "conversation_config": {"agent": {"prompt": {"tool_ids": ["tool_RAW"]}}},
                "procedures": {"op_RAW": {"version_id": "opv_RAW"}},
            },
        }
        preview = {
            **copy.deepcopy(pre["source_agent"]),
            "overridden_fields": [],
            "conflicts": [],
        }

        class MergeClient:
            def __init__(self):
                self.calls = []

            def get(self, path, query=None):
                self.calls.append(("GET", path, None, query))
                return copy.deepcopy(preview)

            def post_with_query(self, path, body, query):
                self.calls.append(("POST", path, copy.deepcopy(body), copy.deepcopy(query)))
                return {}

        merge_client = MergeClient()
        read_client = mock.Mock()
        expected = {"runtime_risk": {"forced_tool_behavior": "EVIDENCE_REQUIRED_IN_GATE_3"}}
        tool_payload = {"tool_config": {"name": "bodyshop_resolve_confirmed_intake"}}

        with mock.patch.object(gate2, "_preflight", side_effect=[pre, copy.deepcopy(pre)]), \
             mock.patch.object(gate2, "_verify_post_merge_main", return_value={"tool_attached": True}) as post, \
             mock.patch.object(gate2, "_verify_archived_source", return_value={"is_archived": True}) as archived:
            evidence = gate2.execute_provider_main_merge(
                read_client,
                merge_client,
                expected,
                tool_payload,
            )

        self.assertEqual("GET", merge_client.calls[0][0])
        self.assertTrue(merge_client.calls[0][1].endswith("/merge-preview"))
        self.assertEqual("false", merge_client.calls[0][3]["force"])
        self.assertEqual("POST", merge_client.calls[1][0])
        self.assertTrue(merge_client.calls[1][1].endswith("/merge"))
        self.assertEqual(
            {"archive_source_branch": True, "force": False},
            merge_client.calls[1][2],
        )
        self.assertEqual({"target_branch_id": "main_RAW"}, merge_client.calls[1][3])
        post.assert_called_once()
        archived.assert_called_once()
        self.assertTrue(evidence["provider_main_merge_performed"])
        self.assertTrue(evidence["source_branch_archived"])
        self.assertEqual("STOP_BEFORE_GATE_3_RUNTIME_CONVERSATION", evidence["next_gate"])

    def test_state_movement_after_preview_blocks_post(self):
        first = {
            "raw": {
                "agent_id": "agent_RAW",
                "main_branch_id": "main_RAW",
                "source_branch_id": "source_RAW",
                "source_version_id": "sourcev_RAW",
                "tool_id": "tool_RAW",
            },
            "safe": {"source_version_id_sha256": "one"},
            "source_agent": {
                "name": "AI Control",
                "conversation_config": {},
                "procedures": {},
            },
        }
        second = copy.deepcopy(first)
        second["safe"]["source_version_id_sha256"] = "two"

        class MergeClient:
            def __init__(self):
                self.posts = 0

            def get(self, path, query=None):
                return {
                    "name": "AI Control",
                    "conversation_config": {},
                    "procedures": {},
                    "overridden_fields": [],
                    "conflicts": [],
                }

            def post_with_query(self, path, body, query):
                self.posts += 1
                return {}

        client = MergeClient()
        with mock.patch.object(gate2, "_preflight", side_effect=[first, second]):
            with self.assertRaises(gate2.ProviderMainMergeError):
                gate2.execute_provider_main_merge(mock.Mock(), client, {}, {})
        self.assertEqual(0, client.posts)

    def test_source_contains_no_force_true_or_gate3_execution(self):
        source = (TOOLS / "elevenlabs_gate2_provider_main_merge_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn('"force": True', source)
        self.assertNotIn('"force": "true"', source)
        self.assertIn('"force": "false"', source)
        self.assertIn('"force": MERGE_FORCE', source)
        self.assertNotIn("simulate_conversation", source)
        self.assertNotIn("/conversations", source)


if __name__ == "__main__":
    unittest.main()
