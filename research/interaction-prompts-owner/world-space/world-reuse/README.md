# Reusable own World renderer — 2026-11-06

**SOURCE_ONLY / OFFLINE_TESTS_PASS / NOT_INSTALLED / NATIVE_TWO_OWNER_RUNTIME_UNKNOWN**

This is an independent candidate in `research/world-renderer-reuse`,
based on the accepted `research/world-owner-handoff` controller.
The frozen `compact-layout` sources, manifest and installed
`CompactLayoutProbe` were not modified. No game files, user settings,
saves, native Screen TipHUD or other mods were changed.

## Purpose

Reuse the adopted four-element World-space composition across
distinct Open / Take / Check owners without overlapping owned World
WidgetComponents. The coordinator in
[`owner-handoff/`](../owner-handoff/README.md) defines
`hide → cleanup → confirmed empty → RELEASED(ticket) → fresh native
observations → bind`. This directory implements the **renderer-side
lease**, not a new target selector or automatic installable entrypoint.

## Source

- [`IIPWorldRenderer.lua`](IIPWorldRenderer.lua) supplies the exact
  `empty/create/hide/resume/refresh/cleanup` adapter required by
  `IIPWorldHandoff.lua`. A new owner is marked leased before native
  allocation; any partial failure requires cleanup and cannot
  authorize another create. It runs one-time `prepare/refresh_assets`
  once; owner object resolution is injected and must be fresh,
  validated and executed on the game thread.
- [`Scripts/IIPWorldChild.lua`](Scripts/IIPWorldChild.lua) is an
  **unfrozen fork**, adding explicit hide/resume/refresh and independent
  pending/empty ownership checks, sequential component creation
  after verified cleanup, session-unique own component names and no
  automatic editor opening. The already-accepted World pose, native
  read-only prompt, and composition materials are otherwise retained.
- [`Scripts/IIPResources.lua`](Scripts/IIPResources.lua) keeps
  its one-import-per-own-composition guard; a **separate lease reset**
  occurs only after `IIPWorldChild.cleanup()` verifies composition,
  component and host cleanup. Each new component receives a fresh
  imported transient ornament; no stored raw UObject wrapper or forced
  GC. Font copies receive monotonically unique names within the
  module session. Actual native GC lifetime across multiple owners
  still needs host evidence.
- [`Scripts/IIPComposition.lua`](Scripts/IIPComposition.lua) retains
  original localized action text and native button hint and carries
  an action-specific **technical** uppercase label; it is **not**
  an authenticated Aphes-world translation.
- [`Scripts/IIPTuning.lua`](Scripts/IIPTuning.lua) uses all
  17 adopted values in `docs/REQUIREMENTS.md` (compact layout
  of Nov 5). No runtime configuration state is saved.

## Test evidence

[CI 42130699221](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42130699221),
code/test SHA `49632960719808bcc2673cb81af5b0f3f23bf464`:
**430 offline tests across 35 scripts PASS.**
The two source-level real-module scenarios in
[`test_world_reuse_real_modules.py`](../../../../tests/test_world_reuse_real_modules.py)
exercise *real* forked WorldChild / Composition / HintSource / Tuning
code under the established UE4SS host mocks, and simulated
resource import: separate creation/cleanup and retry after failed
native component unbind. The related
[`test_world_renderer_lease.py`](../../../../tests/test_world_renderer_lease.py)
checks sequential leases, partial native creation and failure
containment. The test mock now models **more than one World host**,
rather than incorrectly treating the second host as the editor.

These mocks do **not** prove actual UE4 object destruction,
garbage collection, font or PNG re-import behavior, exact native
screen-to-world visual composition, user-selected ownership or
performance in a real game session.

## Readiness boundary

**Do not install this directory as a mod.** It has no independent
integrated `main.lua` that registers the observer, supplies the
native game-thread resolver, wires `IIPWorldHandoffBridge` to this
adapter, or manages one authoritative pump. Reusing the old manually
armed `compact-layout/main.lua` would violate this boundary.

**Next sufficient source-only step:** integrate the already tested
three-action read-only observer, World handoff controller/bridge and
this renderer under a *new* automatic, fail-closed entrypoint with a
pinned exact manifest and offline integration tests. It must not
invent native focus, accept partial snapshots, overwrite original
Screen UI, bind before confirmed cleanup, or introduce arbitrary
time/event caps. A user-started local Codex and separate authorization
are required before installing a frozen diagnostic/game candidate.

This directory documents a bounded source/CI milestone, not
production readiness or an accepted two-owner in-game visual result.
