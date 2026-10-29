# World-space depth-occlusion study — 2026-10-29

**BLOCKED for an executable World-space payload. Engine/API/material feasibility
is source/static-confirmed; no Asterigos World-space rendering/rollback test.**
No Lua/C++ game payload, install, game launch/termination, hot reload, production
edit, tool installation or settings/save change. Prior probes remain untouched.
Preferred next architecture is **B: a separate, owned plain UWidgetComponent**,
conditional on an independent UserWidget host and exact Open-component binding.
This report does not call a speculative recipe READY.

## Current host follow-up

[Independent host review](../userwidget-host/README.md) found shipped concrete
PostionItemUMG_BP_C with direct UMG.UserWidget base and reviewed own-only callbacks.
The original missing-class blocker is now **host-only runtime PASS**:
[exact result](../userwidget-host/probe/README.md) confirms LoadAsset/Create/private
tree/first-Slate Hidden/show/manual viewport cleanup. Probe disabled; do not repeat
that test. Exact natural Open actor/component/pose remains the next independent
World blocker, followed by World renderer/material/pose/occlusion runtime evidence.
No World payload was created by this follow-up.
The [Open binding report/probe](../open-binding/README.md) completed one NO_EVENTS
run: native SetShow registered but0 callbacks/samples during31.965s until user stop.
No actual component/widget/actor pair or pose was obtained; missing-event cause
unknown. Probe disabled. The source getter contracts remain evidence, but another
natural entry route needed separate review. [Source-only route review](../open-binding/ROUTE_REVIEW.md)
now prefers the explicit BaseLoot parent Blueprint BeginPlay chain, paired with
proven CanShow for exact selection. A separate [read-only join source](../open-binding/beginplay-probe/README.md)
is READY_SOURCE with105 offline tests, not installed/run; no World payload. The host gate passed one
viewport cycle; live binding and World registration/render/occlusion remain BLOCKED.
The original comparison/checkpoint below is retained as historical provenance.

## Recovery and scope

Clean, single research checkout initially at1320ad57665124f18b61244b10c5c7c6980388ea,
then fetched and fast-forwarded the two published decision commits to requested
`cd43bc72737ed1223fc28c6e9fa2d5dba726404f`. No unpublished changes were replaced.
Research checkout78822686... fast-forwarded only to published5a8d495..., preserving
its newer action-observer/field-alias caveats. DevRules current remote
0f4888bb9501afa42e3b9492c5794c98bf58537f checked; applicable engineering/Codex/Git,
runtime harness/integration and licensing rules reused/read. DLL SHA256 still
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290` (UE4SS83330635).
Target remains Steam1.09/build12996889, UE4.27 Windows x64; no whole-install audit.

Accepted direction is object-tied compact Aphes/action UI hidden by Hilda's model
where it is behind her from the camera. Upper Aphes outline0, ornament, native
localized action/input hint and interaction semantics remain required. Existing
X50%/Y78% viewport sample is a verified fallback, not preferred placement.
The accepted font, child creation, ornament import and cleanup runs were reused,
not repeated. Their display success does not prove a 3D render-target/depth path.

## 1. Existing Screen evidence and the important transition boundary

Actual generated UHT `Genesis/Private/ExtendedWidgetComponent.cpp` assigns
Space=Screen, while base UMG WidgetComponent CDO defaults World. Those constructor
assignments reflect loaded CDO values (pinned UEHeaderGenerator.cpp789ff); empty
method bodies/generated returns are stubs. BaseGameEventObject_BP's SCS template
selects TipHUD/DrawSize1000×1000 without a serialized Space override. Exact live
placed-instance overrides and the Genesis native position writer remain unobserved.
UE4.27 SWorldWidgetScreenLayer.cpp92–145 projects component world location into
screen coordinates; that screen overlay has no scene-depth occlusion. User's
preferred change is real depth behavior, not another projected screen offset.

The source `WidgetComponent.h337` setter is only `Space = NewSpace`. It does not
unregister/re-register, remove the screen-layer entry, invalidate all render state
or create a renderer. **OnRegister861–895 allocates FWidgetRenderer only for
non-Screen mode.** A component originally registered Screen may therefore lack
that renderer after a setter-only switch; DrawWidgetToRenderTarget1259ff explicitly
returns when WidgetRenderer is null. CreateSceneProxy731ff also needs it.
This is a concrete initialization boundary, not merely an untested bool setter.

Tick1139ff calls UpdateWidget and branches on Space. World UpdateWidget1631ff can
create a virtual window/material and takes Widget->TakeWidget; its Screen branch
unregisters the virtual window. It does not supply the missing OnRegister renderer
allocation or perform a complete old screen-layer migration. RemoveWidgetFromScreen
1355ff, virtual-window membership, CurrentSlateWidget, MaterialInstance, renderer,
render target and scene proxy have separate ownership. A reflected Space readback
or later tick is not proof of full transition/restoration. These resource operations
are not all reflected setters available to Lua.

SetWidget is not a harmless mode-refresh shortcut: it removes screen membership,
may clear/rebind Widget/SlateWidget, and changes native caches. The Genesis subclass
also exposes NewUserWidget/SenderActor and native SetArrayData/SetShow; their native
implementation is not recovered by the UHT stubs. Rebinding the live original is
not used as an assumed rollback or preserved native lifecycle.

## 2. World rendering and the installed material family

World mode creates a scene proxy, renders Slate into a texture and draws a quad
in SDPG_World. WidgetComponent.cpp365–389 constructs a local YZ plane, with +X
normal, from render-target dimensions and Pivot, then applies component transform.
It is not the camera-facing screen-layer path. CanBeOccluded573 returns the inverse
of material disable-depth relevance; MaterialInterface.cpp195 sets that relevance
for translucent base materials from bDisableDepthTest. This is not itself a
per-pixel visual test in Asterigos; the ordinary material/render pipeline must run.

Bounded existing CUE4Parse1.2.2 extraction from installed **base** Paks: exactly
seven `Engine/Content/EngineMaterials/Widget3DPassThrough*.uasset` packages, no
broad inventory or mod override. Parent graph:

| Material | Parent | Serialized interpretation |
| --- | --- | --- |
| Widget3DPassThrough | none | Material, Unlit, Translucent |
| _Masked | base | blend override Masked, explicit TwoSided=true |
| _Masked_OneSided | _Opaque | blend override Masked; two-sided override enabled, false value omitted/default |
| _Opaque | base | blend override enabled, Opaque omitted/default; TwoSided=true |
| _Opaque_OneSided | _Opaque | blend/two-sided overrides enabled, default Opaque/false |
| _Translucent | base | Translucent, TwoSided=true |
| _Translucent_OneSided | _Translucent | Translucent, two-sided override enabled/default false |

All six instances resolve to the same base. No serialized bDisableDepthTest=true
was found on that base; actual UHT UMaterial CDO sets bDisableDepthTest=false.
Absent serialized values are interpreted with the class/default provenance,
not treated as an explicit stored false or a live shader measurement. No compiled
DX11 shader/RHI draw or Hilda occlusion has been tested. UWidgetComponent's CDO is
Masked/one-sided/Plane, with no hardware-input reception. GetMaterial(0) prioritizes
OverrideMaterials, then BlendMode/two-sided family: **packaged assets do not prove
which material is active on the actual ExtendedWidgetComponent**. A future attempt
must inspect GetMaterial(0)→GetBaseMaterial().bDisableDepthTest and reject unknown
or disabled-depth overrides; never mutate the shared base material.

Base export SHA256
`50f69813fcca27b7b7b59b41ab9d5bbaadafe0a689851fcd737e29d0b32a2533`;
Masked_OneSided export
`b1c11f8f940bce8600d73923ca2fc941fdc995b86246ea1592ca75696bfb2ac1`.
These identify local CUE4Parse JSON, not the original package bytes or loaded shader.
Full seven-file hashes/parent checks and raw exports stay under ignored
`.local/research/interaction-prompts/world-space/`.

Conclusion: stock depth-capable World UI materials exist; an authored texture,
depth-mask, CustomDepth or post-process is not currently justified. Ordinary depth
also admits chest/wall/opaque or masked foliage occlusion; it is not Hilda-only.
Translucent hair/vegetation/particles need separate visual assessment.

## 3. Actual reflected API and ownership contracts

| API / data | Confirmed contract and limit |
| --- | --- |
| EWidgetSpace | Actual UHT enum World0, Screen1 |
| WidgetComponent.SetWidgetSpace / GetWidgetSpace | void setter(enum), enum getter; setter-only transition limitation above |
| WidgetComponent.SetWidget / GetWidget | UUserWidget pointer, not arbitrary UWidget; cached Slate ownership matters |
| WidgetComponent.SetDrawSize, SetPivot, SetTwoSided | FVector2D/FVector2D/bool setters; texture size and physical world scale differ; two-sided is not billboarding |
| PrimitiveComponent.GetMaterial(0), MaterialInterface.GetBaseMaterial | Reflected material/base pointers; Material.bDisableDepthTest is reflected; no live query was executed |
| Actor.AddComponentByClass / FinishAddComponent | (class, manualAttachment, const FTransform&, deferredFinish)→component; (component, manualAttachment, const FTransform&)→void |
| ActorComponent.K2_DestroyComponent | Explicit UObject caller; native code permits self/owner (or explicit allow-anyone), then destroys/unregisters; not an instant-GPU-free promise |
| SceneComponent | K2_GetComponentLocation/Rotation, K2_GetComponentScale, SetRelativeScale3D/SetWorldScale3D; K2 world/relative rotation/location setters have sweep/out FHitResult/teleport contracts |
| KismetMathLibrary.FindLookAtRotation | FVector start/target→FRotator; faces component +X toward camera for an initial planar pose; no automatic tracking |
| UUserWidget.GetOwningPlayerCameraManager | Reflected camera manager; owning player is not the world interaction actor |
| WidgetBlueprintLibrary.Create | WorldContextObject, UserWidget subclass, OwningPlayer; base UUserWidget is Abstract and is rejected by engine class validation |

Pinned UE4SS LuaMod/UE4SSProgram and LuaUObject contracts from the earlier exact
review are reused: StaticConstructObject with explicit RF_Transient, exact UFunction
lookup/calling context, UObject references, typed structs. LuaUObject.cpp751–827
copies matching native structs or converts Lua tables over reflected fields.
FTransform reflects Rotation(FQuat X/Y/Z/W), Translation and Scale3D, unlike opaque
FGeometry. An identity transform must include unit quaternion and unit scale, not
an empty/zero table. This generic marshalling proof is not an executed component
registration/rotation/out-parameter test; no raw offsets or ABI guesses are used.

AddComponentByClass is more than allocation: ActorConstruction.cpp1140–1184 creates
an actor-owned component, PostCreateBlueprintComponent adds it to
BlueprintCreatedComponents, FinishAddComponent invokes OnComponentCreated, optional
autoattachment/root promotion, applies transform and registers. The helper supplies
no RF_Transient argument. Do not call this automatically on a native game actor
and declare it nonpersistent merely because eventual cleanup is planned.

A cleaner conditional candidate is plain UMG WidgetComponent allocated with the
already known StaticConstructObject RF_Transient contract and exact actor Outer,
then reflected FinishAddComponent(manualAttachment=true, complete transform).
ActorComponent.cpp282ff adds native actor-owned components; FinishAddComponent
performs registration, provided ownership/class/default invariants hold. Configure
own World mode **before registration**, NoCollision/no overlaps, hardware input
false and window focus false before enabling. Never promote/replace actor root or
write native component arrays directly. DestroyComponent1305ff removes own component
membership; WidgetComponent.DestroyComponent/ReleaseResources1060ff releases its
widget/window/renderer with deferred engine cleanup. None of this recipe is a
runtime-validated payload; original actor serialization/lifecycle remains a gate.

## 4. Route comparison and decision

| | A — existing ExtendedWidgetComponent | B — separate plain World WidgetComponent |
| --- | --- | --- |
| Advantage | Original localization, input/material producers and show/hide stay naturally connected | Original TipHUD and its renderer remain untouched; no in-place migration/restore |
| Required work | Exact live component/transform/material; renderer registration and old screen-layer removal; finite snapshots of mutable state do not cover private renderer caches | Independent safe UserWidget, exact target owner/pose; transient allocation/finish-registration/no-collision; own orientation/scale and teardown |
| Principal risk | Renderer absent after setter; stale/duplicate screen attachment or world proxy; native Genesis writes; rebuilding original Slate/native construct behavior | Host viewport lifecycle passed, but World rebuild/resource lifetime remains untested; sharing the same live widget across renderers and improper actor component persistence/collision remain unsafe |
| Cleanup | Returning Space/scale/material values alone cannot prove native resource restoration | Conditional self-destroy/own-resource release path is source-visible; original needs no restoration; actual destroy/GC still untested |
| Decision | Not a safe first payload; do not replace simple setter with blind re-registration/SetWidget(original) calls | **Conditional preferred architecture, BLOCKED** at live binding/World runtime; independent host viewport gate has passed |

A live TipHUD cannot be used as B's SetWidget argument to dodge the missing host:
UWidget.TakeWidget returns cached Slate content, not a deep UI clone. It would
share/reparent rendering state. The successful UFont Template-copy result does
not establish independent UUserWidget/WidgetTree/Slate duplication. The earlier
HUD-root sample created Canvas/TextBlock/Image children; a CanvasPanel is not a
UUserWidget and cannot be passed as one to SetWidget.

Base UUserWidget is Abstract. The known concrete ExtendedUserWidget/TipHUD inherit
a game native base; UHT stubs do not recover native Initialize/Construct/Tick
contracts. Bounded review of already retained IndicateTip_UMG and
IndicateTipItemWidget_BP did not produce an inert replacement: both inherit
Genesis classes and bClassRequiresNativeTick=true; the former also initializes
boss-rush state via its own native API. This is not proof that all game UI classes
are unsafe or that no empty class exists. A narrow Blank/Empty widget-name lookup
found only an image asset, not a reviewed empty concrete UserWidget class. No
broader package-class inventory or automatic native bridge/cooker installation.

Likewise no proven inverse link from a CanShow UUserWidget to its owning world
WidgetComponent was established. Component.InitWidget uses CreateWidget(World),
whose outer can be GameInstance; GetOwningPlayerPawn is Hilda, not the interactive
object. NewUserWidget/SenderActor are component-side properties. The retained first
CanShow run (948 callbacks/three widgets) already records all three TipHUD full
names under MainGameInstance_BP_C, not an actor/component path. This existing
runtime identity evidence is reused; it does not supply a component backlink or
a new World test. The existing actor→component→widget Blueprint evidence is not its inverse. Do not pick the
first loot actor/component, spawn beside Hilda and pretend it is the actual Open
anchor, or install a global object scan to discover it.

## 5. Readability/pose and the bounded test that is not yet READY

- World quad dimensions follow render-target pixels × component scale. At fixed
  scale projected text shrinks approximately as inverse camera depth. Matching
  the old constant pixel size would add distance-aware scaling, not happen from
  SetWidgetSpace. First test should use one bounded distance, no scaling framework.
- World plane follows component transform, not camera rotation. One-sided can
  disappear from behind; two-sided can show reversed rear text and still goes
  edge-on. First proof can freeze one source-confirmed camera-facing pose with
  limited lateral movement; production camera billboarding would be a separate seam.
- Original Screen anchor may be inside the chest/actor. World geometry can hide
  the entire plane; capture the real component pose and choose a justified bounded
  offset above the object. No guessed source actor or arbitrary model-specific offset.
- Increasing DrawSize improves render-target sampling, not physical UI size by
  itself. Masked edges/thin ornament, distance, oblique filtering, AA and scene
  post-processing can reduce legibility. Own NoCollision/focus/input guards must
  prevent interference with native interaction traces.
- Occlusion should be assessed only when the plane is behind Hilda along camera
  rays. No positive occlusion result is manufactured by hiding the widget, using a
  line trace, or moving it inside chest/wall geometry. The stock prompt remains.
- Native show/hide/locked/hold/input updates remain unmodified on the original.
  A future sample may copy one Open state only; it must not claim production
  semantics/lifecycle from that snapshot or from a one-view occlusion frame.

**Next cheapest sufficient evidence:** first establish one independently creatable
concrete UserWidget host through the real Create/Initialize contract, with reviewed
base/construct/tick behavior and own WidgetTree/Slate ownership. A bounded check of
one candidate is sufficient; do not build a new general observer. If no existing
inert class can be confirmed, supplying an authored empty UE4.27 widget class is an
explicit missing dependency (cooked/native authoring infrastructure is separate,
not installed or invented here). Before an executable World Open sample is READY,
validate the exact naturally loaded Open component/owner/pose/material binding as
well. Component-side SetArrayData(sender,display_mode) is a narrow declared read
candidate, not an authorized or implemented native hook/result.

Then one short separately permitted test would create only the own no-collision
component/widget, use native depth-tested stock material, demonstrate Hilda crossing
in front while the original prompt remains, and explicitly destroy only its own
objects. No installation or runtime permission is inferred from this plan.

## Checks and source identities

Offline audit traversed all seven extracted material parents without cycles,
checked base fields against the UMaterial CDO default, distinguished enum/CDO data
from generated method stubs, checked reflected lifecycle/transform signatures and
pinned Lua struct-copy contracts. The renderer allocation/setter/no-renderer return
paths were read directly. Existing runtime source/probes/VERSION remained untouched;
no new unit suite asserts guessed native behavior. Git whitespace/local Markdown
links/public-file hygiene are checked. These checks do not prove the game renderer.

UE4.27 source mirror revision `306a7e9f7fb53f14c2cb3bfd3854ad906710a17e`:
[WidgetComponent.h](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Public/Components/WidgetComponent.h),
[WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp),
[ActorConstruction.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/ActorConstruction.cpp),
[ActorComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Components/ActorComponent.cpp),
[MaterialInterface.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Materials/MaterialInterface.cpp).
[Official Epic UE4.27 overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-components?application_version=4.27)
supports World-mesh/Screen-overlay semantics, not this game's runtime result.
The mirror is engine-version evidence, not recovered Genesis binary source.
Local manifests retain exact URLs/hashes; raw engine/game exports stay ignored.

### Local material-export identities

| Export | SHA256 |
| --- | --- |
| Widget3DPassThrough.json | 50f69813fcca27b7b7b59b41ab9d5bbaadafe0a689851fcd737e29d0b32a2533 |
| Widget3DPassThrough_Masked.json | 7fe9e1eb9532c15091f951462dab9ef2142e81d3473c0673d4fd1a96880e71c8 |
| Widget3DPassThrough_Masked_OneSided.json | b1c11f8f940bce8600d73923ca2fc941fdc995b86246ea1592ca75696bfb2ac1 |
| Widget3DPassThrough_Opaque.json | 537632a0967e742f7d2e47cdd6fce3fbded401b41159aaa4b81dee082591e911 |
| Widget3DPassThrough_Opaque_OneSided.json | 4c4bd48531f3c013c3ce19f93867b7fd5b4fad306b271130434aff0de7a649c0 |
| Widget3DPassThrough_Translucent.json | f7172f19cdef0bd2d88cd00628e15a31c98985ab8998698ba9a5f1a9ff04ecaa |
| Widget3DPassThrough_Translucent_OneSided.json | 2a16f4ef62d5013544fc2e90e8d56b80e012b6721a69dd6dd8dc9dfb8a6e9f47 |
