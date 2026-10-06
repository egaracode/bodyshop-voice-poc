import importlib.util
import inspect
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MODULE_PATH = TOOLS / "elevenlabs_issue42_workshop_installation_alignment_v2.py"
V1_PATH = ROOT / "elevenlabs" / "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json"
V2_PATH = ROOT / "elevenlabs" / "GATE3_WORKSHOP_INSTALLATION_EXPECTED_PROVIDER_CONFIGURATION_V2.json"
TOOL_CONFIG_PATH = ROOT / "elevenlabs" / "CONFIRMED_INTAKE_CLIENT_TOOL_V1.json"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location("issue42_alignment_v2", MODULE_PATH)
v2mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v2mod
spec.loader.exec_module(v2mod)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class Issue42WorkshopInstallationAlignmentV2Tests(unittest.TestCase):
    def setUp(self):
        self.v1 = load(V1_PATH)
        self.v2 = load(V2_PATH)
        self.tool = load(TOOL_CONFIG_PATH)

    def test_v2_is_versioned_successor_not_historical_rewrite(self):
        delta = v2mod.validate_expected_delta(self.v1, self.v2)
        self.assertEqual(2, self.v2["schema_version"])
        self.assertEqual(
            "GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1",
            self.v2["authority"]["extends_without_rewriting"],
        )
        self.assertEqual(42, self.v2["authority"]["issue"])
        self.assertEqual([1, 3], delta["changed_step_indexes"])

    def test_only_workshop_and_installation_ask_steps_change(self):
        old_steps = self.v1["operator_procedure"]["content_template"]["steps"]
        new_steps = self.v2["operator_procedure"]["content_template"]["steps"]
        self.assertEqual(len(old_steps), len(new_steps))

        changed = [
            i
            for i, (old, new) in enumerate(zip(old_steps, new_steps))
            if v2mod.staging.canonical_json(old)
            != v2mod.staging.canonical_json(new)
        ]
        self.assertEqual([1, 3], changed)

        for i, (old, new) in enumerate(zip(old_steps, new_steps)):
            if i not in (1, 3):
                self.assertEqual(old, new)

    def test_workshop_ask_has_clear_semantic_and_exit_boundary(self):
        instruction = self.v2["operator_procedure"]["content_template"]["steps"][1][
            "instruction"
        ]
        self.assertIn("¿De qué taller BODYSHOP llamas?", instruction)
        self.assertIn("not the installation", instruction)
        self.assertIn("does not satisfy this step", instruction)
        self.assertIn("Do not advance", instruction)

    def test_installation_ask_is_separate_after_workshop(self):
        instruction = self.v2["operator_procedure"]["content_template"]["steps"][3][
            "instruction"
        ]
        self.assertIn("¿Qué instalación?", instruction)
        self.assertIn("distinct from workshop/Taller", instruction)
        self.assertIn("Do not reuse", instruction)
        self.assertIn("Do not advance", instruction)

    def test_v2_does_not_duplicate_canonical_catalog_values(self):
        encoded = json.dumps(self.v2, ensure_ascii=False, sort_keys=True)
        for forbidden in (
            "Taller 1",
            "Taller 2",
            "Taller 3",
            "Autobastidor",
            "Mascarón",
            "LAT-IZQ",
            '"T01"',
            '"AUT"',
        ):
            self.assertNotIn(forbidden, encoded)

    def test_client_tool_contract_reference_is_unchanged(self):
        self.assertEqual(self.v1["client_tool"], self.v2["client_tool"])
        params = self.tool["tool_config"]["parameters"]
        self.assertIn("workshop", params["required"])
        self.assertIn("installation", params["required"])
        self.assertNotEqual(
            params["properties"]["workshop"]["description"],
            params["properties"]["installation"]["description"],
        )

    def test_readback_and_tool_call_still_require_both_fields(self):
        steps = self.v2["operator_procedure"]["content_template"]["steps"]
        readback = steps[8]["instruction"]
        tool_call = steps[9]["instruction"]
        self.assertIn("workshop, model, installation", readback)
        self.assertIn("workshop, model, installation", tool_call)
        self.assertEqual("tool_call", steps[9]["type"])
        self.assertEqual(
            "bodyshop_resolve_confirmed_intake",
            steps[9]["tool_ref"],
        )

    def test_network_client_exposes_get_only(self):
        methods = {
            name
            for name, value in inspect.getmembers(
                v2mod.ReadOnlyProviderClient, inspect.isfunction
            )
            if not name.startswith("__")
        }
        self.assertEqual(
            {
                "_get",
                "list_agents",
                "get_agent",
                "list_branches",
                "get_procedure",
                "get_tool",
            },
            methods,
        )
        self.assertNotIn("post", methods)
        self.assertNotIn("patch", methods)
        self.assertNotIn("put", methods)
        self.assertNotIn("delete", methods)

    def test_sanitized_plan_has_no_raw_provider_ids_and_no_write_authorization(self):
        tool_id = "tool_RAW_SECRET"
        source_item = {
            **v2mod.materialize_operator(self.v1, tool_id),
            "version_id": "expected",
        }
        source_fp = v2mod.staging.semantic_procedure_fingerprint(source_item)
        source_fp["version_present"] = True

        live = {
            "raw": {
                "agent_id": "agent_RAW_SECRET",
                "main_branch_id": "main_RAW_SECRET",
                "version_id": "version_RAW_SECRET",
                "tool_id": tool_id,
                "operator_procedure_id": "operator_RAW_SECRET",
                "technician_procedure_id": "technician_RAW_SECRET",
            },
            "safe": {
                "agent_id_sha256": "agent_hash",
                "main_branch_id_sha256": "main_hash",
                "version_id_sha256": "version_hash",
                "system_prompt_sha256": "prompt_hash",
                "system_prompt_length": 2305,
                "language": "es",
                "llm_id": "qwen35-397b-a17b",
                "dynamic_variable_names": list(v2mod.BASELINE["dynamic_variable_names"]),
                "voice_id_sha256": "voice_hash",
                "auth_enable_auth": False,
                "tool_id_sha256": "tool_hash",
                "tool_name": "bodyshop_resolve_confirmed_intake",
                "operator_procedure_id_sha256": "op_hash",
                "technician_procedure_id_sha256": "tech_hash",
                "operator": source_fp,
                "technician": dict(v2mod.BASELINE["technician"]),
                "main_draft_exists": False,
            },
        }

        plan = v2mod.build_sanitized_plan(live, self.v1, self.v2)
        encoded = json.dumps(plan, ensure_ascii=False)

        for raw in live["raw"].values():
            self.assertNotIn(raw, encoded)

        self.assertFalse(plan["provider_write_performed"])
        self.assertFalse(plan["diagnosis"]["canonical_domain_change_required"])
        self.assertFalse(plan["diagnosis"]["client_tool_contract_change_required"])
        self.assertEqual(
            "STOP_FOR_ALBERT_PROVIDER_WRITE_SET_AUTHORIZATION",
            plan["next_gate"],
        )

        operations = plan["planned_provider_operations"]
        self.assertEqual(
            ["POST", "GET", "PATCH", "PATCH", "GET", "GET", "BLOCKED_DECISION"],
            [op["method"] for op in operations],
        )
        for op in operations:
            if op["method"] in {"POST", "PATCH", "BLOCKED_DECISION"}:
                self.assertIs(op["authorized_now"], False)

    def test_target_changes_operator_content_but_not_trigger_or_identity(self):
        tool_id = "tool_RAW_SECRET"
        source = v2mod.staging.semantic_procedure_fingerprint(
            {**v2mod.materialize_operator(self.v1, tool_id), "version_id": "expected"}
        )
        target = v2mod.staging.semantic_procedure_fingerprint(
            {**v2mod.materialize_operator(self.v2, tool_id), "version_id": "expected"}
        )
        self.assertEqual(source["name"], target["name"])
        self.assertEqual(source["raw_api_type"], target["raw_api_type"])
        self.assertEqual(source["trigger_sha256"], target["trigger_sha256"])
        self.assertNotEqual(source["content_sha256"], target["content_sha256"])

    def test_cli_has_no_provider_write_flag(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("--execute", source)
        self.assertNotIn("execute_provider", source)
        self.assertIn("provider_write_performed", source)


if __name__ == "__main__":
    unittest.main()
