# Owned World hint — Masked/Translucent A/B

**READY_SOURCE / NOT_INSTALLED / RUNTIME_NOT_TESTED**, 2026-10-30.
Automatic native Screen-size measurement: **BLOCKED at opaque FGeometry return**;
the permitted screenshot fallback is used. Own geometric slot projection is
implemented. Visual equivalence, full composition and production remain BLOCKED.

## Method and scope

The [source review](../VISUAL_FIDELITY.md) left one useful runtime question:
does the stock continuous-alpha surface improve this borrowed retained hint,
with all other settings held constant? Static analysis cannot decide final
pixels. A small addition to the accepted hint harness is warranted: record two
states, validate comparability, change only the owned surface. No shader,
reconstructed keymap, second Retainer or new scene-wide observer is needed.

This is a new independent four-Lua candidate in `Scripts/`, copied from the
frozen parent and extended narrowly. Parent files and installed disabled probe
are unchanged. Reuse exact natural Open binding, one private host, World mesh,
frame-Yaw, native source updates, cancellation and native cleanup. No Aphes,
ornament, text, original UI mutation or distance scaling.

## Material contract — no guessed SetBlendMode UFunction

Installed UHT exposes PrimitiveComponent.SetMaterial(int32, MaterialInterface*),
GetMaterial(int32), WidgetComponent.GetMaterialInstance and reflected BlendMode.
It does **not** expose WidgetComponent.SetBlendMode as a UFunction. UE4SS83330635
supports numeric FEnumProperty/byte writes. We set only **own** `c.BlendMode=2`,
then call the reflected virtual `c:SetMaterial(0,stock_translucent)` on EngineTick.

UE4.27 WidgetComponent.cpp707–728 proves the virtual override runs
UpdateMaterialInstance, creates the component-owned MID, rebinds SlateUI and
tint/opacity parameters, then MarkRenderStateDirty. The scene proxy captures the
updated blend enum. No re-registration, second component, widget transfer or
manual render-state offset is needed. The native setter itself has no extra
effect beyond enum assignment/render-state dirtiness (2038–2047).

Both exact stock MICs are resolved/validated before own allocation, with at most
one exact LoadAsset attempt per missing resource, after leaving CanShow. Masked
starts at component1/material BLEND_Masked1; Translucent uses component
Transparent2/material BLEND_Translucent2. Both must have the expected base,
two-sided override and depth-disable=false. GetMaterial override and actual
MID.Parent/Outer are checked before and after the single switch. Original effect
MID is never mutated. Native UI flags, show/hide guards and hint change budgets
remain intact.

One component/host/image/RT remains in use. SetMaterial creates a new **own MID**;
the old one is left to native GC, not rooted or reused. If a different RT or
component appears, this experiment rejects the pair. A failed native call has
BEGIN/END markers and uses existing full cleanup. No automatic switch retry or
back-and-forth cycle. Camera is neither frozen nor repositioned by code.

## Measurement and diagnostic contract

- Own icon slot stays centered at38×38 (or the same validated native source size),
  RT512×128, scale0.25, fixed anchor+32Z and accepted vertical Yaw. Own root/host/
  image render transforms must be identity. Slot anchors/alignment/position and
  component pivot are read and checked. No sizing correction is applied yet.
- For each of the four slot corners, use the real plane mapping
  `local=(0,-u,-v)`, current component location/scale and vertical Yaw, then
  `PlayerController.ProjectWorldLocationToScreen(point, out_table, false)`.
  Log four projected corners and their viewport-pixel bounding rectangle.
  This is the **geometric slot footprint**, not the painted glyph bounds,
  anti-aliased coverage or visible pixels after occlusion. No radial-distance/FOV
  approximation is used for the projection.
- Installed UHT has `GetCachedGeometry`/Tick/Paint variants and
  SlateBlueprintLibrary.LocalToViewport/GetLocalSize. Their presence is not
  enough: pinned LuaUObject.cpp339–355 returns UFunction values through
  GetNonTrivialLocal; struct branch751–840 converts to a table by reflected fields
  (conversion652–748). Installed SlateCore.Geometry has **no reflected members**.
  Ordinary FGeometry returns therefore do not preserve its native transforms/
  size for round-tripping into the next UFunction. Passing `{}` would not measure
  the original geometry. No FGeometry calls, fabricated fields, custom properties
  or raw offsets are used. `source_screen_px=UNAVAILABLE` is explicit.
- Actual own values recorded twice: bApplyGammaCorrection; reflected RT **sRGB**
  (case matters), bForceLinearGamma, TargetGamma, format/clear/extent; component
  background/tint/opacity; effective own MID TintColorAndOpacity, BackColor and
  OpacityFromTexture; SlateUI binding; own Image/host opacity, material parent,
  enum, depth and identities. These are reflected fields/known MID getters.
  No missing field is replaced by its expected default. No GPU/shader readback,
  GSlateContrast or effective inherited clip-threshold claim is made.
- Captures wait at least three EngineTick callbacks after explicit A request or
  material switch, plus a ready bound source and live RT. This is not a GPU fence
  or proof of fresh pixels. Screenshots/user observation remain the visual proof.
- Both captures require identical source key **and generation**, component/RT,
  non-material settings and anchor/scale. Same player/camera/viewport; camera
  position tolerance≤1 unit per axis, rotation≤0.2° per axis, FOV≤0.01°. Both real
  poses are logged; this tolerance is a comparison envelope, not exact camera
  equality. Large motion/source replacement/device change rejects the pair.

Sources: installed UHT for WidgetComponent, PrimitiveComponent, PlayerController,
PlayerCameraManager, CanvasPanelSlot, Geometry, Texture/TextureRenderTarget2D and
MaterialInstanceDynamic; [pinned LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
(out tables230–320, struct returns339–355/751–840, enum Set1599–1623);
[exact UE4.27 WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp)
(plane364–380, virtual SetMaterial707–728, proxy material/BlendMode, virtual window
size/DrawWidgetToRenderTarget, material parameter update2124). Source-only
cross-check is not byte identity with Asterigos engine. Local source/UHT hashes
are preserved ignored in `world-space/hint-mirror/ab/source-hashes.json` under the
existing local research evidence root; no dump or game asset enters Git.

## One future separately authorized user test

Installation is **not authorized by this document**. A future installation must
use closed-game identity/rollback checks and enable only this IIP candidate.
Choose keyboard and keep it throughout this pair; no new remapping or settings
changes. The original Screen prompt remains the visible comparison reference.

1. Start the game normally. Ctrl+Alt+F8 once, then the one manual reload required
   by the accepted BeginPlay binding. Approach one natural Open without using it.
2. When the own icon appears, stop movement and choose a view where both icons
   are visible. Press **Ctrl+Alt+F8 again** to request Masked sample A; wait about
   half a second and take screenshot **A** (for example Steam F12).
3. Keep that pose/device. Press **Ctrl+Alt+F6 once** for Translucent; wait about
   half a second and take screenshot **B**. Native readback may be ready before
   rendered pixels: report blank/stale output rather than assuming a successful
   visual switch. A second F6 does nothing.
4. If time remains, slightly move camera/Hilda to inspect occlusion of the **new
   Translucent surface**, then **Ctrl+Alt+F7**. This movement follows both captures;
   do not move between A and B. Original prompt/control should remain unchanged.
5. Exit normally when convenient; return the two screenshots and visual report.
   The agent reads local logs. Compare separately: projected/displayed size,
   edges/holes/background leakage, interior color and partial geometry occlusion.
   A screenshot crop can compare visible glyph pixel bounds; do not call that the
   original Slate slot measurement. If screenshots lack enough resolution or
   glyph is occluded, mark that comparison unavailable.

No requirement to finish by a relaxed deadline: observation120s, bound World/
Yaw45s, callbacks128/4096/12000, candidates8, original pose samples4 and source
generations8 are unchanged. Additional A/B diagnostic samples≤2, switches≤1.
The previous run stopped on the original visibility guard at~3.764s; this may
prevent the pair. If it stops early, do not restart/reload/retry automatically or
weaken guards. Return the incomplete result. F7 is available at every stage;
queued switch after cancellation is inert. Existing native destroy/release and
cancel-loop lifecycle is preserved, with no new persistent scheduled callback.

Expected logs: BASELINE_REQUESTED → SAMPLE mode=masked → own_material_switch
BEGIN/END → SAMPLE mode=translucent → PAIR_READY → existing LOOP_CANCELLED /
RELEASED / COMPONENT_DESTROYED / CLEANED. PAIR_READY proves comparable recorded
state, **not pixel equivalence or production acceptance**.

## Payload and offline checks

Exactly four Lua files, no engine assets, PNG, TTF, enabled marker or loader config:

| File | SHA256 |
| --- | --- |
| `Scripts/main.lua` | `6c863701ec1a0174c66175d2631ffe831f0f208295604e96d8341a7388fb6c1c` |
| `Scripts/IIPWorldChild.lua` | `2f026c71e801c6ad80f1f97d860a0dee5692e7325afd1f6de104bd491114b29d` |
| `Scripts/IIPHintSource.lua` | `66b0d6b7b8b96ae7dd03ffe9a58803920ebf658752d686dc1c34ba647e9a03d9` |
| `Scripts/IIPHintAB.lua` | `09d4acc0dc221bfa74ce3b9d4bc8b153d0199190e6bbfd5497001e53c178bd62` |

Hashes identify the checked source; no numbered build or release.
`tests/test_hint_ab.py`:21 policy tests, including projection corners/native out
tables, one switch/no extra component, early/repeated F6, native failure markers,
view/source/gamma changes, missing API/material/RT, cancel/visibility/timeout and
cleanup. Full suite:253 tests/17 suites PASS (21 new policy tests);
offline mocks cannot prove native material refresh, engine marshalling, rendered
pixel size, GPU latency, source geometry, color or Translucent occlusion.
