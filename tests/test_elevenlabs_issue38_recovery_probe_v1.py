import importlib.util
import inspect
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PROBE_PATH = TOOLS / "elevenlabs_issue38_recovery_probe_v1.py"

spec = importlib.util.spec_from_file_location("issue38_recovery", PROBE_PATH)
probe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


class RecoveryProbeTests(unittest.TestCase):
    def test_source_is_get_only(self):
        source = PROBE_PATH.read_text(encoding="utf-8")
        self.assertNotIn('method="POST"', source)
        self.assertNotIn('method="PATCH"', source)
        self.assertNotIn('method="PUT"', source)
        self.assertNotIn('method="DELETE"', source)
        self.assertNotIn(".post(", source)
        self.assertNotIn(".patch(", source)

    def test_schema_diff_reports_provider_extras_without_false_value_mismatch(self):
        expected = {
            "type": "object",
            "required": ["workshop"],
            "properties": {
                "workshop": {"type": "string", "description": "x"}
            },
        }
        actual = {
            "type": "object",
            "required": ["workshop"],
            "properties": {
                "workshop": {
                    "type": "string",
                    "description": "x",
                    "is_omitted": False,
                    "dynamic_variable": "",
                }
            },
            "is_omitted": False,
        }
        diff = probe.schema_diff(expected, actual)
        paths = {(item["path"], item["kind"]) for item in diff}
        self.assertIn(
            ("$.properties.workshop.is_omitted", "PROVIDER_EXTRA_FIELD"),
            paths,
        )
        self.assertIn(
            ("$.properties.workshop.dynamic_variable", "PROVIDER_EXTRA_FIELD"),
            paths,
        )
        self.assertIn(("$.is_omitted", "PROVIDER_EXTRA_FIELD"), paths)
        self.assertFalse(any(item["kind"] == "VALUE_MISMATCH" for item in diff))

    def test_schema_diff_detects_real_semantic_mismatch(self):
        diff = probe.schema_diff(
            {"properties": {"line_stopped": {"type": "boolean"}}},
            {"properties": {"line_stopped": {"type": "string"}}},
        )
        self.assertEqual(
            [
                {
                    "path": "$.properties.line_stopped.type",
                    "kind": "VALUE_MISMATCH",
                    "expected": "boolean",
                    "actual": "string",
                }
            ],
            diff,
        )

    def test_probe_never_marks_original_rerun_safe(self):
        source = PROBE_PATH.read_text(encoding="utf-8")
        self.assertIn('"safe_to_rerun_original_staging": False', source)
        self.assertIn(
            '"next_gate": "REVIEW_RECOVERY_EVIDENCE_BEFORE_ANY_PROVIDER_WRITE"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
