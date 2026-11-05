# Open target arbitration — source-only integration foundation

## Local runtime candidate

The [payload manifest](SOURCE_MANIFEST.json) identifies five Lua files. Local
review matched the installed UE4SS DLL to the pinned 83330635 baseline.
The pinned dispatchers wrap the BeginPlay actor and EndPlay actor/reason in
RemoteUnrealParam. The observer unwraps only the actor, and the LoadMapPre
callback leaves its return unset. The previous in-game owner and Retainer
checks support these identity reads. The natural callback order and native
target correlation await the user run.

The original observer logged only a count during ambiguity. This candidate
assigns session owner IDs and records actor/component/widget paths once at join,
with callback versus retry timing. A selection transition logs the shown,
ready, hidden and pending owner sets. Pending owners invalidate the streak
of complete observations. A native validity check guards a retry before
reading the actor's owner chain. The original frame/sample/candidate budgets
apply. At 120 FPS 240 samples every 30 frames cover roughly one minute from
observer startup. Menu time counts toward that window.

Local full suite passed with **385 tests across 29 files**. The historical CI
run 42003357042 applies to eb251161, before this evidence logging change.
Runtime status is **AWAITING_INSTALL_PERMISSION**. Proposed activation uses
a separate AutoOpenEventsProbe directory and temporarily disables the
CompactLayoutProbe marker. The local handoff preserves the exact original
marker and payload hashes for rollback outside UE4SS.

After the switch, start the game normally, load the save and approach Open A,
leave it, approach Open B and leave both. Pause briefly while each prompt
is visible and note the order and any simultaneous prompts. Use a natural
A-to-B transition or location change if readily available. Exit normally.
Use the visible prompts and logged owner sets together. A missing observation
or an ambiguous owner remains unresolved.

## Automatic UE4SS lifecycle observer — source-only, 2026-11-05

**EVENT_SOURCE_AND_OFFLINE_TESTS_PASS / NOT_INSTALLED / NO_UE4SS_RUNTIME_ACCEPTANCE.**
Branch `research/auto-open-events` extends the previous pure-policy research.
[Event observer source](IIPOpenEvents.lua), [native visibility reader](IIPOpenVisibility.lua),
and [entrypoint](main.lua) are authored separately from the immutable compact
World prototype. A small read-only `IIPOpenSource.actor_identity`/
`resolve_actor` extension tracks pending actors across callback boundaries.
No installed mod, stock UI, saves, config, other mods, `main`, `VERSION`
or frozen compact source changed.

**Source behavior:**

- `main.lua` calls actual UE4SS global `RegisterBeginPlayPostHook`,
  `RegisterEndPlayPreHook` and `RegisterLoadMapPreHook` on startup,
  **without a manual edit key, CanShow hook or forced map reload**.
  C++ signatures / callback args are checked against pinned UE4SS `83330635`;
  game-specific dispatch timing remains UNTESTED.
- BeginPlay is filtered through the exact, previously proven
  `BaseGameEventObject_BP`/Open `TipHUDArgument`/ExtendedWidget/TipHUD
  identity chain. No unrelated or nearest-actor selection. Widget-not-ready
  remains a bounded primitive actor identity; on the next sampling cycle only
  these known actors are retried without synthetic native initialization.
- EndPlay removes that exact identity; LoadMapPre clears registered and pending
  records. Global hooks have no project-proven unregistrar; after an observer
  stop their closures are **inert** and never read UObject state.
- EngineTick is used solely for bounded read-only observation of known candidates
  via `LoopInGameThreadAfterFrames(30,...)`, not per-frame world enumeration:
  maximum **8** pending+registered Open identities, **8192** BeginPlay callbacks,
  **240** observation cycles. The owner checks fail closed on exhausted capacity,
  stale/missing UObjects or an unexpected native/UI contract. Loop cancellation
  is separately reported. End-user game runtime resource/performance costs are
  **not measured**.
- Full visibility snapshots are fed to `IIPTargetPolicy.observe`. One visible
  and ready native source must remain unique for two samples to be logged as
  `eligible`; inconclusive or multiple native-visible owners are logged as
  ambiguous/unknown. This is **not evidence of selected target**.
  `IIPTargetPolicy.next/bound/released` are never called by the observer:
  no fabricated World ownership or fake cleanup acknowledgements.
- `IIPOpenVisibility.visible` is a narrow read-only adaptation of the
  previously tested native TipHUD/Retainer leaf visibility checks. It observes
  raw visibility, opacity, enabled state, verified ancestry and leaf identity;
  it does **not** read the native returned `CanShow` bool or promise
  pixel/selected-owner equivalence. Original widget remains completely intact.

**Executable source layout:** these research files currently live together under
`auto-target/`. In a *future separately authorized* local trial, copy only
`main.lua`, `IIPOpenEvents.lua`, `IIPOpenVisibility.lua`,
`IIPOpenSource.lua`, `IIPTargetPolicy.lua` unchanged into the **same**
new UE4SS mod `Scripts/` directory and freeze/check source/install hashes
first. Do **not** enable the source as published or infer install authorization
from its existence. An enabled old World prototype alongside this diagnostic
is also an unapproved shared-owner arrangement.

**CI evidence:** [GitHub Actions run 42003357042](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42003357042)
at exact executable source/test SHA
`eb251161d067482fca362f0a418eb736a449f491`:
**385 offline tests /29 test scripts PASS**, including 12 new event
lifecycle scenarios and 3 new visibility/entrypoint checks. These exercise
the actual Lua modules against injected UE4SS/UMG mocks, not installed-game
event ordering, native selection or render. Reuse this exact code-run evidence
for docs-only successors unless the tested source changes.

**Next decisive gate:** at most **one bounded user-started local Codex
read-only run** after separate explicit permission for hash-guarded installation.
Observe a normal save-load without manual arm, then approach known Open A,
switch to nearby Open B, leave both, and optionally travel/reload normally.
Capture begin/end/map events, pending→joined timing and the **complete per-owner
native visibility set**. The key hypothesis is whether one visible owner
correlates with the truly selected interaction target; if two are native-visible,
the policy abstains by design. Test only evidence-bearing actions, not a new
World render. Stop on missing callbacks, over-capacity, impossible identity,
cleanup uncertainty or unexpected native behavior. No game process operations
by Codex, no save/settings writes, hot reload or modification of CombatHUD.
This evidence must precede tying the selector to repeated World-component
creation.

**2026-11-05: OFFLINE POLICY + READ-ONLY OWNER ADAPTER; NOT INSTALLED; NO RUNTIME
TARGET-SWITCH ACCEPTANCE.** Work branch `research/auto-open-target-policy`
descends from audited `7438fa763859457f7897f9d3e8452b0ddc870c51`.
The frozen compact prototype `2981375afadb968fb272eeab33aab8d384e639ef`
and its separately authorized installation, immutable manifest, accepted 17
future tuning values, `main` and `VERSION` are unchanged.

## What is implemented

- [IIPOpenSource.lua](IIPOpenSource.lua) accepts a naturally supplied actor and
  conditionally reads the **existing exact Open owner chain**:
  `BaseGameEventObject_BP` descendant -> `TipHUDArgument` (`msgTag=Open`,
  `ActionName=Interact(25)`) -> `ExtendedWidgetComponent` ->
  `TipHUD_C`. It checks reciprocal getter/storage links, does not read a guessed
  actor name, and retains only primitive path/class/address records.
  `acquire` returns `not_ready_widget` if the native widget has not been
  initialized; it does **not** force InitWidget/BeginPlay, spawn, or a class load.
  `snapshot` re-resolves exact identities and combines native component screen
  visibility, effective existing hint-widget visibility and usable native
  localized text. Native pending-kill and hint readers are injectable production
  seams, not reimplementations.
- [IIPTargetPolicy.lua](IIPTargetPolicy.lua) is entirely host-independent. It
  requires an explicit **complete, fresh** snapshot for *every registered
  candidate*. Only a **single** ready and effectively native-visible Open
  candidate observed twice is eligible for `bind`. No one wins by newest
  CanShow callback, proximity or registration order. Zero/multiple visible
  candidates abstain; invalid, aliasing, incomplete or stale data fail closed.
  A switch/EndPlay/world clear first requests `release`; a distinct
  `released(ticket)` acknowledgment after successful native cleanup is
  mandatory before another `bind`. Partial creation failure requires cleanup
  and permanently disables that policy session. Source-side `end_actor` and
  `clear_world` are implemented; global UE4SS event subscription is not.
- [tests/test_auto_target_policy.py](../../../../tests/test_auto_target_policy.py)
  and [tests/test_auto_open_source.py](../../../../tests/test_auto_open_source.py)
  exercise real Lua with mocks, including combined owner snapshot -> arbiter
  handover, ambiguous dual visibility, switch before cleanup, EndPlay, map clear,
  invalid identities and fail-closed source errors. These are offline policy
  claims only.

The **pure policy and owner adapter** do not themselves register hooks or
create a renderer. The separate source-only automatic observer described above
now registers the three global lifecycle hooks; it is still not installed or
accepted in-game. The frozen research `main.lua` does not import the policy and
remains unchanged. The existing on-disk World renderer
uses one-time asset refresh/creation and one active target; turning it into a
multi-object production lifecycle is a separate integration change with its
own evidence gate, rather than mutating the accepted research candidate.

## Verified source facts and missing host evidence

The pinned UE4SS `83330635` exports global
`RegisterBeginPlayPostHook` / `RegisterEndPlayPreHook` with actor context;
these require no already loaded game UFunction for registration. The earlier
[Open BeginPlay+CanShow game run](../../open-binding/beginplay-probe/README.md)
proved one actor/component/widget match and pose after manual reload.
[CanShow](../../can-show-state/README.md) delivered 948 callbacks for three live
widgets; it **does not** provide the original returned bool or an authoritative
selected-actor identity.

**Missing decisive assertion:** effective native component/widget visibility
is an observed presentation signal, but has *not* been validated as equivalent
to the game's unique currently selected interaction target when two nearby
eligible actors are present. An exclusive visible candidate is a conservative
source hypothesis, **not** confirmed runtime semantics. Two native prompts
visible at once cause this policy to abstain rather than guess. If the engine
presents inactive widgets as visible or changes final selection later in a
frame, the adapter needs a more authoritative source; do not workaround it with
global scans, synthetic CanShow calls or continuous writes.

**Missing activation/lifecycle assertion:** global `BeginPlayPost` has a
source-level actor contract but its ordering relative to the actual
`TipHUD` initialization, completeness for a live save, and `EndPlayPre`
delivery during travel are not accepted in this host. The separate source-only observer above now registers global hooks, but
native game callback delivery and readiness are not yet accepted. If native widget is null at post-BeginPlay, an event/bounded readiness
path needs proof; do not immediately assume a per-frame world scan or force a
widget initialization. The existing World resource module must also be
assessed for one-time preparation and repeatable own-component teardown before
a second bind is attempted.

## CI evidence

GitHub Actions `Offline Lua policy tests` is scoped to this research branch,
installs `lupa==2.8`, and executes `python tools/test.py` on Python3.12.
Record the **exact run / HEAD** in docs/STATUS.md once the combined suite
finishes; do not transfer historical test success to an untested later commit.
This workflow does not run UE4SS/Asterigos and produces no distributable artifact.

## Next sufficient step

The read-only, candidate-bounded automatic event observer now exists with
passing offline tests. Next establish its live event/readiness and A→B→none
selection semantics in one authorized user-started trial before wiring World
component handover. Verify repeatable World resource/cleanup lifecycle
independently before enabling a second bind. No installation
or runtime execution is authorized by this source-only result.

Before an ordinary-player release: acquire user approval for vanilla Screen
overlay suppression/fallback, preserve actual localization/action/input
semantics (upper OPEN is *technical glyph input*, not verified Aphes translation),
expand only to supported Take/Check families, and pass real in-game lifecycle/
mod-compatibility/packaging acceptance. Slight glow remains acceptable/deferred;
overall scale is optional and deferred. No host font/assets may be shipped.
