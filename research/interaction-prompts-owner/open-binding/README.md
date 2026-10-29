# Natural Open binding — READY_SOURCE for one read-only test, runtime NOT_TESTED

2026-10-29. Steam1.09/build12996889, UE4.27 Windows x64, UE4SS83330635.
[Lua source](Scripts/main.lua), SHA256
`a56d8fda1821f28a01e1d1f4e423a8b33e60d3f36d2c7312c5c2ff3327d3f56f`.
No installation, game execution, production/VERSION, settings/save or other-mod
changes. Independent UserWidget [runtime PASS](../userwidget-host/probe/README.md)
is reused without another test. World rendering/occlusion remains NOT_TESTED.

## Question, existing evidence and chosen boundary

We need a live **pointer correspondence**, not an actor whose name resembles a
chest. Existing exports and the completed CanShow test do not supply the inverse
widget→component link. A short visual action cannot reveal those native pointers,
so one event-scoped read-only probe is justified. The finish condition is either
one reciprocal MATCH with a world pose, or an explicit no-match/contract failure.
No wider discovery or alternative diagnostic is automatically attempted.

The chain already established in [VERIFIED_RUNTIME](../../../docs/VERIFIED_RUNTIME.md#1-подтверждённый-ui-owner-и-цепочка):
BaseGameEventObject_BP contains ExtendedWidget (Genesis.ExtendedWidgetComponent,
TipHUD class, DrawSize1000×1000) and TipHUDArgument. BeginPlay ubergraph102 obtains
GetUserWidgetObject,144 casts TipHUD and219 writes its CanHoldPress from owner
HoldPress. This proves a forward path, not the final target-selection C++ writer.

The original CanShow log recorded948 callbacks/three widget identities. All were
under `/Engine/Transient.GameEngine_2147482619:MainGameInstance_BP_C_2147482611`:

| Observed widget suffix | Address in that old process | Actual localized text |
| --- | --- | --- |
| TipHUD_C_2147481654 |2961039264192 | Взаимодействовать |
| TipHUD_C_2147480979 |2961156630720 | Открыть |
| TipHUD_C_2147480920 |2962282063552 | Взять |

These are archived identities, **not selectors for a new session**. In particular,
the Open widget's Outer is not a chest, and GetOwningPlayerPawn would identify the
player. No actor/component identity was captured by that test. The new pair must
be measured, not inferred from these suffixes.

| Route checked | Decision |
| --- | --- |
| Widget Outer / owning player | Existing live evidence does not lead to interactive owner. No inverse API found in inspected TipHUD/ExtendedUserWidget declarations. |
| Enumerate actors/components, choose a chest or match later | Rejected: global world discovery is outside scope, first/nearest actor is not identity proof. |
| Component-side natural SetShow event | Chosen: supplies an exact component context without discovery. Read its actual widget and owner, then require reciprocal actor fields. Whether natural Open uses this reflected route is untested. |
| WidgetArgumentComponent.Setup(Actor*,ExtendedUserWidget*) | Real reflected alternate pairing seam, but not hooked here; its natural timing/dispatch is also untested. Not an automatic fallback. |

## Exact contracts and what they establish

The installed UHT dump contains:

| Contract | Use / limitation |
| --- | --- |
| ExtendedWidgetComponent.SetShow(bool Show,float NewPeriodNotFading,float NewPeriodFading) → void | Observe native **post** only. Never call it or change its parameters/return. Generated .cpp is a stub; native implementation and natural call frequency are unknown. |
| ExtendedWidgetComponent.SenderActor:Actor*, NewUserWidget:UserWidget* | Read diagnostics. SenderActor is not assumed to equal GetOwner. Null NewUserWidget is recorded; a non-null mismatch refuses capture. |
| WidgetComponent.GetWidget(), GetUserWidgetObject() → UserWidget*, const | UE4.27 WidgetComponent.cpp1591/1939 both return stored Widget without creating/initializing a widget. Require equality with reflected private Widget storage. |
| ActorComponent.GetOwner() → Actor*, const BlueprintPure | Read owner, then require the BP-derived owner's ExtendedWidget field to point back to this exact component. No GetComponentsByClass call/array. |
| BaseGameEventObject_BP.ExtendedWidget / TipHUDArgument | Actual exported object properties; inherited owner fields, not guessed search names. Argument.GetOwner must equal the same actor. |
| TipHUDArgument.msgTag:FName, ActionName:EGenesisInputCommandType | Require Open and Interact25 in addition to the current RU TextBlock_89 text «Открыть». This test is intentionally RU/Open scoped, not a localization resolver. |
| SceneComponent.K2_GetComponentLocation/Rotation/Scale, const BlueprintPure | Return FVector/FRotator/FVector; source SceneComponent.cpp1636–1649 forwards to native component getters. This is the source anchor in world space, not the actor origin or a projected screen point. |
| Actor.K2_GetActorLocation() → FVector, const BlueprintPure | Record owner origin separately; do not silently substitute it for the component anchor. |
| WidgetComponent.Space / bAddedToScreen and SceneComponent.bVisible | Require Screen1, screen membership and visibility for capture, plus own TipHUD/text visible-state checks. These are stored state, not proof of camera priority or actual pixels. |

Pinned UE4SS LuaMod.cpp4200ff accepts RegisterHook(path,pre,post), distinguishes
native UFunctions, and returns separate IDs. Its post dispatcher supplies context
and three input wrappers; bool is read through RemoteUnrealParam:get, never set.
The no-op pre and post callbacks return nothing. UnregisterHook1748ff marks the
owned hook for deferred removal; phase becomes inert first. No other mod's hook
is removed. GetFunctionFlags Native0x400 and exact full name are checked at arm.
This does not prove native internal calls necessarily traverse reflected dispatch.

The post callback consumes the context/bool wrappers synchronously and queues only
primitive path/class/address data. All widget/owner/pose reads occur on explicit
EngineTick. **The pose and pointer correspondence are a later game-thread snapshot,
not a claim of atomic equality at native SetShow entry/exit.** Current storage,
identity, reciprocal links and eligibility are rechecked after dispatch. Struct
getter results are reduced immediately to finite scalar strings; no engine struct,
hook parameter or UObject wrapper is retained across callbacks. Pinned
LuaUObject.cpp push_structproperty GetNonTrivialLocal returns owned Lua table data.
No FTransform constructor, offsets, memory writes or native arrays are involved.

## Probe behavior and stopping

Ctrl+Alt+F8 arms **one**60s window; Ctrl+Alt+F7 stops. There is no rearm. One native
SetShow hook, at most64 relevant method callbacks (the64th ends the window), one
pending sample at a time, one selected component, at most6 pose snapshots.
Only a Show=true event can nominate a candidate; invisible/uninitialized/non-Open
widgets are skipped. No candidates are enumerated or retained as a world registry.

A qualifying candidate must pass actual GetWidget/GetUserWidgetObject/Widget
identity, exact TipHUD class, visible stored state, Screen membership, owner base,
actor.ExtendedWidget backlink and owner argument checks. MATCH records full live
widget/component/actor names, addresses/class and SenderActor/NewUserWidget
relations. It does not assert that all visible Open prompts share that actor or
that this actor is the game's sole active interaction target.

After MATCH, F8 snapshots only that identity (world location, rotation Pitch/Yaw/
Roll, scale, actor origin, changed flag). No polling or per-frame reads. A natural
SetShow(false) on the selected component stops; exact-lookup absence, owner/widget
change, hidden/non-Open state, malformed data, budget, deadline or F7 also stop.
Disappearance without a new event is detectable at the next manual sample/deadline,
not continuously. No retargeting on replacements. User motion of the camera need
not change the component transform; unchanged pose is a valid result.

Stop drops primitive target records and requests only its own hook unregistration.
If unregister fails, the callback remains inert and logs UNREGISTER_FAILED; F7
can retry. Dispatch failure also makes the observer inert, with no game-state
rollback needed because it made no writes. There is no UI cleanup, GC/root control,
load/spawn, Create, show/hide call or asset mutation in this probe.

## Minimum future experiment — not authorized or installed by this stage

1. Start gameplay a short distance outside one natural unopened Open prompt's
   range. F8 chord once, then approach until the normal «Открыть»/input hint appears.
2. F8 once while it is visible; move camera/character slightly and F8 once more.
   Walk out of range; F8 can detect hidden/rebound/gone if no hide event arrived.
3. F7 chord stops any remaining observer. Exit normally and inspect the log.

Expected evidence is WAITING → MATCH reciprocal=true/tag=Open/action25 → POSE(s)
→ STOP. No visible UI changes should occur. If no MATCH appears before60s or the
callback budget, retain the negative result. Do not install another hook, scan
components, guess an actor or expand this test during the same run.

A positive result closes **that one live mapping/anchor** seam. World-component
registration, camera-facing pose, scale/readability and Hilda occlusion still need
their own later test. A no-match means this single event route/timing was
insufficient; it is not proof that no live owner relation exists.

## Offline checks and provenance

Project clean/synced at6e9ebddafeeb1bb68a089e280c1a2f89b99924a8, Research main at
bd94dff9b2a992976aefe3a6a7b6c0833589aa19. One project worktree; a separate existing
Research worktree was left untouched. DevRules clean local1dba779 fast-forwarded
to current origin0f4888bb9501afa42e3b9492c5794c98bf58537f; no unpublished work lost.

`python tools/test.py`:83 tests/9 suites pass, including9 new Lua policy tests for
pointer contradictions, exact event matching, no-event negative result, read-only
invariants, advisory sender, changed pose, disappearance/rebind, deferred stop,
native hide and budgets. These mocks do not establish real dispatch, Lua marshaling
of these new getters, native owner/pose values or camera/render behavior.
Local source/input hashes and test output remain ignored in open-binding.

Source references (reviewed local retained copies):
[UE4SS83330635 LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp),
[LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp),
[UE4.27 WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp),
[SceneComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Components/SceneComponent.cpp).
Game-native implementations are not present in UHT stubs. No extracted game bytes
are published. Production gate remains BLOCKED.
