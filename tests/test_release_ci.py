import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "ci" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load("check-release")
packages = load("verify-packages")


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GITHUB_SHA": "a" * 40,
                              "GITHUB_REF": "refs/tags/v7.2.8-sk1-1"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.good = {"id": 1, "head_sha": "a" * 40, "head_branch": "7.2-ogc", "event": "push",
                     "status": "completed", "conclusion": "success"}
        self.metadata = "v7.2.8-sk1-1\nhttps://github.com/SkorionOS/linux/archive/refs/tags/v7.2.8-sk1.tar.gz\n" + "f" * 64 + "\n"

    def execute(self, runs, metadata=None):
        with patch.object(release.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 0, self.metadata if metadata is None else metadata)), \
                patch.object(release, "api", side_effect=runs):
            release.main()

    def test_both_exact_branch_runs_are_required(self):
        self.execute([{"workflow_runs": [self.good]}, {"workflow_runs": [self.good]}])

    def test_wrong_sha_branch_event_and_incomplete_runs_fail(self):
        for field, value in (("head_sha", "b" * 40), ("head_branch", "other"),
                             ("event", "pull_request"), ("status", "in_progress"),
                             ("conclusion", "failure")):
            with self.subTest(field=field), self.assertRaises(SystemExit):
                self.execute([{"workflow_runs": [dict(self.good, **{field: value})]}])

    def test_later_failed_run_is_not_hidden_by_an_older_success(self):
        with self.assertRaises(SystemExit):
            self.execute([{"workflow_runs": [self.good, dict(self.good, id=2, conclusion="failure")]}])

    def test_prepare_success_cannot_replace_missing_full_build(self):
        with self.assertRaises(SystemExit):
            self.execute([{"workflow_runs": []}])

    def test_tag_must_match_package_version(self):
        with patch.dict(os.environ, {"GITHUB_REF": "refs/tags/v7.2.8-sk1-2"}), self.assertRaises(SystemExit):
            self.execute([])

    def test_skip_source_checksum_is_not_release_ready(self):
        with self.assertRaises(SystemExit):
            self.execute([], self.metadata.replace("f" * 64, "SKIP"))

    def test_commit_archive_is_not_release_ready(self):
        with self.assertRaises(SystemExit):
            self.execute([], "v7.2.8-sk1-1\nhttps://github.com/SkorionOS/linux/archive/abc.tar.gz\n" + "f" * 64 + "\n")


class PackageValidationTests(unittest.TestCase):
    def test_both_packages_payloads_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("linux-skchos", "linux-skchos-headers"):
                (root / f"{name}.pkg.tar.zst").write_bytes(b"test artifact")
            def metadata(package, member):
                if member == ".BUILDINFO":
                    return "pkgbuild_sha256sum = " + "f" * 64 + "\n"
                return f"pkgname = {package.name.removesuffix('.pkg.tar.zst')}\npkgver = 7.2.8.sk1-1\narch = x86_64\n"
            with patch.object(packages, "metadata", side_effect=metadata), \
                    patch.object(packages.subprocess, "check_output", return_value="\n".join("usr/lib/modules/test/" + p for p in ("vmlinuz", "pkgbase", "kernel/test.ko.zst", "build/Module.symvers", "build/.config", "build/Makefile", "build/version", "build/scripts/Makefile"))), \
                    patch.object(packages.sys, "argv", ["verify", directory, "7.2.8.sk1-1", "a" * 40]):
                packages.main()
            manifest = json.loads((root / "build-manifest.json").read_text())
            self.assertEqual(manifest["packaging_commit"], "a" * 40)
            self.assertEqual(len(manifest["packages"]), 2)
            self.assertEqual(len((root / "SHA256SUMS").read_text().splitlines()), 2)

    def test_invalid_version_payload_and_kernel_release_are_rejected(self):
        for failure in ("version", "kernel_modules", "header_config", "kernel_release"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in ("linux-skchos", "linux-skchos-headers"):
                    (root / f"{name}.pkg.tar.zst").write_bytes(b"test artifact")
                def metadata(package, member):
                    if member == ".BUILDINFO":
                        return "pkgbuild_sha256sum = " + "f" * 64 + "\n"
                    version = "7.2.1.sk2-1" if failure == "version" else "7.2.8.sk1-1"
                    return f"pkgname = {package.name.removesuffix('.pkg.tar.zst')}\npkgver = {version}\narch = x86_64\n"
                def contents(command, **_):
                    header = "headers" in command[-1]
                    members = (["build/Module.symvers", "build/.config", "build/Makefile",
                                "build/version", "build/scripts/Makefile"] if header else
                               ["vmlinuz", "pkgbase", "kernel/test.ko.zst"])
                    if failure == "kernel_modules" and not header:
                        members.remove("kernel/test.ko.zst")
                    if failure == "header_config" and header:
                        members.remove("build/.config")
                    release = "wrong" if failure == "kernel_release" and header else "test"
                    return "\n".join(f"usr/lib/modules/{release}/{p}" for p in members)
                with patch.object(packages, "metadata", side_effect=metadata), \
                        patch.object(packages.subprocess, "check_output", side_effect=contents), \
                        patch.object(packages.sys, "argv", ["verify", directory, "7.2.8.sk1-1", "a" * 40]), \
                        self.assertRaises(SystemExit):
                    packages.main()

    def test_missing_packages_fail(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(packages.sys, "argv", ["verify", directory, "7.2.8.sk1-1", "a" * 40]), \
                self.assertRaises(SystemExit):
            packages.main()


class WorkflowSafetyTests(unittest.TestCase):
    def test_full_build_cannot_clean_host_or_use_privileged_mounts(self):
        workflow = (ROOT / ".github/workflows/main.yaml").read_text()
        self.assertNotIn("volumes:", workflow)
        self.assertNotIn("--privileged", workflow)
        self.assertNotIn("rm -rf", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertIn("makepkg --noconfirm", workflow)
        self.assertNotIn("makepkg --nobuild", workflow)
        self.assertIn('install -d -o build -g build "$PKGDEST" "$BUILDDIR"', workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("python ci/check-release.py", workflow)
        self.assertIn("if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')", workflow)
        self.assertIn("branches: ['7.2-ogc']", workflow)
        self.assertIn("python ci/verify-packages.py", workflow)
        self.assertIn("sha256sum --check SHA256SUMS", workflow)


if __name__ == "__main__":
    unittest.main()
