# Vertical world-Z yaw — bounded runtime / manual F7 PASS

Integration successor: [World Aphes composition review](../composition/README.md),
BLOCKED on current hint reproduction. This frozen yaw/F7 result is not reopened.

2026-10-30. User-run vertical yaw / manual F7 PASS recorded below; probe DISABLED.
Exact source and earlier records remain frozen. Production BLOCKED. Reuse accepted
Open binding, private host, World renderer/material,
Hilda occlusion and native cleanup; do not re-prove these prerequisite gates.

## User-run result — 2026-10-30, bounded PASS

Source `f1eb6358fef4e9e9ebcb4e8ad00d2a9f04659851`; source and installed Lua hashes
below matched after exit. Same Steam1.09/build12996889 / UE4.27 / UE4SS83330635.
User reports everything worked almost ideally and explicitly confirms pressing F7.
This supports bounded visual/operational acceptance of vertical frame-yaw and
manual cleanup, not final typography/composition or a quantified performance test.

| Moscow time | Evidence |
| --- | --- |
| 02:36:45.363 | Own WORLD TEST created at the matched natural Open, initial pitch0/yaw97.5467591/roll0, scale.25, RT target512x128, anchor+32Z. |
| 02:36:45.364 | One LOOP_REGISTERED handle3, frames1. |
| 02:36:45.368 | First vertical setter BEGIN/END returned. |
| 02:37:01.777 | User snapshot:985 frames/985 writes, no degeneracies. Own actual rotation(0,73.4368515,0), yaw error0.000117563deg, fixed position(-40619.4648,12241.2139,5704), scale(.25,.25,.25), RT512x128, World0, no collision/overlap/hardware/focus, stock masked depth-disable=false; original_writes0. |
| 02:37:03.159 | LOOP_CANCELLED handle3 reason=user, YAW_SUMMARY1068 frames/1068 writes/degenerate0, last requested yaw73.437059683518, error0.000093741deg, pitch0/roll0. STOP user/MATCHED, init128/open3/ready3/show1071/matches1/poses2/hooks_remaining0. |
| 02:37:03.176 | COMPONENT_DESTROYED native pending-kill check, CLEANED reason=user/own_widget_holder=false/own_component_alive=false. |
| 02:37:25.273 | Event loop end; no later probe events or FAILED/CLEANUP_PENDING/LOOP_CANCEL_PENDING events. |

The1068 writes in about17.796s from creation correspond to roughly60 callbacks/s
in this run. That is observed callback cadence, not a display-FPS measurement,
proof that no engine tick was skipped, or a performance benchmark. The source
uses a one-frame EngineTick-pre loop; the yaw readback guard passed during each
successful update. User feedback supports perceived successful behavior; it
supplies no separate numerical latency/jitter or FPS-drop measurement.

**Closed gates for this scope:** live native frame-loop registration, horizontal
camera-facing yaw with pitch/roll0, returned repeated setter calls/readbacks,
manual F7 cancellation and native own cleanup before timeout. The actual snapshot
and guarded updates support verticality; camera motion/visual behavior is also
user-confirmed. Existing renderer/occlusion acceptance is reused, not repeated.
CancelDelayedAction returned true; PendingRemoval/function-unref follows the
pinned source contract, without an independent post-cancel handle-query log.
No further own updates were logged after stop. No forced GC/GPU-free claim.

No degenerate horizontal direction, fixed fallback, lost-target error or native
45s timeout was exercised in this run; their earlier source/tests/results remain
separate. Full Aphes composition, wider lifecycle, actions/input-device coverage
and production acceptance are still open. The old unknown first-hang cause is
not diagnosed by this success. No new payload or automatic follow-up test.

Ignored archive outside loader:
`.local/research/interaction-prompts/world-space/vertical-yaw/runtime-20261029T233819Z/`.
UE4SS log SHA256 `d06cb0f2d327336493b143f3f2b3ac5fdf39d07a2632d656f58ef0afa747980a`;
Genesis log SHA256 `88b57d58e8c69200a1b0f910c63a7d6473cb9337254e09334106f47f29072019`.
Raw logs/filtered probe events, installed source/manifest and disable record saved.
Game already closed. Removed only this own enabled.txt; payload retained. All33
pre-existing loader/mod hashes match installation,88 current files retain hashes
across disable (not a pre-play-save equality claim). All IIP probes disabled;
other mods/current settings/saves preserved. No agent launch/termination/hot reload.

## Authorized closed-game installation — 2026-10-30

User explicitly requested installation. Exact source commit
`f1eb6358fef4e9e9ebcb4e8ad00d2a9f04659851`; installed Lua SHA256 match the source
values below without code edits. New own UE4SS directory
`ImmersiveInteractionPromptsWorldYawProbe` contains only Scripts/main.lua,
Scripts/IIPWorldChild.lua and empty enabled.txt. Only this IIP probe enabled;
13 previous IIP directories retained disabled, mods.txt unchanged, CombatHUD and
SoulsEnemyHUD enabled as before.

Asterigos/Genesis processes absent before/after installation; no agent game launch
or termination. Steam build12996889 and UE4SS83330635 identity match baseline.
DLL SHA256 `ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`.
29 historical loader/mod hashes match. All33 pre-existing current mod/loader files
and56 existing tracked config/save files retain hashes across install. Current
files are preserved, not claimed equal to pre-gameplay save bytes. No production,
VERSION, settings/save/other-mod writes or hot reload.

Ignored rollback archive outside loader:
`.local/research/interaction-prompts/world-space/vertical-yaw/install-20261029T233337Z/`.
Exact source copies, initial-state/installed manifests, verified result, pretest
UE4SS/Genesis logs, loader settings/mods.txt copies and guarded rollback.ps1 saved.
Rollback verifies closed game, exact owned directory and file hashes before
removing only new own files to restore prior absent state. Syntax PASS; not run.
Installation PASS does not establish frame cadence, vertical visual acceptance,
performance or manual F7/native cancellation. Proceed only with the user test below.

## Adopted orientation and minimum evidence

User chose a vertical vane: yaw toward horizontal camera position each game frame,
pitch=roll=0, fixed world position. No angular deadband, smoothing or interpolation.
Minimum reserve: initial vertical camera-facing yaw once, then fixed. Actor-facing
orientation was not chosen. This supersedes the previous undecided fixed/full
look-at comparison; it does not claim vertical-frame runtime acceptance.

The prior10Hz/full-pitch call returned in the actual build. Static inspection can
prove the new scheduling/math policy, not smoothness, frame phase or live F7.
One narrow frame-yaw/F7 trial is sufficient; no new discovery observer is needed.

## Exact scheduler contract — UE4SS83330635

[LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp),
[LuaMod.hpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/Mod/LuaMod.hpp):

- cpp4790–4853: `LoopInGameThreadAfterFrames(1,fn)` requires EngineTick, returns
  integer handle, no ProcessEvent fallback. Header68ff initializes action.method
  to EngineTick. No reliance on a similarly named API from another revision.
- cpp767–797 make_hook_state returns the calling mod's one anchored m_hook_lua;
  delayed action.lua points to it. cpp5128–5159 CancelDelayedAction matches both
  handle and action.lua==mod.m_hook_lua in active/pending queues, then marks
  PendingRemoval. This establishes the ownership comparison, rather than guessing
  from function names. The frame callback and F7 execute in that same mod.
- cpp3950–4093 processor decrements frames_remaining on EngineTick, executes once
  when due and resets to1 after completion. It calls the Lua callback with **zero
  results**: returning true does not cancel this loop. No catch-up/multiple steps
  are authored. m_is_currently_executing_game_action can defer execution; do not
  promise an invocation during every rendered GPU frame, pause or reentrant action.
- cpp4083ff erases PendingRemoval and luaL_unref's the callback function registry
  ref. The mod's shared hook Lua thread stays anchored for its lifetime; no claim
  to destroy the shared Lua state or unregister UE4SS's global EngineTick hook.
- cpp4130ff runs this from **UEngineTick pre**. Camera state may precede later
  same-frame camera/player updates: smoothness/one-frame phase lag needs runtime
  observation. The frame callback does not add another ExecuteInGameThread hop.
- Cancellation does not retract a callback already copied into the ready list.
  phase/cancel/selected-identity checks happen before native reads; F7 sets intent
  immediately, stop makes the loop inert before cancellation and queued cleanup.
  True cancellation logs LOOP_CANCELLED; already-gone handle logs LOOP_RETIRED.
  Failed cancellation logs LOOP_CANCEL_PENDING, retains the handle for F7 retry
  and leaves callbacks inert. No false promise of physical removal on failure.

Registration occurs exactly once after successful FinishAddComponent, never in
CanShow. Its handle and one-attempt flag are private to this probe. Stop cancels
it from F7, target loss, failure, budgets or timeout. Cleanup is still dispatched
to EngineTick, so own native destruction happens after the loop callback returns.
The existing45s/120s timeout callbacks remain scheduled but become inert after
stop, bounded by their original deadlines; this does not remove other actions
or call CancelAllDelayedActions. The helper's registered flag tracks its own successful creation/cleanup phase;
it is not an invented reflected IsRegistered query.

## Geometry and edge cases

[UE4.27 WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp)
plane vertices377–380 have local normal+X. For own fixed position P and camera C:
`yaw=degrees(atan2(C.Y-P.Y,C.X-P.X))`, pitch=roll=0. Normal becomes
(cos(yaw),sin(yaw),0); local up remains world+Z. Camera east+X→yaw0,
+Y→+90, -X→±180, -Y→-90. Camera height is excluded from orientation.
No180-degree actor-face correction is added. Native K2_SetWorldRotation and fresh
FHitResult out table reuse the bounded runtime-established setter route.

If horizontal distance<1 engine unit (1cm in standard UE units), yaw is undefined:
keep the last valid yaw while staying vertical; record a degenerate-frame count.
If this happens at initial creation, refuse before own component allocation,
rather than select an actor-facing/default direction. This positional singularity
bound is not an angular motion threshold. Camera distance80..1500 (3D) remains the
previous experiment's guard; no former75-degree pitch restriction is needed.

## Per-frame work and safety

Fast frame:8 exact StaticFindObject calls (six primitive identities plus native
validity function/CDO),6 native IsValid checks, ownership/camera/visibility reads,
GetCameraLocation, one setter and one rotation readback. Total13 reflected UE
calls on the successful follow path, plus UE4SS identity/property operations and
Lua arithmetic. At120 EngineTicks/s this is approximately960 lookups/1560 reflected
calls per second, **not a timing/FPS benchmark**; slow/error paths differ. The
prior100ms chain had at most10 updates/s and an additional explicit EngineTick
queue hop. This revision deliberately costs more work to test true frame cadence.

Full reciprocal Open/Interact/localized-text/root/tree/anchor and owned geometry/
scale/World/no-parent/no-collision checks run on frames1,13,25... (every12 callbacks),
and at creation/manual snapshot. They resolve fresh wrappers too. Native lifetime
of actor/source/TipHUD/own component/own host/camera and essential ownership are
checked every frame, including PendingKill; no wrappers persist across callbacks.
CanShow preserves discovery/known-alternative guards but no longer repeats the
full topology inspection for every matched callback. Its current text/visibility
check and the frame check can stop promptly; root/anchor-only changes are detected
within12 callbacks (not a guaranteed100ms at low FPS). No global scans or native
TipHUD Tick mutation; work is bounded to one selected actor and own renderer.

Frame reads source bVisible/bAddedToScreen and TipHUD visibility/enabled/opacity;
full Open semantics remain periodically checked, also by CanShow. A known other
actually-visible Open stops without retargeting. World position/scale remain fixed;
periodic anchor movement/geometry mismatch stops. Same RT512x128/font36/cyan/
scale.25/anchor+32Z/stock masked depth-tested material. No Aphes/composition/hint or
original UI edits. Own surface remains occluded by normal scene geometry.

Limit:12000 frame updates or45s after creation, existing native45s timeout,
120s total observation,8 primitive candidates/128 init/4096 CanShow/four snapshots.
A low-frame-rate stall does not authorize extending the deadline. Fixed reserve
uses `FOLLOW_CAMERA=false` at source (new hash required for any handed alternate):
initial vertical camera yaw only; loop performs bounded health/readback checks but
no rotation writes. Default prepared bytes use true; there is no F6 mode toggle.

At stop YAW_SUMMARY records frames/writes/degeneracies/last yaw/readback error,
closing the previous missing-follow-metrics gap. No per-frame print. Success means
returned setter plus readback pitch/roll<=0.001degree and yaw error<=0.01degree;
these are verification tolerances, not a motion deadband. No performance guarantee.

## Single user test after authorized installation

The installed exact source above is ready for one user-run scenario:

1. Load test save, Ctrl+Alt+F8 once, reload once for the accepted natural binding.
2. At one natural Open, WORLD TEST starts in vertical frame-follow. For about10–15s
   move slightly around the object and change camera height/pitch while remaining
   in Open range. Confirm the plane stays upright and turns horizontally; note
   visible stepping/lag. One Ctrl+Alt+F8 records a sample. No need to re-prove Hilda
   occlusion or reopen the renderer/material experiment.
3. **By about25–30s after creation**, Ctrl+Alt+F7. Confirm only WORLD TEST disappears,
   original action/icon/input remain, move camera briefly and verify no return.
4. Close normally/report. Review LOOP_REGISTERED once, first_vertical_yaw phase
   pair, YAW_SUMMARY/frame-write counts, LOOP_CANCELLED and STOP reason=user,
   hooks_remaining0, COMPONENT_DESTROYED/CLEANED, no subsequent native updates.
   Target-loss/timeout instead of F7 is recorded separately, never F7 PASS.

This historical scenario completed in the bounded PASS above. No repeat is
requested. Precise camera-phase latency and performance remain unmeasured.

## Offline verification and identity

`python tools/test.py`:199 tests /14 suites PASS,22 new vertical policy cases.
Mocks cover quadrants/wrap/height independence, subdegree and stationary writes,
singularity/initial refusal, fixed reserve, native PendingKill/ownership loss,
periodic full checks, setter/registration failures, cancellation failure/retry,
ready-callback inertness, no re-registration, frame/deadline/native timeout caps
and8-lookup fast path. They do not test C++ native scheduling or rendering.
Source/UHT hashes retained ignored in `.local/research/interaction-prompts/world-space/vertical-yaw/`.
Markdown links/git whitespace checked; old accepted Lua, production and VERSION
unchanged; no installed payload/game settings/save changes.

- SHA256 `IIPWorldChild.lua`: `6e4f065752901f00804ec1d33cf64309deb2bac97a31d1b874ec2c3f5e17ab9f`
- SHA256 `main.lua`: `11a581700fd0cbf2d1b75737a2bd51b5eb45465be3cfeed8e5e5e5624958e024`
