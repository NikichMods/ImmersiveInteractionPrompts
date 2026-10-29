# BeginPlay + CanShow Open join — READY_SOURCE, runtime NOT_TESTED

2026-10-29. Steam1.09/build12996889, UE4.27, UE4SS83330635. Separate research-only
[Lua source](Scripts/main.lua), no dependencies beyond the pinned loader APIs.
SHA256 `995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3`.
Not installed or executed. Old SetShow source/result stays unchanged and disabled.
No World component, UI creation, Aphes, input remapping, game/save/config writes,
object enumeration, forced asset load, initialization call or hot reload.
Production and World-space runtime acceptance remain **BLOCKED**.

## Exact contracts and reload lifetime

Uses the two exact script paths selected in [ROUTE_REVIEW](../ROUTE_REVIEW.md):

- `/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C:ReceiveBeginPlay`:
  non-Native, zero inputs/void, actor context; observed by the loader after this
  parent script body. BaseLoot's explicit parent-call source proof is reused.
- `/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:CanShow`: non-Native, zero inputs,
  bool return. The proven callback supplies context only, not a return argument.

Before the one arm attempt, both exact UFunctions must already be loaded and
non-Native. No UObject/function wrapper is retained. RegisterHook(path,callback)
is called once per function, with no invented third script callback; require
positive equal IDs. Both readers explicitly return no value on **every** path,
including guarded failures. A non-nil pcall result must never reach CanShow.
If registration2 fails, registration1 is removed. Cleanup tries both owned IDs
independently; no other hook is removed. Missing startup API/key collision disables
the probe before registration. HasAnyFlags rejects CDO/archetype candidates.

New source check of exact UE4SS:

| Retained source | Relevant lifetime contract |
| --- | --- |
| LuaMod.cpp1138–1186 | get_object_names captures the function/Outer FName chain; exact lookup compares that chain, not the original UFunction address. |
| LuaMod.cpp4271ff /6324ff /7253 | Script registrations keep names plus Lua registry entries at mod scope; script post dispatcher matches Stack.Node by those names and ignores nil return. |
| LuaMod.cpp6477–6551 | Reviewed LoadMap pre/post handlers forward registered map callbacks; they do not clear script registrations. This probe registers no map hook. |
| LuaMod.cpp6129–6164 | Mod uninstall clears its script callback records. An actual mod restart/uninstall is outside this test, not something the probe repairs. |
| LuaUObject.cpp86–90 | Object-delete listener invalidates tracked UObject wrappers; it does not erase the script callback registry. |
| LuaMod.cpp1748ff | UnregisterHook resolves the function by path. For scripts it marks only the matching own registry ID inactive. Metadata absence can prevent immediate unregistration. |

This supports a **possible persistent registration over one manual save reload**
without rooting the old UFunction or automatically registering again. It is not
live reload/dispatch proof for this game. Only ACQUIRED/CanShow evidence after the
user reload can establish that. Path/class/address are bounded primitive identity
checks, not UObject serial-number handles or a production map-lifetime solution.

Stop first makes both callbacks inert, drops all target/candidate records, then
requests removal. If metadata is unavailable, UNREGISTER_PENDING/remaining IDs
are explicit; F7 can retry once metadata is back, without rearming. A dispatch
failure also makes callbacks inert and drops records; explicit stop or normal
exit remains required for registration removal. No automatic retries/rooting/GC.
Outstanding IDs mean our removal request is pending, not live UI ownership.
Explicit cleanup retries preserve the first terminal result, including identity
failure; successful later unregistration must not rewrite it as a successful test.

## Bounded acquisition and exact join

Ctrl+Alt+F8 starts once; F7 chord stops. Deadline120s includes loading time. A single
delayed stop is scheduled; every callback/control checks the wall-clock deadline
before context reads. A blocking native load cannot be interrupted by Lua; expired
callbacks stop at the next dispatch rather than extending the observation window.

BeginPlay actor ancestry, own argument component owner and Open/Interact25 are
checked. At most8 distinct Open actor identities, **including NOT_READY attempts**,
are remembered as primitive keys. Repeated BeginPlay for the same identity never
retries a null widget. Ready records require actor.ExtendedWidget↔component.GetOwner,
GetUserWidgetObject/GetWidget/Widget equality, exact TipHUD class and compatible
NewUserWidget. No sender-is-owner assumption. No transform reads during acquisition.

CanShow checks current stored visible/enabled RU «Открыть» state and joins its
actual widget identity to exactly one record. Actor/component/widget are resolved
fresh and reciprocal links repeated. Ambiguity, missing/replaced identity or changed
ownership refuses capture; no first/nearest/alternate target. Require stock Screen1
component screen membership/visibility. These states do not prove native CanShow's
bool return, interaction priority or rendered pixels; those values are untouched.

MATCH fixes one target, discards other records and releases only the acquisition
hook. Only then is component world location/rotation/scale read, plus actor origin
separately. The first POSE is automatic; F8 adds manual poses up to4 total.
CanShow subsequently validates the selected target/state but does not auto-sample
transforms. No monitoring loop. Missing/disappeared identities are detected on a
relevant callback/manual sample; total expiry also ends the record lifetime.

128th initialization callback /4096th CanShow callback ends with BUDGET before
reading that context. Ninth distinct Open actor also stops, rather than silently
discarding it and claiming uniqueness. Up to8 ACQUIRED/NOT_READY lines,4 POSEs,
one MATCH and two manual waiting CHECKPOINTs; no per-frame log. Stop summary keeps:
init/open/not_ready/ready/show/visible_open/unmatched/matches/poses and owned IDs left.

| Final diagnostic | Meaning |
| --- | --- |
| NO_BEGINPLAY | No observed parent BeginPlay after arm; not evidence that parent never runs. |
| NO_OPEN_CANDIDATE | Initialization was observed but no eligible Open/Interact actor. |
| NO_READY_WIDGET | Open actor(s) seen but no ready own TipHUD pair; no forced initialization/retry. |
| NO_CANSHOW | Ready pair(s), no observed CanShow callbacks. |
| NO_VISIBLE_OPEN | CanShow observed, but no qualifying current Open state. |
| NO_MATCH | Qualifying Open existed but no exact eligible candidate join. |
| IDENTITY_ERROR | Pointer/ownership ambiguity, disappearance/replacement or inconsistency. |
| NOT_LOADED / CONTRACT_ERROR | Required function absent, flags/IDs/arguments/structure/finite pose differ. |
| MATCHED | At least one exact join and finite pose; no World-render/production claim. |

Counters describe callbacks, not physical actions or distinct widgets. A stop
reason (user/timeout/budget/target state) accompanies the result. No automatic next
route or repeated observation follows a negative result.

## Future user test — requires separate closed-game installation authorization

Install only these exact bytes in a new research-only mod, with previous IIP probes
disabled, verified rollback and a closed game. That has **not** been done here.

1. Start normally and load the existing save so both BP functions can be resident.
   Ctrl+Alt+F8 once arms the120s observation. No added text or visual effect is expected.
2. Manually reload that same save **once**, using the normal game UI. Do not restart
   the process, hot reload or save new diagnostic state. Loading counts toward120s.
3. Approach one natural Open prompt. F8 snapshots only after a match; while waiting
   it can log a metadata/counter checkpoint. Move camera/character slightly and
   press F8 again; unchanged component pose is valid, especially with camera motion.
4. Ctrl+Alt+F7 stops. Exit normally and retain the loader log. If no match occurs,
   do not rearm/reload again in that process; report the one negative result.

Log success: two REGISTERED (equal IDs each) → WAITING → ACQUIRED after natural
reload initialization → MATCH reciprocal=true → POSE(s) → STOP result=MATCHED.
Source supports registration persistence but actual metadata availability, parent
dispatch, candidate capacity, ready-widget timing and callback survival all remain
runtime gates. Normal original UI/action behavior must also be observed by user.

## Offline verification

`python tools/test.py`: **105 tests /10 suites PASS**, including22 new Lua policy
tests. Read-only engine-object mocks reject all property writes; callbacks are
asserted nil. Tests cover two single callbacks, partial registration cleanup,
metadata recreation, missing metadata/invalid flags/IDs, duplicate/ambiguous/stale
identity, default/archetype rejection, no-ready/no-join diagnostics, absolute time
and count bounds,4 poses, explicit stop/retry, inert late callbacks/dispatch failure
and finite-pose validation. No mock result is native reload/render/GC acceptance.
Local test output, source contracts and input hashes are retained ignored.
