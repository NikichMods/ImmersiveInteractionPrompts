# Native World editor for Quintus — source-only candidate

Baseline `ce64cbfee71ac0fa2ca5b41f3b8713d012f7fef0`. The experiment retains
the early World/NoCollision write, native TipHUD, and two own CanvasPanel_6
children from the [verified compact candidate](README.md#compact-successor-passed-the-bounded-run--2026-11-20).
Scale and lift are session values applied on BeginPlay and key events.
The one supported owner uses the original scale as the baseline and applies
only the difference from the last accepted lift. A failed transform
readback rolls the transform back to its value immediately before the key.
The editor does not consume game input. Closing it keeps the current
settings and writes measurements to the log.

## Keys

StaffRebalanceDev is active and already owns bare F4 and F7. Use bare F5
and F8 for this checkout. UE4SS registrations are checked before binding.
The game key resolver checks the existing keyboard action inventory on
each open. Raw polling from other editors is outside this audit. Keep the
HildaSoftLight editor closed while using this editor, since it also reads
NumPad. No persisted settings.

| Key | Action |
| --- | --- |
| F5 | Open or resume |
| F8 | Close and log final values |
| NumPad 8 / 2 | Lift / lower by 2 world units |
| NumPad + / − | Scale up / down by 0.025 |
| NumPad 7 / 9 | Log that the requested resolution preset is unavailable |
| NumPad 5 | Log current values and native renderer readback |
| NumPad 0 | Restore scale 0.65 and lift +38 |

Scale range 0.25–1.0, lift range 0–100. Only F5 acts outside editing.

## Resolution and sharpness

The exact shipped BaseGameEventObject SCS template has `DrawSize=1000×1000`.
Quintus inherits it. The export has no `bDrawAtDesiredSize` override
and the stock 4.27 constructor defaults it to false. These are asset/source
values. The accepted run only recorded that a RenderTarget existed.
NumPad 5 reads `GetDrawSize`, `GetCurrentDrawSize`, `bDrawAtDesiredSize`,
`RenderTarget.SizeX/SizeY` and the texture filter during the new run.

`OnRegister` initializes CurrentDrawSize and creates the renderer for
World. `SetDrawSize` stores integer dimensions and dirties render state.
On an eligible draw, fixed mode copies DrawSize to CurrentDrawSize,
desired-size mode derives it from Slate prepass, and the renderer allocates
or resizes the RT. Both branches render with `DrawScale=1`. The stock
scene proxy uses CurrentDrawSize for world geometry and material UVs.

Therefore Native is the sole supported preset. Multiplying DrawSize by
1.5 or 2 and inversely scaling the component would preserve the quad size
but shrink fixed-font glyphs and fixed-size slots in world space. Anchors
may also move. World RT resizing cannot supersample an already retained
input icon. The authored divider is a separate 256×32 PNG and sampling
changes cannot add source detail. Effective filtering and material
sampling may change edge appearance, but neither is evidence for a
sharper font raster at matched world size. This candidate reads dimensions
and filtering without writing DrawSize, RetainerBox, material or texture
settings. The high-resolution presets require a verified Slate scale and
logical layout contract for the intact TipHUD before implementation.
[UE4.27 registration and draw](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp#L1275)
· [Retainer and World material evidence](../hint-mirror/VISUAL_FIDELITY.md).

## Object scope

Talk at Quintus remains the only World target. The cooked
`0-1_plot_outerRimA_interact1` export (SHA-256
`c8fca3bfee13de734a0f8189a07c284cee584ec46f7729719d72c4a4b9a17b97`)
has three **placed** actors: Open `0-1_lootbox_01_mat_ST001`,
Take `0-1_item_loot_bag_03_AP1_3`, and Check `0-1_sosletter3_2`.
Each references its serialized `ExtendedWidget` export with
`RF_WasLoaded` and `CreationMethod=SimpleConstructionScript`, using
the same base template. This is a load/deserialize route, separate from
Quintus's dynamic SCS creation. The existing BeginPlay evidence is late.
Pinned UE4SS may queue notifications from other threads, so receipt of
a generic notification cannot authorize an early write for these objects.
They stay Screen. Two bounded event logs identify whether this exact
component was notified and whether it was Screen at BeginPlay. No write
is made. Readbacks from the next run would not themselves prove safe
pre-registration mutation for these placed objects.

## One next game test

After separate authorization to install, load the same Quintus save. Approach
him and press F5. Adjust lift and scale, log Native RT dimensions with
NumPad 5, and try NumPad 7/9 once to confirm safe refusal. Use NumPad 0
to compare against 0.65/+38. Press F8, then verify that NumPad changes
nothing until F5 opens the editor again. Leave the desired values and
press F8. Withdraw to check the whole native prompt hides. If the same
session reaches the three exact objects above, observe their normal
Screen prompts, then exit. The goal is adjust/reset/close/resume and
retained native behavior, plus one renderer measurement. Screen S1
and the current compact World installation remain active on disk.

## Prepared handoff — 2026-11-20

Source `fdb8842489356ad86380e3a426e28e10667297e6`. Local six-file
payload staged outside the loader. Entry SHA-256
`f1d8314f3535e5729c76a727ee62cad9a5aa6186b9928942e5ec5290861ff6e5`.
The extra dependency is the existing `world-reuse/Scripts/IIPKeyboardBindings.lua`
copied unchanged as `Scripts/IIPQuintusKeyboardBindings.lua`.
Lua compilation, loading both required modules and opening the verified
resource files passed. The predecessor and Screen S1 each matched
their full installed receipt before and after preparation. Rehearsed
replacement and rollback of the existing World folder on copies; both
manifests matched. Actual deployment still requires the closed-game
check and separate authorization.

Nine focused Lua mock scenarios passed, including entry/resume, ignored
keys while closed, preset refusal, reset, transform rollback, gameplay
and UE4SS key conflicts, tuning before spawn, read-only placed control,
and partial decoration cleanup. 63/64 repository suites passed. The
unchanged archived Resident World manifest test compares Windows path
separators to slash keys. All 17 entries and hashes matched after path
normalization. Game rendering, hotkey delivery and native RT dimensions
at sample remain pending. Production BLOCKED.

## Installed — 2026-11-20

The staged six-file payload for `fdb8842489356ad86380e3a426e28e10667297e6`
replaced the compact World candidate with the game closed. All installed
hashes matched the preparation receipt. The compact predecessor
`f0c9ca3491d5c6e41e4703708dff4c909eb29ba1` was moved to a verified rollback
directory outside the loader. The pretest UE4SS log and private installation
receipt were archived. Screen S1 remained active and matched its previous
five-file manifest. Runtime pending. Production BLOCKED.

## Runtime result and follow-up — 2026-11-20

Quintus, same save, UE4SS `83330635`, editor source `fdb8842`.
The log confirms two open/close cycles and preserved settings on resume.
The final `EDITOR_CLOSED` at 07:42:08.5521249 records **scale 0.300,
lift +36**, Native. The matching sample has DrawSize, CurrentDrawSize
and RT all 1000×1000, desired size false, filter enum 3, World,
NoCollision, visible, decorated, and no Screen-layer insertion. The
user accepted the appearance at the reduced scale and closed the
pixelation question. Keep these values for the next comparison. The
log has no preset refusal or placed-object events in this run.

The user reported that a held Talk input reached the dialogue but its
ring appeared late, jumped to about two-thirds and completed abruptly.
No time series was captured during the hold. The attached still confirms
a visible halo around the native action and the added Aphes line.
Source candidate and Screen S1 each matched their installed receipts
after exit and remain active.

Archived log SHA-256
`5c536de6cddf582b88d33a7fe942000859a8a83bdfc3e8091f4032758b9565e8`.
Screenshot SHA-256
`d5f93d9f13bf0e0ba115fbefffa9cb0d8e62907320ae27dbd6e54a687c9b20bf`.

### Hold-ring cadence

The shipped TipHUD Tick enters the ubergraph at 972. In its hold path,
`CanHoldPress` gates reading `GameGlobal:GetToDoInteractActionPressTimer`.
Offsets 497 and 534 transfer the timer's `outTimerRate` to parameter
`t` on `RetainerBox_0`'s effect MID. The final ring is a material effect
over the cached icon. UE4.27's Retainer phase schedules the cached
**child texture**. The final effect brush is emitted separately on outer
paint, so a phase tweak alone is an unsupported fix for a changing MID.

World additionally gates outer paint in `ShouldDrawWidget` by component
visibility, recent rendering, RedrawTime and manual redraw; the component
also has its own TickMode and tick interval. The engine and dumped class
defaults are RedrawTime=0, manual redraw false. The run did not capture
live values or cadence. 120 displayed FPS is a separate measurement.
First measure a bounded hold on the exact TipHUD: component redraw/tick
settings once, timestamps and native `t` during the hold, plus video of
the ring. If `t` itself arrives in steps, trace native Tick/timer delivery.
If `t` progresses smoothly while pixels lag, focus on World paint/RT
delivery and compare against the same Screen S1 input. Keep the hold
threshold, input and dialogue logic intact.
[UE4.27 World draw gate](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp#L1240)
· [Slate Retainer paint](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Slate/SRetainerWidget.cpp#L550).

### Halo

Scene bloom is consistent with the screenshot and the stock unlit,
emissive World material path. The still does not isolate bloom, exposure
or the native glyph/material contributions. The narrow reversible
experiment is a same-camera A/B on this component: read the effective
World MID and current tint, reduce only linear tint RGB through
`SetTintColorAndOpacity`, preserve alpha and restore the saved tint.
In UE4.27 the setter updates the component MID parameters in place. Test
whether the halo contracts while the button, caption and hold ring stay
readable. Keep the layout, material, Retainer and global post-processing
fixed for that comparison. This tests a local mitigation and does not
establish the halo's unique cause.
[UE4.27 component tint setter](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp#L2071)
· [Epic bloom documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/bloom?application_version=4.27).

## Hold and tint successor — source-only

The successor starts at the accepted 0.300 / +36 / Native. Inside the
F5 editor, NumPad 4/6 decreases/increases the component's linear RGB
multiplier by 0.10 (range 0.25–1.00). Alpha is preserved. The change
is verified against the component and its live World MID. A rejected
write restores the preceding tint. NumPad 0 restores tint and placement.
F8 logs the values and closes editing for the session.

Record a short video from the same camera angle. With the visible Talk
prompt, press NumPad 1 and immediately hold the native action. It samples
the game's timer rate and native MID parameter `t` every requested 16 ms
for at most 3.5 seconds or 180 samples, ending early when the prompt hides.
The log timestamps use world real time. A second hold with NumPad 3
temporarily removes positive component redraw/tick intervals and manual
redraw, if present. The original values are restored on completion or
failure if the same component is still available and the temporary values
are still in place. If the existing settings are already continuous,
`changed=false` means this trial made no timing change. It does not override
visibility or the game's input, progress material or hold threshold.
Compare both holds with the same RGB and position. Then try RGB 0.8 and
0.6 from the reference camera, watching both the halo and ring contrast.

The diagnostic reads the exact Quintus widget and retainer MID. It logs
changes and periodic heartbeats rather than generating an independent
progress value. UE4SS scalar out parameters use their property names as
table keys in this pinned build.
[Pinned UE4SS out-parameter binding](https://github.com/UE4SS-RE/RE-UE4SS/blob/8333063595fa3c49ad307f3b0f732accbb760d25/UE4SS/src/LuaType/LuaUObject.cpp#L288).

Prepared source `16f3c7f5847bc1917012129277582741b7fc7ee9`. The local
seven-file payload and verified predecessor were exercised on copies
outside the loader, including rollback. Main Lua SHA-256
`9bf6a2074e3c651c8b4d91fea3ea91f67fe697967bc888a682db002ed87f0071`;
probe Lua SHA-256
`7d0ac685e7bc9f3566916b6e5db8a199799e452be80158617404fc050d5bf6d1`.
The focused probe passed with mocked timer/MID reads, RGB/alpha,
baseline recording, temporary redraw settings, restoration and
default no-op. All other suites except the unchanged Windows path
issue in the archived Resident World test passed, 64/65 overall.
All 17 archived hashes matched after path normalization.
The existing editor and Screen S1 installed receipts still match.
Separate installation authorization is pending, followed by runtime
verification of both hypotheses. Production BLOCKED.

### Hold and tint successor installed — 2026-11-20

With the game closed, the staged seven-file payload for `16f3c7f5847bc`
replaced the World editor. The installed hashes matched the staged
manifest, and Screen S1 matched its complete previous receipt.
The preceding editor `fdb884248935` matched its full receipt after
being moved outside the loader. The private installation receipt and
pretest log snapshot are archived. Runtime verification pending.

### Hold and tint runtime result — 2026-11-20

The user accepted the smoother ring with NumPad 3 and the dimmed prompt.
At the last `EDITOR_CLOSED` the log records scale 0.300, lift +36, linear
RGB multiplier 0.35, Native. The supplied still shows the original
`Y Поговорить` with Aphes and divider at the dimmed appearance.

The exact component reported `RedrawTime=0`, manual redraw false, enabled
tick mode and **component tick interval 0.200 s**. NumPad 3 temporarily
changed only the positive interval to zero, then restored it in both
trials. With the original interval, at 555 ms into the recording the
timer reported 0.6667 while material `t` still reported 0.0556. At 589 ms
the material jumped to 0.7222. Across 14 positive-rate samples there
were two distinct values of `t`. With zero interval, `t` matched the
timer to logged precision in all 53 positive-rate samples across both
trials. The user observed a smooth visible fill. This isolates the
component tick interval as the effective lever for this run. It does
not measure the exact presented frame for every sample.

For the next Quintus iteration, validate `SetComponentTickInterval(0)`
on the exact World component during normal use, outside the timed
probe. Carry forward 0.35 RGB and 0.300 / +36 as the proven starting
appearance. Keep live scale adjustment and explicitly test increasing
it from 0.300. The installed source still binds NumPad +/− in the F5
editor, but this log has no accepted scale change in the hold/tint run.

Source `16f3c7f5847bc1917012129277582741b7fc7ee9`, UE4SS `83330635`.
World and Screen S1 inventories matched their complete installed
receipts after exit. No new payload was installed. Production BLOCKED.

Archived log SHA-256
`25154923773eee762535c6c1a239e046f2dd373cc43c6e59529610b7f5c29751`.
Screenshot SHA-256
`cb920f06547598b456a718b0b5fa87029d61a273af3240d30dc30812d9b4c227`.

### Final scale selected — 2026-11-20

The repeat run on installed source `16f3c7f5847bc` confirmed live scale
adjustment. At 08:16:10 the transform read back scale 0.375 and zero
height delta. The last successful F8 close at 08:16:16 logged **0.375**,
lift +36, RGB 0.35 and Native, with the original visible World TipHUD
and 1000×1000 RT. The user selected this scale for the next iteration.
The source default and editor reset now use 0.375. The installed payload
was left as it was.

One subsequent F5 at 08:16:52 encountered the existing
`component or Quintus identity changed` guard. There was no later
applied scale value. The guard does not identify which object changed.
The archived log SHA-256 is
`1193ac03617a8294bcbb80b8729d9945c43b8bd0d28bce2b4c8bd1c9da822b2c`.

## Normal-use defaults and hold cadence — source-only successor, 2026-11-20

The selected research defaults for Quintus are **scale 0.375**, **lift +36**,
**linear RGB multiplier 0.35** and native 1000×1000 DrawSize. NumPad 0 resets
to the same values. The existing editor uses F5/F8 because StaffRebalanceDev
already owns F4/F7 in this installation.

The previous exact game run observed a component tick interval of **0.200 s**
and jerky hold-ring updates. Temporarily setting that interval to zero aligned
the native MID parameter with the game timer in 53 positive-rate samples and
the user observed smooth filling. The successor applies the same
SetComponentTickInterval(0) once at Quintus BeginPlayPost, checks readback and
logs TICK_CONTINUOUS. It does not touch the native timer, input, material
progress value, RetainerBox settings, interaction selection or show/hide.
The ordinary-use result without the diagnostic interval override still
requires game verification.

After an F5 recurrence, the combined identity assertion reported a mismatch
but did not identify the changed object. The successor retains each strict
predicate in the same order while reporting the first failing condition
(identity:component_* or identity:owner_*). This is a bounded diagnostic, not
a lifecycle fix; no automatic owner or component rebinding is added.

The change is **source-only**. No installation, game launch, saved-game or
settings changes, other-mod edits or Screen S1 changes were made. One
separately authorized normal-game run is sufficient to assess initial tint,
size and continuous hold-ring behavior. If the identity failure recurs,
preserve the first diagnostic rather than guessing the cause.
Production BLOCKED.
