import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "issue40_classifier",
    TOOLS / "elevenlabs_issue40_compiled_artifact_classifier_v1.py",
)
classifier = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = classifier
spec.loader.exec_module(classifier)


class Issue40CompiledArtifactClassifierTests(unittest.TestCase):
    def test_expected_subset_accepts_provider_extras(self):
        expected = {
            "type": "client",
            "name": "bodyshop_resolve_confirmed_intake",
            "expects_response": True,
        }
        actual = {
            "type": "client",
            "name": "bodyshop_resolve_confirmed_intake",
            "expects_response": True,
            "execution_mode": "immediate",
        }
        self.assertEqual(
            [],
            classifier._safe_expected_subset_diff(
                expected, actual, "$.conversation_config.agent.prompt.tools[0]"
            ),
        )

    def test_expected_subset_rejects_semantic_value_change_without_raw_string(self):
        diff = classifier._safe_expected_subset_diff(
            {"name": "bodyshop_resolve_confirmed_intake"},
            {"name": "unexpected-secret-like-value"},
            "$.tool",
        )
        self.assertEqual(1, len(diff))
        self.assertEqual("VALUE_MISMATCH", diff[0]["kind"])
        self.assertNotIn("unexpected-secret-like-value", str(diff))
        self.assertIn("sha256", diff[0]["actual"])

    def test_exact_procedure_id_requires_one_named_match(self):
        agent = {
            "procedures": {
                "agtprc_one": {"name": "Operator breakdown"},
                "agtprc_two": {"name": "Technician pre-close"},
            }
        }
        self.assertEqual(
            "agtprc_one",
            classifier._exact_procedure_id(agent, "Operator breakdown"),
        )
        with self.assertRaises(classifier.ClassifierError):
            classifier._exact_procedure_id(agent, "Missing")

    def test_source_is_get_only(self):
        source = (
            TOOLS / "elevenlabs_issue40_compiled_artifact_classifier_v1.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(".post(", source)
        self.assertNotIn(".patch(", source)
        self.assertNotIn('method="POST"', source)
        self.assertNotIn('method="PATCH"', source)
        self.assertNotIn('method="PUT"', source)
        self.assertNotIn('method="DELETE"', source)
        self.assertIn('"provider_main_write_performed": False', source)
        self.assertIn('"safe_to_rerun_merge_executor": False', source)

    def test_source_does_not_emit_raw_procedure_id_fields(self):
        source = (
            TOOLS / "elevenlabs_issue40_compiled_artifact_classifier_v1.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('"operator_procedure_id": operator_id', source)
        self.assertNotIn('"technician_procedure_id": technician_id', source)
        self.assertIn('"operator_procedure_id_sha256"', source)
        self.assertIn('"technician_procedure_id_sha256"', source)


if __name__ == "__main__":
    unittest.main()
