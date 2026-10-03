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
    "issue38_staging", TOOLS / "elevenlabs_client_tool_staging_v1.py"
)
staging = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = staging
spec.loader.exec_module(staging)

EXPECTED_PATH = (
    ROOT / "elevenlabs" / "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json"
)
TOOL_PATH = ROOT / "elevenlabs" / "CONFIRMED_INTAKE_CLIENT_TOOL_V1.json"
A5_PATH = ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.expected = load_json(EXPECTED_PATH)
        self.tool_payload = load_json(TOOL_PATH)
        self.a5 = load_json(A5_PATH)
        self.agent_id = "agent_RAW"
        self.main_id = "main_RAW"
        self.main_version = "version_RAW"
        self.voice_id = "voice_RAW"
        self.operator_id = "op_RAW"
        self.tech_id = "tech_RAW"
        self.tool_id = "tool_RAW"
        self.isolated_id = "isolated_RAW"
        self.isolated_created = False
        self.tool_created = False
        self.operator_draft = None
        self.isolated_published = False
        self.isolated_tool_ids = []
        self.isolated_version = "isolated_v0_RAW"

        by_name = {p["name"]: p for p in self.a5["procedures"]}
        op = by_name["Operator breakdown"]
        tech = by_name["Technician pre-close"]
        self.main_operator = {
            "procedure_id": self.operator_id,
            "version_id": "opv_RAW",
            "name": "Operator breakdown",
            "type": "deterministic",
            "trigger": op["trigger"],
            "content": staging.canonical_json(op["content"]),
        }
        self.main_tech = {
            "procedure_id": self.tech_id,
            "version_id": "techv_RAW",
            "name": "Technician pre-close",
            "type": "free_form",
            "trigger": tech["trigger"],
            "content": tech["content"],
        }

    def _config(self, tool_ids):
        return {
            "agent": {
                "language": "es",
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {
                        name: ""
                        for name in staging.BASELINE["dynamic_variable_names"]
                    }
                },
                "prompt": {
                    "prompt": self.a5["agent"]["system_prompt"],
                    "llm": "qwen35-397b-a17b",
                    "tool_ids": list(tool_ids),
                },
            },
            "tts": {"voice_id": self.voice_id},
        }

    def _procedures_map(self):
        return {
            self.operator_id: {
                "procedure_id": self.operator_id,
                "version_id": "opv2_RAW" if self.isolated_published else "opv_RAW",
                "name": "Operator breakdown",
                "type": "deterministic",
            },
            self.tech_id: {
                "procedure_id": self.tech_id,
                "version_id": "techv_RAW",
                "name": "Technician pre-close",
                "type": "free_form",
            },
        }

    def list_agents(self, name, cursor=None):
        self.calls.append(("GET_LIST_AGENTS", name))
        return {
            "agents": [{"agent_id": self.agent_id, "name": "AI Control", "archived": False}],
            "has_more": False,
        }

    def get_agent(self, agent_id, branch_id=None):
        self.calls.append(("GET_AGENT", branch_id))
        if branch_id is None:
            return {
                "agent_id": self.agent_id,
                "name": "AI Control",
                "branch_id": self.main_id,
                "main_branch_id": self.main_id,
                "version_id": self.main_version,
                "conversation_config": self._config([]),
                "platform_settings": {
                    "auth": {
                        "enable_auth": False,
                        "allowlist": [],
                        "require_origin_header": False,
                    }
                },
                "procedures": {
                    self.operator_id: {
                        "procedure_id": self.operator_id,
                        "version_id": "opv_RAW",
                        "name": "Operator breakdown",
                        "type": "deterministic",
                    },
                    self.tech_id: {
                        "procedure_id": self.tech_id,
                        "version_id": "techv_RAW",
                        "name": "Technician pre-close",
                        "type": "free_form",
                    },
                },
            }
        if branch_id != self.isolated_id:
            raise AssertionError(branch_id)
        return {
            "agent_id": self.agent_id,
            "name": "AI Control",
            "branch_id": self.isolated_id,
            "main_branch_id": self.main_id,
            "version_id": self.isolated_version,
            "conversation_config": self._config(self.isolated_tool_ids),
            "platform_settings": {
                "auth": {
                    "enable_auth": False,
                    "allowlist": [],
                    "require_origin_header": False,
                }
            },
            "procedures": self._procedures_map(),
        }

    def list_branches(self, agent_id, include_archived=False):
        self.calls.append(("GET_BRANCHES", include_archived))
        values = [
            {
                "id": self.main_id,
                "name": "Main",
                "is_archived": False,
                "draft_exists": False,
                "commits_ahead": 0,
                "commits_behind": 0,
            }
        ]
        if self.isolated_created:
            values.append(
                {
                    "id": self.isolated_id,
                    "name": staging.STAGING_BRANCH_NAME,
                    "description": staging.STAGING_DESCRIPTION,
                    "is_archived": False,
                    "draft_exists": bool(self.operator_draft and not self.isolated_published),
                    "current_live_percentage": 0,
                    "parent_branch_id": self.main_id,
                }
            )
        return {"results": values}

    def get_branch(self, agent_id, branch_id):
        self.calls.append(("GET_BRANCH", branch_id))
        if branch_id != self.isolated_id or not self.isolated_created:
            raise AssertionError(branch_id)
        return {
            "id": self.isolated_id,
            "name": staging.STAGING_BRANCH_NAME,
            "description": staging.STAGING_DESCRIPTION,
            "is_archived": False,
            "draft_exists": bool(self.operator_draft and not self.isolated_published),
            "current_live_percentage": 0,
            "parent_branch": {"id": self.main_id, "name": "Main"},
        }

    def get_procedure(self, agent_id, branch_id, procedure_id):
        self.calls.append(("GET_PROCEDURE", branch_id, procedure_id))
        if procedure_id == self.tech_id:
            return copy.deepcopy(self.main_tech)
        if procedure_id != self.operator_id:
            raise AssertionError(procedure_id)
        if branch_id == self.isolated_id and self.isolated_published:
            result = copy.deepcopy(self.operator_draft)
            result.update(
                {
                    "procedure_id": self.operator_id,
                    "version_id": "opv2_RAW",
                }
            )
            return result
        return copy.deepcopy(self.main_operator)

    def list_tools(self, search, cursor=None):
        self.calls.append(("GET_TOOLS", search))
        if not self.tool_created:
            return {"tools": [], "has_more": False}
        return {
            "tools": [{"id": self.tool_id, "tool_config": self.tool_payload["tool_config"]}],
            "has_more": False,
        }

    def get_tool(self, tool_id):
        self.calls.append(("GET_TOOL", tool_id))
        if tool_id != self.tool_id or not self.tool_created:
            raise AssertionError(tool_id)
        return {"id": self.tool_id, "tool_config": copy.deepcopy(self.tool_payload["tool_config"])}

    def post(self, path, body):
        self.calls.append(("POST", path, copy.deepcopy(body)))
        if path.endswith("/branches"):
            self.isolated_created = True
            self.isolated_version = "isolated_v0_RAW"
            return {
                "created_branch_id": self.isolated_id,
                "created_version_id": self.isolated_version,
            }
        if path == "/v1/convai/tools":
            self.tool_created = True
            return {
                "id": self.tool_id,
                "tool_config": copy.deepcopy(self.tool_payload["tool_config"]),
            }
        raise AssertionError(path)

    def patch(self, path, body, query=None):
        self.calls.append(("PATCH", path, copy.deepcopy(body), copy.deepcopy(query)))
        if path.endswith(f"/procedures/{self.operator_id}/draft"):
            self.operator_draft = copy.deepcopy(body)
            return {
                "procedure_id": self.operator_id,
                **copy.deepcopy(body),
            }
        if path.endswith(f"/agents/{self.agent_id}"):
            if query != {"branch_id": self.isolated_id}:
                raise AssertionError(query)
            self.isolated_tool_ids = list(
                body["conversation_config"]["agent"]["prompt"]["tool_ids"]
            )
            self.isolated_published = True
            self.isolated_version = "isolated_final_RAW"
            return {"version_id": self.isolated_version}
        raise AssertionError(path)


class Issue38StagingTests(unittest.TestCase):
    def patched_baseline(self, fake):
        op_fp = staging.semantic_procedure_fingerprint(fake.main_operator)
        tech_fp = staging.semantic_procedure_fingerprint(fake.main_tech)
        return mock.patch.object(
            staging,
            "BASELINE",
            {
                **staging.BASELINE,
                "agent_id_sha256": staging.sha256_text(fake.agent_id),
                "main_branch_id_sha256": staging.sha256_text(fake.main_id),
                "version_id_sha256": staging.sha256_text(fake.main_version),
                "voice_id_sha256": staging.sha256_text(fake.voice_id),
                "operator": {k: v for k, v in op_fp.items() if k != "version_present"},
                "technician": {k: v for k, v in tech_fp.items() if k != "version_present"},
            },
        )

    def test_expected_state_extends_a5_without_rewriting_it(self):
        expected = load_json(EXPECTED_PATH)
        staging.validate_expected_state(expected)
        self.assertEqual(
            "A5_EXPECTED_PROVIDER_CONFIGURATION_V1",
            expected["authority"]["extends_without_rewriting"],
        )
        self.assertIn("agent.system_prompt", expected["retained_from_a5"])
        self.assertEqual(
            "EVIDENCE_REQUIRED_IN_GATE_3",
            expected["runtime_risk"]["forced_tool_behavior"],
        )

    def test_materialized_operator_contains_required_gate1_sequence_and_one_tool(self):
        expected = load_json(EXPECTED_PATH)
        materialized = staging.materialize_operator(expected, "tool_RAW")
        content = json.loads(materialized["content"])
        encoded = json.dumps(content, ensure_ascii=False).lower()
        self.assertIn("workshop", encoded)
        self.assertIn("línea está parada", encoded)
        self.assertIn("¿es correcto?", encoded)
        tool_calls = [s for s in content["steps"] if s.get("type") == "tool_call"]
        self.assertEqual(1, len(tool_calls))
        self.assertEqual("tool_RAW", tool_calls[0]["tool_id"])
        self.assertEqual(staging.TOOL_NAME, tool_calls[0]["tool_name"])
        self.assertNotIn("tool_ref", tool_calls[0])

    def test_provider_client_rejects_delete_and_put(self):
        client = staging.ProviderClient("x")
        with self.assertRaises(staging.StagingError):
            client._request("DELETE", "/x")
        with self.assertRaises(staging.StagingError):
            client._request("PUT", "/x")

    def test_main_guard_rejects_attached_tool(self):
        fake = FakeProvider()
        original_get = fake.get_agent

        def moved(agent_id, branch_id=None):
            value = original_get(agent_id, branch_id)
            if branch_id is None:
                value["conversation_config"]["agent"]["prompt"]["tool_ids"] = ["unexpected"]
            return value

        fake.get_agent = moved
        with self.patched_baseline(fake):
            with self.assertRaises(staging.StagingError):
                staging.assert_main_baseline(fake)

    def test_existing_branch_name_fails_closed(self):
        fake = FakeProvider()
        fake.isolated_created = True
        with self.assertRaises(staging.StagingError):
            staging.ensure_branch_name_available(fake, fake.agent_id)

    def test_existing_workspace_tool_name_fails_closed(self):
        fake = FakeProvider()
        fake.tool_created = True
        with self.assertRaises(staging.StagingError):
            staging.ensure_tool_name_available(fake)

    def test_full_isolated_staging_sequence_is_verified_and_sanitized(self):
        fake = FakeProvider()
        expected = load_json(EXPECTED_PATH)
        payload = load_json(TOOL_PATH)

        with self.patched_baseline(fake):
            evidence = staging.execute_isolated_staging(fake, expected, payload)

        self.assertTrue(fake.isolated_created)
        self.assertTrue(fake.tool_created)
        self.assertTrue(fake.isolated_published)
        self.assertEqual([fake.tool_id], fake.isolated_tool_ids)

        methods_paths = [
            (call[0], call[1])
            for call in fake.calls
            if call[0] in {"POST", "PATCH"}
        ]
        self.assertEqual(
            [
                ("POST", f"/v1/convai/agents/{fake.agent_id}/branches"),
                ("POST", "/v1/convai/tools"),
                (
                    "PATCH",
                    f"/v1/convai/agents/{fake.agent_id}/branches/{fake.isolated_id}/procedures/{fake.operator_id}/draft",
                ),
                ("PATCH", f"/v1/convai/agents/{fake.agent_id}"),
            ],
            methods_paths,
        )

        encoded = json.dumps(evidence, ensure_ascii=False)
        for raw in (
            fake.agent_id,
            fake.main_id,
            fake.main_version,
            fake.voice_id,
            fake.operator_id,
            fake.tech_id,
            fake.tool_id,
            fake.isolated_id,
            "isolated_final_RAW",
        ):
            self.assertNotIn(raw, encoded)

        self.assertFalse(evidence["provider_main_agent_modified"])
        self.assertTrue(evidence["workspace_tool_created"])
        self.assertFalse(evidence["provider_main_merge_performed"])
        self.assertEqual(
            "REPOSITORY_READY_DECISION_AND_SEPARATE_PROVIDER_MAIN_MERGE_DECISION_REQUIRED",
            evidence["next_gate"],
        )

    def test_main_is_rechecked_after_staging(self):
        source = (TOOLS / "elevenlabs_client_tool_staging_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertGreaterEqual(source.count("assert_main_baseline(client)"), 2)

    def test_source_contains_no_provider_merge_endpoint(self):
        source = (TOOLS / "elevenlabs_client_tool_staging_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("/merge", source)
        self.assertNotIn("archive_source_branch", source)
        self.assertNotIn("target_branch_id", source)

    def test_execution_flag_is_fail_closed(self):
        output = ROOT / "never-created-issue38.json"
        if output.exists():
            output.unlink()
        rc = staging.main(
            [
                "--expected",
                str(EXPECTED_PATH),
                "--tool-config",
                str(TOOL_PATH),
                "--output",
                str(output),
            ]
        )
        self.assertEqual(2, rc)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
