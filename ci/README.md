# Kernel CI and release sequence

- `integration-test.yaml` runs packaging unit tests, downloads/checks source
  hashes, applies all enabled patches with zero fuzz, runs `olddefconfig`, and
  asserts the Skorion configuration. It does not compile the full kernel.
- `main.yaml` additionally runs full Arch `makepkg` on trusted `7.2-ogc` pushes,
  manual runs, and version tags. It verifies the kernel and headers package
  versions, required payloads, and matching kernel releases. Packages, checksums,
  `.BUILDINFO` provenance, packaging commit, and build logs are retained.
- Builds use an unprivileged Arch job container on the existing self-hosted
  runner. There are no extra host-directory mounts and no host cleanup. Ensure
  the runner already has enough free disk space; do not delete host tools to
  accommodate a build. Self-hosted runners still execute trusted repository code
  and must not be exposed to untrusted pull requests.
- The build job has read-only repository access. Only the tag-only release job
  has release write permission. A manual or branch build cannot publish.

## Two-repository release

1. Push the reviewed source commit to the approved source branch.
2. Set the real package version and download the immutable source commit archive;
   record its actual SHA256. Push packaging changes and wait for both workflows
   on that exact packaging SHA, including full `makepkg`, to succeed.
3. Create the source tag on the reviewed source commit. Download its actual tag
   archive, change the source URL/extraction directory and checksum accordingly,
   and push the final packaging commit. Both workflows must succeed again on
   this exact final commit.
4. Create `v${_pkgver}-${pkgrel}` on that final packaging commit only. The tag job
   refuses publication unless the latest matching branch runs for both workflows
   succeeded and PKGBUILD uses the expected, SHA256-pinned source tag archive.
5. Follow the tag-triggered full build and release jobs to completion. The release
   job publishes only this run's verified artifacts and verifies their checksums
   again. GitHub release prerelease status remains enabled, as before.

Never move an existing version tag, use `SKIP` for the source checksum, or count a
prepare-only run or another commit's green status as full-build validation.
A successful package build is not boot or handheld hardware validation.
