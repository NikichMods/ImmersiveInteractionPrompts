# World editor session — reversible same-target visibility

**2026-11-04: READY_SOURCE / INSTALLED; runtime hide/resume pending. Production BLOCKED.**
Successor to the exact [first editor candidate](../live-editor/README.md),
source `c2e36f90d82540bd3e23f25648e16a54c53699b8`. That source and manifest remain
frozen. This candidate's [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) records all
Lua bytes and external resource hashes; its containing commit identifies source.
VERSION remains initial0.1.0 metadata, no release/main promotion.

**Installation superseded:** previous session source/config retained; own enabled
marker disabled after the [expanded candidate](../live-editor-expanded/README.md)
was installed. The old runtime evidence below remains historical.

## User run — recurring visibility worked; tuning exceeded old canvas

Exact source `dbd1a033be6ee860caf0aef93cb304652c0cbb9d` and11 installed hashes
matched. Native log18:08:30.173 initial SHOWN,18:08:32.902 HIDDEN →18:08:35.137
SHOWN,18:08:37.002 HIDDEN →18:08:37.337 SHOWN; same component, native MID/RTs
refreshed. Device4→1 source rebind completed18:08:43.219. Upper32→36 and lower22→23
were applied through own layout. At18:09:52.4785787 Moscow a new layout exceeded
512×128 and triggered terminal STOP; own native cleanup CLEANED18:09:52.4944528.
4778 yaw writes over~82.305s; no timeout/manual STOP. User reports the panel and
text disappeared; subjective large-font quality/acceptance remains unestablished.
Log SHA256 `e73b3789925ba6de7672c1ade44e7f50d58b369de9e2377f9dacebf939596778`,
ignored runtime-20261104T151437Z. This proves two bounded recurring native
presentation cycles and actual tuning dispatch, not complete lifecycle acceptance.
User explicitly asks to enlarge work area/font ranges; the
[expanded successor](../live-editor-expanded/README.md) also rejects ordinary bad
edits without killing the session. This source remains frozen.

## Authorized installation — 2026-11-04

At16:32:58 Moscow, exact source `dbd1a033be6ee860caf0aef93cb304652c0cbb9d`
installed into new ImmersiveInteractionPromptsWorldSessionProbe with host closed.
Nine Lua installed hashes match source manifest; private config SHA256
`7cfb0566b1142060b309142bba678adcc53ec2041af3955aeec1efda35e55b9b` and own empty
marker verified,11 installed files. Former WorldEditorProbe exact Lua/config remain
unchanged but its own enabled.txt is removed after new payload verification.
All18 earlier IIP probes disabled, only new WorldSession enabled.73 other prior
mod/loader/log and44 config/save files unchanged by hash. The74-file before-baseline
includes the intentionally disabled previous own marker. TTF/PNG/pinned loader
hashes unchanged. Backups/logs and before/installed/verified manifests are ignored
under `.local/research/interaction-prompts/world-space/live-editor-session/install-20261104T133258Z`.
Guarded rollback is outside loader, syntax checked, not executed; it disables new
probe and can restore the exact previous marker after payload/path/closed-host checks.
No game launch/termination, hot reload, other-mod/settings/save change. New native
hide/resume and editing session remain awaiting user run; no runtime PASS claimed.
The manifest's NOT_INSTALLED field records the original source handoff, not current
installed state; frozen source bytes and manifest were not rewritten on installation.

## Observed defect and adopted behavior

The first user run created the composition/editor at16:19:39.047 Moscow. At
16:19:39.991 the original visible-Screen guard failed; the old one-shot harness
cancelled its loop, unregistered hooks, released UI resources, destroyed its own
component and reported CLEANED16:19:40.008. This was not a timeout. The exact
visibility field/movement causing the initial hide is unknown.56 vertical-yaw
writes and current-key audit50 succeeded; user saw the expected inscription
briefly. No tuning input, sustained composition/readability or manual STOP was
demonstrated. See the original report for exact log hash/line references.

User now explicitly requires no time/count test limits and ordinary disappearance
on losing focus followed by reappearance when returning to the **same selected
chest**. Reversible presentation is preferable to allocating another font/texture/
component for each camera turn. No new target resolver or all-action mapping is
needed to close this observed regression.

## Change gate and implementation

READY for research source: own host.Visibility is the presentation owner and
native SetVisibility commits to its Slate host; original Screen component and
widget/retainer/text visibility are read-only inputs. Native object identity,
topology and resource invariants remain fatal. The previous conflation of ordinary
visibility loss with invalid native ownership was the mechanism being corrected.

| State | Native behavior | Next transition |
| --- | --- | --- |
| Warming | Own host Hidden; measure own text, obtain three fresh native hint samples over frame boundaries | Hint ready → shown |
| Shown | Own host HitTestInvisible; same depth/material/anchor/scale and world-Z frame-Yaw | Source hidden/faded/not screen-added → hidden |
| Hidden | Own host Collapsed; borrowed hint reference cleared, private font/ornament and same component retained; editor remains usable | Same valid target visible again → warming |
| Stopped | Loop inert/cancelled, independent resource/host/component cleanup; explicit retry if incomplete | Terminal; no automatic reconstruction |

Both focus loss and ordinary opacity fades in original widget/text/hint ancestry
are presentation states. Moving outside the already verified80–1500 distance
envelope hides until returning; it does not expand distance/render support.
The current selected Open remains the native identity anchor. Other Open CanShow
callbacks do not terminate it; they are not automatically decorated by this
same-target candidate. Destroyed/replaced actor/widget/tree/root/camera, semantic
action change, moved fixed anchor, unsupported resource/geometry, setter/input
failures still stop safely. Map travel/new actor binding is not asserted supported.

No45s World/120s acquisition timer,12000 frame/4096 show/128 init/8 Open or hint
source-change test ceiling remains. No timer is registered. Counters are diagnostic
only. Pending initialization records are pruned when new Open actors arrive;
acquisition hook is released after selecting one target. Structural ancestry,
finite-value, ownership and fixed-RT/layout bounds remain. The exact asset loader
still refuses repeated failed loads; this is failure containment, not a test timer.

Source modules for resources, panel, tuning, input audit and keyboard inventory
are byte-identical to the predecessor. Changed code is confined to main lifecycle,
World presentation, hint visibility/pause and the composition pause seam. Only
source/owned setters are used, no original TipHUD setters, focus/bindings/save
changes, gamma/tint/material guessing or native hook return overrides.

Editor keys unchanged: Ctrl+Alt+F11 arm/toggle, Num8/2 select, Num4/6 adjust,
Num5 step, Num7 reset, Num9 values to log only, Num0 close, NumMultiply STOP;
Num1/3 reserved. NumPad inactive with panel closed. NumLock on and HildaSoftLight
editor closed. While the World text is hidden, edits are retained and applied on
return to the target; the independent panel stays available for log/close/STOP.
No automatic save, no settings file output.

## Verification and next sufficient test

`tests/test_world_editor_session.py`:11 regression groups execute the new actual
main/World/composition/hint/panel/input code against existing host fixtures.
Cover same-instance hide/resume and preserved values/resources, opacity/retainer/
text/component fades, hidden editing/close/reopen, other-target callback, distance
excursion, removed timer/callback/source ceilings, fresh-hint warmup, terminal
identity/source errors, STOP while hidden, cleanup retry and inert retired callback.
The old source/resource tests remain unchanged and pass; a byte-equality assertion
ties the reused resource/panel modules to that tested predecessor.
Full `python tools/test.py`: **301 tests /21 files PASS**. Raw output remains ignored
under `.local/world-editor-session-all-tests.txt`. Offline models do not prove
native recurring visibility, rendering, real input or GC/travel acceptance.

After authorized safe closed-host installation, user launches normally:

1. NumLock on, HildaSoftLight editor closed. Ctrl+Alt+F11, one manual reload,
   approach one natural chest/Open. Original Screen prompt stays visible.
2. Turn away/leave its focus, then return to that **same chest** repeatedly;
   World text must disappear/reappear while the editor remains available.
3. Tune at a comfortable pace; no timer/count deadline. Num9 records current
   values. Num0 closes; Ctrl+Alt+F11 reopens without resetting values.
4. NumMultiply with editor open performs full cleanup. If source/context becomes
   invalid instead, record the specific failure; do not silently retry a broken
   native boundary. Tools collect/archive local logs afterward.

No isolated font, size1.0→1.5 or Masked→Translucent experiment is required.
This gate is repeated presentation and practical tuning, not production acceptance.
