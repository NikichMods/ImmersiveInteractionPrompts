# Automatic World — host residency and latency successor (2026-11-06)

**SOURCE_ONLY_OFFLINE_PASS / NOT_INSTALLED / HOST_RECOVERY_RUNTIME_UNKNOWN /
RESPONSIVENESS_AND_PERFORMANCE_RUNTIME_UNKNOWN / PRODUCTION_BLOCKED.**

Separate research branch `research/auto-world-residency-latency` forked
**exactly 17 Lua files** from the failed but runtime-observed AutoWorld
`be1827d014eb4c81543f64f69778e951fdec5e23`. The original
`auto-world/` files and its immutable `SOURCE_MANIFEST.json`, the
restored installed `CompactLayoutProbe`, `main`, `VERSION`, saves,
settings and other mods are unchanged.

## Proven baseline and exact question

The [2026-11-06 installed-game report](../auto-world/README.md#runtime-result--2026-11-06)
is **not** invalidated by this source work:

- Open, Check and Take all rendered with the approved compact composition;
  two distinct-owner transitions completed own component
  `CLEANED → RELEASED → new BOUND` and one Open hide/resume kept the
  same component. Two repeat image/font imports succeeded.
- On the **fourth** creation, the exact previously live generated
  World host class lookup returned `ABSENT_NULL` at `before_create`,
  resulting in `NOT_LOADED: resource changed after refresh`.
  Stop/rollback succeeded. **Why the class disappeared is unknown**;
  GC is a possible explanation, not a measured cause.
- Measured first-sampled native-visible → World SHOWN:
  Open 0.576 s, Check 1.563 s, Take 1.568 s and same-owner Open return
  0.531 s. These numbers exclude time before the first sample and pixel
  presentation beyond the logged SHOWN event. User rejected this latency.

## Solution-space decision

Outcome: contextual World prompts with native input/action unchanged,
negligible perceived appearance delay, only one live own composition,
no inferred ownership from partial/ambiguous observations, and safe
recovery/STOP when a host dependency is unavailable.

Compared:
1. **Keep actor-owned sequential components**, retain the proven
   `cleanup → confirmed empty → fresh owner snapshots → bind`
   protocol, and resolve a missing exact host class at the **new
   allocation boundary**. This reuses the two verified native handoffs
   and native UObject/UPROPERTY ownership already inspected.
2. **One permanent own component reattached across actors.** This would
   remove repeated font/texture/host allocation but requires a different
   attach/ownership lifecycle, surviving actor EndPlay, changing source
   and anchor ownership and additional unverified native APIs. With the
   current actor-owned component design, keeping it after the original
   actor ends is not yet an accepted mechanism.

Selected **(1)**, with host recovery narrow and fail closed. The
permanent-component concept is *deferred*, not claimed impossible.
No new native object rooting, guessed alternate resource, or automatic
asset retry loop has been introduced. This reopens the architecture
choice only if the next runtime test shows repeated failure,
unacceptable resource cost or a newly verified simpler attach route.

## Independent source changes

`Scripts/IIPWorldChild.lua`:

- The already proven one-time `prepare/refresh_assets` step remains.
- If a later `before_create` HOST lookup is still `LIVE`, reuse its
  **fresh** lookup as before; there is no speculative load.
- Only when the previously verified exact HOST becomes `ABSENT_NULL`
  or `ABSENT_NIL` at a clean, prepared allocation boundary, call
  `LoadAsset(HOST)` **once for that allocation attempt** on the
  existing verified game-thread pump. Verify `found/did_load`,
  returned UClass/live identity, a second fresh exact-path lookup with
  matching address, and `UserWidget` superclass. Emit
  `HOST_RECOVERY_ATTEMPT`, `HOST_RECOVERY_RESULT` and
  `HOST_RECOVERED` evidence.
- Invalid-but-non-null, foreign or mismatched host identity, absent
  stock material, failed loader, changed superclass or different
  post-load lookup **still fail closed**, with no second World allocation.
  Previously accepted native cleanup semantics remain in force.
- A single Lua wrapper is not a native GC root. No `AddToRoot`,
  `CollectGarbage` or cross-frame UObject caching has been added.
  This is a recovery *candidate*, not evidence for the reason the
  class disappeared or eventual garbage-collection correctness.

`Scripts/IIPInteractionEvents.lua` and
`Scripts/IIPAutoWorldSession.lua`:

- Full read-only native ownership snapshots now occur every
  **3 game frames**, instead of 30, with at most **48**
  registered owner records per callback. This is a sampling
  cadence, **not** a timer/total-event/session duration limit.
- The complete/partial and ambiguous-owner rules remain identical;
  the coordinator still requires **two fresh complete unambiguous
  snapshots**, and after a release requires two *new* complete
  snapshots. No owner is inferred from CanShow alone.
- The unchanged one-frame World composition pump still performs native
  operations outside event hooks; one step at a time.
- This increases potential sampling work per second by approximately
  10× at a fixed frame rate. **The actual UE4 CPU/FPS cost is unknown.**
  Before production acceptance the user-operated run must check
  responsiveness *and* absence of perceptible frame-time regressions.
  If costly, refine the scanning policy rather than silently reverting
  to the already-rejected 30-frame delay.

Everything else in the 17-script successor is an **identical copy** of
the former exact source. The original Screen TipHUD remains untouched;
`OPEN/TAKE/CHECK` are technical upper labels, not verified Aphes
translations. Authored divider PNG, font and `IIPLiveConfig.lua` remain
external; 17 adopted layout defaults remain unchanged.

## Verification and next gate

[GitHub Actions run 42209313867](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42209313867),
at source/test commit `d48ca6032ab75dec29eec16be4c7a6a741930ac2`:
**473 offline tests in 42 test scripts PASS**.

- `test_resident_host_real_modules.py`: real forked Lua World
  modules on native-style mocks across three accepted builds and a
  *fourth* after simulated lost class, including exact `ABSENT_NULL`,
  wrong type, failed loader, unavailability of stock material and
  no second active component.
- `test_responsive_world_session.py` and
  `test_responsive_world_entrypoint.py`: real Lua source/observer/
  controller/renderer/entrypoint on explicit mocks with the
  **3-frame** observer and unchanged one-frame World pump; Open/Take/
  Check handoffs, hide/resume, EndPlay/map, ambiguous/incomplete
  owner sets, partial creation/cleanup failure, session stop.
- `test_resident_world_manifest.py` verifies every hash in
  [`SOURCE_MANIFEST.json`](SOURCE_MANIFEST.json) matches exactly
  the 17 checked-out Lua source files, and the external resources are
  not redistributed.

**Next sufficient step** (only after separate deployment permission):
user-started local Codex verifies the exact known Steam/UE4SS environment,
private resources, 17 SHA-256 checksums and closed-game rollback. The
user launches and tests a *fourth and fifth* natural inter-owner cycle,
including the previous Take → Check failure route, records native
`HOST_RECOVERY_*` / `CLEANED` / `BOUND`, first-visible → World
appearance latency and observed gameplay responsiveness/performance,
then exits normally and restores CompactLayoutProbe. Neither this
file nor CI is installed-runtime or production acceptance.
