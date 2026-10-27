# Reflection-only capture readiness — 2026-10-28

**Result: partial read-only API confirmed; complete Lua capture BLOCKED by missing
FProperty flag access in UE4SS `83330635`. No runtime Lua payload was authored,
installed or executed.** The missing native signature is still missing. This
replaces the previous report's proposed Lua metadata capture as the immediate next
step: source inspection now shows why that proposal cannot meet the full contract.

## Recovery and existing-data check

Continued the clean, sole registered checkout on
`research/interaction-prompts-owner`, HEAD
`afb5b4500b460734d6f76542926ffb8593d42231`, equal to a freshly fetched remote head;
no local-only commits or staged/unstaged/untracked work. Ignored evidence preserved.
No branch switching or rewriting. Current DevRules `origin/main=c9a90c0` and its
applicable local rules/differences were read; shared Research R-008 already covers
callback marshalling, not FProperty flags. Installed DLL hash remains
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`.

Reused the prior exact-identifier lookup and retained exports rather than repeating
the game inventory. No new native SDK/reflection declaration has appeared among
this workstream's retained inputs. TipHUD.json contains proxy and CanShow
definitions; SetupTipMessage2 is a native import/call, not a declaration. The
previous prerequisite check still passes. No offline exact signature was found.

## Version-pinned mechanism review

All links below refer to the installed revision, not current documentation.

| Requirement | Source-confirmed contract | Result |
| --- | --- | --- |
| Exact loaded lookup | [LuaMod.cpp, StaticFindObject](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L1245): delegates to UObjectGlobals::StaticFindObject; does not call LoadAsset/LoadExport. [auto_construct_object](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp#L373) constructs a UFunction wrapper for a found function | Suitable lookup; actual three objects remain unobserved |
| Full name/type/function flags | UObject GetFullName/GetClass, [UFunction::GetFunctionFlags](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUFunction.cpp) | Readers exist; no actual Genesis values captured |
| Property enumeration | [UStruct::ForEachProperty](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUStruct.cpp#L96) iterates TFieldRange with IncludeDeprecated, wraps FProperty, calls Lua with one property; true stops iteration | Property traversal order can be recorded, but this enumerates properties, not a filtered parameter signature |
| Property name/type/offset | [XProperty](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaXProperty.cpp) exposes GetFullName, GetFName, GetClass, GetOffset_Internal; field class exposes GetFName | Metadata readers exist; offset is not a substitute for flags or ABI order |
| Array element types | [auto_construct_property](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaXProperty.cpp#L18) chooses XArrayProperty; [GetInner](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaXArrayProperty.cpp) returns another typed property; object/enum wrappers expose GetPropertyClass/GetEnum | Source-level route exists; bound recursion would be needed for a future capture |
| Parm/OutParm/ReferenceParm/ReturnParm | XProperty has no property-flag getter or predicate; its actual base hierarchy also lacks one (below) | **BLOCKER**: cannot distinguish parameters from locals or determine calling semantics |
| One-shot dispatch | LuaMod.cpp ExecuteInGameThread (4325+) queues one SimpleLuaAction; process_simple_actions (3793+) moves/clears the queue, runs the callback and unrefs it; scheduling checks the selected engine hook's availability | Source-level one-shot scheduling exists, no polling/requeue needed. Not tested in game; underlying UE4SS EngineTick/ProcessEvent dispatch uses a shared hook, not a hook on a target function |

For each of the same three target paths in [README.md](README.md), a future lookup
could report FOUND/NOT_LOADED at one instant. Neither state was measured here.
NOT_LOADED must remain a legitimate result without force-loading or retries.
The scheduling API alone does not establish when TipHUD is naturally loaded.

## Exact blocker: FProperty is not UObject

[LuaXProperty.hpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/LuaType/LuaXProperty.hpp)
defines XProperty::Super as RemoteObjectBase<FProperty,...>. Its binding methods
are exactly GetClass, GetFullName, GetFName, GetOffset_Internal, IsA,
ContainerPtrToValuePtr, ImportText and type. The last two are not metadata-flag
readers and are not proposed for use.

[ObjectBase/RemoteObjectBase](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/LuaType/LuaUObject.hpp)
adds address/validity/type support; the underlying
[LuaMadeSimple RemoteObject](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/deps/first/LuaMadeSimple/include/LuaMadeSimple/LuaObject.hpp#L103)
adds GetAddress, IsValid and IsValidField. It does not automatically expose C++
members. UObject's HasAnyFlags/HasAllFlags are object flags on a different wrapper,
not EPropertyFlags, and cannot be substituted.

LuaMod's internal C++ code uses FProperty::HasAnyPropertyFlags when marshalling;
that proves native access exists, **not** that Lua can call it. UFunction flags
also do not encode each parameter's flags. Sorting by offset, assuming every
property is a parameter, or borrowing proxy flags for SetupTipMessage2 would
guess the very contract the capture must establish. The retained CanShow export,
with one return parameter and four locals, is a concrete counterexample to
equating properties with parameters.

Built-in DumpAllObjects, GenerateSDK, GenerateLuaTypes and header/JMAP/USMAP
generators expose broad generation entry points, not a three-function filter in
their inspected Lua bindings. They are not a substitute within this task's ban on
global scans. Raw memory offsets/custom fake properties or a UE4SS upgrade would
introduce another unproved mechanism/version and were not attempted.

## Offline verification and limits

Original [audit_metadata_api.py](audit_metadata_api.py) is an **offline Python source
audit, not a Lua mod or capture payload**. It reads supplied upstream snapshots,
checks eight normalized UTF-8/LF SHA256 identities, verifies the relevant bindings,
inheritance route and one-shot queue source markers, then emits a compact summary.
It does not connect to processes, inspect memory, call host APIs or use a network.
Its checks corroborate the manual source review; string checks are not a C++
execution test or proof of all native safety properties.

Run with Python 3: `python research/interaction-prompts-owner/audit_metadata_api.py <snapshot-directory>`.
Snapshots use `ue4ss-83330635-<source-basename>`; exact repository paths are linked
above, and expected hashes are in the audit source. Upstream/game snapshots and
raw check output remain ignored under `.local/research/interaction-prompts/`.

Executed the audit and the previous check-probe-prerequisites.py successfully;
tools/test.py completed and reports no automated runtime test suite. git diff
checks passed. No engine binding, object availability, property order/values,
metadata callback execution, rendering or acceptance was tested.

## Next decision; no payload to install

The immediate useful step is **not** to install a partial Lua capture: it cannot
supply the missing flags even if all three functions are found. My recommendation
is a separately scoped, typed C++ metadata reader against the exact UE4SS API,
restricted to these three functions, with direct FProperty flag reads and no
target invocation/hooks. Source/API, toolchain and ABI compatibility must be
reviewed before producing such a payload. This report does not authorize that
implementation or establish its safety. An already available trustworthy exact
native declaration remains the simpler alternative if supplied.

Only after a complete reader exists should installation be separately authorized:
verify host closed, preserve same-probe predecessor/log outside loader paths,
freeze and hash the payload, install only its distinct research folder, and
verify installed hashes. User launches normally; one-shot capture records missing
objects rather than loading them. Disable/remove only that probe with host closed;
no hot reload. There is no current script to enable/disable and no runtime action
requested now. Production, VERSION, stable mod branch, other mods, game files,
saves/settings and running processes were not changed. Final writer and production
evidence gate remain **BLOCKED**.

The reusable source-level binding limit is also recorded as R-009 in
`NikichMods/Asterigos-Research`, branch `codex/ue4ss-metadata-api`. It is kept off
main under this task's no-main-change constraint; canonical-main integration is
pending and is not implied by publishing the research branch.
