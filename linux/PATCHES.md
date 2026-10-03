# Extra patch audit: OGC 7.2.8

Reviewed 2026-10-03. Upstream is the actual stable release
[v7.2.8-ogc1](https://github.com/OpenGamingCollective/linux/releases/tag/v7.2.8-ogc1),
commit `f90d862923d8254f6df4b7ea81df68eef6d3a45e`.
The reviewed Skorion source commit is
`fafef94d8f17049b6f4d419f358a231868f03451`, tree
`05dd9f1fe9bb4f3131a4bd5b2a721ee4cb4af141`.

The source commit is published on `skos-ogc-7.2`. Package version
`7.2.8.sk2-1` currently validates its immutable commit archive, SHA256
`5d263b89d06258357e959f7457ad9758ce42c1ba9f40fa4a83c8bf9839f40090`.
The dedicated prepare/config workflow is the pre-tag check. The real new
source tag archive is pinned after that check, and its final packaging commit
is checked before the package tag starts the full build. Existing tags are
never moved. No placeholder hash or SKIP is used.

### CEC build correction in sk2

The sk1 tagged build exposed an OGC omission: the AMD Lilac DMI entry used
`port_c_conns`, but its `{"Port C", NULL}` array was not defined. The sk2 source
fix restores that one definition, making the entire CEC source file identical
to the previous Skorion version while preserving the existing device mappings.
A real Kbuild compilation of `cros-ec-cec.o` first reproduced the error and then
passed with the one-line fix, `CONFIG_CEC_CROS_EC=m`, and objtool enabled.
This is a source fix, not a new packaging patch or workflow change.

## Active patches

### CJKTTY: updated, both font sizes preserved

`0001-cjktty-7.2.patch` is replaced with the maintained gentoo-zh 7.2 patch
at [immutable snapshot 52992b2f](https://github.com/gentoo-zh/cjktty-patches/tree/52992b2fea75236df14d846dd21a2c581ea9d007).
Its code last changed in [f4f485fe](https://github.com/gentoo-zh/cjktty-patches/commit/f4f485fe100224b86a4d9022e1db38a90dcc50ee).
The old file was byte-identical to bigshans' 7.2 patch, so no Skorion-only
CJK hunk was discarded. This remains a community downstream patch, not
Linux mainline acceptance.

The new implementation uses the existing `vc_uni_lines` Unicode screen,
removes the fragile private screen-plane/high-word scheme, bounds glyph
access and rotation allocations, and repairs selection, cursor, scrolling,
font mapping and `/dev/vcs` synchronization. Both 16x16 and 32x32 bitmap
payloads are unchanged. Keep both explicit config options enabled because
the new defaults are disabled.

`0002-cjktty-32.patch` is now fetched from the same immutable gentoo-zh
snapshot, not a moving master. It preserves the glyph bytes while correcting
license/source attribution. `cjktty-font-LICENSE` retains the supplied GPLv2,
OFL-1.1 and copyright notices and is installed in the kernel package.

Pinned inputs:
- [7.2 code + 16font](https://raw.githubusercontent.com/gentoo-zh/cjktty-patches/52992b2fea75236df14d846dd21a2c581ea9d007/v7.x/cjktty-7.2.patch): SHA256 `9f4e207c949d63b077e2ce536c05fb4093bd5529ce66bf7214d642c32117d35c`
- [32font](https://raw.githubusercontent.com/gentoo-zh/cjktty-patches/52992b2fea75236df14d846dd21a2c581ea9d007/cjktty-add-cjk32x32-font-data.patch): SHA256 `561a5bfb155394648f3a97c17447c23f0eb2ce00bf441face5dbc66166ab7663`
- [License](https://raw.githubusercontent.com/gentoo-zh/cjktty-patches/52992b2fea75236df14d846dd21a2c581ea9d007/LICENSE): SHA256 `e42e01b6cbdb2c903a5db74f2a04a59d452c63de7e53cff3eb551ccd3a33ae79`

The upstream [7.2.8 verification record](https://github.com/gentoo-zh/cjktty-patches/blob/3ed52bf538c1b5d605666af2d9ab0d235ae4d7cc/tools/supported-verification.json)
reports 16font build/render and full-system checks. This is upstream evidence,
not our own full kernel or both-font hardware validation.

### Power button and PCI workarounds: retained deliberately

- `0009-Input-Don-t-program-hw-debounce-for-soc_button_array.patch`:
  retain software-only debounce behavior for this sync. The original AMD
  sleep bug has a different accepted fix, [8ff4fb27](https://github.com/torvalds/linux/commit/8ff4fb276e2384a87ae7f65f3c28e1e139dbb3fe),
  plus firmware debounce handling [16c07342](https://github.com/torvalds/linux/commit/16c07342b5425b86547146a6e51d9e32cee8d300),
  both already ancestors of OGC 7.2.8. Dropping this patch would still change
  awake-time debounce on all soc_button_array systems, so ancestry alone is
  insufficient to justify removing the user's behavior.
- `0010-Input-Don-t-send-fake-button-presses-to-wake-system.patch`:
  retain Skorion's wake-policy behavior. Mainline/OGC still synthesize a key
  press; [maintainer discussion](https://www.spinics.net/lists/linux-gpio/msg115431.html)
  explains some Android/userspace stacks need that event to remain awake.
  This is not an accepted upstream fix. Test quick release, held keys,
  aborted suspend, evdev press/release balance, and logind/desktop wake policy.
- `0012-PCI-PM-Add-MSI-MS-1T41-DMI-quirk-to-skip-forced-D0-i.patch`:
  retain the exact MSI vendor + MS-1T41 board scope. It bypasses forced D0
  initialization for all PCI devices on that board, not one endpoint. No
  verified accepted replacement was found. See the [original introduction](https://github.com/SkorionOS/linux-skorion/commit/2f8a2c3fa8b1cf54f5ac2465e543639fc600c279).
  Cold/warm boot, storage/Wi-Fi/GPU, runtime PM, s2idle and hibernation need
  hardware regression tests before this workaround can be retired.

## Inactive files: do not reapply blindly

These files remain as historical references and are not in `source=()`.
Their presence does not enable them. Absorption was assessed from current
code and accepted/replacement history, not just whether `patch` accepts them.

| Files | Assessment and action |
| --- | --- |
| `0001-cjktty-7.0.patch`, `0001-cjktty-7.1.patch` | Historical kernel-version variants; do not use on 7.2. Use the reviewed 7.2 replacement above |
| `0001-HID-hid-msi-claw-Add-MSI-Claw-configuration-driver.patch`, `0002-HID-hid-msi-claw-Add-M-key-mapping-attributes.patch`, `0003-HID-hid-msi-claw-Add-RGB-control-interface.patch`, `0004-HID-hid-msi-claw-Add-Rumble-Intensity-Attributes.patch` | Old `hid-msi-claw.c` series has been replaced by the newer `hid-msi.c` series in OGC. OGC explicitly reverted its older FROM-ML copy and applied FROM-UPSTREAM revisions `87eeeb5b`, `7efd79b3`, `aa28f0b5`, `a94b0ff4`. Current code has M-key mapping, RGB and rumble attributes. Keep inactive; preserve source-side Skorion deltas on the newer implementation |
| `0003-Add-OneXPlayer-HID-RGB-driver.patch` | Current OGC `hid-oxp.c` already provides the driver, generation handling, mapping, RGB and vibration interfaces; source also carries reviewed Skorion changes. Keep the old five-patch v3 copy inactive |
| `0011-hid_add_legion_go_and_go_s_drivers_v6.patch` | OGC/current mainline tree already carries `hid-lenovo-go.c` and `hid-lenovo-go-s.c`, plus subsequent fixes (e.g. `73fde0cb` cancels setup work at removal). Keep the old v6 nineteen-patch series inactive |
| `0007-asus-ally-hid.patch` | Historical sixteen-patch multi-file driver has been replaced by integrated `hid-asus-ally.c`. Reapplying would duplicate the driver architecture; keep inactive |
| `0021-asus-ally-hid-disable-wakeup-attribute-on-N-Key-devi.patch` | Behavior already in integrated `ally_disable_nkey_wakeup()` and probe path; retain source implementation, not the obsolete path patch |
| `0022-asus-ally-hid-grab-short-press-QAM-on-ROG-Xbox-Ally-.patch` | `0x93` short-press handling is in integrated driver (OGC `0cd6c69a`); keep inactive |
| `0020-mmc-RTS525A-card-readers-fix-7.0.patch` | All three behaviors are present: exclude RTS525A from aggressive PM and runtime suspend, and 10 ms power-on delay. OGC commits include `a64611dd` and `15089819`; keep inactive |
| `0025-lenovo_wmi_add_fixes_and_enhancement_v4.patch` | Current `lenovo/wmi-other.c` has lwmi_attr_id, corrected attribute layout and CPU/GPU tunables plus later upstream updates; keep old v4 series inactive |
| `0024-hdmi-vrr-v3.patch` | Superseded by OGC's current HDMI/VRR series, including later HF-VSDB/VTEM, MCCS and passive-VRR fixes. Reapplying the old nineteen-patch copy would duplicate or undo newer logic; keep inactive |
| `0050-platform-x86-msi-wmi-platform-update-tdp-range.patch` | **Not** an OGC default: OGC gen1/gen2 use PL1 minimum 8 W and PL2 minimum 9 W. Candidate Skorion source preserves the customization in `01bce0207a6c2`, with both minima 5 W on both generations. Keep the obsolete `ppt_min`-field patch inactive, assert the newer source values |
| `0012-iommu-Skip-mapping-at-address-0x0-if-it-already-exis.patch` | Original broad EADDRINUSE suppression is superseded by target's precise `iommu_iova_to_phys(domain, addr ? addr : 1)` fix, which disambiguates unmapped vs physical-zero. Do not reinstate global suppression that would hide real overlaps |
| `0003-iio-imu_Add_ROG_ALLY_bmi323-support.patch` | Despite its filename, this only excludes RC71L/AIR Plus from bmc150 probing; it does not add a BMI323 driver. It is absent from both active packaging and current source and was not silently re-enabled. Its old DMI exclusion is not claimed absorbed; require a current sensor-binding failure and device repro before reviving it |
| `R0001-Revert-drm-amd-display-enable-tf_blend-if-supported-.patch` | Historical 2025 revert is not active. Current color pipeline uses MPC preblend capability and broader property logic; do not restore the old ogam-only behavior without a current regression |
| `R0002-Revert-drm-re-allow-no-op-changes-on-non-primary-pla.patch` | Historical 2025 revert is not active. Current source deliberately permits no-op non-primary async changes with the subsequent driver checks; do not reintroduce the old behavior without a current regression |

Source links for the replacement history:
- [MSI upstream driver](https://github.com/OpenGamingCollective/linux/commit/87eeeb5bf4815f47aa6fc8ae1234d2c322893ad8)
- [MSI latest rumble revision](https://github.com/OpenGamingCollective/linux/commit/a94b0ff4190abfac5280e6f3e6dfbb6808a9d809)
- [Legion cleanup](https://github.com/OpenGamingCollective/linux/commit/73fde0cbff7d9d618591774a12c23434232752c1)
- [RTS525A runtime suspend](https://github.com/OpenGamingCollective/linux/commit/15089819401ba151d89673e5f9eb8a9993b7f89b)
- [Latest source tree](https://github.com/OpenGamingCollective/linux/tree/f90d862923d8254f6df4b7ea81df68eef6d3a45e)

## Configuration and checks

`prepare()` now normalizes after merging config-sk and checks every requested
symbol using `check-config.py`. It fails on missing/renamed symbols or lost
dependencies. It no longer leaves MODVERSIONS implementation choices to an
interactive SYNC during compilation. The explicit GENKSYMS/BASIC_MODVERSIONS
choices match the current released package. Removed ASHMEM, ANDROID and
ANDROID_BINDER_IPC_SELFTEST lines were absent from that package's final config
already; this does not remove an implemented feature.

Two stale base-config m values (NETFILTER_NETLINK and
SND_SOC_ACPI_AMD_SDCA_QUIRKS) are corrected to bool y, matching both the
released package and candidate normalization.

The checker covers 23 Skorion options. KCFLAGS is a compiler flag, not a
Kconfig symbol: a separate regression test checks exported
`-DAMD_PRIVATE_COLOR`. Existing package names and kernelrelease conventions
are unchanged. The obsolete swallowed-error `drivers/custom install` call
is removed; OGC's actual drivers are installed through modules_install.

Validation performed on the candidate code tree:
- All five updated/retained patches applied in order with `--fuzz=0`
- Actual Kconfig compile and olddefconfig → fragment merge → olddefconfig,
  then all 23 settings verified with both CJK fonts enabled
- Ten unit tests cover success, missing/disabled values, duplicates, malformed
  or empty fragments, MODVERSIONS/fonts and exported AMD color flag
- Bash syntax and input hash/cardinality checks pass
- Real Kbuild/GCC 14.2 compilation passes for both CJK font objects plus
  `selection.o`, `vt.o`, `bitblit.o`, `fbcon.o`, `fbcon_ccw.o`, `fbcon_cw.o`,
  `fbcon_rotate.o` and `fbcon_ud.o` (ten targets), with objtool built and
  enabled. The recorded compiler command contains `-DAMD_PRIVATE_COLOR`
- Applied-source whitespace check passes; the imported patch is preserved
  byte-for-byte, so patch-file context whitespace is excluded from packaging
  `git diff --check`

Configuration and focused object checks used Debian GCC 14.2 and privately
extracted official bison/flex/bc/m4/libelf tools. Do not overwrite the production base config with this
environment's generated config: regenerate/review it under the actual Arch
build toolchain, especially debug/BTF and compiler-capability differences.

These initial local checks do not establish a full kernel package build,
installation, boot, both-font runtime test or handheld hardware validation.
The exact-commit CI workflows separately establish clean Arch prepare/full
makepkg and module/header package checks. Device and CJK runtime regression
tests remain necessary even after CI succeeds.

The release workflow removes privileged mode, host `/usr` and `/opt` mounts,
and destructive host cleanup. Ordinary branch pushes run only prepare/config
CI. Full kernel/package building remains triggered by tags or explicit manual
dispatch, as in the original repository workflow.
