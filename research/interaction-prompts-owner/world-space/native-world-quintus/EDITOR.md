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
