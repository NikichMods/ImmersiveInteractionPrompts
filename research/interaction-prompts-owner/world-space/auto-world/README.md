# Automatic Open / Take / Check World composition — 2026-11-06

**SOURCE_ONLY_OFFLINE_PASS / NOT_INSTALLED / RUNTIME_WORLD_HANDOFF_UNKNOWN /
NO_PRODUCTION_ACCEPTANCE.**

This is an independently frozen source snapshot on
`research/automatic-world-session`, derived from
`research/world-renderer-reuse` `89e174430fe63c1c6392aa113adc4cc2dad17655`.
Neither the frozen CompactLayoutProbe nor the installed game, saves,
settings, activation markers, other mods, `main` or `VERSION` were changed.

## Outcome and boundaries

The new [`Scripts/main.lua`](Scripts/main.lua) uses the previously verified
global `BeginPlayPost` / `EndPlayPre` / `LoadMapPre` observation seam.
There is **no user arm chord, manual save reload, hot reload, timer,
sample-count deadline or total BeginPlay limit**.

All 17 Lua files must remain **co-located** in a single, separately
named UE4SS `Scripts/` directory, exactly as described by
[`SOURCE_MANIFEST.json`](SOURCE_MANIFEST.json) (SHA-256 source identity).
This directory is **not an installation instruction or artifact**:
the original installed CompactLayoutProbe has not been touched.

Two distinct game-thread loops:

1. The read-only `IIPInteractionEvents.lua` observes at most **48**
   supported owner identities per sample, every **30 frames**, and
   forwards **only primitive** native identities and complete/partial
   visibility snapshots. If the registered set exceeds 48, an
   incomplete batch **cannot select a target**. Neither elapsed time
   nor the number of native BeginPlay calls ends the session.
2. `IIPAutoWorldSession.lua` pumps
   `IIPWorldHandoffBridge → IIPWorldHandoff → IIPWorldRenderer`
   every game frame, outside any native game event hook. This loop
   alone may create, hide, update or destroy **our own** transient
   World component. No original Screen TipHUD setters or action
   invocations are used.

[`IIPWorldTarget.lua`](Scripts/IIPWorldTarget.lua) resolves the
primitive owner into a *fresh* native actor/component/TipHUD triple
on the game thread, checks address/path/class and reacquisition,
requires a fresh shown-and-ready native snapshot, and passes the
original objects only for the current creation operation.
No retained UObject wrappers cross asynchronous boundaries.

The handoff requires two consecutive full native samples before an
initial bind. For switching to a different owner:
`hide → cleanup → independent empty proof → CLEANED → RELEASED(ticket)
→ two NEW full unique snapshots → fresh create`. For the same owner,
temporary focus loss retains the existing composition and uses
hide/resume. Partial observations and multiple visible native owners
cannot select a new target. A partial failed create must be cleaned
before any further allocation; failed cleanup blocks all new binds
and stops repeated native mutations.

The World presentation preserves the accepted **17 compact-layout
settings**, local authored separator, localized action read from the
original TipHUD and live native input hint, and the original control
semantics. The large technical upper line currently renders
`OPEN` / `TAKE` / `CHECK` in the selected stylized font: these
are **not verified in-world Aphes translations**. The existing
Screen prompt remains visible; suppression/UX duplication is a
**separate user-owned decision**, not silently implemented here.

## Offline proof

[GitHub Actions run 42133071798](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42133071798)
on commit `5af99f7f6710eb81ab838d6fa0d6a9a6c500e373`:
**446 tests in 38 test scripts PASS**.

The new `tests/test_auto_world_session.py` runs the real Lua
native owner source, event observer, lifecycle controller/bridge,
target resolver, renderer lease, and session orchestrator with
explicit UE4 mocks, including Open → no prompt → Take → no prompt →
Check, same-owner reuse, ambiguity/incomplete snapshots, EndPlay,
map transition, stale target, partial allocation and failed release,
unbounded session duration, stopped callbacks, and terminal cleanup
readback faults.
`tests/test_auto_world_entrypoint.py` checks the actual
`main.lua` registrations, startup error containment and absence
of manual arming.
`tests/test_auto_world_manifest.py` independently verifies
**all 17 file SHA-256 values against their bytes checked out in CI**.
The previous 430 source tests remain part of regression coverage,
including the real forked World-module mock lifecycle and accepted
17 presentation values.

**No test above is a substitute for actual UE4 object allocation,
rendering, garbage collection or input/visual acceptance.**
A direct A→B without withdrawing, populated-map travel and
authoritative native selected-target identity were not established
in the previous host runtime.

## Before any locally authorized installation

- Recover the actual game/UE4SS environment under DevRules and
  repository `AGENTS.md`. Do not assume this source matches a
  different host build.
- Verify that the game is **closed** and the previously restored
  CompactLayoutProbe / existing IIP activation markers and all
  unrelated mods are unchanged. Prepare an out-of-loader rollback.
- Freeze the exact new source and verify every SHA-256 in
  `SOURCE_MANIFEST.json` **before and after deployment**.
- Resolve the required **private**, separately installed
  `IIPLiveConfig.lua` containing the authorized font and
  `separator_filename` paths and the authored PNG. Those
  resources/paths are deliberately not distributed from GitHub.
  Do not copy/provision host-owned fonts or assets into public Git.
- Obtain the user's **separate explicit installation permission**;
  then use **user-started local Codex** for the closed-host install,
  ordinary user-paced gameplay test, logs, and exact rollback.
  Do not start/terminate the game, force a reload, use hot reload
  or modify saves/settings.
- Test natural Open → none → Take → none → Check, confirm owner
  identity, native visible prompt/action and own World component
  `CLEANED` before each next `BOUND`, native re-import/GC,
  no overlap, default 17-value visual layout, and ordinary exit.
  Classify observed vs unknown. Do not claim World acceptance
  based only on mock logs.

The next sufficient gate is **authorized in-game repeated World
allocation and visual acceptance**. No installed payload,
test log or new common host discovery was produced in this
GitHub-only source step.
