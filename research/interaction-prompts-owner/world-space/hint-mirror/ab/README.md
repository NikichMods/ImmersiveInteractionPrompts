# Owned World hint — Masked/Translucent A/B

**MASKED_CAPTURE_PASS / A_B_INCOMPLETE_CAMERA_GUARD / DISABLED**, 2026-10-30.
Source readiness is unchanged. Translucent transition/rendering remains untested;
the disappearance in screenshot B was native cleanup, not a material result.
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

The user subsequently authorized installation; see the exact record below.
Only this IIP candidate is enabled. The remaining steps are user-operated runtime.
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

## Authorized installation — 2026-10-30

Installed exact source `caf955fb271558df1ddd5c991cf5b53217da2ef4` in the new
`ImmersiveInteractionPromptsWorldHintABProbe` loader directory. Four Lua files
match the table above byte-for-byte; the fifth and only enablement file is empty
`enabled.txt` (SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).
No loader configuration/mods.txt changes, source edits, assets or extra observer.

Get-Process and privileged CIM enumeration confirmed no Genesis/Asterigos process
before installation; no process was launched or terminated by the agent.
Installed UE4SS.dll SHA256
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`
matches the earlier baseline; existing log records Git SHA83330635. Target was
absent;15 old IIP directories have no enablement marker and no active IIP entry
in mods.txt. CombatHUD/SoulsEnemyHUD enablement and bytes remain unchanged.

Ignored archive `install-20261030T063049Z` under the local hint-mirror/ab evidence
root contains all36 prior Mods files, loader DLL/settings/log, Genesis log,
four frozen source copies, planned/verified JSON manifests and guarded rollback.
All40 existing mod/loader/log hashes and60 config/save hashes matched after
installation. No settings/save content was modified or restored. Backup copies
also matched their originals. Rollback restores the previous absent target by
removing only the five expected own files after process/path/hash checks; it
refuses unexpected/changed files and does not delete recursively. Both scripts
passed PowerShell parsing; rollback was not executed against this live install.

Installation verification passed; game runtime, screenshots and material A/B
were PENDING at handoff. No hot reload, production/VERSION or other mod changes.

## Runtime result — 2026-10-30 09:40 Moscow

Exact source/installed four hashes above remained unchanged. The user supplied
two2560×1440 screenshots: A shows the small pale/bluish own F above the unchanged
native action/F; B shows the original prompt with own icon absent after F6 and
acknowledged camera movement. Raw frames/logs stay local, not public Git.

| Event, Moscow time | Evidence and interpretation |
| --- | --- |
| 09:40:26.805 | Own component CREATED; accepted anchor/scale/DrawSize/Yaw path retained. |
| 09:40:32.952 | Device1 native source bound, generation2; earlier device4 was replaced before A. No input/keymap override. |
| 09:40:33.203 | One `SAMPLE mode=masked`, native projection/out-table readout completed. |
| 09:40:51.607 | F6 handling fails `AB camera moved` in comparable(view), **before** own_material_switch BEGIN. |
| 09:40:51.623 | Loop cancellation, RELEASED, native COMPONENT_DESTROYED and CLEANED reason=failure complete. |

There is no own_material_switch BEGIN/END, no Translucent SAMPLE and no
PAIR_READY. `comparable` runs before `phase="translucent"`, BlendMode write and
SetMaterial. Thus material mutation was **not attempted**. The movement guard
rejected the pair and removed the own output; B cannot diagnose invisible
Translucent, alpha/gamma or failed SetMaterial. Manual F7 was not captured in
this run; earlier accepted F7 evidence is unchanged. This is also not the earlier
3.764s original-visibility failure: this component lived about24.8s and stopped
specifically on the new camera-comparability guard.

### A: measured state, not a color diagnosis

- Native `ProjectWorldLocationToScreen` produced four finite corners and
  GetViewportSize returned2560×1440, matching both PNG headers. Own **slot**
  rectangle: x1243.62305–1269.57227, y568.714294–593.74115, dimensions
  **25.9492188×25.0268555 px**. Slot38×38 corresponds to9.5×9.5 world units.
  This is neither the painted F glyph bounds nor the source Screen slot size.
  The latter remains unavailable through the selected opaque FGeometry route.
- Camera at A: FOV75, rotation approximately(-20.5475,-75.5397,0), original
  viewport coordinates; own plane Pitch/Roll0, scale0.25 and fixed world position
  unchanged. No persisted pose/address becomes a selector in another process.
- Own actual gamma=false, sRGB=true, force-linear=false, TargetGamma0,
  RenderTargetFormat field6 (=RTF_RGBA16f); clear/background(0,0,0,0).
  This enum field alone is **not** an independent measurement of RHI pixel
  format/OverrideFormat after InitCustomFormat. No GPU-format conclusion follows.
- Component/effective MID tint(1,1,1,1), opacity-from-texture1, own Image tint
  white, Image/host opacity1. Effective BackColor(0,0,0,0). Masked component1 and
  MIC blend1, two-sided=true, depth-disable=false; own RT512×128 and correct
  component-owned MID/SlateUI binding passed. Source Icon51×51, format3,
  AlphaComposite5 as before.

The screenshot now corroborates the reported small/pale-blue appearance.
Recorded values exclude a deliberately reduced own tint/opacity or enabled
own gamma flag at A. They do not establish premultiplied-alpha, sampling or
scene-color causality. No compensation, resize or material fix is justified by
this incomplete pair.

### Preservation and next sufficient step

Ignored archive `runtime-20261030T064347Z` contains UE4SS/Genesis logs, event
extract, original A/B PNGs, four exact installed Lua, enablement marker copy,
installed manifest, current-state hashes and disable result. SHA256:

- UE4SS.log: `b9188c68eecdc626d62062b2ee6b25b603cc40efaa6ba8ab7944f8ef3d8cfaa4`
- Genesis.log: `78f923bd863ee8399c48808a3663676461188e95bf9b5fedd7afaf0b3c5e03f6`
- A.png: `2d18a333241fc8ced14fdad45d7b065c54f38ed147e648210596452b276cbd76`
- B.png: `5ba738882fb420d4fede868011aec25911e9ddaf10371a2554f2a30ff7ade066`

With the game already closed (Get-Process/CIM), only this probe's enabled.txt
was removed. Four Lua bytes remain installed/frozen;104 other current files and
38 historical non-log mod/loader hashes were preserved. Other IIP probes remain
disabled; CombatHUD/SoulsEnemyHUD/settings/saves were not modified or restored.
No game launch/termination/hot reload, payload edit or automatic retry.

Next sufficient evidence is the same separately authorized A/B attempt: choose
camera pose **before** requesting A, then keep camera/character still through F6
and B; only then move for changed-material occlusion. The strict guard worked
as designed; this result calls for no code fix, wider tolerance or longer timeout.
The pair remains open, not a negative verdict on Translucent or on World-space.
