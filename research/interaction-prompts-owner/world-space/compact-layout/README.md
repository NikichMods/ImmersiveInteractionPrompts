# Compact World layout — research successor

**2026-11-05: READY_SOURCE / NOT_INSTALLED / RUNTIME_PENDING.**
Candidate ID `compact-world-layout-20261105`, branch `research/compact-world-layout`.
Base `f2bc83d76804b1085f4f9faebd70544e27188869`; frozen predecessor source
`51b9f265c8b6d6b79ff48513a51a84087eeee6be` in
[divider-color-snapshot](../divider-color-snapshot/README.md).
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) records exact Lua/config-template
and approved asset hashes; its containing source commit identifies the candidate.
No VERSION/main/release change. User subsequently authorized immediate installation
after successful preparation/tests, superseding this task's original no-install
boundary; installation is separately recorded below when actually completed.

## Question, mechanism and evidence gate

The tested predecessor rejected divider_y−3 at gap2 because it treated all32 PNG
rows as visible. The approved256×32 PNG has nonzero alpha bbox `(3,8)-(253,24)`
(exclusive end). Source also padded native upper GetDesiredSize by another two
outline widths, while native styled text measurement already accounts for outline.
The goal is closer text/divider/text without crossing actual measured text areas,
clipping the RT or weakening rollback. This is **not** another glow experiment.

**READY for bounded research implementation:** own Composition is the only final
layout writer; CanvasPanelSlot position/size setters and own ForceLayoutPrepass/
GetDesiredSize already ran in the accepted host. Changed consumers are only the
four own children and layout log. Native TipHUD, localization/current hint,
font/PNG ownership, hide/resume, frame-Yaw, World scale.25/anchor+32Z/RT1024×512,
stock Masked/depth and STOP/cleanup are preserved. Offline tests prove interval
policy and editor/rollback interactions; actual glyph rendering remains a future
user observation. No new renderer/probe/production behavior is required.

Versioned engine cross-check (original engine source in UE4.27 mirror commit
`306a7e9f7fb53f14c2cb3bfd3854ad906710a17e`, not byte identity with Asterigos):

- [STextBlock.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Slate/Private/Widgets/Text/STextBlock.cpp): ComputeDesiredSize245–272, simple mode explicitly includes outline; normal mode delegates styled layout.
- [SlateTextBlockLayout.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Slate/Private/Widgets/Text/SlateTextBlockLayout.cpp):28–103 applies style/margin/line-height/scale and returns layout size.
- [SlateTextRun.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Slate/Private/Framework/Text/SlateTextRun.cpp):32–59 accounts for outline/shadow in baseline/max-height/measurement.

Saved source hashes are private in `compact-layout-source/sources.json` under
ignored research inputs. Installed UHT declarations confirm the real TextBlock/
font/desired-size seams. Do not substitute generated UHT stub bodies for engine
implementation. DesiredSize is a native conservative layout envelope, **not** a
pixel-perfect glyph-alpha crop: do not subtract guessed ascender/leading/shadow.

## Compact interval policy

Both TextBlocks use fresh **fully styled** desired extents after own prepass,
including their configured outlines. Their slots use those measured heights;
no extra `2*outline` is added. One explicit layout-unit guard surrounds text
envelopes for raster rounding. Width guards likewise use native measured width
rather than estimating from font size or counting glyphs.

For divider full height `H=length * 32/256 * thickness`, reserve a one-source-texel
sampling fringe on either side of known alpha: guarded rows `[7,25]`, versus
actual nonzero `[8,24]`. With slot center C, guarded visible interval is
`[C-H/2+7H/32, C-H/2+25H/32]`. At300/1×, full slot37.5, actual alpha height18.75,
guarded height21.09375. PNG bytes/aspect/UV are untouched, no mipmaps added.

Retain the established divider_y **full-slot-center** convention. Its center is
`upper_guard_bottom + gap + H/2 + divider_y`. This gives the transparent portion
back as valid upward travel: at gap2,−3 now passes,−10 still passes for this
divider size,−11 is rejected by the upper-text boundary. This is not a universal
minimum: changing the image extent/measurement changes the valid envelope.

Lower text starts below the **guarded visible** divider bottom plus gap and its
own text guard. `gap` range is now0–48 (default2 preserved); a negative gap is
rejected. The lower row no longer pays for invisible bottom padding. Guarded
intervals may meet but cannot overlap; visible alpha still has reserved fringe.
Full divider slot stays inside the RT, not just its opaque portion. Full text/
button bounds remain checked. A new measured-width AABB check prevents a wide
upper line intersecting the button when vertical spacing becomes compact.
These are local layout bounds, not a promise that accepted scene bloom cannot
visually extend beyond them.

All17 fields retain their controls/ranges except gap minimum2→0. New defaults
are exactly the [adopted NumPad9 set](../../../../docs/REQUIREMENTS.md#новая-база-настроек-и-будущая-компактность--2026-11-05):
fonts50/30; tracking380; outlines3/3; gap2; dividerY−2/length300/thickness1/alpha1;
hint50/gap12/Y0; upper/lower/divider/hint brightness.8/.6/.6/.4. Num7 restores
these new defaults. Recoverable rejection/restoration still belongs to unchanged
Composition policy; missing measurement, new incompatible content, native errors
or failed rollback stay terminal. Layout log adds slot/guarded-alpha heights and
actual guarded clearances after the existing slot setter/readback path.

Uniform scale gate: **DEFERRED**. UHT contains SetRenderScale, but a complete
common-owner/pivot/bounds contract for all four children under the existing RT
has not been demonstrated. Adding an18th parameter or changing World scale is
unnecessary for the compactness goal and would broaden the runtime hypothesis.
No scale control is added. The finished IIPColorSnapshot import/call/module is
omitted; no new gamma/RT/material reads or corrections are performed. Other
hint/resource/input/panel/main modules are byte-identical to the predecessor.

## Verification and one user run

`python tools/test.py`: **345 tests /25 files PASS**, including12 new cases in
[test_compact_layout.py](../../../../tests/test_compact_layout.py). They run actual
Lua for adopted defaults/reset, outline already included in measured height,
former−3 rejection now valid, gap0, true-overlap rejection/restoration, wide upper
text/button collision, native measurement/rollback failure cleanup, hidden edits,
device rebind, resource retention/release, closed keys and unchanged World/native
state. Independent alpha/text interval checks cover accepted/rejected layouts
over font/outline/length/thickness/gap/offset boundaries. Old source/manifest and
unchanged resource seams are hash-checked; mocks are not native rendering proof.
Full log is ignored at `.local/compact-layout-all-tests.txt`.

After authorized closed-host installation with exact hashes and external rollback,
one user-started run: close HildaSoftLight editor; Ctrl+Alt+F11 → one manual reload
→ same natural Open. Check the new baseline; reduce Vertical gaps toward0 and
raise Divider offset past−2. Lines/braid/button must remain distinct; a genuinely
overlapping edit should restore the last valid layout without ending tuning.
Move camera slightly, look away/return, confirm original Screen prompt and native
hint. NumPad9 logs the selected set; NumMultiply while panel open performs full
STOP. After normal game exit tools archive the log and read geometry/cleanup.
No color comparison, repeated RT snapshot, other action/map test or time limit.
Visual compactness and the new runtime behavior remain pending until that run.
