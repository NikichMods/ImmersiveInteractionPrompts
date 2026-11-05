# Open target arbitration — source-only integration foundation

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

No module calls `RegisterHook`, `RegisterBeginPlayPostHook`, `RegisterEndPlayPreHook`,
`NotifyOnNewObject`, engine create/setter APIs or a renderer. The new policy
**is not imported by the frozen research `main.lua`**. No playable mod, native
observer or automatic activation is claimed. The existing on-disk World renderer
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
delivery during travel are not accepted in this host. No global hook is wired
here. If native widget is null at post-BeginPlay, an event/bounded readiness
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

Continue in ChatGPT: determine a minimal **read-only, candidate-bounded
activation/observation seam** based on the established `BeginPlay`,
`EndPlay`, `CanShow` and effective native visibility contracts. Verify the
retargetable World resource/cleanup lifecycle offline before wiring it.
If only installed game evidence can decide active-target exclusivity or
post-BeginPlay readiness, prepare *one narrow* user-started local Codex
observation task with A→B→none, exact identity and state readback. No installation
or runtime execution is authorized by this source-only result.

Before an ordinary-player release: acquire user approval for vanilla Screen
overlay suppression/fallback, preserve actual localization/action/input
semantics (upper OPEN is *technical glyph input*, not verified Aphes translation),
expand only to supported Take/Check families, and pass real in-game lifecycle/
mod-compatibility/packaging acceptance. Slight glow remains acceptable/deferred;
overall scale is optional and deferred. No host font/assets may be shipped.
