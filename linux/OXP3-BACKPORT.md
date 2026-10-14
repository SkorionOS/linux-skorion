# OXP3 backport, package release 7.2.8.sk2-2

This update follows the normal `linux-skchos` / `linux-skchos-headers` package
line on `7.2-ogc`. `pkgrel` increases from 1 to 2; the package tag is
`v7.2.8-sk2-2` and expected kernel release is `7.2.8-sk2-skchos-2`.
No image manifest or CI workflow is changed.

## Pinned inputs and attribution

- Recipe baseline: SkorionOS/linux-skorion `83194d6b7a22cde76a0a255274c5bc4d499373fd`.
- Source baseline: SkorionOS/linux `fafef94d8f17049b6f4d419f358a231868f03451`, tag `v7.2.8-sk2`.
- Source archive SHA256 remains `8d5a9ef66d49a34eed2cdf218d14e7e47a7ce788a58810e2b906ebd90eda0488`.
- OXP3 upstream review: <https://github.com/OpenGamingCollective/linux-unstable/pull/13>.
- Isolated 15-commit series: parent `5be7813f340baa3b2cac9e8297fea101f2d8f35b`
  through `4396c18eef297543889681a77283c13e047dfe22` in Grippy98/linux-unstable.
  Do not apply the moving whole-PR comparison, which includes unrelated history.
- Every patch retains Andrei Aldea's author/date/message/Signed-off-by and other
  original trailers. `oxp3-series.json` records upstream commit, original email
  patch SHA256, and adapted patch SHA256. All 15 local patches are checksum-pinned.

Adaptations retain the stable `system_wq` choice and inherited
`go:rgb:joystick_rings` ABI. New auxiliary zones keep `oxp:rgb:guide_button` and
`oxp:rgb:rear_logo`. No Kconfig dependency is added; `config-sk` continues to
require `CONFIG_HID_OXP=m` and module versioning. The five existing packaging
patches remain unchanged, before the 15 OXP3 patches.

## Verification

The initial backport was prepared and checked on 2026-10-14:
- All 15 provenance-preserving email patches applied to the exact source with
  git am; the resulting driver matched the reviewed adapted source byte-for-byte.
- All 20 active package patches applied with `--fuzz=0`; both config normalization
  passes and all 23 requested Skorion settings passed.
- A real Kbuild `W=1 drivers/hid/hid-oxp.o` build passed without warnings with
  GCC 14.2.0 and official Debian tools, preserving OXP=m, MODVERSIONS, DWARF5,
  BTF, both CJK fonts and the requested production config. This object check
  was not a full kernel, modpost-validated module or package build.
- Initial integration runs 38536116710 and 38537326633 passed all 14 tests and
  the full source/checksum/prepare checks in the existing Arch CI environment.
- The initial full build was cancelled by the user while its machine was offline.
  No binary release was produced by that cancelled run.

The normal release now uses the same patch bytes and configuration, restoring
the standard package names and bumping pkgrel. Its branch prepare/config checks
and tag-triggered full package build must pass for this exact release commit.
The final run/artifact links are recorded with the release, not inferred from
these earlier focused checks.

## Publishing and deployment boundary

Use the existing branch prepare/config workflow, then the normal new package tag
for the full self-hosted Arch build and release. Never move old tags or overwrite
old release assets. Do not rebuild the abandoned experimental tag.

A successful package build does not establish hardware or immutable-deployment
validation. SKOS/frzr uses generic kernel/initramfs paths and an ESP guard; no
user machine or image manifest is modified by preparing and publishing this
kernel package. Before broad rollout, test actual OXP3 boot, DMI/interface-2
ownership, controls/F15/F16, Steam/QAM, rumble, all RGB zones, suspend/resume,
reconnect and available older OXP hardware. Check recovery on the actual frzr
layout before suggesting installation or rollback commands.
