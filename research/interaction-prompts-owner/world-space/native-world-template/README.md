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

## World composition follow-up — source-only candidate (2026-11-20)

**RESEARCH ONLY — NOT INSTALLED — production BLOCKED.** Following game
feedback on installed `59cc569`, a bounded successor changes only
native visual composition in `IIPTemplateStyle.lua` and reads the
original actor's `TipHUDArgument.msgTag` in `main.lua`. The single
SCS-template World/NoCollision write, original World components,
native action, hints, input selection, visibility, interactions, world
scale 0.400, +36 world Z, 1000×1000 RT and hold cadence are unchanged.

- Native component RGB tint multiplier rises **0.35 → 0.45**,
  preserving alpha and the existing MID verification.
- Original stock `TextBlock_89` and its autosized `CanvasPanelSlot`
  are read once at decoration. Only if current text is not a
  placeholder and `GetDesiredSize` / anchors / alignment are valid
  does the upper line/divider center at
  `slotX + width * (0.5 - slotAlignmentX)`.
  Neither the stock slot nor the native text is changed.
- When that geometry is not available at BeginPlay, use **instant
  provisional RU-route X positions**: Take 70, Open 81, Check 93,
  Talk/Interact 121.75, unknown 80. Divider remains constant width
  142.375. These are **not universal widths** and do not prove
  center alignment on other languages. No timer, forced prepass,
  frame pump or late position correction.
- Render test-only font tokens `OPEN`, `TAKE`, `CHECK`, `TALK`
  by the original `TipHUDArgument.msgTag`, not actor class or
  hard-coded localized string. Other/missing tags use `ACTION`.
  These are **not translations into Aphes lore**. A known tag
  transition in native `CanShow` updates only the owned upper text
  once if it changed; its horizontal position is never moved late.

**Evidence boundary:** The prior S1 merchant had zero desired size
at first CanShow and a nonzero value ~200 ms later. The newer World
candidate has not recorded whether the valid native text width
exists at BeginPlay. A fallback is intentional to preserve prompt
latency and avoid a post-reveal jump. Provisional token mapping
and geometry require one real-game visual check before acceptance.
In particular `style.start` and `style.can_show` receive only a
read-only tag from the original TipHUDArgument owner; if unavailable,
native behavior is unaffected and visual test glyphs remain neutral.

## World Composition installed (2026-11-20)

**INSTALLED**, exact source `151c38eaaef3b91f36fd2390c99cea68aa3a15bb`.
The confirmed seven-file active `59cc569` package was replaced
in the existing World loader slot with both game processes closed.
Only `main.lua` and `IIPTemplateStyle.lua` changed. The authored PNG
and private TTF/config were verified against their known hashes.
All four authored Lua modules and the private config compiled.
Resource validation passed again using the installed config.
Seven Template and nine visual tests passed locally.
[Full CI PASS on the exact source](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44804483529).

Installed manifest SHA-256
`9fb741f968f6fadf265e2f238ca65bbd8c293e5e407133fca8b1dd4d6f780dcd`.

| Installed file | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `0f46837ee12e8c5ab6b5e2e645a57d2a0fa87353bd47ead64281c6df4729cd86` |
| `Scripts/IIPTemplateStyle.lua` | `a6711908466312b848acb2a23dcbdf6e2ff1ec214d8853f9fb70e4fb8b6643ff` |
| `Scripts/IIPTemplateProbe.lua` | `f32a663aa36a3490825d590a1d7a1c9da4d110e97e16a7e1fda636b4aa1f19af` |
| `Scripts/IIPTemplateResources.lua` | `8f9502f29fb05b4c1f8e1d561a6e63a583b5afb010babf5802b7b92b511eb1cc` |
| `Assets/aphes_divider_256x32.png` | `b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969` |
| `Scripts/IIPLiveConfig.lua` | `894f191e0d8d1beaaafd21c9e4265e2a623cd7b6028b979a2e67811d270d9978` |
| `enabled.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

All five Screen S1 files and neighboring file inventories matched,
including 12,548 other ue4ss files, 26 Win64 root files, 11 pak-mod
files, 16 save files and 53 config files. The full original `59cc569`
directory was archived outside the loader. The seven predecessor
files and seven newly installed files were independently rehashed
after installation. Full active restoration was rehearsed on a copy.
The private deployment receipt records the resolved archive location.
Closed-game rollback uses `.local/install-native-world-composition-151c38e.py
--rollback`.

Ready for a user visual run. Compare brightness, alignment and
action-specific upper words on the known chest, note, potion and
optionally Talk. Observe first appearance for delay or a horizontal
jump. Press F5 while a relevant native prompt is visible and exit
normally. The log identifies `center=measured` or `center=fallback`,
the early token and any later token-only update. Runtime PENDING,
production BLOCKED.

## World Composition runtime and upright follow-up (2026-11-20)

Installed `151c38e` matches all seven World manifest entries. Screen S1
matches all five entries. The live log was copied while both game processes
were running. The screenshot and log are retained privately. Log snapshot
SHA-256: `43ab6e89f7464656253150ec81364b623e5be9c187c7a002409242de1a2a262f`.

| User-tested object | Early decoration | F5 native World sample |
| --- | --- | --- |
| Chest | OPEN, fallback X 81 | RT present |
| Note | CHECK, fallback X 93 | RT present |
| Potion bag | TAKE, fallback X 70 | RT present |

All three samples report World, NoCollision and no Screen insertion.
On initialization the three components report `STYLE_TINT rgb=.45 mid=pending`.
The session has five later `STYLE_TINT_VERIFIED rgb=.45` events. Verification
compares both the original component and the World material's
`TintColorAndOpacity` to the seeded baseline times 0.45 with the original
alpha. Those events lack object IDs and establish no first-frame timing.
The user reported little perceived brightness change. The run provides no
matched image comparison, so perceived brightness remains open. The
three measured branch outcomes were fallback positions, with centering
against actual native text width still open.

The potion screenshot shows the entire sign tilted. Composition changes
scale and world-Z height and uses the native rotation. The source-only
follow-up applies one `K2_SetWorldRotation` at existing BeginPlay styling
on the original World component. It removes world Pitch/Roll and keeps
the original Yaw, verifies the result, and attempts to restore the
original rotation if the write fails verification. The native setter
was previously exercised on a registered custom widget component in
the [orientation experiment](../orientation/README.md). This use on the
original attached component needs runtime verification. No new hook or
camera update path. Parent rotation after initialization may still affect
the sign. The remaining runtime check is a cold first approach to the
sloped potion bag and control approaches to the chest and note. Check
verticality, retained heading and normal prompt behavior. Active game
files were left in place. Production BLOCKED.

## Fixed placement and RGB 0.50 (2026-11-20)

The next source-only candidate applies RGB ×0.50 with the original alpha.
The existing per-tag positions now provide the only placement path for
both owned elements: Open 81, Take 70, Check 93, Talk/Interact 121.75,
and other or missing tags 80. They are selected once during decoration.
The chest, note and potion used these positions in the Composition run.
The text measurement branch has been removed. The divider remains
142.375 wide, and the upright orientation change is included.

On the next authorized gameplay run, check brightness and placement at
the chest, note and sloped potion bag. Expected diagnostics include
`STYLE_ARMED rgb=0.50`, `STYLE_DECORATED placement=fixed` and material
verification at `rgb=0.50`. Runtime acceptance pending. Production BLOCKED.

## Fixed placement and RGB 0.50 installed (2026-11-20)

**INSTALLED**, source `cb6fc4390d61a613d9eca36a30817e9c4a6f1cc2`.
Both game processes were closed for the replacement and final checks.
The existing World loader slot was reused. Only `main.lua` and
`IIPTemplateStyle.lua` differ from the installed predecessor
`151c38eaaef3b91f36fd2390c99cea68aa3a15bb`.

Manifest SHA-256
`95e5c8924f0f5873eca474e1ffc376ecbc8381416fd6b6e0d92a378bf4980e1a`.

| Installed file | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `710e0c9432997c8dd8565be6d7faa706e1a48ec244b2b91a52fc25c2bfc10596` |
| `Scripts/IIPTemplateStyle.lua` | `b2b66b06e1f4f7ee7f14f69a94e059ebb360672daf1ebb7da7715014f3f694f9` |
| `Scripts/IIPTemplateProbe.lua` | `f32a663aa36a3490825d590a1d7a1c9da4d110e97e16a7e1fda636b4aa1f19af` |
| `Scripts/IIPTemplateResources.lua` | `8f9502f29fb05b4c1f8e1d561a6e63a583b5afb010babf5802b7b92b511eb1cc` |
| `Assets/aphes_divider_256x32.png` | `b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969` |
| `Scripts/IIPLiveConfig.lua` | `894f191e0d8d1beaaafd21c9e4265e2a623cd7b6028b979a2e67811d270d9978` |
| `enabled.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

All five Screen S1 files matched. Hash inventories matched before and
after across 12,548 other loader files, 26 Win64 root files, 11 pak-mod
files, 16 saves and 54 config files. Host, UE4SS and the private resources
passed the existing install checks. The four Lua modules and private config
compiled. Seventeen targeted tests passed and
[full CI passed](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44810251010).
Local Windows discovery ran 650 tests with one failure in the historical
AutoWorld manifest test, which compares Windows separators with POSIX
separators. Its test and fixture are byte-identical to the predecessor.

The full previous World folder was archived outside the loader and
rehashed against its manifest. Restoring all seven files was rehearsed on
a copy. The private receipt records the backup location. With the game
closed, the rollback entry point is
`.local/install-native-world-fixed-cb6fc43.py --rollback`.

For runtime evaluation, approach the chest, note and same sloped potion
bag from a cold launch. Observe brightness, fixed placement and a
world-upright prompt whose heading stays fixed as the camera moves.
Use F5 while a native prompt is visible and retain the UE4SS log.
Runtime PENDING. Production BLOCKED.

## Fixed placement and RGB 0.50 accepted on three placed prompts (2026-11-20)

The user explicitly accepted the appearance and behavior seen on the
chest, note and same potion bag on a slope. The session used installed
`cb6fc4390d61a613d9eca36a30817e9c4a6f1cc2` with the manifest above.
The live log was copied at 23:36 Moscow time while the game was still
running. Snapshot SHA-256
`7dda04ba9ede9d79b6c20b06504e7e2258a71c27db437b56255ac0c31fa73363`.

| Object | Fixed placement | World orientation at initialization | F5 |
| --- | --- | --- | --- |
| Chest | OPEN, X 81 | Already upright | Native RT present |
| Note | CHECK, X 93 | Already upright | Native RT present |
| Sloped potion bag | TAKE, X 70 | Tilt removed, yaw retained | Native RT present |

Orientation readback precedes the bag's `STYLE_READY`. All three F5
records report World/NoCollision and no Screen insertion. Five later
material readbacks confirmed RGB ×0.50 with source alpha during the
session. Those entries omit actor IDs and do not establish first-frame
tint. The visual acceptance covers these three placed prompts. Moving
parents, doors, other action routes and production acceptance remain open.

## Native coverage and fictive Aphes vocabulary — source-only (2026-11-20)

The accepted `cb6fc43` World visuals remain frozen on chest, note and
sloped potion bag. Broad coverage is first sought through the SAME
`BaseGameEventObject_BP_C:ExtendedWidget_GEN_VARIABLE` SCS template:
there is no reason to add separate per-actor selection/show/hide code
for compatible descendants. The previously observed 164 successful
style starts are evidence of scope beyond the three exact objects,
not proof of every interaction class or simultaneous prompts.

### Verified row inventory and authored vocabulary (2026-11-21)

CUE4Parse 1.2.2 read stock Steam build 12996889 with UE4.27 from
`/Game/MainContent/Tables/UMG/InteractTipToText`. The new export
matched the retained export byte-for-byte (SHA-256
`768d62913e90c1d3df2734bb2a8e76038421c0bbec1723d1d07dbb0337869b8a`).
All 18 exact row names are listed below, in export order. The one
lookup in `IIPTemplateStyle.lua` maps each to a fictional word.
The private stock font's cmap was independently checked for all
26 uppercase ASCII letters. The authored words have no official
Aphes or Greek translation status. The lower label remains game-owned.

| RowName / msgTag | Invented word |
| --- | --- |
| `Climb` | `ORTHA` |
| `Restart` | `PALINO` |
| `Interact` | `NEMARO` |
| `Open` | `ANOKE` |
| `Talk` | `LETHO` |
| `Gossip` | `PSYRA` |
| `Knock` | `KROTA` |
| `Heal` | `IATHE` |
| `Insert` | `EMVORA` |
| `Remove` | `EKLON` |
| `Press` | `PIEZA` |
| `Take` | `LAVO` |
| `Break` | `THRAKO` |
| `Enter` | `EISORA` |
| `Check` | `SKERA` |
| `Activate` | `KINERA` |
| `Pray` | `EUKRA` |
| `UILoadTest` | `DOKIRA` |

Retained selected-native and World logs contain `Break`, `Check`,
`Gossip`, `Interact`, `Knock`, `Open`, `Press`, `Pray`, `Take`
and `Talk`. The battery-switch template also serializes `Remove`.
The other rows, including `UILoadTest`, establish a lookup key and
leave its actual gameplay use open. The NPC's cooked `SetNPCTip`
copies a caller-supplied name into `msgTag`. The selected merchant
sample saw `Talk`, which is already a row. No action tag outside
the table was confirmed in the reviewed exports and prompt logs.
`None` was observed as an unset name. `Descend` is absent from the
table and lacks a confirmed `msgTag` observation. On initial
decoration, missing or unmapped tags use `ACTION`. The existing
`CanShow` path updates the owned header on a recognised change
and retains it during unrecognised or missing reads. Wider game
routes or dynamic writers could still supply other tags.

### Shared component coverage (2026-11-21)

Inheritance was checked against the cooked parent chain, local
SCS nodes and inherited component overrides. Stock
`BaseGameEventObject_BP_C` owns the shared
`ExtendedWidget_GEN_VARIABLE` and gives it `TipHUD_C`. These
findings apply to the named samples.

| Family | Confirmed evidence | Runtime boundary |
| --- | --- | --- |
| Chest, pickup, document | Shared ancestor and component; World RT and visual acceptance on the three named instances | Baseline `cb6fc43`; new words await a run |
| Dynamic NPC | `NPCInteract_Bp_C` → `BaseNPCInteract_BP_C` → shared base. No replacement widget in the two exports. Selected merchant evidence has original Screen `TipHUD_C` and `Talk` | Expected to inherit World with the shared patch. No World rendering or timing proof for this dynamic NPC route |
| Doors and gates | `Base1SideDoor_BP_C`, `Base2SideDoor_BP_C`, `BaseTeleportDoor_BP_C` and `BaseGate_BP_C` descend from the shared base. Cooked aqueduct door resolves through `Base1SideDoor_BP_C`. Its original World component reached `STYLE_READY` as `Open` in the `cb6fc43` log | No F5 RT sample or visual/door interaction acceptance for that actor. Other door variants require their own ancestry or observation |
| Levers and switches | The sampled heavy wooden lever, battery switch and crystal switch descend through `BaseGear_BP_C` from the shared base. The two switch exports set `Remove` and `Press` respectively | Likely native World coverage for these descendants. Visible state changes and actual runtime tag transitions remain open |
| Moving objects | The sampled B01, round A01 and water lifts descend through `BaseElevator_BP_C` from the shared base. The base has move-to-start/end functions. A separate elevator script actor follows `BaseGameScriptObject_BP_C` | Likely shared coverage on those lift actors. Component tracking and heading during movement, and any prompt on the separate script path, are unverified |
| Ladders | `Ladder_BP_C` and the sampled A01 route lead to native `BaseClimbObject`. The sampled B01 via `BaseSwitchLadder_BP_C` has its own SCS `ExtendedWidget_GEN_VARIABLE` pointed at `TipHUD_C`, with a separate `Interact` argument | The shared write does not reach that separate template. The stock prompt mechanism for ordinary climbing/descent and the switch ladder's live behaviour remain open |

**Source only.** Keep the existing single SCS write and reuse
`BeginPlayPost` and `CanShow` on the original component. The
three-object diagnostic list does not gate styling. The code change
is limited to the word lookup. Accepted dimensions, RGB, elevation,
orientation and fixed X values remain those of the previously
installed `cb6fc43` baseline. Production BLOCKED.

## Fictive vocabulary installed (2026-11-21)

**INSTALLED**, source `0ddec340d15944e10178cec478c2161f3c5e0db8`.
Both game processes were closed. The existing World loader slot was
reused. Six entries match the previous installed manifest byte for byte.
The sole change is `Scripts/IIPTemplateStyle.lua`, SHA-256
`928e248ac26eb1b60560e2fe20c623a71d1e0ece3cc8db2d85f3ef6b5befc146`.
See the [previous manifest](#fixed-placement-and-rgb-050-installed-2026-11-20)
for the other six hashes. All seven installed files were rehashed.
The new manifest SHA-256 is
`f64a8194296049f0d770f8ead00a10e5f9c0739dcc24604be33823a2aa682758`.

The four authored Lua modules and local config compiled. Private font
and divider validation passed. Nineteen targeted tests passed, and
[full CI passed on this exact source](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44817344307).
All five Screen S1 files matched. Before/after snapshots also matched
12,548 other loader files, 26 Win64 files, 11 pak-mod files, 16 saves and
52 config files.

The full previous World folder was archived outside the loader.
Its seven files match `cb6fc43` and were restored successfully on a copy.
The private receipt records the archive location. For closed-game
rollback use `.local/install-native-world-vocabulary-0ddec34.py --rollback`.

On the next user run, check the chest, note and potion bag for
`ANOKE`, `SKERA` and `LAVO` above the original localized action.
If the same merchant or an eligible door is on the route, note whether
the new header appears there. Press F5 near the placed controls and keep
the UE4SS log. Runtime PENDING. Production BLOCKED.

## NPC Talk first facing (2026-11-21)

The user reported that the installed vocabulary worked generally.
One NPC approached from behind had a World prompt facing away, and
interaction did not work from that side. The session's private log
snapshot SHA-256 is
`02ca9f60a1e9aab98630bb4da0d26ab615110819893fa42bf865e2c1403d8445`.
On `0ddec34`, eight `NPCInteract_Bp_C` actors reached `STYLE_READY`
and five `Talk → LETHO` updates were logged. The update events omit
actor IDs. The log contains neither the failed actor's eligibility
decision nor a video measurement of its first rendered frame.
The retained NPC graph contains separate native `SetIsCanInteract`
calls. The report alone cannot link a rear approach to an interaction
gate or show that rotating the widget restores interaction.

The source-only experiment reuses the original component's existing
post-`CanShow` path and the existing world rotation setter/readback.
It runs once per styled widget identity for exact `NPCInteract_Bp_C`,
native tag `Talk` and `ExtendedWidget.bVisible == true`. It uses the
widget's owning camera manager. The plane's local +X points to the
camera's horizontal position while world pitch and roll remain zero.
An unavailable camera or degenerate horizontal displacement skips
the attempt. Setter/readback failure uses the existing restoration
path. The existing tag refresh and hold cadence still run.

The setter was verified on the original component for world upright.
The +X geometry and owning-camera route were used in the prior
[vertical-yaw experiment](../vertical-yaw/README.md#geometry-and-edge-cases).
The first World frame and owning camera on this exact NPC route
still need user-run evidence. `CanShow` is a post-callback with
widget context. It supplies no native return or selected-owner
decision. The experiment adds no hook or polling and leaves native
action availability, visibility, selection and input to the game.
The heading is initialized once, so approaching an already-styled
widget from the other side is outside this first test.

For the next authorized install/run, approach the reported NPC from
behind first. Record initial readability and whether the game allows
Talk. Then compare interaction from the front, and verify one non-NPC
control such as the chest. Collect the `NPC_TALK_ORIENTATION` or
`NPC_TALK_ORIENTATION_SKIPPED` result with the recording. Production BLOCKED.

## NPC Talk first facing installed (2026-11-21)

**INSTALLED**, source `10fa4f0448c14c1b0db49156498baabb5baf5cbd`.
Both game processes were closed. The existing World loader slot was
reused. Five entries are byte-identical to the
[vocabulary manifest](#fictive-vocabulary-installed-2026-11-21).
The changed files were rehashed after installation:

| File | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `a8c64b264f8417201f35ee1458fcab4f36034a548ae19255ffd3b5ab34f60d02` |
| `Scripts/IIPTemplateStyle.lua` | `3368a95c0ec9e964d9dfb78fd40d3f42d52be06fad3f099e07efb5f4bff0e47a` |

Seven-file manifest SHA-256
`fabb5035d6b8bf2e879d3eb0182b5b844be75f14c5babd865980b7d0df3833a4`.
All seven World files and all five Screen S1 files matched.
Before/after snapshots matched 12,549 other loader files, 26 Win64
files, 11 pak-mod files, 16 saves and 47 config files. The Lua modules
and local config compiled. Private resources passed verification.
Twenty targeted tests and [full CI](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44820429113) passed.

The full previous `0ddec34` World folder was archived outside the
loader. Its seven files matched the previous manifest. Restoration
was rehearsed on a copy. The private receipt records the folder.
With the game closed, use
`.local/install-native-world-npc-facing-10fa4f0.py --rollback`.

The user will approach the same NPC from behind first and check the
first readable frame and whether the native Talk action starts.
Retain the recording and UE4SS log for correlation with the
`NPC_TALK_ORIENTATION` or `NPC_TALK_ORIENTATION_SKIPPED` marker.
Runtime PENDING. Production BLOCKED.

## NPC repeat facing and door occlusion (2026-11-21)

The user confirmed the facing change on installed `10fa4f0`.
The session has four `NPC_TALK_ORIENTATION changed=true` records
on distinct NPC instances, each followed by the Talk header update.
No orientation skip was recorded. The log and user confirmation
establish the turn. First-pixel timing and successful rear-side
Talk remain open. Log snapshot SHA-256
`4707d8aadce5221ca687a39a7681a82ea17fa6c3194f3541b02155db6007312`.

**Repeat facing, proposed.** Reuse the existing setter once on each
native hidden-to-visible transition. Keep the heading fixed while
the prompt is visible. The current `CanShow` callback confirms the
visible side of this path. Its cadence while this NPC's World prompt
is hidden is unverified. Prior reflected `SetShow` and base-class
`ShowTipEvent` probes registered with no delivered callbacks.
Start with one read-only trace on the existing callback for one NPC:
approach, withdraw through a full hide, and approach from the other
side. Record whether the same widget reports hidden state before the
next visible state. A state reset in that callback is sufficient if
the edge is observable. A missing hidden callback rules out that
reset scheme. No elapsed-time heuristic is justified.
[Prior notification evidence](../show-tip-event-observer/README.md#runtime-result--2026-11-07).

**Door clearance, proposed.** The screenshot shows bars in front of
both action lines and the ornament. The fresh log lists multiple
eligible door owners in that area and does not identify the one in
the screenshot. The corresponding cooked level export contains
sewer-door instances with front and rear alignment points, a
`WidgetLocator` and the native `ExtendedWidget`. Once the exact
door is identified, use its approach-side sign along the door normal
to put the existing World prompt just ahead of the closed leaf.
Tune the smallest clearance in world units for that door. This
preserves ordinary depth occlusion elsewhere and the shared `Open`
presentation on chests. A fixed move along the current widget
forward axis can be tested for a known one-sided door with a verified
axis and side. A global `Open` offset and through-wall drawing
would also affect prompts outside the reported case.

**Chest readability around the full circle, proposed.** The user
reports that the fixed chest prompt disappears when viewed from
behind. The stock World widget is a plane with one UV layout. Its
two-sided setting would expose that image in reverse from behind,
and the plane would still be edge-on from the side. Two readable
faces would share the same side-view limit. To keep text readable
through a full walk around the chest, consider turning the existing
World plane toward the camera in yaw while visible, with world Z
up and the anchor kept in place. The one-shot NPC turn only serves
the start of an appearance. A yaw-following plane can still be
occluded by intervening geometry, so door clearance remains its
own placement issue. Runtime cost, smoothness, scope and the
visibility boundary for this option remain open.
[Prior yaw geometry trial](../vertical-yaw/README.md#geometry-and-edge-cases).

These are design options under discussion. The installation and
runtime code remain as tested. Production BLOCKED.

## Accepted Billboard Yaw / Door Plane — read-only CanShow cadence trial (2026-11-21)

The user adopted two presentation policies without changing native actions:
1. Non-door world owners (including chest/NPC): original World plane stays
upright, yaw follows camera when the prompt is active; never fake a second
renderer or change game selection, action text, input, hide or interaction.
2. Door/gate: original World plane stays parallel to the closed leaf and
is placed slightly ahead of the leaf on the **player's** side. Needs
verified class/geometry/side, unlike the `Open` tag shared by chests.

**Research-method checkpoint:** The shipped `10fa4f0` already has a
working post-`TipHUD:CanShow` seam and a proven one-shot NPC camera-facing
setter. Prior `vertical-yaw` proved the per-frame rotation math/setter
on a separate World component, but not an active original-widget loop.
Rather than add new hooks/timers or mutate world geometry speculatively,
a source-only `IIPTemplateFacingObserver.lua` samples the existing
CanShow event **only after the user presses F5** and prints a bounded
summary on the next F5. Its observation groups are exact NPC class,
exact known chest, and *potential* doors selected by class/actor-name
substring only for diagnostics (never for policy). It records counts,
`bVisible`, native widget `RenderOpacity`, and sampled camera bearing
versus component yaw (one pose read per eight native callbacks, capped).
No rotation, visibility, player state or native interaction setter is
called by this new module; no second hook or separate scheduler.

**When installed by separate approval, one short user-run:**
- In front of the known chest, press F5 to arm; walk around it or
  rotate the camera substantially while near the prompt; press F5
  to stop. A camera bearing change across multiple callback samples
  supports reusing CanShow for updates; only one call/pose does not.
- On a known NPC, arm F5, approach/withdraw fully and reapproach
  from the opposite side; stop F5. Interpret `visible_false` and
  `opacity_zero` as sampled signals, *not* a definite native
  hide event. Absence of hidden samples excludes a `CanShow`-only
  hidden-edge reset but not native hide by other events.
- Record native Talk success/failure separately from the visual
  rotation; existing NPC `SetIsCanInteract` can gate Talk.
- At the reported grille, start F5 before approaching, move into view of
  the prompt, then stop F5. Compare the candidate actors' observations and
  the visible prompt in the same interval. The static match and its limits
  are below.

## Static closure — sewer grille, NPC Talk and observer payload (2026-11-21)

### Door Plane

The best-supported match for the photographed grille is
`0-2_plot_shelterA_main2:PersistentLevel.1-1_slumpass_door_bp1`
with actor tag `1-1_slumpass_door`. The image shows the Black Streets
objective to meet Quintus at the sewer entrance. The cooked level places
the slum passage and the separate Arges route in the same sublevel,
and the Slums export also contains a passage-specific
`1-1_slumpass_door_insurance` overlap actor. The recorded session styles
both doors at load with `Open`. Both use `item_door_sewer_a01_bp_C`
and the same skeletal mesh and material override. Consequently the
match rests on the quest and route, and the captured log cannot prove
which actor displayed the photographed prompt. `STYLE_READY` is an
acquisition record. The door class also differs from the nearby
`2-1_routearges_door_hint` overlap actor.

The matching placed actor owns both components. The attachment chain is
`RootArrow → WidgetLocator → ExtendedWidget`; the terminal component
hosts `TipHUD_C`. The inherited locator is `(0, 0, 180)` in root space.
The mesh is a separate child of the root. The level export gives the
slum root yaw as approximately +90°, with zero pitch and roll.
The archetype chain `item_door_sewer_a01_bp_C → Base1SideDoor_BP_C →
BaseGameEventObject_BP_C` gives the following root-local geometry
(Unreal units, rounded):

| Component or axis | Relative to its parent | In root space |
| --- | --- | --- |
| Front trigger | `(55, 0, 35)` | `(55, 0, 35)` |
| Front alignment under front trigger | `(0, 0, -35)`, yaw 180° | `(55, 0, 0)`, faces −X |
| Rear trigger | `(-50, 0, 35)` | `(-50, 0, 35)` |
| Rear alignment under rear trigger | `(-10, 0, -35)`, yaw ~0° | `(-60, 0, 0)`, faces +X |
| Skeletal mesh component | yaw −90° | world yaw ~0° on the slum instance |
| Closed-leaf plane inferred from the opposing alignments | spans root Y/Z, front normal root +X | spans world X/Z, front normal world +Y |

The opposed alignments establish the passage axis and a well-supported
closed-leaf normal. The retained exports do not measure the actual
rendered bars' depth or animation pose. The locator sits at root X=0.
For a closed leaf, let `N` be the normalized horizontal rear-to-front
vector, `O` a verified point on the closed-leaf plane, and `A` the
unmodified prompt anchor with the existing height adjustment.
Use `s = sign(dot(playerPawnLocation - O, N))`, then project `A` onto
the plane and add a side-specific clearance:
`P = A + (s * clearance - dot(A - O, N)) * N`.
Choose clearance beyond the nearest outer bar surface on that side,
keeping the tangential coordinate and height. Use the original World
component's location setter and yaw its local +X toward `s * N`,
with pitch and roll zero. One component suffices geometrically.
Use a small dead zone around the plane and require a valid closed-leaf
reference before applying any move. Confirm the selected actor at the
reported doorway and measure the plane offset and clearance before
implementing it. The other sewer instance has root yaw ~−180°, which
would put its front normal near world −X. A fixed world-axis move
would fail to generalize. The calculation says nothing about whether
the game permits interaction from either side.

Evidence retained locally for reproduction: the screenshot and the
`4707d8aa…` session above, the `0-2_plot_shelterA_main2` and
`1-1_plot_slumB1_main1` level exports, and the cooked sewer door,
`Base1SideDoor_BP` and `BaseGameEventObject_BP` archetypes.

### NPC Talk availability

The retained `CharacterSetCanInteract` Blueprint can create
`NPCInteract_Bp_C` with the character as owner. The base NPC graph
resolves the owner as `GenesisCharacter`, attaches the interaction
actor, sizes its box from character capsule dimensions and positions
the widget locator. `BaseNPCInteract_BP.ExecuteAction` dispatches the
named plot actions `CanInteract` and `CanNotInteract` to the native
`BaseGameEventObject:SetIsCanInteract(true/false)` calls (cooked
ubergraph offsets 1156 and 1172). The battle availability branches
write their own `IsCanInteractInBattle` flag. The `SetNPCTip` branch
handles the tip tag separately. The derived `InteractBeginEvent`
delegates to the base event and uses NPC interaction metadata and the
native plot/touch path. These are distinct routes from the Lua
one-shot presentation turn.

In this exported availability branch the setter receives a literal
boolean selected by action name. The graph has no approach-direction
test on that path. Native selector conditions and the runtime plot,
overlap and availability state for the reported failed attempt are
unobserved. The archived log identifies several dynamic NPC interaction
actors and visual turns, so it cannot correlate the failed attempt to
an exact NPC, a disabling call, or a particular native gate. Whether
a directional check elsewhere or another condition blocked Talk remains
unknown.

Evidence retained locally: the cooked `CharacterSetCanInteract`
function, the `BaseNPCInteract_BP` and `NPCInteract_Bp` ubergraphs,
and the reflected `BaseGameEventObject` declaration.

### Observer audit and pending installation

`04265a1b5b7a82207c8f1dac75970e449a1909e6` loads the observer optionally.
It starts inactive and reuses the post-`TipHUD:CanShow` hook. The
existing hook first joins the styled widget and its original World
component by path/address and verifies the current widget binding.
The diagnostic is reached after the existing first NPC turn and before
the existing cadence routine. F5 schedules the toggle on the same game
thread queue and retains the earlier placed-object sample. A second F5
stops observation and prints the summary. F5 requires the existing
engine tick entry point and an unclaimed key bind. The observer makes
getter calls and updates Lua counters only. It adds no native setters,
hook or polling loop. The inherited style path still performs its
previous presentation writes.

Each window retains up to 24 actor paths and 12,000 tracked callbacks
per actor. Pose attempts start on callback 1 and repeat every eight,
with up to 450 successful poses per actor. Failed poses count separately
and may be retried on the sampled cadence up to the callback cap. The
summary emits at most 24 actor lines plus a stop line. The overflow
counter counts rejected callbacks, rather than unique actor paths.
An unexpected sample error disables observer sampling for that styled
record and the usual style handler still runs. Only already-styled
actors that match the NPC class, known chest or name heuristic enter
the observer. The report aggregates by actor path and has no per-sample
timestamp or device/input outcome. Read one target per F5 interval.
Counts and bearing changes can show recurring delivery during a sweep;
they cannot prove frame-aligned updates, reliable identity across
widget recreation, or a native hidden edge from opacity alone.

Eight-file payload prepared outside the loader. Compare all entries
with the private `prepared.json` alongside `candidate/` and
`rollback-10fa4f0/` under the ignored
`native-world-template/04265a1b5b7a/facing-observer-offline/` stage.
Relative to the verified installed seven-file manifest
`fabb5035d6b8bf2e879d3eb0182b5b844be75f14c5babd865980b7d0df3833a4`:

| File | Candidate action and SHA-256 |
| --- | --- |
| `Scripts/main.lua` | Replace with source bytes. `a74cab50e6a64def93a2bcf15e8eca1e8ea6f128cbcb61e606fe97d85c12911f` |
| `Scripts/IIPTemplateFacingObserver.lua` | Add from source. `3008b77db4502fe94b700acd9af6113b06f1fa33b8dfad6ed4e985702cf2dd20` |
| `Scripts/IIPTemplateProbe.lua`, `Scripts/IIPTemplateStyle.lua`, `Scripts/IIPTemplateResources.lua`, `Scripts/IIPLiveConfig.lua`, `Assets/aphes_divider_256x32.png`, `enabled.txt` | Copy the six byte-identical entries from the installed manifest |

The private config continues to point at the existing external TTF and
at the same installed divider location. The World and Screen S1
inventories matched their last verified receipts. The staged Lua files
compiled and rollback restored all seven predecessor hashes in a local
copy rehearsal. For a future separately approved install, verify game
closure and both current manifests, replace the single World slot as a
folder and compare all eight hashes. For rollback, move the trial out of
the loader, restore the verified `10fa4f0` folder and check that all
seven hashes match and the observer is absent. The older rollback under
the `10fa4f0` deployment record would restore its own predecessor;
use the new local rollback copy for this trial.

Offline validation covered all 69 test files, including six facing
observer tests. The stock runner stops on Windows at the archived
resident-world manifest's slash comparison. That test and the rest of
the suite passed with that one comparison normalized in memory, with
the archived test file unchanged. The staged resource check also
verified the external TTF hash and the divider.

**State:** source prepared, runtime pending. The installed World remains
`10fa4f0`. Billboard Yaw and Door Plane remain design policies.
Production BLOCKED.

## Installed observer results and orientation successor (2026-11-21)

The user-run `04265a1` session had four completed F5 windows. The chest
had 271 callbacks, 34 poses and changing camera bearing with fixed widget
yaw. One NPC had 935 callbacks and 117 poses across the approach route.
It had zero sampled visibility or opacity drops. The inactive grille
window sampled another NPC only. The active grille window sampled
`1-1_slumpass_door_bp1` exclusively (241 callbacks, 31 poses, yaw 90°).
This pins the doorway identity. `CanShow` supplies repeat pose reads
while the prompt is available. These aggregates do not measure the
distribution between frames or provide a hidden-edge signal.

The user independently confirmed that Talk succeeded from behind when
the interaction button was held. Preserve the native hold and the
localized row. Earlier single-press failure is not evidence of a
directional interaction gate.

The first divider import succeeded and was bound to its own image brush.
After travel, the resource module persisted but its cached transient
texture failed the validity check. An earlier successful import had
latched `import_attempted`, causing `second import refused` before
decoration could finish. The trace establishes loss of the valid
reference and a stale guard, while the exact engine destruction point
is unobserved. The successor shares the valid texture and permits one
replacement when a previously bound texture is no longer valid. Failed
import/bind attempts remain latched. Brushes retain the texture as
before. No map-wide hook, forced GC or native root is added.

The successor updates Billboard Yaw in the existing `CanShow` callback
for the exact observed chest and `NPCInteract_Bp_C` owners with a visible,
nontransparent native tip. It follows the camera around the existing
anchor independent of decoration state. Door Plane is restricted to the
confirmed placed grille of the exact sewer-door class. It reads the
owner's root, locator and front/rear alignments, and chooses the side
from the owning player pawn. With the door closed and native `Open`
visible, it puts the original component 24 cm from the root plane,
preserving height and lateral placement. A pawn within 8 cm of the plane
causes no side change. The previous pose is restored on an observed
callback outside the closed Open state. These distances are trial values.
The actual outer surface of the bars and coverage of the restoration
callback need runtime checks. Other door instances and shared Open tags
do not acquire this placement.

Verification on an authorized later run: start at the known chest,
circle it, travel into the Shelter, check the divider on a new prompt,
approach the NPC with full withdrawal between sides and hold to Talk.
At the identified grille check native Open, parallel placement, the
side and clearance from the bars, and behavior on opening. The F5
observer remains available. Local source and staged payload, no install.
Production BLOCKED.

## Runtime result — orientation successor 27b095d (2026-11-21)

Installed source `27b095d2f40a27a27fac3eeef2473523d449c997`.
All eight World files matched the prepared manifest after installation.
The eight-file `04265a1` rollback was verified outside the loader;
Screen S1 matched its pre-install manifest.

- **NPC Billboard Yaw:** the user confirmed readable NPC orientation.
  The session logged `ORIENTATION_APPLIED mode=billboard` on four
  distinct NPC instances. The user clarified that the chest was not
  visually checked. NPC success cannot establish chest behavior.
- **Divider:** the user reported seeing the divider after traveling
  into the Shelter. The session logged one successful texture bind
  and successful decoration in the Shelter. No replacement import
  (`replaces_invalid=true`) or divider-import rejection was logged.
  The appearance passed on the tested route. The invalid-texture
  recovery branch remains unconfirmed in the game.
- **Grille:** the user screenshot shows bars still occluding both
  the ornament and the native Open row. The confirmed actor
  `1-1_slumpass_door_bp1` reached `STYLE_READY decorated=true`, but
  has no `ORIENTATION_APPLIED` or `ORIENTATION_REJECTED` record.
  The session ended with an F5 arm and no completed summary. There
  is no readback showing that the 24 cm shift ran. The current path
  can quietly return on action/state, visibility, pawn availability
  or the near-plane dead zone. The next useful measurement is the
  eligibility and pose readback for this exact owner before changing
  the clearance. Occlusion failure is confirmed, and its cause remains open.

Private UE4SS session snapshot SHA-256
`fdcf76e22344a72c6c204beeabf42169559f1321c307f97414e313c2c8fcc5c8`.
Production BLOCKED.

## Door family classification and placement limits (2026-11-21)

The cooked class exports for Steam 1.09/build 12996889 make
`Base1SideDoor_BP_C`, `Base2SideDoor_BP_C`, `BaseTeleportDoor_BP_C`
and `BaseGate_BP_C` direct children of `BaseGameEventObject_BP_C`.
That parent serves other interactables as well. The available class
inventory also contains `item_0-1rockdoor_a01_bp_C`, a separate direct
child with its own mesh and opening path. The placed Minerva room
door has class `item_door_bazaar_a01_bp_C`. Its ancestry is absent
from the retained exports, and its name alone does not establish
membership in the known `item_2leaf_door_bazaar_a01_bp_C` family.
The inventory supports an extensible classifier with known roots;
it does not establish complete coverage of every game door.

The central classifier walks exact Blueprint class paths via
`GetSuperStruct()` once when the original widget is acquired.
The pinned UE4SS `83330635` Lua binding exports that method, and the
repository already uses it in the selected-owner and World reuse paths.
The walk stops at the generic event-object class or at the end of the
class chain. It classifies both the known roots and derived classes.
`ExtendedWidget`, `WidgetLocator`, a skeletal mesh, trigger areas or
`CurrentState` alone are shared or incomplete indicators. No name
substring, prompt text or `msgTag` participates in classification.

| Recognized family | Cooked geometry and lifecycle boundary | Placement in this candidate |
| --- | --- | --- |
| `Base1SideDoor_BP_C` | Front/rear trigger and alignment pairs face across root X. In the retained sewer instances both alignments, original widget/locator attachment and the root-plane estimate are available. The native graph controls open/close and interaction failure. | Existing 24 cm trial only for the exact sewer Blueprint, on any placed instance passing the existing geometry checks. Other descendants retain baseline placement. |
| `Base2SideDoor_BP_C` | Opposing `Leftt_CharacterAlign` and `Right_CharacterAlign` with respective triggers give a plausible root-X passage axis. Native graph owns direction-dependent open/close. Closed leaf surface and locator/mesh placement across derivatives are unverified. | Baseline placement. |
| `BaseTeleportDoor_BP_C` | Front alignment and blocking area are present. No rear alignment or generic rendered-leaf surface is established. Native open, close and transition behavior remain separate from placement. | Baseline placement. |
| `BaseGate_BP_C` | No confirmed opposing alignment pair. The retained descendants include a two-leaf bazaar door and a vertical wooden gate, with different moving geometry. A common face cannot be inferred from their shared root or state machine. | Baseline placement. |
| `item_0-1rockdoor_a01_bp_C` | Separate static mesh and effect arrangement; no verified opposing pair or leaf frame. | Baseline placement. |

The families share inherited TipHUD infrastructure, and the original
component remains authoritative. On acquisition, recognized doors pick
Door Plane even with `Knock` or `Gossip`. Their placement profile is
separate from that classification. The sewer experiment still moves only
on the existing closed/visible native `Open` callback. Keep this gate
until the reason for the failed `27b095d` approach is observed. On a
later callback outside that state, the existing pose restoration can
run. Callback delivery when a prompt hides is still pending.
Unsupported geometry keeps the previous World placement and never
falls through to Billboard. Chest and NPC Billboard behavior is unchanged.

The candidate retains `DOOR_PLANE_ROUTE`, bounded `DOOR_PLANE_SKIP`
and `ORIENTATION_APPLIED/REJECTED`. The smallest sufficient next game
test is the original closed slum grille once it is interactive.
Correlate its route record with the first recorded outcome and the
visibility of the bars over the text. A skip identifies the gate to
investigate; a verified apply with remaining occlusion supports measuring
the mesh surface. No clearance or guard was loosened for this candidate.
Source-only; installed `27b095d` remains the runtime baseline.
Production BLOCKED.

## Door Plane skip trace — source-only (2026-11-21)

The `27b095d` runtime report confirms a visible grille occlusion but
no evidence that the 24 cm offset executed. Do not alter clearance or
native eligibility on that basis. The next source-only revision adds
**diagnostics only** to the existing `CanShow`/Door Plane code path:

- `DOOR_PLANE_ROUTE` logs once for the exact
  `1-1_slumpass_door_bp1` on BeginPlay, showing whether the strict
  original actor path and class selected `mode=door`.
- The existing `door_plane` returns optional reason strings on
  legitimate no-op paths: `inactive_state=<exact CurrentState>`,
  `native_not_visible`, `pawn_unavailable`, `near_plane`,
  `already_placed` (or `restored` when leaving a previously placed
  state). No new state setter, hook, timer, or retry is introduced.
- Main logs a `DOOR_PLANE_SKIP` once per **distinct** skip string,
  at most 8 entries per original widget, with native tag, component
  visibility and widget opacity. `ORIENTATION_APPLIED` and
  `ORIENTATION_REJECTED` remain the definitive write/failure markers.

The choice to return the exact native state string is intentional:
a case/spelling mismatch such as `Close` versus hard-coded `close`
is a **hypothesis**, not a diagnosed cause. The already-verified
`NPC` Billboard and native interaction, GameState, rendering, font and
hold logic are unchanged. Offline tests exercise early native no-write
routes. **SOURCE ONLY; installed World stays `27b095d`.** New runtime
correlation at the exact grille is required before changing the
clearance or deciding how to generalize to other door classes.
