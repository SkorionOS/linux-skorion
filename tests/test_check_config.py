import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "linux" / "check-config.py"
SPEC = importlib.util.spec_from_file_location("check_config", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CheckConfigTests(unittest.TestCase):
    def run_check(self, actual, fragment):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "actual").write_text(actual)
            (root / "fragment").write_text(fragment)
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(root / "actual"), str(root / "fragment")],
                capture_output=True, text=True, check=False,
            )

    def test_tristates_and_quoted_empty_string(self):
        text = 'CONFIG_DRIVER=m\nCONFIG_BUILTIN=y\nCONFIG_DEVICES=""\n# CONFIG_OFF is not set\n'
        result = self.run_check(text, text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Verified 4", result.stdout)

    def test_disabled_forms_are_equivalent(self):
        result = self.run_check("# CONFIG_OFF is not set\n", "CONFIG_OFF=n\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_symbol_is_not_silently_disabled(self):
        result = self.run_check("CONFIG_DRIVER=m\n", "CONFIG_REMOVED=n\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected n, got <missing>", result.stderr)

    def test_dependency_disables_requested_module(self):
        result = self.run_check("# CONFIG_DRIVER is not set\n", "CONFIG_DRIVER=m\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected m, got n", result.stderr)

    def test_reports_all_mismatches(self):
        errors = MODULE.compare_config({"CONFIG_A": "n"}, {"CONFIG_A": "m", "CONFIG_B": "y"})
        self.assertEqual(len(errors), 2)

    def test_rejects_duplicate_settings(self):
        result = self.run_check("CONFIG_DRIVER=m\nCONFIG_DRIVER=y\n", "CONFIG_DRIVER=m\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate setting", result.stderr)

    def test_rejects_malformed_fragment(self):
        result = self.run_check("CONFIG_DRIVER=m\n", "CONFIG_DRIVER m\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid config line", result.stderr)

    def test_rejects_empty_fragment(self):
        result = self.run_check("CONFIG_DRIVER=m\n", "# Only a comment\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no requested config settings", result.stderr)


if __name__ == "__main__":
    unittest.main()
