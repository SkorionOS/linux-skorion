from pathlib import Path
import shlex
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PkgbuildContractTests(unittest.TestCase):
    def test_private_amd_color_macro_is_exported(self):
        result = subprocess.run(
            ["bash", "-c", 'source "$1"; printenv KCFLAGS', "check", str(ROOT / "linux" / "PKGBUILD")],
            capture_output=True, text=True, check=True,
        )
        flags = shlex.split(result.stdout.strip())
        self.assertIn("-DAMD_PRIVATE_COLOR", flags)
        self.assertNotIn("-UAMD_PRIVATE_COLOR", flags)

    def test_fragment_preserves_module_versioning_and_both_cjk_fonts(self):
        fragment = (ROOT / "linux" / "config-sk").read_text().splitlines()
        for setting in (
            "CONFIG_MODVERSIONS=y", "CONFIG_GENKSYMS=y",
            "CONFIG_BASIC_MODVERSIONS=y", "CONFIG_FONT_CJK_16x16=y",
            "CONFIG_FONT_CJK_32x32=y",
        ):
            self.assertIn(setting, fragment)


if __name__ == "__main__":
    unittest.main()
