# World style editor — divider weight, button row, brightness comparison

**2026-11-04: READY_SOURCE / INSTALLED; new style/color rendering pending. Production BLOCKED.**
Successor to source `19d35a5a0238a3b228f7058bfcd7234e647ede7e` in
[expanded editor](../live-editor-expanded/README.md). Exact bytes:
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json), identified by its containing commit.
Earlier sources remain frozen; VERSION unchanged, no main/release promotion.

## Authorized installation — 2026-11-04

At18:50:11 Moscow, exact source `da830808912b38527fb5088a6543d6a070b5f3f7`
installed into new ImmersiveInteractionPromptsWorldStyleProbe with host closed.
Nine authored Lua installed hashes match source manifest; private config SHA256
`7cfb0566b1142060b309142bba678adcc53ec2041af3955aeec1efda35e55b9b` and empty own
marker verified,11 files total. Previous WorldExpanded source/config unchanged,
only its verified own marker disabled after new payload verification.20 older IIP
probes disabled; only new Style enabled.93 other prior mod/loader/log files and46
config/save files hash-preserved;94-file baseline includes intentionally disabled
old own marker. Pinned loader/external resources unchanged. Private pretest logs,
before/installed/verified records, backups and guarded rollback ignored under
`.local/research/interaction-prompts/world-space/live-editor-style/install-20261104T155011Z`.
Rollback syntax verified, not executed. No host launch/termination/hot reload,
other-mod/settings/save modification. New native style/color effects still pending;
frozen manifest's NOT_INSTALLED records source handoff, not current installation.

## Verified preceding run and user's choices

The exact predecessor/11 installed hashes match. Archived log shows12 HIDDEN,
12 RESUMING and13 SHOWN,16 SOURCE_BOUND,202 successful LAYOUT records,5 recoverable
EDIT_REJECTED and2 explicit VALUES logs. Initial showing18:25:21.2753563 Moscow →
last showing18:33:33.3413709 (~492.066s); Event loop end18:33:36.2135491.
No IIP FAILED/STOP/CLEANED: editing and repeated return worked in this bounded run,
but no manual STOP/cleanup was exercised before normal host exit. The five rejected
divider-overlap settings did not close the editor. User's frame confirms the
expanded composition/editor coexists with original Screen prompt. This is narrow
runtime evidence, not blanket visual design, native lifetime/GC or performance acceptance.

Final logged/frame values: upper52, lower30, tracking400, outline0, gap7,
dividerY0, length240, opacity1, hint54, gap64. They are reused as the next probe's
starting point, not silently adopted as final design. User requests independent
line thickness (length alone was insufficient), button vertical placement with
a trial row at the divider, and brightness controls for comparison. User explicitly
chooses temporary dimming controls after being told that they also darken the
elements; subsequently asks for independent upper-line brightness as well.

Exact private evidence is owned by the predecessor report. No game frame, font,
texture, material dump or derivative enters public Git.

## Changes and native owners

Same selected Open actor, one World component/RT1024×512/scale.25, separate viewport
editor, untimed reversible presentation and recoverable edit rollback. No renderer,
depth/material/gamma/post-process/global-input change. Source-owned changes are
only Tuning, Composition and HintSource; World/main/resource/panel/input modules
are byte-identical to the tested predecessor.

| Control | Initial / range | Meaning |
| --- | --- | --- |
| Divider length |240 /100–640| Existing horizontal extent |
| Divider thickness |2× /.5–6×| Independent vertical scale of stock ornament; fine.25/coarse.5. Deliberate GPU layout stretch, not a new image asset |
| Button Y from divider |0 /−100–180|0 places button center exactly on divider center; positive down, fine1/coarse4 |
| Button gap from text/line |64 /2–128| Button stays left of the wider lower text/divider, preserving a relative gap |
| Upper brightness |1 /.2–1| Independent neutral RGB multiplier on own upper TextBlock |
| Lower brightness |1 /.2–1| Independent neutral RGB multiplier on own lower TextBlock |
| Divider brightness |1 /.2–1| Own Image RGB only; separate existing opacity control |
| Button brightness |1 /.2–1| Own mirror Image RGB relative to current source color; never mutate borrowed MID/texture |
| Lower outline |0 /0–3| Optional black contour for separation/readability, not a contrast curve or brightness restoration |

Other font/spacing controls retain predecessor ranges. Larger divider weight starts
as an explicitly provisional2×. Upper/divider/lower remain centered on the text
column; divider thickness participates in native slot height and relative row
spacing so increasing weight need not immediately overlap the upper text.
Button height no longer dictates lower-row height; button can move vertically
without dragging the localized action. Own font measurement, fixed RT bounds,
aspect-preserving button size and rejected-edit rollback remain in force.

There are17 parameters. The panel shows a moving9-row window and range label;
Num8/2 selects and automatically scrolls it. It has the same number of visible
lines as before. Chord/NumPad controls unchanged, no automatic save or timer.

### Brightness is an explicit comparison, not a glow fix

Native TextBlock.SetColorAndOpacity(FSlateColor), Image.SetColorAndOpacity
(FLinearColor) and typed FontInfo.SetFont are already source-supported/used seams.
RGB factors apply to own elements only, with native property readbacks; alpha is
held at its baseline, preserving opacity/coverage policy. Default1 leaves intensity
unchanged. Upper and lower font references remain isolated from original TipHUD.

HintSource samples source color into primitive numeric fields, then own brightness
is the final own-color writer after every native source update, even when geometry
is unchanged. Retained mode uses unit baseline; inactive mode uses current child's
color. No multiplicative accumulation from the previously dimmed own Image. Rebind,
device change and hide/resume reapply the stored factor. Shared native resource
parameters and original Image color are never written. Actual UI-material response
and scene appearance still require the next game run.

Direct retained source: base Widget3DPassThrough export is Unlit with Emissive
output; its examined cached parameter metadata exposes SlateUI, TintColorAndOpacity,
BackColor and OpacityFromTexture, no separate per-child glow parameter. All four
elements share this World surface. Upper shadow is explicitly zero, upper outline
was0; engine TextBlock default shadow color is transparent. The visible halo is
therefore **not proved** to be a configurable TextBlock shadow, nor is scene bloom
or halo established as the cause of faded F. Existing tone-mapping/alpha/gamma
uncertainties remain in [visual fidelity](../hint-mirror/VISUAL_FIDELITY.md).

Dimming may reduce halo and also reduce glyph fill brightness. A true contrast
curve that restores fill without affecting halo is not implemented/proved in this
shared pipeline. Lower black outline can improve background separation without
raising emitted fill RGB, but cannot restore the fill's lost brightness. It starts
disabled. No bogus “glow”/“contrast” switch, global bloom command or guessed gamma
compensation is added. Native color values/readbacks are not pixel-equivalence proof.

## Verification and next sufficient run

Full `python tools/test.py`: **318 tests /23 files PASS**. Nine new integration
groups execute actual new modules: independent length/weight, button divider-row
alignment/Y movement,17-field paging, four colors/alpha/original preservation,
retained/device/MID/hidden refresh, inactive current-color/no cumulative dimming,
optional lower outline, bounds rejection and real native color failure cleanup.
Source manifest and byte-identical unchanged seams checked. Raw output ignored
under `.local/world-editor-style-all-tests.txt`. Offline tests do not establish
native style rendering or an improvement to glow/contrast/F fidelity.

After safe exact installation, user launches normally: NumLock on, HildaSoftLight
editor closed; Ctrl+Alt+F11 → one reload → same natural Open. Compare Divider
thickness, Button Y (0=divider line), and each brightness independently, returning
to1 for baseline. Optional Action outline starts0. Num9 logs all17 values;
NumMultiply with panel open exercises the still-pending manual STOP/cleanup for
this candidate. No prior isolated size/material tests required. Visual acceptance
and the independent glow/fidelity question remain open.
