# UFont Template copy: creation and storage-isolation probe

**Runtime STORAGE_CHECK_PASS; probe disabled after the closed session.**
No FFontData writes, Aphes loading, TextBlock assignment, UI changes or
rendering claim. Production stays BLOCKED. This is the first narrow check of the
candidate in [DYNAMIC_FONT_READINESS.md](../DYNAMIC_FONT_READINESS.md).

## Runtime result — 2026-10-28

Installed exact source `6c75063300c9aa84ec946f64ca108cc4d686e1e3`, SHA256 below,
matched after the user's run and normal exit. One naturally loaded donor, one
CREATE_BEGIN and one CREATED; no probe failure. Established Steam1.09/build12996889,
UE4.27 / UE4SS83330635 baseline.

| Log line / Moscow time | Observed result |
| --- | --- |
| 652 /16:31:47 | ARMED |
| 697–698 /16:32:16.995 | Template argument8 construction returned a separate transient UFont |
| 699–700 | Distinct native array headers/buffers, entry/FontData and remaining inspected struct/header storage; entry address equals its corresponding data pointer; expected shared FontFace reference |
| 701 | DONOR_UNCHANGED for the observed identity/storage/field snapshot |
| 702 | DONE result=STORAGE_CHECK_PASS, font_data_writes=0, ui_writes=0, retained_objects=0, gc_forced=false |

Representative buffer pair was `2189049476864 / 2194346407920`; FontData pair
`2189049476872 / 2194346407928`. These are one-session native identities, not
portable offsets or addresses to reuse. Passing guards also confirms Runtime
cache, one Default entry, empty fallback/subtypes and matching selected values.

Raw log SHA256 `c8c06876154954e94d507e7af1ebc683e37830ea42329564329d46a935f22453`;
ignored archive `.local/research/interaction-prompts/font-template/20261028T133327Z/`
holds the log, parsed result and saved enabled marker. After verifying host closure,
only this probe's enabled.txt was removed; source remains hash-identical. Ten
pre-existing mod files and UE4SS settings still match the installation baseline.
No claim is made that natural gameplay left all save bytes unchanged.

**This closes the Template creation/observed-storage gate.** It does not prove
all internal FString allocations independent, setters safe, texture/font render,
immediate GC or production lifecycle. No FFontData/FontFace/UI assignment was
executed in this test. The following [Aphes writer](../aphes-text/README.md) now
contains the separate setter/ownership review and source to configure only its
own copy and TextBlock. It is not installed/run; no change to this accepted probe.

## Exact source and boundary

[Scripts/main.lua](Scripts/main.lua), SHA256
`f771481709412b2bdf5bc9f54e262b1d8cd7f69db23b1e9c72b0dca7b3b9cc7d`.
Recovered a clean single worktree at `872929ce07ef19d504c14a977eb6cfe04cf17ccc`,
branch research/interaction-prompts-owner, same live remote. Shared Research main
was `d4005c5d25ceca2c41ce8539d1271cf74b425061`; current DevRules origin/main
`0f4888bb9501afa42e3b9492c5794c98bf58537f`. Project/rules/requirements/status,
Engineering, Git/Codex, runtime integration and harness rules were consulted.
No unpublished work was overwritten. Prior successful child/divider tests were
reused; their code and installed state were not changed.

Question: does installed UE4SS83330635 actually construct a distinct UFont from
an already loaded Template, with distinct storage on the single default-typeface
path? Existing UHT/native source predicts copying, but cannot inspect actual
addresses in the running game. A single key-triggered game-thread callback is
sufficient; no hook, widget, panel, timer, scanner, polling or object registry is
needed. The old visual label/divider test would not answer this question.

The only target is
`/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font`.
Missing naturally loaded donor reports NOT_LOADED and exhausts the one attempt.
No force-loading, fallback donor or retry after moving to another screen.

## Verified pinned contracts

- [LuaMod.cpp1916–2023](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp)
  parses StaticConstructObject class, outer, name, flags, internal flags, two
  booleans, **Template at argument8**. The call explicitly supplies
  `class, outer, FName(name), RF_Transient, 0, false, false, donor`.
  No positional omission, pointer arithmetic or assumed alternative overload.
- [LuaTArray.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaTArray.cpp)
  13–17 stores params.data as the remote FScriptArray pointer; 79–109 returns
  that header's address, Num/Max and GetData address as Lua integers. These are
  native storage identities, not Lua userdata identities. Get IsValid alone
  checks a non-null header, not lifetime or bounds. Indexed Get can AddZeroed;
  the probe first requires the exact expected count and only then reads index1.
- [LuaUObject.cpp748–826](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
  Operation::Get wraps `params.data` as ScriptStructWrapper.start_of_struct.
  It does not create an independent value copy for ordinary object/struct-field
  Get. GetNonTrivialLocal has a different table path and is not used here.
- [LuaUScriptStruct.cpp86–94,167–198](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUScriptStruct.cpp)
  GetStructAddress returns start_of_struct; nested field Get derives its data
  from that struct plus the reflected field's own offset. The probe never reads
  memory through the returned integer. The pinned header confirms userdata type
  UScriptStruct; inherited GetFullName identifies the reflected struct metadata.
  GetPropertyAddress instead identifies shared property metadata and must not
  be used as evidence of independent value storage.
- Installed UHT confirms Runtime enum1, Font/FontFace classes, CompositeFont →
  DefaultTypeface → Fonts → TypefaceEntry → FontData, and the recorded fields.
  The retained donor JSON has one Default entry, zero fallback Fonts and zero
  SubTypefaces. Different actual structures stop rather than being traversed.

Raw source snapshots, UHT and extracted data stay ignored/local. Native engine
copy semantics and their mirror/build limits remain in the parent report;
Template forwarding through the installed engine was the experiment's question;
the one observed run above now confirms construction/storage on this target.

## What the probe does

Ctrl+Alt+F7 queues at most one callback via the already established EngineTick
dispatch. The attempt flag is set before dispatch, preventing rapid keys from
queuing extra copies. Key collision or missing startup APIs disables it. A failed
dispatch is terminal. It never registers CanShow or modifies its return value.

1. Exact donor/class/outer checks, Runtime cache and shape checks; snapshot only
   primitive values/addresses. Num is checked before every indexed traversal;
   empty fallback/subtype arrays are never indexed. Capacity must be plausible.
2. Unique transient UFont construction with native Template. Outer is the donor's
   already resident package, an explicit verified UObject; no unverified API is
   invented to obtain the transient package. RF_Transient applies to the new
   object. No package save/dirty operation or donor flag changes are performed.
3. Reject invalid/original alias, wrong class/path/outer, absent transient flag,
   unexpected cache/typeface/shape/field values or unavailable address API.
4. Compare native CompositeFont, typeface, array-header/data, entry and FontData
   addresses. Require entry1's address to equal the data pointer before accepting
   it as a view into the actual array. Fallback value/header and subtype header
   must also be distinct. All are positive Lua integers; no offsets are guessed.
5. Compare selected field values, expecting the same immutable FontFace object
   reference and filename/hinting/loading/subface values. Equal values alone do
   not pass. Log four donor/copy address pairs and STORAGE_DISTINCT only after
   the complete checks pass.
6. Recheck donor object/storage/selected values after construction, including
   after a caught construction/inspection failure. No repair writes on mismatch.
   DONE result=STORAGE_CHECK_PASS requires this donor check too.

All UObject/array/struct wrappers remain callback-local. No roots or persistent
objects are added; no reference is assigned to UI/FontInfo. The single unreferenced
transient copy is left for normal engine GC. No manual destruction, forced GC,
immediate collection claim, delayed read or retained wrapper is used. A failure
after allocation may still leave that one transient object pending normal GC.
Lua pcall contains Lua/binding errors; it is not protection against native access
violations. The deliberate native construction is the only runtime mutation.

## Evidence limit and next gate

Distinct actual array buffers and nested struct addresses demonstrate separate
storage at this observed path, interpreted under the inspected typed native
container contracts. They do **not** prove independence of every allocation:
FontFace references intentionally remain shared, FString character-buffer storage
and private engine state are not exposed by these checks. No raw-memory read or
mutation is added to prove them. There are no populated subfonts to inspect.

Therefore the pass marker is deliberately **STORAGE_CHECK_PASS**, not
MUTATION_SAFE, font-ready, Aphes-ready or full deep-copy/GC acceptance. It closes
the observed-template-storage question; any future FFontData assignment needs its
own setter/ownership review and separate authorization. If addresses cannot be
obtained, the probe returns FAILED without attempting a mutation to infer aliasing.
The narrow next evidence would be a reviewed native reflection/ownership path,
not a guessed write or pointer-offset workaround.

## Offline verification

`python tests/test_font_template.py`: **10 test groups pass** with existing Lua5.4
test dependency. Mocks exercise the authored control flow, exact eight argument
positions, game-thread dispatch and one-attempt policy. Scenarios include:

- missing donor; invalid donor/copy class; missing class and name collision;
- wrong/empty arrays, capacity, struct type, cache or transient flag;
- native creation throw/null/original-object alias;
- unavailable/zero addresses and equal-valued aliased header/data/entry/FontData;
- donor change injected in the mock native layer, caught by the post-check;
- startup/collision/dispatch failure and repeated/rapid keys.

Read-only mock proxies reject authored field/array writes. Native Template copying,
real pointer values, UObject lifetime, GC and Aphes rendering are not mock results.
Existing visual tests are not repeated as font evidence. Document links/diff
hygiene and unchanged VERSION/old probe hashes are checked. No font payload,
DLL, SDK or tools were generated/installed; only original research source/tests.

## Completed authorized runtime procedure

### Authorized installation — historical record, 2026-10-28

Exact source commit `6c75063300c9aa84ec946f64ca108cc4d686e1e3` and SHA256 above
were installed as ImmersiveInteractionPromptsFontTemplateProbe/Scripts/main.lua,
with an empty enabled.txt. Host absence was checked before copying, before enabling
and after verification. Pinned UE4SS DLL identity matched the established baseline.
The target did not previously exist; rollback restores that absence after verifying
the two exact files and a closed host, refusing unexpected additions/changed bytes.
Rollback syntax and expected file-set guard were checked without executing removal.

Ignored evidence `.local/research/interaction-prompts/font-template/20261028T132712Z/`
contains before/deployment manifests, pretest log and rollback.py, outside loader
paths. Ten pre-existing mod files, UE4SS settings and 61 config/save files were
hash-verified unchanged. Prior CanShow/UIChild remain disabled; no PNG probe was
installed. No game was launched/terminated, source changed or hot reload performed.
Installation proof is not Template-copy/runtime acceptance.

After closed-host installation/rollback preparation, launch normally and reach a
normal game scene where the font may already be loaded. Press Ctrl+Alt+F7 once,
then exit normally. **No visible UI change is expected.** Maintainer inspects
CREATE_BEGIN → CREATED → STORAGE_ADDRESSES → STORAGE_DISTINCT → DONOR_UNCHANGED
→ DONE result=STORAGE_CHECK_PASS. NOT_LOADED is an honest terminal outcome; do
not repeat or force load automatically. A second key does nothing. No Aphes.ttf
or config file is needed for this stage. This run is now complete; the agent did
not launch the game. Do not repeat this successful storage test without a new reason.
