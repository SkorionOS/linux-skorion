# OXP3 experimental kernel, 7.2.8.sk2.oxp3-1

This is a separate `linux-skchos-oxp3` / `linux-skchos-oxp3-headers` test
package. It does not change the shipped `linux-skchos` recipe, the source tag,
or any image manifest. The expected kernel release is
`7.2.8-sk2-skchos-oxp3-1` (archive build, without Git suffixes).

## Pinned inputs and attribution

- Recipe baseline: SkorionOS/linux-skorion `83194d6b7a22cde76a0a255274c5bc4d499373fd`.
- Source baseline: SkorionOS/linux `fafef94d8f17049b6f4d419f358a231868f03451`, tag `v7.2.8-sk2`.
- Source archive SHA256 remains `8d5a9ef66d49a34eed2cdf218d14e7e47a7ce788a58810e2b906ebd90eda0488`.
- OXP3 upstream review: <https://github.com/OpenGamingCollective/linux-unstable/pull/13>.
- Isolated 15-commit series: parent `5be7813f340baa3b2cac9e8297fea101f2d8f35b`
  through `4396c18eef297543889681a77283c13e047dfe22` in Grippy98/linux-unstable.
  The entire moving PR diff MUST NOT be applied: it contains unrelated history.
- Each patch retains Andrei Aldea's author/date/message/Signed-off-by and other
  original trailers. `oxp3-series.json` records upstream commit, original email
  patch SHA256, and adapted patch SHA256. All 15 local patches are checksum-pinned.

Adaptations are intentionally limited to retaining the stable `system_wq`
choice and inherited `go:rgb:joystick_rings` ABI. The new auxiliary zones keep
`oxp:rgb:guide_button` and `oxp:rgb:rear_logo`. No new Kconfig dependency is
introduced; `config-sk` continues to require `CONFIG_HID_OXP=m` and module
versioning. The existing five packaging patches remain unchanged, before the
15 OXP3 patches. No CI workflow changes are part of this experiment.

## Local verification, 2026-10-14

- All 15 provenance-preserving email patches applied to the exact source with
  `git am`; the resulting driver equals the reviewed adapted source byte-for-byte.
- The complete package `prepare()` succeeded with all 20 active patches using
  `patch --batch --forward --fuzz=0`, both config normalization passes, and the
  package's `check-config.py` verification of all 23 requested settings.
- A real Kbuild `W=1 drivers/hid/hid-oxp.o` build passed without warnings using
  GCC 14.2.0, binutils, and workspace-extracted official Debian build tools.
  This is an object build, not a linked/modpost-validated module or full package.
- This local compiler differs from the Arch runner. The normalized config keeps
  OXP=m, MODVERSIONS, both CJK fonts, DWARF5 and BTF; it does not disable production
  features to make the focused build pass. Compiler/pahole capability fields are
  naturally regenerated (GCC 14, pahole 1.30 locally).
- Full kernel/package, headers, modpost, package conflict verification and physical
  hardware validation must be recorded separately when actually complete.

## Build and deployment boundary

Normal branch integration runs unit tests and `makepkg --nobuild`. A new unique
package tag triggers the unchanged self-hosted Arch full build and publishes a
non-draft prerelease. A test tag must not reuse or move `v7.2.8-sk2-1`, and the
prerelease must not be promoted to stable/latest. Current production image
manifests pin the old exact package URL; this experiment does not edit them.

The unique package/kernel names separate the packaged `/usr/lib/modules/`
trees and header/license locations. This alone does NOT establish safe parallel
booting on an immutable SKOS/frzr installation. Image creation and deployment
scripts select/copy kernel and initramfs paths separately. Do not install this
on a user machine until the particular deployment/rollback layout is checked.

Hardware acceptance still includes correct DMI matching, interface 2 ownership,
front and rear controls, F15/F16 mapping, Steam/QAM, rumble, all RGB zones,
suspend/resume and disconnect/reconnect, plus available legacy OXP regression.
