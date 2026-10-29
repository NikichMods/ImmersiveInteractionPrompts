# World orientation/readability — INSTALLED, RUNTIME_PENDING

2026-10-30. Comparison source based on frozen accepted V3. Authorized installation
completed below; no game launch/reload or new runtime acceptance. Production BLOCKED.

## Authorized installation — 2026-10-30

User explicitly requested installation. Exact source commit
`6d44daa28b4dcc1cf0109b6f6d3c4fcb06467a9f`; source/installed SHA256 match the
values below, Lua unchanged. Only new own directory
`ImmersiveInteractionPromptsWorldOrientationProbe` contains Scripts/main.lua,
Scripts/IIPWorldChild.lua and empty enabled.txt. It is the only enabled IIP probe;
all12 previous IIP directories remain disabled and unchanged. mods.txt unchanged:
CombatHUD and SoulsEnemyHUD enabled as before.

Asterigos/Genesis processes absent before and after installation. Steam manifest
build12996889, latest loader log identifies83330635; UE4SS DLL SHA256
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`
matches prior baseline.29 historical mod/loader hashes match; all31 current
mod/loader files and59 current config/save files retain hashes across install.
No game launch/termination, hot reload, settings/save write or other-mod change.

Ignored backup outside loader:
`.local/research/interaction-prompts/world-space/orientation/install-20261029T224843Z/`.
Contains exact two Lua copies, pretest UE4SS/Genesis logs, mods.txt/settings copies,
initial-state/installed hash manifests, verified result and guarded rollback.ps1.
Rollback checks game closure, exact own target and unchanged files before removing
only this new directory; prior state was absent. Syntax PASS, not executed.

Installation PASS is not runtime rotation/marshalling/readability/F7 acceptance.
Next step is the single user-operated camera comparison/manual cleanup below.

## Question and minimum sufficient experiment

Can ordinary camera movement keep a World prompt readable using one small
rotation updater, and is that preferable to a fixed plane? V3 already proves
binding, host, World rendering, Hilda occlusion and timeout destruction. Those
results are reused, not reopened. Manual F7 cleanup remains an independent gap.
The earlier perceived initial movement is still unexplained; two late identical
world rotations do not establish motion during the first22s.

| Option | Consequence | Cost and decision |
| --- | --- | --- |
| One initial FindLookAtRotation | No later rotation calls. A plane becomes oblique as the camera changes position; 60-degree incidence halves its projected width, near90 becomes edge-on; the two-sided material can expose reversed text from behind. | Simplest baseline, preserved as initial mode. A restricted camera arc has not been accepted as UX. |
| Update point-facing pitch/yaw | Reuse FindLookAtRotation from own fixed position to current camera location; roll0. | One bounded scheduler and registered-component setter. Selected for comparison, not adopted production billboard. |
| Yaw-only, camera-roll alignment, automatic distance scaling | Yaw alone leaves pitch foreshortening; view alignment/scaling introduces different geometry and UX decisions. | No new implementation for this test. |

Recommendation: compare fixed and follow in the same short run. Ordinary camera
movement makes a permanent fixed plane an unlikely final solution, but smoothness
and readability cannot be accepted from source. Rotating the camera in place does
not change the camera-to-plane direction; orbit/translation does. Follow targets
the camera position, not its forward vector. No decorative animation is added.

## Exact contract and evidence boundary

Installed baseline remains Steam1.09/build12996889, UE4.27, UE4SS83330635.
Local installed UHT `Engine/Public/SceneComponent.h:156` declares:

```cpp
void K2_SetWorldRotation(FRotator NewRotation, bool bSweep,
                        FHitResult& SweepHitResult, bool bTeleport);
```

[UE4.27 SceneComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Components/SceneComponent.cpp)
3839–3842 passes a null hit pointer when sweep=false. SetWorldRotation1475ff
uses the native relative-rotation/movement path; SetRelativeLocationAndRotation
1229ff updates component-to-world/render state. This is appropriate for an
already registered, unattached own scene component. Direct reflected writes to
RelativeRotation would skip the native setter's side effects and are not used.

Pinned [LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
153ff zero-initializes parameter memory,229ff requires a Lua table for non-const
OutParm,287ff copies output back/reuses the table and releases its registry ref.
The struct converters initialize provided fields and read supported properties;
unsupported fields are skipped. The call is `c:K2_SetWorldRotation(rot,false,{},true)`:
fresh hit table, no sweep, teleport, no returned hit data used or retained.
Installed UHT also contains HitResult. This source analysis supports preparing
the call; actual FHitResult marshaling and registered renderer rotation remain
**NOT_RUNTIME_TESTED** in this Asterigos process/version. First setter BEGIN/END
markers and readback distinguish entry, return and angle verification failures.

Pinned [LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp)
EngineTick execution queues work; the queue invokes actions outside its queue
mutex. ExecuteInGameThreadWithDelay uses the configured/default execution method,
not an explicit EngineTick argument. Therefore its callback only queues an
explicit EngineTick action. All camera/native reads and setter calls happen there,
after script callbacks return. No original Tick hook, world scan or asset lookup
beyond exact known identities. No CancelDelayedAction ownership assumption.
Local source/UHT hash manifest stays ignored under `.local/research/interaction-prompts/world-space/orientation/`.

## Source and bounds

[main.lua](Scripts/main.lua), [IIPWorldChild.lua](Scripts/IIPWorldChild.lua).
Frozen V3 files under `../probe/deferred/Scripts` are unchanged.

- Start fixed. Ctrl+Alt+F6 toggles follow/fixed; switching back freezes the current
  angle, without snapping back to the initial angle.
- At most one100ms timer/action outstanding, rescheduled only after completion;
  at most10 checks/s, slower under load, no catch-up. Rotate only when facing
  error>=1degree; read back error<=0.1degree. No per-poll log flood.
- At most450 checks /45s after creation, plus existing45s native timeout and120s
  total deadline,128 init callbacks,4096 CanShow,8 primitive candidate identities,
  four total snapshots. No persistent UObject wrappers across callbacks.
- Each poll re-resolves exact live actor/component/widget/root/tree and reciprocal
  links, Open/Interact/localized text, actual source Screen visibility. Camera
  manager identity must stay equal. Own renderer/host/native validity, no parent,
  World/no collision/no overlap, fixed position/scale are rechecked. Source anchor
  movement>0.01 stops rather than silently adding tracking.
- A different known candidate only stops this test if its full binding is valid
  and it is actually screen-added/visible Open. No automatic retarget, no claim
  to detect every unacquired object in the world.
- Distance80..1500 engine units and |look-at pitch|<=75degrees are experimental
  safety bounds, not production UX. Out of bounds, source hide/loss/replacement,
  setter failure/readback mismatch, budget, F7 or timeout stop the updater before
  cleanup. Pending timer/queued actions become inert; no claim of physically
  cancelling their scheduler entries. Controls remain session-resident/inert.
- F7 sets cancellation intent immediately, then native cleanup on EngineTick.
  Native component unbind/self-destruction and own host release reuse V3. Dispatch
  failure is explicit; if cleanup dispatch itself fails, F7 can retry, without
  automatically extending the test or rebuilding the component.

Unchanged: WORLD TEST/cyan/font36; RT512x128; scale0.25/physical128x32; source
anchor+32Z; stock masked depth-tested/two-sided material; independent host and
original Screen TipHUD. No Aphes, ornament, localized UI or input-hint writes.
Fixed physical size shrinks approximately inversely with distance (fixed FOV),
and incidence compresses text. Logs report distance/normal angle and initial/current
distance ratio, **not** measured screen pixels or a readability guarantee. Follow
removes most incidence distortion but does not solve small distant text, camera
lag/stepping, scenery occlusion or overall composition.

## User test after authorized installation, including manual cleanup

The separately authorized installation above is ready. Run once:

1. Start normally, load the same test save. Ctrl+Alt+F8 arms, then reload once as
   in the accepted binding procedure. Approach one natural «Открыть» prompt.
2. When WORLD TEST appears, keep within the original Open range. In default fixed
   mode make a small camera/character arc; note skew/readability. F8 once records
   a sample. This does not reopen the accepted occlusion/render test.
3. Ctrl+Alt+F6 enables follow; repeat a comparable small arc, then modest near/far
   movement while native Open remains visible. Note smoothness, facing and size.
   F8 once records a sample. F6 may freeze again to compare if time permits.
4. **Within about30s of WORLD TEST appearing**, Ctrl+Alt+F7. Confirm only WORLD TEST
   disappears, native prompt/control remains; move the camera and verify no return.
   Do not take a fourth total F8 snapshot: its budget would stop the test before F7.
5. Close normally and report fixed vs follow preference, jitter/size problems,
   and whether F7 removed the test. Technical analysis checks first setter phase
   pair, ORIENT_SAMPLE/write counts/readbacks, STOP reason=user, hooks_remaining0,
   native COMPONENT_DESTROYED/CLEANED, no later updates. Timeout/target loss instead
   of F7 is recorded as that result, never manual-key PASS.

A setter hang is still possible in untested native runtime; phase markers locate
its entry, not prove recovery. No automatic retry. Existing first-hang cause is
unknown; accepted V3 creation is reused without redesign.

## Offline verification

`python tools/test.py`:177 tests /13 suites PASS, including19 new mocked Lua policy
cases: fixed/follow, EngineTick separation, threshold, one pending timer, finite
caps, target/UI/camera loss, alternative prompt guard, bad setter/readback,
missing API, queued cancellation, timeout and cleanup-dispatch failure/retry.
Mocks establish policy, not UE marshalling, rendering, smoothness or user acceptance.
Markdown local links and git diff whitespace checked. Production/VERSION and
accepted V3 Lua bytes unchanged. No game files or installed payload touched.

SHA256:

- `IIPWorldChild.lua`: `c5dc50ca8622817406842714efbbb9d8d543ca1a3003870c0081020f16e1deef`
- `main.lua`: `191693db4b35a0db69b33a7ec813e4e3136f740fab2f770ddded58652d4f4d9d`
