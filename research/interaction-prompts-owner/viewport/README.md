# Fixed screen-position research prototype — 2026-10-29

**Screen placement/render/manual cleanup PASS in one bounded run. User selected
50%/78% as the continuing baseline. Arrow tuning NOT_PASSED; reset/commit keys
unverified. Probe disabled. Production BLOCKED.** Prior native Aphes/font,
ornament and TipHUD-child results are reused, not reopened.

## User-run result and adopted position — 2026-10-29

The user reports the procedure worked except arrow movement: arrows moved the
camera and the sample did not move. They explicitly prefer the displayed initial
position and choose it for further work. Preserve **X50%, Y78%, HUD-root normalized
point anchors**, alignment(.5,.5), own Canvas320×132; sample text axis is X160,
upperY0, ornamentY48, lower-row centerY76, debug indicatorY112. Removing the debug
indicator must not silently resize/recenter the composition and shift its accepted
visual position. This is a selected baseline at2560×1440, not multi-resolution,
UI-scale or production-lifecycle acceptance. Exact viewport pixel mapping remains
bounded by the native HUD-root geometry, not inferred for every aspect ratio.

The one2560×1440 user frame shows both the untouched world-relative stock prompt
and a separate lower-screen sample with native Aphes, ornament, copied current F
hint/localized action on one baseline, and TEST X=50% Y=78%. The user's report
supports the screen-position/camera check; a single still alone cannot prove
stability across motion. The position was chosen explicitly in chat, **not** by
pretending the F7 commit action succeeded.

| Log lines / Moscow time | Observation |
| --- | --- |
| 726 /02:28:05.067 | F6 arms the one Open snapshot |
| 727–734 /02:28:05.102–.126 | One PNG import/bind, private font bind/donor unchanged; initial POSITION50,78, viewport2560×1440; five own children plus one Canvas attached |
| 735–743 /02:30:43.515 | coords removed, font released/upper removed, both image brushes released/images removed, lower removed; CLEANED reason=user remaining0 |

Manual cleanup completed≈158.45s after arming, before180s timeout. CLEANED also
requires successful empty own-Canvas detachment in this exact source. No probe
FAILED/CLEANUP_FAILED events. No POSITION move/reset/commit events exist in the
retained run. Arrow tuning therefore did not pass; reset/Home and F7 logging
are not runtime-verified. Native key consumption/routing/modifier recognition is
**not diagnosed** by missing log lines. Do not call the symptom a proven interception
cause or retry/fix controls merely to recover a position already chosen by the user.
No new payload/control revision or extra game test was prepared for that symptom.

Exact installed source/helper/config, TTF/PNG/DLL and18 previous mod/loader files
matched the installation manifest after exit. Host absent; only own enabled.txt
removed, all scripts/private config and guarded rollback retained. No agent
launch/termination/hot reload/settings/save/other-mod changes. Post-gameplay
config/save byte identity is not asserted. Partial cleanup fault paths/GC/map
travel, live remapping/device changes and dynamic target/lower-text synchronization
remain outside this result. Final styling is not blanket accepted by the position choice.

Local raw archive `.local/research/interaction-prompts/screen-space/runtime-20261028T233241Z`:
log SHA256 `1f2f787adc0d82bfcdc005981c6ed513c0b218dafb90eb1bdefc0c37bdeb3096`;
frame SHA256 `f49ecdafb7d1b635fa8f36b57704c4d1497bc0051ca052ba36b38f3f1daa2b07`.
User frame/host resources/log remain local; no raw proprietary assets in Git.
Next useful scope is synchronizing one screen-space Open prompt with native
show/hide/current-target state while retaining the stock prompt for comparison;
this requires its own bounded design/readiness, not automatic production work.

## Authorized installation — 2026-10-29

Exact source `242a5f0a6f5807dd4cdc3953f1f51acc02b0be06` installed at01:42 Moscow
with host closed. New UE4SS mod folder `ImmersiveInteractionPromptsViewportProbe`,
previously absent: main.lua, IIPPosition.lua, private IIPViewportConfig.lua and
empty enabled.txt. No overwrite of accepted/previous probe source. All older
IIP probes remain disabled. Source hashes below matched installed bytes;
config SHA256 `baf73b46c7cd284737304e9f20ada0464afc9eae8ae3f0cd174ea5e5490e43bc`.
TTF443fcae9..., PNG901b7260... and pinned DLLce5e3c46... matched prior identities.
TTF/PNG remain outside the game; loader/global config and other mods unchanged.

Rollback/pretest log/settings/mods.txt and before/installed manifests stay ignored
under `.local/research/interaction-prompts/screen-space/install-20261028T224203Z`.
Guarded rollback checks closed host, exact target/hashes and unexpected files,
then restores its prior absent state.18 previous mod/loader files and56 current
config/save files hash-identical at installation. This does not claim byte
preservation after later natural gameplay. The agent did not launch/close the
host or hot reload. Await user controls/result, not another installation approval.

## Question, recovered baseline and selected mechanism

Goal: a compact sample stays in the lower screen while the world target/camera
moves; user tunes X/Y live. Original TipHUD remains visible/unmodified. This
stage does not select/hide/update all interaction types or own production lifecycle.
Checkout was clean, one worktree, research branch at17c2080b4baa7dfca09f18fdbd9d1e64406720cd;
Research mainbea384a6ba5cfb6ca19f50ac29987107538bb107 and fresh remotes matched.
DevRules origin/main0f4888bb9501afa42e3b9492c5794c98bf58537f was checked and reused.
No unpublished work replaced; no VERSION/main/other-mod runtime changes.

### The current prompt is screen-space, but world-positioned

Retained actual UHT `Genesis/Private/ExtendedWidgetComponent.cpp` constructor
contains `Space=EWidgetSpace::Screen`; base UMG WidgetComponent default is World.
These generated **constructor assignments** are reflected CDO values: pinned
UEHeaderGenerator.cpp789ff reads GetClassDefaultObject and compares parent values.
The generated empty gameplay method bodies/placeholder returns are not native code.
BaseGameEventObject_BP's ExtendedWidget component template supplies TipHUD class,
activation and DrawSize1000×1000, with no serialized Space override. Thus this
baseline inherits Screen; live/placed overrides were not read in this step.

UE4.27 WidgetComponent registers screen components in FWorldWidgetScreenLayer;
SWorldWidgetScreenLayer.cpp92–145 projects SceneComponent.GetComponentLocation
through the local player's projection, then converts viewport position to layer
coordinates. Screen-space here is not a fixed viewport coordinate. Native
Genesis SetArrayData/SetShow internals and the exact live component transform
writer remain unknown. No need to resolve those writers for a separate sample.

### Comparison

| Route | Evidence / complexity | Behavior preservation / maintenance decision |
| --- | --- | --- |
| Move existing TipHUD/component | Component already Screen; position projected from scene component. Fixed-position override would fight its owner or require reparenting the live widget | Changes the original prompt and ownership; not selected |
| New standalone viewport UserWidget | Actual UHT has WidgetBlueprintLibrary.Create(WorldContextObject, TSubclassOf<UserWidget>, OwningPlayer), AddToViewport/AddToPlayerScreen, normalized-anchor/position methods. UE4.27 Initialize creates WidgetTree and viewport owns the Slate layer | UUserWidget itself is Abstract and ValidateUserWidgetClass rejects it. Game ExtendedUserWidget is concrete but native initialization callbacks are not fully known; reusing a game Blueprint would also execute its construct graph. No bypass of Initialize/abstract checks, no native bridge/new cooked BP for this test |
| **Own Canvas under existing viewport HUD root** | Existing CombatHUD/R-004/005 already find in-viewport HUDMainUMG_BP_C and validate gameplay pawn. Saved root is Canvas Main_Panel. AddChildToCanvas uses existing proven native primitive attachment; no new UserWidget construction | **Selected minimum.** Add one owned subtree, move only its slot anchors, delete only that subtree. Borrows host visibility/DPI/lifetime; desktop/fullscreen-root assumptions guarded. Broader HUD lifecycle still unaccepted |
| Coherent HTML | Actual UHT includes CreateJSEvent/AddString/AddBool/TriggerJSEvent and readiness APIs; Html has genesis-input-direction controls. But ShowTipMessage/HideTipMessage bindings2678–2686 and TipMessage DOM5987ff are commented out; no active native TipHUD→current action/input bridge was established in these bounded inputs | Possible custom event bridge, not impossible. Would need payload/target/hide/input synchronization, document readiness and compatible common Hud.html patch; this overlaps other Coherent mods. More new seams than the selected root Canvas. CSS convenience does not remove state ownership |

No global object/actor inventory, frame monitor, new native observer or game run
was used. A one-time class-scoped FindAllOf(HUDMainUMG_BP_C), already used by
CombatHUD, returns a Lua table in LuaMod.cpp1398ff; this is not a TArray out-param
or array-resize path. Count limit8; require exactly one matching in-viewport HUD
with GenesisCharacter-derived owning pawn. Wrong-map DefaultPawn is rejected.

## Prototype and evidence boundaries

[Scripts/main.lua](Scripts/main.lua), [IIPPosition.lua](Scripts/IIPPosition.lua).
One post-only CanShow hook waits for a naturally visible RU Open, reads its
font/localized display text and actual RetainerBox child Image brush. It then
becomes inert. This is one snapshot sample, not a continuing interaction observer.
The sample deliberately remains while walking away from the chest, until user
cleanup or180s timeout. It is not presented as a valid live action prompt.

The existing HUD must have stretched viewport anchors0,0→1,1, zero viewport
alignment and identity RenderTransform; its WidgetTree.RootWidget must be exact
Canvas Main_Panel with identity transform. On controls, viewport presence,
transforms and stretch are rechecked. No original child/root/slot properties are
set. Add one own transient Canvas320×132 to this root; fixed size, centered
alignment, zero offsets, point anchors initially(.50,.78), own z-order100.

Coordinates denote that Canvas center (upper/lower text horizontal axis at its
center); they are integer percentages of the **HUD root**, expected to cover the
viewport under the stock stretched-host layout. Hidden native viewport margins
are not reflected/read; exact viewport-pixel correspondence remains a runtime
check, not a claim derived from a cached desired size or opaque FGeometry.
No GetCachedGeometry conversion or DPI guessing is used. Anchor percentages
are DPI-independent relative to the parent. Viewport dimensions are logged
through the exact UHT WidgetLayoutLibrary.GetViewportSize static function/CDO.

Five own children: Aphes OPEN28/LetterSpacing150/outline0/shadow0; stock-font
localized snapshot22 with original outline; copied current Image hint on the
same Y as lower text; one local stock ornament200×6 between rows; temporary
coordinate indicator. Hint FSlateBrush is a native value copy retaining the
current resource (possibly MID), with no material-parameter writes. It is not
reconstructed from a hard-coded F/keymap; whole hint/device changes are not
synchronized after the snapshot. Original input hints, arrays and action untouched.
No externally shared font/resource contents are mutated. Font/PNG paths and
assets remain local; no proprietary image/font enters public Git.

Own widget references come from the HUD's native panel/tree and own font/brush
properties, not Lua wrapper retention or Outer alone. Cleanup hides the own
Canvas, releases upper Font via the own lower FontInfo carrier, detaches each
own child and clears image resources, then removes the empty own Canvas. Partial
release failure keeps the hidden Canvas and lower carrier attached for explicit
retry. Primitive path/address/class records guard every future lookup; no GC
forcing, raw offsets, roots, owner-array edits or original UI restoration needed.
No input mode/focus, actor location, loader/game settings or save write calls.

### Controls for the future user-run test

All keys use **Ctrl+Alt**:

- **F6**: arm at one Open prompt; after attachment, clean up. One creation attempt
  per game session, including failures; no rearm/reimport after successful cleanup.
- **Arrow keys**:1 percentage-point X/Y steps, bounded10–90%.
- **Home**: reset50%,78%.
- **F7**: structured POSITION action=commit log, including percentages and viewport
  size. No config/save is written. Every move/reset also logs its value.
- Timeout180s from arming: cleanup. Original TipHUD is unaffected throughout.

Key symbols and synchronous registration/dispatch were checked in pinned
LuaMod.cpp471ff/1631ff; all7 collisions are checked before registering any key.
Registration failure leaves callbacks inert. Every engine operation is dispatched
to EngineTick game thread; no per-frame layout writes/loop/ticker.

## Offline checks and readiness

Eight new mock groups: create/style/move/commit/reset/cleanup; sample independent
of later target text; ambiguous/nonstretched HUD rejection; import failure;
partial attachment; timeout/viewport loss; font-release retry with preserved
carrier; coordinate bounds and collision preflight. Full runner66 tests passed.
Mocks do not establish actual HUD anchors, hint material display, clipping,
placement under DPI/aspect ratios, input propagation or native GC/render.

Source mirror UE4.27 revision306a7e9f7fb53f14c2cb3bfd3854ad906710a17e was inspected:
UserWidget.cpp109–160/887–970/1102–1177/2013–2042, WidgetComponent.cpp and
SWorldWidgetScreenLayer.cpp92–145. Local source manifest records URL/hash. Source
mirror is not the game binary; retained game UHT confirms relevant reflection.
[Official UE4.27 UMG viewport example](https://dev.epicgames.com/documentation/unreal-engine/user-interface-with-umg?application_version=4.27&lang=en-US)
is supporting precedent; UE5 and other Lua integrations are not contract proof.
Pinned UE4SS source: [LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp).

Historical prepared procedure (completed result above governs current status): At one unopened chest arm F6; inspect
screen sample while rotating camera/walking away, choose X/Y, F7, Home/reset if
needed, F7 again after final choice, F6 cleanup before180s, close normally. Check
stock prompt unchanged and own block completely removed. The completed run accepts the displayed baseline and cleanup, not arrow tuning,
production visibility or target selection.

## Prepared source hashes

`Scripts/main.lua` SHA256 `3fa10606000f9b44406d1ddf5a798d1634483e6809570c8fc9b242ed12da63fa`.

`Scripts/IIPPosition.lua` SHA256 `e2e83b83e2a8b4d1efdef5b01b7125383de99d784f15319ecbbc5ce89bc59620`.

[Pinned UE4.27 projection source](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/SWorldWidgetScreenLayer.cpp) and [UserWidget implementation](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/UserWidget.cpp) support the comparison above.
