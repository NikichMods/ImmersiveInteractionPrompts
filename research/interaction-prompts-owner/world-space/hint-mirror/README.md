# Current native hint — partial runtime PASS, visual equivalence OPEN

2026-10-30. User-run partial result below; probe DISABLED. Native retained-source
binding/device update and guard cleanup ran. Final pixel/device-cycle acceptance
is incomplete. Full Aphes composition/automatic production lifecycle remain BLOCKED.
Reuse [vertical-yaw/F7](../vertical-yaw/README.md) and the accepted Open/host/World
renderer without repeating their independent investigations. Prior integration
[blocker and alternatives](../composition/README.md) remain the reason for this test.

## User-run result — 2026-10-30, partial PASS / visual gate OPEN

Exact source7c2aa07b7f33edcd22f69c95ddc1a03191b38da8; installed three Lua hashes
matched the frozen source values below after exit. User reports seeing the hint
change correctly from controller glyph to keyboard **F**, with a quick return
toward controller. User also reports a smaller, faded/semitransparent bluish
appearance, too small to judge precisely. No frame was supplied for this run.
Record these as observations, not measured RGB/alpha/size values or an accepted
visual match. Code does not select or hardcode F or reconstruct the keymap; the glyph comes
from the native source. No independent FKey/remapping query was logged. **User correction (2026-10-30):** the observed key was F, not U; U came from speech-to-text transcription. The log records input-device state, not the glyph letter.

| Moscow time | Technical evidence |
| --- | --- |
| 03:48:09.258 | Exact natural Open actor/component/TipHUD match, same validated actor class as earlier. |
| 03:48:09.282 | PREFLIGHT retained_mid, device4 (XboxController per installed enum), retained=true/global1/phase0-count1/on_phase=true/on_invalidation=false. Source ImageInteractAllowed, existing effect MID/Icon RT ready. Slot38x38, source Icon RT51x51, linear_gamma=false, rt_format3=RTF_RGBA8_SRGB, source_blend5=BLEND_AlphaComposite. |
| 03:48:09.291–.306 | Own component CREATED; pending→SOURCE_BOUND device4, borrowed resource readback passed. Initial match snapshot RENDER_PENDING; no later own-RT STATE snapshot was taken. |
| 03:48:10.856–.891 | SOURCE_PENDING generation2 device1 (KeyboardAndMouse), own hidden/old reference cleared, then SOURCE_BOUND. Retainer/child/brush/MID/texture identities and slot/RT metadata unchanged. |
| 03:48:13.055–.056 | Frame-context visibility guard failed: target no longer visible Screen Open. LOOP_CANCELLED handle3 reason=failure; hint SUMMARY227 source observations/2 generations/bound=true. Yaw226 frames/226 writes, no degeneracy, last error0.000003612deg. STOP CONTRACT_ERROR, matches1/poses1/show228/hooks_remaining0, cleanup queued. |
| 03:48:13.072 | RELEASED borrowed_resource_reference=false; native COMPONENT_DESTROYED, CLEANED reason=failure/own_widget_holder=false/own_component_alive=false. |
| 03:48:50.247 | Event loop end; no later probe events. |

The two source generations share MID2247658706304 and Icon RT2242862811392
(historical process identities, never selectors). Together with the user's glyph
observation this supports a **live retained native output reference**, not a
frozen F/key texture. It closes the normal existing-MID getter/bind/rebind/resource
release path for this one controller→keyboard transition. It does not prove a
complete keyboard→controller→keyboard cycle, every remapping/device, or final
retainer/pixel equivalence. The quick return is user-reported but no subsequent
device4 SOURCE_BOUND was captured before stop. There is no manual/user F7 STOP
in this run; earlier vertical-yaw F7 PASS stands and is not reopened.

Stop occurred about3.764s after creation, before45s timeout. The guard combines
source component bVisible/bAddedToScreen and TipHUD visibility/opacity/enabled;
which predicate changed and why is not recorded. Do not diagnose an input bug,
range exit, chest activation, or renderer failure from that symptom alone.
The terminal FAILED is this contract stop, not an established crash/material API
failure. Native guarded cleanup completed; no RELEASE/CLEANUP_PENDING event.

**Visual gate remains OPEN/BLOCKED for full composition:** current symbol update
was seen, but user could not resolve the small/faded/bluish appearance. Own slot
uses the source38x38 logical size; at fixed component scale.25 it spans9.5x9.5
world units. This is not the same coordinate system as38 Screen UI units or the
51x51 source RT. Without viewport/FOV/frame measurements, actual screen-pixel
size cannot be asserted. The observed smallness is consistent with differing
coordinate systems, not proof of a particular sizing defect.

Source uses AlphaComposite and RGBA8_SRGB; retained OnPaint has explicit
PreMultipliedAlpha|NoGamma, while own UImage has default paint flags and is drawn
through the accepted masked World renderer. This is a **concrete hypothesis seam**
for opacity/color differences, not a diagnosed cause. Own active-mode color was
white RGBA1 by source. No raw pixel comparison or causal toggle was captured.
Do not silently fix with tint/gamma/opacity/scale/material changes or declare the
appearance merely cosmetic and accepted. Full Aphes composition/production stay
BLOCKED. Next narrow engineering question is source-versus-own paint/alpha/gamma
and size equivalence, using this saved state; no new payload or repeat run is
prepared or authorized by recording the result. No need to repeat accepted
renderer/font/yaw/F7 mechanisms as independent experiments.

Ignored archive outside loader:
`.local/research/interaction-prompts/world-space/hint-mirror/runtime-20261030T005315Z/`.
UE4SS log SHA256 `28c4f19be610588b8eee0e5ee12f8757d6ec484773bca4b75da59f176e7e154e`;
Genesis log SHA256 `3832c69f83a80bb38b4111297fb7271a6e6fc294b24899d0ca726144d6d48249`.
Raw logs, filtered events, exact three installed Lua/manifest and disable record
saved. Game already closed. Removed only own enabled.txt; all35 baseline
mod/loader hashes match and91 current files retain hashes across disable (not
pre-play save equality). All IIP probes disabled; original installed source,
other mods/current settings/saves preserved. No agent launch/termination/hot reload.

## Authorized installation — 2026-10-30

User explicitly requested installation. Exact source commit
`7c2aa07b7f33edcd22f69c95ddc1a03191b38da8`; source and installed SHA256 match all
three values below, Lua unchanged. New own directory
`ImmersiveInteractionPromptsWorldHintProbe` contains Scripts/main.lua,
Scripts/IIPWorldChild.lua, Scripts/IIPHintSource.lua and empty enabled.txt.
Only this IIP probe enabled;14 older IIP directories retained disabled. mods.txt
unchanged; CombatHUD/SoulsEnemyHUD enabled as before.

Game processes absent before/after install. Steam build12996889 and UE4SS83330635
match baseline; DLL SHA256
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`.
29 historical mod/loader hashes match. All35 pre-existing current mod/loader files
and55 existing tracked config/save files retain hashes across installation.
No agent game launch/termination, hot reload, settings/save or other-mod write.
Production/VERSION unchanged; runtime source route/pixels/device still PENDING.

Ignored backup outside loader:
`.local/research/interaction-prompts/world-space/hint-mirror/install-20261030T004415Z/`.
Exact three Lua, initial-state/installed hashes, verified result, pretest UE4SS /
Genesis logs, loader settings/mods.txt copies and guarded rollback.ps1 retained.
Rollback validates closed game, exact own target and known file hashes before
removing only new own files/directories to restore prior absent state. Syntax
PASS; not executed. Installation identity is not visual/runtime acceptance.

## Selected mechanism, including the inactive case

Before own component allocation, inspect the exact selected TipHUD's WidgetTree /
RetainerBox_0 and one direct Image child. Native hierarchy/root/visibility/opacity,
CanvasSlot parent/content and16..96 logical-unit size are guarded; no global search.
Read the original owning GenesisPlayerController's GetNowInputControllerType
(enum1..5) without querying or changing keymaps. This is a change token/log field,
not a key→glyph mapping. Native source output supplies the current configured hint.

First read bRetainRender, TextureParameter, phase and live effect/texture state:

| Supported state | Own image operation | Refusal |
| --- | --- | --- |
| Retainer desire=true, global cvar1, phase0/count1/RenderOnPhase=true, Icon parameter, existing TipIconMat UI-domain MID and live TextureRenderTarget2D Icon | SetBrushFromMaterial on our own UImage, referencing that existing MID read-only. Native retainer alone owns parameter updates/render target painting. | Null/wrong MID/texture/parent, unsupported schedule, pending kill, hidden/faded source, size mismatch. No child fallback on this failure. |
| bRetainRender=false with unchanged supported global cvar1; one untransformed Image, non-RTL Texture2D Image brush | SetBrush(source child.Brush) value-copy and copy ColorAndOpacity to own Image each update. Native texture untouched; no SetBrushFromTexture residency writes. | Non-Texture2D/complex child/material/transform/RTL/inherited-tint path, missing brush or any unsupported shape. Not a universal fallback. |

GetConsoleVariableIntValue returns0 both for disabled and missing cvar. Additionally,
Shipping SRetainerWidget has no development cvar-change refresh delegate. This
probe supports the normal pinned global value1 only; missing/zero/change refuses,
rather than claiming to read private live Slate state from a potentially stale
cache. It never executes a console command or changes cvars. Positive retained
readiness requires both configuration and an existing nonempty Icon RT, evidence
that native painting has supplied a final texture; this is not a private
bEnableRetainedRendering accessor or proof of every subsequent pixel refresh.
Manual reload uses the accepted acquisition route, with the same observed global
mode at preparation and live sampling. Other runtime cvar histories are outside
this bounded test. Original Screen TipHUD stays visible and unmodified throughout.

## Exact contracts and ownership

Installed UHT: URetainerBox.GetEffectMaterial() const→UMaterialInstanceDynamic*;
UImage.SetBrushFromMaterial(UMaterialInterface*), SetBrush(const FSlateBrush&),
SetBrushResourceObject(UObject*); MID.K2_GetTextureParameterValue(FName)→UTexture*;
KismetSystemLibrary.GetConsoleVariableIntValue(FString)→int32; Widget.GetOwningPlayer()
→PlayerController; GenesisPlayerController.GetNowInputControllerType()→enum.
Expected source base is `/Game/MainContent/Template/UMG/TipIconMat.TipIconMat`,
MaterialDomain UI5. Texture `Icon` must be exact TextureRenderTarget2D, dimensions
1..1024, with readable gamma/format metadata. No custom ABI, offsets or native hooks.

Exact UE4.27 mirror revision306a7e9f7fb53f14c2cb3bfd3854ad906710a17e:

- [RetainerBox.cpp55ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/RetainerBox.cpp): GetEffectMaterial asks the live Slate object, returns null if absent; no creation or writer.
- [SRetainerWidget.cpp295ff/565ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/SRetainerWidget.cpp): getter returns existing DynamicEffect. OnPaint sets its Icon texture and uses PreMultipliedAlpha|NoGamma. A second Retainer with that MID would reuse it and become a second writer, so none is created. Global mode formula and Shipping delegate boundary at20ff/205ff/221ff.
- [MaterialInstanceDynamic.cpp194ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Materials/MaterialInstanceDynamic.cpp): K2 getter delegates to Super.GetTextureParameterValue and returns the existing texture; no setters or new resource.
- [Image.cpp241ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/Image.cpp): material setter changes only the recipient brush reference/Slate image. Our Image is native-initialized DrawAs Image3; it is the sole new content child of the private host Canvas. No GetDynamicMaterial call or material parameter write.
- [KismetSystemLibrary.cpp385ff](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/KismetSystemLibrary.cpp): cvar getter only FindConsoleVariable/GetInt;0 on missing with warning.

Pinned [LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
uses reflected parameter storage/object pushers; same-typed struct userdata input
uses CopyCompleteValue, not manual field reconstruction. Own Image.Brush storage
is checked distinct from child Brush in inactive mode. Shared material/texture
UObjects are intentionally borrowed through own native Brush.ResourceObject,
with no retained Lua wrappers across callbacks, roots or forced GC. Raw game
textures/materials/dumps stay local; no proprietary payload is distributed.

## Update, cancellation and cleanup

[main.lua](Scripts/main.lua) retains accepted BeginPlay+CanShow acquisition and
one-loop EngineTick/frame-yaw/F7 policy. [IIPWorldChild.lua](Scripts/IIPWorldChild.lua)
keeps RT512x128, scale.25, anchor+32Z, world position, depth material, camera yaw
and native component teardown. It replaces WORLD TEST with one own UImage at the
same canvas center; its slot matches source key size, no font/text/Aphes/ornament.
The private host's stock placeholder subtree remains collapsed. No original child,
TipHUD or Slate tree is passed to another renderer.

[IIPHintSource.lua](Scripts/IIPHintSource.lua) resolves/checks the live source each
frame, including source objects' native validity, exact owning Open (via unchanged
World guards), controller/device, retainer/MID/texture identities and flags. All
wrappers are local to the current call. One native validity endpoint/CDO pair is
resolved per source snapshot, rather than for every object in its ancestor chain;
at most8 ancestors are read. This adds per-frame read cost to accepted yaw;
performance is not measured and remains a user-runtime observation, not a promise.

On a source/device/size/MID/texture change, immediately hide our Image and clear
its old reference. Require three consecutive matching observations (two frame
boundaries), then re-resolve/bind the current source and show own Image again.
This settling interval is not proof of GPU freshness or correct original glyph;
comparison with the original remains essential. Same-MID retained output updates
through the native texture/parameters; only identity changes need brush rebinding.
Inactive child Brush is copied every frame so same-atlas UV/value changes are not
missed. No persistent sampling log: PREFLIGHT / SOURCE_PENDING / SOURCE_BOUND /
manual SAMPLE / final SUMMARY / failure / RELEASED only. Device switches are
logged automatically; no F8 is required while testing controller input.

Absent/invalid/unsupported source immediately hides/releases own content before
throwing to the existing fail-closed stop path; it never displays a stale fallback
F or restarts. Limits:8 source generations including the initial source, one own
component/creation attempt, existing8 Open candidates/128 init/4096 CanShow,
12000 frame updates/45s after creation/120s total, four pose snapshots maximum.
No asset loads for hint resources; only existing exact host/stock World-material
refresh behavior is inherited outside CanShow.

F7 sets intent before native work, cancels the exact owned frame-loop handle and
queues cleanup on EngineTick. Hide own host/Image; release only own brush reference,
detach own Image, SetWidget(nil), native K2_DestroyComponent and own host release.
Original MID/Icon remain game-owned. Native validity/identity guards support
partial-cleanup retry, including an already detached own Image. No immediate
GPU/native GC-free claim. Late ready callbacks become inert before object reads.

## Historical user scenario — partial outcome recorded above

The separately authorized closed-game installation above is ready for one user
run, with rollback saved and older IIP probes disabled:

1. Load the usual test save, Ctrl+Alt+F8 once, reload once, approach one natural
   Open without activating it. The original Screen prompt remains the reference.
   A small standalone icon should appear at the accepted World anchor; no text.
2. For about5s use keyboard/mouse. Compare actual symbol, cropping, transparency,
   color/outline with the original. No keymap assumption: it must match the game's
   currently configured Interact. Optional F8 once while still on keyboard.
3. Use the connected controller's camera/movement for about5s, remaining in Open
   range; do not press the Interact action. Compare both hints. **Do not press F8
   during this part**: that keyboard chord can switch the game's input device back.
   SOURCE_PENDING/BOUND capture the change automatically.
4. Return to keyboard/mouse for about5s and compare again, then Ctrl+Alt+F7 well
   before30s. Only own icon disappears; original prompt/control stays. Close
   normally/report appearance, transparency, device agreement, any blank/stale
   interval and F7 removal. An already remapped Interact is covered where available;
   settings are not changed specially. If absent, mark remapping coverage untested.

Technical review checks selected route/flags, device and MID/texture transitions,
bounded source count, source/own readbacks, user STOP/cancellation/RELEASED/native
CLEANED, no probe failure and no later updates. Compare actual pixels/user report;
resource readbacks alone are not visual PASS. Invalid source may refuse before
own component creation; record its exact gate rather than trying another method.
No repeating renderer/occlusion/font/yaw/F7 prerequisite studies as separate tests.

## Future user-operated test usability — preference recorded 2026-10-30

The user prefers free observation duration and input order whenever those do not
compromise safety or the tested assertion. The 5-second blocks and device order
in the historical scenario were recommended for traceable transitions, not
restrictions enforced on gameplay. Ctrl+Alt+F8/F7 are keyboard chords that can
change the game's active input-device indication during controller observation.
The 45-second bound, 120-second overall watchdog, source/pose/frame budgets and
strict visible-Open identity guards are real constraints of this research probe.
They protect bounded native ownership and evidence scope; extending only a timer
would not prevent the earlier visibility-guard stop. Preserve the frozen tested
probe. For later visually exploratory work, use a more flexible manual-stop
procedure where possible; if roaming across prompt targets is genuinely required,
assess the separate reacquisition/cleanup lifecycle before authoring a new
research-only candidate. Do not loosen fail-closed safety guards merely to avoid
user inconvenience.

## External UE4.27 documentation cross-check — 2026-10-30, source-only

Internet research supplied concrete comparison targets, **not** a diagnosis or new
runtime PASS:

- [Epic UE-35531](https://issues.unrealengine.com/issue/UE-35531) documents
  washed-out colors with a RetainerBox **inside** a 3D WidgetComponent versus a
  screen widget (marked Won't Fix; listed affected versions 4.12.5/4.14/4.15).
  That reproduction is not our topology: our World UImage borrows a game-owned
  *Screen* Retainer's existing MID; no second Retainer is created. It is evidence
  that color-space boundaries matter, **not** that this exact engine bug affects
  Asterigos/UE4.27.
- [Epic UE4.27 RetainerBox](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/RetainerBox?application_version=4.27)
  explicitly requires AlphaComposite/premultiplied-alpha handling for correct
  final transparency. Our observed source uses AlphaComposite and
  SRetainerWidget PreMultipliedAlpha|NoGamma, while the own widget uses normal
  UImage paint. Compare the real paint/blending chain, without modifying the
  game-owned Retainer/MID.
- [Epic UE4.27 WidgetComponent](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/WidgetComponent?application_version=4.27)
  documents World render-target-to-material behavior, BlendMode,
  apply_gamma_correction, DrawSize and displayed quad. Our frozen
  IIPWorldChild.lua selects stock `Widget3DPassThrough_Masked` and
  c.BlendMode==1 (Masked), not the source Retainer's AlphaComposite UI paint path.
  Check actual masked 3D material/target/bApplyGammaCorrection/tint state before
  treating gamma or alpha as the cause. Do not blindly flip gamma or blend mode.
- [Epic 4.27 Widget Components](https://dev.epicgames.com/documentation/ja-jp/unreal-engine/widget-components?application_version=4.27)
  distinguishes Screen from World mesh rendering. A 38x38 Slate slot at
  component scale 0.25 represents 9.5x9.5 world length units before perspective,
  **not** a guaranteed 38x38 screen-pixel glyph. Pixel equivalence additionally
  depends on camera distance, FOV, viewport and DPI/UI scale.
- [Community discussion](https://forums.unrealengine.com/t/ue4-17-retainer-box-is-washing-colors/405296)
  describes both gamma and blend-mode workarounds across engine versions;
  these are version-specific reports, not validated Asterigos fixes.

Next cheapest action: source-only comparison of the *specific* UE4.27
SRetainerWidget/own UImage/stock Widget3DPassThrough_Masked/WidgetComponent paint
and gamma path, plus correct size projection. Decide if a minimal isolated
research candidate is justified; if pixels or host material behavior remain
unprovable from code, use at most one narrowly targeted game comparison.
Keep current probe and accepted mechanisms frozen; no automatic install/run.

## Source review follow-up — 2026-10-30

Next separate [material A/B source candidate](ab/README.md): READY_SOURCE,
NOT_INSTALLED. Four Lua files; parent candidate remains frozen. Exact own slot
projection plus two screenshots; original Screen FGeometry measurement is not
available through the pinned ordinary Lua return path. No new runtime PASS.

[Visual fidelity analysis / exact sources / one proposed A/B](VISUAL_FIDELITY.md):
SOURCE_REVIEW_COMPLETE, visual equivalence OPEN. The material-brush path selects
AlphaComposite from the MID itself; missing UImage premultiplied draw flag does
not switch it to straight-alpha blending. Expected component gamma=false also
selects gamma1, like NoGamma at this paint stage; actual state remains unlogged.
Outer Masked coverage and perspective units are confirmed differences. Stock
Translucent is only a controlled comparator until outer RGB/alpha handling and
pixels are checked. No new payload or installation; frozen Lua unchanged.

## Remaining risks and evidence boundary

UImage does not reproduce SRetainerWidget's explicit paint draw flags, but that
alone is not an alpha/gamma diagnosis; the follow-up traces material-specific
blending. Outer RT/material/color/cropping and update ordering remain relevant.
Source RT existence/readback does not prove fresh pixels on each
device transition; one-frame/native-retainer latency or blank intervals must be
observed. If unsupported/broken, stop; do not compensate with gamma/material
changes in this test. Narrow phase/opacity/size/class gates can reject other
legitimate game states; that is a bounded negative result, not a universal verdict.
No remapping resolver, input hooks, original RequestRender/SetRetainRendering,
material/texture parameter setter, second Retainer or console setting writes.

## Offline checks / identity

`python tools/test.py`:232 tests/16 suites PASS;25 new hint groups exercise both
routes, device/MID/texture replacement, settling/hide/rebind, same-atlas Brush
refresh, missing resources/APIs, wrong material/domain/schedule/size/device,
source pending-kill/hide, source budget, timeout/late callback, F7 and partial
resource-release retry, detached image cleanup and absence of source mutators.
These mocks do not run native Slate/UMG, evaluate pixels, profile performance or
prove live controller/remapping behavior. Local source/UHT hash manifest stays
ignored at `.local/research/interaction-prompts/world-space/hint-mirror/source-hashes.json`.
Old accepted source, production/VERSION, installed probes/settings/saves unchanged;
Markdown links and whitespace checked. No game launch/termination/hot reload.

- SHA256 `IIPHintSource.lua`: `b49d814534b1df3eabb8a4cedc45f6fdf7b847284465224046a638a7e3d4a92d`
- SHA256 `IIPWorldChild.lua`: `e214651e937ac4241805d7db043e2080239dd9b1da3333ca49936b9358ed5cdc`
- SHA256 `main.lua`: `73e8205c4322cb6b78121b98195b3beda1825d3deaf95aa33eb30043e3e0be90`
