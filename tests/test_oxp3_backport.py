from pathlib import Path
import hashlib
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINUX = ROOT / 'linux'


def recipe_values():
    script = '''source "$1"
    printf '%s\\n' "$pkgbase" "$pkgver" "$_pkgver" "$pkgrel" "$_srccommit"
    printf '%s\\n' "${source[@]}"
    printf '%s\\n' --CHECKSUMS-- "${sha256sums[@]}"
    '''
    lines = subprocess.check_output(['bash', '-c', script, 'check', str(LINUX / 'PKGBUILD')], text=True).splitlines()
    split = lines.index('--CHECKSUMS--')
    return lines[:5], lines[5:split], lines[split+1:]


class Oxp3BackportTests(unittest.TestCase):
    def test_release_version_and_source_are_pinned(self):
        values, _, _ = recipe_values()
        self.assertEqual(values, ['linux-skchos', '7.2.8.sk2', '7.2.8-sk2', '2',
                                  'fafef94d8f17049b6f4d419f358a231868f03451'])

    def test_contiguous_queue_provenance_and_checksums(self):
        series = json.loads((LINUX / 'oxp3-series.json').read_text())
        self.assertEqual(len(series), 15)
        self.assertEqual(series[0]['sha'], 'f61f96a50cc4573879644da77272aaa8bef59718')
        self.assertEqual(series[-1]['sha'], '4396c18eef297543889681a77283c13e047dfe22')
        _, sources, sums = recipe_values()
        self.assertEqual(len(sources), len(sums))
        self.assertNotIn('SKIP', sums)
        patch_names = [source for source in sources if source.startswith('01') and source.endswith('.patch')]
        self.assertEqual(patch_names, [entry['filename'] for entry in series])
        for entry in series:
            with self.subTest(commit=entry['sha']):
                data = (LINUX / entry['filename']).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry['backport_sha256'])
                self.assertEqual(sums[sources.index(entry['filename'])], entry['backport_sha256'])
                text = data.decode()
                self.assertTrue(text.startswith('From ' + entry['sha'] + ' '))
                self.assertIn('From: Andrei Aldea <andrei1998@gmail.com>', text)
                self.assertIn('Signed-off-by: Andrei Aldea <andrei1998@gmail.com>', text)
                self.assertIn('Upstream-commit: ' + entry['sha'], text)
                self.assertNotIn('system_dfl_wq', text)
                self.assertNotIn('oxp:rgb:joystick_rings', text)

    def test_oxp_module_and_versioning_are_required(self):
        fragment = (LINUX / 'config-sk').read_text().splitlines()
        for setting in ('CONFIG_HID_OXP=m', 'CONFIG_MODVERSIONS=y', 'CONFIG_GENKSYMS=y'):
            self.assertIn(setting, fragment)

    def test_local_file_checksums_match(self):
        _, sources, sums = recipe_values()
        for source, digest in zip(sources, sums):
            if '://' in source:
                continue
            self.assertEqual(hashlib.sha256((LINUX / source).read_bytes()).hexdigest(), digest, source)


if __name__ == '__main__':
    unittest.main()
