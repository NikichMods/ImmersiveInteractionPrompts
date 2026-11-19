# Native TipHUD S1 — compact C source-only pilot (2026-11-17)

**State:** SOURCE-ONLY research candidate, not installed or runtime-accepted.
**Installation authorization (2026-11-17):** User authorized bounded local installation with host closed, hash/backup/rollback verification and no game launch. This does not establish that installation occurred, that the existing local state is compatible, or that the first in-game check passed. Install through user-started local Codex under DevRules; stop on an unresolved preflight gate.
Exact tested source commit `6ffa2cfc248d15797c89067283389b0ecda23175`; [offline CI 44004664689 PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44004664689), including nine new S1 mocks.
No stock/runtime/live-game validation is inferred.
Production is BLOCKED. The user approved the **compact C** visual direction,
not the test payload or any change to installed game files.

## Purpose and bounded implementation

One existing screen-space \`TipHUD_C\` remains authoritative for selection,
native \`CanShow\`, action text, current button/hold/locked effect and show/hide.
The candidate adds only two own, transient children to the source
\`CanvasPanel_6\`: a private-font Aphes TextBlock and the already approved
\`assets/dividers/aphes_divider_256x32.png\` on an Image. No second viewport
or World renderer, Screen prehide, stock text/icon setters, callback return
override, component transform, per-frame polling or global native detours.

The passive decoration inherits the native screen-projected position and
visibility. The lower action and input branch are **never duplicated**.

- A single Blueprint post-only \`TipHUD_C:CanShow\` hook is used as
  the candidate observation seam. It is not claimed to run before first paint.
- Each compatible instance is identified by full path, class and address.
  No exact actor/path allowlist and no hard-coded Russian action string.
  Incompatible or not-yet-measured widgets stay **native-only**.
- This first pilot's upper text is the deliberately neutral ASCII
  **ACTION** rendered with the private Aphes font: decoration only, *not*
  a validated Aphes translation. An action-specific glyph lexicon has
  **not** been selected and must not be invented silently.
- Derived upper size = 1.2× native font (bounded 18–38);
  divider width = 0.85× cached native text width (bounded 94–190),
  its 256:32 aspect is preserved. These are trial layout units;
  the fixed image's visible alpha occupies approximately the middle half
  of its height. The lower native line/button are not moved.
- Reuses the tested transient Template UFont copy/storage guards and
  own Image PNG import. One transient font and texture are shared across
  at most 64 attached TipHUD widgets per map; at capacity the oldest
  own pair is removed before decorating a new one. This is a
  **resource containment policy**, not a hard cap on game interactions.
  An eviction/unknown state keeps the stock prompt working.
- A map-pre callback attempts reversible own-child teardown and
  resets shared references; Ctrl+Alt+F9 is the test-only manual STOP.
  If a cleanup operation fails the session stops further UI writes,
  retains failed identities for review/retry and requires a closed-host
  rollback before any new installation.

**Assumptions not yet established in real game:** attachment may occur
after the first native pixel, cached desired size may be stale/zero,
native centered ancestors may move when children change the layout,
long/other-language/handheld text and hold/locked states may differ,
map teardown timing and cleanup thread context need live evidence.
The mock tests cannot prove any of these.

## Files

- \`Scripts/main.lua\` — event-driven visual augmentation.
- \`Scripts/IIPS1Layout.lua\` — pure compact layout policy.
- \`Scripts/IIPS1Config.example.lua\` — local TTF and authored PNG paths
  for a separately authorized installation. No proprietary fonts or
  installed-game assets are distributed by this source.

## Next evidence gate

First run \`python -m unittest discover -s tests -p test_native_tiphud_s1.py\` (or
the repository's \`python tools/test.py\`) with test dependencies.
Authorization to install was given on 2026-11-17, subject to all local preflight, closed-host, and rollback gates.
After source/CI review and exact-hash installation with game closed and
rollback ready, the human visual check should cover one Open, Take and
Check/Read natural object when available, direct switching/return,
keyboard/gamepad remapping, light/dark background, first visible frame
and load of another save/map. Record \`IIP_S1\` diagnostics and user
visual verdict. Unsupported cases must leave the stock prompt intact.
An offline PASS is not permission to merge to main, mark VERSION
released, or claim production readiness.

## Local installation — 2026-11-17

**INSTALLED**, runtime PENDING. Installed source revision
`7c4655a91618ebaad2f7a6000ea623b4729627c2`; executable Scripts
match tested `6ffa2cfc248d15797c89067283389b0ecda23175`.
Nine S1 tests passed locally; full CI 44004664689 is PASS.

Closed host verified before and after installation. Steam build
12996889, executable and UE4SS 83330635 DLL hashes matched the
verified local baseline; external UEHelpers was present and hashed.
Private Aphes.ttf matched the established resource hash. The
authored divider was installed without modification.

Installed manifest SHA-256
`18708c073eab4ed2d750199fd91c51f9e83a0f3833a34f70ff8e183b3724b32b`:

| Relative file | SHA-256 |
| --- | --- |
| Scripts/main.lua | b63d65efc1e5b9643992c23aa8f78d34aadaf8fb4f6237f04e11583be8f6d602 |
| Scripts/IIPS1Layout.lua | 65f69b106aac838446f945a6ba24a31e0463e6b9c57e8feb7ad91b9a46371d15 |
| Scripts/IIPS1Config.lua | 57ac954c99f3a1ca8b9f920956d6a07f0f299ce419c7851b309910b16e565383 |
| Assets/aphes_divider_256x32.png | b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969 |

Private config contains verified absolute font/divider paths and remains
ignored. The only active IIP is ImmersiveInteractionPromptsNativeS1.
All earlier IIP prototypes remained disabled and preserved. All 587
pre-existing mod files, loader configuration, saves and game settings
retained hashes across installation. Game was not launched.

Ignored installation evidence is under
`.local/research/interaction-prompts/native-tiphud-s1/install-7c4655a`:
payload, hash manifests, before-state, copied mods.txt and pretest log.
Local `.local/s1-7c4655a-deploy.py --rollback` checks closed host,
payload hashes and activation state, then removes only S1 enabled.txt
and verifies no active IIP remains. Previous prototypes stay disabled.
Rollback was prepared, not executed after installation.

First user test may now begin. The upper ACTION is a technical Aphes
font string. Manual stop is Ctrl+Alt+F9. Record visual behavior and
IIP_S1 diagnostics before considering any runtime acceptance.

## First runtime attempt — 2026-11-19

**Initialization BLOCKED.** Exact installed source 7c4655a and all four
payload files matched the installation manifest after exit. User saw no
added decoration while approaching several objects and pressed Ctrl+Alt+F9.

The new UE4SS 83330635 session loaded S1 at 02:09:35 and immediately
reported:
`UNAVAILABLE main.lua:474: CanShow Blueprint hook unavailable`.
No READY, ATTACHED, FONT_WRITE_BEGIN or manual-stop event followed.
The assertion precedes RegisterHook and manual key registration, so this
attempt exercised neither decoration nor the Ctrl+Alt+F9 cleanup path.
The game event loop ended normally at 02:14:48.

This combined assertion checks availability, reflected type/full name
and absence of native flag 0x400. Its single message does not identify
which predicate failed. Local cooked TipHUD exports contain CanShow,
but that does not establish live availability during loader initialization.
An unloaded Blueprint function at this early point is a hypothesis.

Fresh log retained in ignored installation evidence, SHA-256
`c0c54553a0d1c38e6482ca29074b1ff5e6722ddf25f21e4ff5dddcad2e38ff59`.
With host closed, S1 activation was removed through verified rollback.
All other 591 files in the loader Mods tree retained hashes.

Next sufficient source step is to distinguish the failed reflection
predicate and inspect the existing accepted registration timing before
choosing a narrowly deferred initialization boundary. No layout or
font diagnosis follows from this run. A new runtime candidate requires
exact identity and the usual checks.

## Deferred initialization correction — 2026-11-19

S1 previously checked CanShow once at Lua load, whereas the earlier
ui-child/aphes-text probes registered their hook only after user
activation in an already loaded game. The failed S1 log cannot identify
the failed predicate retroactively. Blueprint residency at startup is
the supported loading hypothesis, pending runtime verification.

The corrected entrypoint logs WAITING when the exact function is absent
and retries lookup on the already used global BeginPlayPost boundary.
It registers CanShow once when valid, logging READY. Type, full-name
and native-flag mismatches remain terminal with distinct diagnostics.
Ctrl+Alt+F9 is registered before waiting and stops initialization as well
as decoration. Stopped sessions cannot register later. No timer,
per-frame polling or forced asset load was added. BeginPlayPost callbacks
become inert after readiness or stop.

Twelve local S1 tests pass, including delayed function residency,
stop-before-readiness and native-function refusal. This remains a
candidate for a second runtime test: startup should produce ARMED and
possibly WAITING, followed by READY during game loading, then ATTACHED
on compatible prompts. If no READY occurs, the session still provides a
usable stop key and the log identifies its waiting/error state.
Corrected payload is source-only and has not been installed.

Corrected source `ea32076a830ad55ee4f4946232c48c2d146fd779`:
[full offline CI 44420502777 PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44420502777).
A four-file local staging payload with the previously verified private
config and authored divider is ready. Manifest SHA-256
`fcd41c1a14c6a18f882af560519174213162919a820c4c6db7e751290a5a3162`.
Game installation remains at the disabled predecessor. No new game
session or installation was performed during this correction.

## Corrected S1 installed — 2026-11-19

**INSTALLED**, runtime PENDING. Source
`ea32076a830ad55ee4f4946232c48c2d146fd779`, manifest SHA-256
`fcd41c1a14c6a18f882af560519174213162919a820c4c6db7e751290a5a3162`.
All four installed files verified. Host closed throughout deployment.
Previous disabled S1 copied and hash-verified outside loader paths.
Only the two S1 source files were replaced and its enabled.txt activated.
Neighboring mods, loader configuration, saves/settings retained hashes.

Ignored evidence is in native-tiphud-s1/install-ea32076.
Local .local/s1-ea32076-deploy.py --rollback restores the previous
disabled S1 after closed-host and exact payload checks. All other IIP
prototypes remain disabled. User launches the first corrected runtime
check and uses Ctrl+Alt+F9 to stop. ACTION remains a technical glyph string.

## Corrected S1 runtime — 2026-11-19

Source `ea32076a830ad55ee4f4946232c48c2d146fd779`, installed
manifest `fcd41c1a14c6a18f882af560519174213162919a820c4c6db7e751290a5a3162`.
All four installed files matched after exit. New UE4SS 83330635 log
retained locally, SHA-256
`e4b8463b95c9e4a191c97d475f2359c1c91e1255684eeb089b079f886f4931a6`.

At 03:03:04.886 the startup lookup returned unavailable and logged
WAITING CanShow_NOT_LOADED. At 03:03:05.695 the BeginPlayPost retry
registered CanShow and logged READY. This run establishes that the
function can be absent at Lua startup and available later. It supports
the timing diagnosis of the predecessor, whose combined error alone
did not establish which predicate failed.

Three ATTACHED events at 03:04:46.328, 03:05:01.516 and 03:05:34.408
each reported two own children. One shared private font configuration
and one 256x32 texture import were logged, with DONOR_UNCHANGED.
There were no UNAVAILABLE, ATTACH_FAILED or cleanup-failure events.
At 03:06:01.580 Ctrl+Alt+F9 produced
CLEANED reason=user_stop own_widgets=0. No later attachments occurred
before normal game exit at 03:07:45.

User observed decoration at the conduit, merchant and ground potion.
Merchant appearance had a noticeable estimated 0.1–0.2 s delay;
potion appearance was quick. ATTACHED events do not log owner identity
or an independently timed first native/own pixel. Exact mapping of
each event to an object, duration and cause of the delay are unproved.
First font initialization preceded the first ATTACHED by about 10 ms,
but the log has no initial callback/measurement timestamp, so this
does not account for full attachment or visible latency.

The successful decoration and manual cleanup are bounded runtime
evidence, not complete visual acceptance. Startup readiness is no
longer the immediate blocker. The next useful decision is whether the
observed merchant delay is acceptable; if it blocks UX, compare the
native first frame with decoration readiness and cached desired-size
availability on that same object before changing the seam.

After closed-host exit, verified rollback restored the previous disabled
S1, preserved corrected staging and retained all neighboring file hashes.
No active IIP remains. Corrected candidate remains available for a
separately authorized next installation.
