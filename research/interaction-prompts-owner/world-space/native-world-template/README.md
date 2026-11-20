# One-shot shared SCS template World trial — source-only (2026-11-20)

**RESEARCH ONLY; NOT INSTALLED; PRODUCTION BLOCKED.**

Goal: test whether setting `Space=World` and `NoCollision` once
on the *original* `BaseGameEventObject_BP_C:ExtendedWidget_GEN_VARIABLE`
template **before** loading a placed level is inherited by native
`ExtendedWidget` on the three known placed `Open/Take/Check` actors.
This is *not* a general change to `Genesis.ExtendedWidgetComponent` CDO.

This template is known from cooked SCS exports; those data do **not**
prove that a component already serialized in a level will inherit the
in-memory override. The exact runtime `LoadAsset` result and template
identity are also unverified. No package, Blueprint or level asset is
modified on disk.

## Minimal candidate

`Scripts/main.lua` is a **separate replacement trial**, not an
additional enabled mod alongside the installed Quintus experiment.
It queues exactly one job on pinned UE4SS's game-thread EngineTick.
That job refuses to mutate anything if the exact known Open actor is
already loaded. It locates the known template or calls `LoadAsset`
for its owning Blueprint package once, verifies the template's exact
path and class, and writes only two template settings:
`Collision=NoCollision`, `Space=World`, with immediate readback.
On failure it attempts to restore the template; it never modifies
placed actors directly. No hooks into level-streaming delegates,
post-registration conversion, new WidgetComponent or World renderer,
per-frame scan, timer or per-instance reassertion.

**Blast radius:** if inheritance works, *every* subsequently created
or deserialized component using this specific shared template can
receive World and NoCollision. This includes unknown objects other
than the three known targets and can overlap the ordinary Quintus
test if run together. The experiment must be installed **instead of**
the current World mod with closed-game backup/rollback and tested
in only one controlled save. A successful common write is not
production authorization for global use.

A read-only `RegisterBeginPlayPostHook` logs the three already-known
placed actors if they load, and F5 samples their current original
component after it can render. Observations:

- `TEMPLATE_FOUND` / `TEMPLATE_WORLD`: read/write on the one
  SCS template succeeded, *not* proof of inheritance.
- `SKIP`: target already loaded, template missing/wrong, invalid
  baseline or no game thread; no World write.
- `PLACED_BEGIN action=Open|Take|Check space=0`: original placed
  component reads World by BeginPlay; still not proof of live RT.
- `PLACED_SAMPLE ... space=0 widget=true rt=true
  added_to_screen=false`: candidate native World infrastructure
  in the actual game; visual readability, render depth, location,
  native interactions and teardown require user observation.
- `space=1` after `TEMPLATE_WORLD`: inheritance did not occur
  on that observed loaded instance (or a later writer reset it).
  No arbitrary retry or class CDO fallback.

**Important:** accepted Quintus appearance defaults and native action,
localized text, remapping and show/hide remain requirements.
This trial tests renderer inheritance only; does not provide Aphes,
divider, layout tuning or fixes to world orientation and tick.
The original Screen S1 and unrelated mods must remain unchanged.

Local Codex may inspect the exact pinned installed runtime's
preexisting asset/cache state and installation paths when authorized
for a closed-game installation, but must not launch/terminate the
host or hot reload absent separate authorization. Exact source
and rollback manifests, observed game build, loader and installed
file checks are required before any runtime acceptance.

## Installation preflight — BLOCKED (2026-11-20)

Exact source `40b4939ed64e969a3d308ab2e2f2b99ca4599d99`, candidate
`Scripts/main.lua` SHA-256
`99af00acd55bc5cc1b85f4aa2cf59c89527a438d428a1c90c9d65a97f40a42ee`.
Six focused local mock tests passed.
[Full CI PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44769783016).

Asterigos and its Shipping process were running at the installation
check. The additional cold-load issue is independent of process state.
The candidate passes the package name
`/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP`
to `LoadAsset` if the template is not resident. Pinned UE4SS 83330635
passes that string to `GetAssetByObjectPath` with no package-name
conversion. The stock build 12996889 Asset Registry
(SHA-256 `9ba7a655f82877869145de2bc62c2fa76b392fd3d8e7ec67b6b9667784f1ac92`)
lists the corresponding object paths with suffixes
`.BaseGameEventObject_BP` and `.BaseGameEventObject_BP_C`.
The bare package string occurs as `PackageName`. There is no matching
`ObjectPath` for the current fallback argument. The mock accepts
that argument without modeling the real registry lookup.
[Pinned LoadAsset implementation](https://github.com/UE4SS-RE/RE-UE4SS/blob/8333063595fa3c49ad307f3b0f732accbb760d25/UE4SS/src/Mod/LuaMod.cpp#L3288).

The already-resident `StaticFindObject(TEMPLATE)` branch is separate.
Neither template lookup nor property inheritance was exercised in the
game. Before a cold trial, use a registry-verified generated-class
object path in a new exact candidate and exercise a mock with the
two distinct lookups. The exact candidate above was left untouched.

World `52c6035` and Screen S1 `8f1231d` matched all seven and five
files respectively and remain active. The external staged copy of
`52c6035` also matches its seven-file manifest. No replacement
transaction took place, so a rollback of this attempted deployment
was unnecessary. The game session and installed files were untouched.

## Corrected cold-load candidate installed (2026-11-20)

**INSTALLED**, source `5fd1f2fb1ccc3459d315c992d4ff074eeff0c035`.
The fallback now passes the registry-verified generated-class ObjectPath:
`/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C`.
The exact SCS subobject lookup remains in place after loading. The mock
accepts the class ObjectPath and models a lookup miss for the bare package
name, including the resulting skip without a template or actor write.
Seven local tests, staged Lua compilation and
[full CI](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44776623175)
passed.

With both Asterigos processes closed, the two-file Template payload
replaced the entire prior World directory in the existing loader slot.
Its SHA-256 manifest is
`334f26727e0deb4d0f8e0a9a6662981bbde9836ab182d5995f1d19a1a43e31bf`.

| Installed file | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `826e79f2a6b3e26b1aa16d71890a33c3ecd86ef61694afa7053d1e7872abba21` |
| `enabled.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The active Screen S1 inventory (5 files) and other mod, loader, pak,
save and settings inventories matched the preflight. The original
seven-file active `52c6035` directory was archived intact outside the
loader. The complete restoration was rehearsed on a copy and the
archived files rechecked after installation. The private deployment
receipt stores the resolved archive path. Closed-game rollback uses
`.local/install-native-world-template.py --rollback`.

For a single controlled run, start the game fresh and load the save with
the three selected placed objects. Press F5 with the relevant prompt
visible and exit normally. Collect `TEMPLATE_FOUND` and `TEMPLATE_WORLD`
or `SKIP`, then compare `PLACED_BEGIN` and `PLACED_SAMPLE` for
`Open/Take/Check`. Exact template lookup, inheritance and native
World RT remain runtime questions. No launch, hot reload or runtime
write was made during installation. Production BLOCKED.

## Placed World inheritance runtime result (2026-11-20)

One user-run session on `5fd1f2fb1ccc3459d315c992d4ff074eeff0c035`.
The installed Template (2 files) and Screen S1 (5 files) matched
their manifests after normal exit. The archived UE4SS 83330635 log
SHA-256 is `3c1eaa1a55c4488417155ceee403a6273e780b23ee7d04256fb4a592307ba3b8`.
The user's chest frame SHA-256 is
`0636bdcc18d5949d0bba9013756b510d4161378ad7147a6023ea4c2ac3478e4e`.
Both are retained privately.

`TEMPLATE_FOUND space=1 collision=1` at 20:07:25.2377030
was followed by `TEMPLATE_WORLD space=0 collision=0 write=one_shot`
at 20:07:25.2377531. The logs do not distinguish the already-resident
template path from the class-loading fallback. A successful template
lookup and write were observed.

| Exact placed action | BeginPlay space / collision / RT | F5 space / collision / RT |
| --- | --- | --- |
| Check | World / NoCollision / absent | World / NoCollision / present |
| Open | World / NoCollision / absent | World / NoCollision / present |
| Take | World / NoCollision / absent | World / NoCollision / present |

All samples passed the original component owner/path checks,
reported the native TipHUD, and had `added_to_screen=false`.
BeginPlay samples were at 20:13:48.692–.696, F5 at
20:14:41.672. With the single-template write and no per-instance
mutation, this is positive inheritance evidence for all three exact
placed objects and native World RenderTarget evidence at F5.

The user reports visible action prompts at the conduit, chest, note
and potion, appearing without noticeable delay. The chest screenshot
shows the native `F Открыть` in perspective. The conduit was outside
the three-object log allowlist, so its Space and RenderTarget are not
classified by the log. Frame-level latency, collision with gameplay
traces, actual interaction outcomes and broad shared-template coverage
were not verified by this handoff. Size and position may need adjustment.
The installed experiment was retained. Production BLOCKED.
