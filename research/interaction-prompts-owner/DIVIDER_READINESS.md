# Resource-free divider in native TipHUD — 2026-10-28

**Installed with explicit permission; first visual divider test pending.**
No runtime result yet for this revision. Actual line rendering is unverified. Production
BLOCKED; Aphes/cooker, native observer and general lifecycle are out of scope.

Recovered clean single-worktree checkout on `research/interaction-prompts-owner`,
HEAD/live remote `a89ab33358df4e905f97942dc7deb64d59b5f16a`. DevRules remote
`c9a90c04336072e821761e376d1702d63899c4ab`, applicable current rules/deltas read.
The successful one-label run and Research R-006 are reused; no repeat runtime
observation was performed. Installed label-only source stays hash-identical and
disabled. No game/settings/save/mod/tool installation or hot reload.

## Question and smallest mechanism

Can a resource-free color box on a new UImage draw a thin divider immediately
below the already-proven OPEN label, then detach with it? The accepted label
baseline proves UWidget construction/attachment and manual removal, not Image
brush rendering. A focused future visual test is needed for that remaining fact.

| Option | Assessment |
| --- | --- |
| **UImage + color-only FSlateBrush Box** | Chosen: one extra primitive/slot, no children, texture/material/font resource or paint override; explicit brush configuration |
| UBorder | Same brush question plus content/padding/container behavior. Default background could depend on a style/resource. No benefit for an empty thin rectangle |
| DrawLine / text glyphs | DrawLine needs a verified PaintContext/paint path rather than persistent Canvas child; dash/underline glyphs depend on font metrics/shaping. More assumptions for this goal |

Epic's [4.27 FSlateColorBrush contract](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/SlateCore/Brushes/FSlateColorBrush?application_version=4.27)
describes a box with zero margins and color only. This establishes the intended
Slate rendering mode beyond merely finding SetBrush. It does **not** make the
C++ FSlateColorBrush constructor callable from Lua or prove pixels in Asterigos.
The prototype configures a native-initialized owned FSlateBrush to that color-box
shape through reflected fields, and uses UImage.SetBrush for the update. It does
not invent a Lua FSlateColorBrush factory or initialize raw struct memory.

## Installed-version API, enums and defaults

Existing UHT dump from UE4.27 / UE4SS `83330635` supplies:

- UImage.Brush: FSlateBrush; SetBrush(const FSlateBrush&),
  SetColorAndOpacity(FLinearColor). UBorder.Background and its SetBrush/SetBrushColor
  exist too, but are not used. SetBrushResourceObject is unnecessary because the
  selected new Image must already be resource-free; unexpected resources fail.
- FSlateBrush reflected ImageSize, Margin, TintColor, ResourceObject,
  ResourceName, DrawAs, ImageType, Tiling, Mirroring, bIsDynamicallyLoaded,
  bHasUObject. No raw offsets or hidden cache/handle fields are written.
- ESlateBrushDrawType: NoDrawType=0, Box=1, Border=2, Image=3.
  ESlateBrushImageType.NoImage=0; NoTile/NoMirror=0.
  ESlateColorStylingMode.UseColor_Specified=0; FSlateColor.SpecifiedColor and
  ColorUseRule are reflected. FLinearColor has explicit R/G/B/A.

[LuaUScriptStruct.cpp at 83330635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUScriptStruct.cpp)
63–65 routes __newindex to Operation::Set; 163–230 resolves reflected properties
and invokes their type pushers. Pinned LuaUObject.cpp 572–652 / 754–830 supports
nested struct fields and same-type typed struct CopyCompleteValue. These are the
contracts used for configuring the owned brush and passing it to SetBrush.
LuaUObject.cpp 229–232 excludes ConstParm from the OutParm table/writeback path,
consistent with the reflected const-reference SetBrush input. No native hook
frame or borrowed array parameter is involved. Pinned LuaFName.cpp 119–125
confirms ToString used for the ResourceName default check.
The source copy was retained locally, SHA256
`d7896437d23331d799a1cdce0225df7cd03cc02e3052693c6d646e0a4d09d277`.

**Defaults are not asserted from generated stub constructors.** Actual UImage
defaults on the live installation have not been observed. The future prototype
logs BRUSH_DEFAULT (DrawAs, resource presence/name, dynamic/object flags), then
requires ResourceObject absent, ResourceName=None and both resource flags false.
Unknown/missing fields or any unexpected resource fail before the divider is
attached and trigger cleanup of both owned objects. It does not clear/replace a
shared texture or brush. Native construction preserves unreflected brush state;
there is no assumption that a zero-filled Lua table is a valid FSlateBrush.

Explicit configuration before attachment: DrawAs=Box, ImageType=NoImage,
NoTile/NoMirror, ImageSize=(140,2), all four margins zero; specified white tint
and white UImage ColorAndOpacity, alpha=1. Then SetBrush receives the **complete
typed owned brush**. Readback checks enums, size/margins, absent resource,
specified white tint and image RGBA. BRUSH_READY proves these checks passed,
**not** visible rendering. ResourceHandle/bIsSet/renderer caches are not patched.

The [FSlateBrush reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/SlateCore/Styling/FSlateBrush?application_version=4.27)
is semantic support; even pages labelled 4.27 include newer fields/types. Exact
Lua-accessible fields/enums come from the installed UHT and pinned binding. The
method/default existence is not represented as a successful resource-free draw.

## Geometry, ownership and cleanup

The existing selection/guards stay: one natural «Открыть», TipHUD exact class,
its WidgetTree/CanvasPanel_6 ownership, three original canvas children,
TextBlock_89/CanvasPanelSlot, measured Position=(38,0), Alignment=(0,0.5), point
anchors `(0,0.5)` and desktop font size22. No force-load, native-array access,
action/input change or original Text/Font/Slot/ancestor write.

- Label remains 140×28, bottom at original.Y−18, native font copied as before.
- Divider is 140×2 **Slate/layout units**, center at original.Y−15, X=original.X;
  it is below the label. No claim of exactly two physical screen pixels/DPI.
  These are temporary technical values, not an accepted ornament/design.
- Both objects are transient siblings with Outer=that WidgetTree. Native slots
  hold attachment references. No Lua strong-root assumption or forced destruction.
  Only path/address/class/role records persist across callbacks.
- Both stay Collapsed until both configuration/attachment paths pass, then
  HitTestInvisible. No additional input target or parent opacity/visibility override.
  Same chord/one 30-second timer/state-change/failure triggers pair cleanup.
- Creation remains one attempt, reentrancy guarded. Cleanup works in reverse
  order with **independent pcall per child**; failure on one still attempts the
  other. Successful/absent items are forgotten; only failed identities remain
  for an explicit retry. Foreign reparenting/identity replacement is not removed.
  CLEANED requires no pending own children; no ClearChildren or index removal.

Adding even a tiny child can affect desired-size/layout. No original geometry
is assigned, and the divider width matches the existing added label, but absence
of engine-driven reflow/clipping still needs user observation. Inherited opacity,
pixel coverage/thickness and texture-free Box support remain this test's visual
questions. Full target/menu/GC/device coverage is not added to this stage.

## Source, checks and future test

### Authorized deployment, 2026-10-28

User authorized source `180ffbfa8d0ba6e0e6c5da8aa8efe9f818152f3c`. Host absent
immediately before replacement; installed hash matches below. Prior successful
label-only source/hash and its disabled state preserved outside loader paths,
with guarded rollback and pretest log. Nine other mod files and loader settings
remain hash-identical. Only own main.lua/activation marker changed; old CanShow
probe remains disabled. No game launch/termination/hot reload or visual result.

[ui-child/Scripts/main.lua](ui-child/Scripts/main.lua), SHA256
`94f7bd87b91038dfea8c6c39cd1123fadbaa452fee88a7867c3b5b06e53ac8cb`.
Frozen successful label-only source stays at `6e55c184dded60eb1e2a1c0f8753f37bdeda18fe`
with hash `b0e0f6c3db12c90b62e6e285d0ddfa227f22f383dd5eaf243512d643aad3d7bb`.

Offline checks: retained UHT field/signature/enum inventory, pinned struct-writer
source, typed-brush/readback policy and cleanup tests. `tools/test.py` passes
7 unchanged CanShow groups plus 15 revised UIChild groups. The latter cover two
idempotent children, brush configuration, absent Image class, unexpected defaults,
second construction/configuration/attachment failure, independent cleanup after
one failure, explicit retry, vanished owners and original identity guards.
Mocks prove authored policy and failure containment, not native brush defaults,
GPU pixels or GC. Input header hashes/check result stay local in
`.local/research/interaction-prompts/divider-api-check.json`; raw SDK not published.

**Next sufficient step:** separate permission for exact-source installation with
closed host and preserved disabled baseline. One future Open prompt/chord test
should judge the new line, not re-prove the accepted TextBlock: visible solid thin
line under OPEN, original action/icon still in place, second chord removes both.
Capture BRUSH_DEFAULT/BRUSH_READY, two role-tagged attachments/removals and final
CLEANED; user observes actual pixels. If absent, use this evidence to distinguish
configuration failure from render/scale behavior, without an automatic broad
observer or asset-override fallback. Installation was subsequently authorized as
recorded above; execution/observation is now the user's next step.
