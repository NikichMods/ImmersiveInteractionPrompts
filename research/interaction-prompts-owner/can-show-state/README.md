# Minimal CanShow state observer

**First runtime observation succeeded 2026-10-28; probe now disabled.** User-adopted
reduced scope: current text and state of TipHUD at one zero-input Blueprint
boundary. UEPseudo/native-array investigation is deferred; production remains
BLOCKED. This does not implement the earlier full observer specification.

## Payload identity and behavior

- Source: [Scripts/main.lua](Scripts/main.lua), research ID `can-show-state`.
- SHA256: `ae75d8419d988ea91be288ba1aa33760ab980b354cd4d74d791564eec5109e09`.
- No runtime dependencies beyond the existing UE4SS `83330635` baseline and
  standard Lua libraries; no UEHelpers or proprietary payload included.
- One exact hook:
  `/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:CanShow`, Blueprint **post**.
- **Ctrl+Alt+F10** starts after the save/prompt has naturally loaded; pressing it
  again stops. No rearming/retry in the same session, no force-load. Existing
  UE4SS chord registration is checked before adding this session-only control.
- Observes only widget/class/name/address, TextBlock_89.Text, and TipHUD's stored
  Visibility, RenderOpacity and bIsEnabled. Invalid child text is explicitly
  `text_state=unavailable`; no setter or original CanShow invocation is used.
- One field snapshot per wall-clock second globally, logging only changes per
  identity. Maximum eight widget identities and 600 diagnostic lines including
  the terminal record; at most ten minutes from activation. Text is bounded to
  1024 bytes; control characters are escaped to keep each event on one line.
- Any contract/scheduling error stops the whole observer. Registered callbacks
  then return nothing and perform no host reads. No global object scan,
  parameter arrays, delayed UI readback, font/texture/material/actor inspection,
  UObject retention or production integration.

Two scheduler uses are **control only**: transport the diagnostic key's action
onto the game thread; schedule one timeout. No scheduled callback reads a widget.
Every natural CanShow callback also checks the deadline before host access; if
game-thread dispatch stalls, it cannot read beyond that deadline upon resuming.
All engine/parameter/FText wrappers are local to the synchronous callback; only
strings, counts and timestamps persist. Stop leaves only inert research callbacks
and the session key binding until ordinary process exit; no physical unhook or
hot-reload contract is claimed.

## Why this route avoids the previous blocker

The retained TipHUD export (SHA256
`8c9a885d2904956a4899d979b2c4b60f355f62ec05b7e53b45d95938dc1be16e`)
defines CanShow as non-native with **no input parameters**. The sole Parm is
ReturnValue:Bool, Parm|OutParm|ReturnParm; the other properties are Blueprint
locals, not arguments. This is combined with the loader's actual dispatch code,
not treated as a Lua ABI by itself:

1. [RegisterHook at 83330635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L4200)
   resolves a loaded exact UFunction and selects the script branch for its actual
   pointer/flags. The probe checks function identity/type and absence of
   FUNC_Native (`0x400`) before registration; it expects equal script-hook IDs.
   The numeric flag is documented by [Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/CoreUObject/EFunctionFlags).
2. LuaMod.cpp script_hook (6323+) supplies a RemoteUnrealParam around its Context
   pointer, skips non-Parm fields and the return property, then calls Lua with
   context plus input count. For this signature that is **context only**: no
   FFrame::Locals array addresses, out-param array addresses or element wrappers
   are read. UE4.27 dispatch is post-ProcessLocalScriptFunction (7250+).
3. Script-hook output handling writes RESULT_DECL only when Lua returns non-nil.
   The probe callback deliberately returns no values, including every error and
   stop path. It neither receives nor reconstructs the original CanShow bool.
4. [RemoteUnrealParam get and ObjectProperty get](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
   resolve the current context/TextBlock wrapper. Both objects are validated
   before property access; class paths are checked. Direct reflected-property
   reads use Operation::Get through
   [UObject property lookup](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/LuaType/LuaUObject.hpp).
   TextProperty Get creates a local
   [FText wrapper](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaFText.cpp)
   which is converted to a Lua string immediately. No native target is called.
5. Pinned LuaMod.cpp verifies RegisterKeyBind/IsKeyBindRegistered, explicit
   EngineTick ExecuteInGameThread registration dispatch, and the one-shot
   ExecuteInGameThreadWithDelay timeout. These are built-in control dispatchers,
   not probe-defined global discovery hooks. No polling loop or custom
   ProcessEvent/SetText interception is installed by the source.

The installed baseline must be checked again before future deployment; this is
not a fallback for an unknown host/version or a proof that all UE4SS reads are
safe. The existing native-array frame blocker remains relevant to the deferred
SetupTipMessage2 observer, not this zero-input CanShow scope.

## Diagnostics and interpretation

Every line starts `IIP_CANSHOW`; events:

| Event | Meaning |
| --- | --- |
| START | Script loaded and waiting for the diagnostic chord; no hook yet |
| REGISTERED | Exact script hook accepted; actual invocation is still unproved |
| FIRST_CALL | Callback was reached; original CanShow bool remains unknown |
| SNAPSHOT | New/changed stored fields at the current natural callback |
| STOP | User or line limit stopped observation |
| TIMEOUT | Ten-minute deadline stopped observation |
| FAILED | Missing API/function, wrong type/class, exhausted identity limit or another contract error; session is inert |

No FIRST_CALL after REGISTERED means **not observed**, not successful live
binding or proof of hidden UI. Missing fields fail closed, except a not-yet-valid
TextBlock which is explicitly unavailable. Unchanged state emits no new snapshot.
Global throttling coalesces short transitions and can favor one of several
widgets; it does not promise complete instance coverage. No callbacks can mean
no new observation, not that the widget was destroyed/hidden. Visibility is a raw
enum value; state/text are stored properties, not an effective Slate render,
component visibility, binding evaluation or screenshot assertion. This probe
does not establish actor ownership, final writer, update timing, later transient
writes, textures/device switching or Ladder_BP coverage.

## Offline checks

Run `python tools/test.py`; requires externally installed `lupa==2.8` and uses
Lua 5.4. Local ignored environment configuration may supply its existing
testLibraries directory. Seven unittest groups cover state changes, suppressed
duplicate reads/logs, missing child recovery, nil returns, UI-write traps,
game-thread access, missing/incorrect APIs/functions, failed registration/timer,
invalid objects/types, input-signature mismatch, manual/timeout stops, line and
identity budgets and diagnostic escaping. The mocks do not emulate engine binding
and are not runtime acceptance. A local source assertion check separately
confirmed CanShow's zero inputs and the actual return-skipping dispatch route.

## Installed identity and short test

Completed first session: script hook registered; 948 calls, three widgets and six
changed snapshots, no FAILED observer event. The text changed from stored `???`
to localized actions; this is not proof of a visible placeholder or complete
show/hide lifecycle. [Exact findings and evidence hash](../../../docs/VERIFIED_RUNTIME.md)
are canonical. After normal exit the enabled marker was moved into ignored
evidence outside Mods; unchanged script remains installed but inactive. No rerun
is requested merely to repeat successful binding/text reads.

User authorized installation; performed at 03:10 Moscow with the host closed.
Installed exactly the script from `4cda59f27f4719a728a88d671e04cca901e08ab8`
with the SHA256 above, plus an empty enabled.txt, in the distinct
ImmersiveInteractionPromptsCanShowProbe folder. No previous same-probe payload
existed. Pre-test log and deployment/hash manifest were preserved in ignored
storage outside Mods. All eight previous mod files and loader config remain
hash-identical. The agent did not launch/terminate the game; the subsequent
user-operated run confirmed loading and callback execution. These script bytes are frozen for this test; a
changed script must receive a separately identified test artifact/hash.

For any subsequent separately authorized installation: verify game closed without
terminating it, verify UE4SS DLL hash
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`, source commit
and script hash. Inspect the distinct `ImmersiveInteractionPromptsCanShowProbe`
loader folder; preserve any predecessor/log with hashes **outside Mods**. Copy
only this script to its Scripts/main.lua and create that folder's empty
enabled.txt using the existing baseline loader mechanism; verify installed hash.
Do not edit shared mods.txt, replace other mods or enable GUI/hot reload.

The user then performs only normal gameplay observation:

1. Launch normally, load a save, approach an available prompt, press Ctrl+Alt+F10.
2. Leave/re-enter its range or approach another available object; optionally
   open/close a normal menu. No interaction, synthetic state or settings edit is
   required. Report whether the ordinary prompt remained normal.
3. Press the same chord to stop, then exit normally. The agent snapshots/reads
   UE4SS.log locally before another launch and correlates the diagnostic markers.

If CanShow is NOT_LOADED, the attempt stops; do not add a new hook or force-load.
Rollback/disable with host closed: move this probe's enabled marker outside the
loader and remove only its verified research folder, or restore its exact
predecessor. Preserve unrelated mods/log evidence/settings/saves. There is no
in-game cleanup of game state because the probe never writes it. Prepared source
is identified by hash/commit, not a production version; VERSION is unchanged.
