# Resource-free divider in native TipHUD — 2026-10-28

**Completed: resource-free divider visible; both own children detached by user
control. Probe disabled after the session.** Production
BLOCKED; Aphes/cooker, native observer and general lifecycle are out of scope.

## Runtime result — 2026-10-28

Exact tested source `180ffbfa8d0ba6e0e6c5da8aa8efe9f818152f3c`, SHA256
`94f7bd87b91038dfea8c6c39cd1123fadbaa452fee88a7867c3b5b06e53ac8cb`;
installed bytes rechecked after normal exit. UE4SS 83330635 / established Steam
UE4.27 baseline. User supplied a 2560×1440 screenshot showing OPEN, the horizontal
white divider below it, original «Открыть» and F hint. It establishes visible
rendering in this case, not final design/typography approval or unchanged pixel
geometry against a before frame.

| Log lines / Moscow time | Observation |
| --- | --- |
| 652, 04:51:05 | ARMED |
| 710–715, 04:51:51 | WAITING, measured slot `(38,0)` / alignment `(0,0.5)`, label created/attached |
| 716–718 | Image created; native default brush DrawAs=3(Image), ResourceObject absent, ResourceName=None, dynamic=false, has_uobject=false |
| 719–723 | BRUSH_BEGIN → BRUSH_READY (Box, no resource, 140×2, white RGBA1); divider attached; own_children=2 |
| 724–728, 04:51:56 | divider REMOVED, label REMOVED, CLEANED reason=user own_children_remaining=0 |
| 731, 04:52:14 | normal Event loop end |

Twenty UIChild lines; no FAILED/CLEANUP_ITEM_FAILED/CLEANUP_FAILED. Both
RemoveChild calls returned true and subsequent GetParent checks found no parent.
Cleanup happened about 5.5 seconds after ATTACHED, by the key-control path, **not
the 30-second timeout**. User was uncertain about pressing the second chord and
visually observing disappearance; no confident before/after disappearance claim
or post-cleanup screenshot is invented. Native pair detachment is established by
the log/source readbacks. The earlier separate label-only visual removal remains
its own evidence, not a substitute observation of this pair.

The default values above describe this newly constructed UImage in this run,
not all FSlateBrush constructors/styles. Explicit configuration/readback plus
the screenshot closes the resource-free Box-render question for this case.
Failure cleanup branches remain mock-tested, not exercised in this healthy run.
No forced GC, timeout, menu/target lifecycle or device/DPI coverage established.

Archived log SHA256
`24010b2bec863fdd17617b1b40502607c60f29273f0466670be96a2d0a825cd9`;
original screenshot SHA256
`076e2622aeef660b4a827200631a5d7d706dfe473d66ceff91544f5ddc79fda8`.
Both remain local/ignored. Host closed; only probe enabled.txt moved outside
loader paths, exact script retained disabled. Nine other mod files/settings
unchanged by hashes; previous tested label-only rollback remains available.
This bounded experiment is complete; no extra repeat just to accumulate passes.

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

**Defaults are not asserted from generated stub constructors.** At preparation
time actual UImage defaults had not been observed; the run above now records the
resource/default fields for one Image. The prototype
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
of engine-driven reflow/clipping beyond the supplied frame is not established.
The frame answers the texture-free Box visibility question for this case;
inherited opacity/scaling across other states and layouts remain unverified.
Full target/menu/GC/device coverage is not added to this stage.

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

**Test complete:** the single permitted run established line pixels and native
detachment of the pair. No further generic observer or asset-override fallback
is needed for that question. Aphes font, final visual proportions/ornament and
broader production lifecycle remain separate decisions. Any next experiment
needs a specific unresolved property, not another pass of this same case.
