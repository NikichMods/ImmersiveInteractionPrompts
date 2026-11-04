# Expanded World editor — large fonts and rejected-edit rollback

**2026-11-04: READY_SOURCE / INSTALLED, native expanded rendering pending; production BLOCKED.**
Successor to [untimed session](../live-editor-session/README.md), exact predecessor
source `dbd1a033be6ee860caf0aef93cb304652c0cbb9d`. Prior sources stay frozen.
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) pins9 Lua files and config example;
the commit containing it is the source identity. VERSION unchanged, no release.

**Installation superseded:** this exact source/config is retained, its own marker
disabled and the [Style editor](../live-editor-style/README.md) installed. New
style/color behavior remains unaccepted; prior runtime evidence is preserved.

## User run — large-font editing / recurring presentation passed narrowly

Source `19d35a5a0238a3b228f7058bfcd7234e647ede7e` and11 installed hashes match.
2026-11-04 Moscow: first SHOWN18:25:21.2753563 → last SHOWN18:33:33.3413709,
~492.066s.12 hidden/resume returns,13 shown,16 native source binds,202 LAYOUT,
5 EDIT_REJECTED and2 Num9 VALUES. No IIP FAILED/STOP/CLEANED. Overlap edits reverted
without stopping; fonts/parameters applied and preserved across repeated focus
return. User's frame shows expanded composition/editor and original Screen prompt.
Host exited normally18:33:36.2135491; explicit manual STOP/cleanup remains untested
in this run. No overall aesthetic/performance/full-lifecycle acceptance inferred.
Last values52/30, tracking400, outline0, gap7, dividerY0/length240/opacity1,
hint54/gap64. User requests thickness/button-Y and appearance comparison controls;
[next style candidate](../live-editor-style/README.md) owns that change.

Archived privately: log SHA256
`348f4fbb397aef22a90efd4cc086d52aaa760ca95ded3a27c7d68a86ef8f8e78`,
user PNG SHA256 `64fe50595fbc7eedeabcc7fa6d32ddf93034324dbbba66ca96727c2307cdb547`,
ignored runtime-20261104T153816Z. No raw frame distributed.

## Authorized installation — 2026-11-04

At18:21:59 Moscow, exact source `19d35a5a0238a3b228f7058bfcd7234e647ede7e`
installed into new ImmersiveInteractionPromptsWorldExpandedProbe with host closed.
Nine authored Lua match source manifest; private config SHA256
`7cfb0566b1142060b309142bba678adcc53ec2041af3955aeec1efda35e55b9b` and empty
own enabled marker verified,11 installed files. Former WorldSession source/config
retained unchanged, its verified own marker disabled after new payload verification.
All19 older IIP probes disabled; only new Expanded enabled.83 other preexisting
mod/loader/log files and45 config/save files hash-preserved;84-file baseline includes
intentionally removed own marker. Pinned loader and external resource hashes match.
Private before/installed/verified manifests, pretest logs, backups and guarded
rollback are ignored under
`.local/research/interaction-prompts/world-space/live-editor-expanded/install-20261104T152159Z`.
Rollback syntax checked, not executed. No game launch/termination, hot reload,
other-mod/settings/save change. Expanded native RT/font rendering/fit rejection
still pending user run. Frozen manifest's NOT_INSTALLED records the source handoff;
installation did not rewrite the source/manifest bytes.

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
