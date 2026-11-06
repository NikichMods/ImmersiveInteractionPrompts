# Current selected interaction owner — existing-evidence audit (2026-11-06)

## Local static follow-up — 2026-11-06

**Result B.** The local evidence identifies exact reflected candidates, but
does not link any of them to the final prompt winner. The missing edge is
the native Genesis code that updates interaction state and causes the
stock `ExtendedWidgetComponent` to show or hide. A fast World selector
cannot yet use any of these candidates as authoritative.

### Traced boundaries

| Stage | Static evidence | Limit |
| --- | --- | --- |
| Association at initialization | `BaseGameEventObject_BP` owns `ExtendedWidget` and `TipHUDArgument`. Its ubergraph enters BeginPlay at 92, gets the widget at 102, casts to `TipHUD_C` at 144 and copies `HoldPress` at 219. | Association of one actor with one widget. Global BeginPlayPost indexing was performed by the earlier observer. The game's own candidate-registration logic is not exposed by this graph. |
| Eligibility | `InteractObjectFunctionLibrary_C:InteractObject_IsCanInteract` casts the supplied actor to `BaseGameEventObject` (0), reads `IsActive && IsCanInteract` (79), and returns false on a failed cast (185 → 196). | A Boolean about one supplied object. No proven caller in the prompt selection chain. |
| Range and facing | Generated Genesis declarations expose `GenesisCharacter:SetInterActionDetectBoxComponent(UBoxComponent*)`, `PlayerActionComponent.InteractObjectDetectTickInterval`, `GameEventObject_AimInteractComponent.InteractAngle`, and character-overlap component classes. | Evidence of available mechanisms. No executable link from these declarations to the tested Open/Take/Check owners, actual direction source, threshold, trace, or tie-break. The user's distance/body-facing report remains a gameplay observation. |
| Selection/update boundary | `MainGameInstance_BP_C:TestInteractDebugState` calls native `GameGlobal:SetInteractDebugState` at 131. Diagnostic labels at 466/578/658 distinguish skipping `UpdateInteractAction`, skipping object detection, and skipping interaction-component show/hide. | These are debug labels and a real setter call, not recovered native implementation. No ordering or writer for a single winner follows from the labels. |
| UI gate and presentation | `TipHUD_C:CanShow` calls native parent `ExtendedUserWidget:CanShow` at 0 and ANDs it with the input-mode gate at 20/50/81/119. The native parent body and its stock caller are unresolved. TipHUD Tick writes its own debug opacity at 1127/1147. The proxy at 713 calls `SetupTipMessage2` for content. | Widget-local gate, debug opacity and content setup establish no native object ranking or actor→show command. |
| Action dispatch | Open `BaseLoot_BP`, Take `BaseLoot2_BP`, Check `BaseDocumentObject` receive `InteractBeginEvent(caller, objectAction, interactComponent)`. Each wrapper dispatches at 54 into its respective graph at 2787, 1087 or 3363. The parent forwards the inherited event at 261. | These are consumers of an already supplied interaction. They do not establish the pre-input prompt target or which native caller selected it. |

### Exact reflected candidates

- `/Script/Genesis.GameGlobal:GetLastInteractObject` and
  `/Script/Genesis.GameGlobal:GetDoingInteractObject` are declared static
  `BlueprintPure` functions taking `AGenesisCharacter*` and returning
  `ABaseGameEventObject*`. Their signatures make a direct reflected
  read plausible without walking all owners. Names and flags do not
  establish the value's lifetime, null/clear behavior, cost or whether
  it tracks selection before input. The dump's generated C++ bodies
  returning null are stubs and provide no game behavior evidence.
- `/Script/Genesis.BaseGameEventObject:ShowTipEvent` is declared as
  `BlueprintImplementableEvent void(bool Show)`. It is an actor-local
  candidate notification. Neither a natural producer nor an executable
  override was located in the retained corpus. Reflection alone does not
  establish callback delivery through UE4SS, or a global unique winner.

### Scope and reproducibility

Verified the installed shipping executable against the established Steam
1.09/build 12996889 SHA-256
`ddea6b5ca5d34836f01702993d20209c2595367287e6cd5a135a7ace1958b1c0`.
Used the retained CUE4Parse 1.2.2 UE4.27 exports and the installed UE4SS
UHT dump. Literal reference search across **304 retained bytecode exports**
found no references to the two object getters, `ShowTipEvent` or
`CheckInteractCondition`. The spatial-pattern search located overlap
in climb/ladder exports and a debug trace, with no reachable edge from
them to the tested prompt chain. This corpus is bounded. Native callers,
unexported assets and other spatial implementations remain open.

| Local evidence identifier | SHA-256 |
| --- | --- |
| `GameGlobal.h` | `a6d1b5c0828e0bcc188f05fa8e29e5e58d618c08731d4bc9fd0ba8b3c4925023` |
| `BaseGameEventObject.h` | `f18758d5bd186a84eee122d3ecb63ee92c13b35d74f38ed08c01c5ea5911cb00` |
| `MainGameInstance_BP--TestInteractDebugState.bytecode.json` | `10e43e369e90623e75f8f25333339ccadb890af355a5a798b28707f1fc3ff188` |
| `InteractObjectFunctionLibrary--InteractObject_IsCanInteract.bytecode.json` | `144d2d642d0977f7e60b50f62ba84a40b07eeaa5f8b1e60d574a4586b511eaa5` |
| `TipHUD--CanShow.bytecode.json` | `39cfc83d79b6e20b086aceb44dab96f9e5797ef6cbde980e0a5457bae9bbd605` |

**One next check, if World needs this authority:** trace the native
`GetLastInteractObject` implementation in the exact shipping binary to
the state it reads and the writer of that state. The decisive distinction
is whether it is updated by prompt detection before input and cleared on
loss of focus, or written only by interaction execution. This can rule the
getter in or out for a later read-only correlation test. No probe prepared.

## Earlier committed-evidence audit

**Scope:** source/document audit only. Parent revision [`d5e6def`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/d5e6def72863bf617366cc973fb8f588860c2404) is the bounded in-game CanShow correlation result. No installed game, local private SDK/assets/logs, new UE4SS probe, renderer, host write or performance experiment was accessed or performed here. This is a finding about **available committed evidence**, not a whole-game proof that an authoritative selector does not exist.

**Question:** Is there an **already demonstrated, cheaply readable authoritative current selected actor/widget**, independent of a global 34-owner visibility sweep, which could safely authorize the World renderer's one active prompt?

**Result: NO ESTABLISHED AUTHORITATIVE TARGET SOURCE.** Current `CanShow` + widget→actor index gives a timely **candidate** for six observed episodes, not exclusive/native selected-target authority. Production World selector **BLOCKED**. This conclusion does not negate the observed event correlation.

## Actual evidence and boundaries

| Mechanism / source | Established | What it does **not** establish |
| --- | --- | --- |
| Native owner registration on `RegisterBeginPlayPostHook`; [`IIPInteractionSource.acquire`](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/d5e6def72863bf617366cc973fb8f588860c2404/research/interaction-prompts-owner/world-space/auto-world-successor/Scripts/IIPInteractionSource.lua) | 34 ready reciprocal actor↔ExtendedWidgetComponent↔TipHUD pairs (Open 6/Take 18/Check 10) on a normal load. Primitive widget→owner indexing can be performed once and updated on EndPlay/map. [Live acquisition](../multi-action/README.md#runtime-result--2026-11-06). | Which of these objects the engine has *currently selected* near the player. The actor's `GetOwner`, `GetUserWidgetObject`, `Widget`, `NewUserWidget` and TipHUD Outer/owning player express identity or lifecycle, not selected-target state. |
| Exact non-native `TipHUD_C:CanShow` script post-hook; [`IIPEventCorrelation.lua`](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/d5e6def72863bf617366cc973fb8f588860c2404/research/interaction-prompts-owner/world-space/event-driven/Scripts/IIPEventCorrelation.lua) | 528/528 callbacks mapped to the indexed widget/owner; six show edges and six hide edges; six shown episodes were read one observer frame after **the latest callback** of that widget. [Game report](PROBE.md#runtime-result--2026-11-06). | The original returned CanShow boolean, first callback→pixel time, that every callback means selection/show, or a global show/hide/target-switch event. The post-callback has only the widget context; calling CanShow again would create another query. |
| [`IIPInteractionSource.snapshot`](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/d5e6def72863bf617366cc973fb8f588860c2404/research/interaction-prompts-owner/world-space/auto-world-successor/Scripts/IIPInteractionSource.lua) and [`IIPOpenVisibility`](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/d5e6def72863bf617366cc973fb8f588860c2404/research/interaction-prompts-owner/world-space/event-driven/Scripts/IIPOpenVisibility.lua) | Read-only check of Screen WidgetComponent `bVisible && bAddedToScreen`, plus TipHUD/text/retainer/icon visibility and opacity, native localized action readiness and reciprocal identity. | An independent native focus/selection writer or exclusive-target invariant. 85 *sparse* complete 60-frame diagnostic audits (10 unique/75 none/0 ambiguous) cover their sampled moments only; they may miss transient overlap or a direct adjacent-object switch. |
| `ExtendedWidgetComponent:SetShow`, `SetArrayData`, `SenderActor` / `NewUserWidget` | `SetShow` hook registration succeeded with **zero callbacks** in one 31.965 s natural session. `SetArrayData` and component fields are known from reflected/native declarations; the old bounded 304-Blueprint-export review found no natural callsite for SetShow/SetArrayData/Setup. [Route review](../../open-binding/ROUTE_REVIEW.md), [negative runtime](../../open-binding/README.md#runtime-result--2026-10-29). | That these APIs are an active selected-target notification. `SenderActor` is not a proven current focused actor. Zero callbacks is not proof that native direct dispatch never uses SetShow. No repeat of the identical hook is justified. |
| `ExtendedUserWidget:SetupTipMessage2` / `TipHUD:SetupTipMessage_Proxy` | Exact text/icon consumer and reflected array parameter declarations established. [UHT review](../../UHT_SIGNATURE.md). | Selection ownership, final native winner, safe Lua array-hook ABI or a prompt event. Content setup is not target arbitration. |
| [`IIPTargetPolicy.observe`](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/d5e6def72863bf617366cc973fb8f588860c2404/research/interaction-prompts-owner/world-space/auto-target/IIPTargetPolicy.lua) | A conservative *project-owned* arbiter: require a complete fresh visibility snapshot, choose only one ready shown owner, request cleanup before a different bind. | A native selected target or cheap O(1) producer. Two complete samples every 3 frames is a sampling hypothesis, not a proof of exclusivity or negligible frame cost. |
| Existing original `TipHUD` native Screen hierarchy | Its own native visible/show/hide and localized action/hint are already coupled to the game's selection. Authored child/ornament primitives rendered in a tested Open widget. [Source/UX study](README.md#5-native-screen-suppression-must-preserve-event-evidence). | Real World occlusion by Hilda, accepted automatic multi-owner native child lifecycle, or safe removal/recomposition of the old decoration. |

The event observer marks one `active_owner` and samples one queued candidate per frame, but this **observer's state machine is not engine authority**. Its full audit calls `sample` and updates internal observed states; no data source independently reports the engine-selected actor. The six observed sequences are Open #10, Check #3, Take #19, Check #3, Open #10, Check #3: returns to known owners, **not** a direct A→B switch with two adjacent objects continuously eligible.

## Mechanism tradeoff and result

1. **World from CanShow/index.** Responsive **candidate** is supported. Authoritative unique current owner, independent visibility evidence if original prompt is visually hidden, native show/hide suppression/restore, real frame-time and repeated World component resource lifetime all remain **independent BLOCKED gates**. Earlier World tests recorded first sampled native visible→World SHOWN 0.531–1.568 s and a fourth host lookup failure of **unknown cause**; the user rejected that appearance delay. [World evidence](../auto-world/README.md#runtime-result--2026-11-06). Do not treat a one-frame event-read as a one-frame World render or as a resource fix.
2. **Native-owned Screen S1.** Attach own upper lettering/divider under the *same existing* TipHUD, retain native lower action and remapped input glyph, and recompose presentation without a second separate prompt. It inherits the host's own selection/show/hide, eliminating the **need to identify a global current actor solely for presentation**. The one-widget child/ornament primitive already passed real rendering; full native child placement/cleanup and one-prompt visual acceptance are unproved. **Not equivalent to World**: foreground character depth occlusion is lost, and its placement must deliberately communicate Screen-space HUD behavior. This is the cheapest credible next **source-design** study, not a production decision or user visual acceptance.
3. **Separate Screen S2 HUD root.** Still needs authoritative target synchronization and native stock-suppression. Retain only as an option for deliberately fixed screen placement after its own gates; not a cheaper fix for this selection problem.

**Conclusion:** No additional unconditional all-owner polling and no invented global `ProcessEvent`/`SetVisibility` hooks. Do not promote either architecture. The existing evidence alone cannot choose World safely. Research Screen S1 composition/one-native-prompt integration next; preserve World as conditional preference and avoid silently changing its depth behavior.

## User-observed selection envelope — 2026-11-06

**User visual report (not independently instrumented):** A native interaction
prompt appears only when Hilda is **close** to an object **and her character body
is facing toward it**. Being close with her back to the object does not show
the prompt; facing it from far away also does not show the prompt. The user
explicitly clarified that **Hilda's body orientation, not camera orientation**,
is what matters in their observed gameplay. This establishes a body-facing +
distance dependence *at the observed UX level*, not the internal comparison or
the engine's exact source field. The numeric angle/distance thresholds,
occlusion criterion and native final writer remain unknown.

The conditions are consistent with several materially different mechanisms:
- overlap/proximity creates an eligible set, while an independent direction
  threshold (`forward · normalized(target-position)`) or trace chooses a prompt;
- a bounded forward ray/shape sweep that inherently combines direction and
  maximum range;
- game-specific logic on the player, interaction object or UI owner combining
  distance, facing and/or line-of-sight, possibly alongside other input state.

**No mechanical inference:** visual gating alone does **not** prove an actual
Overlap callback, LineTrace/SphereTrace, dot-product implementation, event
availability, or existence of an accessible selected-target property. Avoid
recreating the selector from approximate distance/yaw: such a copy may disagree
about priorities, thresholds, collision, camera/body rotation and eligibility.

**Source-search refinement:** From the verified interaction actor/TipHUD chain,
follow actual show/CanShow callers and the player/interaction dispatcher;
prioritize **Hilda/pawn actor-forward or movement-facing vectors** and their
combination with object-relative direction, distance and native prompt state.
Inspect reachable `OnComponentBeginOverlap`, `OnComponentEndOverlap`, actor
overlap, `LineTrace`/`SphereTrace`/other trace functions,
`GetActorForwardVector`, `DotProduct`/angle comparisons, distance/radius checks
and native Genesis predicates. The goal remains the **final selected
actor/widget writer** or existing read-only event/field, not merely an
intermediate eligibility predicate. Do not assume the literal
`GetActorForwardVector` API is used: animation/control-facing could be stored
or computed elsewhere. A camera-only trace would not by itself explain the
reported dependence on body direction; the exact game callchain still decides.

**Minimal remaining discriminating gameplay observation, only if later justified:**
the body-vs-camera question is already resolved for the user's observation and
must not be repeatedly requested. If a game test later becomes necessary,
observe a continuous A→B transition between adjacent eligible interactables
without leaving proximity, to test selection priority and simultaneous native
visibility. It still would not identify a native API on its own. No new game
session, installation or test has been requested by this audit.

## Epic UE4.27 mechanisms — external documentation check (2026-11-06)

The **official Unreal Engine 4.27** documentation identifies standard building
blocks but **no engine-wide automatically maintained current interactive
world-actor accessor**. This is a documentation scope finding, not a claim
about every plugin or game's private C++ implementation.

| Documented UE4.27 API/pattern | What it establishes | Asterigos implication / limit |
| --- | --- | --- |
| [Blueprint Actor Begin/End Overlap](https://dev.epicgames.com/documentation/unreal-engine/blueprint-events?application_version=4.27), [Setting Up Input on an Actor](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-input-on-an-actor?application_version=4.27) | Collision triggers can notify the actor when the player enters/leaves an interaction area; Epic uses a chest/nearby-light example. | Good candidate for cheap *eligibility* transition; multiple overlapping triggers do not establish which one has priority or prove that this game uses them. |
| [Line Trace By Channel](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-a-single-line-trace-raycast-by-channel?application_version=4.27), [Traces Overview](https://dev.epicgames.com/documentation/unreal-engine/traces-overview?application_version=4.27) | A trace can return a hit actor/component. Epic explicitly demonstrates line-trace use in an Event Tick; shape traces and object filtering also exist. | A possible focused target signal *if the game calls a trace and its actual hit is forwarded to interaction arbitration*; running our own guessed raycast would create a potentially divergent selector rather than read the game's current choice. |
| [Blueprint Interface interaction guide](https://dev.epicgames.com/documentation/unreal-engine/interface-quick-start-guide?application_version=4.27) | Different actor types can expose the same `Interact` operation. | A dispatch/behavior contract, **not** a native chosen-object getter. |
| [Widget Interaction Component](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-interaction-component?application_version=4.27) | UI pointer/hover simulation for interactive WidgetComponents, with `GetHoveredWidgetComponent`, hit testing and simulated clicks. | **False friend**: hovering a clickable Slate/UMG widget is not the gameplay selection of lootboxes/documents unless Asterigos demonstrably routes its interactions through that component; no such game evidence exists. |
| [Widget Component API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/WidgetComponent?application_version=4.27) | UMG can be drawn in screen space or as a world-rendered surface via an actor's WidgetComponent. | Supports why the stock native Screen TipHUD already follows its actor location but does not get Hilda depth occlusion; renderer space itself does not reveal the selection manager. |

**Prioritization (hypotheses, not established game facts):** (A) overlap
gates entry/exit into an eligible candidate set; (B) optional trace/facing/
distance decision resolves priority; (C) a Genesis-specific manager or
owner-local native method updates ExtendedWidget/TipHUD. The actual game
might use A, B, C in combination or none of these exact patterns.

**Revised narrow source-search order if World authority is necessary:**
start with existing accepted Open/Take/Check actor+TipHUD+ExtendedWidget
ownership; trace backwards through **actual Asterigos Blueprint callsites**
for native prompt visibility and `CanShow`. In that reachable callgraph,
identify first the actual Begin/End Actor/Component Overlap event consumers,
any `LineTraceByChannel`/Kismet trace/shape-trace call consumers and actual
Interact action dispatcher, then any demonstrated Genesis writer/selector.
For each possible signal prove the concrete sender→decision→selected owner/
widget→show/hide route, distinguish candidate-eligibility transitions from
final priority, and check whether an **already committed** reflected
property/function can read its result cheaply without causing another trace.
Do not guess a global selected-target field, indiscriminately hook every
overlap or ProcessEvent, reproduce the game's selector from approximate
distance/direction, or install a new probe based solely on generic Epic
tutorials.

**Exit condition:** identify an exact traced authoritative read-only
seam with class/member/value provenance and testable unique-target
invariant **or** document the last inspected writer edge and remaining
unavailable native/private evidence. Then re-evaluate World versus
native-owned Screen S1, without silently treating Screen as accepted World.

## Only if World remains the needed visual outcome: one narrow local static evidence gap

The committed repository does **not** contain the private cooked bytecode/SDK/installed-host artifacts needed to identify the actual **final writer** of selected-object state. That is an access gap, **not evidence of nonexistence**.

A user-started local Codex could perform a **read-only, no-game-launch, no-install** inspection of *already available* verified Steam 1.09/build12996889 static exports/generated SDK (without publishing them). Search backwards from the **actual calls/branches** that produce native TipHUD show/hide and from existing `CanShow` callsites; identify exact concrete owner/class/function, selecting condition, final writer and data type, and verify whether a currently focused actor/widget is exposed by a reflected, cheaply readable field or exact non-native callback. Do not guess names from semantics, use arbitrary global hooks or call native functions to manufacture evidence. Review all relevant script exports **only where the traced call chain leads**, with count/scope and negative-search limitations explicit; a zero-match in a limited corpus is UNKNOWN, not absence in C++.

**Sufficient positive output:** exact class/function/field paths, concrete callchain/offets/provenance, writer and read-consumer, value lifetime and how unique active owner is determined; then one separately authorized read-only live check with two adjacent interactables, if needed. **Sufficient negative output:** bounded list of searched callers/exports and the missing writer step, not a fabricated API or an open-ended new reverse-engineering project. Keep private game exports/logs outside public Git; report only succinct reusable game-level findings to Asterigos-Research if genuinely established.

**Not part of this audit:** runtime benchmark, native UI suppression, resource recovery, production World/S1 implementation, installation, or an approval to change accepted visual requirements.
