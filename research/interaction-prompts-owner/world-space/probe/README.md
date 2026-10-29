# One owned World component — READY_SOURCE, 2026-10-29

**Source preparation only. NOT_INSTALLED / RUNTIME_NOT_TESTED.** Production and
World rendering/occlusion acceptance remain **BLOCKED**. This is one separately
authorizable experiment, not the final prompt or a production lifecycle system.

## Question and sufficient evidence

Can an independent plain UMG WidgetComponent render a depth-tested `WORLD TEST`
above the exact natural Open object, with Hilda hiding only the letters behind
her, while the original Screen prompt remains? Existing host and binding passes
cannot answer this renderer question. A small owned renderer is sufficient; no
in-place Screen→World migration, shared TipHUD Slate, new engine asset, special
depth mask or new global observer is justified.

Recovered clean project branch `research/interaction-prompts-owner` at
48b6b2b35a5455017a0a76d279d6db6b9be97947, shared Research/main at
4611646b6d21b3990c58cf6eb1743f078e29af9c, DevRules at
0f4888bb9501afa42e3b9492c5794c98bf58537f; fetched remotes matched. No unpublished
work was overwritten. Baseline: Steam1.09/build12996889, UE4.27 Windows x64,
UE4SS v3.0.1-1181-g83330635. Installation identity recorded previously includes
DLL SHA256 ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290;
this stage did not install or launch anything. Recheck installed identity before
any future deployment.

## Source contracts and decisions

| Seam | Evidence / chosen implementation |
| --- | --- |
| Exact natural target | Reuses corrected [BeginPlay + CanShow](../../open-binding/beginplay-probe/README.md), accepted source603ab6b. Only live reciprocal actor/argument/component/widget identity, Open/Interact25 and visible RU `Открыть`; never old process addresses/coordinates or first-found actors. |
| Independent host | Reuses [host-only runtime PASS](../../userwidget-host/probe/README.md): exact PostionItemUMG_BP_C, native WidgetBlueprintLibrary.Create, private WidgetTree/slots, no native Genesis base/Tick. Own component's SetWidget calls TakeWidget, so first Construct must yield Hidden2 before own host is shown3. No AddToViewport. |
| Native ownership before registration | UE4.27 ActorComponent.cpp253ff/282–316: owner is typed actor Outer, native CreationMethod0; cooked PostInitProperties calls AddOwnedComponent. Pinned StaticConstructObject supplies RF_Transient. No direct writes to native arrays or AddComponentByClass/BlueprintCreatedComponents. |
| Registration | ActorConstruction.cpp1165–1208 FinishAddComponent(component, **true**, const FTransform&): OnComponentCreated, no automatic attachment/root promotion, apply transform, RegisterComponent. Plain WidgetComponent OnRegister861ff creates World renderer. All own World/draw/material/input/collision settings precede this call. |
| Exact transform | Reflected KismetMathLibrary.FindLookAtRotation(FVector,FVector)→FRotator and MakeTransform(FVector,FRotator,FVector)→FTransform, called with exact native CDO receivers. No fabricated quaternion or out-parameter ABI. Camera comes from original widget's GetOwningPlayerCameraManager. |
| Plane and size | Native quad is YZ with +X normal. DrawSize512×128, pivot(.5,.5), scale(.25,.25,.25): physical128×32 world units. One camera-facing pose, two-sided, frozen; source anchor movement>0.01 stops. Camera distance allowed80–1500 world units. No dynamic billboard/distance scaling. |
| One bounded offset | Live source component anchor +32 world Z, exactly one quad height, to separate test text from original Screen overlay. This is a first-test geometry choice, not universal placement or a reused recorded coordinate. Root/parent of the original actor/component stay unchanged. |
| Depth material | Exact `/Engine/EngineMaterials/Widget3DPassThrough_Masked.Widget3DPassThrough_Masked`, stock instance→Widget3DPassThrough base. Runtime guards require Masked1/two-sided overrides and base bDisableDepthTest=false. GetMaterial(0) before registration; own MID.Parent/Outer checked on samples. Never mutate shared material. Engine constructor already references stock family; exact LoadAsset is allowed once per needed asset if absent, with no fallback search. |
| No input/physics | Own NoCollision0, overlap events false, bReceiveHardwareInput=false, window focus=false, own host bIsFocusable=false, own UI HitTestInvisible3. TickWhenOffscreen=true avoids visibility-based first-frame starvation during the short test. Original interaction is untouched. |
| Cleanup | Hide/detach own label, SetWidget(nil), own component K2_DestroyComponent(**self**), RemoveFromParent on own host. Native self-caller permission is explicit in ActorComponent.cpp1369ff; DestroyComponent1305ff unregisters/removes only own component membership and marks pending kill. WidgetComponent.cpp1060ff releases widget/window/renderer. GPU cleanup/GC are engine-deferred, never forced. |

**Important validity distinction:** UE4SS LuaUObject.hpp761–775 `IsValid()` checks
pointer/global-map/unreachable, not PendingKill. Destruction is therefore checked
through reflected `/Script/Engine.KismetSystemLibrary:IsValid(const UObject*)`
with `/Script/Engine.Default__KismetSystemLibrary` as receiver. UE4.27
KismetSystemLibrary.h1984–1987 delegates to `::IsValid(Object)` (non-null and not
pending kill). The still-addressable Lua wrapper is not used as a live component
after native destruction. This verifies logical native death, not physical GPU
resource reclamation or final UObject deallocation.

Actual installed UHT declarations were checked for every new reflected seam:
Actor.FinishAddComponent, ActorComponent.K2_DestroyComponent/CreationMethod,
WidgetComponent World/draw/material/window/input methods/fields, UserWidget camera
manager/bIsFocusable, Kismet math and native validity, Material/MaterialInstance
fields, TextBlock.SetColorAndOpacity(FSlateColor). UHT bodies are stubs; native
implementation comes from the pinned UE4.27 source, not generated empty bodies.
The mirror is versioned engine evidence, not recovered Genesis implementation.

## Source, bounds and failure policy

- [Scripts/main.lua](Scripts/main.lua): two proven exact script post hooks, no
  return override; orchestration only differs at the owned-renderer seam.
- [Scripts/IIPWorldChild.lua](Scripts/IIPWorldChild.lua): own component/host/label,
  material guards, fixed pose, samples, partial-allocation rollback.
- [Policy tests](../../../../tests/test_world_child.py): adversarial mocks, not
  engine emulation or visual acceptance.

Main SHA256 `4b54ebc97ab64b6c3ff75ed2216efe3a778591b2cc614d9e257c8060c07443ed`.
Helper SHA256 `9173993d5c6cd0f82f4179d5594418112f12a31b582ff5f68aed3c4b498db6e8`.
Both Lua files are required; no TTF, PNG, private config, compiled assets or new
dependency. Previous accepted binding/host/font sources are unchanged.

Exactly one arm, ≤8 Open attempts, init cap128 closes acquisition only, CanShow
cap4096, total observation≤120s including manual reload. Once matched: one own
composition, maximum45s from creation, no recreation/retarget, ≤4 pose/state
requests including initial match. Ctrl+Alt+F8 arms/checkpoints/samples;
Ctrl+Alt+F7 stops/cleans, and retries pending cleanup without rearming. No engine
access runs directly from the keyboard callback; dispatch uses EngineTick.

Only primitive identities are retained: path/class/address and numeric anchor.
Native actor ownership retains the transient component; its Widget UPROPERTY
retains the own host and the own tree/children retain their UI. Original TipHUD
is used only as Create world context/camera source and read-only identity input,
never passed to SetWidget or moved/reparented/mutated.

Bound matching callbacks recheck identity/visibility/source anchor; errors,
disappearance, hidden original, budget or user stop make hooks inert before
unregistering and independently attempt all own cleanup. If no further callback
arrives, timeout provides the bounded stop (not immediate continuous detection).
An identity mismatch refuses unsafe operations. Cleanup errors log CLEANUP_PENDING
and retain primitive ownership records for explicit F7 retry. Unremoved hooks are
reported; keyboard callbacks and already queued one-shot timers become inert
after successful stop. They are not claimed to be unregistered/unscheduled.
There are no scans, per-frame Lua polls, line traces, visibility tricks or
automatic reloads. Native component render ticks are ordinary WidgetComponent
behavior, bounded by the experiment's own destruction deadline.

## Future single test — only after separate closed-game installation

Deployment must first verify closed game, DLL/source hashes, rollback outside
loader paths, and disable other completed IIP probes without changing other mods.
This document does **not** authorize that installation.

1. Load the familiar save near the unopened Open chest. Press **Ctrl+Alt+F8 once**,
   then manually reload that same save once. Acquisition must observe natural
   BeginPlay; do not start again. Loading and approach must fit the120s limit.
2. Approach until original `F Открыть` is visible. Exact CanShow match creates one
   cyan `WORLD TEST` slightly above its live anchor. Do not open the chest or
   change graphics/settings. If no test text appears, stop with **Ctrl+Alt+F7**;
   do not add offsets/retry in this process or infer occlusion from absence.
3. Within45s, find a small camera/character movement where all letters are visible;
   press **Ctrl+Alt+F8** once. Then place Hilda between camera and text, without
   leaving interaction range or rotating the camera to an edge-on view. Look for
   **partially hidden letters following Hilda's silhouette**, with remaining
   letters visible. Press **Ctrl+Alt+F8** once and capture the two views if possible.
   Move slightly aside to show the same letters reappearing. Original prompt
   must remain visible and input/camera movement normal throughout.
4. Press **Ctrl+Alt+F7**. Own text must disappear; stock prompt/icon stay. No
   recreation should occur on approach. Close the game normally yourself when
   finished and report visible/partial-cover/reappearance/removal separately.
   If45s expiry removes it first, that is timeout cleanup, **not** occlusion.

Logs must pair MATCH/CREATED with STATE (native visible/not-hidden, RT512×128,
exact own MID/material, fixed world position, actual rotation and scale). CREATED
also records the expected camera-facing rotation. Then COMPONENT_DESTROYED with native
pending-kill check, CLEANED and hooks_remaining=0. Initial RENDER_PENDING before
first render tick is diagnostic, not success. STATE alone does not establish a
draw or Hilda occlusion. No full disappearance, wrong-facing plane, chest/wall
occlusion, source hide, FAILED or timeout may substitute for the partial-letter
criterion. Normal depth may also occlude behind walls/chest/opaque foliage; this
is not a Hilda-only mask. Translucent hair/material behavior remains unverified.

## Offline checks and evidence limits

16 new policy tests cover pre-registration configuration/ownership, render-pending
vs ready state, exact material/depth rejection, missing factory, private-tree and
Construct failures, partial registration rollback, native-vs-Lua validity,
detach/destroy retry, source disappearance/movement/hide, timeout, no-match and
one-creation/four-snapshot limits. Existing accepted suites also run. No assertion
claims native renderer behavior from mocks.

Private `.local/research/interaction-prompts/world-space/probe/source-audit.json`
records targeted UHT declarations and engine/UE4SS source hashes; SHA256
`5cfd54c15b54d10430200c01e9024a66da2a348de0e210069fbd0d40d50334e9`.
Local engine snapshots/exports remain ignored; no game asset is published.
Run `python tools/test.py`; Git whitespace, links and public-file hygiene are
checked separately. Runtime-only gates: actual World registration/first Slate/
RT draw, projection/readability, Hilda depth coverage, original UI/control
preservation, and native teardown/resource release in this Shipping build.

Source links (exact revisions): engine
[ActorConstruction](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/ActorConstruction.cpp),
[ActorComponent](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Components/ActorComponent.cpp),
[WidgetComponent](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp),
[KismetSystemLibrary](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Classes/Kismet/KismetSystemLibrary.h);
UE4SS [LuaUObject.hpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/LuaType/LuaUObject.hpp),
[LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp).
