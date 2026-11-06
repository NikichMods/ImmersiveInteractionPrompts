# Event correlation observer

Baseline: `research/event-driven-target-study` commit `6aa2ba33cf9c070293141f7d8079aa472df1db10`.
Branch: `research/event-correlation-probe`. Research-only. **BOUNDED RUNTIME PASS / PROBE DISABLED / PRODUCTION BLOCKED**.

**Offline proof:** source and tests [`f03c571`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/f03c571f8fba9c88994a00f56daaa0ad54d95355); [CI run 42219818296](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42219818296), 488 tests / 44 Python files PASS.

## Runtime result — 2026-11-06

Normal user-started load on Steam 1.09/build 12996889, UE4.27 and UE4SS
83330635. Four Lua hashes matched source `f03c571f8fba9c88994a00f56daaa0ad54d95355`
before and after deployment and again after the run. Closed-host rollback
disabled EventCorrelationProbe and verified all 12 recorded CompactLayoutProbe
files, including its restored marker. Exact raw logs remain local.

- UE4SS.log SHA-256 `68e76fbb7c1ba89c972c4c2a08e4cc4114e95af87701968bd353bce92759cc4e`.
- Genesis.log SHA-256 `02b969d2a8c73d71d54d250c922ff9af37f5bd5182264646bab273c934716ccc`.

| Check | Bounded result |
| --- | --- |
| CanShow delivery and identity | **PASS** for the observed intervals. Armed at frame 1675 after the first ready owners (UE4SS line 694). 34 owners joined (Open 6, Take 18, Check 10). Last complete audit counters were 528 callbacks, all matched to indexed widget/owner records, zero unmatched. |
| Event to visible | **PASS** for six observed shows. Open #10, Check #3, Take #19, Check #3, Open #10, Check #3 at frames 4936, 5188, 5362, 5734, 5878 and 5992. Each fast-path show read the same indexed native widget visible/ready one observer frame after its most recent callback. This measures neither age from the first callback in a burst nor time to visible pixels. |
| Hide | **PASS** for six fast-path observations, at frames 5038, 5290, 5464, 5770, 5962 and 6094. No independent exact native hide timestamp or hide-callback latency was measured. |
| Unproductive or missing events | Zero event-without-visible-window or eventless-show diagnostics. **UNKNOWN** for the per-callback false-positive rate and transient or pre-arm misses. Matching counts identify owners, and repeated callbacks for an already visible owner contribute to them. |
| Ambiguity and authoritative selection | **PASS** for observed audit consistency. 85 complete audits, ten with one visible owner, 75 with none, zero ambiguous/incomplete. Global exclusivity, short overlaps between audits and direct adjacent-object switching remain **UNKNOWN**. The native CanShow bool and selected-target authority remain unproved. |
| Lifecycle | **PASS** for one joined owner removed by EndPlay (owner 2) and four LoadMapPre resets. The final reset occurred during exit preparation (UE4SS line 847), with normal exit status 0 (Genesis lines 2993–2995). No probe fault observed. Explicit stop/unregistration, callback behavior after travel into another playable map and teardown while visible remain **UNKNOWN**. |
| Native control and performance | **PASS** for stock prompt visibility by user observation and read-only localized source snapshots. CPU cost, frame time and FPS impact **UNKNOWN**, with no controlled capture. |

The exact indexed hook is a viable candidate signal for these observed
episodes. The next decision needs independent evidence for authoritative
selection or exclusivity, and measured frame-time cost on the real path.
This run authorizes neither World fast-path promotion nor Screen S1.

## What this tests

- Read-only native BeginPlay owner acquisition for Open/Take/Check (the previously
  game-observed 6/18/10 owner families). Exact indexed widget identity on the
  proven non-native `TipHUD_C:CanShow` script post-hook. Original boolean is
  not read or replaced. Hook is armed only after a real owner becomes ready.
- At most one queued candidate plus one previously active candidate is
  snapshotted per frame. A time-window of 60 frames bounds follow-up for a
  *single event*, **not** the session lifetime or interaction availability.
  Eventless visible edges are reported, not fabricated as successful matches.
- A separate diagnostic-only full registry audit every 60 frames (48 owners
  maximum; >48 or pending means INCOMPLETE, never globally unique). This audit
  is explicitly **not** an O(1) production fast path. Same-frame audit reports
  observed multi-visible collisions without guessing the selected target.
- Callback count, matching/unmatching, per-action show/hide, event age
  **in frames** and source of observation are logged on transitions.
  A logged `unique_observed` is NOT proof of engine-selected target.
  Game frame-time, GPU cost and wall-clock latency are not measurable offline.

## Read-only and failure boundary

All four source files under `Scripts/` are a *research recipe*, **not an
installed plugin or a preauthorized installation**. Copies of
`IIPInteractionSource.lua` and `IIPOpenVisibility.lua` are byte-identical
to the baseline `auto-world-successor/Scripts/` source; new observer and
entrypoint are independent. Only exact existing UE4SS callbacks and native
getters are called. No UI writes, hook returns, own World renderer, input
override, game/saves/config changes, synthetic interaction or force-load.
The existing native Screen prompt must remain visually present during trial.

An absent/changed `CanShow` function or identity contract stops coverage
claims and makes callbacks inert; failures are not repaired by polling all
owners more often. The loop is cancelled when stopped. Global hooks may not
have a verified unregistration route and must remain inert.

## Test and acceptance boundary

Offline Python 3.12 + lupa `python tools/test.py` checks callback no-return,
no native writes, indexed owner matching, simultaneous prompts, eventless
show, missing hook, pending readiness, EndPlay/map, duplicate identities and
cleanup. GitHub Actions validates source behavior only; **no latency/FPS,
native hook timing or runtime pass is implied**.

**Separate local Codex runtime authorization needed before installing.**
At that time inspect checkout/worktree and currently installed marker, closed
host and rollback; verify all four Scripts hashes against exact commit.
During a user-operated normal load, move naturally
Open → leave → Take → leave → Check → leave → return.
Capture logs and independent frame-time/perceptual observations.
Report CanShow event coverage, event-age and false/ambiguous edges; never
interpret sparse auditing as proof that transients were absent.
Restore previous installed probe only with closed host and verified hashes.

**Decision:** If real event coverage and observed exclusivity are insufficient,
do not accelerate brute-force all-owner polling. Re-evaluate Screen S1
(native TipHUD child layout), while separately retaining the requirement
for one visible prompt and no native control changes.
