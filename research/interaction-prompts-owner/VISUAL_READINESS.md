# Two-line TipHUD: layout and font readiness — 2026-10-28

**Dynamic font follow-up:** [DYNAMIC_FONT_READINESS.md](DYNAMIC_FONT_READINESS.md)
identifies private Template UFont + reflected FFontData filename as the next
candidate before a C++ bridge. Its storage test passed, and
[aphes-text/README.md](aphes-text/README.md) now records the successful native
OPEN→READ/manual cleanup run and user visual confirmation;
stock-resource replacement has no safe donor. The older cooker blocker is scoped
to creating cooked assets, not a universal requirement for dynamic fonts.

**PNG alternative:** [PNG-header](png-header/README.md) is prepared for one separate
native texture/alpha test. It bypasses a cooked UFont for fixed raster glyphs;
it is not a native Aphes font resource or a runtime-proven image path yet.

**Completed independent step:** [stock-font child experiment](ui-child/README.md)
created, visibly rendered and manually detached one added label in-game, with
original text/icon reported in place. Probe disabled. This closes that narrow
primitive attachment question; Aphes/divider and broader lifecycle remain open.
The Aphes-specific BLOCKED checkpoint below is unchanged.

**Divider follow-up:** [resource-free Image Box revision](DIVIDER_READINESS.md)
rendered in one Open prompt; native pair detachment and one Image's resource
defaults were logged. Probe disabled. Full lifecycle/final design remain unverified.

**Follow-up:** [local toolchain check](FONT_RESOURCE_READINESS.md) completed:
no compatible editor/cooker located; repak is packaging-only. No font asset or UI
payload created. The concrete prerequisite is an available UE4.27 font import/
cook toolchain; the earlier proposed tooling check below is historical.

**Checkpoint: BLOCKED for an executable Aphes visual prototype.** The least
invasive candidate remains an additive runtime extension of the existing
`CanvasPanel_6`, with an isolated font resource. Layout ownership is established
offline; a valid Aphes UMG font resource/construction path is not. No visual Lua
payload, asset override, package or imitation of working UMG code was created.
This is a specific missing font bridge, not evidence that UMG cannot render Aphes.

## Scope and recovered evidence

Clean independent checkout, one worktree, branch `research/interaction-prompts-owner`,
HEAD and live remote both `1d0983ec76a33bdf396932949f2164e5848e1bb0` before this work.
No unpublished files were overwritten. DevRules remote main was checked at
`c9a90c04336072e821761e376d1702d63899c4ab`; applicable local rules and their
origin/main deltas read without changing the older DevRules checkout.
`d52939b`/`a74d64f` explain the deferred native/UEPseudo route;
`4cda59f`/`294e8cc`/`1d0983e` own the minimal observer/source/install/live result.
Its 948 calls, six snapshots and three widgets are reused, not repeated.
Shared Research R-006 on `codex/ue4ss-metadata-api` already contains that live
result and its limits. Current remote Research main `766e79c` was also inspected;
it has the UHT result but not those later branch additions. Promotion here updates
the existing research branch, without modifying either repository's main.

Target remains Steam 1.09/build12996889, UE4.27 Windows x64, UE4SS `83330635`.
This stage reads retained stock CUE4Parse exports, the completed UHT dump and
the pinned UE4SS source snapshots. No new game execution or installation.
Raw game data, fonts and generated headers stay ignored/local.

## 1. Actual serialized tree and slots

Edges are established by resolving export indices, checking each slot's Parent
and Content and the child's reciprocal Slot, not by widget names:

```text
TipHUD_C.WidgetTree
└─ CanvasPanel_0 (RootWidget)
   └─ [CanvasPanelSlot_0] HorizontalBox_4
      └─ [HorizontalBoxSlot_9] CanvasPanel_6
         ├─ [CanvasPanelSlot_29] TextBlock_89
         ├─ [CanvasPanelSlot_1] RetainerBox_0
         │  └─ [PanelSlot_0] ImageInteractAllowed
         └─ [CanvasPanelSlot_2] CanvasPanel_2
            └─ [CanvasPanelSlot_19] ImageInteractNotAllowed
```

| Slot / object | Explicit exported layout/property | Consequence / limit |
| --- | --- | --- |
| CanvasPanelSlot_0 | Point anchors `(0.5,0.5)`, alignment `(0.5,0.5)`, offsets Right=1000, Bottom=100 | Serialized centered 1000×100 container; not a measured screen rectangle |
| HorizontalBoxSlot_9 | Fill size rule, horizontal center | CanvasPanel_6 participates in the native horizontal layout; omitted fields are defaults, not newly measured values |
| CanvasPanelSlot_29 | Point anchors `(0,0.5)`, alignment `(0,0.5)`, Left=88, Right=198.28572, Bottom=72.28572, AutoSize=true | Text uses desired size; these offsets do not prove a fixed live 198×72 text area |
| TextBlock_89 | Size=22, outline=2, center justification, WrapTextAt=800 | Localized line can grow/wrap; no new forced truncation/width is justified |
| CanvasPanelSlot_1 | Point anchors `(0,0.5)`, alignment `(0,0.5)`, 128×128 | Retainer branch is separate from text |
| CanvasPanelSlot_2 | Same anchors/alignment, 38×38 | Separate forbidden-action overlay branch |
| CanvasPanel_2 | Collapsed, ClipToBounds | This clipping applies to the forbidden overlay subtree, not evidence that the whole prompt clips upper text |
| CanvasPanelSlot_19 | Maximum anchor `(1,1)`, Right/Bottom=0 | Stretched overlay; absent minimum/other fields retain engine defaults |

Canvas/slot behavior must still be observed in the real game: serialized offsets
are not final layout geometry, DPI scaling, clipping, desired-size or native
consumer writes. In particular, adding children may change a panel's desired
size and therefore the position of its centered ancestors. The component's
serialized DrawSize=1000×1000 is not proof of space available on screen.

### Ownership and update boundaries

- Blueprint ubergraph **661** supplies exactly `[TextBlock_89]` to the native
  consumer at **713**. The proposed upper label is NOT added to that array.
  It must not replace, reparent or change TextBlock_89.Text/Font/Slot.
- ImagePanels is cleared at **773**, rebuilt at **593** with RetainerBox_0 and
  consumed at **713**. Do not add decoration there: it is native-owned input UI.
- The original icon branch has TipIconMat/parameter Icon; **407–534** updates
  hold-progress scalar `t`. Keep that branch and the forbidden overlay intact.
- Construct enters **1167**; handheld mode jumps to **10–361**, copies original
  font settings and changes size to 56. A new label needs its own sizing policy;
  22 is an exported baseline, not an unconditional runtime font size.
- Tick **1127/1147** changes TipHUD's own opacity for DebugHideUMG. Children in
  this tree can inherit parent visibility/opacity; they must not force ancestors
  visible or alpha=1. Individual TextBlock/native display-mode changes are a
  separate unproved boundary. CanShow post does not expose its bool result.
- Only BaseGameEventObject_BP references TipHUD class in the retained relevant
  non-bytecode export set. Inheritance links Take/Open/Check families to that
  component. This bounded set is not a full game's reverse-reference graph;
  ladder remains unlinked. All live TipHUD instances share the class definition,
  but template children are instanced: editing one instance is narrower than
  overriding the class asset. Other similarly named TextBlocks are not shared
  merely because their names match.

## 2. What the actual UI API establishes

The completed installed-build UHT dump declares UCanvasPanel::AddChildToCanvas,
UPanelWidget::RemoveChild, CanvasPanelSlot SetPosition/SetSize/SetAnchors/
SetAlignment/SetAutoSize, UWidget GetParent/SetVisibility/RemoveFromParent and
UTextBlock::SetFont(FSlateFontInfo)/SetText(FText). WidgetTree exposes RootWidget;
ConstructWidget is not a reflected function in this dump. Do not invent a Lua
WidgetTree:ConstructWidget method from a C++ template example.

[LuaMod.cpp at 83330635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp),
**1916–2023**, implements StaticConstructObject using a UClass and UObject Outer
and the native FStaticConstructObjectParameters path. This is an available
primitive for new TextBlock/decorative widgets, not a checked UMG factory or
proof of correct widget initialization/GC attachment. Existing CanShow post is
a verified narrow access point to a live TipHUD; no new native/global hook is
needed to select a first test instance. Creation/attachment and rollback of only
our children would still be experimental UI behavior.

The generated UHT `.cpp` files contain stub bodies. They are NOT implementations
of SetFont, FontFace loading, constructors or native layout. Generated UPROPERTY
specifiers also must not be treated as original source access/Blueprint policy.

## 3. Aphes: a font bridge, not a string substitution

Existing stock TTF SHA256:
`443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0`.
Its cmap has glyphs for O/P/E/N, no Cyrillic. `OPEN` can be technical glyph input
only; it is neither a translation nor an adopted word in Aphes. The Russian
action must continue through the original localized TextBlock.

1. **Existing resource:** retained inventory/research found the raw
   `Genesis/Content/Fonts/Aphes.ttf`, no confirmed Aphes UFont/FontFace. The known
   Umg_Font composite references EBGaramond, FiraSans and Noto faces, not Aphes.
   Do not globally replace that shared composite or infer a usable Aphes object
   from `.AphesText` in Coherent. No broad inventory was repeated.
2. **Supported UMG asset path:** Epic's
   [UE4.27 UMG font guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-fonts-with-umg?application_version=4.27)
   describes runtime-cached composite font assets. Its
   [Font/FontFace guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/font-asset-and-editor?application_version=4.27)
   separates the composite from the imported face payload. This is the most
   direct standard route: a **new, local-only companion** runtime UFont/FontFace
   cooked for UE4.27, used exclusively by our new label. No stock UI/font asset
   replacement. Such a resource has not been built or shown loadable here.
3. **Runtime file path:** UE4.27 documents a
   [FFontData filename constructor](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/SlateCore/Fonts/FFontData?application_version=4.27).
   That is a C++ API, not a Lua constructor. Installed-build reflection contains
   UFont.CompositeFont → DefaultTypeface.Fonts → FTypefaceEntry.Font →
   FFontData.FontFilename/Hinting/LoadingPolicy/SubFaceIndex/FontFaceAsset.
   FSlateFontInfo exposes FontObject, FontMaterial, OutlineSettings,
   TypefaceFontName, int32 Size and LetterSpacing; it has no reflected filename
   member. Thus SetFont with a made-up path field is not a supported bridge.
4. **Why field writes are not proof:** pinned LuaUObject.cpp **572–652, 754–830**
   marshals reflected struct fields; **908–928** appends zeroed array elements
   and writes their properties. This does not establish the native FFontData
   filename constructor, its complete non-reflected state/cache invariants,
   file resolution from the game's packaged TTF, or the validity of the resulting
   font. No raw-offset/cache patch or constructor emulation is justified.
   Likewise, setting UFontFace.SourceFilename alone is not an import operation:
   the [4.27 FontFace contract](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FontFace?application_version=4.27)
   distinguishes source filename from the raw font payload/cooked `.ufont`.

Epic's API pages are conceptual support, not installed ABI proof: even pages
labelled 4.27 currently show some newer declarations (for example float Size /
TObjectPtr). The installed UHT dump and pinned UE4SS source govern exact fields.
No conclusion relies on a UE5-only runtime plugin or a different loader revision.

**Blocking prerequisite:** obtain a valid, version-compatible, isolated Aphes
UMG font object through the standard local cook path, or prove a complete exact
4.27 runtime construction/loading contract. Reflection field existence alone
does not close it. Prefer the local cooked-font route before considering native
code. This changes the pure-Lua proposal into Lua plus a companion font asset;
it does not justify a whole TipHUD replacement or independent overlay.

The font and any generated asset containing its data remain local, outside Git.
An original build recipe may eventually be public; this work grants no
redistribution rights for extracted glyph payloads. No font dependency imported.

## 4. Mechanism choice

| Candidate | Native text/buttons and final writer | Lifecycle / layout / devices / long strings | Compatibility, complexity and rollback |
| --- | --- | --- | --- |
| **Add two siblings under CanvasPanel_6, with isolated font** — preferred | Keep exact TextBlock and icon/material inputs. No need to intercept final SetText for a fixed technical OPEN sample. Must verify native per-child visibility/slot changes so decoration follows the displayed action | Inherits prompt ancestors; creation/GC, panel desired-size, clipping and individual modes untested. Original localization/input and wrapping remain native; keyboard/gamepad geometry must be tested | No stock package replacement or common font mutation. Small Lua addition + companion font dependency. Detach only our children on failure; full rollback must be checked before payload readiness |
| Narrow TipHUD asset/UI override | Can preserve original names/graph, but changes the shared generated class/template and depends on accurate serialization/cooking | Native lifecycle retained if compatible; reparenting TextBlock into a vertical box changes its slot type and could break native assumptions. Still needs font, device/long-text checks | Larger collision surface with any other TipHUD replacement; exact cooked reconstruction/patch pipeline unproved. Removing own package reverts next session; not the first choice |
| Independent overlay | Must mirror text, target, geometry, hide/show and input ownership across UI systems; still no proven contextual link to Coherent | Separate lifecycle/position synchronization, stale-state and menu risks. Coherent's Aphes support does not solve these links | More moving parts than the missing font bridge. Reject for this stage; no overlay implementation |

The unknown final writer remains relevant to native geometry/per-child visibility
and eventual action mapping, **not** a prerequisite to replacing localized text:
we do not replace it. A fixed OPEN first prototype should be manually scoped to
an actual ordinary «Открыть» prompt and disabled elsewhere. No pseudo-dictionary,
automatic general action mapping or full native observer is proposed.

## 5. READY/BLOCKED checkpoint and sufficient next step

| Property | Current evidence |
| --- | --- |
| Observable change | New compact upper glyph label + authored thin divider; original localized action and input untouched |
| Owner | Serialized CanvasPanel_6 and seven reciprocal slot edges confirmed; live text access already observed |
| Final consumer / commit | Native original text consumer known; private UFont configured and actual Aphes rendered/switched on own child, manual detach/reference replacement passed |
| Blast radius | Intended one test instance; class override/shared fonts would broaden it and are excluded from preferred route |
| Preserved invariants | Original TextBlock reference/font/text/slot, icon/hold/lock branch, parent visibility/opacity, native input/localization |
| Acceptance evidence | Stock-font label/divider, Template storage and actual Aphes OPEN→READ/manual cleanup passed; final composition and GC/production lifecycle not accepted |

**Production BLOCKED; bounded Aphes visual mechanism PASS.** The
[transient-provider prototype](aphes-text/README.md) bypassed cooked resources
in the accepted technical run after setter/ownership review. The historical
editor/cook route is still unavailable, but is not a prerequisite to this source.

The one natural «Открыть» prompt OPEN→READ/manual cleanup test is complete;
do not repeat it. Next choose composition, outline, sizes and divider without
treating the current technical appearance as adopted design. Broader hide/show,
world-travel, input-device/DPI/long-string and GC acceptance remain later gates.

## Offline checks and exact inputs

`audit_tip_layout.py` resolves all seven reciprocal slot edges, verifies the root,
text/icon branches and one-TextBlock native consumer array, enumerates known
composite font faces and bounded retained class references, and emits hashes.
Run with Python 3 and the retained static-export directory; no engine/API calls,
loading, extraction, input edits or third-party dependency. Result:
`STATIC_LAYOUT_CONFIRMED_FONT_BRIDGE_UNPROVED`.

Repository `tools/test.py` also passes all seven existing CanShow mock test
groups; this is a preservation check, not font or new UI runtime validation.
Python syntax, changed relative documentation links and `git diff --check`
are checked before publication. No binary build/cook or new runtime test claimed.

| Retained input | SHA256 |
| --- | --- |
| TipHUD.json | `8c9a885d2904956a4899d979b2c4b60f355f62ec05b7e53b45d95938dc1be16e` |
| TipHUD ubergraph bytecode JSON | `980f62888f5db2a6f6e46a12ccfdce8703887842b6b43583988c0c8e70435dd0` |
| Umg_Font.json | `e99035e6fba5c0e3100e4114877be5219b0cdfbe4e95c5a3de11e40d32fcc5c5` |
| LuaMod.cpp, revision 83330635 | `ecc9448999fdac16d4b9181d73f99aafeb8f75dd12ad921e3f7f7922d8298227` |
| LuaUObject.cpp, revision 83330635 | `9dd81472765d66596b31fc12100d1098fbd84e5311226b4d1decc397a13e9b17` |

UHT provenance/dump identity: [UHT_SIGNATURE.md](UHT_SIGNATURE.md). Font cmap and
prior observer runtime identity: [VERIFIED_RUNTIME.md](../../docs/VERIFIED_RUNTIME.md).
These checks prove static structure/contracts, not successful rendering or a
safe runtime prototype. VERSION/production/main and installed environment unchanged.
