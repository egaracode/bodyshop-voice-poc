import importlib.util
import inspect
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOOL_PATH = TOOLS / "elevenlabs_client_tool_contract_v1.py"
CONFIG_PATH = ROOT / "elevenlabs" / "CONFIRMED_INTAKE_CLIENT_TOOL_V1.json"

spec = importlib.util.spec_from_file_location("client_tool_v1", TOOL_PATH)
v1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v1
spec.loader.exec_module(v1)


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


class FakeClient:
    def __init__(self, enable_auth=False, tool_ids=None):
        self.enable_auth = enable_auth
        self.tool_ids = [] if tool_ids is None else list(tool_ids)

    def list_agents(self, name, cursor=None):
        return {
            "agents": [{"agent_id": "agent_RAW_SECRET", "name": name}],
            "has_more": False,
        }

    def get_agent(self, agent_id):
        return {
            "agent_id": agent_id,
            "name": "AI Control",
            "branch_id": "branch_RAW_SECRET",
            "version_id": "version_RAW_SECRET",
            "main_branch_id": "main_RAW_SECRET",
            "platform_settings": {
                "auth": {
                    "enable_auth": self.enable_auth,
                    "allowlist": [{"hostname": "https://example.test"}],
                    "require_origin_header": True,
                }
            },
            "conversation_config": {
                "agent": {"prompt": {"tool_ids": self.tool_ids}}
            },
        }


class ClientToolContractV1Tests(unittest.TestCase):
    def valid_parameters(self):
        return {
            "workshop": "T01",
            "model": "A01",
            "installation": "LAT-IZQ",
            "operation": "OP100",
            "device": "Robot 01",
            "subdevice": "Control soldadura",
            "description": "No inicia ciclo.",
            "line_stopped": True,
        }

    def test_versioned_tool_payload_is_exact_and_waits_for_response(self):
        payload = load_config()
        v1.validate_tool_create_payload(payload)
        cfg = payload["tool_config"]
        self.assertEqual(v1.TOOL_NAME, cfg["name"])
        self.assertEqual("client", cfg["type"])
        self.assertIs(cfg["expects_response"], True)
        self.assertEqual(
            list(v1.REQUIRED_TOOL_FIELDS), cfg["parameters"]["required"]
        )
        self.assertEqual(
            v1.ALLOWED_TOOL_FIELDS, set(cfg["parameters"]["properties"])
        )

    def test_tool_input_maps_to_bodyshop_observation_with_client_owned_provenance(self):
        observation = v1.build_voice_observation(
            self.valid_parameters(),
            observation_id="obs-test-001",
            timestamp="2026-10-03T18:30:00Z",
        )
        self.assertEqual("ELEVENLABS_WEB", observation["source_channel"])
        self.assertEqual("obs-test-001", observation["observation_id"])
        self.assertEqual("2026-10-03T18:30:00Z", observation["confirmed_at"])
        self.assertIs(observation["line_stopped"], True)
        self.assertEqual("Control soldadura", observation["subdevice"])

    def test_optional_subdevice_omission_maps_to_null(self):
        params = self.valid_parameters()
        params.pop("subdevice")
        observation = v1.build_voice_observation(
            params, observation_id="obs-1", timestamp="2026-10-03T18:30:00Z"
        )
        self.assertIsNone(observation["subdevice"])

    def test_llm_cannot_supply_client_owned_provenance(self):
        params = self.valid_parameters()
        params["observation_id"] = "forged"
        with self.assertRaises(v1.ContractError):
            v1.build_voice_observation(
                params, observation_id="obs-1", timestamp="2026-10-03T18:30:00Z"
            )

    def test_missing_required_field_fails_closed(self):
        params = self.valid_parameters()
        params.pop("operation")
        with self.assertRaises(v1.ContractError):
            v1.build_voice_observation(
                params, observation_id="obs-1", timestamp="2026-10-03T18:30:00Z"
            )

    def test_line_stopped_must_be_real_boolean(self):
        params = self.valid_parameters()
        params["line_stopped"] = "true"
        with self.assertRaises(v1.ContractError):
            v1.build_voice_observation(
                params, observation_id="obs-1", timestamp="2026-10-03T18:30:00Z"
            )

    def test_resolved_result_is_projected_without_reference_path_or_internal_ids(self):
        result = {
            "status": "RESOLVED",
            "reference_path_id": "canonical-secret-id",
            "canonical_context": {
                "workshop": {"id": "w1", "code": "T01", "name": "Taller 1"},
                "model": {"id": "m1", "code": "A01", "name": "Modelo A01"},
                "installation": {"id": "i1", "code": "LAT-IZQ", "name": "Lateral Izq"},
                "operation": {"id": "o1", "code": "OP100", "name": "Soldadura", "family": "WELDING"},
                "device": {"id": "d1", "name": "Robot 01", "asset_code": "R01", "device_type": "WELDING_ROBOT"},
                "subdevice": {"id": "s1", "name": "Control soldadura", "asset_code": "CS1", "device_type": "BOSCH_REXROTH_CONTROL"},
            },
        }
        safe = v1.to_agent_safe_result(result)
        encoded = json.dumps(safe, ensure_ascii=False)
        self.assertEqual("RESOLVED", safe["status"])
        self.assertNotIn("canonical-secret-id", encoded)
        self.assertNotIn('"id"', encoded)
        self.assertEqual("OP100", safe["canonical_context"]["operation"]["code"])

    def test_fail_closed_result_preserves_only_bounded_clarification(self):
        safe = v1.to_agent_safe_result(
            {
                "status": "INCOMPLETE",
                "reason": "MISSING_REQUIRED_FIELDS",
                "missing_fields": ["subdevice"],
                "candidate_count": 2,
                "reference_path_id": "must-not-pass",
            }
        )
        self.assertEqual(
            {
                "status": "INCOMPLETE",
                "reason": "MISSING_REQUIRED_FIELDS",
                "missing_fields": ["subdevice"],
                "candidate_count": 2,
            },
            safe,
        )

    def test_unknown_result_status_fails_closed(self):
        with self.assertRaises(v1.ContractError):
            v1.to_agent_safe_result({"status": "MAYBE"})

    def test_public_agent_classification(self):
        snapshot = v1.collect_agent_access_snapshot(FakeClient(enable_auth=False), "AI Control")
        self.assertEqual(
            "PUBLIC_AGENT_ID_ALLOWED",
            snapshot["safe"]["connection_classification"],
        )

    def test_private_agent_classification(self):
        snapshot = v1.collect_agent_access_snapshot(FakeClient(enable_auth=True), "AI Control")
        self.assertEqual(
            "SIGNED_URL_REQUIRED",
            snapshot["safe"]["connection_classification"],
        )

    def test_write_set_is_sanitized_and_stops_at_expected_state_decision(self):
        snapshot = v1.collect_agent_access_snapshot(
            FakeClient(enable_auth=False, tool_ids=["tool_EXISTING_RAW"]), "AI Control"
        )
        plan = v1.build_sanitized_write_set(snapshot, load_config())
        encoded = json.dumps(plan, ensure_ascii=False)
        for forbidden in (
            "agent_RAW_SECRET",
            "branch_RAW_SECRET",
            "version_RAW_SECRET",
            "main_RAW_SECRET",
            "tool_EXISTING_RAW",
        ):
            self.assertNotIn(forbidden, encoded)
        self.assertIs(plan["operator_contract_gap"]["gate1_requires_workshop_context"], True)
        self.assertIs(
            plan["operator_contract_gap"]["current_a5_expected_operator_procedure_collects_workshop"],
            False,
        )
        self.assertEqual(
            "EXPECTED_STATE_DECISION_REQUIRED",
            plan["operator_contract_gap"]["classification"],
        )
        self.assertEqual(
            "STOP_FOR_EXPECTED_STATE_AND_PROVIDER_WRITE_DECISIONS",
            plan["next_gate"],
        )
        self.assertEqual(
            ["POST", "GET", "POST", "GET", "PATCH", "BLOCKED_DECISION"],
            [op["method"] for op in plan["planned_provider_operations"]],
        )

    def test_api_client_is_get_only(self):
        methods = {
            name
            for name, value in inspect.getmembers(v1.ApiClient, inspect.isfunction)
            if not name.startswith("__")
        }
        self.assertEqual({"_get", "list_agents", "get_agent"}, methods)
        source = inspect.getsource(v1.ApiClient._get)
        self.assertIn('method="GET"', source)
        for forbidden in ('method="POST"', 'method="PATCH"', 'method="PUT"', 'method="DELETE"'):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
