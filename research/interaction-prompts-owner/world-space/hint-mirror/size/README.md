# Fixed own-hint size calibration — source candidate

**OWN_SIZE_1.0_TO_1.5_RUNTIME_PASS / MANUAL_F7_PASS / DISABLED**, 2026-10-30.
One independent research candidate, no production/VERSION changes.
Final composition, apparent-size acceptance and production remain **BLOCKED**.

## Decision and narrow seam

The [completed material A/B](../ab/README.md) found no visible improvement from
Masked→stock Translucent. Do not repeat it. This candidate keeps the established
Masked/depth/occlusion baseline and changes **only its own Image's CanvasPanelSlot
extent** once. Accepted Open binding, private host, live source, renderer,
vertical frame-Yaw and F7/native cleanup are reused, not independently retested.

Compare **1.0× and 1.5×** source logical dimensions: current38×38 becomes57×57.
There is no measured native Screen slot/glyph rectangle to derive an exact target
ratio from, so1.5 is a bounded diagnostic contrast, not a chosen product scale.
The earlier~28×24px was our projected geometric slot in one camera pose, not the
native size or painted F bounds. A different reference pose produces different
pixels; even at the same pose perspective need not make the projected bounding
box exactly1.5 times larger. Use real projected corners, not a distance formula.

Live SetSize is the least complex evidenced seam. A second component, render
transform scaling, component scale/DrawSize changes and dynamic distance scaling
are unnecessary and excluded. Source-only tests cannot prove actual Slate paint
or perceived improvement; the next evidence must be a user-operated visual pair.

## Exact contract and ownership

Installed UHT declares CanvasPanelSlot.SetSize(FVector2D) and GetSize() plus
GetAnchors/GetAlignment/GetPosition/GetAutoSize. Engine source cross-check is
[CanvasPanelSlot.cpp175–194](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/CanvasPanelSlot.cpp):
SetSize changes LayoutData.Offsets.Right/Bottom and forwards the whole offsets
value to the live Slate slot when present. GetSize reads that slot's OffsetAttr
when present, otherwise LayoutData. Left/Top, anchors and alignment are untouched
by this setter. The candidate retains the accepted equal centered anchors, so Right/Bottom
are interpreted as width/height in this verified layout. This mirror is a UE4.27 contract cross-check,
not a claim of byte-identical proprietary engine source.

Pinned [UE4SS LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
supports FVector2D input tables/finite numeric struct returns; that route already
ran in the existing hint binding and projection. SetSize/GetSize exact UFunctions
are checked during preparation, before allocation. No custom properties/offsets,
FGeometry guessing, new native ABI or native module.

Only an owned Image whose Outer/parent/slot identities match its private
WidgetTree/Canvas may be resized. WidgetComponent remains the native holder of
the private host/Slate tree. No wrapper is retained for the new diagnostic state:
factor, extents, view fingerprints and keys are numbers/strings/tables. Existing
native pending-kill/owner/visibility checks and component destruction remain.

### Persistence and containment

- `IIPHintSource` owns `state.multiplier`, initially1, changed once to1.5 before
  the live setter. Both ordinary SOURCE_BOUND sizing and explicit enlargement
  use a fresh `{X=native.X*factor,Y=native.Y*factor}` table. The original native
  dimensions/slot are never assigned through or mutated. Repeat SOURCE_BOUND
  after a legitimate device/MID/Icon/source-size change reapplies the current
  factor instead of resetting to1.0. There is no per-frame SetSize loop.
- Pair comparability still requires the same source key/generation and view
  between A and B. A source change there rejects the pair. Legitimate source
  changes **after** the pair retain1.5 subject to the existing eight-generation
  lifetime/visibility rules; this is separate from the same-glyph visual pair.
- Every source read verifies both planned sizes fit within510×126 logical units,
  leaving at least one unit per512×128 RT edge. Normal57×57 occupies Canvas
  bounds(227.5,35.5)–(284.5,92.5). Source heights above84 are rejected even if the
  original1.0 size would fit, rather than allowing the enlarged state to clip.
  No auto-resize of Canvas/component/RT is used as a fallback.
- Read back the live slot after every own size write. Periodic existing World
  validation also detects an unexpected reset of own extent. At both diagnostic
  captures validate centered anchors/alignment/position, auto-size=false,
  component pivot0.5, identity Image/root/host render transforms and the Canvas
  envelope. No clipping or center shift is asserted from pixels before testing;
  these checks establish the geometric containment conditions.
- The same component, own MID, material, RT, tint/opacity/gamma/background and
  source must survive the pair. **No live SetMaterial or BlendMode write** exists
  in the size path; the sole SetMaterial call is initial stock Masked setup.
  Component scale0.25, RT/DrawSize512×128, world anchor+32Z and frame-Yaw remain.
- F6 is consumed once; premature/repeated presses are inert. Native setter is
  bracketed by own_size_switch BEGIN/END. Failure, bad readback, pending-kill,
  guard violation, F7 or unchanged timeout uses the inherited cleanup. No retries,
  longer deadline, second frame loop or guard relaxation.

## Measurement and evidence boundary

Keep the [accepted projected-corner route](../ab/README.md): plane local points
`(0,-u,-v)` transformed by current fixed position/scale and vertical Yaw, then
PlayerController.ProjectWorldLocationToScreen with numeric FVector2D out table.
Two records include factor, native logical dimensions, actual own logical/world
extent, Canvas bounds, four viewport-pixel corners and bounding rectangle.
The same API projects the unchanged geometric slot center separately. A projected
bounding-box midpoint need not equal that center under perspective; do not
mistake that for an anchor shift.
Viewport size/view/source/RT/material/gamma/tint diagnostics are retained.

The native Screen slot is **not automatically measured**. Pinned ordinary Lua
FGeometry returns do not preserve opaque size/transform data; do not round-trip
an empty table into SlateBlueprintLibrary or infer source pixels from its38-unit
slot/51-texel RT. `source_screen_px=UNAVAILABLE` remains explicit. Compare the
visible native icon in the screenshots at a fixed pose; geometry footprint is
not painted glyph coverage. Screenshot/source pixels are not invented here.

## One future separately authorized test

The user subsequently authorized installation; see the exact record below.
Only this IIP probe is enabled. Four authored Lua only, no assets/font/PNG,
loader edits or release. The following steps are user-operated runtime.

1. Start/load normally. Ctrl+Alt+F8 once, then the one manual reload required by
   accepted BeginPlay acquisition. Approach one natural Open without using it.
2. Choose the camera pose **before A**, stop character/camera and keep keyboard
   input throughout the pair. With native and own icons visible, Ctrl+Alt+F8
   again, wait about half a second and take screenshot **A, 1.0×**.
3. Keep that pose. Ctrl+Alt+F6 **once**, wait half a second, screenshot **B, 1.5×**.
   Do not touch the mouse between A and B. F6 changes size, not material.
4. Judge own versus native visible icon size/readability, edge/alpha/color and
   whether the own icon remains centered/unclipped. A larger icon may look better
   without fixing the pale/blue color. Report those properties separately.
5. Ctrl+Alt+F7; own icon disappears while native prompt/control remain. Exit
   normally and provide the two frames/report; local logs are collected by agent.

If the existing guard stops early, report the incomplete pair; no automatic
reload/restart or longer deadline. Same view tolerances as the accepted material
pair:≤1 world unit/axis,≤0.2°/axis, FOV≤0.01°, unchanged viewport/player/camera.
The raw two poses remain logged; tolerances do not imply mathematically identical
view. Two frame boundaries/three callback settling is not a GPU fence. User
screenshots remain necessary for paint/readability/color acceptance.

Observation120s, bound World/Yaw45s, candidates8, init callbacks128, CanShow4096,
frame callbacks12000, source generations8, pose samples4 remain unchanged. New
diagnostic samples≤2 and explicit size changes≤1; normal bounded rebind sizing
is not an extra user switch. No independent re-test of accepted renderer/Yaw/
occlusion/source or material A/B is requested.

Expected new records: BASELINE_REQUESTED → SAMPLE mode=original multiplier=1 →
own_size_switch BEGIN/END + SIZE_APPLIED → SAMPLE mode=enlarged multiplier=1.5 →
PAIR_READY → inherited LOOP_CANCELLED / RELEASED / COMPONENT_DESTROYED / CLEANED.
PAIR_READY establishes comparable recorded state, not native Screen-size equality
or a color diagnosis. Clipping/visual benefit and runtime rebind persistence
remain unverified until the appropriate gameplay observation; offline tests
establish the rebind sizing policy, not native engine execution.

## Payload identity / checks

| File | SHA256 |
| --- | --- |
| `Scripts/main.lua` | `c8e94b6902651ac04cd0829afacc54d35f7e921b77339fc390386e3620cc63f2` |
| `Scripts/IIPWorldChild.lua` | `283c301f7cfbee5aa6f063afe06e483e8363f7476d7fcd73c4fe54033ccdc5d7` |
| `Scripts/IIPHintSource.lua` | `62bb1cfa307dc29a2232b9c53e86ea5ffa4ad215743e0b747818915aa8bcfd0c` |
| `Scripts/IIPHintSize.lua` | `d8f9a41b0f33515014e88ebbd0196d08fe50ae8a7fa2e63e451171a98f77342f` |

New source tree is independent; parent material/hint probes remain byte-frozen.
`tests/test_hint_size.py`:22 policy tests cover1.0→1.5, exact geometric corner
inputs, proportional and centered extents, rebind/device/MID/RT/source-size
persistence, clipping envelope/boundary, one switch, native setter/readback
failures, source/view/settings changes, cancellation/visibility/timeout/cleanup
and forbidden mutation scope. Full suite:275 tests/18 suites PASS. Local-link/whitespace/hash checks also pass. Mocks do not render UE/Slate or establish pixels.
Local source/UHT hashes stay ignored under hint-mirror/size/source-hashes.json
in the existing local research evidence root. No game assets are published.

## Authorized installation — 2026-10-30 11:21 Moscow

Installed exact source `9954b04828706820f94774a95f29cbb10f93629c` in the new
`ImmersiveInteractionPromptsWorldHintSizeProbe` loader directory. All four Lua
source/installed SHA256 values match the table above. The fifth file is empty
enabled.txt, SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Lua was copied byte-for-byte, not edited for installation. Target was absent.

Get-Process/CIM checks confirmed no Genesis/Asterigos process before mutation.
Pinned UE4SS.dll SHA256
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`
matched, existing log records83330635.16 prior IIP probes have no active marker
or mods.txt enablement. Only this new marker was enabled; mods.txt and current
CombatHUD/SoulsEnemyHUD bytes/enablement are unchanged.

Ignored archive `install-20261030T082145Z` under the local hint-mirror/size evidence
root holds all40 prior Mods files, loader DLL/settings/log and Genesis log,
four exact source copies, planned/verified manifests, installer and guarded
rollback. All44 existing mod/loader/log hashes and64 config/save hashes matched
after installation; all backup copies also matched. No settings/save content
was modified or restored. Rollback removes only five own expected files after
closed-game/path/hash checks, refuses changed/unknown files and does not recurse.
Install/rollback PowerShell parsing passed; rollback was not executed on the
live install. Independent post-install hashing confirmed all five files.

Agent did not launch/terminate game, hot reload or change old research payloads.
Runtime size/readability/color/rebind/cleanup acceptance was PENDING at handoff.

## Runtime result — 2026-10-30 11:30 Moscow

Exact installed source `9954b04828706820f94774a95f29cbb10f93629c`; all four Lua
hashes above remained unchanged. The user confirms visible enlargement by F6,
improved readability and closed game. Both supplied Steam JPEGs are2560×1440.
This accepts the narrow own-slot change/rendered enlargement and manual cleanup,
not a final product size, color match or complete lifecycle.

| Event, Moscow time | Technical result |
| --- | --- |
| 11:30:46.120 | SAMPLE original1.0; native source38×38, own slot38×38. |
| 11:30:49 | `20261030113049_1.jpg`, screenshot A/1.0×. |
| 11:30:55.453 | own_size_switch BEGIN → SIZE_APPLIED1.5, own slot57×57, original_writes0 → END. |
| 11:30:55.486 | SAMPLE enlarged1.5 and PAIR_READY; same source generation2/view/material/MID/component/RT/settings. |
| 11:31:00 | `20261030113100_1.jpg`, screenshot B/1.5×. |
| 11:31:06.751–.768 | F7 reason=user: LOOP_CANCELLED, hooks_remaining0, RELEASED, native COMPONENT_DESTROYED, CLEANED. |

### Measured pair and limits

| Own geometry | A1.0× | B1.5× |
| --- | --- | --- |
| Logical slot | 38×38 | 57×57 |
| World extent | 9.5×9.5 | 14.25×14.25 |
| Projected slot rectangle, px | 26.7949219×24.6033325 | 40.2382812×36.9034424 |
| Projected geometric center, px | 1264.46191,543.175842 | 1264.46191,543.175842 |
| Canvas bounds | (237,45)–(275,83) | (227.5,35.5)–(284.5,92.5) |

Both slots preserve aspect/center and fit within the unchanged512×128 own Canvas.
No geometric envelope/readback/transform guard failed; frames show the full own
symbol rather than an apparent clipped element. This is not a glyph-pixel mask
measurement or original Screen slot size. The source Screen size remains
UNAVAILABLE; same-pose comparison is visual only.

The recorded camera position/rotation/FOV75/viewport were identical across
captures. Native source38×38, borrowed MID/Icon/generation2, own component/MID/RT
identities and stock Masked1 stayed the same. World scale0.25, fixed anchor,
frame-Yaw, gamma=false, RT flags, white tint/unit opacity and background were
unchanged. User screenshots keep the native localized action and key hint visible.
The run logged1851 frame-Yaw writes, zero degeneracy, no FAILED records and no
cleanup-pending result; these counters are not a fresh FPS/performance benchmark.

SOURCE_BOUND device4→1 occurred **before** A and before enlargement. There was
**no SOURCE_BOUND after SIZE_APPLIED** in this run. Persistence of1.5 across a
later rebind therefore remains offline-policy-tested, **not runtime accepted**.
Do not claim the visual pair demonstrated remapping/controller coverage or
native behavior after a source-size/MID/texture replacement.

User observation: larger means more readable. Increasing further to about1.7×
or2× was mentioned **tentatively**; design will be discussed elsewhere. This is
a deferred design note, not adoption of a new scale or authorization to modify
the frozen1.5 candidate. No code/size/requirements change follows from that note.
Color causality and Screen color/alpha equivalence were not established; this
test changed no color/gamma/material setting and does not diagnose the blue tint.

### Archive and disabled state

Ignored archive `runtime-20261030T083457Z` holds full logs/event extract, original
JPEGs, installed Lua, marker copy, installed manifest, current-state hashes and
disable result. SHA256:

- UE4SS.log: `f37f4a6193de9b43e0662abea33bd6e5ea6889d217ebac2518b6bfb6ebfad72e`
- Genesis.log: `0009de7a33ba50f7cbe0254673719511147eb6f3d76c9dba28b82384748475de`
- A-1x.jpg: `0f98becfed6ee2a4c3d2a163a516eca409792b57c86cc75966aa2fad44f88157`
- B-1.5x.jpg: `2a5244232557dd145eef8634cc554d6598366acecc97a824e4c84a872a538f4f`

With game already closed (process/CIM checks), removed **only own enabled.txt**.
111 other current files and42 historical non-log mod/loader hashes preserved.
Old probes remain disabled; CombatHUD/SoulsEnemyHUD, settings/saves and Lua bytes
unchanged. No game launch/termination, hot reload, new payload or automatic retry.
Local links/archive hashes/Git scope checked; frozen executable tests were not
rerun for this result-only update. The requested technical stage is complete;
do not repeat the same1.0→1.5 pair or start a design/color experiment automatically.
