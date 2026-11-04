# Authored divider + one World color snapshot

**2026-11-05: INSTALLED / RUNTIME_PENDING.** Source readiness remains verified.
Candidate `divider-color-snapshot-20261105`, branch `research/divider-color-snapshot`.
Exact source/asset/config-template hashes: [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json);
its containing Git commit identifies the exact candidate. History is linear:
audit `adedeef423480149695ae5beadaeaf9b0135fe82` → authored asset
`7ff9d6eebfd678d7abada1f16d149e5e02c5ed99` → this candidate.
No cherry-picked duplicate asset or independently redesigned renderer.

This self-contained successor follows the prior candidate layout. Accepted Style
source `da830808912b38527fb5088a6543d6a070b5f3f7` and its manifest are untouched.
main/Composition/Panel/InputAudit/KeyboardBindings are byte-identical to Style.
VERSION0.1.0/main/releases are unchanged; no semantic version is consumed.

## Scope and readiness

Two outcomes in **one** future session: visually evaluate the approved divider
in World space and capture actual same-session RT/MID metadata missing from the
accepted Style archive. The [archive audit](../hint-mirror/VISUAL_FIDELITY.md#local-archive-audit--2026-11-04-read-only)
is reused, not repeated. The latter needs a live instance; one bounded readout in
the already-requested visual successor avoids a second test mod/material A/B.
This is evidence gathering, **not a color/halo correction**.

Source readiness: owner is the own ornament UImage/Canvas slot and its Brush;
native ImportFileAsTexture2D/SetBrushFromTexture are the established seam.
Own Composition is the final layout/tint writer. Only the own divider and new
readout change behavior; original TipHUD/Retainer/MID/RT are read-only. Preserve
hide/resume, frame-Yaw, input, RT1024×512, scale.25, anchor+32Z, stock Masked
depth/occlusion, font isolation and terminal cleanup. Tests cover import failure,
full-envelope layout/rollback and lifecycle. Native sampling/rendering, apparent
thickness and this candidate's STOP require user observation; production BLOCKED.

## Exact resource and geometry

Runtime uses only [aphes_divider_256x32.png](../../../../assets/dividers/aphes_divider_256x32.png):
SHA256 `b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969`.
256×32, non-interlaced8-bit RGBA. SVG is editable source; the opaque dark preview
is never imported. No game-owned PNG is packaged; Aphes.ttf remains private.

Direct offline alpha measurement (exclusive right/bottom): nonzero alpha bbox
`(3,8)-(253,24)` =250×16; alpha>127 bbox `(4,11)-(252,21)`; straight shaft
region x32..95 occupies rows13..18, six rows including fringe. The complete PNG
has32 rows; it is not a32-pixel solid bar. Exact PNG bytes/chunk CRCs are checked
offline, IHDR and decoded native dimensions at runtime.

| Candidate start | Meaning |
| --- | --- |
| Length300 / thickness1× | Only two defaults changed from Style source (240/2×).1× preserves authored aspect and braid. |
| Slot height `length * 32/256 * thickness` =37.5 | Layout reserves the **whole** texture rectangle; no cropping/UV exception. |
| Visible nonzero envelope about18.75; shaft fringe about7.03 | Derived layout units at300/1×, not measured screen pixels or rendering acceptance; filtering can alter appearance. |
| Other15 defaults | Identical to Style source: fonts52/30, tracking400, gaps7, hint54/gap64/Y0, brightness1, outlines0. Last user settings remain a tuning reference, not silently adopted defaults. |

The old length300/thickness2.5× described a570×16 texture; copying2.5× would make
the new slot93.75 high. Default1× avoids that unproved transfer. Length/thickness/
alpha/Y/gaps remain live controls; thickness intentionally scales Y, while1× is
the undistorted authored aspect. All17 fields, ranges, paging, recoverable edit
rejection and last-valid rollback remain. Full-slot bounds keep text gaps
conservative despite transparent padding. No mipmaps, custom shader/material,
C++ plugin, distance scaling or World-pose change.

Import remains once-only, using explicit CDO/world context and private path.
Returned Texture2D must carry RF_Transient and report256×32. Own Brush binding is
read back and retains it. This does **not** claim texture Outer is the Image:
the established native importer owns construction. Unchanged Composition cleanup
clears only the own Brush and detaches own children, preserving release retry.
No forced GC/package unload. Future installation must check the exact PNG SHA;
the runtime IHDR guard is not a cryptographic hash implementation.

## One bounded read-only snapshot

[IIPColorSnapshot.lua](Scripts/IIPColorSnapshot.lua) runs on the existing
EngineTick path after Composition's stable native binding and own SHOWN state.
It waits for actual GetRenderTarget, checking at most eight eligible visible
frames; hidden frames do not count. This bounds diagnostic queries, not gameplay
duration. If unavailable, one reason is logged and the editor continues. Once
captured, edits/hide-show/device changes/NumPad9 never repeat it. No snapshot
UObject is retained.

Four `IIP_COLOR event=SNAPSHOT id=1` lines normally form **one** snapshot:

| Scope | Actual readbacks attempted |
| --- | --- |
| component | Identity, bApplyGammaCorrection, BlendMode enum, BackgroundColor, TintColorAndOpacity, OpacityFromTexture. |
| own_rt | Identity, SizeX/SizeY, reflected **sRGB** (case matters), TargetGamma, bForceLinearGamma, RenderTargetFormat enum, OverrideFormat enum, ClearColor. |
| own_mid | Identity, Outer/Parent, SlateUI equals own RT, effective TintColorAndOpacity/BackColor/OpacityFromTexture via verified K2 getters. |
| native | Retainer identity/mode/opacity, child tint, effect MID identity/Outer/Parent/blend, actual Icon texture and corresponding RT fields. Internal renderer gamma is UNAVAILABLE. |

Unavailable optional fields/getters/invalid numeric values are `UNAVAILABLE`,
never constructor defaults. No reflected GetFormat is invented;
`RHI_pixel_format=UNKNOWN` is explicit regardless of enum values. Inactive
Retainer mode gives no fabricated Icon RT. Native TipIconMat is not known to
declare the own outer material's Tint/BackColor/Opacity parameters; these stay
unavailable rather than treating missing-parameter zero as an effective value.
Native Icon binding comes from the verified texture getter in the same callback.

Real own RT/MID ownership, MID parent or observed wrong SlateUI binding remains
fatal through existing guarded STOP/cleanup. Strict native identity/visibility
guards are reused. Optional errors are contained only in the new readout;
mandatory lifecycle checks remain. No color/RT/material/native-resource setter,
game setting change, raw-memory read or pixel capture. A successful snapshot
alone does not identify the cause of pale/blue/halo appearance.

## Offline verification

`python tools/test.py`: **333 tests /24 files PASS**, including15 new cases in
[test_divider_color_snapshot.py](../../../../tests/test_divider_color_snapshot.py).
New tests execute successor Lua for full-slot bounds/control persistence,
rejection/rollback, one snapshot across lifecycle/device changes, optional
absence/throws/inactive Retainer and fatal ownership/binding mismatch; the actual
resource module for valid/invalid IHDR, imported extent/transient/binding failure
and once-only import/release; exact PNG hash/CRC and old manifest preservation.
Established host fixtures are reused; policy/API-contract tests do **not** prove
UE rendering or GC. Full output remains ignored in
`.local/divider-color-snapshot-all-tests.txt`.

## Authorized installation — 2026-11-05

User explicitly authorized installation after the source handoff. At01:11 Moscow
(`install-20261104T221116Z`, UTC archive identity), exact source
`51b9f265c8b6d6b79ff48513a51a84087eeee6be` was installed in a distinct own
`ImmersiveInteractionPromptsDividerColorProbe` directory with host closed.
All13 installed hashes verified: ten Lua files, authored PNG, private config and
own empty enabled marker. PNG matches the manifest; config points to that installed
PNG and the existing private Aphes.ttf. Installed config SHA256:
`0303ceb251fb8c3b09189a088ace1877c2c9f140c6bfa2f27891755035aaa885`.

All21 prior IIP candidates remain disabled, with payload/config preserved;
no old marker needed removal or reactivation.103 existing mod/loader/log files
and46 Config/SaveGames files were copied outside loader and hash-preserved.
UE4SS DLL matches the pinned hash. Verified rollback and exact installed manifest
are private under the ignored installation archive; rollback's syntax and path/
hash guards were checked, but rollback was not executed. It disables only this
new own marker and returns to the prior all-disabled IIP state, retaining payload.
No game launch/termination, hot reload, settings/save/foreign-mod change occurred.
Native load, new import/rendering, snapshot and manual STOP remain **PENDING**.
Frozen source manifest still describes its original source-only handoff; it was
not rewritten to represent installation or runtime acceptance.

## One future test and installation boundary

The following preparation boundary is historical; the separately authorized
installation above is complete. Game launch/termination, hot reload, graphics/
save or foreign-mod changes were not performed. Previous IIP markers are untouched.
Private config is prepared in the ignored local candidate directory; tracked
[example](IIPLiveConfig.example.lua) contains placeholders. No installation
script/marker is handed out as deployment authorization.

Prerequisite: separate installation approval with host closed. Recheck current
loader/mod state; preserve other mods/settings/saves by hashes; external rollback
outside loader; copy/check exact successor Lua/PNG/private config in a distinct
own `ImmersiveInteractionPromptsDividerColorProbe` directory, only one IIP
candidate enabled. Verify installed hashes against the manifest and record config
identity. Preserve Style payload/config/rollback. Do not infer closed host here.

One user-started session after authorized installation:

1. Close HildaSoftLight editor. Ctrl+Alt+F11, one manual reload, natural Open at
   the same known chest. Original Screen prompt must remain visible.
2. Inspect braid/strokes/text/button spacing. Try divider thickness/length/opacity:
   Num8/2 select, Num4/6 adjust, Num5 step, Num7 reset selected. No need to reach
   extremes; rejected edits must restore layout and leave tuning available.
3. Move camera slightly, look away/return. Check vertical Yaw/occlusion,
   same-target hide/show and retained tuning without reimport.
4. NumPad9 logs values; **NumMultiply** explicitly stops while panel is open.
   All own UI must disappear; original Screen action/hint remains.
5. After the user closes the game, tools archive/read the log and verify installed
   identity. Expect one four-line id1 snapshot ending `complete=true` or one
   explicit unavailable reason, plus manual STOP/cleanup evidence. No user log
   transcription. Missing optional fields are evidence limits, not a gamma
   diagnosis or reason for an automatic new run.

Divider visual acceptance, lifecycle/manual cleanup and metadata capture are
separate results from this one session. Do not repeat Masked/Translucent A/B or
compensate gamma/tint/format from appearance alone.
