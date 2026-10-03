#!/usr/bin/env python3
"""Check fresh makepkg outputs and retain exact build provenance and digests."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys


def metadata(package, member):
    return subprocess.check_output(["bsdtar", "-xOf", str(package), member], text=True)


def fields(text):
    result = {}
    for line in text.splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            result.setdefault(key, []).append(value)
    return result


def main():
    destination, version, commit = sys.argv[1:]
    root = Path(destination)
    packages = sorted(root.glob("*.pkg.tar.zst"))
    expected = {"linux-skchos", "linux-skchos-headers"}
    manifest = {"packaging_commit": commit, "version": version, "packages": []}
    sums = []
    kernel_releases = set()
    for package in packages:
        info = fields(metadata(package, ".PKGINFO"))
        build = fields(metadata(package, ".BUILDINFO"))
        name = info["pkgname"][0]
        if name not in expected or info["pkgver"] != [version] or info["arch"] != ["x86_64"]:
            raise SystemExit(f"Unexpected package identity: {package.name}")
        expected.remove(name)
        contents = subprocess.check_output(["bsdtar", "-tf", str(package)], text=True).splitlines()
        contents = [path.removeprefix("./") for path in contents]
        releases = {match.group(1) for path in contents
                    if (match := re.match(r"usr/lib/modules/([^/]+)/", path))}
        if len(releases) != 1:
            raise SystemExit(f"Expected one kernel release in {package.name}, got {releases}")
        kernel_release = releases.pop()
        kernel_releases.add(kernel_release)
        prefix = f"usr/lib/modules/{kernel_release}/"
        if name == "linux-skchos":
            required = {prefix + "vmlinuz", prefix + "pkgbase"}
            if not any(path.startswith(prefix + "kernel/") and
                       re.search(r"\.ko(?:\.(?:zst|xz|gz))?$", path) for path in contents):
                raise SystemExit(f"No installed kernel modules in {package.name}")
        else:
            required = {prefix + "build/" + member for member in
                        ("Module.symvers", ".config", "Makefile", "version")}
            if not any(path.startswith(prefix + "build/scripts/") for path in contents):
                raise SystemExit(f"No header build scripts in {package.name}")
        if not required.issubset(contents):
            raise SystemExit(f"Missing required payloads in {package.name}: {required - set(contents)}")
        with package.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        sums.append(f"{digest}  {package.name}\n")
        manifest["packages"].append({"file": package.name, "sha256": digest, "buildinfo": build})
    if expected:
        raise SystemExit(f"Missing packages: {sorted(expected)}")
    if len(kernel_releases) != 1:
        raise SystemExit(f"Kernel and headers release mismatch: {kernel_releases}")
    manifest["kernel_release"] = kernel_releases.pop()
    (root / "SHA256SUMS").write_text("".join(sums))
    (root / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"packaging_commit": commit, "version": version,
                      "packages": [p["file"] for p in manifest["packages"]]}, indent=2))


if __name__ == "__main__":
    main()
