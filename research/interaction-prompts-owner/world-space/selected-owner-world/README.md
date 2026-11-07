# Selected-owner-driven World prompt — research candidate

**BOUNDED WORLD RUNTIME PASS / ROLLED BACK / VISUAL, PERFORMANCE AND PRODUCTION ACCEPTANCE PENDING.**

Base `85531a66f84923772204a11a5bb9f6f2533e70c2`. Target Steam
1.09/build 12996889, UE4.27 x64 and UE4SS 83330635. Verify the pinned
shipping and DLL hashes in the [committed-owner observer protocol](../committed-owner-observer/README.md)
before any separately authorized installation.

## Bounded installed-game result — 2026-11-07

**Observed research result: PASS for Open/Take/Check World display and
normal NONE handoffs; not visual/performance/production acceptance.**
The exact installed Lua source is
[`2e167227e8b29c692fdd9157de06c5cf7ed4660f`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/2e167227e8b29c692fdd9157de06c5cf7ed4660f).
The bounded runtime analysis was committed as
[`66912dd`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/66912dd51fb93c089a81b7d2d5dd43f47cd6114a).
The approved offline CI is
[run 42375931783](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42375931783)
(525 tests across 48 suites).

- **37 SHOWN/HIDDEN episodes**: 34 new BOUND (Open 13, Take 6,
  Check 15), and three same-owner RESUMED. All 33 owner changes in
  this run went through `NONE`; each next creation followed confirmed
  `COMPONENT_DESTROYED → CLEANED → RELEASED`. No observed overlapping
  own World leases or recorded IIP runtime errors. Native original
  TipHUD was not deliberately modified. The authored font/divider
  imports succeeded for all 34 constructions.
- Diagnostic **SELECTION → SHOWN** intervals: 57.51–67.96 ms when
  creating (median 60.60 ms), 34.21–35.14 ms when reusing. Observed
  NONE → HIDDEN was 0.30–1.56 ms. These are intervals between logger
  milestones, **not** input-to-visible-pixel latency or a controlled
  frame-time/FPS/CPU/GPU benchmark. They cannot on their own establish
  the <100 ms perceived UX objective.
- **Lifecycle gap:** after the final `HIDDEN` the native controller
  `EndPlayPre` occurred, followed by a normal game exit, but there is
  **no following `CLEANED/RELEASED` acknowledgement** for the last
  hidden own component. In the current source, `on_controller_end`
  calls `observer.invalidate` and cleanup is deferred to the next
  game-thread `IIPSelectedWorldSession.step`. During shutdown that
  next tick is **not guaranteed**. This explains why the expected
  acknowledgement may be absent, but neither establishes a native
  resource leak nor proves engine teardown cleanup. Do not repair by
  blindly invoking native destruction from the EndPlay callback.
- **Not exercised:** direct adjacent A→B, populated-map travel and
  owned cleanup while the game continues, HOST recovery (the class
  remained available), controlled performance measurement, independent
  visual acceptance, and selective suppression of the duplicate stock
  Screen rendering.

After normal user exit, the observer was disabled and
`CompactLayoutProbe` was restored; all 12 predecessor file hashes and
the activation marker matched. UE4SS.log SHA-256
`e7adc1a41c3b4a97f62906a90efef61ceb2038333976455b974978e18fe7dc54`;
Genesis.log SHA-256
`427b48544df9297cde98898656d504a05fac87f267ad2b196ba96c04b53eef0b`.
Raw logs stay in ignored local storage.
[Canonical runtime summary](../../../../docs/VERIFIED_RUNTIME.md#selected-owner-world--bounded-runtime-2026-11-07).

**Next sufficient step:** source-only audit and design for a safe,
deterministic own-component retirement at controller/map/host shutdown,
with a minimal test of the exact game-thread boundary and fail-closed
behavior. Preserve event callback non-mutation; distinguish
missing observation from incomplete native cleanup. Do not broaden to
global scans or another full World redesign. Separately define the
minimum user-facing visual/performance acceptance for a later run and
the independent native Screen-render suppression gate. Installation and
any native cleanup-behavior changes require their own review/permission.

## Mechanism and boundaries

The [observed committed-owner route](../committed-owner-observer/README.md#runtime-result--2026-11-07)
supplies one actor through `PlayerActionComponent+0x410`. The entrypoint
reuses lifecycle capture of the local controller and exact identity lookup.
There is no global object enumeration, visibility-based target arbitration,
two-sweep gate, hot reload, forced map change or session deadline. A single
EngineTick loop owns the renderer. MapPre and EndPlay only invalidate Lua
state; native cleanup runs in the next pump.

- **NONE** hides the owned composition and retains its lease for a same-owner
  return. **GAP**, context replacement and EndPlay retire it. Unsupported
  actions are skipped. The actor, component and widget are validated against
  stock localized text and visibility before a new bind.
- Switching owners uses hide, cleanup, own-empty proof and RELEASED before
  a new BOUND. The pump rereads selection after cleanup, before allocation
  after HOST preparation/recovery, and before showing the new composition.
  Failed cleanup is terminal. Partial creation receives one cleanup attempt.
- The resident successor's World composition, native hint, localized action,
  vertical yaw, depth and 17 compact defaults carry forward. The HOST recovery
  is limited to one exact late reload per session at an empty allocation
  boundary, with fresh class and parent validation. Initial loading has its
  own existing one-attempt guard. No added rooting or GC control.
- Stock TipHUD stays visible. Runtime owner authority comes from the committed
  weak slot. The stock widget remains the read-only text/hint/visibility
  source. The candidate's own renderer mutates only its owned presentation.

## Source identity and verification

[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) lists all 13 co-located Lua
files and their SHA-256. The established private `IIPLiveConfig.lua`,
authorized Aphes font and authored divider PNG remain external.
The new pump and entrypoint are exercised on controlled Lua/UE4SS mocks.
The tests cover NONE and direct handoff, hide/reuse, selection churn across
cleanup/create, context loss/replacement, MapPre/EndPlay, stale identities,
unsupported action, failed create/cleanup, bounded HOST recovery, and
localized text/hint visibility. The World fixture executes actual renderer
and composition code with mocked native objects and private resources.
Local verification passed 525 tests in 48 suites. The Windows run
normalized separators in one historical manifest assertion in memory.

## Next sufficient runtime check

After a separately approved installation with closed-host rollback, use a
normal save load, approach Open, withdraw, approach Take, withdraw, and
approach Check. Return to an earlier target and confirm the stock prompt
remains intact. A direct adjacent switch is optional if naturally available.
Compare selection, RELEASED, BOUND and SHOWN in the journal and check for
late, stuck or duplicate own compositions. Confirm normal exit and restore
the prior IIP marker. A missing adjacent pair leaves direct handoff untested.

Observer-frame ages describe diagnostic boundaries. Actual presentation
latency, CPU/GPU cost, component lifecycle during real travel, repeated HOST
availability, and one-prompt visual suppression remain separate runtime
gates. The cause of the previous HOST absence remains unknown.
