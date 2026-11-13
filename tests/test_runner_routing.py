from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RunnerRoutingTests(unittest.TestCase):
    def test_release_build_targets_atx(self):
        text = (ROOT / '.github/workflows/main.yaml').read_text()
        self.assertIn('runs-on: [self-hosted, Linux, X64, atx]', text)
        self.assertIn("    tags:\n      - '*'", text)
        self.assertNotIn('branches:', text)
        self.assertNotIn('privileged', text)
        self.assertNotIn('/usr:/', text)
        self.assertNotIn('/opt:/', text)

    def test_atx_integration_is_explicit_and_non_release(self):
        text = (ROOT / '.github/workflows/integration-test.yaml').read_text()
        self.assertIn('inputs.atx &&', text)
        self.assertIn('default: false', text)
        self.assertIn('makepkg --nobuild', text)
        self.assertNotIn('action-gh-release', text)


if __name__ == '__main__':
    unittest.main()
