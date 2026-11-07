# Current selected interaction owner — existing-evidence audit (2026-11-06)

## Selected prompt owner read seam — remote source-only audit, 2026-11-07

**NO VERIFIED CHEAP LUA READER / ONE BOUNDED LOCAL STATIC CHECK / NO RUNTIME ACTION.**

This pass reuses the exact Steam 1.09/build 12996889 native trace and
the previous bounded Genesis reflection inventory; it inspects the **pinned**
UE4SS source revision `83330635` through GitHub, not a later API version.
It does **not** inspect new local-only game binaries/SDK, make a Lua probe,
install anything, run the game, or claim World target authority.

### Established and missing edges

- In the proved character-side update `0x11E39C0`, the active prompt-owner
  weak-reference pair is at **interaction state +0x410** and the proposed
  owner is at **state +0x418**. The update compares them, hides the old valid
  actor, commits the proposed pair and shows the new valid actor. The
  character's **+0x560** field is used to obtain the separate state pointer
  in the earlier native getter trace. These are **not** offsets to be
  conflated: `character + 0x410` is not the verified owner field.
- The prior 568-header / 2,618-property and 33-package / 201-member
  inventory established **no reflected accessor linked to this committed
  owner pair**. That bounded corpus cannot disprove a native-only bridge.
  `GameGlobal:GetActionTarget(GenesisCharacter*) -> AActor*` and
  `SetActionTarget(GenesisCharacter*, AActor*)` are the most relevant
  reflected getter/setter by shape; their native bodies, writers and
  relation to `state+0x410` were **not traced**. Do not mistake the word
  `Target` for selection authority.
- Pinned UE4SS `UObject` Lua member reads resolve an existing custom
  property or `UClass::FindProperty`; `GetPropertyValue` uses the same
  member access. `RegisterCustomProperty` **does exist** in this exact
  revision, but registers a property on a concrete `BelongsToClass`
  using an absolute `OffsetInternal` or an offset relative to another
  *reflected property on that class*. It is not a demonstrated generic
  read-memory API or a dereference-a-pointer-then-read-offset facility.
  [Pinned Lua UObject implementation](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/LuaType/LuaUObject.hpp),
  [pinned registration implementation](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp),
  [pinned API contract](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/docs/lua-api/global-functions/registercustomproperty.md).
- Thus **`state+0x410` by itself is not a usable Lua property**. Whether
  state is a reflected UObject/UStruct reachable through a reflected
  character member, and whether a weak-object property can be accessed
  with valid lifetime/index/serial semantics, remain unknown. Do not
  register `character+0x410` as a fake property or blindly expose
  `character+0x560` as a UObject pointer. Native weak resolution in
  the earlier trace verifies a C++ path, not an exposed Lua reader.
- The separately tested exact base-class `ShowTipEvent` hook registered
  but delivered **zero callbacks** during its 2026-11-07 user run. That
  does not make an alternative raw-memory reader safe or prove game
  events absent. [Exact run](../show-tip-event-observer/README.md#runtime-result--2026-11-07).

### One necessary local static discriminator (not permission to install)

Use **only the already retained** verified host binary/UHT/private
exports with local user-started Codex, no game launch or injection:

1. Resolve the **native** implementation of
   `GameGlobal:GetActionTarget` and its paired setter from their exact
   reflected exec thunks. Trace character argument, state pointer,
   actual read/write offsets, whether the getter has side effects, and
   whether they coincide with **committed `state+0x410`** rather than
   candidate `+0x418` or unrelated gameplay target state.
2. At the proven `+0x560 -> state` edge, establish the type and lifetime:
   UObject/reflected struct or native-only allocation; any concrete
   exposed reflected property/UFunction and safe weak-reference resolver.
   An existing getter counts only if its **native body** proves it reads
   the currently committed prompt winner **before input**, including
   hide-to-null / A-to-B lifecycle. No calls or simulated writes.
3. If one exact O(1), read-only, lifetime-safe **UE4SS 83330635** route
   exists, report class/function/property and pointer/weak semantics,
   precise native RVA chain, provenance and still-unproved runtime
   behavior. A later separately authorized natural runtime correlation
   would remain necessary. Otherwise stop with the **last reached edge**
   and mark World selected-owner fast path **unavailable in established
   interfaces**; do not build a speculative offset reader, native DLL,
   all-owner scanner or broad `ProcessEvent` hook.

**Architecture checkpoint:** absent a proved safe cheap seam, prefer
source-design work on native-owned **Screen S1** (reuse one `TipHUD` with
the native localized action/hint and own upper line/divider). S1 avoids
a separate target synchronizer but **changes depth occlusion** and
requires explicit visual/product approval. World remains conditional,
not accepted; native-only visual suppression, real latency, GPU/CPU
frame-time and repeated resource lifetime remain independent blockers.

## Native TipHUD show and hide — 2026-11-07

**Result A, static.** One character-side update commits a single prompt
owner and commands hide on the previous actor and show on the new actor.
The same actor helper dispatches `ShowTipEvent(bool)` and directly calls
`ExtendedWidgetComponent:SetShow`. This yields a candidate event seam
without a mod-side owner sweep. Its delivery to Lua remains unverified.

Steam 1.09/build 12996889, UE4.27 x64. The read-only PE/Capstone analysis
checked shipping SHA-256
`ddea6b5ca5d34836f01702993d20209c2595367287e6cd5a135a7ace1958b1c0`
and the prior UE4SS 83330635 DLL hash. All addresses below are RVAs.

| Edge | Binary evidence |
| --- | --- |
| Reflection → native implementation | ASCII `SetShow` at `0x4389AE8`, name/exec pair at `0x4389F00`, exec `0x12530C0`. The exec unmarshals bool and two floats, then calls `0x10D9960` at `0x12531BB`. The implementation branches on DL at `0x10D9979`; false tails into hide helper `0x10D9640`, true reaches the component show helper `0x10D9A30` subject to its local guards. |
| Actor → component and event | Actor helper `0x10A59F0` preserves the incoming bool, calls event wrapper `0x123E680`, then loads its component at actor `+0x320` and calls `0x10D9960` directly at `0x10A5A20` if present. UTF-16 `ShowTipEvent` at `0x4368E40` initializes the FName at `0x55503F8` through `0x691066`; `0x123E680` reads that name and dispatches the actor and bool through virtual slot `+0x220`. Thus this wrapper is the actual named event dispatch, distinct from the reflected function-construction helper `0x123E020`. |
| Character update → one committed owner | Update `0x11E39C0`, called at `0x11DEA9E`, resolves proposed actor from state `+0x418` and compares it to the previous prompt-owner weak ref `+0x410` at `0x11E4585–0x11E45AA`. On change, it calls the actor helper with **false** for the old valid actor at `0x11E45CE`, copies the proposed weak ref at `0x11E45D9`, then calls with **true** for the new valid actor at `0x11E45FB`. Null proposal yields hide without a new show. The helper also has an execution-path hide caller at `0x11DD91A`. This proves one committed actor for this update path, without implying global exclusivity across other widgets or paths. |
| Update and detector identification | Reflected `SetInteractDebugState` exec `0x1289590` calls `0x11128F0`, which tails into `0x1150B00` and writes character-state `+0x48C` through character `+0x560`. The update skips entirely for mode 1, skips detector `0x11DED50` for mode 2, and skips both transition commands for mode 3. This matches the earlier Blueprint debug labels for UpdateInteractAction, object detection, and component show/hide. |
| Detection → proposal | Detector `0x11DED50` clears detection slots `+0x3F0/3F8/400/408`. One path iterates candidate components, compares an orientation score with a per-component threshold and keeps the better score at `0x11DF334–0x11DF34A`. It resolves the winning component's owner at `0x11DF370` and writes the actor weak ref into `+0x3F0` at `0x11DF3A6`. The update checks that actor and takes it into the proposed slot at `0x11E3B84` or `0x11E3C95` on the corresponding branches. The orientation helper uses vector normalization and dot-product arithmetic. Exact source of the facing vector, range thresholds for Open/Take/Check and every detection branch remain open. |

The PE reference check scanned `.text` for relative E8/E9 targets and
validated hits against decoded instructions in exception-directory ranges.
It confirmed five direct calls to the SetShow body including the exec,
and three direct callers of the actor helper. This does not enumerate
indirect calls or prove every caller is an interaction caller.

**World implication.** The actor and bool are present at `ShowTipEvent`
dispatch, and the single committed prompt-owner slot is a distinct native
state from Last/Doing. No reflected getter for the slot has been shown.
The direct call bypasses the SetShow exec thunk on this path, consistent
with the old zero-callback observation. Also, `ShowTipEvent` dispatch
precedes the component command, so it indicates selection intent before
the component gate, not confirmed visibility or pixels.

**One remaining check, if separately authorized:** verify read-only delivery
of the exact `ShowTipEvent` on natural Open/Take/Check transitions and match
actor/bool order to the existing native visibility snapshots. This would
establish whether UE4SS can consume the event seam in practice. No runtime
hook or probe was prepared, and production use remains gated.

## Genesis reflected API inventory — 2026-11-07

**No verified reflected source for the selected pre-input TipHUD owner.**
The broad inventory surfaced one generic actor getter, concrete
interaction-volume templates and several presentation endpoints. These
are different parts of the chain. The shipped binary and UHT corpus
are from the Steam 1.09/build 12996889, UE4.27 x64 baseline used below.

### Coverage and reproducibility

- Scanned all **568 Genesis Public headers** in the retained UE4SS UHT
  dump. Counted **1,782 UFUNCTIONs, 2,618 UPROPERTYs, 130 UCLASSes,
  278 USTRUCTs and 143 UENUMs**. Checked that each function/property
  annotation yielded one declaration ending at a semicolon. SHA-256 of
  sorted UTF-8 `filename sha256\n` rows:
  `b050e240984c4737acdfd3aafee7cec696ea67f10805f71459ab0573906509c4`.
- Parsed **33 retained package export JSONs**, with **304 Function exports,
  201 generated-class member properties and 14 generated classes**
  (10 Blueprint and 4 Widget Blueprint). Function parameters and locals
  are excluded from the property count. Used the **304 retained bytecode
  JSONs** for exact reference checks on shortlisted declarations.
- First pass matched header owner plus declaration, or Blueprint export
  and member names, case-insensitively. Stems: `interact|current|last|doing|
  active|focus|target|select|candidat|aim|detect|near|closest|range|distanc|
  angle|tip|prompt|widget|show|visib|action|overlap`. This yielded 448
  native function and 676 property hits, plus 60 Blueprint functions,
  44 member properties and five generated classes. Then reviewed
  actor/component/widget return and out types and the context of each
  promising owner. Combat lock-on, AI targeting, camera, climbing,
  NPC dialogue and generic spatial helpers were separated unless an
  interaction-prompt edge was present. The corpus excludes unexported
  Blueprint packages and unreflected native state.

### Shortlist by responsibility

Native owners in the table are under `/Script/Genesis`. Listed native
members are reflected declarations; runtime availability, cost and
hook delivery require separate evidence.

| Responsibility | Member or component | Evidence and limit |
| --- | --- | --- |
| Discovery | `GenesisCharacter:SetInterActionDetectBoxComponent(UBoxComponent*)`; `PlayerActionComponent.InteractObjectDetectTickInterval: float` | Configuration of a detection box and cadence by declaration. Neither exposes candidates or a winner. |
| Discovery | `GameEventObject_InteractAreaComponent`, `GameEventObject_InteractTriggerAreaComponent` (box); `GameEventObject_AimInteractComponent.InteractAngle: float`; character-overlap component family | Actual exported templates: `BaseLoot_BP` (Open) has `InteractLookArea` of the area type and `InteractTriggerArea` of the trigger type; `BaseLoot2_BP` (Take) has `InteractTriggerArea_NoAlign` of the **area** type, with `CharacterAction=pick up`; `BaseDocumentObject` (Check) has `GameEventObject_InteractArea` of the area type. The names of template variables alone can mislead. Their native consumers, facing test and priority remain unknown. The aim/overlap classes are alternatives in the inventory, with no demonstrated use by these templates. |
| Eligibility and selection | `BaseGameEventObject:CheckInteractCondition(AActor*) → bool`; `GameGlobal:CheckInteractCondition(AActor*, const TArray<FInteractCondition>&) → bool`; object `IsActive` / `IsCanInteract: bool` | The retained Blueprint helper reads the two flags at offset 79. Single-object predicates are not a winning-actor source. `GameGlobal:GetNearestObjectFromArray(AActor*, const TArray<AActor*>&) → AActor*` takes a caller-supplied set and has no traced stock prompt callsite. |
| Selection / state | `GameGlobal:GetActionTarget(AGenesisCharacter*) → AActor*` (BlueprintPure), paired with `SetActionTarget(AGenesisCharacter*, AActor*) → void` | Strongest new declaration by return shape. The setter makes explicit that an action target can be supplied, but the inventory does not establish who writes the value, its lifetime, or whether detection writes it before input. No exact getter/setter reference in retained Blueprint bytecode. `GetLockOnTarget` and AI target caches are separate leads with no prompt connection. |
| Execution state | `GameGlobal:GetLastInteractObject` and `GetDoingInteractObject`, both `(AGenesisCharacter*) → ABaseGameEventObject*`; `GetToDoInteractActionPressTimer(float&) → float`; `BaseGameScriptObject:EventObjectInteractBegin/End/Fail(AActor*, AActor*, FName) → void` | Native trace below identifies Last as execution history and Doing as the distinct execution slot cleared on End. TipHUD reads the timer in its hold-progress graph. Script events are execution-shaped declarations with no proven prompt callback path. None supplies current pre-input selection. |
| Presentation | `BaseGameEventObject:ShowTipEvent(bool) → void` (BlueprintImplementableEvent); `ExtendedWidgetComponent:SetShow(bool,float,float) → void` | Strongest actor-local notification and component command by signature. No exact retained Blueprint caller for either. Prior SetShow runtime saw registration and zero callbacks; direct native dispatch remains possible. Neither signature proves exclusivity. |
| Presentation / lookup | `ExtendedWidgetComponent.SenderActor: AActor*`, `NewUserWidget: UUserWidget*`; `SetArrayData(AActor*,int32)`; `GameGlobal:GetUserWidget(AGenesisCharacter*, AActor*) → UUserWidget*`; `ExtendedUserWidget:CanShow() → bool` | Component-local state and widget lookup with an explicit actor input. The actual Blueprint initialization at 102 calls inherited `WidgetComponent:GetUserWidgetObject`, a different method. `TipHUD_C:CanShow` calls its native parent and applies an input-mode gate. Existing runtime proved rapid widget/owner correlation, without proving an authoritative selected actor. |

**One next check, separately scoped:** trace the **native caller of
`ExtendedWidgetComponent:SetShow` in the stock interaction path**, using
the component command as the anchor and following the true/false producer
back to its owner reference. This can discriminate a shared winner from
per-object show/hide. The direct caller must first be established; a
reflected thunk or old zero-callback result is insufficient. That check
has not been started in this inventory.

## Native GetLastInteractObject — 2026-11-06

**Result B: reject this getter as the pre-input TipHUD target.** It resolves
the weak reference to an object committed on interaction execution paths,
including a failure-dispatch path. It can still refer to that object after
the current execution slot is cleared. This is not necessarily the last
successful interaction and establishes no authority over stock prompt selection.

Read-only PE analysis of Steam 1.09/build 12996889, UE4.27 x64, shipping
SHA-256 `ddea6b5ca5d34836f01702993d20209c2595367287e6cd5a135a7ace1958b1c0`.
UE4SS `83330635` DLL identity matched the prior baseline. Addresses below
are RVAs relative to the PE image base `0x140000000`. Used a local PE reader,
exception directory for function ranges, and the already available Capstone
4.0 DLL to decode candidate instruction sites. Full listings remain local.

| Edge | Native evidence |
| --- | --- |
| Name → exec thunk | ASCII `GetLastInteractObject` at `0x43AEE18`. Its name/function pointer pair at `0x43B9CD0` identifies the exec thunk `0x1273690`. The thunk unmarshals the object argument into RCX, calls `0x110C110` at `0x12736FD` and stores RAX in the reflected result at `0x1273707`. A separate name reference at `0x4392208` points to a lazy reflection constructor, not the body. |
| Return value | `0x110C110` returns null on a null character, otherwise tails into `0x114BCA0`. That loads the character's state pointer at `+0x560` and resolves its eight-byte weak reference at `+0x484` through `0x1644430`. The resolver checks the object index, serial and object flags before returning a pointer. Missing state or a non-resolving reference yields null. |
| Initialization | `0x11DCF5B` / `0x11DCF65` initialize the pair to index −1 and serial 0, adjacent to equivalent initialization for the execution slot at `+0x47C`. |
| Execution writes | `0x11DD8E8` copies the staged weak reference from `+0x418` to `+0x484`, and `0x11DD8EF` copies it to `+0x47C`. The path dispatches Begin or Fail at `0x11DD9EF` / `0x11DDA1E` and clears the staged slot at `0x11DDA3E`. A second path at `0x11E47C9` writes the same history slot after accumulated time exceeds the threshold compared at `0x11E478A`, resets that accumulation and dispatches Begin or Fail at `0x11E4813` / `0x11E483E`. It then clears the staging reference at `0x11E4852`. |
| Dispatch identification | Independently located the reflected `TriggerInteractBeginEvent`, `TriggerInteractEndEvent` and `TriggerInteractFailEvent` thunks at `0x123F980`, `0x123FA90`, `0x123FBA0`. They use the same native virtual dispatch stubs `0x10A5D30`, `0x10A5D40`, `0x10A5D50` respectively. |
| End and sibling getter | `GetDoingInteractObject` exec `0x126E710` → `0x110AE30` → `0x114B380` resolves `+0x47C` on the same state. End dispatch at `0x11DE9DC` uses that slot. The following store at `0x11DEA00` clears `+0x47C` with the empty weak-reference pair, leaving `+0x484` intact on that path. |

Writer search was anchored on the decoded state displacement and the weak
reference layout. Equal offsets in unrelated types were excluded from the
trace. This is a bounded positive identification of execution writers and
of persistence across the traced End path, not a proof that every possible
reset or indirect copy has been enumerated. The getter performs no scan or
fresh selection. A resolved pointer can be live but stale relative to the
visible prompt, and object invalidation can turn it into null independently
of prompt visibility. No link to distance/facing detection, arbitration or
TipHUD show/hide was established. No reflected call was made in game.

**Disposition:** close `GetLastInteractObject` as a World target candidate.
No additional runtime check of this getter is needed to make that decision.

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
