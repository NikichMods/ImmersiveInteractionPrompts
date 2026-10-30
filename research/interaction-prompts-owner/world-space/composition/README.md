# World Aphes composition integration — BLOCKED on current input-hint reproduction

2026-10-30. Source-only integration review. **No executable World-composition
payload prepared, installed or run.** [IIPCompositionPlan.lua](IIPCompositionPlan.lua)
is only a pure slot-envelope function, with no UE APIs, loading, callbacks or
entrypoint. It is not a partial working mod. Production/final visual design/full
lifecycle remain BLOCKED. Existing accepted source and runtime bytes are frozen.

## Decision checkpoint

Reuse [vertical frame-yaw/F7 PASS](../vertical-yaw/README.md),
[deferred World renderer](../probe/deferred/README.md),
[private Aphes rendering](../../aphes-text/README.md) and
[ornament/composition](../../composition/README.md), without repeating them.
The new seam is independent reproduction of native **current content**, especially
input hints. A single earlier copied F brush was a snapshot, not keyboard/gamepad,
remapping or final-retainer-output acceptance. Do not turn that into a full hint
contract, or re-implement keymaps because a default happens to be F.

| Content route | Evidence / cost | Decision |
| --- | --- | --- |
| Read selected TextBlock_89.GetText and update own TextBlock | Current displayed value, existing localization selected by the game; no action table to maintain. | Preferred for lower action, with refresh and overflow guards. |
| Own InteractTipToText lookup or hard-coded label | Duplicates culture/state selection; loses the actual current consumer. | Unnecessary; no Russian text replacement. |
| Copy RetainerBox_0 child Image.Brush repeatedly | Struct value-copy/own resource reference is supported; earlier one keyboard snapshot displayed. But this copies the child, not the complete Retainer output. Active device/rebuild/topology change behavior not established. | Not sufficient for the required complete current hint. |
| Read live Retainer effect MID and display through own UImage | Reuses native-produced icon/effect state rather than mapping keys. Getter and own Image material setter are source-supported. Retainer uses special alpha/gamma flags; correctness in World target not established. | Preferred **candidate for the next hint-only test**, not a verified integration route. |
| Rebuild hint from current FKey/device/atlas | Shared R-014 proves a scalar PC mapping query, not key→glyph/atlas/chord/hold rendering. More dependencies than borrowing final native output. | Do not choose as automatic fallback. |
| Reparent/copy original TipHUD Slate/children or use original MID in another Retainer | Ownership conflict, second renderer or shared render-target parameter writes. | Rejected. Original Screen prompt remains untouched. |

## Action/localization contract

Installed UHT `UMG/Public/TextBlock.h:71,98` declares SetText(FText) / GetText() const.
[UE4.27 TextBlock.cpp297–319](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/TextBlock.cpp)
GetText reads live Slate when available, otherwise Text. SetText unbinds **its
recipient's** TextDelegate, so it must only be called on our own TextBlock.
Read the exact bound actor's original TextBlock_89; never call a setter/prepass
on the original or use another prompt's text. Copy stock FontInfo as a value
into our own lower label; do not change original outline/style.

Pinned [LuaUObject.cpp1728–1754](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
push_textproperty gets an owned Lua FText wrapper, but its **Set** branch uses
ToFString→SetString instead of copying full native FText history. That branch is
also used to marshal a reflected SetText argument. Merely passing FText userdata
therefore does **not** prove preservation of string-table namespace/key/history.
[LuaFText.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaFText.cpp)
uses a local value object; no borrowed text wrapper needs to survive callbacks.

Safe scope: reproduce the game's current localized **display value** on the own
label, re-read on bounded content checks, update if the value changes, and stop
on invalid/empty/unsupported extent or semantic mismatch. This avoids hard-coded
RU text but is not automatic culture propagation of the copied FText. Compare
rendered strings for a value change, not FText namespace equality. The old World
probe's RU eligibility literal is a historical test restriction, not a localization
implementation; a future integration should select Open by proven msgTag/Interact25
binding, with nonempty current text, rather than rewrite its displayed translation.

## Exact hint blocker

Retained `TipHUD.json` has RetainerBox_0 under the key branch; EffectMaterial is
`/Game/MainContent/Template/UMG/TipIconMat`, TextureParameter=`Icon`. Its ubergraph
bytecode offsets455/497/534 reads GetEffectMaterial and
GameGlobal.GetToDoInteractActionPressTimer then writes scalar `t` to that MID.
Offset713 forwards native SetupTipMessage2 with panel/text/texture arrays.
Thus the hint has a native child-production path and a configured Retainer material
stage. Live bRetainRender/phase flags and whether that stage is active in every
device/state were not captured; do not infer them from serialized EffectMaterial
alone. No opaque array interception is needed or authorized.

[RetainerBox.cpp55ff/120ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/RetainerBox.cpp)
GetEffectMaterial only asks its live Slate retainer; it does not create a material.
[SRetainerWidget.cpp295ff/565ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/SRetainerWidget.cpp)
returns the existing DynamicEffect. OnPaint updates its `Icon` texture parameter
to the retainer render target, then draws with PreMultipliedAlpha|NoGamma.
**SetEffectMaterial reuses an already supplied MID directly**; a second own
Retainer using the original MID would also write its own target into the shared
parameter. That is an unacceptable original-UI side effect, even without an
explicit Lua SetTextureParameterValue call. No such implementation is prepared.

A separate own UImage with SetBrushFromMaterial(existing source effect MID) would
hold a read-only reference, without a second Retainer's parameter writer.
[Image.cpp241ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/Image.cpp)
supports that setter. Do not call GetDynamicMaterial or mutate the borrowed MID.
But matching final alpha/gamma/cropping/size and the live material/retainer identity
across device switches/current remapping still need a **new narrow visual test**.
Copying child Brush alone is not declared broken; its completeness is unproved.
Unknown runtime material/branch transitions must fail closed, not leave a stale F.
This is the concrete blocker, not absence of a key API or missing font/toolchain.

## Provenance, independent tree and resources

Four own children only: Aphes TextBlock, ornament Image, localized TextBlock and
current-hint Image. Use the accepted separate PostionItemUMG_BP_C/tree/Canvas;
never pass original TipHUD to SetWidget or transfer any original child/Slate tree.
Aphes technical OPEN is not a verified translation. Candidate upper32 vs lower
stock22, LetterSpacing150, white/outline0/no shadow; exact sizes remain provisional.

Use the proven Template UFont copy with independent checked FontData storage,
local Aphes filename, FontFaceAsset=nil only on that copy; its own upper FontObject
is the native strong holder. Do not write original UFont/FontFace. Import the one
local stock ornament570x16 once as in the accepted PNG route; own Image brush
retains UTexture2D. These are ordinary Slate TextBlock/Image resources; the accepted
World host uses the same UMG draw path, so source supports an integration candidate
without cooker/new assets. The **combined World** font/ornament display is not
runtime-proven; do not call it PASS by transferring separate experiments.

Local files were present and hashed, no new extraction/image generation:
Aphes.ttf SHA256 `443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0`;
stock ele_loctitleline.png SHA256
`901b72602a69a535e6a3d54bce2a13f18d0badc20d59abfca351eec70161e668`.
Existing base-game provenance belongs to the prior composition/font reports.
No redistribution rights inferred; TTF/PNG/imported derivatives/raw exports stay
local/ignored. A public mod would need each user's own extraction or authored
replacement art, not these host bytes. No installer is added here.

Future cleanup keeps the accepted loop-cancel→own UI/resource release→SetWidget(nil)
→native own component destroy/host release order. It must release own upper font
using the typed stock lower FontInfo carrier and clear own image resources;
partial failure retains only own primitive cleanup records for retry. No new
roots/forced GC/borrowed material mutation. This is an integration plan, not an
implemented four-child cleanup claim. Original lower text/font/slot/parent/native
arrays and original Screen prompt remain intact and visible during the first test.

## RT512x128 feasibility — pure plan only

No change to RT, scale.25, stock masked/depth material, anchor+32Z or accepted
world-Z frame-Yaw. No distance scaling. Proposed four slot regions fit512x128
with a four-unit outer margin: upper440x48 at(36,4), ornament200x(200*16/570)
centered(256,64), lower and key centered on rowY100. Center upper/line/lower on
X256, **excluding the key**. Action measured width<=340/height<=40; key<=64x40,
eight-unit horizontal gap. At the former cached127.75x37.5/38x38 baseline this fits.

The pure function rejects invalid/unmeasured/oversized values; it does not silently
truncate, shrink fonts, alter localization or resize the renderer. No claim that
slot bounds prove actual glyph/outline bounds. Own upper Aphes text must be
measured after its own Slate initialization/prepass before a future candidate
can claim no clipping; no prepass on original UI. Long locale/chord/unsupported
hint sizes require a separate layout decision. Masked depth material can make a
thin downscaled ornament subtle; no material/line redesign is adopted here.

## One next sufficient test — hint mirror before full composition

First prepare a separately reviewable **hint-only** bounded candidate using the
accepted exact Open binding/private World host/Yaw/F7. Its new seam is one own
Image referencing the selected original retainer's existing effect MID read-only,
with exact live identity/size validation and re-resolution after device changes.
First sample bRetainRender/render-phase flags and the live final MID/resource; if
retention is inactive, evaluate the simpler child-brush route from that evidence
instead of forcing an unnecessary effect mirror.
No Aphes/font/import or full four-child payload is needed for that test. This
candidate is **not authored/installed in this task**; no speculative executable
setter sequence is supplied to conceal the blocker.

After separate source readiness and installation permission, one run should show
native Screen hint alongside that own mirror for keyboard→connected controller→
keyboard, taking at most four bounded snapshots of exact actor/retainer/MID/brush/
current displayed action and source visibility. Confirm both show the actual
currently configured Interact, including an already remapped binding where present,
not a shipped default; no settings/save write is authorized or needed here. If
there is no already-remapped case, record that as untested instead of changing
settings silently. Manual F7 then removes only own Image/host/component. Do not
repeat World rendering/occlusion/rotation as separate acceptance gates.

Success must establish glyph content, transparency and live device/current-key
agreement; missing/changed unsupported branch or stale output is a negative
result, not a fallback to F. If sampling source state alone suffices to reject the
candidate, stop before any copy. Passing this hint seam would justify the full
four-element integration source and its combined clipping/readability trial;
this document does not announce that full prototype READY_SOURCE.

## Offline checks and exact evidence

`python tools/test.py`:207 tests/15 suites PASS,8 new pure slot-envelope cases.
No new engine payload means no native integration tests or runtime acceptance.
Local Markdown links, whitespace/Git hygiene and frozen accepted source checked.
TipHUD export SHA256 `8c9a885d2904956a4899d979b2c4b60f355f62ec05b7e53b45d95938dc1be16e`;
ubergraph bytecode SHA256 `980f62888f5db2a6f6e46a12ccfdce8703887842b6b43583988c0c8e70435dd0`.
Exact UE4.27/pinned UE4SS/UHT/local-resource input hash manifest remains ignored at
`.local/research/interaction-prompts/world-space/composition/source-hashes.json`.
No production/VERSION/game/mod/settings/save changes or installation/hot reload.
