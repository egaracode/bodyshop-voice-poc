import importlib.util
import inspect
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "reconcile_v1", TOOLS / "elevenlabs_provider_reconciliation_v1.py"
)
v1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v1
spec.loader.exec_module(v1)

EXPECTED_PATH = ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"


def load_expected():
    with EXPECTED_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


class FakeVoiceClient:
    def __init__(self, voice_id="voice_EXPECTED_RAW", duplicate_name=False):
        self.voice_id = voice_id
        self.duplicate_name = duplicate_name

    def search_voices(self, search, next_page_token=None):
        voices = [{"voice_id": self.voice_id, "name": v1.TARGET_VOICE_NAME}]
        if self.duplicate_name:
            voices.append(
                {"voice_id": "voice_OTHER_RAW", "name": v1.TARGET_VOICE_NAME}
            )
        return {"voices": voices, "has_more": False, "next_page_token": None}

    def get_voice(self, voice_id):
        return {"voice_id": voice_id, "name": v1.TARGET_VOICE_NAME}


class FakeBranchClient:
    def __init__(self, names):
        self.names = names

    def list_branches(self, agent_id):
        return {"results": [{"name": name} for name in self.names]}


class ReconciliationPlannerV1Tests(unittest.TestCase):
    def test_a5_target_maps_historical_structured_to_current_deterministic(self):
        target = v1.derive_expected_target(load_expected())
        self.assertEqual(v1.EXPECTED_A5_TARGET_FINGERPRINTS_V1, target)
        self.assertEqual(
            "deterministic",
            target["procedures"]["Operator breakdown"]["target_api_type"],
        )
        self.assertEqual(
            "free_form",
            target["procedures"]["Technician pre-close"]["target_api_type"],
        )

    def test_exact_classified_provider_guard_passes(self):
        v1.assert_current_provider_guard(
            json.loads(json.dumps(v1.CURRENT_PROVIDER_GUARD_V1))
        )

    def test_stale_provider_guard_fails_closed(self):
        moved = json.loads(json.dumps(v1.CURRENT_PROVIDER_GUARD_V1))
        moved["agent"]["system_prompt_sha256"] = "0" * 64
        with self.assertRaises(v1.PlannerError):
            v1.assert_current_provider_guard(moved)

    def test_provider_draft_guard_fails_closed(self):
        moved = json.loads(json.dumps(v1.CURRENT_PROVIDER_GUARD_V1))
        moved["branch"]["draft_exists"] = True
        with self.assertRaises(v1.PlannerError):
            v1.assert_current_provider_guard(moved)

    def test_existing_provider_branch_name_fails_closed(self):
        client = FakeBranchClient(["Main", "bodyshop-a5-reconcile-issue-34"])
        with self.assertRaises(v1.PlannerError):
            v1.ensure_provider_branch_name_available(
                client, "agent_RAW", "bodyshop-a5-reconcile-issue-34"
            )

    def test_target_voice_requires_exact_fingerprint(self):
        raw_id = "voice_EXPECTED_RAW"
        original = v1.TARGET_VOICE_ID_SHA256
        try:
            v1.TARGET_VOICE_ID_SHA256 = v1.sha256_text(raw_id)
            resolved = v1.resolve_target_voice(FakeVoiceClient(raw_id))
            self.assertEqual(raw_id, resolved["raw_voice_id"])
            self.assertEqual(
                v1.sha256_text(raw_id), resolved["safe"]["voice_id_sha256"]
            )
        finally:
            v1.TARGET_VOICE_ID_SHA256 = original

    def test_target_voice_wrong_fingerprint_fails_closed(self):
        with self.assertRaises(v1.PlannerError):
            v1.resolve_target_voice(FakeVoiceClient("voice_WRONG_RAW"))

    def test_plan_is_sanitized_and_operation_order_is_deterministic(self):
        target = v1.derive_expected_target(load_expected())
        live = {
            "safe_guard": json.loads(json.dumps(v1.CURRENT_PROVIDER_GUARD_V1)),
            "raw": {
                "agent_id": "agent_SECRET_RAW",
                "branch_id": "branch_SECRET_RAW",
                "version_id": "version_SECRET_RAW",
                "main_branch_id": "mainbranch_SECRET_RAW",
                "procedure_ids_by_name": {
                    "Element identification": "procedure_ELEMENT_SECRET_RAW",
                    "Operator breakdown": "procedure_OPERATOR_SECRET_RAW",
                    "Technician pre-close": "procedure_TECH_SECRET_RAW",
                },
            },
        }
        target_voice = {
            "raw_voice_id": "voice_SECRET_RAW",
            "safe": {
                "name": v1.TARGET_VOICE_NAME,
                "voice_id_sha256": v1.sha256_text("voice_SECRET_RAW"),
                "same_name_candidates": 1,
            },
        }

        plan = v1.build_sanitized_plan(
            live, target, target_voice, "bodyshop-a5-reconcile-issue-34"
        )
        self.assertEqual(
            list(range(1, 9)),
            [item["order"] for item in plan["planned_operations"]],
        )
        encoded = json.dumps(plan, ensure_ascii=False)
        for forbidden in (
            "agent_SECRET_RAW",
            "branch_SECRET_RAW",
            "version_SECRET_RAW",
            "mainbranch_SECRET_RAW",
            "procedure_ELEMENT_SECRET_RAW",
            "procedure_OPERATOR_SECRET_RAW",
            "procedure_TECH_SECRET_RAW",
            "voice_SECRET_RAW",
        ):
            self.assertNotIn(forbidden, encoded)

    def test_plan_never_uses_delete_draft_as_committed_removal(self):
        target = v1.derive_expected_target(load_expected())
        live = {
            "safe_guard": v1.CURRENT_PROVIDER_GUARD_V1,
            "raw": {
                "agent_id": "agent_RAW",
                "branch_id": "branch_RAW",
                "version_id": "version_RAW",
                "main_branch_id": "mainbranch_RAW",
                "procedure_ids_by_name": {
                    "Technician pre-close": "procedure_TECH_RAW"
                },
            },
        }
        target_voice = {
            "raw_voice_id": "voice_RAW",
            "safe": {
                "name": v1.TARGET_VOICE_NAME,
                "voice_id_sha256": "f" * 64,
                "same_name_candidates": 1,
            },
        }
        plan = v1.build_sanitized_plan(live, target, target_voice, "isolated")
        methods = [op["method"] for op in plan["planned_operations"]]
        self.assertNotIn("DELETE", methods)
        self.assertIn(
            "DELETE draft as committed Procedure removal", plan["prohibited"]
        )

    def test_provider_main_merge_has_separate_approval_gate_and_no_force(self):
        target = v1.derive_expected_target(load_expected())
        live = {
            "safe_guard": v1.CURRENT_PROVIDER_GUARD_V1,
            "raw": {
                "agent_id": "agent_RAW",
                "branch_id": "branch_RAW",
                "version_id": "version_RAW",
                "main_branch_id": "mainbranch_RAW",
                "procedure_ids_by_name": {
                    "Technician pre-close": "procedure_TECH_RAW"
                },
            },
        }
        target_voice = {
            "raw_voice_id": "voice_RAW",
            "safe": {
                "name": v1.TARGET_VOICE_NAME,
                "voice_id_sha256": "f" * 64,
                "same_name_candidates": 1,
            },
        }
        plan = v1.build_sanitized_plan(live, target, target_voice, "isolated")
        merge = plan["planned_operations"][-1]
        self.assertEqual("POST", merge["method"])
        self.assertEqual(
            "SEPARATE_PROVIDER_MAIN_MERGE_APPROVAL_REQUIRED",
            merge["approval_gate"],
        )
        self.assertFalse(merge["body_safe"]["force"])

    def test_api_client_is_get_only(self):
        method_names = {
            name
            for name, value in inspect.getmembers(v1.ApiClient, inspect.isfunction)
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
                "search_voices",
            },
            method_names,
        )
        source = inspect.getsource(v1.ApiClient._get)
        self.assertIn('method="GET"', source)
        for forbidden in (
            'method="POST"',
            'method="PATCH"',
            'method="PUT"',
            'method="DELETE"',
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
