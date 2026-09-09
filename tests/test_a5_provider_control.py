import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "a5_provider_control.py"
EXPECTED_PATH = ROOT / "elevenlabs" / "A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json"

spec = importlib.util.spec_from_file_location("a5_provider_control", MODULE_PATH)
a5 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = a5
assert spec.loader is not None
spec.loader.exec_module(a5)


class A5ProviderControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

    def exact_actual(self):
        exp = self.expected
        procedures = []
        for item in exp["procedures"]:
            if item["type"] == "structured":
                content = a5.canonical_structured_content(item["content"])
            else:
                content = a5.normalize_text(item["content"]) or ""
            procedures.append(
                {
                    "name": item["name"],
                    "type": item["type"],
                    "trigger": a5.normalize_text(item["trigger"]) or "",
                    "content_canonical": content,
                    "content_sha256": a5.sha256_text(content),
                    "has_draft": False,
                    "procedure_version_present": False,
                }
            )
        return {
            "agent": {
                "name": exp["agent"]["name"],
                "language": exp["agent"]["language"],
                "first_message": exp["agent"]["first_message"],
                "system_prompt": exp["agent"]["system_prompt"],
                "llm": exp["agent"]["llm"],
                "voice_name": exp["agent"]["voice"]["name"],
                "dynamic_variable_names": sorted(exp["agent"]["dynamic_variable_names"]),
            },
            "procedures": procedures,
            "procedures_gap": None,
            "provider_metadata": {
                "version_present": False,
                "branch_present": True,
                "main_branch_present": False,
                "version_id_sha256": None,
                "branch_id_sha256": "fixture",
                "main_branch_id_sha256": None,
            },
        }

    def test_exact_state_is_no_drift(self):
        results = a5.compare_expected(self.expected, self.exact_actual())
        self.assertEqual("NO_DRIFT", a5.overall_status(results))
        self.assertTrue(all(item["status"] == "NO_DRIFT" for item in results))

    def test_material_difference_is_drift(self):
        actual = self.exact_actual()
        actual["agent"]["llm"] = "different-model"
        actual["procedures"][0]["type"] = "free_form"
        results = a5.compare_expected(self.expected, actual)
        self.assertEqual("DRIFT", a5.overall_status(results))
        drift_fields = {item["field"] for item in results if item["status"] == "DRIFT"}
        self.assertIn("agent.llm", drift_fields)
        self.assertIn("procedures.Operator breakdown.type", drift_fields)

    def test_missing_procedure_branch_is_unverifiable(self):
        actual = self.exact_actual()
        actual["procedures"] = None
        actual["procedures_gap"] = "Provider did not expose branch_id"
        results = a5.compare_expected(self.expected, actual)
        self.assertEqual("UNVERIFIABLE", a5.overall_status(results))
        statuses = {
            item["field"]: item["status"]
            for item in results
            if item["field"].startswith("procedures.")
        }
        self.assertEqual("UNVERIFIABLE", statuses["procedures.Operator breakdown"])
        self.assertEqual("UNVERIFIABLE", statuses["procedures.Technician pre-close"])

    def test_sanitized_snapshot_excludes_raw_text_and_resource_ids(self):
        safe = a5.sanitized_snapshot(self.exact_actual())
        rendered = json.dumps(safe, ensure_ascii=False)
        self.assertNotIn(self.expected["agent"]["system_prompt"], rendered)
        self.assertNotIn(self.expected["agent"]["first_message"], rendered)
        self.assertNotIn("agent_id", rendered)
        self.assertNotIn("procedure_id", rendered)
        self.assertIn("system_prompt_sha256", rendered)


if __name__ == "__main__":
    unittest.main()
