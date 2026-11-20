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

## Adopted direction: full Quintus visuals on shared native World (2026-11-20)

After the positive inheritance run, the user adopted this original
SCS-template mechanism for the ongoing visual integration. The next
candidate is to reproduce Quintus's accepted 0.400 scale, +36 UE global
Z lift, RGB×0.35, native 1000×1000 resolution, native hold cadence and
original TipHUD decorations. Separate gameplay/selection/hide preflight
is intentionally skipped as a development assumption, not marked tested.
Do not conflate general placement with Quintus's one verified anchor:
parent/WidgetLocator orientation and per-instance transform may vary.
Preserve original action text and input hint, and leave game show/hide
in control. This is not authorization for installation or release.

## Full Quintus appearance successor — SOURCE ONLY (2026-11-20)

**Source-only research candidate. NOT INSTALLED. NOT runtime-accepted.
Production BLOCKED.** The installed experiment remains the verified
two-file \`5fd1f2f\`, with Screen S1 unchanged. This entry supersedes
earlier assertions that the template inheritance mechanism is unproven;
they remain historical records of previous trials.

The successor retains the single cold-start SCS-template write for
\`Space=World\` and \`NoCollision\`, unchanged. For each **original**
World \`ExtendedWidget\` with reciprocal actor ownership and genuine
\`TipHUD_C\` at BeginPlay, it applies the *accepted Quintus appearance*
exactly once to that native component:

- Relative scale ×0.400 from the component's own current scale;
  world-space Z lift +36 UE from its native anchor. No change to
  anchor selection, world-space orientation, DrawSize or pivot.
- RGB linear ×0.35 to the original component tint, preserving alpha;
  prefer the verified component pre-MID seed and verify the original
  MID when naturally available on \`CanShow\`.
- Native \`1000×1000\` draw size/RT retained; no new World renderer.
- Native component interval zero at BeginPlay, and a guarded
  reset to zero on the native \`TipHUD_C:CanShow\` when Genesis
  has restored a positive interval, preserving the native hold timer.
- Two **transient children in the original TipHUD WidgetTree**,
  using the approved Quintus placement and font/asset binder:
  a test upper \`ACTION\` Aphes-font line and the authored braided
  divider. \`ACTION\` is NOT a verified Aphes translation.
  Both become HitTestInvisible; original localized action, button
  and hold RetainerBox are not copied, hidden or replaced.

There is **no separate rendered prompt, collision shape,
per-frame search, own input/visibility selection, or replicated
localization**. On unrelated actors, non-World/Screen components
or invalid native identity the style helper does nothing.
The general BeginPlayPost observation is event-driven; its
unproven blast radius is all original \`World/NoCollision\`
\`ExtendedWidget/TipHUD_C\` actor pairs, not just the three
known objects. This is explicitly research-only and not
production-safe without coverage checks.

The Aphes TTF is private and must remain outside public Git.
The authored PNG is \`assets/dividers/aphes_divider_256x32.png\`.
The committed \`IIPTemplateResources.lua\` is based on the earlier
proven local-resource binder and supports a single shared
transient PNG texture across several *original* TipHUD widgets;
font copies remain private per label. Installation must supply
\`Scripts/IIPLiveConfig.lua\` through the verified local path and
hash checks. Configuration failure must not create a custom UI
or fall back to unverified fonts. Screen S1 may still be active,
but this separate original-World visual hook must not act on
Screen-only TipHUDs.

**Not established by offline tests:** whether those visual edits
survive native placement/initialization for each placed actor,
whether +36 world Z is a good placement for chest/note/potion,
correct startup RGB in the MID, lifetime of shared imported
texture across changing maps, or smooth hold for every type.
The existing \`5fd1f2f\` runtime result establishes only World
inheritance; it does not establish these additional properties.

The user explicitly chooses to **assume** interaction, switching
and native show/hide are fine during this visual iteration, without
claiming a tested PASS. Full gameplay acceptance still applies
before release. Next meaningful handoff is one bounded, closed-game
installed candidate with verified rollback and one user visual run
on the three known objects, after separate permission. Do not
install on a running host or reuse an immutable numbered artifact.

## Full World appearance installed (2026-11-20)

**INSTALLED**, exact source `59cc569de1cc1f4354658145c843c1efe9a62166`.
The [last green CI](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44785806199)
was on `592207d`. The only subsequent Lua delta isolates failure of
initial native tick correction so decoration and tint still run.
An exact-source mock confirmed that failure path. The other delta
updates the repository entrypoint documentation.

Seven Template and five visual tests passed. The standard local
runner hit the existing Windows separator mismatch in the legacy
World source-manifest test. Its three cases passed with only the path
comparison normalized in memory. All 67 other suites passed on the
exact checkout, for 645 unittest cases across 68 suites. Staged Lua
compiled, the private TTF and PNG matched their known hashes, and
resource preflight also passed against the actual installed config.

The existing World loader slot was replaced with a seven-file payload
while both game processes were closed. Manifest SHA-256
`89b0256a1a9a00f62c8b8f8e55af7f86d16ce707ba3f2f5f466b7504c91983ac`.

| Installed file | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `84cd2954e57926e804dfc2c18c14356df6edcbf5e9e2d6fab73135d1606c32e9` |
| `Scripts/IIPTemplateProbe.lua` | `f32a663aa36a3490825d590a1d7a1c9da4d110e97e16a7e1fda636b4aa1f19af` |
| `Scripts/IIPTemplateResources.lua` | `8f9502f29fb05b4c1f8e1d561a6e63a583b5afb010babf5802b7b92b511eb1cc` |
| `Scripts/IIPTemplateStyle.lua` | `549a1ccc04c3824bbf2a53b155466c9b1c3042a004c5dc833a0b02d1762c1fab` |
| `Assets/aphes_divider_256x32.png` | `b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969` |
| `Scripts/IIPLiveConfig.lua` | `894f191e0d8d1beaaafd21c9e4265e2a623cd7b6028b979a2e67811d270d9978` |
| `enabled.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

All five active Screen S1 files and neighboring mod, loader, pak,
settings and save inventories matched preflight. The seven installed
files and the two previous active `5fd1f2f` files were independently
rehash-verified after deployment. The original `5fd1f2f` folder is
archived outside the loader, and full active restoration was rehearsed
on a copy. The private receipt holds the resolved archive location.
Closed-game rollback uses `.local/install-native-world-visual-59cc569.py
--rollback`.

Ready for one user visual run on the known chest, note and potion.
Check the complete original prompt, test header and divider in context,
alignment, size and brightness. Press F5 while the relevant prompt
is visible and exit normally to preserve the runtime log. Report any
issue with native input, hide or hold encountered during the route.
Runtime PENDING, production BLOCKED.

## Full World appearance runtime feedback (2026-11-20)

One user-run session on `59cc569de1cc1f4354658145c843c1efe9a62166`.
World (7 files) and Screen S1 (5 files) matched the installation
receipt after exit. Archived UE4SS 83330635 log SHA-256
`f9daa7a74903f2466762eb49613577353169509037cdb3d0f962ba08a3b4753b`.
User Take screenshot SHA-256
`73bdfc5876bd77c1e1964af098f238cf3503ea81257e03a0851f56ea09964510`.
Both artifacts are private.

The template write ran once. The three known actors each logged
`STYLE_READY decorated=true` and World/NoCollision in BeginPlay.
Three F5 snapshots each captured all three original TipHUDs with
World RTs and `added_to_screen=false`. The session logged 164
successful decoration starts, including actors outside those three,
and five native MID tint verifications. The tint verification
markers carry no actor identity. The user saw the styled prompts
and confirmed normal interaction, including successfully picking up
an item. That observation is bounded to this route. Hold cadence
under a sustained hold and wider gameplay coverage were not measured.

The user found RGB ×0.35 too dim, wants the upper line and divider
centered on the current stock word, and wants upper text to vary by
action. In the Take frame the upper pair is visibly to the right of
the word «Взять». `IIPTemplateStyle.lua` sets X=121.75 for both owned
children with center alignment. That was the center of the measured
Russian merchant Talk layout and is now reused for every word.
Prefer deriving the word center from its verified text slot and
measured width in the same canvas while keeping divider width fixed.
The earliest usable World measurement still needs evidence. Prior
Screen evidence had a late desired size. A smaller fixed X is the
fallback if dynamic centering would delay the prompt or cause a
visible correction. Exact brightness and action lettering remain open.

The user noted that retaining the native orientation can look odd
from some angles and may suit a door plane. No door or camera-facing
change was exercised. Candidate remains installed. Production BLOCKED.
