# BeginPlay + CanShow Open join — one natural Open mapping/pose PASS, disabled

## Corrected revision runtime result — 2026-10-29

Exact source603ab6be645bbc2b552f3e88e0d2448c981485b1 / Lua SHA256
932901d8766bfb3640ddd48f1d7811e8ccadbf83df2b63bc597dfece225ea664 verified unchanged.
Log SHA256 `953bcf244a2c6bb952092a99bbac290556f90ff7a56be81c40331281fd2f8e1c`;
raw log/events/result local at budget-fix/runtime-20261029T171750Z.

- 20:13:44.145: two script registrations10/10 and11/11, then WAITING.
- 20:13:52.147–52.148:3 Open initialization pairs acquired after manual reload.
- 20:13:52.727: ACQUISITION_CLOSED init=128 retained=3, selection_continues=true,
  deadline_unchanged=true. Only own BeginPlay hook removed, not the CanShow reader.
- 20:14:18.239: CHECKPOINT metadata_loaded=true init=128 ready=3 show=6.
- 20:14:23.741: MATCH reciprocal=true for exactly one pair below, then finite POSE1.
- 20:14:27.189: explicit user POSE2 for that same checked identity, changed=false.
- 20:14:30.539: own CanShow unregister accepted and STOP reason=user result=MATCHED,
  init128/open3/not_ready0/ready3/show415/visible_open1/unmatched0/matches1/poses2,
  hooks_remaining=0. Elapsed46.394s before120s, not a budget/timeout stop.
- 20:14:41.760: Event loop end. No probe failure/pending-unregister/dispatch events.

Live identifiers in **this process only**, not reusable selectors:

| Role | Exact identity |
| --- | --- |
| Actor | `/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001` |
| Concrete actor class | `/Game/MainContent/Act/Discoveries_BP/common/item_lootbox02.item_lootbox02_C` |
| Component | exact actor path + `.ExtendedWidget`, class `/Script/Genesis.ExtendedWidgetComponent` |
| Widget | `/Engine/Transient.GameEngine_2147482619:MainGameInstance_BP_C_2147482611.TipHUD_C_2147478037`, exact TipHUD_C class |
| Addresses actor/component/widget |2147071029840 /2147055182048 /2144665516864 |

Both POSE records:

| Native read | X / Y / Z, or Pitch / Yaw / Roll |
| --- | --- |
| Component world location | -40619.4648 /12241.2139 /5672 |
| Component world rotation |0 /109.320808 /0 |
| Component scale |1 /1 /1 |
| Actor world location | -40619.4648 /12241.2139 /5552 |

The printed component anchor is120 world units above this actor origin, with
matching X/Y in these samples. This is not a universal offset to hardcode. Both
poses were unchanged; moving-anchor behavior, camera-facing behavior and wider
placement coverage are not established by two identical samples.

**Closed gate:** one naturally shown RU Open TipHUD is now joined through exact
identity and rechecked reciprocal pointers to its concrete actor/component and
finite world pose. Both script readers remained usable through this one manual
reload, without automatic re-registration. This does not prove UFunction objects
were unloaded/recreated, all map lifecycles, other Open classes or production
target priority. visible_open counts qualifying waiting callbacks, not physical
button presses or a proof that only one prompt exists globally.

Game verified closed; log archived, only own enabled.txt removed. Corrected Lua
remains unchanged/disabled. All24 other baseline mod/loader files still matched;
all88 other current files retained hashes across disable. No rollback of other
mods/config/save state. No new code, observer or World component installed.

Next independent step is source preparation of one owned World WidgetComponent
experiment at this verified natural anchor, reusing the accepted independent
UserWidget host. Registration/resources, camera-facing orientation, scale/depth,
actual Hilda occlusion and own teardown still need their own evidence. Original
prompt must remain visible in the first World experiment. No World installation
is authorized by this result; World runtime and production remain **BLOCKED**.

## Corrected revision installation history — before this run

Exact source603ab6be645bbc2b552f3e88e0d2448c981485b1 installed with the host closed.
Own main.lua replaced, empty enabled.txt added; source/installed hash is932901d8...
(full SHA256 below). Only this IIP probe is enabled. All24 other mod/loader files
and62 current config/save files retained hashes. Pinned UE4SS DLL identity matched;
current CombatHUD/other mods preserved. No game launch/reload/hot reload.

Verified old995a581f... source and disabled marker state retained outside loader
at local beginplay-probe/budget-fix/install-20261029T165639Z, with new source copy,
pretest log/settings/mods.txt, baseline/installed manifests and guarded rollback.ps1.
Rollback restores the old main.lua and removes only the new marker, after hash
checks and closed-host check. It does not restore other mods or user data.
Installation is not runtime acceptance. Repeat only the one user procedure below;
ACQUISITION_CLOSED should leave CanShow able to select the retained pair(s).

## Corrected research revision — 2026-10-29

User authorized preparation and installation of the budget correction. Current
[source](Scripts/main.lua) SHA256
`932901d8766bfb3640ddd48f1d7811e8ccadbf83df2b63bc597dfece225ea664`.
On the128th BeginPlay callback, acquisition becomes inert before unregistration;
ACQUISITION_CLOSED logs retained pairs and an unchanged deadline. Only own BeginPlay
hook is released; checked candidate records and CanShow remain active. There is
no new acquisition/re-registration, no change to the8-candidate/4096-CanShow/
120s/4-pose bounds, identity checks, return policy or read-only scope. A pending
BeginPlay removal cannot consume more contexts because the acquisition flag is
already false. Candidate overflow still stops globally rather than hiding a ninth
candidate; CanShow/pose/time limits and explicit stop still end everything.

`python tools/test.py`:108 tests/10 suites PASS,25 join policy tests. The new real-run
regression acquires3 pairs, reaches128, then matches the second pair via CanShow.
Other new checks cover pending acquisition unregistration/inert late callbacks
and unchanged timeout/pose cap. Prior runtime evidence below belongs to unchanged
3497ab5 bytes, not acceptance of this correction. No production release/VERSION
change or World payload. Exact replacement installation is recorded above; runtime pending.

## Original revision runtime result — 2026-10-29

Exact installed3497ab5234e61084cf75fe32fe1a16d4b92de443 source/hash below unchanged.
Native loader83330635 registered script IDs10/10 (parent BeginPlay) and11/11
(CanShow) at19:41:14.437; WAITING19:41:14.4375096. After the requested manual reload,
ACQUIRED appeared three times at19:41:34.642–34.643. This confirms parent script
dispatch after reload and successful read-only ownership/widget getter checks.

All actor paths share
`/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.`
Their components are the exact actor path plus `.ExtendedWidget`; widgets share
`/Engine/Transient.GameEngine_2147482619:MainGameInstance_BP_C_2147482611.`

| Actual actor suffix | Actual widget suffix |
| --- | --- |
| 0-1_lootbox_01_mat_ST001 | TipHUD_C_2147477784 |
| 0-1_lootbox_02_phy_r1t1 | TipHUD_C_2147477777 |
| 0-1_lootbox_03_phy_r1t1 | TipHUD_C_2147477772 |

ACQUIRED is emitted only after non-default actor/base checks, Open/Interact25,
argument ownership, actor.ExtendedWidget↔GetOwner and GetWidget/GetUserWidgetObject/
Widget equality and NewUserWidget compatibility. Those checks executed without
failure for three distinct initialization pairs. Numeric addresses and concrete
actor classes were not printed at this stage; do not invent them or identify
the user's currently visible Open from actor names alone.

At19:41:35.2264700 STOP reason=init_budget result=NO_CANSHOW:
init=128 open=3 not_ready=0 ready=3 show=0 visible_open=0 unmatched=0 matches=0
poses=0 hooks_remaining=0. Both own script unregister operations were accepted.
Elapsed20.7889604s from arm, before120s; Event loop end19:42:22.2775601.
No FAILED/UNREGISTER_PENDING/DISPATCH_FAILED from the probe.

**Partial result:** acquisition/reciprocal initialized pairing and BeginPlay
registration through this reload PASS. Current visible CanShow selection and
world pose remain NOT_OBSERVED. CanShow callback survival is neither proved nor
disproved: the entire observer was stopped by its initialization budget before
any CanShow callback was observed.128 counts callbacks, not distinct actors;
the8-Open limit was not reached. No world transform getter ran.

Log SHA256 `62e8dcd171f9de0b4056ce2df4aa8470be07827cd5034aaf90ad9d8b9a74636f`;
raw log/events/result retained locally at beginplay-probe/runtime-20261029T164344Z.
Game verified closed; only own enabled.txt removed after archiving. Source remains
unchanged/disabled. All24 prior mod/loader hashes still matched installation;
all87 other current files retained hashes across disable, including other mods.

The next correction proposed after that original run was to close only acquisition
at the existing128 callback budget, keeping the already checked≤8 pairs and the
CanShow selection window within the same120s/4096/4-pose limits. Do not raise the
init cap, repeat unchanged, automatically retry or install a new revision in this
run. That budget correction is now prepared/tested above and authorized for
installation. It may permit selection, not
guarantee a CanShow callback. World rendering/production remain BLOCKED.

## Installation history — 2026-10-29, before this run

User authorized installation; host verified closed before copying/enabling.
Exact source3497ab5234e61084cf75fe32fe1a16d4b92de443 installed unchanged as
ImmersiveInteractionPromptsOpenJoinProbe, Scripts/main.lua + empty enabled.txt.
Source/installed SHA256 both
`995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3`.
Pinned UE4SS.dll SHA256ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290
matched. All24 previous mod/loader and61 current config/save files retained hashes;
other mods/current CombatHUD preserved, prior IIP probes disabled.

Outside-loader local backup at beginplay-probe/install-20261029T163735Z contains
exact source copy, prior UE4SS.log/settings/mods.txt, installed/verified manifests
and hash-guarded rollback.ps1 restoring the previously absent target. No source
edit, launch/termination/reload/hot reload or runtime observation. Test below is
now authorized for this installation; results are still PENDING.

## Original source preparation record — 3497ab5

2026-10-29. Steam1.09/build12996889, UE4.27, UE4SS83330635. Separate research-only
[Original Lua source](https://github.com/NikichMods/ImmersiveInteractionPrompts/blob/3497ab5234e61084cf75fe32fe1a16d4b92de443/research/interaction-prompts-owner/open-binding/beginplay-probe/Scripts/main.lua), no dependencies beyond the pinned loader APIs.
SHA256 `995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3`.
Prepared without installation/execution; later installation recorded above.
Old SetShow source/result stays unchanged and disabled.
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

In the corrected revision, the128th initialization callback closes acquisition
before reading that context, retaining checked pairs for CanShow. The4096th CanShow
callback ends everything with BUDGET. Ninth distinct Open actor also stops, rather than silently
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

## Historical user procedure — completed once, result above

Install only these exact bytes in a new research-only mod, with previous IIP probes
disabled, verified rollback and a closed game. Exact installation is recorded above;
no game or save reload has been performed by the agent.

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

## Original offline verification — before the correction

`python tools/test.py`: **105 tests /10 suites PASS**, including22 new Lua policy
tests. Read-only engine-object mocks reject all property writes; callbacks are
asserted nil. Tests cover two single callbacks, partial registration cleanup,
metadata recreation, missing metadata/invalid flags/IDs, duplicate/ambiguous/stale
identity, default/archetype rejection, no-ready/no-join diagnostics, absolute time
and count bounds,4 poses, explicit stop/retry, inert late callbacks/dispatch failure
and finite-pose validation. No mock result is native reload/render/GC acceptance.
Local test output, source contracts and input hashes are retained ignored.
