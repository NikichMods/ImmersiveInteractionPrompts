# Observer marshalling readiness — 2026-10-28

**Result: BLOCKED on native hook-frame provenance/lifetime for the established
Blueprint → SetupTipMessage2 call. No executable Lua observer was authored,
registered, installed or run.** The UHT declaration remains established; this
does not reopen SDK generation or require a C++ metadata reader. No crash or bad
pointer has been observed in this work: the blocking condition is missing
necessary evidence, not a demonstrated failure of UE4SS.

## Scope and recovered state

Existing independent checkout/sole registered worktree, research/interaction-prompts-owner,
HEAD `946fbf61dc40e7018f5a5c5047e9e904f16a745c`, clean and equal to fresh
origin after fetch; no local-only commits or unfamiliar work to overwrite.
Current DevRules origin/main `c9a90c0` and task-relevant contracts/evidence were
reused. All ignored UHT/research data preserved. Installed UE4SS.dll SHA256 still
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`.

Question: can the proposed exact-function hooks supply valid parameter memory,
then support bounded read-only state capture without retaining temporary
wrappers? Static UHT data answers types/order, not this lifetime question; screen
observation does not reveal write ordering. One observer would be justified if
this contract were established. The requested stop-before-registration gate
applies when it is not. No independent mechanism was substituted.

## Established source route and remaining boundary

All source links are pinned to UE4SS `83330635`.

| Boundary | Confirmed source behavior | Limit |
| --- | --- | --- |
| Loaded function / FUNC_Native | [RegisterHook](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L4200) resolves the exact loaded UFunction and classifies by function pointer/FUNC_Native. GetFunctionFlags is exposed to Lua | Actual SetupTipMessage2 classification/registration was not exercised; UHT BlueprintCallable is normalized, not a full flag mask |
| Native pre/post | LuaMod.cpp 132–233 / 321–425 obtains property addresses from TheStack.Locals(), or FindOutParamValueAddress for OutParm, and invokes GetParam pushers before calling Lua | Callee-correct Locals and its valid lifetime on this specific Blueprint native call have not been established |
| Native arrays | [push_arrayproperty](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp#L835) GetParam creates RemoteUnrealParam. Its get() calls Operation::Get, which constructs TArray over the same data address | Borrowed FScriptArray header; no owned snapshot or validity guarantee supplied by this route |
| Array elements | [TArray](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaTArray.cpp) computes data + index × inner element size and dispatches the inner property pusher | Requires valid array/header/storage; non-null TArray IsValid is not lifetime validation |
| ObjectProperty | LuaUObject.cpp 441+ get dereferences UObject** and auto-constructs the object wrapper; covers TextBlock, PanelWidget and Texture2D array elements | This happens only after the array element address must already be valid; object checks cannot repair an invalid array address |
| TextProperty | LuaUObject.cpp 1728+ get passes *FText by value into [LuaFText.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaFText.cpp); ToString then reads the local FText wrapper | Copying FText first still dereferences the borrowed element address; convert to Lua string inside the valid callback, never retain the parameter/array/element wrapper |
| EnumProperty | LuaUObject.cpp 1542+ GetParam creates RemoteUnrealParam; get reads the underlying property with size/signedness handling and returns an integer | The underlying value address must be valid. ByteProperty's exact applicable binding/route was not separately certified after the earlier native-frame stop condition was reached |
| Blueprint proxy / CanShow | LuaMod.cpp script_hook skips ReturnValue and is dispatched at the UE4.27 post boundary; proxy's const-ref arrays use out-parameter address resolution | CanShow supplies context, not its original bool as a callback argument; returning non-nil can overwrite host result. No synthetic CanShow call or parent-hook substitution |
| Deferred readback | ExecuteInGameThread queues one-shot work; ExecuteInGameThreadWithDelay uses steady-clock deadlines and game-thread dispatch, with engine-dispatch fallback in this revision | No parameter wrapper may escape its callback. Delayed UI reads would require fresh object/identity validation and bounded scheduling; no such schedule was created or tested |

The five non-out value inputs are known from [UHT_SIGNATURE.md](UHT_SIGNATURE.md).
Thus the applicable native branch is **ContainerPtrToValuePtr(TheStack.Locals())**,
not the out/reference address branch used by the Blueprint proxy. This is why
existence of ArrayProperty/TextProperty handlers is insufficient evidence.

## Exact missing dependency evidence

The [Unreal gitlink](https://github.com/UE4SS-RE/RE-UE4SS/tree/83330635/deps/first/Unreal)
pins native dependency `Re-UE4SS/UEPseudo` to
`fbb4fdd3fffc59d5b5268b23a643f500f702115e`. This contains the lower native
UFunction hook layer used by RegisterPreHook/RegisterPostHook.

To close the route, establish from that exact implementation (or already accepted
exact-boundary evidence) how the hook presents FFrame/Locals for a native function
called via Blueprint EX_FinalFunction, and whether the callee array parameters
remain valid during pre and post callbacks. The retained Blueprint call at 713 is
that relevant path; successful neighboring hooks with different argument shapes
do not establish it.

Access checks: GitHub connector returned 404 for the gitlink's dependency source
and the alternate organization spelling; ordinary authenticated Git ls-remote
against the declared submodule URL returned `Repository not found`. Raw-source
retrieval also did not yield the pinned file. A bounded lookup in retained local
research/tool inputs found no dependency implementation. These results establish
unavailability through the checked routes, not why access is unavailable or that
the upstream repository/commit no longer exists. No newer/unpinned fork was used.

### Web access follow-up

The [official UE4SS build instructions](https://docs.ue4ss.com/#build-instructions)
explicitly require GitHub linked to Epic Games for access to the Unreal pseudo
code submodule. [Epic's access guide](https://www.unrealengine.com/en-US/ue-on-github)
describes linking the accounts and accepting the GitHub organization invitation.
This establishes a documented access prerequisite, not whether the user's account
already meets it or whether the current tool credentials can access the source.
There is no verified relocation to another official source URL.

Public repository/commit search found ashandarei/uepseudo-goa (a GoA/KH3 fork),
but querying the exact required commit returned “No commit found for the ref”.
The other named candidate, deadkiller13113/https-github.com-Re-UE4SS-UEPseudo,
is empty. Neither supplies the pinned dependency; no replacement version was used.

The locally preserved release metadata and matching ZIP SHA256 confirm the
installed loader package was UE4SS_v3.0.1-1181-g83330635.zip from the official
GitHub release, archive SHA256
`b9a166a756605b21058a64cde93bcaab1a855dba3553e5c7e6ce0fa8fdfad7b9`.
That binary archive contains no C++ source. UEPseudo is a source dependency of
UE4SS, not a separate Nexus gameplay mod; redownloading the loader binary does
not provide this missing implementation. The next useful action is authorized
access to the original dependency at the pinned commit, not a loader update.

LuaMod itself reads the parameter addresses and constructs wrappers before the
Lua callback; the later get()/TArray element read then dereferences them. A Lua
pcall, a registered type handler, UHT type correctness, or a context-only callback
does not prove this earlier memory contract. No probe is handed over to discover
a bad native address by crashing the host. Omitting the main consumer or replacing
it with global SetText/ProcessEvent hooks would not answer the requested question.

## Additional concrete array-read constraints

Pinned TArray::prepare_to_handle calls AddZeroed when the index is beyond Num,
**including Operation::Get**. Therefore array indexing is not unconditionally
read-only. A future observer must read/check the count and enforce bounded
in-range integer indexes within the same valid callback; no ipairs or read-until-nil
on TArray userdata. Copying a Lua wrapper does not copy its underlying storage.

ForEach also uses borrowed element addresses and contains an unresolved source
comment about stack corruption/crashes with large arrays. That comment is not
proof of a failure for our small arrays, and it is not the blocking condition
above. Guarded indexed reads are a possible future alternative, once valid frame
memory is established; they do not by themselves close the earlier boundary.

## Offline checks, identity and next step

Local source-route assertion check verified the native address selection,
RemoteUnrealParam get route, borrowed TArray construction, read-side AddZeroed
branch, FText copy wrapper, Blueprint post dispatch and unchanged UHT header hash.
Result: BLOCKED_NATIVE_FRAME_PROVENANCE. It corroborates manual source review;
it does not execute/validate the native hook layer. tools/test.py completed and
reported no automated runtime test suite. No synthetic Lua mocks can prove the
missing native address/lifetime contract, so none are presented as that evidence.

| Pinned source snapshot (UTF-8/LF) | SHA256 |
| --- | --- |
| LuaMod.cpp | ecc9448999fdac16d4b9181d73f99aafeb8f75dd12ad921e3f7f7922d8298227 |
| LuaUObject.cpp | 9dd81472765d66596b31fc12100d1098fbd84e5311226b4d1decc397a13e9b17 |
| LuaTArray.cpp | c5c4be252fc9a026152a70d0964d5a7dc4889b68f609e37baa8eab216d80bbac |
| LuaFText.cpp | 05543331fe333fb03bb48fd1807c5e15ec19d6f940016cff3d2aa284bb5c703c |

Snapshots/check output remain ignored under .local/research/interaction-prompts;
no proprietary SDK or raw game log is published. There is no runtime source/hash,
START/REGISTERED/FIRST_CALL/READBACK/STOP/FAILED implementation or installable
payload. Existing proposed ceilings remain unchanged: 10 minutes, 600 lines,
8 widget identities, readback at most 4/s for at most 2 seconds per relevant
update. These are still requirements, not verified executable controls.

The smallest next step is offline access to the pinned native hook implementation
or accepted evidence for this exact Blueprint native-array boundary. Review that
first, then implement/test one observer if it establishes the contract. Repeating
UHT generation cannot supply this missing evidence. No installation or game run
is needed/requested now; there is nothing to enable or roll back. When an observer
can be prepared, its future deployment requires separate authorization, a closed
host, frozen source/hash, verified predecessor backup outside loader paths and
explicit same-probe-only rollback. No global hooks or target invocation.

Widget/component/actor association, actual displayed/localized text and textures,
visibility/input/later writes and the separate Ladder_BP path remain unobserved.
Production gate remains BLOCKED. Production/VERSION/main, installed mods,
settings/saves and game processes were not changed in this stage.
