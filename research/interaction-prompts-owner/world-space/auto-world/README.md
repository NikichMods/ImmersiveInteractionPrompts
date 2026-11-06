# Automatic Open / Take / Check World composition — 2026-11-06

**RUNTIME_THREE_BINDS_PASS / REPEATED_REBIND_AND_LATENCY_FAIL /
COMPACT_PROBE_RESTORED / NO_PRODUCTION_ACCEPTANCE.**

This is an independently frozen source snapshot on
`research/automatic-world-session`, derived from
`research/world-renderer-reuse` `89e174430fe63c1c6392aa113adc4cc2dad17655`.
The frozen source was installed temporarily for the run below.

## Runtime result — 2026-11-06

Normal Steam 1.09/build 12996889, UE4.27 and UE4SS 83330635 session.
Source `1bf1cd2cb0b8a17a739d9de8a5cb2b23e9445ae5`, CI/manifest commit
`5af99f7f6710eb81ab838d6fa0d6a9a6c500e373`, handoff HEAD `41ed7126`.
All 17 installed Lua hashes and the separate local config matched before
rollback. AutoWorld was disabled after normal exit, and all 12 recorded
CompactLayoutProbe files including its enabled marker were verified.
Exact raw logs are archived locally outside UE4SS.

- UE4SS.log SHA-256 `a26798de7ce3403900ea81b8b9ff48edc6bf22519f58dab08a3a15731f6121ae`.
- Genesis.log SHA-256 `b45a1005fd58daaeda52757596e5b32a85763955ecb73a728d32515a5ebc2d09`.

| Check | Result |
| --- | --- |
| First display for three actions | **PASS** in this run. Log order was Open #10 (BOUND ticket 1, line 824), Check #3 (ticket 3, line 902), Take #19 (ticket 5, line 968). The user saw all three and found their appearance acceptable. |
| Same-owner return | **PASS** for Open. Hide and return reused the first component without a new allocation (lines 831–842). |
| Handoff and duplicate ownership | **PASS** for the recorded transfers. Native destroy with pending-kill check and empty own holders preceded CLEANED → RELEASED for tickets 2/4/6 (lines 851–863, 917–929, 982–994), before the next create attempt. Three distinct components were created with no overlapping own leases in the trace. Global enumeration of components and eventual GC remain **UNKNOWN**. |
| Private resource reuse | **PASS** for two rebuilds. Font configuration/bind and 256×32 PNG import/texture bind succeeded on all three created compositions (lines 808–813, 886–891, 952–957). The fourth attempt failed before these stages. |
| Continued operation | **FAIL**. Returning from Take #19 to Check #3 released Take successfully. The fourth create found the host class `ABSENT_NULL` at `before_create` and raised `NOT_LOADED: resource changed after refresh` (lines 997–1004). This stopped the session. The reason the class became unavailable, including any role of GC, remains **UNKNOWN**. |
| Containment and exit | **PASS** for the observed fault. Observer cancelled, terminal empty cleanup/release acknowledged (ticket 8), pump cancelled and `TERMINAL reason=stopped_clean` logged (lines 1005–1011). Genesis.log lines 3853–3856 record normal exit with status 0. Cleanup triggered by ordinary exit while still bound was **NOT_TESTED**. |
| Responsiveness | **FAIL** against the user's final UX requirement. First sampled native shown → World SHOWN took 0.576 s (Open), 1.563 s (Check) and 1.568 s (Take), and Open return took 0.531 s. The logged 30-frame sample period was about 0.5 s. Owner changes waited for confirmation and then two fresh samples after release (about 1 s), before create. These intervals exclude time before the first sampled visibility and pixel presentation after SHOWN. |
| Native TipHUD and localized text | **PASS** for read-only source and matching visible native text → World layout for «Открыть», «Проверить», «Взять». Trace reports zero original UI writes. Continuous visual preservation of the original Screen prompt is **UNKNOWN** from this report. |
| Native input hint and gameplay | **PASS** for read-only native hint binding on all three builds and the Open return. Pixel equivalence is **UNKNOWN**. Device switching, executing each interaction and direct A→B without withdrawal were **NOT_TESTED**. |

`OPEN/TAKE/CHECK` are technical upper labels with unverified Aphes translation.
This run leaves two independent gates open: host-class availability across
repeated handoffs and acceptable appearance latency. No successor is selected
by this evidence.

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

## Original pre-installation checklist

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
