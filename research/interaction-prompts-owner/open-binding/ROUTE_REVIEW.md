# Binding route review after NO_EVENTS — source-only, 2026-10-29

**Preparation follow-up:** [BeginPlay probe source/procedure](beginplay-probe/README.md)
is now READY_SOURCE with105 offline tests, not installed/run. This review records
the preceding route-selection evidence; actual reload/identity/pose remain untested.

**Preferred next design: exact parent Blueprint ReceiveBeginPlay acquisition +
the already proven TipHUD CanShow callback for identity selection.** There is now
a positive Blueprint callsite through the Open-tagged BaseLoot branch, rather
than another guessed native show/setup event. This supports preparation of one
bounded read-only test, **not live binding PASS or a ready World payload**.
No new runtime Lua/DLL/probe was authored or installed in this review.

## 1. Reopened architecture checkpoint

Goal remains an object-relative compact prompt with real scene-depth occlusion by
Hilda, native localized action/hint and unchanged interaction behavior. The
[SetShow result](README.md#runtime-result--2026-10-29) is0 callbacks in31.965s before
user stop, after successful native hook registration. It does not establish that
SetShow is unused, broken, or always bypasses reflected dispatch. Its timing and
dispatch coverage were unproven assumptions; registration alone did not prove them.

| Architecture | Acceptance / cost and remaining risk | Decision |
| --- | --- | --- |
| Separate owned World WidgetComponent + independent host | Normal depth-capable source/material route exists; independent UserWidget viewport lifecycle passed. Still needs exact live owner/anchor, own World registration/material/render/teardown, orientation, distance scale/readability and show/hide/input lifecycle. Ordinary depth also admits walls/chests/foliage. | Retain conditional preferred architecture. Next binding test can be finite and read-only; no justification for cooker/C++/depth-mask expansion. |
| Convert original ExtendedWidgetComponent to World | Same identity gate plus private renderer/screen-layer migration/restoration and Genesis native writes. Setter-only Space change does not allocate the World renderer. | Still unsuitable as first experiment; sharing original live TipHUD in a second renderer is also unsafe. |
| Proven Screen-space50%/78% fallback | Own composition placement/render/manual removal passed. Avoids World registration, world pose, billboarding and distance scaling, but full state/hint lifecycle still needs work. Screen overlay lacks required Hilda depth occlusion. | Lower engineering cost, **does not satisfy the accepted occlusion requirement**. Remains fallback, not an adopted change of design. |

This is an engineering judgment from the listed dependencies, not a measured time
estimate. World work now has a source-grounded next entry, but remains materially
more expensive than Screen. If the bounded dual-script route cannot acquire and
match a pair, stop and reassess before building a broader registry or native bridge.
No repeat of accepted Aphes/host/PNG/CanShow rendering tests is needed.

## 2. Compared entry mechanisms

| Entry / exact owner | Natural timing evidence | Identity available | UE4SS83330635 / test assessment |
| --- | --- | --- | --- |
| `/Script/Genesis.WidgetArgumentComponent:Setup(Actor* Owner,ExtendedUserWidget* Widget)` inherited by TipHUDArgumentComponent | **Unknown.** Native UHT declaration/body stub; no callsite in the304 retained Blueprint script exports. Could occur during native initialization, but that is not established. | Context argument component and two explicit object inputs could form a direct pair. Owner input still needs comparison to context.GetOwner and actor.ExtendedWidget.GetWidget. | Native reflected hook/call contract is known; natural hook coverage is not. Calling Setup ourselves would mutate setup and manufacture the seam. Not preferred for another speculative native-event run. Correct declaring path is WidgetArgumentComponent, not TipHUDArgumentComponent. |
| `/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:CanShow()` → bool | **Live callback proved**:948 callbacks/three widgets in accepted prior run; Open text/identity readable. | Widget only. Its Outer is GameInstance; owning pawn is player, not interactive object. | Known script hook/context-only reader, no return override. Best selection seam, insufficient acquisition seam alone. Reuse proof; do not repeat a CanShow-only test. |
| `/Script/Genesis.ExtendedWidgetComponent:SetArrayData(Actor* sender,int32 display_mode)` | **Unknown.** Exact declaration, but no natural callsite in inspected exports; native body unavailable. | Component context, sender input, NewUserWidget/SenderActor fields. Sender is not proven owning actor. | Supported scalar/object signature is not proof of natural reflected invocation. Do not call setter or hook unknown native ABI. Not preferred without a new callsite. |
| `ExtendedWidgetComponent:SetShow(bool,float,float)` | Registered but NO_EVENTS in the one scoped run. | Component context only if event arrives. | Preserve negative result; no unchanged repeat or automatic longer observation. |
| `BaseGameEventObject_BP_C:ReceiveBeginPlay()` → void | **Positive executable call chain through BaseLoot_BP** below. Happens at natural actor BeginPlay, not necessarily when player approaches an already initialized prompt. | Actor context; direct own ExtendedWidget and TipHUDArgument fields lead to component/widget. | Non-native, zero inputs/void; exact script-hook route supported. Preferred acquisition seam if registered before a new natural BeginPlay generation. |
| `WidgetComponent:GetUserWidgetObject()` → UserWidget* | **Positive Blueprint call at parent ubergraph102.** Calls from native screen-layer code also exist, but their interception is not established. | Component context plus return pointer could pair it directly. | A narrow native getter hook is feasible in principle, but adds a new native-return hook seam. Reading this getter from the actor's script callback uses the same positive chain with fewer marshaling assumptions. No independent hook proposed. |

Absence of Setup/SetArrayData/SetShow callsites is limited to retained exports,
not a whole-game search or proof of absence in native code/other packages. No new
game-asset inventory, native disassembly or global runtime discovery was performed.

## 3. New positive chain and exact script contract

Existing extracted resources establish:

1. BaseLoot_BP's inherited TipHUDArgument template overrides msgTag to **Open**.
2. BaseLoot_BP.ReceiveBeginPlay enters ExecuteUbergraph_BaseLoot_BP at **2152**.
   That exact first instruction is EX_LocalFinalFunction calling
   **BaseGameEventObject_BP_C:ReceiveBeginPlay**, with zero parameters.
3. Parent ReceiveBeginPlay enters its ubergraph at **92**;92 calls Actor's parent
   event,102 reads own ExtendedWidget.GetUserWidgetObject,144 casts TipHUD,
   then219 writes the native HoldPress value to CanHoldPress after cast success.
   The observer must not repeat that write or call BeginPlay manually.
4. Exported parent ReceiveBeginPlay flags are Event/Protected/BlueprintEvent,
   **not Native**, with no input/output properties. Exact target:
   `/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C:ReceiveBeginPlay`.

Pinned LuaMod.cpp4271ff registers non-native callbacks by exact function identity
and uses equal pre/post IDs; the optional third callback is not a separate script
post hook. Its script_hook6324ff dispatches exact Stack.Node with context, removes
return properties from input count and ignores nil callback results. For UE4.22+
the observer is installed on **ProcessLocalScriptFunctionPostCallback**7253, so
this recipe uses the single script callback after the parent body, not a fabricated
pre/post pair. CanShow similarly receives context without a return argument;
returning any non-nil value could override its result and is forbidden.

This is source proof of an executable ancestor call and API support, not proof
that the particular tested live Open actor executes it. Descendants may override
BeginPlay without calling their parent. Other Open classes and all placed objects
are not covered by the one BaseLoot branch. Exact live class and getter availability
must still be measured. A failed cast/null widget at BeginPlay must be recorded,
not repaired by forcing InitWidget or creating/loading anything.

## 4. Minimal next experiment specification — no payload yet

The proposed test uses **two exact script hooks**, a temporary bounded set of
primitive Open-only identity records, and existing game-thread dispatch/readers.
No FindAllOf, actor/component enumeration, polling, permanent actor registry,
unknown ABI, extra native event hook or UI writes.

- Arm only when both exact script UFunctions are already loaded; verify names,
  non-Native flags and extracted signatures. Missing metadata ends as NOT_LOADED;
  no LoadAsset/NotifyOnNewObject/global fallback.
- Registration must precede natural BeginPlay for the actor generation being
  measured. Arming beside an already initialized chest is insufficient. A practical
  future run is: load normal gameplay so metadata is resident, arm, then manually
  reload the same existing save once and approach one Open. No observer-triggered
  reload/spawn/BeginPlay call. Metadata and callback survival over that reload remain
  explicit test gates; do not assume main-menu residency.
- Parent BeginPlay callback obtains its actual actor context. Require BP ancestry,
  own TipHUDArgument.GetOwner==actor, Open/Interact25 and an exact ExtendedWidget
  component whose GetOwner and actor backlink agree. Read GetUserWidgetObject,
  GetWidget and Widget storage; retain a record only when these agree on an exact
  TipHUD instance. Record null/not-ready without forcing initialization or retry.
- Keep only primitive actor/component/widget path/class/address records for at
  most **8 distinct Open candidates**, not all actors. Overall proposed deadline
  **120s**, at most128 acquisition callbacks and4096 CanShow callbacks (the earlier
  948-callback run shows this is a frequent callback). Overflow ends with BUDGET,
  never silently drops candidates and claims unique selection. These are proposed
  research bounds, not production constants or a released implementation.
- On existing CanShow callback with current visible RU Open state, join the actual
  widget identity to **exactly one** candidate. Re-resolve all identities and
  reciprocal pointers; do not pick first/nearest actor or infer owner from sender.
  Multiple matches, rebind, missing identities or expired records refuse capture.
- First MATCH fixes one target and drops other candidates/acquisition ownership.
  Read component world location/rotation/scale separately from actor origin, using
  the already checked const getters. At most4 total pose snapshots, user stop and
  deadline. No continuous tracking/lifecycle framework in this experiment.
- Release only own hooks/local records on MATCH completion, stop, expiry or failure.
  Leave CanShow return, original widget, hints, actions and actor state untouched.
  Log acquisition count/ready pairs/qualified CanShow/matches, so zero acquisition,
  null widget, missing join and pointer contradiction are distinguishable outcomes.

One positive exact join and world pose is sufficient; this is not another CanShow
rendering/host acceptance test. A zero-pair/missing-join outcome is also final for
that run, with no automatic Setup/SetArrayData fallback or heavier observer.

## 5. Evidence status, checks and remaining cost

**PREFERRED_ROUTE_DEFINED / source-sufficient for bounded probe preparation.**
Implementation, installation and runtime testing are separate next stages; none
was performed. Before any future source is called READY, its candidate ownership,
budgets, failure/stop and no-return-override behavior need focused offline tests.
The current actor/component/pose gate is still NOT_OBSERVED.

Offline assertions passed on both entry offsets, BaseLoot parent call/signature,
parent component getter/cast, Open override, script flags and pinned dispatcher.
Reviewed304 **existing** bytecode files for the named native calls; no matching
Setup/SetArrayData/SetShow instructions found. Input hashes and audit result remain
local in open-binding/route-review/audit.json. No Lua source changed; existing83
policy tests were not rerun as a substitute for new native/source evidence.
Markdown links/Git hygiene checked. Clean project/Research checkouts matched the
requested e1b7d9c/dfd611d revisions; DevRules current0f4888b unchanged. Other Research
worktree left untouched. No unpublished changes overwritten.

| Exact retained input | SHA256 |
| --- | --- |
| BaseLoot_BP--ReceiveBeginPlay.bytecode.json |404c2e114fed66b5c277ab1096ac0f2643360c5a6bb73cff5485ed151392461f |
| BaseLoot_BP--ExecuteUbergraph_BaseLoot_BP.bytecode.json |29e1b9ef53cee4eb146849060c1a7bda1d37b1c6ec2c7565d4c81f7c98a14240 |
| BaseGameEventObject_BP--ReceiveBeginPlay.bytecode.json |3b3df6908f23b434e1a1c532b734be26ddc78da3be31a83eb9807793283f19cb |
| UE4SS83330635 LuaMod.cpp |ecc9448999fdac16d4b9181d73f99aafeb8f75dd12ad921e3f7f7922d8298227 |

After a successful join the separate World experiment still needs native own
component registration/resources, actual material depth/render, camera orientation,
scale and safe teardown. Production needs broader object/input/localization/state
lifecycle acceptance. The preferred design is unchanged; World rendering and
production remain **BLOCKED**. If another entry is needed after this test, reopen
the cost/reliability checkpoint rather than accumulate speculative hooks.

Sources: retained BaseLoot_BP/BaseGameEventObject_BP/TipHUD exports and bytecode,
installed UHT declarations, and exact
[UE4SS LuaMod.cpp83330635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp).
Original [World engine/material evidence](../world-space/README.md) and
[Screen fallback result](../viewport/README.md) are reused. No host payloads published.
