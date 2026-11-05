# Source-only automatic World ownership handoff — 2026-11-06

**HANDOFF_POLICY_OFFLINE_READY / NATIVE_RENDERER_REENTRANCY_BLOCKED /
NOT INSTALLED / NO GAME ACCEPTANCE.**

Separate branch `research/world-owner-handoff` based on
`research/multi-action-observer` `d0d72b07d9dd1b3fe390fc311966840544865aa1`.
No changes to the accepted/frozen `CompactLayoutProbe`, installed mod activation
markers, `main`, `VERSION`, host, saves or settings.

## What live evidence actually establishes

The Nov06 local normal-load run observed **34 ready native owners**:
Open 6, Take 18, Check 10. Five complete-sweep visible intervals
correlated with three different owner IDs and native localized
`Открыть`/`Проверить`/`Взять` via withdrawal; EndPlay retired
all 34 by normal exit. A reported sixth Open approach lacked a separate
logged interval. Direct simultaneous A→B, game-authoritative selected
target and populated map travel are not established.
[Native report](../multi-action/README.md#runtime-result--2026-11-06).

## Implemented source-only boundary

- [`IIPWorldHandoff.lua`](IIPWorldHandoff.lua): a pure Lua
  single-owner coordinator accepting only primitive actor/component/widget
  identity and supported Open/Take/Check action. It requires two **fresh,
  complete** stable snapshots before any bind. Incomplete sweeps, unresolved
  hints and multiple shown native owners never select a target.
- [`IIPInteractionEvents.lua`](IIPInteractionEvents.lua): **separate
  research fork** of the read-only native event observer. Retains normal
  auto-BeginPlay/EndPlay/LoadMap behavior and per-callback read limits,
  adding primitive `on_join/on_end/on_map/on_snapshot` callbacks. No UObject
  is passed to the lifecycle coordinator or stored across frames.
- [`IIPWorldHandoffBridge.lua`](IIPWorldHandoffBridge.lua):
  converts these callbacks into coordinator facts **without performing
  native UI writes in event callbacks**. `Bridge.pump` must be called
  later from a separate verified game-thread boundary.

The coordinator requires an injected renderer implementing
`empty/create/hide/resume/refresh/cleanup`. It is **not** a synthetic
implementation of `World.create` or proof of its reentrancy.

### Single-owner transition contract

- **A shown → none → A:** call `hide` then `resume`; retain all own
  World resources and the original owner. Never reconstruct for normal
  focus loss or a partial native visibility sweep.
- **A → B:** hide A, then call `cleanup`. Emit `CLEANED` and
  `RELEASED(ticket)` only if cleanup explicitly returns success **and**
  `renderer.empty()` independently confirms no own resources. After
  release invalidate previous target observation: obtain two **new**
  complete stable B snapshots before creating any B component.
- **EndPlay/map pre/stop:** invalidation is read-only in the native
  callback; perform cleanup on a later pump. Never create during
  an EndPlay, map or BeginPlay native callback.
- **Ambiguous, partial or unreadable native state:** hide or retain
  hidden, never guess a target or allocate a replacement.
- **Creation failure after partial allocation:** treat the new owner as
  potentially owning resources; cleanup must succeed and be confirmed
  empty before anything else. A contract fault disables automatic
  rebinding for the session.
- **Cleanup failure:** freeze in `cleanup_blocked` without per-frame
  retry or second allocation. A separate explicit `retry_cleanup()`
  is allowed to release held resources, but it **does not erase** the
  original contract fault or resume automation. This is not an arbitrary
  time/sample limit.

One adapter mutation at most per coordinator `pump` call, no native
write/read outside injected renderer; logs `BOUND`, `CLEANED`,
`RELEASED` with serial tickets, never fabricates a native release ack.

## Known native World renderer blockers — DO NOT install this source

The existing exact frozen
[`compact-layout/Scripts/IIPWorldChild.lua`](../compact-layout/Scripts/IIPWorldChild.lua)
passed **one** owner allocation, same-owner hide/resume and manual
`CLEANED` in real gameplay. It is **not a reusable render factory** yet:

1. [`IIPResources.lua`](../compact-layout/Scripts/IIPResources.lua)
   stores `import_attempted` at module scope and rejects a second
   ornament texture import, even after
   `IIPComposition.cleanup()` releases the prior image's brush.
   It has no independently verified retained texture lease.
2. `IIPWorldChild.prepare()/refresh_assets()` are intentionally
   one-shot. That may be fine for module preparation, but a new
   owner must revalidate resident resources without assuming an
   old bound native reference survives across destruction/GC.
3. `IIPWorldChild.create()` and private font creation derive object
   names from `os.time()`. Rebinding within one second can collide
   while old native transient objects have not been GC'd.
4. `IIPWorldChild.create()` calls `toggle_editor()` automatically;
   production-like automatic focus changes must not open/close the
   research editor every time. It does not currently provide an
   external source-only `hide` or `resume` lease contract.
5. Cleanup has passed only after the one tested user-operated STOP;
   it has **not** proved repeatable A→B owner teardown and new
   component creation, resource re-import, cleanup after EndPlay
   or collection order across map changes.

These are **source-verified limitations**, not observed crashes.
Do not simply remove `import_attempted`, change existing frozen
bytes, reuse a transient UObject without a native GC ownership chain,
force GC, silently migrate the component to a foreign owner or
acknowledge cleanup because a mock returned true.

## Tests and next sufficient step

[`tests/test_world_owner_handoff.py`](../../../../tests/test_world_owner_handoff.py)
runs the real pure Lua coordinator against a stateful renderer fake.
[`tests/test_world_handoff_bridge.py`](../../../../tests/test_world_handoff_bridge.py)
runs the real Lua source observer fork and bridge on pinned-API mocks.
They cover A→none→B and B→A, same-owner hide/resume, ambiguity,
partial snapshots, repeatable observations without timeout,
native EndPlay/map invalidation, partial bind, bad identity,
cleanup failure, explicit retry without reset of fault,
and no overlapping own resources. **Mocks do not verify UE4
resource allocation/destruction or visual behavior.**

**Next independent source-only task:** design a separate reentrant
native World resource/host lease based on the exact
`IIPWorldChild`, `IIPComposition`, `IIPHintSource`,
`IIPResources`, and `IIPTuning` contracts. Retain the accepted
17 [future defaults](../../../../docs/REQUIREMENTS.md#актуальная-база-после-compact-layout-прогона--2026-11-05)
and the original Screen TipHUD, action, remapping, materials,
world orientation, visual design, separator and input. Prove
per-instance transient resource lifetime and successful
`cleanup`→fresh `create` using source/host-native evidence,
then attach the renderer to this bridge and run offline failure-path
checks. Do **not** install or claim automatic World acceptance
until a separate authorized local-Codex test demonstrates at least
one real A→none→B component teardown and fresh allocation.

This is a coherent **source-only coordinator milestone**, not a
release/test payload. No manual game execution or new shared game
fact was produced.
