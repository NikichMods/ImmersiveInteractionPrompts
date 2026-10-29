# Deferred World creation — bounded rendering/occlusion/timeout cleanup PASS

**Current V3: bounded runtime PASS2026-10-30; probe DISABLED.** User confirmed
WORLD TEST visibility, partial letters hidden by Hilda and their reappearance.
Native state/readbacks and45s timeout cleanup completed. Manual F7 cleanup was
not exercised before timeout. The first hang's exact cause remains unknown.
Frozen first-run source and its BLOCKED result stay in [the parent report](../README.md).
This proves one World rendering/depth mechanism, not the final composition or
production lifecycle. Production acceptance remains BLOCKED.

## V3 user-run result — 2026-10-30, one natural Open

Exact source6ad93fc302d43c9578792cd339ddf10421f3e0fe, main/helper hashes below
matched installed bytes after exit. Same Steam1.09/build12996889, UE4.27,
UE4SS83330635/DLL baseline; original Screen component remained in use.

| Moscow time | Evidence |
| --- | --- |
| 01:10:19.450 | API-only prepare and two script registrations. |
| 01:10:27.423–.425 /28.006 | Three initialized pairs; init128 closes acquisition only. |
| 01:10:49.238/.251 | Exact natural Open MATCH, queued then dispatched EngineTick. Actor0-1_lootbox_01_mat_ST001, class item_lootbox02_C, its ExtendedWidget and TipHUD_C_2147478021; no old process selector. |
| 01:10:49.260 | Host ABSENT_NULL→one exact LoadAsset→found/did_load=true, LIVE on returned object and fresh lookup. Material LIVE, zero material loads. |
| 01:10:49.261–.270 | Post-load target check and every construct/config/Create/first Slate/private UI/registration/original-check phase returned. CREATED. First sample RENDER_PENDING before render target was ready. |
| 01:11:11.635 /15.901 | Two user F8 STATE snapshots, same render target1620911494464,512×128. Visible3/not-hidden, World0, collision0/overlap/hardware/focus=false, stock masked material/depth-disable=false, scale(.25,.25,.25). |
| 01:11:34.283 | STOP world_timeout,74.833s from arm /45.013s from creation; init128/open3/ready3/show2536/match1/poses3/unmatched0/hooks_remaining0, cleanup queued. |
| 01:11:34.300–.301 | Unbind/destroy/host release phase pairs completed; COMPONENT_DESTROYED native pending-kill check; CLEANED own_widget_holder=false/own_component_alive=false. No forced GC or instantaneous GPU-free claim. |
| 01:11:49.277 | Event loop ends. No probe FAILED/CLEANUP_PENDING/DISPATCH_FAILED events. |

Source anchor in both post-load checks and all3 poses:
(-40619.4648,12241.2139,5672), source rotation(0,109.320808,0), source scale1;
actor origin Z5552. Own component
`0-1_lootbox_01_mat_ST001.IIP_WorldTest_1793311849` at
(-40619.4648,12241.2139,5704), actual rotation
(16.5287838,86.5690613,0), scale.25 in both user snapshots. These are historical
measurements, not selectors or general placement constants.

**User visual evidence:** user performed the scenario and explicitly confirmed
that Hilda covered only part of the WORLD TEST letters and those letters returned
when moving aside. This distinguishes geometry coverage from whole-widget hide
or timeout. The user did not reach F7 before timeout; record timeout cleanup PASS,
**not** manual World cleanup-key PASS. Original identity/visibility/Open and root/
tree checks held; no source original-UI writes or input remapping. This is not an
exhaustive test of all native interaction semantics, actions or input devices.

User also perceived initial shift/turn toward camera followed by stability.
Source performs camera-facing transform once, before registration; no later
billboard/transform setter exists. Two logged actual world poses/angles match,
and expected initial rotation differs only by float roundoff. These snapshots do
not cover the first22s. Changing camera perspective can change the apparent angle
of a fixed plane; it is a plausible explanation, not a diagnosed early movement.
Do not silently treat this as a tested dynamic camera-facing mechanism.

Ignored archive outside loader:
`.local/research/interaction-prompts/world-space/probe/deferred/post-reload-refresh/runtime-pass-20261029T221444Z/`.
UE4SS log SHA256de0d42d942662da4e38298ded3f54908d3993559b23179c01c4f436aaaccb543;
Genesis log SHA2566d532c5857ebaf49e142a2215156010c8f908475ee098964d2d39bc68a0f396f.
Exact payloads, installation manifest, filtered events and result/disable record
retained. Game already closed when inspected; agent did not terminate it. Removed
only own enabled.txt;29 previous mod/loader hashes match,91 current files retain
hashes across disable. Current save/config bytes preserved across disable, not
claimed identical to pre-play data after the user's gameplay.

**Closed gate:** one independent owned World renderer, live natural Open binding,
exact host load after reload, private UI/stock material/native state, user-confirmed
partial Hilda occlusion/reappearance and timer-driven native logical destruction.
Do not repeat this same test just to re-prove it. Open items: manual F7 on the
World sample, continuous camera-facing/distance readability, broader lifecycle,
other geometry/translucency, full Aphes composition/current input hints. A useful
next separate decision is a bounded camera-motion/readability study using this
accepted mechanism, rather than a replacement renderer or another binding probe.
No new payload/design changes or installation are made by this result.

## Authorized V3 installation — 2026-10-30

Exact source `6ad93fc302d43c9578792cd339ddf10421f3e0fe` installed with explicit
user permission, game closed throughout deployment. Source/installed main/helper
SHA256 match the V3 values below; no Lua edits for installation. Only own new
`ImmersiveInteractionPromptsWorldRefreshProbe` directory was created, containing
Scripts/main.lua, Scripts/IIPWorldChild.lua and empty enabled.txt. Only this IIP
marker enabled; V1/V2 retained unchanged/disabled, other mods including CombatHUD
and SoulsEnemyHUD untouched. Pinned UE4SS DLL verified;29 old mod/loader and59
current config/save files retained their hashes. No game launch/termination,
reload/hot reload, production/VERSION or settings/save edits.

Ignored backup outside loader:
`.local/research/interaction-prompts/world-space/probe/deferred/post-reload-refresh/install-20261029T220606Z/`.
Exact Lua copies, initial-state/installed hashes, pretest UE4SS/Genesis logs,
loader settings/mods.txt, verified result and guarded rollback.ps1 retained.
Rollback checks closed host, exact resolved own target and file hashes, refuses
unfamiliar files, and removes only this new probe's own files/directories. Its
PowerShell syntax was checked; rollback was not executed. Pretest logs are not
V3 runtime evidence. That scheduled user-run scenario has now completed as
recorded above; no repetition of the accepted mechanism is requested.

## Current V3 correction — one exact refresh after reload

Recovered clean single checkout at c2a1068ed38a4edaf7f127024f2ba6226ff08cf5 on
research/interaction-prompts-owner; project/DevRules remotes fetched and aligned,
DevRules remains0f4888bb9501afa42e3b9492c5794c98bf58537f. No unpublished work was
overwritten. Changed only this deferred resource seam/tests/docs, not installed
files, production, VERSION, game settings/saves or other mods. Earlier V2 bytes
remain in Git2941123/c2a1068 and the archived installed/run copies above/below.

The observed NOT_LOADED is sufficient new reason to change the old lookup-only
policy. To avoid wasting a load before map reload **and** preserve the total
budget, F8 preparation now checks APIs only, with `asset_loads=0`. The same
BeginPlay+CanShow discovery and explicit EngineTick queue stay unchanged. Once
matched, EngineTick performs:

1. Fresh target/reciprocal UI/native validity and finite anchor check, then discard
   these wrappers. Mark phase creating to suppress own reentrant callbacks.
2. One `refresh_assets` operation; resolve exact HOST and MASK. A live correct
   resource needs no load. Unavailable resources get at most **one LoadAsset call
   each in the whole session**, consumed before entering native code. No loops,
   automatic retries, unload/replacement tricks or loads inside CanShow.
3. Check LoadAsset's found/did_load flags, returned object's live/type/path state,
   then fresh StaticFindObject and returned-vs-looked-up address identity. Wrong
   identity is a hard refusal, not a reason to load something else.
4. Check cancellation/deadline after loading. Re-resolve actor/component/TipHUD,
   native not-PendingKill, Open/Interact25, widget storage/getters/NewUserWidget,
   owner/argument links, original tree/text/actor root, visible Screen state and
   finite world anchor **again after all loads**. No old wrappers span loading.
5. Only then call the existing World.create; it retains lookup-only asset checks
   before allocation. Component/host/Slate/renderer/cleanup code, anchor+32Z,
   scale.25, draw512×128, material and original UI setters remain unchanged.

Limits are still one session/create,≤8 candidates, init128/show4096/120s,≤4
samples, own lifetime45s and explicit F7 cancellation/cleanup. Cancellation is
checked before and after resource refresh; it cannot interrupt an in-flight
synchronous load. A deadline, failed load, mismatched identity or changed UI
refuses allocation. No extra probes or observers were added.

### Exact loader/validity contract and new diagnostics

Pinned UE4SS LuaMod.cpp1245–1275 StaticFindObject delegates to exact lookup and
auto_construct_object; LuaUObject.cpp373–386 wraps a null pointer as an **empty
UObject userdata**, rather than necessarily Lua nil. LuaUObject.hpp172–185
GetAddress for remote UObject returns the pointer value without dereferencing it;
zero distinguishes a null wrapper. IsValid761–775 checks pointer/sentinel/global
map/unreachable but not PendingKill. Native KismetSystemLibrary.IsValid remains
the separate non-null/not-PendingKill predicate (UE4.27 header1984ff).

LoadAsset3334–3381 is game-thread-only, returns object/found/did_load, and can
synchronously invoke LoadObject through AssetRegistry. did_load=true means a
non-null returned pointer in this implementation, **not** proof of current native
validity, expected UClass identity, WidgetTree creation or rendering. No raw memory
or offsets are used to improve these distinctions.

| ASSET state | Observation and policy |
| --- | --- |
| ABSENT_NIL | Lua nil; exact load may be attempted once. |
| ABSENT_NULL | Lua IsValid false, remote address0; exact load may be attempted once. |
| LUA_INVALID | Lua IsValid false, nonzero address; no dereference/path/class query; exact load may be attempted once. Does not diagnose deletion versus unreachable. |
| NATIVE_INVALID | Lua valid, native IsValid false; exact load may be attempted once but a still-invalid return is refused. No forced resurrection. |
| IDENTITY_MISMATCH | Native-live wrong path or resource type; log/stop without loading or allocation. Host native-parent and material-parent/overrides also remain checked. |
| LIVE | Native-live expected exact path/type; no load needed. |

Prefix now IIP_WORLD_V3 / IIP_WORLD_V3_BIND. New pairs:
`target_check BEGIN/END stage=before_refresh`, `refresh_assets`, `resolve_host`,
`resolve_material`, optional **load_host/load_material BEGIN/END**, then
`target_check BEGIN/END stage=after_refresh world_anchor=...` before `create`.
ASSET logs before_load/after_load/before_create; LOAD_RESULT records flags and
return state. Load failure leaves no own component; later creation/cleanup phases
are retained from V2. Logs localize progress, not native stack/deadlock cause.

### Current source identity and checks

[main.lua](Scripts/main.lua) SHA256
`52fbcba729e062451f989557e9f1d690834cd884342a8033c66c7519507ec877`;
[IIPWorldChild.lua](Scripts/IIPWorldChild.lua) SHA256
`ca02673f7258b5459219d3e5cf0fb9e265c937f91875906375f1a8cd806fd33c`.
`python tools/test.py`: **158 tests /12 suites PASS**, deferred suite34 cases
(was15). Added/updated cases exercise per-resource load caps, nil/null/invalid/
native-invalid/identity distinctions, false flags, stale fresh lookup, mismatched
addresses, post-load owner/tree/widget/Open/visibility checks, fresh anchor,
reentry, cancellation/expiry and no allocation on failure. Mocks do not prove
that native loading returns, World renderer works or Hilda occludes the result.
Private audit/tests: `.local/research/interaction-prompts/world-space/probe/deferred/post-reload-refresh/`;
source-hashes.json SHA256c67b672fe68ac1eb7eafa110e901a7e65fde4759d1dc84773857f61fb42517e6.
Git whitespace/relative links/source and installed-file preservation checked.

**The planned V3 run is completed above:** ASSETS_READY→post-refresh target check→
component phases, user-confirmed rendering/occlusion and timer cleanup. Loading
alone was not used as the visual criterion. Do not repeat this accepted mechanism
or older prerequisite tests independently. First-hang cause, manual F7, continuous
camera/distance behavior, broader lifecycle and production remain unverified.

## First deferred run — execution separation observed, host residency gate failed

Exact2941123 installed hashes matched. User reports no cyan WORLD TEST. Logged
00:42:59.389 load_host END/PREPARED before own hook registration; material was
already resident. After manual reload three Open pairs acquired; init128 closed
acquisition retaining3. At00:43:34.870 MATCH and CREATE_QUEUED;00:43:34.884
CREATE_DISPATCHED on EngineTick, about14ms later. Fresh target checks passed;
anchor_camera, look_at and make_transform each have BEGIN/END.

resident_assets BEGIN then FAILED kind=NOT_LOADED at00:43:34.892:
`prepared asset no longer resident: /Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C`.
This gate combines fresh lookup, native validity and exact path. The log cannot
distinguish null lookup, pending kill or a path mismatch; GC/unload is not a proven
cause. It does establish that pre-reload load success did not suffice for the
required post-reload live-class contract in this run.

STOP reason=failure result=NOT_LOADED, init128/open3/ready3/show2/visible_open1/
matches1/poses0/hooks_remaining0/cleanup_queued=false. No component_construct,
host_create, first Slate, registration or CREATED/STATE phase was entered. By source
order the component was never allocated, so no native renderer cleanup was needed
or exercised. Event loop ends00:44:06.144. This is a clean negative gate result,
not World rendering acceptance, proof of first-hang cause or successful creation.

Archived ignored outside loader:
`.local/research/interaction-prompts/world-space/probe/deferred/not-loaded-run-20261029T214538Z/`.
UE4SS log SHA2560c3f4cee9155bc87125c005e4dd2cdae9889c363449bb998ed98d22ec4afbc92;
Genesis log SHA2566a35d73848a0de4697016fbc22fc7d6b403a04ef22cfafe23ba2116f904faafe.
Archive retains payload copies, installation/disable manifests. Game already closed
on inspection; agent did not terminate it. Removed only own enabled.txt;27 previous
mod/loader hashes still match installation,88 current files retain hashes across
disable. Other mods and current settings/saves preserved, with no claim that the
user run itself left pre-play save/config bytes unchanged.

**Historical V2 lookup-only revision remains BLOCKED for another visual test.**
Next minimal candidate seam: allow one explicitly bounded exact host/material
refresh in the queued EngineTick action after reload, with paired load markers,
then re-resolve/revalidate target and UI **after** any synchronous load before
capturing pose or allocating components. Suppress own reentrant discovery during
that preparation. This would reuse the now-observed EngineTick loading route;
it does not require actor scans, old pointers, new geometry or a load in CanShow.
The V3 source correction is now described above; it is not installed and no
repeat run is requested for the unchanged V2 bytes.

## Authorized closed-game installation — 2026-10-30

Exact source `2941123d56f2840e98ce8ca49d81204b8185fbc5` installed after the user's
explicit “Устанавливаем”. Both Lua/source/installed hashes below match. Only new
own directory `ImmersiveInteractionPromptsWorldDeferredProbe` was created, with
Scripts/main.lua, Scripts/IIPWorldChild.lua and empty enabled.txt. Original failing
WorldProbe remains disabled and unchanged; no other IIP probe is enabled.
UE4SS DLL matches pinned ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290.
27 prior mod/loader and59 current config/save files retained their hashes.
CombatHUD/SoulsEnemyHUD/mods.txt and loader configuration unchanged.
Game closure checked repeatedly before writes/enable and after verification;
no game launch/termination, reload, hot reload or Lua-source edits.

Ignored backup outside loader:
`.local/research/interaction-prompts/world-space/probe/deferred/install-20261029T214003Z/`.
It stores exact new Lua copies, pretest UE4SS/Genesis logs, loader settings/mods.txt,
initial-state hashes/installed manifest, verified result and guarded rollback.ps1.
Rollback checks closed game, resolved exact own target and known file hashes,
refuses unexpected contents, then removes only this new directory's own files.
Older disabled payload/failed-run evidence and other mods are preserved. Pretest
logs are historical snapshots, not a successful run of this revision.

At installation handoff it was ready for one user-run scenario; its NOT_LOADED
result and current disabled state are recorded above. No runtime
rendering/occlusion/cleanup PASS is inferred from installed byte identity.

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

## Original V2 execution and lifetime policy (historical)

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

## Original V2 diagnostic phases and procedure (historical)

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

Historical procedure for the completed run: both files were deployed together,
preserving disabled v1 bytes/rollback. One user run
with the existing F8→manual reload→Open→F7 procedure. If it freezes before reload,
the preload markers are already useful; do not repeat or extend the run. If it
reaches WORLD TEST, use the original partial-letter Hilda-occlusion/reappearance
criterion and manual cleanup, without changing camera/visual settings or anchor.
Review the last phase pair alongside both logs before any further correction.

## Prior V2 source and checks (historical)

[V2 main.lua](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/2941123d56f2840e98ce8ca49d81204b8185fbc5/research/interaction-prompts-owner/world-space/probe/deferred/Scripts/main.lua),
[V2 IIPWorldChild.lua](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/2941123d56f2840e98ce8ca49d81204b8185fbc5/research/interaction-prompts-owner/world-space/probe/deferred/Scripts/IIPWorldChild.lua).
Main SHA256 `1b0f4bd4d48e183f04d7501cc28361651e94c2c0e641a9ec126ba8045f79ed38`;
helper SHA256 `eb6cb013af851a765a8d8a40da1d917fb1cd2b8efa0f4890093f099761d057a3`.
Source preparation changed no installed bytes or frozen v1 files; subsequent
installation is recorded above. No production/VERSION edits.

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
