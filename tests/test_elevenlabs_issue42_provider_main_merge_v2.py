import copy
import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MODULE_PATH = TOOLS / "elevenlabs_issue42_provider_main_merge_v2.py"
V1_PATH = ROOT / "elevenlabs" / "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json"
V2_PATH = ROOT / "elevenlabs" / "GATE3_WORKSHOP_INSTALLATION_EXPECTED_PROVIDER_CONFIGURATION_V2.json"
TOOL_PATH = ROOT / "elevenlabs" / "CONFIRMED_INTAKE_CLIENT_TOOL_V1.json"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location("issue42_provider_main_merge_v2", MODULE_PATH)
merge42 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = merge42
spec.loader.exec_module(merge42)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class FakeMergeProvider:
    def __init__(self, v1, v2, tool):
        self.v1 = v1
        self.v2 = v2
        self.tool = tool

        self.agent_id = "agent_RAW"
        self.main_branch_id = "main_RAW"
        self.main_version_id = "mainversion_RAW"
        self.new_main_version_id = "newmainversion_RAW"
        self.tool_id = "tool_RAW"
        self.source_branch_id = "source_RAW"
        self.source_version_id = "sourceversion_RAW"
        self.operator_id = "operator_RAW"
        self.technician_id = "technician_RAW"

        self.merged = False
        self.merge_post_count = 0
        self.preview_conflicts = []
        self.preview_overrides = []

        self.main_agent_v1 = self._make_agent(
            branch_id=self.main_branch_id,
            version_id=self.main_version_id,
            expected=self.v1,
            operator_version="opv1_RAW",
            workflow_text="gate2",
        )
        self.source_agent = self._make_agent(
            branch_id=self.source_branch_id,
            version_id=self.source_version_id,
            expected=self.v2,
            operator_version="opv2_RAW",
            workflow_text="gate3-v2",
        )

        self.technician = {
            "procedure_id": self.technician_id,
            "version_id": "techv_RAW",
            "name": "Technician pre-close",
            "type": "free_form",
            "trigger": "Technician trigger",
            "content": "Technician content",
        }

    def _make_agent(self, *, branch_id, version_id, expected, operator_version, workflow_text):
        return {
            "agent_id": self.agent_id,
            "branch_id": branch_id,
            "main_branch_id": self.main_branch_id,
            "version_id": version_id,
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
                "__xi_procedure__operator_RAW/node": {"text": workflow_text},
                "__xi_procedure__technician_RAW/node": {"text": "same"},
            },
            "procedures": {
                self.operator_id: {
                    "name": "Operator breakdown",
                    "version_id": operator_version,
                },
                self.technician_id: {
                    "name": "Technician pre-close",
                    "version_id": "techv_RAW",
                },
            },
        }

    def _operator(self, expected, version_id):
        return {
            "procedure_id": self.operator_id,
            "version_id": version_id,
            **merge42.planner.materialize_operator(expected, self.tool_id),
        }

    def _main_agent(self):
        if not self.merged:
            return copy.deepcopy(self.main_agent_v1)
        agent = copy.deepcopy(self.source_agent)
        agent["branch_id"] = self.main_branch_id
        agent["main_branch_id"] = self.main_branch_id
        agent["version_id"] = self.new_main_version_id
        return agent

    def list_branches(self, agent_id, include_archived=False):
        source = {
            "id": self.source_branch_id,
            "name": merge42.BRANCH_NAME,
            "agent_id": self.agent_id,
            "description": merge42.staging42.BRANCH_DESCRIPTION,
            "current_live_percentage": 0,
            "parent_branch_id": self.main_branch_id,
            "draft_exists": False,
            "draft_created_at": None,
            "draft_is_behind_tip": False,
            "is_archived": self.merged,
            "commits_ahead": 2 if not self.merged else 0,
            "commits_behind": 0,
            "merged_into_branch_id": self.main_branch_id if self.merged else None,
        }
        main = {
            "id": self.main_branch_id,
            "name": "Main",
            "agent_id": self.agent_id,
            "description": "",
            "current_live_percentage": 100,
            "parent_branch_id": None,
            "draft_exists": False,
            "draft_created_at": None,
            "draft_is_behind_tip": False,
            "is_archived": False,
            "commits_ahead": 0,
            "commits_behind": 0,
            "merged_into_branch_id": None,
        }
        rows = [main]
        if include_archived or not source["is_archived"]:
            rows.append(source)
        return {"results": rows}

    def get_branch(self, agent_id, branch_id):
        if branch_id == self.source_branch_id:
            return {
                "id": self.source_branch_id,
                "name": merge42.BRANCH_NAME,
                "agent_id": self.agent_id,
                "description": merge42.staging42.BRANCH_DESCRIPTION,
                "created_at": 1,
                "last_committed_at": 2,
                "is_archived": self.merged,
                "current_live_percentage": 0,
                "parent_branch": {"id": self.main_branch_id, "name": "Main"},
                "most_recent_versions": [
                    {
                        "id": self.source_version_id,
                        "agent_id": self.agent_id,
                        "branch_id": self.source_branch_id,
                        "seq_no_in_branch": 2,
                    }
                ],
            }
        if branch_id == self.main_branch_id:
            return {
                "id": self.main_branch_id,
                "name": "Main",
                "agent_id": self.agent_id,
                "description": "",
                "created_at": 1,
                "last_committed_at": 3 if self.merged else 1,
                "is_archived": False,
                "current_live_percentage": 100,
                "parent_branch": None,
                "most_recent_versions": [
                    {
                        "id": self.new_main_version_id if self.merged else self.main_version_id,
                        "agent_id": self.agent_id,
                        "branch_id": self.main_branch_id,
                        "seq_no_in_branch": 3 if self.merged else 1,
                    }
                ],
            }
        raise AssertionError("unexpected branch")

    def get_agent(self, agent_id, branch_id=None):
        if branch_id == self.source_branch_id:
            return copy.deepcopy(self.source_agent)
        return self._main_agent()

    def get_procedure(self, agent_id, branch_id, procedure_id):
        if procedure_id == self.technician_id:
            return copy.deepcopy(self.technician)
        if procedure_id == self.operator_id:
            if branch_id == self.source_branch_id or self.merged:
                return self._operator(self.v2, "opv2_RAW")
            return self._operator(self.v1, "opv1_RAW")
        raise AssertionError("unexpected procedure")

    def get_tool(self, tool_id):
        return copy.deepcopy(self.tool)

    def get_merge_preview(self, agent_id, source_branch_id, target_branch_id):
        preview = copy.deepcopy(self.source_agent)
        preview["conflicts"] = copy.deepcopy(self.preview_conflicts)
        preview["overridden_fields"] = copy.deepcopy(self.preview_overrides)
        return preview

    def merge_once(self, agent_id, source_branch_id, target_branch_id):
        if self.merge_post_count != 0:
            raise merge42.Issue42MainMergeError("duplicate merge")
        if self.merged:
            raise merge42.Issue42MainMergeError("already merged")
        self.merge_post_count += 1
        self.merged = True
        return {}


class Issue42ProviderMainMergeV2Tests(unittest.TestCase):
    def setUp(self):
        self.v1 = load(V1_PATH)
        self.v2 = load(V2_PATH)
        self.tool = load(TOOL_PATH)

    def _main_live(self, fake):
        source_operator = merge42.staging42._fingerprint(
            {
                **merge42.planner.materialize_operator(self.v1, fake.tool_id),
                "version_id": "opv1_RAW",
            }
        )
        technician = merge42.staging42._fingerprint(fake.technician)
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
                "agent_id_sha256": merge42.planner.staging.safe_id_fingerprint(
                    fake.agent_id
                ),
                "main_branch_id_sha256": merge42.planner.staging.safe_id_fingerprint(
                    fake.main_branch_id
                ),
                "version_id_sha256": merge42.planner.staging.safe_id_fingerprint(
                    fake.main_version_id
                ),
                "system_prompt_sha256": "prompt_hash",
                "system_prompt_length": 6,
                "language": "es",
                "llm_id": "qwen35-397b-a17b",
                "dynamic_variable_names": list(
                    merge42.planner.BASELINE["dynamic_variable_names"]
                ),
                "voice_id_sha256": "voice_hash",
                "auth_enable_auth": False,
                "tool_id_sha256": merge42.planner.staging.safe_id_fingerprint(
                    fake.tool_id
                ),
                "tool_name": "bodyshop_resolve_confirmed_intake",
                "operator_procedure_id_sha256": merge42.planner.staging.safe_id_fingerprint(
                    fake.operator_id
                ),
                "technician_procedure_id_sha256": merge42.planner.staging.safe_id_fingerprint(
                    fake.technician_id
                ),
                "operator": source_operator,
                "technician": technician,
                "main_draft_exists": False,
            },
        }

    def test_execute_flag_is_required(self):
        out = ROOT / "never-created-issue42-main-merge.json"
        if out.exists():
            out.unlink()
        rc = merge42.main(
            [
                "--expected-v1",
                str(V1_PATH),
                "--expected-v2",
                str(V2_PATH),
                "--tool-config",
                str(TOOL_PATH),
                "--output",
                str(out),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(out.exists())

    def test_client_has_no_branch_create_or_patch_surface(self):
        client = merge42.Issue42MainMergeClient("x")
        with self.assertRaises(merge42.Issue42MainMergeError):
            client._request(
                "POST",
                "/v1/convai/agents/a/branches",
                body={},
            )
        with self.assertRaises(merge42.Issue42MainMergeError):
            client._request(
                "PATCH",
                "/v1/convai/agents/a",
                body={},
            )
        with self.assertRaises(merge42.Issue42MainMergeError):
            client._request(
                "DELETE",
                "/v1/convai/agents/a",
            )

    def test_merge_body_and_second_post_are_rejected_before_network(self):
        client = merge42.Issue42MainMergeClient("x")
        client.merge_post_count = 1
        with self.assertRaises(merge42.Issue42MainMergeError):
            client.merge_once("agent_x", "source_x", "main_x")

    def test_conflicted_preview_blocks_before_merge(self):
        fake = FakeMergeProvider(self.v1, self.v2, self.tool)
        fake.preview_conflicts = [{"field": "workflow"}]
        live = self._main_live(fake)

        with mock.patch.object(
            merge42.planner,
            "collect_live_main",
            return_value=copy.deepcopy(live),
        ):
            with self.assertRaises(merge42.staging42.Issue42StagingError):
                merge42.execute_authorized_main_merge(
                    fake,
                    self.v1,
                    self.v2,
                    self.tool,
                )
        self.assertEqual(0, fake.merge_post_count)
        self.assertFalse(fake.merged)

    def test_exact_merge_runs_once_archives_source_and_verifies_v2_main(self):
        fake = FakeMergeProvider(self.v1, self.v2, self.tool)
        live = self._main_live(fake)

        with mock.patch.object(
            merge42.planner,
            "collect_live_main",
            side_effect=[copy.deepcopy(live), copy.deepcopy(live)],
        ):
            evidence = merge42.execute_authorized_main_merge(
                fake,
                self.v1,
                self.v2,
                self.tool,
            )

        self.assertEqual(1, fake.merge_post_count)
        self.assertTrue(fake.merged)
        self.assertTrue(evidence["provider_main_merge_performed"])
        self.assertEqual(1, evidence["merge"]["post_count"])
        self.assertIs(evidence["merge"]["force"], False)
        self.assertIs(evidence["merge"]["archive_source_branch"], True)
        self.assertTrue(evidence["post_merge"]["main_matches_verified_source"])
        self.assertTrue(evidence["post_merge"]["source_archived"])
        self.assertTrue(evidence["post_merge"]["source_merged_into_main"])
        expected_target = merge42.staging42._target_operator_fingerprint(
            self.v2,
            fake.tool_id,
        )
        self.assertEqual(
            expected_target["content_sha256"],
            evidence["post_merge"]["operator"]["content_sha256"],
        )
        self.assertEqual(
            "c8238704959494ea15c8e7897cd4b18420b23b99a56a8ad4236662f1f180fae2",
            evidence["post_merge"]["technician"]["content_sha256"],
        )
        self.assertFalse(evidence["repository_ready_authorized"])
        self.assertFalse(evidence["repository_merge_authorized"])
        self.assertFalse(evidence["gate3_retry_authorized"])

        encoded = json.dumps(evidence)
        for raw in (
            fake.agent_id,
            fake.main_branch_id,
            fake.main_version_id,
            fake.new_main_version_id,
            fake.tool_id,
            fake.source_branch_id,
            fake.source_version_id,
            fake.operator_id,
            fake.technician_id,
        ):
            self.assertNotIn(raw, encoded)

    def test_second_execution_after_success_cannot_merge_again(self):
        fake = FakeMergeProvider(self.v1, self.v2, self.tool)
        live = self._main_live(fake)
        fake.merged = True

        # Exact Gate-2 Main precondition must fail in the real planner after
        # success. Model that failure directly and ensure merge is untouched.
        with mock.patch.object(
            merge42.planner,
            "collect_live_main",
            side_effect=merge42.planner.AlignmentError("Main version fingerprint moved"),
        ):
            with self.assertRaises(merge42.Issue42MainMergeError):
                merge42.execute_authorized_main_merge(
                    fake,
                    self.v1,
                    self.v2,
                    self.tool,
                )
        self.assertEqual(0, fake.merge_post_count)

    def test_post_merge_source_must_be_archived_into_exact_main(self):
        fake = FakeMergeProvider(self.v1, self.v2, self.tool)
        live = self._main_live(fake)

        original_list = fake.list_branches

        def bad_list(agent_id, include_archived=False):
            result = original_list(agent_id, include_archived)
            if fake.merged:
                for row in result["results"]:
                    if row["id"] == fake.source_branch_id:
                        row["merged_into_branch_id"] = "other_main"
            return result

        fake.list_branches = bad_list

        with mock.patch.object(
            merge42.planner,
            "collect_live_main",
            side_effect=[copy.deepcopy(live), copy.deepcopy(live)],
        ):
            with self.assertRaises(merge42.Issue42MainMergeError):
                merge42.execute_authorized_main_merge(
                    fake,
                    self.v1,
                    self.v2,
                    self.tool,
                )
        self.assertEqual(1, fake.merge_post_count)


if __name__ == "__main__":
    unittest.main()
