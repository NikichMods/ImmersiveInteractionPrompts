# ShowTipEvent — read-only owner transition observer

**Source-only; not installed; not a runtime pass.**

## Purpose and provenance

The verified native trace at commit c8aec0a9382198abef14cb6b8403e4504853a494
identifies a character-side single-owner transition. Its actor helper dispatches
ShowTipEvent(bool) before directly invoking the ExtendedWidgetComponent:SetShow
body. The reflected SetShow hook is bypassed on that path.

This candidate asks whether UE4SS 83330635 can deliver the natural event on
Open/Take/Check actors and whether its bool/actor identity correlates with
subsequent independent stock visibility.

## Contract

- Scripts/main.lua attempts an exact event hook only after a supported ready
  actor is seen through the existing BeginPlay observer. No forced host load.
- The callback reads the actor and one bool immediately, returns nil,
  and records selection intent. It never sets any native state.
- Only actors affected by a delivered event are inspected afterward, for
  up to 12 observer frames each; at most 12 pending events. No all-owner scan.
- Visibility uses the existing event-driven source and hint adapters,
  copied unchanged from the previous observed CanShow candidate.
- Unsupported owners do not become evidence for Open/Take/Check. EndPlay
  and map transitions clear the scoped identities. On STOP the callback
  remains inert even if a script hook cannot be unregistered.

## Material uncertainty

UE4SS LuaMod.cpp at pinned revision 83330635 only registers a non-native
script hook when the resolved UFunction has ProcessInternalInternal as its
function pointer. A bare BlueprintImplementableEvent may not meet that
condition, or natural virtual dispatch may use a derived UFunction.
Registration failure is a clean HOOK_UNAVAILABLE result; registration success
does not itself establish callback delivery. Do not replace the target by
a global ProcessEvent hook merely to force a pass.

ShowTipEvent precedes native SetShow. INTENT is not confirmed pixels;
CORRELATED is a later sampled state, not a render timestamp. No events
during real visible prompts means unknown delivery / negative evidence for
this exact hook, not proof that game show events never occur.

## Verification and proposed runtime procedure

The Python/Lupa test tests/test_show_tip_event.py validates callback
arguments, ordering, read-only intent/snapshot separation, missing hook,
bounded timeout, EndPlay/map reset, and inert stop. Existing independent
offline/live results support the two copied adapters only in their tested
scope. A source/CI pass does not establish delivery or visuals in game.

**No installation, game launch/termination, mod activation, hot reload,
settings/save edits or production change is authorized here.**

For a later separately authorized local test: recover real worktree, verify
the installed UE4SS and exact source identity, stop with game closed,
preserve installed probe and rollback outside loader paths, install only
this research observer, then let user start game normally and visit
Open → leave → Take → leave → Check → leave, ideally adjacent A→B.
Leave stock TipHUD fully visible. Record exact logs, actor/bool sequence,
callback delivery or its absence, and independent native visibility.
Restore the prior active own probe after host closes and hash-check all
touched files. No runtime acceptance or performance claim is implied.
