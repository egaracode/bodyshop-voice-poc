import importlib.util
import inspect
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "compat_v2", ROOT / "tools" / "elevenlabs_provider_compat_v2.py"
)
v2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v2
spec.loader.exec_module(v2)


class FakeClient:
    def __init__(self, procedure_type="deterministic", duplicate=False, branch=True):
        self.procedure_type = procedure_type
        self.duplicate = duplicate
        self.branch = branch

    def list_agents(self, name, cursor=None):
        return {
            "agents": [
                {
                    "agent_id": "agent_SECRET_RAW_ID",
                    "name": name,
                    "archived": False,
                }
            ],
            "has_more": False,
        }

    def get_agent(self, agent_id):
        return {
            "agent_id": agent_id,
            "name": "AI Control",
            "branch_id": "branch_SECRET_RAW_ID" if self.branch else None,
            "main_branch_id": "mainbranch_SECRET_RAW_ID",
            "version_id": "version_SECRET_RAW_ID",
            "conversation_config": {
                "agent": {
                    "language": "es",
                    "first_message": "RAW FIRST MESSAGE",
                    "prompt": {
                        "prompt": "RAW SYSTEM PROMPT",
                        "llm": "qwen35-397b-a17b",
                    },
                    "dynamic_variables": {
                        "dynamic_variable_placeholders": {
                            "channel_mode": {},
                            "flow_stage": {},
                        }
                    },
                },
                "tts": {
                    "voice_id": "voice_SECRET_RAW_ID",
                    "model_id": "tts-model",
                    "stability": 0.5,
                    "speed": 1.0,
                    "similarity_boost": 0.8,
                },
            },
        }

    def list_branches(self, agent_id):
        return {
            "results": [
                {
                    "id": "branch_SECRET_RAW_ID",
                    "name": "main",
                    "is_archived": False,
                    "draft_exists": False,
                    "commits_ahead": 0,
                    "commits_behind": 0,
                    "parent_branch_id": None,
                }
            ]
        }

    def list_procedures(self, agent_id, branch_id, version_id):
        procedures = [
            {
                "procedure_id": "procedure_SECRET_RAW_ID",
                "name": "Operator breakdown",
                "type": self.procedure_type,
                "trigger": "RAW TRIGGER",
                "has_draft": False,
                "version_id": "procedure_version_SECRET_RAW_ID",
            }
        ]
        if self.duplicate:
            procedures.append(
                {
                    "procedure_id": "procedure_SECRET_RAW_ID_2",
                    "name": "Operator breakdown",
                    "type": self.procedure_type,
                    "trigger": "RAW TRIGGER TWO",
                    "has_draft": False,
                    "version_id": "procedure_version_SECRET_RAW_ID_2",
                }
            )
        return {"procedures": procedures}

    def get_procedure(self, agent_id, branch_id, procedure_id, version_id):
        return {
            "procedure_id": procedure_id,
            "name": "Operator breakdown",
            "type": self.procedure_type,
            "trigger": "RAW TRIGGER",
            "content": json.dumps(
                {
                    "steps": [
                        {
                            "type": "ask",
                            "instruction": "RAW PROCEDURE CONTENT",
                        }
                    ]
                }
            ),
            "version_id": "procedure_version_SECRET_RAW_ID",
        }

    def get_voice(self, voice_id):
        return {"name": "Eric - Smooth, Trustworthy"}


class CompatibilityProbeV2Tests(unittest.TestCase):
    def test_current_procedure_types_are_exactly_documented_values(self):
        self.assertEqual(
            {"free_form", "deterministic", "folder"},
            v2.CURRENT_PROCEDURE_TYPES,
        )

    def test_deterministic_raw_type_is_preserved_and_json_shape_detected(self):
        snapshot = v2.collect_provider_snapshot(FakeClient(), "AI Control")
        procedure = snapshot["procedures"][0]
        self.assertEqual("deterministic", procedure["raw_api_type"])
        self.assertEqual("JSON_STEPS", procedure["content_shape"])
        self.assertEqual([], procedure["warnings"])
        self.assertEqual(
            "NOT_EMITTED_BY_V2_COMPATIBILITY_PROBE",
            snapshot["probe"]["drift_verdict"],
        )

    def test_probe_does_not_emit_raw_ids_or_raw_prompt_content(self):
        encoded = json.dumps(
            v2.collect_provider_snapshot(FakeClient(), "AI Control"),
            ensure_ascii=False,
        )
        for forbidden in (
            "agent_SECRET_RAW_ID",
            "branch_SECRET_RAW_ID",
            "mainbranch_SECRET_RAW_ID",
            "version_SECRET_RAW_ID",
            "voice_SECRET_RAW_ID",
            "procedure_SECRET_RAW_ID",
            "RAW FIRST MESSAGE",
            "RAW SYSTEM PROMPT",
            "RAW TRIGGER",
            "RAW PROCEDURE CONTENT",
        ):
            self.assertNotIn(forbidden, encoded)
        self.assertIn("sha256", encoded)

    def test_unknown_provider_type_fails_closed(self):
        with self.assertRaises(v2.ProbeError):
            v2.collect_provider_snapshot(FakeClient(procedure_type="structured"), "AI Control")

    def test_duplicate_procedure_names_fail_closed(self):
        with self.assertRaises(v2.ProbeError):
            v2.collect_provider_snapshot(FakeClient(duplicate=True), "AI Control")

    def test_missing_current_branch_fails_closed(self):
        with self.assertRaises(v2.ProbeError):
            v2.collect_provider_snapshot(FakeClient(branch=False), "AI Control")

    def test_content_shape_keeps_text_separate_from_json_steps(self):
        shape, canonical = v2.content_shape("plain text")
        self.assertEqual("TEXT", shape)
        self.assertEqual("plain text", canonical)

        shape, canonical = v2.content_shape('{"foo": []}')
        self.assertEqual("INVALID_JSON_STEPS", shape)
        self.assertEqual('{"foo":[]}', canonical)

        shape, canonical = v2.content_shape("")
        self.assertEqual("EMPTY", shape)
        self.assertEqual("", canonical)

    def test_api_client_exposes_no_mutation_method(self):
        method_names = {
            name
            for name, value in inspect.getmembers(v2.ApiClient, inspect.isfunction)
            if not name.startswith("__")
        }
        self.assertEqual(
            {
                "_get",
                "list_agents",
                "get_agent",
                "list_branches",
                "list_procedures",
                "get_procedure",
                "get_voice",
            },
            method_names,
        )
        source = inspect.getsource(v2.ApiClient._get)
        self.assertIn('method="GET"', source)
        for forbidden in ('method="POST"', 'method="PATCH"', 'method="PUT"', 'method="DELETE"'):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
