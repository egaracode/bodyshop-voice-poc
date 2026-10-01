import ast
import copy
import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/reference_resolution_harness.py"
FIXTURE_PATH = ROOT / "tests/fixtures/reference_resolution_v1.json"

spec = importlib.util.spec_from_file_location("rrh", TOOL_PATH)
rrh = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rrh
spec.loader.exec_module(rrh)


class ReferenceResolutionHarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        rrh.validate_fixture(cls.fixture)

    def observation(self, **overrides):
        value = {
            "workshop_scope": "T01",
            "model": "A01",
            "installation": "LAT-IZQ",
            "operation": "OP100",
            "device": "Robot 01",
            "subdevice": None,
            "description": "Texto libre no usado para identidad",
        }
        value.update(overrides)
        return value

    def test_valid_device_path_resolves(self):
        result = rrh.resolve_reference(self.fixture, self.observation())
        self.assertEqual("RESOLVED", result.outcome)
        self.assertEqual("DEVICE", result.grain)
        self.assertEqual("fixture-ref-t01-a01-latizq-op100-r01", result.reference_path_id)

    def test_valid_device_subdevice_path_resolves(self):
        result = rrh.resolve_reference(self.fixture, self.observation(subdevice="motor robot"))
        self.assertEqual("RESOLVED", result.outcome)
        self.assertEqual("DEVICE_SUBDEVICE", result.grain)
        self.assertEqual("fixture-ref-t01-a01-latizq-op100-r01-motor", result.reference_path_id)

    def test_declared_aliases_and_accents_resolve(self):
        result = rrh.resolve_reference(
            self.fixture,
            self.observation(
                workshop_scope="Taller Uno",
                model="Modelo A01",
                installation="Lateral Izquierdo",
                operation="Operación 100",
                device="Robot Uno",
                subdevice="Cuadro Robot",
            ),
        )
        self.assertEqual("RESOLVED", result.outcome)
        self.assertEqual("fixture-ref-t01-a01-latizq-op100-r01-armario", result.reference_path_id)

    def test_wrong_parent_hierarchy_is_not_found(self):
        self.assertEqual(
            "NOT_FOUND",
            rrh.resolve_reference(self.fixture, self.observation(model="A02")).outcome,
        )

    def test_unknown_device_is_not_found(self):
        self.assertEqual(
            "NOT_FOUND",
            rrh.resolve_reference(self.fixture, self.observation(device="Robot 77")).outcome,
        )

    def test_unknown_subdevice_is_not_found(self):
        self.assertEqual(
            "NOT_FOUND",
            rrh.resolve_reference(
                self.fixture, self.observation(subdevice="Servo inexistente")
            ).outcome,
        )

    def test_ambiguous_device_alias_fails_closed(self):
        result = rrh.resolve_reference(self.fixture, self.observation(device="Robot Principal"))
        self.assertEqual("AMBIGUOUS", result.outcome)
        self.assertEqual(2, result.candidate_count)
        self.assertIsNone(result.reference_path_id)

    def test_missing_workshop_scope_is_incomplete(self):
        result = rrh.resolve_reference(self.fixture, self.observation(workshop_scope=None))
        self.assertEqual("INCOMPLETE", result.outcome)
        self.assertIn("workshop_scope", result.missing_fields)

    def test_missing_required_parent_context_is_incomplete(self):
        result = rrh.resolve_reference(self.fixture, self.observation(operation=""))
        self.assertEqual("INCOMPLETE", result.outcome)
        self.assertIn("operation", result.missing_fields)

    def test_inactive_path_is_not_selectable(self):
        result = rrh.resolve_reference(self.fixture, self.observation(device="Robot 99"))
        self.assertEqual("NOT_FOUND", result.outcome)
        self.assertIsNone(result.reference_path_id)

    def test_device_without_device_grain_requires_subdevice(self):
        result = rrh.resolve_reference(
            self.fixture, self.observation(operation="OP200", device="Robot 03")
        )
        self.assertEqual("INCOMPLETE", result.outcome)
        self.assertEqual("subdevice_required", result.reason)

    def test_free_text_description_cannot_resolve_identity(self):
        result = rrh.resolve_reference(
            self.fixture,
            self.observation(
                device="Equipo desconocido",
                description="La avería está en Robot 01 motor",
            ),
        )
        self.assertEqual("NOT_FOUND", result.outcome)

    def test_duplicate_reference_path_id_fails_closed(self):
        fixture = copy.deepcopy(self.fixture)
        duplicate = copy.deepcopy(fixture["paths"][0])
        duplicate["device"] = {"value": "Robot 55", "aliases": []}
        fixture["paths"].append(duplicate)
        with self.assertRaises(rrh.HarnessError):
            rrh.validate_fixture(fixture)

    def test_duplicate_canonical_path_fails_closed(self):
        fixture = copy.deepcopy(self.fixture)
        duplicate = copy.deepcopy(fixture["paths"][0])
        duplicate["reference_path_id"] = "fixture-ref-duplicate"
        fixture["paths"].append(duplicate)
        with self.assertRaises(rrh.HarnessError):
            rrh.validate_fixture(fixture)

    def test_malformed_grain_fails_closed(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["paths"][0]["grain"] = "UNKNOWN"
        with self.assertRaises(rrh.HarnessError):
            rrh.validate_fixture(fixture)

    def test_fixture_must_declare_noncanonical_authority(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["authority"] = "CANONICAL"
        with self.assertRaises(rrh.HarnessError):
            rrh.validate_fixture(fixture)

    def test_harness_imports_no_network_or_provider_client(self):
        tree = ast.parse(TOOL_PATH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(
            {"urllib", "http", "socket", "requests", "supabase"}.isdisjoint(imported)
        )


if __name__ == "__main__":
    unittest.main()
