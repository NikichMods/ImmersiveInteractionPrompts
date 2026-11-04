# World prompt + live editor — source-only research candidate

**2026-11-04: source READY_SOURCE; authorized installation PASS / RUNTIME_PENDING. Production BLOCKED.**
One candidate on `research/interaction-prompts-owner`, based on
`9d8ad982a680d275a80c1ead0005fb0dbe6a9581`. Exact source bytes and external resource
identities: [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json). The commit containing
that manifest is the candidate's Git identity; VERSION remains 0.1.0 metadata.
The frozen manifest describes the original source-only handoff; the subsequent
authorized installation is recorded below. No release or runtime acceptance exists.

**Superseded installation:** after this run the exact old source was retained,
its marker disabled and the [untimed session successor](../live-editor-session/README.md)
installed. Its repeated native hide/resume remains runtime-pending.

## First user run — brief appearance, one-shot visibility stop, 2026-11-04

Exact installed source `c2e36f90d82540bd3e23f25648e16a54c53699b8` and11 installed
hashes match. User reports the expected inscription appeared briefly then vanished
and could not return. Log lines889–904: original visible-Screen guard failed
16:19:39.9911388 Moscow, approximately0.944s after composition creation; not45s
or120s timeout. Loop cancellation, resource release, native component destruction
and CLEANED16:19:40.0084476 all completed without cleanup failure.56 frame-Yaw
writes, layout/import/private font donor check and editor/current50-key audit
were reached. No actual tuning actions/manual STOP or sustained rendering accepted.
Exact field/camera movement behind the visibility change is not established.
Archived log SHA256 `90a5b5bc868b0610aae77afc96655406fb50dc56688544872cf671f0db847e83`,
ignored `.local/research/interaction-prompts/world-space/live-editor/runtime-20261104T132320Z`.
The one-shot STOP policy explains why later refocus could not recreate the prompt.
User adopts an unlimited same-target session with reversible hide/show;
[successor source and verification](../live-editor-session/README.md). Original
source/manifest below are frozen history, not a claim that its behavior was accepted.

## Authorized installation — 2026-11-04

At16:08:49 Moscow, with host verified absent, exact source
`c2e36f90d82540bd3e23f25648e16a54c53699b8` was installed under the new
`ImmersiveInteractionPromptsWorldEditorProbe`. Nine Lua source/installed hashes
match SOURCE_MANIFEST; private IIPLiveConfig.lua SHA256
`7cfb0566b1142060b309142bba678adcc53ec2041af3955aeec1efda35e55b9b` plus empty
enabled.txt verified,11 files total.17 older IIP probes stay disabled.
Existing63 mod/loader/log files and42 config/save files were backed up and
hash-preserved; mods.txt/other mods/pinned loader unchanged. TTF/PNG match
manifest hashes and remain external. Private pretest logs, backups, before/installed/
verified manifests and guarded rollback are under ignored
`.local/research/interaction-prompts/world-space/live-editor/install-20261104T130849Z`.
Rollback syntax passed; not executed. It disables only this exact own marker with
closed-host/path/hash checks, retaining source files. No game launch/termination,
hot reload, source/guard/deadline or save/settings changes. Runtime pending.

Next: user launches normally, NumLock on and HildaSoftLight editor closed;
Ctrl+Alt+F11 → one manual reload → approach natural Open → tune/log/close/reopen →
NumMultiply before the retained45s timeout. The numbered procedure below is the
prepared user-run scenario, now authorized for this installed exact source.

## Question and sufficient result

Can the already demonstrated private World renderer, Aphes font, stock ornament,
localized display-value read and native hint mirror form one isolated four-child
composition, with temporary live controls? Source inspection and offline assembly
tests establish a reviewable integration candidate. The combined World rendering,
clipping, controls and cleanup still require one separately authorized user run.
This replaces the earlier composition source blocker with source readiness; it
does not close the unresolved pale/blue native-hint fidelity question.

## Ownership / final writers / preserved behavior

| Surface | Owning writer and consumer | Boundary |
| --- | --- | --- |
| World host | Existing separate PostionItemUMG instance/tree and World WidgetComponent; configure before FinishAddComponent, native scene renderer afterward | RT512×128, scale.25, anchor+32Z, fixed world position, stock Masked/depth material. Original Screen component untouched |
| Upper | Private transient Template UFont; checked distinct storage and unchanged donor. Own TextBlock.FontObject holds it; SetFont updates STextBlock | Technical `OPEN`, not a verified Aphes translation. White, outline0, tracking150, size32 initially |
| Divider | One local stock570×16 PNG import; own Image.Brush holds transient Texture2D | No PNG/font/derivative distributed, no shared-resource setter |
| Lower | Same selected original TextBlock_89.GetText display value → own SetText | Refresh every frame; no RU replacement or separate localization table. UE4SS copied FText history is not claimed preserved |
| Native hint | Existing original retainer effect MID/Icon RT, or accepted inactive-retainer child Brush route → own Image | Read-only borrowed resource; no second Retainer, GetDynamicMaterial or parameter writes. Missing/unsupported source fails closed |
| Layout | IIPComposition exclusively writes its four CanvasPanelSlots and own FontInfo/Image opacity | Hint source changes cannot overwrite tuned size; native aspect ratio retained. Own ForceLayoutPrepass/GetDesiredSize; no original prepass or layout writes |
| Editor | Second independent viewport host, own label; AddToViewport/RemoveFromParent | No gameplay HUD child insertion, focus change, input-mode call, binding replacement or save write |

World binding remains the previously proved bounded **natural Open / Interact25**
join, not a new all-action mapper. Localized Open display values may refresh;
changing the actor's semantic action, owner, original visibility, root/anchor or
known alternative visible Open stops the one-shot candidate. No automatic retarget.
The frame-Yaw setter retains Pitch=Roll=0, no1° threshold or interpolation;
degenerate horizontal direction retains last valid yaw after creation.

## Native setters and source evidence

Reuses exact evidence in [font](../../aphes-text/README.md),
[ornament](../../composition/README.md), [World](../probe/deferred/README.md),
[Yaw](../vertical-yaw/README.md), [hint](../hint-mirror/README.md), and
[composition review](../composition/README.md). No closed size/material experiments
were repeated. Shared Research R-006/R-007/R-012/R-014/R-016/R-017 and R-008 timer
contracts were consulted; this change adds mod-specific integration, no new
cross-project runtime fact.

Installed UHT: `UMG/Public/TextBlock.h`89/98 SetFont/GetText;
`SlateCore/Public/SlateFontInfo.h` FontObject/Size/LetterSpacing/OutlineSettings;
`FontOutlineSettings.h` OutlineSize/OutlineColor/OutlineMaterial;
`CanvasPanelSlot.h`29/32 SetSize/SetPosition; `Image.h`50 opacity;
`Widget.h`277 ForceLayoutPrepass; `UserWidget.h`396 AddToViewport;
`Engine/Public/PlayerController.h`371 IsInputKeyDown(FKey) const.
The existing locally retained UE4.27 source `TextBlock.cpp`94–100 copies FontInfo
and calls live STextBlock.SetFont. SlateFontInfo.h documents tracking and size
limits. Native setters, not raw FontInfo writes alone, commit live font changes.
CanvasPanelSlot setters update Slate offsets as already established by the size
research. Panel follows the existing independent viewport-host route, also used
by the installed HildaSoftLight editor. Local evidence hashes are retained in the
ignored source-audit record; no host headers/dumps were copied into public Git.

## Controls and bounded parameters

`Ctrl+Alt+F11` first arms acquisition; after the one manual reload and natural Open
selection, the composition and editor appear. Further chord presses close/reopen
the panel without removing the composition. A second press while still waiting
cancels acquisition. After STOP the chord only retries incomplete cleanup.

With panel open and **NumLock on**: Num8/2 previous/next; Num4/6 decrease/increase;
Num5 fine/coarse; Num7 reset selected; Num9 log all values; Num0 close;
NumMultiply full STOP; Num1/3 reserved. The panel displays this legend and values.
Opening seeds held keys; no held-key repeat. Control/Alt/Shift suppress editing.
Closed panel does not poll NumPad or change settings. Values stay in session
memory across close/reopen; **no settings file is written**, including on close.

| Parameter | Initial | Range | Fine / coarse |
| --- | --- | --- | --- |
| Upper font |32|20–44|1 /2|
| Lower font |22|16–30|1 /2|
| Upper tracking |150|0–400|10 /50|
| Upper outline |0|0–3|1 /1|
| Vertical gaps |8|2–16|1 /4|
| Divider relative Y (+down) |0|−6–6|1 /2|
| Divider width |200|100–280|2 /10|
| Divider opacity |1|0–1|.05 /.2|
| Hint height |38|24–64|1 /4|
| Hint-to-action gap |8|2–24|1 /4|

Numbers are provisional research settings, not adopted design. Position/extent
values use UMG layout units, not projected screen pixels; tracking uses native
font spacing units. Both lines/divider share X256; the hint sits to the lower
text's left, excluded from its center axis. Divider keeps stock aspect ratio.
Actual own text desired sizes plus outline padding determine relative rows.
Zero/unmeasured, multiline, long/oversized text, unsupported hint aspect, overlap
or exceeding the four-unit RT margin **stops and cleans**, rather than silently
clipping/scaling/localizing differently. Individual ranges do not guarantee that
every combination fits the fixed RT. Reopening does not reset the safety deadline.

### Input applicability / conflicts

UE4.27 InputCoreTypes.cpp88–99/608–619 defines NumPadZero…Nine/Multiply names;
the installed HildaSoftLight source uses the same FKey.KeyName/native held polling.
IIP polls from its existing one-frame EngineTick loop only while editing, detects
up→down edges and seeds on open. It does not rely on frame-scoped JustPressed
values sampled on a slower timer. Only the F11 chord uses one UE4SS key callback
which queues EngineTick; no native UObject operations run on its input thread.

Source review of installed scripts found HildaSoftLight bare-NumPad polling and
Ctrl+Alt+F10, old disabled IIP probes, and no new IIP F6/F12/AltF9 bindings.
This is not a live registry certification. At activation/opening, candidate checks
the F11 chord registry, bare NumPad registry, required polling seam, and all50
current keyboard action mappings through GameGlobal.GetKeyByVirtualKey using the
retained authored virtual-ID inventory. Collision, registry exception or unavailable
getter fails closed, including the previously unexplained registry-error case.
Saved current FKeys cannot be read offline through these APIs; this runtime audit
has not run for the new candidate. It does not mutate bindings or settings.
Raw polling by another mod is invisible to the registry: **close the HildaSoftLight
editor first; simultaneous editors are unsupported**. No cross-mod state added.

## Containment, cleanup and evidence

Original acquisition8 candidates/128 initializations/4096 show callbacks,
120s outer deadline,45s World deadline and12000 frame callbacks are retained.
The frame loop gates native validity/ownership/current source; full topology is
checked every12 frames. Changing text/parameters triggers only own prepass/layout;
no repeated asset loads/import, broad per-frame discovery or per-frame log dump.

STOP makes hooks/loop inert, cancels the delayed loop, hides both own hosts,
releases borrowed hint/ornament brushes and private font via the own stock-font
carrier, detaches owned children, then unbinds/destroys only the own component and
releases hosts. Independent releases are attempted even after one failure.
Incomplete resource release keeps hidden native holders and primitive identities
for explicit Ctrl+Alt+F11 cleanup retry; it never destroys the only retry carrier.
No forced GC, original restoration writes, save edit or automatic host control.

Offline checks: `tests/test_world_live_editor.py` executes actual main, World,
composition, panel, input audit, tuning and hint modules against host mocks;
`tests/test_live_resources.py` exercises the actual extracted private-font/import
module using existing independent fixtures. Full `python tools/test.py` is the
integration gate. Exact counts/results are summarized in docs/VERIFIED_RUNTIME.md;
full output remains ignored under `.local/live-editor-all-tests.txt`.
These tests establish source policy and mocked integration, **not native Slate
measurement, rendering, keyboard capture, GC or visual acceptance**.

## User-run scenario for the installed candidate

The authorized installation is complete as recorded above. The user launches the
game; no agent launch/termination/hot reload was performed. Older IIP probes remain disabled.

1. With HildaSoftLight editor closed and NumLock on, Ctrl+Alt+F11, one manual
   reload, approach one natural Open. Original Screen prompt must remain visible;
   expect four World elements plus independent screen editor.
2. Within the retained45s budget, Num6 changes upper size, Num7 resets it;
   Num2 selects lower size, Num6 changes it; Num9 records settings.
   Num0 closes; Num6 must do nothing; Ctrl+Alt+F11 reopens. A held Num6 at reopening
   must wait for release and a new press.
3. If readily available within the same budget, switch keyboard→controller→keyboard;
   both prompts must show current native glyph content. Existing pale/blue output
   is recorded, not corrected by guessing. An already remapped Interact may be
   observed; do not change settings for this test.
4. NumMultiply with panel open: editor and own World prompt disappear, native
   Screen prompt still works; expect LOOP_CANCELLED, RELEASED, COMPONENT_DESTROYED,
   CLEANED. Log/frames are archived locally by tools afterward. Timeout or natural
   source hide can stop earlier; report exactly which paths were actually reached.

This run checks the combined path; it need not repeat isolated World/size/material
experiments. Wider types/languages/travel/GC/performance and final design remain
separate production gates.45s may limit tuning; increasing that budget is not part
of this candidate and needs a reasoned follow-up, not an invisible timeout change.
