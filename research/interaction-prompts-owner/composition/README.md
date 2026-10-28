# Compact Aphes / ornament / localized action — 2026-10-28

**READY for one separately authorized research installation/test. Not installed or
run. Production BLOCKED.** Source: [Scripts/main.lua](Scripts/main.lua), small
bounded geometry helper [IIPLayout.lua](Scripts/IIPLayout.lua).
The accepted `aphes-text` source is unchanged; its font/render/OPEN→READ and manual
cleanup evidence is reused, not rerun. This variant tests composition and an
unproven native PNG import, not the font mechanism again.

## Adopted layout and scope

The user's follow-up places the separator at the vertical center of the F key:
Aphes above, localized action below. Horizontal centering excludes the key.
Moving the lower line is allowed only through a simple reversible mechanism;
continually fighting native positioning is explicitly out of scope.

This candidate uses `UWidget::SetRenderTranslation(FVector2D)` once on the exact
stock `TextBlock_89`. UE4.27 Widget.cpp assigns only RenderTransform.Translation
and calls UpdateRenderTransform. It does not change the slot, font, text, scale,
shear, angle, desired size, parent or icon. Retained game UHT Widget.h declares
the method, GetDesiredSize and reflected RenderTransform; WidgetTransform.h
reflects Translation. The existing UE4SS83330635 reflected FVector2D/table call
contract is reused. No opaque FGeometry conversion is introduced.

Original translation must be exactly zero. A primitive identity/value snapshot
is stored before the setter, covering an exception after a partial write. On
cleanup it is restored only if it still equals our write (or already original).
A newer external translation is preserved and logged as LOWER_CONFLICT. On an
attached CanShow call, a changed translation terminates the attempt; it is never
reapplied. A restoration error retains the record for explicit cleanup retry.
Native final-writer behavior is not proved absent: the future test must check
stability and LOWER_RESTORED, not merely a good-looking frame.

Only one naturally visible RU «Открыть», desktop stock font22 and measured slot
(38,0) are eligible. The separate RetainerBox_0 key branch must have compatible
point anchors/alignment, non-auto-sized slot at (0,0), width at most38. Otherwise
stop before allocation. Read cached stock GetDesiredSize only: 80–260 wide and
20–40 high are the deliberate test limits, not supported localization policy.
Zero/malformed/out-of-range extent stops; no prepass on the original interface.
GetDesiredSize can still be stale, so these bounds do not establish screen geometry.

Temporary Aphes32 vs stock22 gives ratio1.45; white, own outline1/black alpha.75.
Own label is centered in a region at least160 wide, height40. Separator width is
cached stock-text width minus8; aspect570:16 is preserved. Four-unit inset keeps
the separator to the right of the guarded key slot. Eight-unit gaps separate it
from the upper label region and lower text extent. Lower translation is rounded
up to integer units for exact UE4 float32 readback. These are preliminary values,
not final design acceptance. OPEN/READ remain technical strings, not Aphes translation.

## How the original location-title separator works

Narrow extraction from installed **base containers**, Steam1.09/build12996889:
only Hud.html, commonObj/basic.css and images/menu/ele_loctitleline.png, using the
existing CUE4Parse1.2.2 reader. No extraction from another installed mod or broad
asset inventory. Retained raw inputs/audit live under ignored `.local`.

| Input under Genesis/Content/uiresources | SHA256 |
| --- | --- |
| Hud.html | f3edde51ec5d285ef242968a66f97f8da207cf5ec65b3c229e573f938937c87b |
| commonObj/basic.css | 5449a256f3d1b44bd286ecb37592ee25c6136c86671f8cefca47a0480da30a24 |
| images/menu/ele_loctitleline.png | 901b72602a69a535e6a3d54bce2a13f18d0badc20d59abfca351eec70161e668 |

Hud.html5676–5682 has PlaceName with Aphes/localized LevelName/MainName elements
and an Ani2 img referencing that PNG. Active CSS297–301 positions the image
absolutely at width40.5vw, height1.48vh, bottom3.88vh; the parent is a centered
column. Earlier background/pseudo-element alternatives are commented out.
The actual separator is **one 570×16 RGBA image**, alpha0–228, with symmetric
end ornaments and a small central motif. It is not a font glyph or CSS border.
The large title's spacing/viewport sizes are unsuitable for direct compact reuse.

An exact-basename search in the retained path index found the PNG, no matching
uasset/uexp. That does not prove absence of differently named UTextures. A Coherent
URL/HTML element is not itself a native UMG texture.

Chosen minimum: import this one stock PNG locally into our own UImage, rather
than author an imitation before seeing the real ornament at prompt scale. One
image serves all words/locales. It stays external/ignored, is not redistributed,
and no stock files are replaced. Future distribution would need extraction from
each user's game or independently authored art; neither installer nor rights to
redistribute host bytes are claimed. No plain-line fallback on import failure.

## Import, ownership and cleanup

Reuses the source-verified [PNG API contract](../png-header/README.md): exact
ImportFileAsTexture2D UFunction called with explicit library CDO, current TipHUD
world context and absolute local PNG path. Header/dimensions/RGBA/bounds checked;
exact hash must be checked before any separately authorized installation. One
import maximum, including failures. NOT_LOADED never forces object loading.

UE4.27 KismetRenderingLibrary.cpp565–568 delegates to FImageUtils. Image.cpp
SetBrushFromTexture updates its own brush and the imported texture's residency
flags; it is not a promise of no transient engine activity. Brush.ResourceObject
holds the imported texture. No wrapper/Outer-as-root/forced GC assumption.
On cleanup: stop behavior, restore owned stock translation, detach each own
element independently, release own font using the accepted typed SetFont(stock
read), clear detached image's brush resource. Failed items can retry cleanup
without import/allocation. At most two new children; one session/30s; no new
hooks beyond the existing post-only zero-input CanShow contract.

Reviewed UE4.27 source mirror revision
`306a7e9f7fb53f14c2cb3bfd3854ad906710a17e`:
[Widget.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/Widget.cpp),
[Image.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/Image.cpp),
[KismetRenderingLibrary.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/KismetRenderingLibrary.cpp).
This engine-source comparison is not the game's native binary source.

## Verification and next sufficient test

Eight new mock groups cover composition/one import, geometry rejection before
allocation, missing/null import before stock writes, partial stock setter error,
timeout/target exit, restoration retry, external-write preservation and texture
release retry. Existing suites also pass; they are regression checks, not new
native font evidence. No engine/GPU/GC, ornament alpha, DPI/clipping, desired-size
freshness or full lifecycle is proved offline.

Private `IIPCompositionConfig.lua` must return `{filename=<absolute local TTF>,
separator_filename=<absolute stock PNG>}` beside the source for a future install;
actual machine paths are in local configuration only. Missing config disables.

Next sufficient step, **after separate installation permission**: closed-game
rollback/hash-verified install of this source + helper + private config; one
natural chest Open prompt, Ctrl+Alt+F6: attach → READ → cleanup within30s. Check
ornament/upper/lower separation, F unchanged, no collision/flicker, and original
lower position after removal. Preserve log COMPOSITION_GEOMETRY, TEXTURE_BOUND,
LOWER_SHIFTED/LOWER_RESTORED and both REMOVED. If native drift/conflict occurs,
stop this arrangement; do not add per-frame enforcement. No new font diagnostic.

## Prepared source identity

Implementation commit `996ee47f06f6cf88d0440d235d13acb9daf05284`.

`Scripts/main.lua` SHA256: `3c8eb86e695b716616d89f143dd6d2f66ce4ff40c98db1aad50d99738f604abe`.

`Scripts/IIPLayout.lua` SHA256: `332ffbdda46c7ac9edc245dfc42913529e8ee9f20752a9ee9e077a367525ecc6`.
