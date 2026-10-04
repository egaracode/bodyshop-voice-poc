import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PROBE_PATH = TOOLS / "elevenlabs_issue40_preflight_diff_v1.py"

spec = importlib.util.spec_from_file_location("issue40_preflight_diff", PROBE_PATH)
probe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


class Issue40PreflightDiffTests(unittest.TestCase):
    def test_read_only_client_rejects_non_get_methods(self):
        client = probe.ReadOnlyClient("x")
        with self.assertRaises(probe.DiagnosticError):
            client._request("POST", "/x", body={})
        with self.assertRaises(probe.DiagnosticError):
            client._request("PATCH", "/x", body={})
        with self.assertRaises(probe.DiagnosticError):
            client._request("DELETE", "/x")

    def test_sanitize_path_hashes_raw_procedure_ids(self):
        raw = "$.workflow.nodes.__xi_procedure__agtprc_example123/ask_1"
        safe = probe.sanitize_path(raw)
        self.assertNotIn("agtprc_example123", safe)
        self.assertIn("__xi_procedure__agtprc_sha256_", safe)

    def test_structural_diff_reports_extra_field_without_raw_string(self):
        diff = probe.structural_diff(
            {"agent": {"prompt": {"tool_ids": []}}},
            {
                "agent": {
                    "prompt": {"tool_ids": []},
                    "first_message": "sensitive provider string",
                }
            },
            "$.conversation_config",
        )
        self.assertEqual(1, len(diff))
        self.assertEqual(
            "$.conversation_config.agent.first_message",
            diff[0]["path"],
        )
        self.assertEqual("SOURCE_EXTRA_FIELD", diff[0]["kind"])
        self.assertEqual("str", diff[0]["source"]["type"])
        self.assertIn("sha256", diff[0]["source"])
        self.assertNotIn("sensitive provider string", str(diff))

    def test_structural_diff_reports_safe_boolean_values(self):
        diff = probe.structural_diff(
            {"auth": {"enable_auth": False}},
            {"auth": {"enable_auth": True}},
            "$.platform_settings",
        )
        self.assertEqual(
            [{
                "path": "$.platform_settings.auth.enable_auth",
                "kind": "VALUE_MISMATCH",
                "main": {"type": "bool", "value": False},
                "source": {"type": "bool", "value": True},
            }],
            diff,
        )

    def test_structural_diff_detects_list_length_change(self):
        diff = probe.structural_diff(
            {"values": ["a"]},
            {"values": ["a", "b"]},
        )
        self.assertEqual("$.values", diff[0]["path"])
        self.assertEqual("LIST_LENGTH_MISMATCH", diff[0]["kind"])
        self.assertEqual(1, diff[0]["main"]["length"])
        self.assertEqual(2, diff[0]["source"]["length"])

    def test_output_contract_forbids_merge_rerun_claim(self):
        source = PROBE_PATH.read_text(encoding="utf-8")
        self.assertIn('"provider_main_write_performed": False', source)
        self.assertIn('"safe_to_rerun_merge_executor": False', source)
        self.assertIn(
            '"next_gate": "REVIEW_GET_ONLY_DIFF_BEFORE_ANY_PROVIDER_WRITE"',
            source,
        )

    def test_source_has_no_post_patch_put_delete_invocations(self):
        source = PROBE_PATH.read_text(encoding="utf-8")
        self.assertNotIn(".post(", source)
        self.assertNotIn(".patch(", source)
        self.assertNotIn('method="POST"', source)
        self.assertNotIn('method="PATCH"', source)
        self.assertNotIn('method="PUT"', source)
        self.assertNotIn('method="DELETE"', source)


if __name__ == "__main__":
    unittest.main()
