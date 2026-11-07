# ShowTipEvent — read-only owner transition observer

**HOOK REGISTRATION PASS / CALLBACK DELIVERY NOT OBSERVED / ROLLED BACK.**

## Runtime result — 2026-11-07

The user reported completing the run. All four installed Lua hashes matched
the installation record before rollback. The stock loader started the mod
(UE4SS line 654), the observer joined 34 ready owners (Open 6, Take 18, Check
10), and the exact base-class script hook registered as `(12, 12)` at
03:40:22.958 (lines 693–694). **Zero callbacks were recorded.** There were no
`INTENT`, `UNRESOLVED`, `CORRELATED`, `NO_MATCH` or probe stop/error entries.
The final map reset followed about 61 seconds after arming (line 768).
Genesis logged normal exit with status 0 (lines 3126–3128).

The exact registered hook did not yield an observable selection signal in
this session. The observer samples visibility only after a delivered event,
so it captured no independent visibility timeline. The user did not specify
individual visible episodes or adjacent-object switching. Delivery by action,
event order, correlation and latency remain unknown. This result does not
identify the dispatch gap or contradict the earlier static native trace.

After exit, the observer was disabled and the prior CompactLayoutProbe
marker restored. All 12 recorded CompactLayoutProbe files including its
marker were verified. Both raw logs are archived locally.

- UE4SS.log SHA-256 `6be7484be7d95bad1dc9fc898da82a3ea9b0783d9165c64fe197b42de2a369c8`.
- Genesis.log SHA-256 `e8c3fc3ba9ece3c79c0ec159a546cf61f886638e9f4279b83941320770169cf8`.

## Verified installation — 2026-11-07

User-authorized closed-host installation of source
`e4c8164093a7a8c5338e5bd30e6ec3a9debcd303` on Steam 1.09/build 12996889
and UE4SS 83330635. The only active IIP mod is
`ImmersiveInteractionPromptsShowTipEventObserver` via `enabled.txt`.
The previously active CompactLayoutProbe was disabled by its marker only.
Its 12 recorded files, including the original marker, were verified in a
rollback snapshot outside UE4SS. After switching, 227 existing files,
including other mod files, settings and saves, matched their preflight hashes.

| Installed Lua | SHA-256 |
| --- | --- |
| `IIPInteractionSource.lua` | `39f7da52a1297937c3866d9a55d2ff73639a5a45eed2fdb5c9bfe3903cf5850c` |
| `IIPOpenVisibility.lua` | `c32fe59ba3d3e20e4619bc8e2c7c63e1eb05cd836e408429865709691d2f9806` |
| `IIPShowTipEventObserver.lua` | `1a43b425bcb0a457edbd84b22122774f71283f1d55f44e55d275bc9cec285019` |
| `main.lua` | `0768d0fe796983a53210207fbd7f40470624f8ec91763b960c8f70eb1c3485d1` |

[CI 42317715437](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42317715437)
and local checks report 499 passing offline tests. The local Windows run
normalized path separators in one historical manifest assertion in memory.
Game launch and hook delivery remain pending the user-operated trial.

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

For the user-operated local test, start the game normally and visit
Open → leave → Take → leave → Check → leave, ideally adjacent A→B.
Leave stock TipHUD fully visible. Record exact logs, actor/bool sequence,
callback delivery or its absence, and independent native visibility.
Restore the prior active own probe after host closes and hash-check all
touched files. No runtime acceptance or performance claim is implied.
