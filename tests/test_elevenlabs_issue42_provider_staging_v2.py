import copy
import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MODULE_PATH = TOOLS / "elevenlabs_issue42_provider_staging_v2.py"
V1_PATH = ROOT / "elevenlabs" / "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json"
V2_PATH = ROOT / "elevenlabs" / "GATE3_WORKSHOP_INSTALLATION_EXPECTED_PROVIDER_CONFIGURATION_V2.json"
TOOL_PATH = ROOT / "elevenlabs" / "CONFIRMED_INTAKE_CLIENT_TOOL_V1.json"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location("issue42_provider_staging_v2", MODULE_PATH)
stage = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = stage
spec.loader.exec_module(stage)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class FakeProvider:
    def __init__(self, v1, v2, tool, existing_target=False):
        self.v1 = v1
        self.v2 = v2
        self.tool = tool
        self.agent_id = "agent_RAW"
        self.main_branch_id = "main_RAW"
        self.main_version_id = "mainversion_RAW"
        self.tool_id = "tool_RAW"
        self.branch_id = "branch_RAW"
        self.operator_id = "op_RAW"
        self.technician_id = "tech_RAW"
        self.branch_exists = existing_target
        self.published = existing_target
        self.draft = None
        self.calls = []

        self.main_agent = {
            "agent_id": self.agent_id,
            "branch_id": self.main_branch_id,
            "main_branch_id": self.main_branch_id,
            "version_id": self.main_version_id,
            "name": "AI Control",
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": "prompt",
                        "llm": "qwen35-397b-a17b",
                        "tool_ids": [self.tool_id],
                    },
                    "language": "es",
                    "dynamic_variables": {
                        "dynamic_variable_placeholders": {
                            "activation_verified": "",
                            "active_breakdown_count": "",
                            "breakdown_ref": "",
                            "caller_role": "",
                            "channel_mode": "",
                            "flow_stage": "",
                            "known_identity": "",
                            "known_installation": "",
                            "known_model": "",
                            "known_operation": "",
                        }
                    },
                },
                "tts": {"voice_id": "voice_RAW"},
            },
            "platform_settings": {"auth": {"enable_auth": False}},
            "workflow": {
                "__xi_procedure__op_RAW/node": {"text": "gate2"},
                "__xi_procedure__tech_RAW/node": {"text": "same"},
            },
            "procedures": {
                self.operator_id: {"name": "Operator breakdown", "version_id": "opv1_RAW"},
                self.technician_id: {
                    "name": "Technician pre-close",
                    "version_id": "techv_RAW",
                },
            },
        }

        self.technician = {
            "procedure_id": self.technician_id,
            "version_id": "techv_RAW",
            "name": "Technician pre-close",
            "type": "free_form",
            "trigger": "Technician trigger",
            "content": "Technician content",
        }

    def _operator(self):
        expected = self.v2 if self.published else self.v1
        item = stage.planner.materialize_operator(expected, self.tool_id)
        return {
            "procedure_id": self.operator_id,
            "version_id": "opv2_RAW" if self.published else "opv1_RAW",
            **item,
        }

    def _branch_agent(self):
        agent = copy.deepcopy(self.main_agent)
        agent["branch_id"] = self.branch_id
        agent["version_id"] = "branchversion2_RAW" if self.published else "branchversion0_RAW"
        if self.published:
            agent["procedures"][self.operator_id]["version_id"] = "opv2_RAW"
            agent["workflow"]["__xi_procedure__op_RAW/node"]["text"] = "gate3-v2"
        return agent

    def list_branches(self, agent_id, include_archived=False):
        if not self.branch_exists:
            return {"results": []}
        return {"results": [self.get_branch(agent_id, self.branch_id)]}

    def create_isolated_branch(self, agent_id, *, parent_version_id):
        self.calls.append(("POST_BRANCH", agent_id, parent_version_id))
        self.branch_exists = True
        return {
            "created_branch_id": self.branch_id,
            "created_version_id": "branchversion0_RAW",
        }

    def get_branch(self, agent_id, branch_id):
        return {
            "id": self.branch_id,
            "name": stage.BRANCH_NAME,
            "description": stage.BRANCH_DESCRIPTION,
            "parent_branch": {"id": self.main_branch_id, "name": "Main"},
            "current_live_percentage": 0,
            "is_archived": False,
            "draft_exists": self.draft is not None and not self.published,
            "commits_ahead": 1 if self.published else 0,
            "commits_behind": 0,
        }

    def get_agent(self, agent_id, branch_id=None):
        return copy.deepcopy(self._branch_agent() if branch_id else self.main_agent)

    def get_procedure(self, agent_id, branch_id, procedure_id):
        if procedure_id == self.operator_id:
            return copy.deepcopy(self._operator())
        if procedure_id == self.technician_id:
            return copy.deepcopy(self.technician)
        raise AssertionError("unexpected procedure")

    def get_procedure_draft(self, agent_id, branch_id, procedure_id):
        if self.draft is None:
            raise AssertionError("draft not available")
        return {
            "procedure_id": self.operator_id,
            **copy.deepcopy(self.draft),
        }

    def update_operator_draft(self, agent_id, branch_id, procedure_id, payload):
        self.calls.append(("PATCH_DRAFT", agent_id, branch_id, procedure_id))
        self.draft = copy.deepcopy(payload)
        return {
            "procedure_id": self.operator_id,
            **copy.deepcopy(payload),
        }

    def publish_isolated_branch(self, agent_id, branch_id):
        self.calls.append(("PATCH_PUBLISH", agent_id, branch_id))
        if self.draft is None:
            raise AssertionError("publish without draft")
        self.published = True
        self.draft = None
        return {
            "agent_id": self.agent_id,
            "branch_id": self.branch_id,
            "version_id": "branchversion2_RAW",
        }

    def get_tool(self, tool_id):
        return copy.deepcopy(self.tool)

    def get_merge_preview(self, agent_id, source_branch_id, target_branch_id):
        self.calls.append(("GET_PREVIEW", agent_id, source_branch_id, target_branch_id))
        preview = self._branch_agent()
        preview["conflicts"] = []
        preview["overridden_fields"] = []
        return preview


class Issue42ProviderStagingTests(unittest.TestCase):
    def setUp(self):
        self.v1 = load(V1_PATH)
        self.v2 = load(V2_PATH)
        self.tool = load(TOOL_PATH)

    def _main_live(self, fake):
        source = stage.planner.materialize_operator(self.v1, fake.tool_id)
        operator_fp = stage._fingerprint({**source, "version_id": "opv1_RAW"})
        tech_fp = stage._fingerprint(fake.technician)
        return {
            "raw": {
                "agent_id": fake.agent_id,
                "main_branch_id": fake.main_branch_id,
                "version_id": fake.main_version_id,
                "tool_id": fake.tool_id,
                "operator_procedure_id": fake.operator_id,
                "technician_procedure_id": fake.technician_id,
            },
            "safe": {
                "agent_id_sha256": stage.planner.staging.safe_id_fingerprint(fake.agent_id),
                "main_branch_id_sha256": stage.planner.staging.safe_id_fingerprint(
                    fake.main_branch_id
                ),
                "version_id_sha256": stage.planner.staging.safe_id_fingerprint(
                    fake.main_version_id
                ),
                "system_prompt_sha256": "prompt_hash",
                "system_prompt_length": 6,
                "language": "es",
                "llm_id": "qwen35-397b-a17b",
                "dynamic_variable_names": list(stage.planner.BASELINE["dynamic_variable_names"]),
                "voice_id_sha256": "voice_hash",
                "auth_enable_auth": False,
                "tool_id_sha256": stage.planner.staging.safe_id_fingerprint(fake.tool_id),
                "tool_name": "bodyshop_resolve_confirmed_intake",
                "operator_procedure_id_sha256": stage.planner.staging.safe_id_fingerprint(
                    fake.operator_id
                ),
                "technician_procedure_id_sha256": stage.planner.staging.safe_id_fingerprint(
                    fake.technician_id
                ),
                "operator": operator_fp,
                "technician": tech_fp,
                "main_draft_exists": False,
            },
        }

    def test_required_execute_flag_is_fail_closed(self):
        output = ROOT / "never-created-issue42-staging.json"
        if output.exists():
            output.unlink()
        rc = stage.main(
            [
                "--expected-v1",
                str(V1_PATH),
                "--expected-v2",
                str(V2_PATH),
                "--tool-config",
                str(TOOL_PATH),
                "--output",
                str(output),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(output.exists())

    def test_client_rejects_unapproved_write_paths(self):
        client = stage.Issue42ProviderClient("x")
        with self.assertRaises(stage.Issue42StagingError):
            client._request("DELETE", "/v1/convai/agents/x")
        with self.assertRaises(stage.Issue42StagingError):
            client._request(
                "POST",
                "/v1/convai/agents/a/branches/b/merge",
                body={},
            )
        with self.assertRaises(stage.Issue42StagingError):
            client._request(
                "PATCH",
                "/v1/convai/agents/a/branches/b",
                body={},
            )

    def test_branch_guard_rejects_live_archived_behind_and_no_ahead(self):
        baseline = {
            "name": stage.BRANCH_NAME,
            "description": stage.BRANCH_DESCRIPTION,
            "parent_branch": {"id": "main_RAW"},
            "current_live_percentage": 0,
            "is_archived": False,
            "commits_ahead": 1,
            "commits_behind": 0,
        }
        stage._verify_branch_meta(
            baseline,
            main_branch_id="main_RAW",
            require_ahead=True,
        )

        mutations = [
            ("current_live_percentage", 1),
            ("is_archived", True),
            ("commits_behind", 1),
            ("commits_ahead", 0),
        ]
        for field, value in mutations:
            moved = copy.deepcopy(baseline)
            moved[field] = value
            with self.assertRaises(stage.Issue42StagingError):
                stage._verify_branch_meta(
                    moved,
                    main_branch_id="main_RAW",
                    require_ahead=True,
                )

    def test_execute_fresh_branch_runs_only_authorized_mutations_and_preview(self):
        fake = FakeProvider(self.v1, self.v2, self.tool)
        live = self._main_live(fake)

        with mock.patch.object(
            stage.planner,
            "collect_live_main",
            side_effect=[copy.deepcopy(live)] * 4,
        ):
            evidence = stage.execute_authorized_staging(
                fake,
                self.v1,
                self.v2,
                self.tool,
            )

        self.assertEqual(
            ["POST_BRANCH", "PATCH_DRAFT", "PATCH_PUBLISH", "GET_PREVIEW"],
            [call[0] for call in fake.calls],
        )
        self.assertTrue(evidence["isolated"]["branch_created_this_run"])
        self.assertEqual("PATCHED_AND_VERIFIED", evidence["isolated"]["draft_action"])
        self.assertEqual("PUBLISHED_ISOLATED_V2", evidence["isolated"]["publish_action"])
        self.assertEqual(0, evidence["isolated"]["current_live_percentage"])
        self.assertTrue(
            evidence["isolated"]["workflow_diff_only_in_operator_namespace"]
        )
        self.assertFalse(
            evidence["isolated"]["workflow_diff_touches_technician_namespace"]
        )
        self.assertEqual(0, evidence["merge_preview"]["conflicts_count"])
        self.assertEqual(0, evidence["merge_preview"]["overridden_fields_count"])
        self.assertFalse(evidence["provider_main_merge_performed"])
        self.assertFalse(evidence["provider_main_merge_authorized"])
        self.assertEqual(
            "STOP_FOR_ALBERT_PROVIDER_MAIN_MERGE_AUTHORIZATION",
            evidence["next_gate"],
        )

        encoded = json.dumps(evidence)
        for raw in (
            fake.agent_id,
            fake.main_branch_id,
            fake.main_version_id,
            fake.tool_id,
            fake.branch_id,
            fake.operator_id,
            fake.technician_id,
        ):
            self.assertNotIn(raw, encoded)

    def test_recovery_of_already_published_exact_v2_performs_no_write(self):
        fake = FakeProvider(
            self.v1,
            self.v2,
            self.tool,
            existing_target=True,
        )
        live = self._main_live(fake)

        with mock.patch.object(
            stage.planner,
            "collect_live_main",
            side_effect=[copy.deepcopy(live)] * 3,
        ):
            evidence = stage.execute_authorized_staging(
                fake,
                self.v1,
                self.v2,
                self.tool,
            )

        self.assertEqual(["GET_PREVIEW"], [call[0] for call in fake.calls])
        self.assertFalse(evidence["isolated"]["branch_created_this_run"])
        self.assertEqual("NONE", evidence["isolated"]["draft_action"])
        self.assertEqual("NONE", evidence["isolated"]["publish_action"])

    def test_existing_unexpected_draft_fails_closed_before_publish(self):
        fake = FakeProvider(self.v1, self.v2, self.tool, existing_target=True)
        fake.published = False
        fake.draft = {
            **stage.planner.materialize_operator(self.v1, fake.tool_id),
        }
        live = self._main_live(fake)

        with mock.patch.object(
            stage.planner,
            "collect_live_main",
            return_value=copy.deepcopy(live),
        ):
            with self.assertRaises(stage.Issue42StagingError):
                stage.execute_authorized_staging(
                    fake,
                    self.v1,
                    self.v2,
                    self.tool,
                )
        self.assertNotIn("PATCH_PUBLISH", [call[0] for call in fake.calls])

    def test_merge_preview_conflict_blocks_success_without_main_merge_capability(self):
        fake = FakeProvider(self.v1, self.v2, self.tool)
        live = self._main_live(fake)

        original_preview = fake.get_merge_preview

        def conflict_preview(*args, **kwargs):
            preview = original_preview(*args, **kwargs)
            preview["conflicts"] = [{"field": "workflow"}]
            return preview

        fake.get_merge_preview = conflict_preview

        with mock.patch.object(
            stage.planner,
            "collect_live_main",
            side_effect=[copy.deepcopy(live)] * 3,
        ):
            with self.assertRaises(stage.Issue42StagingError):
                stage.execute_authorized_staging(
                    fake,
                    self.v1,
                    self.v2,
                    self.tool,
                )

        self.assertFalse(hasattr(fake, "merge"))
        self.assertFalse(hasattr(stage.Issue42ProviderClient, "merge"))

    def test_target_is_exactly_v2_and_preserves_v1_tool_contract(self):
        target = stage._target_operator_fingerprint(self.v2, "tool_RAW")
        source = stage._target_operator_fingerprint(self.v1, "tool_RAW")
        self.assertNotEqual(source["content_sha256"], target["content_sha256"])
        self.assertEqual(source["trigger_sha256"], target["trigger_sha256"])
        self.assertEqual(self.v1["client_tool"], self.v2["client_tool"])


if __name__ == "__main__":
    unittest.main()
