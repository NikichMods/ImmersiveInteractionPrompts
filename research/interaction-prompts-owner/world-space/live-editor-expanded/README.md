# Expanded World editor — large fonts and rejected-edit rollback

**2026-11-04: READY_SOURCE, native expanded rendering pending; production BLOCKED.**
Successor to [untimed session](../live-editor-session/README.md), exact predecessor
source `dbd1a033be6ee860caf0aef93cb304652c0cbb9d`. Prior sources stay frozen.
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) pins9 Lua files and config example;
the commit containing it is the source identity. VERSION unchanged, no release.

## Observed failure and user's decision

The predecessor log demonstrates initial showing, two hide→resume→shown cycles
using the same World component, refreshed native MID/RTs and device4→1. It then
accepted upper font32→36 and lower22→23. Next layout failed with
`composition exceeds 512x128` at18:09:52.4785787 Moscow, about82.305s after initial
show.4778 yaw writes; loop/resource/native cleanup completed18:09:52.4944528.
No timeout or manual STOP caused that event. User reports panel/text disappeared;
sustained visual quality and full control acceptance are not inferred from logs.
[Predecessor report](../live-editor-session/README.md) owns exact archived evidence.

User explicitly requests a larger work area and larger possible fonts because
the current text is too small. Merely rejecting oversized settings cannot fulfill
that request. Chosen change: enlarge the existing own renderer before native
registration, widen parameter ranges, and make expected edit overflow reversible.
No native hook/layout replacement, distance scaling or material compensation.

## Mechanism and bounds

Own DrawSize/RT **1024×512** replaces512×128; component scale stays.25, pivot.5,
world anchor+32Z and frame-Z-Yaw unchanged. Native SetDrawSize is the existing
pre-registration seam; native registration/renderer allocates the larger target.
Own draw/current-draw/RT readbacks now require1024×512. Render-target area is8×;
actual performance and new clipping/rendering remain user-run checks.

Horizontal axis is width/2. Vertical coordinates add `(512−128)/2=192` layout
units, so identical settings and measured text extents have the same coordinates
relative to the physical component pivot as before. The canvas expansion alone
does not move the inscription in world space. Larger fonts naturally enlarge the
composition; the initial research values are now **48 upper /28 lower**, not an
accepted final design. Upper slot spans the enlarged work area while centering
actual glyphs on the same axis. Native Image/material resources and tint unchanged.

| Parameter | Initial | Range | Fine / coarse |
| --- | --- | --- | --- |
| Upper font |48|20–96|1 /4|
| Lower font |28|16–64|1 /4|
| Upper tracking |150|0–400|10 /50|
| Outline |0|0–3|1 /1|
| Vertical gaps |8|2–48|1 /4|
| Divider Y |0|−32–32|1 /4|
| Divider width |200|100–640|2 /20|
| Divider opacity |1|0–1|.05 /.2|
| Hint height |38|24–128|1 /8|
| Hint gap |8|2–64|1 /4|

All geometry uses existing native layout units, not projected pixels. Fixed four-
unit render margins and aspect ratios remain; not every combination must fit.
Actual font sizes are measured by own ForceLayoutPrepass/GetDesiredSize.

## Edit transaction / final writer / failure containment

Only expected **fit failures during an explicit edit against the same known
content** are recoverable. Tuning.plan returns a fit reason rather than throwing
for ordinary width/height/overlap. Before native slot/opacity writes, own FontInfo
is applied/measured; the previous successful10-value tuning snapshot is retained.
If the proposed layout does not fit, restore that snapshot, call the same native
SetFont setters and prepass, verify the restored plan, then apply its valid slots.
The panel shows `Does not fit: previous values restored`; EDIT_REJECTED logs
requested/restored values. Panel, component, resources and frame loop remain active.
Selection and fine/coarse mode are retained. Pending hidden edits are checked on
return; their last validated set can be restored together.

This does not catch arbitrary exceptions or suppress native failures. Invalid/
zero/non-finite measurement, changed text/resource geometry that cannot fit,
missing prior valid state, ownership/setter/readback failure or failed rollback
still use terminal STOP/cleanup. No partially uncertain native layout is allowed
to continue. Original TipHUD is never edited or used as a rollback destination.
FText/history limits and Open-only selected actor scope remain unchanged.

Renderer configuration, own style setters, slot setters and existing native
consumers are the same as prior candidates; changes are their owned data/ranges
and the explicit fit-rejection policy. Resource/panel/input/hint/main modules
are byte-identical to the session candidate. No production acceptance is inferred.

## Verification and next user run

Full `python tools/test.py`: **309 tests /22 files PASS**, including8 actual new
integration/geometry tests for native DrawSize configuration, fonts beyond old
limit, physical coordinate rebasing, expected rejection/rollback and continued
editing, hidden edits/resume, actual native/measurement/rollback failure cleanup,
source manifest and unchanged seams. Shared resource/lifecycle tests still pass.
Raw logs ignored under `.local/world-editor-expanded-all-tests.txt`. Mocks do not
establish actual larger-RT allocation/rendering, native font metrics or performance.

After exact authorized closed-host installation, user launches normally:

1. NumLock on, HildaSoftLight editor closed; Ctrl+Alt+F11 → one reload → same
   natural Open. Original Screen prompt remains visible.
2. Num5 toggles coarse step; Num6 increases upper font by4. Num2 selects lower;
   Num6 increases it by4. Adjust comfortably without a test timer.
3. Check larger text, divider/button layout and ordinary focus-away/return.
   A fit-limit warning must retain working panel/text and last valid values.
4. Num9 logs current values; NumMultiply with editor open performs full STOP.
   Native errors remain failures for diagnosis, not a reason to guess tint/gamma.

No old size1.0→1.5 or material A/B repetition, no native keymap/settings/save edit,
no automatic file save, no game launch/termination/hot reload by the agent.
