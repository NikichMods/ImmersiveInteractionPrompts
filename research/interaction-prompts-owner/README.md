# Observation probe readiness — 2026-10-28

**Current preferred direction:** [world-space/README.md](world-space/README.md).
Source/static study completed; executable World payload BLOCKED. Separate owned
WidgetComponent preferred conditionally; independent concrete UserWidget and exact
natural Open binding are missing. Setter-only original-component migration is not
safe/proved. Stock depth-capable materials exist; no mask/PostProcess detour needed.
No game run/install. Earlier screen-position result below is a verified fallback.


**Verified screen-position fallback:** [viewport/README.md](viewport/README.md).
Own HUD-root Canvas rendering/manual cleanup passed; user selected initial50%/78%
as the continuing baseline. Arrow tuning did not pass, reset/commit keys unverified;
no input-routing cause claimed. Probe disabled. Original TipHUD unchanged;
production lifecycle/other resolutions/final styling remain open. Production BLOCKED.

**Current composition result:** [composition/README.md](composition/README.md).
Native stock PNG import/display, F-height placement and state-change cleanup
passed one bounded run; user reports visual success. Native lower translation
restored; both children detached/resource references cleared. Probe disabled.
Final styling/full lifecycle remain open; no manual-attached removal/READ claim
from this run. Production BLOCKED.

**Current Aphes writer:** [aphes-text/README.md](aphes-text/README.md), setter/
ownership review followed by one user-confirmed OPEN→READ/manual cleanup run.
Native glyph rendering passed; probe disabled. Final design/GC/lifecycle remain open.

**Current dynamic-font investigation:** [DYNAMIC_FONT_READINESS.md](DYNAMIC_FONT_READINESS.md).
Shared replacement is blocked; [font-template/README.md](font-template/README.md)
records one successful private transient UFont creation/storage run; probe disabled.
That storage test itself contained no writes/render; the separate Aphes result is above.

**Current PNG-header preparation:** [png-header/README.md](png-header/README.md),
one local Aphes glyph PNG and Texture2D import source, READY for one separately
permitted test; not installed/run. Completed UI/divider results are reused.

**Current divider preparation:** [DIVIDER_READINESS.md](DIVIDER_READINESS.md),
UImage/color-only Box rendered visibly; both own children detached by key-control,
probe disabled. The successful label-only run remains its separate narrow baseline.

**Completed ui-child history:** [stock-font ui-child](ui-child/README.md) first stopped at the
live layout guard before construction. A second run measured X=38, not designer
X=88. Revised measured-baseline source then created/rendered/detached one OPEN
label successfully; user confirmed original text/icon stayed in place. Probe now
disabled, the bounded test is complete. Divider also completed separately;
Aphes font-specific blockers are not prerequisites to these established results.

**Cooked-font route:** [toolchain checkpoint](FONT_RESOURCE_READINESS.md) remains
BLOCKED without UE4.27 import/cooker. No cooked Aphes resource was created. This
does not block the distinct transient-provider source prepared above.

**Current visual stage:** [layout/font readiness](VISUAL_READINESS.md) confirms
the seven slot edges and selects additive siblings under CanvasPanel_6 with an
isolated font provider. Stock-font label/divider and Template storage already
passed. Aphes writer has passed its bounded visual run; the new composition remains untested.
Native C++/UEPseudo bridge remains deferred.

**Current adopted scope/result:** [minimal CanShow state observer](can-show-state/README.md)
confirmed live callback/text/state reads from three TipHUD instances; the first
run is preserved in docs/VERIFIED_RUNTIME.md and the probe is now disabled.
UEPseudo/native-array/delayed-readback work remains deferred. Earlier proposals
and blockers below are historical, not prerequisites for repeating that result.

**Historical full-observer route:** [observer route review](OBSERVER_READINESS.md) stops before Lua payload
creation: the pinned lower native hook-frame implementation is unavailable, so
callee Locals provenance/lifetime for the actual Blueprint call is not established.
UHT signature evidence remains valid. No observer is ready to install.

**Earlier UHT result:** [built-in UHT declaration](UHT_SIGNATURE.md) closes the missing
SetupTipMessage2 declaration gap. Preparation of one observer is the next step;
hook activation, final writer and production acceptance remain unproved. The
initial blocker and proposals below are historical evidence.

**Earlier metadata review:** [metadata API review](METADATA_CAPTURE.md) checked the proposed
next step and found that UE4SS 83330635's Lua FProperty wrapper lacks parameter
flag readers. The original observer blocker remains; a complete Lua capture is
also blocked. The procedure below is the historical initial proposal, not a
currently ready payload or installation instruction.

**Research-only; BLOCKED before hook registration. No executable probe or
installable payload was created.** This is the explicit technical-blocker outcome
of the requested offline preparation, not a runtime failure or proof that UE4SS
cannot observe these functions. Production evidence gate remains **BLOCKED**;
VERSION remains 0.1.0.

## Question and sufficient evidence

Correlate a real actor, its ExtendedWidget and TipHUD with native action text,
texture and show/hide changes; compare native update with bounded later readback.
Existing static evidence proves the Blueprint call chain, not the final writer.
Looking at the screen cannot identify internal owners or write ordering, so a
narrow observer is justified **after** its reflection/marshalling prerequisites
are established. Re-exporting all assets would not establish the missing native
signature.

## Recovered state

- Independent repository: `NikichMods/ImmersiveInteractionPrompts`, origin
  `https://github.com/NikichMods/ImmersiveInteractionPrompts.git`.
- Initial clean main: `0db203443a333e70beadd57ddfc08963559e1ac2`; no staged,
  unstaged or untracked files; ignored `.local` preserved. One registered worktree.
- Requested local branch initially `05d058a`; fresh fetch found two remote-only
  commits and no local-only commits. Switched the clean checkout to that existing
  branch and fast-forwarded to `838b51142037539f520e2e92e979ae4e0ab6ab40`.
  No reset, stash, clean, history rewrite or other checkout changes.
- Rules: local DevRules main `1dba779`, supplemented by current fetched
  `origin/main` `c9a90c04336072e821761e376d1702d63899c4ab`; inspected applicable
  rule differences without changing its checkout. Shared Research current at
  `e7437f68fe9466d0ab43311117e8087c54a12b37`; remote heads verified live.
- Existing installed UE4SS log identifies `v3.0.1 Beta #0`, SHA `83330635`,
  UE4.27. Installed DLL SHA256
  `ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`
  equals the retained original package DLL. This checks identity, not new execution
  of the probe. Existing log is historical input, never a new test session.

## Exact functions: established and missing

| Exact boundary | Available evidence | Unresolved prerequisite |
| --- | --- | --- |
| `/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:SetupTipMessage_Proxy` | Existing asset export: non-native Blueprint event; eight inputs, including six const reference/out arrays; bytecode copies parameters into persistent frame | Actual loaded UFunction properties and array/enum marshalling for this boundary have not been observed |
| `/Script/Genesis.ExtendedUserWidget:SetupTipMessage2` | Exact native import/call at ubergraph offset 713; text/image arrays reach this consumer | No native UFunction declaration/property list in available exports, SDK or reflection snapshot; full parameter flags/order/inner types and loaded function classification unverified |
| `/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:CanShow` | Non-native Blueprint event; only `Parm` is bool `ReturnValue`; other listed properties are locals | Actual loaded function/binding unverified; Blueprint callback does not receive its return value as an input |

The bounded local lookup covered this repository's retained exports, relevant
sibling research/diagnostic evidence, installed UE4SS files/log, retained UE4SS
package and game-tree dump/SDK/usmap filenames. It found no usable native
`SetupTipMessage2` declaration or prior successful observation of these exact
hooks. This is a statement about inspected evidence, not absence everywhere.

## Version-pinned callback findings

Primary source: [UE4SS LuaMod.cpp at 83330635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp).
The [RegisterHook documentation](https://docs.ue4ss.com/dev/lua-api/global-functions/registerhook.html)
is supporting guidance, not a replacement for checking this installed revision.

- Lines 4242–4299: registration resolves an already loaded UFunction. Routing
  checks its actual function pointer and `FUNC_Native`; a path prefix alone is
  not a capability check. Native hooks register separate pre/post callbacks;
  Blueprint registration retains the second Lua argument as the script callback,
  not a separate pre/post pair.
- Lines 6323–6477 and 7250–7259: UE4.27 script callbacks run through the
  ProcessLocalScriptFunction **post** boundary. Script marshalling skips
  `ReturnValue`; a no-input Blueprint CanShow callback receives context only.
  Returning a non-nil value can overwrite the result; every future observer
  callback must return nil. Calling CanShow again would make a new query, not
  read the original result, and is not an approved substitute.
- Lines 132–233: native input properties are marshalled **before** entering Lua;
  out/reference properties use `FindOutParamValueAddress`. Omitting arguments
  from a Lua callback does not bypass engine-side parameter handling. A Lua
  `pcall` around observer reads cannot validate this preceding native work.
- [LuaUFunction.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUFunction.cpp)
  exposes `GetFunctionFlags`; UFunction inherits UStruct, whose
  [ForEachProperty](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUStruct.cpp)
  provides a source-confirmed reflection entry point. That API's existence does
  not supply a live Genesis UFunction or prove safe marshalling of its parameters.
- The pre-existing loader log reports custom events enabled and the
  ProcessLocalScriptFunction posthook registered. That confirms loader setup
  in that historical session, not registration/execution of these three hooks.

**Decision:** the requested prerequisite “verify actual signatures before
registering callbacks” cannot yet be met for SetupTipMessage2. Do not infer its
Lua ABI from the call operands. Do not ship a context-only hook as a workaround,
silently omit this consumer, substitute a parent CanShow/global TextBlock setter,
or call interaction/UI functions to manufacture observations. No current evidence
establishes that registration would crash; safety is unproved, not disproved.

## Offline checks and retained evidence

Ran the ignored `check-probe-prerequisites.py` using the configured Python:
validated the two Blueprint flags/parameter distinctions, native import at 713,
absence of a SetupTipMessage2 definition in that export, pinned source control
flow and installed DLL hash. Result: `OFFLINE_PREREQUISITE_GAP_CONFIRMED`.
`python tools/test.py` also completed and honestly reported no automated runtime
test suite. These are offline checks, not engine binding, rendering or acceptance.

Reused original export hashes from VERIFIED_RUNTIME.md; they still match.
Local source snapshots/check result remain under ignored
`.local/research/interaction-prompts/`. No game assets, raw logs or private
paths are included here. Local UTF-8 source snapshot SHA256:

| Source at 83330635 | SHA256 |
| --- | --- |
| LuaMod.cpp | ecc9448999fdac16d4b9181d73f99aafeb8f75dd12ad921e3f7f7922d8298227 |
| LuaUFunction.cpp | 666aa018513f0e3297357f9463fa33e184b0c809725545a490b3c1dfdc190b14 |
| LuaUStruct.cpp | 794192fb1646a1ee5a35d8da0872335bb4a4032969cabbbae57e339e170667d8 |

## Smallest next step and future observation contract

First obtain a **targeted reflection-only metadata capture**, separately authorized
for installation/execution, for the exact three UFunctions above. It should record
loaded identity, flags and parameter properties (including nested array types and
reference/out/return flags), without RegisterHook, calls to the target functions,
asset loading, actor scans or UI writes. Resolve its read-only reflection API
before preparing that payload; the current report is not such a payload. If a
function is not naturally loaded, report it missing, without force-loading it.
An existing trustworthy exact-build declaration can instead close this gap offline.

After metadata review, prepare **one** observer. Proposed bounds: ten minutes,
600 diagnostic lines, at most eight widget identities; changed-state readback no
more than four times per second and at most two seconds after a native update,
using a separately verified game-thread scheduling mechanism. These are preparation
requirements, not implemented capabilities. Never retain callback parameter
wrappers for delayed use. Revalidate each object; stop observation on contract,
object-limit, time, log-budget or scheduling failure; callbacks become inert and
return nil. Record missing fields as unavailable. No global scans or per-frame work.

Distinguish future startup, registration, first observed call, change/readback and
stop/timeout markers. Registration alone is not successful execution. A registered
hook with zero calls is `NOT_OBSERVED`, not evidence of hidden UI. Record actor
component ownership and widget identity only when directly linked; Ladder_BP
remains unlinked unless the actual object supplies evidence. Bounded readback can
detect sampled later overwrites, never exclude transient writes between samples
or identify every final writer by itself.

Future gameplay pass, **only after** the metadata gap is closed and observer
preparation/installation approved:

1. Approach an available pickup; observe the prompt normally.
2. Repeat at a chest and a document; preserve the actual localized action.
3. Approach a ladder/descent if available; record unavailable cases as untested.
4. Change target, leave range and return; correlate actual show/hide and identities.
5. Switch keyboard/gamepad through normal player input.
6. Open/close an ordinary menu and observe the same prompt state.

Do not invoke interactions for the player or change saves/settings. User visual
correlation remains necessary alongside internal observations.

There is currently **nothing to enable, install or roll back**. For a future
approved payload: use a distinct research-only loader folder; freeze source and
hash; verify host closed without terminating it; preserve any previous same-probe
payload and current log outside loader paths; install only that payload and verify
hashes. Enable/disable via the loader's separately verified mechanism with the
host closed. Do not edit shared mod activation files by assumption or hot-reload.
Rollback removes only this probe or restores its verified predecessor; retain
other mods untouched. Capture logs locally before another launch. No installation,
game start/termination, UI/settings/save write or production change occurred here.
