# Stock-font TipHUD child experiment — source preparation only

**READY for one separately authorized research runtime test of an added label.**
Not installed, not run, not accepted UI. Production remains BLOCKED. The divider
is deliberately omitted: no checked texture-free solid-brush construction or
existing narrow brush resource was established in this step. Aphes/cooker work
is deferred; neither is required for the label-only experiment.

Source: [Scripts/main.lua](Scripts/main.lua), SHA256
`25ba56ca3de419fd187ee4ab29dfb88bc5ffa0c8a68cf19e2a9b7b72ac330f2d`.
Target: Steam 1.09/build12996889, UE4.27, UE4SS `83330635`.
Recovered clean project source/remote was `52f519ec850ef05f5e1b7d623eef8a46a9e8ac26`;
one worktree, same research branch, current rules/deltas read. Existing findings
from [visual readiness](../VISUAL_READINESS.md) and
[font checkpoint](../FONT_RESOURCE_READINESS.md) are reused, not repeated.

## Question, mechanism and evidence

Can a new primitive TextBlock attach as a sibling to the original localized
TextBlock in one existing TipHUD, display a temporary OPEN with copied stock
font settings, and detach cleanly? This tests creation/attachment/layout only;
OPEN is not an Aphes translation or accepted visual design.

| Boundary | Evidence / implementation |
| --- | --- |
| Native UObject construction | Pinned LuaMod.cpp 1916–2023 implements StaticConstructObject(UClass, Outer, FName, flags, ...). Uses the engine construction path, not raw allocation or field-offset fabrication |
| Primitive widget and owner | Exact loaded `/Script/UMG.TextBlock` UClass; Outer is selected TipHUD.WidgetTree, RF_Transient, unique checked name. No UUserWidget, Blueprint class duplication or guessed Initialize/Construct calls |
| Parent/slot | Installed-build UHT: CanvasPanel.AddChildToCanvas returns CanvasPanelSlot; PanelWidget.RemoveChild returns bool; slot Parent/Content and getters are reflected. Existing seven-edge export identifies TextBlock_89 → CanvasPanel_6 |
| Stock font | LuaUObject.cpp 754–830 supports same-type ScriptStructWrapper CopyCompleteValue. `SetFont(b.Font)` is synchronous and uses the existing complete typed value, not a made-up filename or partial font table. Original Text/Font/Slot untouched |
| Text / geometry | Pinned LuaFText.cpp supplies FText(string); UHT declares SetText, SetFont, SetJustification and slot setters. New label only: fixed 140×28, `(88,-18)`, anchors `(0,0.5)`, alignment `(0,1)`, no autosize |
| GC references | Reflected PanelWidget.Slots → PanelSlot.Content supplies the attached object-reference chain. Lua variables and Outer alone are not claimed to root objects. No AddToRoot/forced GC/destruction |
| Detachment | Only the exact created child can be passed to RemoveChild; never ClearChildren, RemoveChildAt, source reparenting or native-array writes. Recheck GetParent after removal |

Primary engine contracts:
[UE4.27 UObject construction/reference handling](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-object-handling?application_version=4.27),
[Panel AddChild](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/UMG/Components/UPanelWidget/AddChild?application_version=4.27),
[lazy Slate TakeWidget](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/UMG/Components/UWidget/TakeWidget?application_version=4.27).
The native constructor/UMG attachment API handles primitive widget construction;
the actual successful Slate realization is precisely what the first runtime
experiment must establish. No equivalence to the complete C++
[WidgetTree ConstructWidget template](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/UMG/Blueprint/UWidgetTree/ConstructWidget?application_version=4.27)
is asserted, and no unreflected template or TakeWidget is called through Lua.
UHT `.cpp` stubs are not used as native implementation evidence.

Pinned source:
[LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp),
[LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp),
[LuaUObject.hpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/include/LuaType/LuaUObject.hpp).
Local snapshot hashes for cpp files are in VISUAL_READINESS; hpp SHA256
`1b011de1b90390abd02c9f11ebf9da7eb7b55b7d8b2c3f7040f749bd4649e157`.
hpp 761–775 checks the global object map and IsUnreachable; cpp 25–92 implements
map/deletion-listener handling. This is not a serial-number weak handle or a
strong GC reference. All persisted identities are path/address/class strings
and numbers; cleanup reacquires exact objects through StaticFindObject, then
checks identity/outer/parent. Stale stored wrappers are never dereferenced.

## Bounds and failure behavior

- Initially armed; no engine object touched until explicit control. One chord
  Ctrl+Alt+F9 schedules game-thread control. First press registers the already
  verified non-native zero-input Blueprint CanShow post seam, always returning
  nil. No SetupTipMessage/native/global hook or object scan.
- A 30-second overall window selects only the first naturally visible, enabled
  TipHUD with current «Открыть». It requires the exact text class, WidgetTree /
  CanvasPanel_6 ownership, three original canvas children, original slot/anchors/
  position and desktop Font.Size=22. Any structural mismatch stops before UI
  creation; nonmatching actions are simply skipped. Handheld/other layouts are
  outside this first test, not silently resized into the baseline.
- A reentrancy guard plus attaching/attached phases prevents duplicate creation.
  New child is collapsed before attachment/configuration, then HitTestInvisible;
  no new input target or root visibility/opacity override.
- CREATE_BEGIN/CREATED, ATTACH_BEGIN/SLOT_READY and REMOVE_BEGIN/REMOVED bracket
  the new engine operations, so an incomplete log localizes a stall/failure.
- Same chord stops; one nonrecurring game-thread timer also cleans up, even if
  CanShow never runs again. A changed action/visibility state observed on the
  selected widget ends the experiment. Other widgets never receive children.
- Cleanup collapses our child, checks its actual parent, removes only it and
  verifies detachment. A gone/unreachable child needs no removal. CLEANED means
  detached or not found/reachable, not immediate object deallocation. Detached
  transient objects may remain until engine GC; no UObject destruction forced.
- CLEANUP_FAILED retains only identity metadata and leaves the hook inert;
  another explicit chord retries cleanup. Failure, identity collision, external
  reparenting or game-thread dispatch failure is reported, never claimed as a
  successful rollback. No code can guarantee a successful engine call when the
  engine/API has failed; normal cleanup and partial-attachment failures are
  tested offline. Runtime verification of this boundary remains mandatory.

No UObject, font/slot wrapper or native parameter survives a synchronous call.
No helper mod/import, custom font, external asset, save/config change or release.
Registered callback stays inert after stopping; no unregister/reload dependency.

## What remains experimental

Adding a child can change CanvasPanel_6 desired size and shift centered parents
even though no existing property is assigned. Fixed new size limits this input;
it does NOT prove zero reflow/clipping. Native layout/individual visibility and
full menu/target lifecycle remain unknown. Actual font inheritance, rendering,
GC survival while attached, detachment in the game and restored layout require
runtime evidence. This is enough for a bounded research experiment, not a
production readiness claim or a guarantee against every engine failure.

Offline `tools/test.py`: seven existing CanShow groups and twelve new Lua54 mock
groups pass. New checks cover no allocation before eligibility, repeated callbacks,
manual/timer/state-change cleanup, partial attachment failures, missing/layout
contracts, cleanup failure/retry, destroyed-owner lookup, hidden/disabled states,
external reparenting and identity reuse. They test authored
policy, not native initialization, rendering, GC or engine method bodies.

## Future test — not authorized for installation in this stage

After separate installation permission, freeze exact source/hash, verify closed
host and preserve prior same-probe payload/log outside loader paths. Install only
this distinct research folder; leave the previous CanShow probe disabled. Check
installed hash. No current installation was performed.

In a separately permitted session, approach a normal «Открыть» prompt, press
Ctrl+Alt+F9 once, observe OPEN/original action/icon and any shift/clipping, then
press again to remove it. Confirm layout returns; let a second separately
authorized run test timeout only if the first result leaves that question open.
Preserve ATTACHED/CLEANED or actual failure log and user visual observations.
Do not repeat the old read-only CanShow test or infer visual acceptance from logs.
