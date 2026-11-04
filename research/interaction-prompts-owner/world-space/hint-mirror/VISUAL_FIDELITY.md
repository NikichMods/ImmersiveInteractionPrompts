# World hint visual fidelity — source review, 2026-10-30

Status: **SOURCE_REVIEW_COMPLETE / VISUAL_EQUIVALENCE_OPEN**. This review did not
create a payload or runtime result. The frozen hint source remains unchanged.
Full composition and production remain **BLOCKED**.

**2026-11-05 runtime follow-up:** the requested paired own1024×512/native
metadata capture [completed once on source51b9f26](../divider-color-snapshot/README.md#user-run--snapshot-and-manual-stop-pass-2026-11-05).
Own sRGB=true/TargetGamma0/force-linear=false/RT enum6/override2 and native
sRGB=false/TargetGamma1/force-linear=false/RT enum3/override2 are now observed,
along with own MID owner/Masked parent/SlateUI/effective parameters. Thus the
archive audit's latest-instance metadata gap below is **closed**, not an active
request for another capture. RHI pixel format/shader arithmetic/scene-color cause
remain unknown; different pipeline metadata alone is not a diagnosed error or
permission for a gamma/tint/material fix. This run also passed explicit STOP.

Subsequent [owned material A/B](ab/README.md) completed in-game: the same-pose
Masked/stock Translucent comparison showed no visible improvement; the probe is
disabled. Earlier source-only A/B planning sections below are historical, not an
active install request. The next bounded issue is fixed own-icon apparent size.

That step now has a separate [1.0×/1.5× size source candidate](size/README.md),
READY_SOURCE/NOT_INSTALLED. It changes only the owned Canvas slot, preserves
Masked/RT/scale/anchor/color settings and does not claim a color fix or adopt a
final product size. Existing material A/B remains completed.

## Color-pipeline audit — 2026-11-04 (source-only, no runtime writes)

**STATIC_CHAIN_REVIEW_COMPLETE / COLOR_CAUSE_UNPROVED / PATCH_BLOCKED.**
User authorized a bounded investigation of pale/haloed World UI after the
accepted `da830808912b38527fb5088a6543d6a070b5f3f7` style run. This section
updates the decision on the *latest* 1024x512 World component; older 512x128,
Masked/Translucent and size experiments remain historical and closed.
No game launch, installation, test payload, settings/save change or production
code change occurred. The separate divider-artwork task is out of scope.

### Engine and owner/writer cross-check

The below conclusions are source-contract level against
[public UE4.27 mirror](https://github.com/AlexMercer-MA/UnrealEngine-4.27/tree/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e),
**not a proof** of exact engine bytes or cooked material graph in the installed
Asterigos Steam 1.09 host.

| Stage | Established source behavior | What it does *not* prove |
| --- | --- | --- |
| Native Screen `SRetainerWidget` | `UpdateWidgetRenderer` explicitly writes gamma-space; retainer RT is `RTF_RGBA8_SRGB`, with `TargetGamma=1` and `SRGB=false` in that branch; final SRetainer paint uses `PreMultipliedAlpha | NoGamma`. [SRetainerWidget.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/SRetainerWidget.cpp) | Does not mean that borrowing the final MID into our own Image yields pixel-equivalent RGB/alpha after a second render. |
| Our own UMG | [Current composition](../live-editor-style/Scripts/IIPComposition.lua) builds own TextBlocks, ornament Image, read-only borrowed native hint Image. RGB-only brightness is applied to owned children, alpha kept separately; upper shadow is explicitly disabled and lower outline is optionally black. | No evidence of accidental extra text glow, nor independent ability to change halo without reducing glyph RGB. |
| World `UWidgetComponent` target | [WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp) constructor defaults `bApplyGammaCorrection=false`, `Masked`, transparent background. On *initial allocation*, `UpdateRenderTarget` uses Slate's recommended format with `InitCustomFormat(size, format, false)`; the renderer is constructed from the gamma flag. [Current source](../live-editor-style/Scripts/IIPWorldChild.lua) sets draw size1024x512 before registration and does not explicitly override gamma or the RT format. | The **actual** own RT `SRGB`, `bForceLinearGamma`, `TargetGamma`, `GetFormat`/`RenderTargetFormat`, clear, and Slate recommended pixel format have not been captured together at runtime. `false` is the InitCustomFormat force-linear argument; it is **not** proof of any final sampled gamma exponent. |
| World material/MID | The source explicitly selects `Widget3DPassThrough_Masked`, verifies stock masked/two-sided, depth test enabled and component-owned MID. UE4.27 `UpdateMaterialInstanceParameters` sets `SlateUI`, `TintColorAndOpacity`, `OpacityFromTexture`. [IIPWorldChild.lua](../live-editor-style/Scripts/IIPWorldChild.lua) | No reconstructed pixel-shader expression graph / exact premultiplied-alpha compensation. Changing the `BlendMode` enum without the effective material cannot solve that gap. Prior *real-game* stock Masked vs stock Translucent A/B produced no visible improvement. |
| Scene and display | UE4.27 [filmic tonemapper documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/color-grading-and-filmic-tonemapper?application_version=4.27) states that exposure/tonemapping can alter emissive colors and saturation; ordinary Screen UI and emissive World UI do not follow identical paths. | Not proof that scene exposure, bloom or temporal AA is causing this specific halo/washed-out F. |

Additional nuance: `FWidgetRenderer::CreateTargetFor` explicitly assigns
`SRGB`, `TargetGamma`, and a force-linear choice for its own factory
([WidgetRenderer.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/WidgetRenderer.cpp)).
`UWidgetComponent::UpdateRenderTarget` **does not call that factory**; copying
its settings into our World target without source/runtime evidence would be an
unsupported fix. The engine has a separate branch for reallocating an existing
RT (`PF_B8G8R8A8`), but the accepted style candidate allocates the1024x512
component before registration; no RT reallocation or format switch has been
observed in that session. This branch is **not** a diagnosed bug.

### Decision and cheapest next discriminating evidence

**Follow-up completed:** the [local archive audit below](#local-archive-audit--2026-11-04-read-only)
recovers actual October values, but not the accepted Style instance's RT/MID
readback. The proposed archive inspection is no longer pending; only the
separately authorized live metadata capture remains a possible next step.

**Do not** change `ApplyGammaCorrection`, `SRGB`, `TargetGamma`,
`bForceLinearGamma`, `Tint`, `OpacityFromTexture`, outer material,
global bloom/exposure or post-process by trial and error; do not repeat the
finished Masked-vs-Translucent test. A production change is **BLOCKED**:
final color writer/consumer and the Asterigos-specific pixel values/material
graph remain insufficiently evidenced.

The next sufficient **read-only** step is for user-started local Codex, only
if/when proceeding: recover the actual worktree and accepted local archives;
first inspect previously captured logs/UHT declarations/cooked material exports
without running the host. Extract a concise, non-proprietary field/value matrix
for the *own* World RT (`SRGB`, force-linear, target gamma, pixel/RT format,
clear color), World component gamma, effective material parent/parameters,
and native source-retainer target (to the extent already recorded).
Distinguish values genuinely observed from constructor/source defaults; do
not invent absent UHT getters, reconstruct proprietary shader assets or
commit raw host exports. If essential runtime fields remain unavailable,
report that blocker and propose **one** separately authorized, bounded
read-only metadata capture rather than building a new renderer/A-B harness.

Only if these values establish a plausible local conversion mismatch should
a minimal *owned-component* research A/B candidate be considered; otherwise
the remaining candidate is scene HDR/tonemapping/Emissive or unknown material
sampling, whose correction has a materially larger cost. Natural Hilda
occlusion, original TipHUD/native hints, clean ownership and the accepted
research prototype remain preserved. The divider texture/mipmap work remains
a separate task.

## Local archive audit — 2026-11-04 (read-only)

**ARCHIVE_REVIEW_COMPLETE / LATEST_RT_READBACK_MISSING / PATCH_BLOCKED.**
Question: do already retained values establish a concrete color conversion
conflict that permits a minimal owned-component correction? **No.** Actual
October metadata is recoverable, including gamma/tint/clear values; the accepted
November Style run did not capture the equivalent own RT/MID snapshot. Distinct
Screen/World settings are not by themselves an erroneous conversion.

Evidence keys (all raw inputs remain ignored/private):

- **S**: accepted source `da830808912b38527fb5088a6543d6a070b5f3f7`,
  `world-space/live-editor-style/runtime-20261104T160838Z/UE4SS-runtime.log` under
  `.local/research/interaction-prompts/`; lines781/829 (native source),820
  (own creation),1272/1443 (explicit settings). SHA256
  `f9928b5c4f697fab6ece7211140b16beeff09d1d282bcad653056b3fe4f52d95`.
- **A**: [completed A/B](ab/README.md), source
  `caf955fb271558df1ddd5c991cf5b53217da2ef4`,
  `world-space/hint-mirror/ab/runtime-20261030T070257Z/UE4SS.log`, lines795/799.
  SHA256 `2acdb0b32027fbb2ad8a0c0f047f9dbb86c518e0bb3b766c9d412b000a43b119`.
- **Z**: [completed size test](size/README.md),
  `world-space/hint-mirror/size/runtime-20261030T083457Z/UE4SS.log`, lines794/798.
  SHA256 `f37f4a6193de9b43e0662abea33bd6e5ea6889d217ebac2518b6bfb6ebfad72e`.
- **U**: installed `uht-run/UHTHeaderDump` declarations, specifically Engine
  `Texture.h`, `TextureRenderTarget.h`, `TextureRenderTarget2D.h`,
  `ETextureRenderTargetFormat.h`, `MaterialInstance{,Dynamic}.h` and UMG
  `WidgetComponent.h`. Declarations establish fields/signatures, not instance
  values; generated `.cpp` constructors/stub methods are not engine execution.
- **C/E**: existing cooked `world-space/materials/Widget3DPassThrough{,_Masked}.json`
  and the pinned UE4.27 source files listed below. All12 entries in the existing
  `visual-fidelity/source-hashes.json` match, including those cooked exports.
  This authenticates the saved inputs, not their shader completeness or engine
  byte identity. All nine Style Lua files still match the accepted source.

| Parameter | Established value | Evidence | Unknown / applicability limit |
| --- | --- | --- | --- |
| Own RT `sRGB` (reflected spelling; engine `SRGB`) | **true observed** on512×128 | A795/799; Z794/798 | No value for Style1024×512. |
| Own RT `TargetGamma` / `bForceLinearGamma` | **0 / false observed** | A; Z | Style values and resource-effective display gamma not captured;0 is not a measured gamma exponent. |
| Own RT format | **RenderTargetFormat=6**, `RTF_RGBA16f`, observed enum field | A; Z; U enum | No captured `OverrideFormat`, `GetFormat()` result, Slate recommended pixel format or RHI format. Do not call this an observed HDR/float target. |
| Own RT clear / component background | **RGBA(0,0,0,0)** observed | A; Z | Style not read back; UE source transparent default is not its measurement. |
| Component gamma / material mode | **bApplyGammaCorrection=false**, World0, Masked1, two-sided, depth-disable=false | A; Z; S creation guards in [IIPWorldChild.lua](../live-editor-style/Scripts/IIPWorldChild.lua) | S proves configured World/Masked/two-sided/depth contract at creation; gamma=false is only the unchanged source/CDO expectation for S. |
| Effective own MID / texture | A: component-owned MID parent Masked, then Translucent; Z: Masked; **SlateUI equals own RT** | A/Z sample assertions and logs | S explicitly installs Masked, but no effective MID parent/SlateUI readback was logged. |
| Component / effective MID parameters | **TintColorAndOpacity=(1,1,1,1)**, **OpacityFromTexture=1**, effective **BackColor=(0,0,0,0)** | A; Z; C cached defaults independently agree | Actual S component/MID parameters unknown. Cooked SlateUI default WhiteSquareTexture is not the live binding. |
| Own child tint / opacity | A/Z Image white, Image/host RenderOpacity1; S last logged RGB brightness **.7/.4/1/.5** (upper/lower/divider/hint), divider alpha1 | A; Z; S1443; [composition source](../live-editor-style/Scripts/IIPComposition.lua) | S settings are intentional per-child dimming, not a measured outer MID tint or diagnosis of the original pale/blue symptom. |
| Native Retainer Icon RT / material | **51×51**, **force-linear=false**, **RenderTargetFormat=3=RTF_RGBA8_SRGB**, **MID blend5=AlphaComposite**; retained=true/global1 | S781/829; A; Z; U enum | Native instance `sRGB`, `TargetGamma`, clear, override/RHI format and pixels were not recorded. |
| Native Retainer gamma contract | Source explicitly selects gamma-space renderer; update branch assigns **SRGB=false, TargetGamma=1**; transparent clear; final NoGamma/PreMultipliedAlpha | E: SRetainerWidget130–171,570–590 | Source-contract values, not observed native fields. The different own values do not prove an extra/missing conversion. |
| Cooked outer shader | Masked MIC overrides blend/two-sided; parent Unlit/Emissive; cached parameters match names above | C; A/Z depth-disable=false readback | Expression name `MaterialExpressionMultiply_6`, empty resource list and null expression pointer do not reveal sampling, unpremultiplication or gamma arithmetic. Effective clip threshold remains unmeasured. |

**Coverage check:** S has zero `IIP_WORLD_HINT event=STATE`, `rt_srgb=`,
`rt_linear=`, `rt_gamma=`, `rt_clear=` or `effective_tint=` records. Its42
`linear_gamma=false rt_format=3` records belong to **native Icon**, not own RT.
Creation logs report draw1024×512; they are not a post-allocation RT-field read.
Older512×128 A/Z snapshots corroborate one another but cannot fill those gaps.

**UE4.27 interpretation:** the saved WidgetComponent source initially calls
`InitCustomFormat(..., GetSlateRecommendedColorFormat(), false)` and binds the
result to SlateUI; its resize/clear-change branch explicitly uses PF_B8G8R8A8.
It does not call `FWidgetRenderer::CreateTargetFor`. Thus the enum6 readback
cannot identify the chosen pixel format, and copying the other factory's gamma
settings is unsupported. Native Retainer gamma-space paint, own renderer gamma
flag and RT texture encoding are separate boundaries. The known Masked coverage
difference and completed negative Translucent A/B do not diagnose RGB hue/halo.

**Decision:** no concrete erroneous color conversion or parameter value is
established. A minimal local fix remains **not justified**; gamma/tint/format/
material edits would be a new hypothesis. No executable code, installation,
game process, graphics settings, saves, foreign mod or source Retainer changed.
No new general host contract was discovered beyond already shared R-006/R-016
evidence; this instance/archive coverage belongs to this repository.

**Smallest missing check, not executed:** one separately authorized read-only
metadata snapshot of the exact Style component **after** its own RT exists,
paired with the native Retainer in the same visible state: component gamma,
background/tint/opacity, own/native `sRGB`, `TargetGamma`, force-linear,
RenderTargetFormat, **OverrideFormat**, clear/extent; effective MID Outer/Parent
and `K2_GetTextureParameterValue("SlateUI")`, vector TintColorAndOpacity/BackColor,
scalar OpacityFromTexture. U declares these fields/getters; A/Z already exercised
the getter route. U does **not** declare a reflected `GetFormat()` on this RT:
record only OverrideFormat/RenderTargetFormat if no independently verified
pixel-format inspection exists, leaving RHI format unknown. No invented getter,
new test mod, renderer, A/B or shader reconstruction is needed for this check.
The current prototype is disabled; such a live snapshot is outside this task's
authorization. Even a complete metadata snapshot only closes the metadata gap;
if it exposes no conflicting conversion, scene processing/material sampling
remain hypotheses rather than a reason to adjust another switch.

## Question and evidence boundary

The [partial runtime result](README.md) established a live game-owned hint source
and controller→keyboard **F** update. Small size, pale/bluish color and apparent
translucency are user observations, without a screenshot or pixel measurements.
The visibility guard ended that run after about 3.764s; its precise failing
predicate is unknown. This review does not reinterpret it as a rendering failure.

Documentation/precedent was checked before proposing a change. Epic
[UE-35531](https://issues.unrealengine.com/issue/UE-35531) concerns a Retainer
*inside* a World widget, unlike our borrowed Screen Retainer MID. Its affected
versions are 4.12.5/4.14/4.15. It is not a diagnosis for this UE4.27 topology.
Historical community gamma/power/tint and material-graph workarounds are not
accepted fixes here. Exact versioned source is more discriminating.

## Additional Epic precedent and next decision — 2026-10-30

These external references refine the **hypotheses**, not the accepted game evidence:

- [Epic UE-32520](https://issues.unrealengine.com/issue/UE-32520) explicitly attributes a Screen-versus-World widget color discrepancy to tone mapping. **Important version limit:** the issue affects UE4.12.3 and is marked Fixed in July 2016; it does not demonstrate that the same defect exists in the pinned Asterigos UE4.27 build.
- [Epic forum answer by Nick Darnell](https://forums.unrealengine.com/t/umg-3d-widget-color-problem/97035) (2017) independently explains that world-rendered widgets pass through the scene tone mapper. That is a pipeline distinction, not a diagnosis of our borrowed Retainer MID or a prescribed material adjustment.
- [Community World-space UMG report](https://forums.unrealengine.com/t/umg-element-as-widget-component-colors-are-washed-out-in-world-space/422677) (2018) describes an apparent size-dependent change in washed-out colors. It is anecdotal and does not prove that scale, texture filtering, antialiasing or tone mapping caused this project's appearance.
- [Epic UE4.27 post-process materials documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/post-process-materials?application_version=4.27) distinguishes before/after-tonemapping passes, discusses temporal AA jitter, and warns that inverse tone mapping is not an easy general solution. This does not authorize changing the game's post-process settings or installing a new post-process material.

**Post-A/B decision:** the own Masked→stock Translucent comparison [completed without visible improvement](ab/README.md). Keep the established Masked/occlusion baseline. The next independent test should **change only the own icon's fixed World-space extent** at one reference camera pose, against the original Screen hint, preserving source, depth material, RT512x128, component world scale/anchor, Yaw, tint, gamma, ownership and native cleanup. The earlier ~28×24 px figure is the projected **own slot**, not a measurement of the native hint or glyph pixels. Use a same-pose visual comparison for the original when its FGeometry is inaccessible; do not invent a native-size value or use a hard-coded target multiplier as acceptance. Evaluate edge/color visibility again at comparable *apparent* sizes. No distance-dependent scaling, shader changes, gamma/power compensation or post-process installation at this stage. If blue/pale appearance persists, distinguish scene tone mapping, RT sampling/color conventions and small-pixel filtering with a separately bounded evidence gate rather than assuming which one is responsible.

## Actual image path

| Boundary | Established fact | Remaining uncertainty |
| --- | --- | --- |
| Game child → Screen Retainer | Runtime retained/global mode active; logical slot38×38; Icon RT51×51, format3=RTF_RGBA8_SRGB, force-linear=false. Source UI MID blend5=AlphaComposite. | Fresh pixel contents and exact screen rectangle/DPI were not captured. |
| Screen Retainer → final material paint | UE4.27 SRetainerWidget paints final effect material with PreMultipliedAlpha and NoGamma, premultiplying its style tint. | Actual shader outputs are not equivalent to knowing a texture pointer. |
| Same MID → own UImage → own RT | Same existing MID/RT, white own Image color; no second Retainer or source parameter writes. The UI material selects AlphaComposite blend state itself. | Own RT contents, actual gamma/contrast and complete effective tint chain were not captured after rendering. |
| Own RT → World mesh | Explicit stock Widget3DPassThrough_Masked override, component Masked1, two-sided, scale0.25, DrawSize512×128. Stock base depth test enabled; earlier World occlusion acceptance stands. | Cooked export lacks the complete shader expression graph; precise RGB/alpha conversion at this boundary is not proved. |
| World mesh → screen | Perspective and scene rendering replace native Screen placement/compositing. Base export is Unlit with Emissive output. | Final post-processing/exposure/tone mapping and measured pixels in this game run are unknown; unlit does not mean Screen color equivalence. |

### Alpha: one tempting diagnosis is ruled out

In UE4.27 `FSlateMaterialShaderPS::SetBlendState`, AlphaComposite chooses
`RGB: ONE, INV_SRC_ALPHA; A: ONE, INV_SRC_ALPHA` (premultiplied source).
`SlateRHIRenderingPolicy` calls that method for a material brush. Its separate
PreMultipliedAlpha draw-flag branch applies to non-material resources. Thus
normal UImage paint does **not** turn this MID into straight-alpha blending
merely because it lacks SRetainerWidget's explicit flag. Missing that flag is
not evidence of double multiplication at the own UImage material pass.

Retainer's tint treatment still differs for non-unit ancestor opacity. The
bounded source checks accepted unit source opacity and own color is white;
do not generalize to arbitrary fading ancestors. Preserve those guards.

The **outer Masked surface is a real mismatch**: it discards alpha below a clip
threshold rather than preserving continuous edge coverage. It can remove thin
features/soft edges and change perceived weight. It does not by itself explain
a blue hue or demonstrate smoothly increased transparency. The cooked instance
contains clip value0.3333 but no enabled clip override: this is not a measured
effective threshold for the parent shader.

Changing to stock Translucent is a justified comparison, **not a proved fix**.
AlphaComposite accumulation into a transparent RT generally stores associated
(premultiplied) RGB. If the outer material treats it as straight RGB, a further
SRC_ALPHA multiplication can darken edges. The cooked base export exposes
parameters and Emissive expression name, not enough graph to establish whether
it unpremultiplies. Do not promise equivalence from the MIC's blend enum alone.

### Gamma: do not blindly enable correction

`UWidgetComponent` defaults `bApplyGammaCorrection=false`; the frozen helper
does not write it. This is source-default evidence, not an actual logged value.
It is passed into FWidgetRenderer/Slate3DRenderer. The rendering policy then
uses DisplayGamma1 when gamma correction is disabled; NoGamma also selects1.
The material pixel shader skips its gamma conversion when inverse gamma is1.
Consequently, under that expected default, lacking NoGamma in own UImage does
not introduce a different gamma exponent at this paint stage. NoGamma also
forces contrast1; own material paint uses GSlateContrast, not measured in run.

Do not conflate these with the RT's texture encoding/sampling. SRetainerWidget
explicitly configures its own renderer and gamma-space target; WidgetComponent
creates its target with InitCustomFormat(..., false). The latter is not the
FWidgetRenderer::CreateTargetFor helper path. Actual own RT SRGB,
bForceLinearGamma, TargetGamma, format/clear color and final material parameters
remain to be recorded. Enabling correction, applying a power curve or tinting
against an unmeasured chain would add an uncalibrated conversion.

### Material selection: enum alone cannot correct the frozen override

UE4.27 `UWidgetComponent::GetMaterial(0)` prefers OverrideMaterials over BlendMode.
The frozen helper explicitly installs Masked. `SetBlendMode` only changes the
enum and dirties render state; it does not rebuild the material instance.
A future comparison must consistently set **own component Transparent2 and
explicit Widget3DPassThrough_Translucent**, before initial registration, with
readback of the effective MID parent. Both installed MICs share the same stock
base and depth-test-enabled configuration. Source Retainer, TipIconMat and Icon
must remain read-only. Translucent depth sorting/depth writes and interaction
with other translucent geometry still require their own visual boundary;
previous Masked occlusion PASS does not accept a changed outer material.

## Size: separate logical units, texture samples and screen pixels

Own38×38 slot × component0.25 = **9.5×9.5 world length units**. Source51×51 is
sampling resolution, not guaranteed displayed pixels. Native38×38 logical units
are affected by UI/DPI/geometry; 51/38 alone is not a proved screen scale.
World plane lies in local Y/Z with normal+X; accepted yaw rotates that plane,
while camera elevation still foreshortens a strictly vertical plane.

For a front-facing square of world height L at camera-space forward depth z:

`height_px ≈ viewport_height_px * L / (2 * z * tan(vertical_FOV / 2))`.

Use camera-space depth, not radial distance. For actual yaw/elevation, project
the four transformed icon corners and compare their screen rectangle to the
native hint's actual screen rectangle in the same viewport. Installed UHT
contains PlayerController.ProjectWorldLocationToScreen(FVector, FVector2D&,
bool) and WidgetLayoutLibrary.GetViewportScale(UObject*). These declarations
support a future measurement plan, not proof of a new Lua out-param helper.
No such helper or runtime code is prepared here.

The recorded radial distance623.112 alone cannot determine a correct multiplier:
viewport, FOV, orientation and native screen geometry are missing. Enlarging
DrawSize while leaving the icon slot38×38 does not generally enlarge the icon:
larger plane extent and smaller icon UV fraction cancel. Increasing RT samples
is not the same as increasing visible icon extent.

Recommend a **fixed own icon extent calibrated at one explicit reference pose**
after measuring the two rectangles. Keep anchor, component scale, yaw and render
target unchanged initially. This makes sizing reviewable without introducing
distance scaling. Fixed world size necessarily changes projected size with
distance; constant-pixel scaling would be a separate product choice, not an
implicit correction authorized by this review.

## Decision and one sufficient next experiment

The mechanism can be adjusted entirely on owned UI/component state; nothing
requires writing to the original Retainer/MID, settings or other mods. However,
the exact cause of pale/blue appearance is **not established**. Source analysis
establishes coverage and unit/projection mismatches and excludes the simplistic
missing-draw-flag/gamma-toggle explanations above.

**CORRECTION_PLAN_SUPPORTED / IMPLEMENTATION_NOT_PREPARED.** Preferred direction:
measure/project own extent; use a continuous-alpha, depth-tested outer surface
only after confirming its premultiplied-RGB handling. Stock Translucent is the
cheapest available comparator, not a commitment to a new cooked material or to
a final design. Preserve white tint and expected gamma=false meanwhile.

One separately prepared and authorized **fixed-pose material A/B** is sufficient
to decide whether stock Translucent is usable or an alpha-compatible own surface
is a remaining dependency:

1. One natural Open, original Screen hint visible, same glyph/device/camera pose
   and one owned component. Obtain actual source/own screen extents. If a larger
   diagnostic extent is needed, use the same measured extent for both samples.
2. Before comparing, capture actual own gamma flag, RT SRGB/force-linear/format/
   TargetGamma/clear, own tint/opacity, effective material parent/blend/depth and
   source identity. Record only available read-only contracts; do not invent
   getters. Capture a screenshot for each stable sample; no need for a new
   shader/texture readback infrastructure.
3. Compare Masked baseline with Transparent2 + stock Translucent on the owned
   surface. Use one-at-a-time owned recreation if needed so initial configuration
   is consistent, never two simultaneous renderers sharing the original widget.
   Freeze size, gamma, tint, anchor, yaw and source. Examine edges/holes separately
   from interior RGB and background leakage; compare the original in both shots.
4. If Translucent restores edges without a color/opacity defect, it is a candidate
   for visual acceptance, not production acceptance. If still faded/blue, stop:
   remaining gate is outer shader/RT color convention and scene processing,
   not another blind gamma/tint tweak. A/B alone cannot distinguish those causes.
5. Keep existing visibility/identity guards, timeout and F7 cleanup. Do not relax
   the original visibility guard or add reacquisition merely to prolong samples.
   A repeat guard stop is a distinct result; no automatic retry.

No executable probe is needed to finish this source-only task, and none was
created. The next experiment requires its own preparation/permission; it must
not silently overwrite/reinstall the frozen tested candidate.

## Exact sources and reproducibility

UE4.27 source cross-check uses mirror commit
`306a7e9f7fb53f14c2cb3bfd3854ad906710a17e`, not proof of byte-identical proprietary
Asterigos engine code. Installed UHT/cooked exports plus prior runtime evidence
bind the comparison to Steam1.09/UE4.27/UE4SS83330635. Relevant source locations:

- [WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp): mesh364–380; defaults608; UpdateMaterialInstance714; renderer884; RT1710–1755; SetBlendMode2038; GetMaterial2094.
- [SRetainerWidget.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/SRetainerWidget.cpp): renderer/RT130–171, final paint570–590.
- [SImage.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/SlateCore/Private/Widgets/Images/SImage.cpp): OnPaint tint/MakeBox.
- [SlateRHIRenderingPolicy.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/SlateRHIRenderer/Private/SlateRHIRenderingPolicy.cpp): gamma604–606, non-material blend823–828, material blend1093 and gamma1113–1115.
- [SlateMaterialShader.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/SlateRHIRenderer/Private/SlateMaterialShader.cpp): blend87–123, gamma uniforms136–140.
- [SlateElementPixelShader.usf](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Shaders/Private/SlateElementPixelShader.usf): contrast/GammaCorrect26–48.
- [WidgetRenderer.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/WidgetRenderer.cpp) and [Slate3DRenderer.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/SlateRHIRenderer/Private/Slate3DRenderer.cpp): renderer gamma propagation.
- Official [RetainerBox4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/RetainerBox?application_version=4.27) and [WidgetComponent4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/WidgetComponent?application_version=4.27): alpha/gamma contract, distinct Screen/World path.

Ignored local evidence: `.local/research/interaction-prompts/world-space/visual-fidelity/`
(source files and SHA256 manifest), `world-space/materials/` (installed cooked
material exports), `uht-run/UHTHeaderDump/` and the earlier hint runtime archive.
No proprietary graph/texture/dump is published. Cooked expression graph absence
is an explicit limit, not permission to infer shader arithmetic from its name.

Checks:188 changed-document local links resolve; git diff --check in both
repositories; source SHA256 manifest; all three frozen Lua hashes match the
published candidate; VERSION unchanged and documentation-only Git scope.
External sources are listed separately; this local-link check does not assert
availability of every historical external URL. No behavior changed; frozen Python suites were
not rerun just to enlarge a test count. No runtime/visual acceptance is inferred.
