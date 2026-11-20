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
