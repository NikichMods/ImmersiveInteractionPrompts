# World hint visual fidelity — source review, 2026-10-30

Status: **SOURCE_REVIEW_COMPLETE / VISUAL_EQUIVALENCE_OPEN**. This review did not
create a payload or runtime result. The frozen hint source remains unchanged.
Full composition and production remain **BLOCKED**.

Subsequent source-only step: [separate A/B candidate](ab/README.md) is prepared,
not installed. The historical plan below is superseded only by that narrow
implementation contract; it does not establish new pixels or a corrected color.

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
- [Epic forum answer by Nick Darnell](https://forums.unrealengine.com/t/umg-3d-widget-color-problem/97035/2) (2017) independently explains that world-rendered widgets pass through the scene tone mapper. That is a pipeline distinction, not a diagnosis of our borrowed Retainer MID or a prescribed material adjustment.
- [Community World-space UMG report](https://forums.unrealengine.com/t/umg-element-as-widget-component-colors-are-washed-out-in-world-space/422677/2) (2018) describes an apparent size-dependent change in washed-out colors. It is anecdotal and does not prove that scale, texture filtering, antialiasing or tone mapping caused this project's appearance.
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
