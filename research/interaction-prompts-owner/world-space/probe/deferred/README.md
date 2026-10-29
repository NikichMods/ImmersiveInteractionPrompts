# Deferred World creation — READY_SOURCE diagnostic revision, 2026-10-30

**NOT_INSTALLED / RUNTIME_NOT_TESTED.** This revision removes the inline creation
path and adds bounded phase diagnostics. It is not a proven fix for the hang.
Frozen first-run source and its BLOCKED result stay in [the parent report](../README.md).
World visual acceptance and production remain BLOCKED.

## Question, method and conclusion

Question: did executing a loading/UMG creation chain inside CanShow's script
callback introduce a concrete context risk absent from the successful independent
host test, and can a supported queue isolate that chain? Exact source is sufficient
to answer the scheduling/lock question. The logs cannot recover the blocked native
stack; one later separately authorized phase-marked run is needed for that.

Clean single project checkout recovered at b3db2fd8f164daa1b8b653beadaf7d2f77d9fdff,
on research/interaction-prompts-owner, no unpublished work overwritten. Project
and DevRules remotes fetched; DevRules unchanged0f4888bb9501afa42e3b9492c5794c98bf58537f.
Existing Asterigos-Research R-016/R-017 and accepted host/binding evidence reused.
No new world scans, native hooks, assets, tools, game run or installation.

**Established source difference:** pinned UE4SS83330635 LuaMod.cpp6324ff
`script_hook` acquires global `m_thread_actions_mutex` (recursive) before dispatch
and holds it across the Lua callback. Original main.lua logs MATCH, then calls
World.create synchronously before returning. By contrast, ExecuteInGameThread
EngineTick4331–4404 queues a SimpleLuaAction; it never calls the supplied function
inline. `process_simple_actions`3793–3834 moves the queue under the mutex, releases
that scope, then invokes Lua. `engine_tick_hook`4130–4164 processes the queue
outside its short lock scopes and merges newly queued actions only afterwards.
The accepted host probe's F6 handler used this explicit EngineTick route.

Recursive mutex allows same-thread reacquisition; that fact **does not** protect
against another thread needing the mutex while the game thread waits for that
thread's loading work. A load/construct/Slate chain while retaining this mutex is
a plausible cross-thread wait/reentrancy risk. No hang dump or two-thread stack
proves that cycle in this session. EngineTick removes this outer script-callback
lock/context, not every engine/Slate lock or possible native hang. It is not a
worker thread and does not make arbitrary engine APIs nonblocking.

The cheapest change remains the same independent World component architecture.
Changing materials, geometry, anchor, adding a cooker/native bridge or abandoning
the accepted depth requirement would not follow from the present evidence. A
direct source comparison is sufficient for this seam; unrelated UI experiments
and broad diagnostic mechanisms add no necessary evidence.

## Complete old path and blocking boundaries

The old MATCH was after reciprocal Open actor/component/widget validation and
BeginPlay hook release. World.create then performed the following synchronously
on that CanShow stack; CREATED was printed only after the whole sequence.

| Old operation | Exact source contract / possible work / evidence limit |
| --- | --- |
| Anchor, camera, native IsValid, LookAt/MakeTransform | Native getter/math/struct marshalling path; these too preceded any creation marker. They cannot be excluded from the old log gap simply because they look cheap. |
| Exact host/material resolution | StaticFindObject is lookup; on miss old asset() called LoadAsset. UE4SS LuaMod3334–3381 requires game thread, gets AssetRegistry data, then UAssetRegistryHelpers.GetAsset. UE4.27 Helpers.cpp55–58 delegates to FAssetData.GetAsset; CoreUObject/Public/AssetRegistry/AssetData.h279–294 calls FindObject then **LoadObject** on miss. Synchronous load completion can wait/initialize dependencies. No successful `Asset loaded` marker follows old MATCH, but residency and exact stuck call were not recorded. |
| StaticConstructObject(component) | Pinned LuaMod1916–2023 immediately invokes UObjectGlobals.StaticConstructObject; native object initialization/PostInitProperties happens synchronously. WidgetComponent ctor loads stock material references, even if explicit Lua LoadAsset was skipped. Preloading does not prove absence of all internal loads. |
| Component configuration/SetMaterial | WidgetComponent.cpp707–728 SetMaterial invokes UpdateMaterialInstance→UMaterialInstanceDynamic.Create and render-state dirtiness. It is more than a scalar assignment. |
| WidgetBlueprintLibrary.Create | UE4.27 cpp37–61 chooses CreateWidget context. UserWidget.cpp109ff Initialize runs generated-class InitializeWidget/private tree setup and possibly NativeOnInitialized. Known PostionItem callbacks are bounded, not proof that allocation/initialization is safe on every outer stack. |
| SetWidget(host) | WidgetComponent1596–1611 assigns own Widget then UpdateWidget.1631ff takes Widget.TakeWidget, builds/updates virtual Slate window/material. Widget.cpp803ff first TakeWidget rebuilds Slate and calls OnWidgetRebuilt; UserWidget750ff/1336ff reaches NativeConstruct/Blueprint Construct. Hidden2 is therefore an expected native lifecycle result, not an ordinary pointer-set invariant alone. |
| Own private UI | TextBlock construction, Font struct copy, Slate/slot configuration. No original UI setters. Still part of the unmarked gap in the old run. |
| FinishAddComponent | ActorConstruction1165ff OnComponentCreated→manual transform→RegisterComponent; ActorComponent registration can initialize/begin play for the own plain component. WidgetComponent.OnRegister861ff creates World renderer; render/physics state and world delegates are involved. Completion was never logged in the old run. |
| Original recheck, CREATED, timer | Final identity/anchor checks and CREATED preceded scheduling45s timer. Old log has neither CREATED nor cleanup/STOP; absence is not proof of a particular failed stage or successful partial rendering. |

**Placement policy for this revision:** all asset resolution/loading, construction,
Create/first Slate/registration, and own teardown run only from explicit EngineTick
actions after the CanShow callback returns. This is a conservative local policy
derived from the context risk and the accepted host route, **not** a claim that
UE4.27 categorically forbids every Create/SetWidget in every Blueprint callback.
Read-only binding/getters and proven hook release remain on the original route.

## New execution and lifetime policy

1. First F8 queues EngineTick control. One `prepare` attempt resolves exact host
   class and stock material, calling LoadAsset at most once each only on lookup
   miss. Validate host parent/material, then register the same two script hooks.
   The total120s deadline starts before preparation; if preparation returns late,
   fail without registering hooks. No game object/component is created here.
2. Natural BeginPlay acquisition/CanShow matching is unchanged. MATCH stores only
   path/class/address records for actor/component/widget plus original tree/text/
   actor-root identities. Phase becomes pending; enqueue **one** EngineTick create
   action. No captured UObject wrappers, callback context or borrowed parameters.
3. The action checks phase/deadline/cancellation, resolves all identities freshly,
   checks native not-PendingKill, reciprocal Open links, exact tree/text/root,
   original visible Screen state and RU action. It then marks phase creating,
   preventing reentrant own hooks from retargeting or allocating duplicates.
4. Creation uses **lookup-only** host/material resolution. Preloaded assets may
   be collected/unloaded by manual map reload; no GC rooting or cache-lifetime
   promise is made. Missing or pending-kill asset yields NOT_LOADED with no new
   LoadAsset call, no fallback and no component allocation. Shared asset identities
   may legitimately change on reload; exact class/path/type is revalidated, not
   an old asset address used as a live selector.
5. On return, phase bound and the same bounded pose/state sample. Original anchor
   +32Z, render target512×128, scale.25, stock Masked material, fixed orientation,
   WORLD TEST/font/color/slots and original TipHUD remain unchanged from v1.
6. Stop/hide/error marks stopped and releases own hooks immediately. Any native
   cleanup is queued to EngineTick, never called inline from script callback.
   STOP may precede CLEANED; `cleanup_queued=true` is **not** completed cleanup.
   F7 records a Lua cancellation intent before scheduling control, so already
   queued creation can be cancelled. Cleanup errors retain ownership records for
   explicit F7 retry; queue failures are reported, no automatic retry/rearm.

Same bounds: one preparation/session/creation,≤8 Open candidates, init128 closes
only acquisition, show4096, total120s,≤4 samples, own creation≤45s. No continuous
world tracker. Deadline checks/timers do **not** interrupt a native call that has
not returned. The expected executor separation still needs runtime confirmation;
mock queue/reentrancy checks are not native-thread or load-progress proof.

## Diagnostic phases and sufficient next test

Prefix `IIP_WORLD_V2` / `IIP_WORLD_V2_BIND`, bounded fixed phase names:

| Markers | Narrow interpretation |
| --- | --- |
| prepare / resolve_host / resolve_material | Before own hooks. Optional nested load_host/load_material BEGIN/END only if a real LoadAsset call is needed. PREPARED means this phase returned. |
| MATCH → CREATE_QUEUED → CREATE_DISPATCHED | Binding succeeded; one action enqueued; then actual EngineTick execution/fresh validation began. Neither queue marker claims allocation. |
| create / anchor_camera / look_at / make_transform / resident_assets | Entry and prerequisites. A missing END localizes an interval, not an exception cause or native stack. |
| component_construct / component_configure / component_material | Allocation vs initial settings vs own MID creation. |
| host_create / widget_bind_first_slate | Independent native Create vs first Slate/Construct/window. |
| private_ui / label_construct / finish_component / verify_original | Private child setup vs native registration vs postconditions. |
| cleanup_unbind / cleanup_destroy / cleanup_host_release | Native ownership removal phases. CLEANED/native logical death is separate from deferred GPU/GC completion. |

Every listed phase has BEGIN and END on success. Failed calls can leave an
unmatched BEGIN followed by FAILED/STOP/cleanup; a hang can leave only BEGIN.
Log buffering/process exit may truncate evidence, so no marker alone proves the
root cause. No high-frequency progress printing or new observers were added.

Next sufficient step, after separate installation authorization: deploy **these
two files together**, preserving the disabled v1 bytes/rollback. One user run
with the existing F8→manual reload→Open→F7 procedure. If it freezes before reload,
the preload markers are already useful; do not repeat or extend the run. If it
reaches WORLD TEST, use the original partial-letter Hilda-occlusion/reappearance
criterion and manual cleanup, without changing camera/visual settings or anchor.
Review the last phase pair alongside both logs before any further correction.

## Source and checks

[main.lua](Scripts/main.lua), [IIPWorldChild.lua](Scripts/IIPWorldChild.lua).
Main SHA256 `1b0f4bd4d48e183f04d7501cc28361651e94c2c0e641a9ec126ba8045f79ed38`;
helper SHA256 `eb6cb013af851a765a8d8a40da1d917fb1cd2b8efa0f4890093f099761d057a3`.
No installed bytes or frozen v1 files changed. No production/VERSION edits.

`python tools/test.py`: **139 tests /12 suites PASS**, including15 new policy
tests for enqueue-before-create, duplicate callback/reentry, native validity/
identity/tree/hide changes, expiry/cancel, preload-before-hooks and no load after
reload, phase boundaries, partial registration and deferred cleanup/retry. Mocks
reject construction/registration/Create from inside script callbacks. They model
thrown failures, **not** a native deadlock or actual successful world rendering.
Whitespace/relative Markdown links/public-file hygiene checked separately.
Private `.local/research/interaction-prompts/world-space/probe/deferred/`
retains test output and source hashes; source-hashes.json SHA256
`c1c856861a6d3a602ea02d4e87bf9b1144e52dff381b33ef1b12225cd46e1932`.

Primary exact source references: [UE4SS LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp),
[UE4.27 AssetRegistryHelpers.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/AssetRegistry/Private/AssetRegistryHelpers.cpp),
[CoreUObject AssetData.h](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Public/AssetRegistry/AssetData.h).
Engine Create/Slate/registration sources and exact UHT are those already recorded
in the parent report. New copies remain ignored, not redistributed.
