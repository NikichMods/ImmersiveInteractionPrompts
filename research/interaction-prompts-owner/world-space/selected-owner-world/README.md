# Selected-owner-driven World prompt — research candidate

**SOURCE ONLY / NOT INSTALLED / RUNTIME AND PRODUCTION ACCEPTANCE PENDING.**

Base `85531a66f84923772204a11a5bb9f6f2533e70c2`. Target Steam
1.09/build 12996889, UE4.27 x64 and UE4SS 83330635. Verify the pinned
shipping and DLL hashes in the [committed-owner observer protocol](../committed-owner-observer/README.md)
before any separately authorized installation.

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
