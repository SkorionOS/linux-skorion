#!/usr/bin/env python3
"""Fail closed unless this exact release commit passed both branch CI workflows."""
import json
import os
import re
import subprocess
from urllib.request import Request, urlopen


def api(path):
    request = Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/{path}",
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                 "Accept": "application/vnd.github+json"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    sha = os.environ["GITHUB_SHA"]
    ref = os.environ["GITHUB_REF"]
    result = subprocess.run(
        ["bash", "-c", 'source linux/PKGBUILD; printf "%s\\n" "v${_pkgver}-${pkgrel}" "${source[0]}" "${sha256sums[0]}"'],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    expected_tag, source_url, source_hash = result
    if ref != f"refs/tags/{expected_tag}":
        raise SystemExit(f"Tag does not match PKGBUILD version: {ref}, expected {expected_tag}")
    if not re.fullmatch(r"[0-9a-f]{64}", source_hash):
        raise SystemExit("Source archive must have a real SHA256 checksum")
    source_tag = expected_tag.rsplit("-", 1)[0]
    if source_url != f"https://github.com/SkorionOS/linux/archive/refs/tags/{source_tag}.tar.gz":
        raise SystemExit("Release requires a published, checksum-pinned source tag archive")
    for workflow in ("main.yaml", "integration-test.yaml"):
        runs = api(f"actions/workflows/{workflow}/runs?head_sha={sha}&event=push&branch=7.2-ogc&per_page=100")
        matching = [run for run in runs["workflow_runs"]
                    if run["head_sha"] == sha and run["head_branch"] == "7.2-ogc"
                    and run["event"] == "push"]
        latest = max(matching, key=lambda run: run["id"], default=None)
        if latest is None or latest["status"] != "completed" or latest["conclusion"] != "success":
            raise SystemExit(f"Latest 7.2-ogc branch run of {workflow} has not succeeded for {sha}")
    print(f"Release gate passed: {expected_tag}, exact packaging commit {sha}")


if __name__ == "__main__":
    main()
