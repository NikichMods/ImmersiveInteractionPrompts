# Independent UserWidget host — bounded source review, 2026-10-29

**FOUND / SOURCE_READY for a separate bounded host-lifecycle experiment.**
The missing concrete host class is resolved statically. Runtime residency,
Create/WidgetTree/first Slate construction/cleanup are NOT_TESTED. Full World Open
prototype remains BLOCKED on its separate exact actor/component/pose binding and
its runtime gates. No executable game payload, install, game launch, production,
VERSION, settings/save or other-mod changes in this study.

Candidate (retain shipped spelling):
`/Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C`.

## Recovery and bounded selection

Clean single research worktree at21d3fd994002bbcd78293a8833f87c432a73e1b2; fresh
origin matched. Research main2f0936d... fast-forwarded cleanly to published
eebb9b6... without dropping its current-PC key-resolver addition. DevRules remote
0f4888bb9501afa42e3b9492c5794c98bf58537f unchanged; owning rules reused.
Existing font/material/World-component studies were not repeated.

Only the retained Template/UMG path index was used for selection (56 entries,
including non-widget resources; no new global inventory). Four exact packages
were read from installed base Paks with the existing CUE4Parse1.2.2 reader:

| Candidate | Real base / result |
| --- | --- |
| WaterMarkUMG_BP | Genesis.WaterMarkUMG, requires native tick; small tree is not evidence that its game native base is inert; not selected |
| HelloPlayerUMG_BP | Genesis.HelloPlayerUMG, native tick and animations; not selected |
| ScreenPostionUMG_BP | Direct UMG.UserWidget, but six nested PostionItem widgets; led to the simpler child candidate |
| **PostionItemUMG_BP** | **Direct UMG.UserWidget, no game native base, no nested UserWidgets; selected and search stopped** |

This is a result for one shipped class, not a universal claim about other UI.
Raw packages/exports/bytecode remain local/ignored under
`.local/research/interaction-prompts/userwidget-host/`; no proprietary class asset
is copied into public Git or redistributed.

## Actual inheritance, class flags and complete behavior surface

Chain: PostionItemUMG_BP_C → UMG.UserWidget → UMG.Widget → UMG.Visual →
CoreUObject.Object, verified against export SuperStruct and actual UHT parents.
Candidate generated ClassFlags lacks Abstract/Deprecated/NewerVersionExists;
abstract base UUserWidget does not make this concrete Blueprint abstract.
There are exactly14 exports, including four function exports:

| Function | Executable evidence / effect |
| --- | --- |
| Construct | calls ubergraph entry36→10: SetVisibility(2=Hidden) on **self**, then26→41 return |
| PreConstruct | stores IsDesignTime in its own persistent frame, entry31→41 return; no visible/global action |
| ExecuteUbergraph | computed entry switch with only the self-visibility call/jumps/return above |
| SetText helper | int→string conversion/concatenation, string→FText, Value_Text.SetText, self SetVisibility(3=HitTestInvisible); not a constructor/tick callback and not needed by the host recipe |

Candidate CDO explicitly has bHasScriptImplementedTick=false and Paint=false.
Generated-class bClassRequiresNativeTick is absent with actual reflected UMG
WidgetBlueprintGeneratedClass CDO default false. No Blueprint Tick/OnInitialized/
Destruct override, animations, property bindings or dynamic-binding objects are
present; no custom Genesis native callbacks are inherited. Standard engine UMG
bookkeeping/cache activity is still possible; this is not a claim of zero engine
side effects. Enumerating **all** callable bytecode symbols, including EX_CallMath,
finds only own ubergraph/SetVisibility/SetText and Kismet string/text conversions.
No actor/game-mode/controller/input/save/file/network/event-registration operations
occur in those graphs. Constructor self-Hidden is a real behavior, not ignored.

WidgetTree:
CanvasPanel_0 → Main_Panel → {Bg_Image, Value_Text}. Three slot edges were checked
with reciprocal Parent/Content/child.Slot export indices. All four widgets are
native UMG primitives; no nested game UserWidget initialization is hidden here.
Bg_Image/Value_Text are reflected instanced references. Main_Panel/root names do
not automatically establish direct Lua widget aliases: use WidgetTree.RootWidget
and verified child/parent relationships for future inspection.

## Independent creation, WidgetTree and Slate contract

Use the **normal** reflected WidgetBlueprintLibrary.Create(WorldContextObject,
WidgetType, OwningPlayer), not direct StaticConstructObject(UserWidget), Template
cloning of a live TipHUD, CDO mutation or bypass of Initialize/abstract validation.
Pinned UE4SS LuaUObject.cpp480–510 accepts UClass/nil for a class property, and
its previously reviewed UFunction calling contract requires the explicit library
CDO before reflected parameters. This is source confirmation, not an executed
Lua Create call for this candidate.

UE4.27 CreateInstanceInternal creates a new UserWidget with RF_Transactional,
sets player context when available, calls Initialize and returns it. Do not label
this returned host RF_Transient merely because its lifetime is intended temporary.
Generated-class InitializeWidgetStatic uses the instance tree or invokes
DuplicateAndInitializeFromWidgetTree; the latter creates a tree owned by the new
UserWidget using an FObjectInstancingGraph and marks it Transient/DuplicateTransient.
Instanced child references are rebound to this cloned tree. No reparent/write to
original TipHUD or another UI's WidgetTree is required.

UWidget.TakeWidget_Private keeps MyWidget/MyGCWidget per object; a new Create
instance does not reuse the live TipHUD's Slate cache. UUserWidget.RebuildWidget
uses its own RootWidget; OnWidgetRebuilt invokes PreConstruct then Construct.
Thus the first build **hides this host**, even if visibility was set before it.
A future probe must complete its first bind/build, then set/check only the owned
host's visibility. If rebuilt later, Hidden can recur; do not silently reassert it
per frame or claim a finished lifecycle. World registration/renderer construction
remains a separate contract in the World report.

A contained composition recipe can keep the private root, collapse only its
private Main_Panel placeholder and add own siblings under CanvasPanel_0. It need
not replace RootWidget or call the host SetText helper. Before writing, runtime
must verify fresh host address, tree outer==host, root/leaf outer==private tree,
reciprocal edges and no identity matches to original UI/archetypes. Native Font/
Brush resource references may intentionally share stock assets read-only; tree/
widget identity must not be shared. A Lua wrapper/Outer alone is not a GC root.
An owned component.Widget or viewport Slate holder must supply native ownership;
cleanup must release only that holder and own resources, with no forced GC claim.

## Availability gate and proposed separate test boundary

Cooked presence is proved, **loaded-class residency is not**. Exact StaticFindObject
may return NOT_LOADED. Pinned UE4SS LuaMod.cpp3334ff does expose game-thread-only
LoadAsset(path), returning object/was_found/did_load through AssetRegistry.
The follow-up targeted registry check now confirms a separate exact `_C` entry
(WidgetBlueprintGeneratedClass, direct UMG.UserWidget), not only a guessed
Blueprint path. Registry SHA256 and the bounded loading policy are recorded in
the [host-only probe](probe/README.md). One exact LoadAsset attempt is prepared;
no loader call has been executed. Missing/wrong class or parent stops the probe.

The source evidence is sufficient to design a small **host-only** lifecycle test:
check the exact class/Create API; create one independent host; validate tree/identity
before writes; establish one native owner/first Slate build; observe expected self
Hidden, make only the own host visible and verify a local label; remove only own
content/owner. Compare original UI state and record the result. No natural Open
actor or World-space positioning is needed to answer that question. Actual Lua
Create marshaling, class availability, ownership across callbacks and teardown
remain runtime gates. The requested [Lua prototype](probe/Scripts/main.lua) is now
READY_SOURCE with offline policy tests, not an observation of those native facts.
It uses one owned viewport host and a plain label; no World component or TipHUD
mutation. See [procedure, checks and cleanup limits](probe/README.md).

No editor/cooker/C++ class project is needed **if this shipped candidate is usable
at runtime**. Authoring an empty Blueprint/cooked asset or native UserWidget subclass
remains an explicit fallback with new build/maintenance dependencies, not an
automatic next step. Reusing the live TipHUD or CanvasPanel as a UserWidget is still
invalid. The next independent World blocker is unchanged: exact natural Open
actor/component/pose binding; this investigation did not try to solve it.

## Offline verification and provenance

Asserted concrete/parent flags, complete function set and callable-symbol whitelist,
Construct/PreConstruct entry paths, Tick/Paint defaults, no nested UserWidgets or
bindings/animations, and three reciprocal slot edges. Reviewed native Create,
InitializeWidgetStatic/instancing and per-object Slate cache paths. No mocked
native render/GC success or new game execution is claimed. Production source is
unchanged; public Git contains authored research source/tests/findings only.

Source mirror revision306a7e9f7fb53f14c2cb3bfd3854ad906710a17e:
[UserWidget.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/UserWidget.cpp),
[WidgetBlueprintGeneratedClass.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/WidgetBlueprintGeneratedClass.cpp),
[Widget.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/Widget.cpp).
These are engine-version source evidence, not new game-binary execution.
The local audit/source manifest records exact inputs and source hash.

| Local candidate export | SHA256 |
| --- | --- |
| PostionItemUMG_BP--Construct.bytecode.json | d8fd1f391d9cd86eead6ed2e8cda101805a1627cc1626a6dd2dd7bf348c3d682 |
| PostionItemUMG_BP--ExecuteUbergraph_PostionItemUMG_BP.bytecode.json | f03baab2734d97441166dc107bb5e7418ef5c7410cb03ac54491c262c2bbe683 |
| PostionItemUMG_BP--PreConstruct.bytecode.json | 60781172ee0ee173490347c51bbc6f1686a438212f01691459c73ad9fa61e683 |
| PostionItemUMG_BP--SetText.bytecode.json | e4ea6fb537137ba74e4e9de45dcafaf881a167260037910ffde96fbd418bb15a |
| PostionItemUMG_BP.json | cac88b3e55127ad3afe5d9d976ed65371afabca9e61586311612aa5db192441f |
