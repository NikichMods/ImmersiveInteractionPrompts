# Event correlation observer — source-only candidate

Baseline: `research/event-driven-target-study` commit `6aa2ba33cf9c070293141f7d8079aa472df1db10`.
Branch: `research/event-correlation-probe`. Research-only. **NOT INSTALLED / NOT ACCEPTED**.

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
