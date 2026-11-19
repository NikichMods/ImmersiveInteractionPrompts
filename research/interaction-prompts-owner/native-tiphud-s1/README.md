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

## Drawable native visibility and perceived latency — source-only correction (2026-11-19)

The user judged the merchant's estimated 0.1–0.2-second delayed ornament a
**perceptible UX defect**, not an acceptable effect. Prefer a small, grounded
change over premature caching systems, broad owner scans or per-frame polling.

The current source already shares one Aphes UFont and PNG texture per map
(after the first compatible attachment) and keeps each pair of visual children
attached to its own native TipHUD for subsequent appearances. It **does not**
precreate each per-widget pair at map load. In the prior runtime the shared
font/texture initialized only once, but attachment happened three times.
Those logs do **not** time first native paint or establish the cause of the
merchant's visual delay.

A specific small semantic mismatch was identified from accepted
`can-show-state` runtime evidence in `docs/VERIFIED_RUNTIME.md`:
three distinct native TipHUDs reported stored visibility `4 → 0`.
UE4.27 `ESlateVisibility` defines both as drawable
(`4=SelfHitTestInvisible`, `0=Visible`), while the original S1 eligibility
test required the root to equal `0`. The corrected source accepts all
draw-capable native states `0/3/4` for root and original text child,
without modifying either native property. `1/2` remain excluded.
Native opacity, enabled state, valid action and guarded geometry remain
requirements, so this change is **not an early precreation mechanism**
for blank, zero-opacity or unmeasured widgets.

The existing `ATTACHED` record now includes the source
`root_visibility` value, permitting an ordinary game run to reveal whether
earlier attachment in state `4` is actually reached. No new hook, timer,
forced load, clone, cache tier or asset import was added. The change
neither guarantees first-paint coincidence nor proves the merchant's
delay was caused by visibility gating. If the same delay remains, the
next smallest diagnostic is a first-native/own-pixel comparison on that
same interaction before expanding prewarming architecture.

**Offline verification:** exact code commit `00c3e6782aba037088bebfa5bea3bfc8c9ae6d68`,
[GitHub Actions #44430338590 PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44430338590),
including 15 S1 tests and the repository-wide offline suite.
The added cases cover root Visibility 4→0 reuse, drawable 3,
hidden/collapsed 1/2 exclusion, and unchanged zero-opacity guard.

**Authorization update (2026-11-19):** The user explicitly approved **installation** of this exact visibility-fix source candidate `00c3e6782aba037088bebfa5bea3bfc8c9ae6d68`, after CI PASS. This is an authorization, **not** a completed installation or live acceptance. User-started local Codex must verify closed host, exact local staging/resources and backup/rollback, preserve old immutable evidence, leave other IIP prototypes disabled and record installed hashes. No automatic game launch/exit, hot reload, changes to settings/saves/other mods, or production release. If a preflight gate fails, leave the installation untouched and report BLOCKED. A later user-run merchant visual comparison is the intended acceptance question. Production BLOCKED.


## Visibility correction deployment — BLOCKED (2026-11-19)

Requested source 00c3e6782aba037088bebfa5bea3bfc8c9ae6d68,
checkout 9c98d7676e132af3de0b771f41d8aec925fd1425.
CI 44430338590 and 15 local S1 tests PASS.
Four-file staging manifest SHA-256
`b74b2683944c6500eb62bd52460a8a2cb74460546d8d79cacc508c5c0aff7433`.
Private config and authored PNG retain previous verified hashes.
Host closed, no active IIP and no observed Ctrl+Alt+F9 conflict.

Deployment stopped before backup creation or copying any game files.
The mandatory predecessor check expected the hash-verified disabled S1,
but ImmersiveInteractionPromptsNativeS1 was absent from the configured
Mods directory. No other ImmersiveInteractionPrompts folders were found.
The source or time of this external removal is unknown. This prevents
claiming restoration of the previous installed payload as verified here.
Archived previous payloads remain available outside loader paths.

No partial installation was made. Other mods, loader configuration,
saves/settings were not written. Reconcile the now-empty IIP baseline
before a fresh installation; the prepared replacement procedure must
record absence as its rollback state instead of assuming an installed
disabled predecessor. User explicitly required stopping on a failed
mandatory check, so this deployment reports BLOCKED.

## Visibility correction installed after archive reconciliation — 2026-11-19

**INSTALLED**, source `00c3e6782aba037088bebfa5bea3bfc8c9ae6d68`.
Manifest SHA-256
`b74b2683944c6500eb62bd52460a8a2cb74460546d8d79cacc508c5c0aff7433`.
The earlier BLOCKED result is superseded. User supplied the cleanup
restore manifest. Its S1 entry maps to the established installed folder;
all four archived predecessor files match both archive manifest and
the original installation hashes. Absence was explained by cleanup.

Installation used the verified current no-IIP baseline, preserving the
cleanup archive. The retired old divider path was resolved in that archive
for hash checking; S1 uses its own installed approved PNG. All four
new payload files matched, only one IIP is active. The 43 pre-existing
Mods files, loader configuration, saves/settings retained hashes.
Host closed throughout deployment. Runtime still PENDING.

Ignored evidence is in prepared-00c3e67. The local
s1-00c3e67-fresh-deploy.py --rollback checks closed host and exact
payload, then removes only S1 enabled.txt, returning to no active IIP
while retaining disabled S1 files. The cleanup archive and original
restore manifest remain available for recovering earlier prototypes.
No other prototypes were restored. Stop key remains Ctrl+Alt+F9.

## Visibility 0/3/4 runtime feedback — 2026-11-19

Installed source 00c3e6782aba037088bebfa5bea3bfc8c9ae6d68 matched
the four-file manifest after exit:
`b74b2683944c6500eb62bd52460a8a2cb74460546d8d79cacc508c5c0aff7433`.
Fresh UE4SS 83330635 log archived locally, SHA-256
`50666523074489105c8444ea2f23d9c357b0253e55e88fbe96aafa3e21fb42ee`.
User screenshot archived locally, SHA-256
`6790d7b9645eb6dcb78481e749ceefdaf36acf17de5371e18bdf365ee91a3411`.

WAITING was followed by READY; eight ATTACHED events all logged
root_visibility=0. No attachment failures were logged. These events
do not measure rejected earlier callbacks or first pixels. User still
sees a noticeable delay across prompts and considers it closer to
unacceptable than acceptable. The visibility correction has not
established acceptable appearance timing.

User did not press Ctrl+Alt+F9 this run. The log ends normally with
Event loop end, with no user_stop cleanup confirmation. Do not count
exit as a manual cleanup PASS. S1 remains installed and enabled;
this feedback-recording step changed no game files.

Visual requests recorded for subsequent design, without implementation:
place the interaction key vertically at the divider's centerline if
feasible at proportionate cost; reduce native localized action outline
to a thin appearance comparable to the Aphes caption. The screenshot
shows the current key alongside the lower action line and a visibly
heavier outline on the localized action. These requests may require
revising the current preserve-native-layout/font boundary. Their
mechanism and feasibility are open. No timing fix, layout change or
native font mutation is authorized by this record-only feedback.

## First-pixel onset timing — bounded source-only instrumentation (2026-11-19)

**Question:** Why did the upper Aphes/ornament appear noticeably later than
the native merchant action in the user's runtime observation, despite eight
successful attachments? The saved UE4SS log contains only `ATTACHED`
timestamps (all root visibility `0`), not earlier `CanShow` callbacks,
rejected guard states or any independent frame/pixel measurement.
The prior visibility correction did not fix the perceived delay.

**Cheapest sufficient evidence:** retain the accepted native S1 runtime path
and log a few milestones at its **existing** zero-input Blueprint
`CanShow` post hook, with one short user-screen recording as an independent
source for what pixels actually appeared. No lower-level native paint hook,
new selection scanner or preload architecture is justified before this.

**Research-only instrumentation:**
- `TRACE_FIRST_CALLBACK` — first delivered CanShow for each exact
  TipHUD path/address, including root visibility;
- `TRACE_PENDING` — first distinct eligibility failure or change of
  reason/root visibility, capped to **five** per widget;
- `TRACE_ELIGIBLE` — first native state passing existing guards;
- `TRACE_ATTACH_BEGIN` — immediately before the existing `decorate`
  call, followed by the existing `ATTACHED` or `ATTACH_FAILED`;
- Native guard outcomes, widget state, construction, asset loading,
  `CanShow` return and original input/action remain unchanged.
  At most **64** widget identities are traced per map; diagnostics
  reset after successful map-pre cleanup and after manual STOP.
  No polling, separate observer hook or timer; no retained UObject wrappers.
  This is a bounded logging overhead, not a performance-neutral observer.

The **UE4SS.log timestamp deltas** locate coarse intervals from callback
to eligibility and attachment, not true game input-to-paint,
GPU completion or a guarantee that the native action was on-screen.
They should not be subtracted from unrelated logs/recordings with
unknown clock alignment. More logging can perturb the critical path;
interpret a few-millisecond difference cautiously.

**Single bounded user-operated scenario (after a separately authorized
closed-host installation):** record one continuous native-size screen
capture at 60 FPS or faster if the user's existing capture facility
supports it, without changing game graphics/settings. Approach the same
merchant from outside prompt range for a first exposure and once again
after leaving range; include at least one direct interaction-free return.
If convenient in the same brief session, capture an object that formerly
appeared fast for contrast. Finish by pressing `Ctrl+Alt+F9`, then exit
the game voluntarily. Local Codex can archive the exact fresh UE4SS log
and capture with hashes. Frame-to-frame measurement is between **first
visible native action/button** and **first visible upper Aphes/divider**:
use actual frame timestamps for variable FPS, or delta frames / recorded
FPS for fixed-rate capture. The recording's displayed FPS is not
automatically the encoder's stored frame rate; do not count synthetic
interpolated frames as native paint evidence.

**Decision table:** 
- First `CanShow` **after** the lower native action appears: the hook
  arrives too late for same-frame decoration; extra caching alone
  cannot fix first paint.
- `CanShow` early but `TRACE_PENDING` remains until late: identify
  which guard/host state is late before changing eligibility.
- `TRACE_ATTACH_BEGIN→ATTACHED` is long: creation/resource path
  is a plausible cost; consider narrower preinitialization.
- `ATTACHED` precedes the visible ornament by multiple recorded
  frames: Slate/render timing or video synchronization needs checking.
- Normal second approach reuses same widget without new attachment:
  distinguishes a cold-attach problem from recurrent show/hide delay.

**Offline verification:** exact code candidate
`946f4d1e6705aaa6ab9e9b1a793f7ae4ae9f8252`,
[GitHub Actions #44435907441 PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44435907441),
including **18 S1 tests** (three new trace assertions), and **621
tests over 62 batches** in the repository test runner. Tested source
has no extra native setter or input/write surface. CI is not gameplay evidence.

**Limits:** No visual latency claim from logging alone. No proof of
generic owner/selection from CanShow alone. No native layout/font/button
change is part of this study. Stop after the one controlled comparison
with causal milestone evidence, or report `INCONCLUSIVE` with the
single missing measurement. The currently installed S1 remains the
previous code until an independently authorized new installation.
Production BLOCKED.

## Authorization for timing diagnostic installation — 2026-11-19

User explicitly authorized installing the bounded S1 timing instrumentation
at exact tested source `946f4d1e6705aaa6ab9e9b1a793f7ae4ae9f8252`, CI
[44435907441 PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44435907441).
This is approval to deploy **only**, not evidence that deployment or
runtime measurement has occurred. User-operated local Codex must confirm
actual checkout, installed active predecessor `00c3e67` and exact prior
manifest, external font/divider, closed host, backups and a checked rollback
plan **before** replacing any bytes. Preserve all adjacent mods, prior
research prototypes, loader configuration, saves and settings. Do not
launch/terminate Asterigos or use hot reload. If a preflight check fails,
leave installation unchanged and report BLOCKED rather than guessing.

After successful installation the user, not Codex, runs a short
first-and-repeat merchant video test and manual `Ctrl+Alt+F9` STOP;
collect a fresh exact UE4SS log and capture frame evidence. No timing
value, layout change, cache expansion, product acceptance or release is
preapproved. Production remains BLOCKED.

## Timing diagnostic installed — 2026-11-19

**INSTALLED** from `946f4d1e6705aaa6ab9e9b1a793f7ae4ae9f8252`, with
[offline CI PASS #44435907441](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44435907441).
The clean local research branch fast-forwarded to remote
`0f4798fb1c90a3771ba6bd775bc2d79432bcb41e` before deployment.
The active predecessor matched all four files in the saved
`00c3e6782aba037088bebfa5bea3bfc8c9ae6d68` manifest
`b74b2683944c6500eb62bd52460a8a2cb74460546d8d79cacc508c5c0aff7433`
and its empty activation marker.

Preflight confirmed Steam build 12996889, the pinned host executable,
UE4SS 83330635 DLL/settings, external UEHelpers, private Aphes.ttf,
approved divider PNG and the local config's resolved asset paths.
The Steam manifest had changed since the previous preparation. Its app ID,
install directory, installed state and build still matched, and its freshly
recorded hash remained identical throughout deployment.

The deployment atomically replaced only `Scripts/main.lua`. The temporary
file carried a restrictive Windows ACL. The post-install check detected
it, restored the Scripts directory's inherited permissions and verified
that the new file has the same access entries as the neighboring layout
script and is readable from the sandbox. SHA-256 of the installed
four-file payload manifest is
`16b4132fcc70309ce63903e3736931856aa30b992c70077f5ce40029d017b080`.

| Installed file | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `982256b7cc91da4c65801f85f7f8dd66cba701490c18c257a3d8b7c86f3dfd54` |
| `Scripts/IIPS1Layout.lua` | `65f69b106aac838446f945a6ba24a31e0463e6b9c57e8feb7ad91b9a46371d15` |
| `Scripts/IIPS1Config.lua` | `57ac954c99f3a1ca8b9f920956d6a07f0f299ce419c7851b309910b16e565383` |
| `Assets/aphes_divider_256x32.png` | `b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969` |

S1 is the only active IIP. Before/after inventories match for all
12,524 other files under ue4ss (including 43 files in Mods), 26 files
at the Win64 root, 11 pak-mod files, 29 configuration files and
16 save files. The archived pretest UE4SS log SHA-256 is
`50666523074489105c8444ea2f23d9c357b0253e55e88fbe96aafa3e21fb42ee`.

The verified backup outside the loader contains all four predecessor
files and its activation marker. The local `.local/s1-946f4d1-deploy.py
--rollback` checks closed host, backup and installed inventories and
restores the prior main.lua with S1 still active. A round trip through
the same swap routine, including ACL inheritance, on a copy restored all
five hashes. Live rollback
was not executed. Private receipts, inventories, backup and archived
log are in ignored `install-946f4d1`.

Runtime PENDING, production BLOCKED. Game process stayed closed. For
the measurement, record one continuous 60+ FPS capture if available.
Approach the same merchant from outside range, walk away and return
without interacting. Capture the first visible native action/button,
Aphes line and divider on both passes. Press `Ctrl+Alt+F9`, exit
normally and retain the original video and fresh UE4SS.log before the
next launch. Video determines first visible frames. Log timestamps
measure milestones within the callback and attachment sequence.

## Merchant timing result — 2026-11-19

One continuous ShadowPlay recording covers the user's first and repeat
approaches to the same merchant, then the fresh UE4SS session log records
manual STOP and normal exit. Installed `main.lua` matched the diagnostic
hash above after exit. Recording SHA-256
`74a06c07f9e98e05b74764b56d0ad15540746d21d949410f494918269ba197de`.
Archived runtime log SHA-256
`dcf0c26b8078a71a3e1c2569527b9b29c842d810f873e3bf9ce67414c5b6cad2`.
The source video stays external. The log and frame crops stay in the ignored
`install-946f4d1` directory.

Frame indices are zero-based in the decoded recording. Times are video PTS.
The recording has variable frame timing, so intervals use PTS.

| Approach | First native action and button | First Aphes and divider | Visible delay |
| --- | --- | --- | --- |
| First | 438 / 7.791878 s | Both visible with distortion at 452 / 8.025211 s, both clean at 453 / 8.041878 s | 14 recorded frames / 233.3 ms to first visible, 15 / 250.0 ms to clean |
| Repeat | 774 / 13.392089 s | 774 / 13.392089 s | 0 recorded frames |

Frames 437 and 773 show no prompt. Frames 438–451 show the native
prompt alone. Frame 452 contains both decorative elements and doubled
and warped text. The source of the distortion was not established.
Recorded frames do not establish engine-rendered frame counts.

The log has one attachment sequence, for widget 1. First callback at
04:41:44.5892695 had root visibility 4. PENDING followed at
04:41:44.5894935 with `native_measurement_unready`. ELIGIBLE at
04:41:44.7894344 had root visibility 0, 200.165 ms after the first
callback. ATTACH_BEGIN followed 0.043 ms later. ATTACHED at
04:41:44.8199537 was 30.476 ms after ATTACH_BEGIN and 230.684 ms after
the first callback. The font and texture events occur during attach.
The repeat appearance has no second attachment in the log, consistent
with reuse of the existing children. `CLEANED reason=user_stop
own_widgets=0` confirms manual cleanup in this session.

Most measured S1 time elapsed before attachment, while the native layout
plan was ineligible. The pending reason aggregates the layout checks and
does not identify the late input. Root visibility 4 is already allowed.
The two clocks were not aligned to a shared frame marker, so these results
do not isolate callback-to-first-pixel or post-attach render time.
If the cause must be narrowed further, distinguish which existing layout
input first becomes valid before considering changes to eligibility or
resource creation. Production remains BLOCKED.

## Early pre-attach feasibility — source review (2026-11-19)

**Decision sought:** Can S1 prepare the two own children before the first native
prompt paint, so first exposure behaves like the already observed repeat?
**Scope:** repository/source and accepted-evidence review only; no payload change,
local/game inspection, deployment or runtime observation. Reviewed at branch
head `77a6f359902bf49f9b4325be31b8ae15b2497fce`.

### What is established

1. The merchant timing test had one first-attach sequence and none on repeat:
   first native action at video PTS 7.791878, own elements at 8.025211
   (clean at 8.041878); repeat showed both in the same *recorded* frame.
   In the log the first `CanShow` reached `native_measurement_unready`
   200 ms before `TRACE_ELIGIBLE`, then attachment took ~30 ms.
   The video and log clocks have no alignment. No claim about engine frame
   boundaries, initial `CanShow` relative to first native paint, or the
   particular failed measurement follows.
2. Current `Scripts/main.lua` already separates native structural guards from
   `Layout.plan()` in `native_candidate()`. The recorded
   `native_measurement_unready` necessarily means that, at that callback,
   the exact TipHUD class, native TextBlock, drawability, nonempty text,
   native WidgetTree/CanvasPanel_6, original text slot, original RetainerBox_0
   and icon slot passed their existing checks. Only the *combined* geometric
   plan then failed. Thus **tree/slot availability is not the same as
   successful measured layout**. The combined reason does not prove that
   `GetDesiredSize()` specifically was the invalid input.
3. Current `decorate()` has an avoidable coupling: it requires the final
   `layout` before creating/binding the private Aphes font, divider texture,
   TextBlock/Image and two canvas children. `make()` already sets each own
   child to `Collapsed` while constructing it, but `decorate()` switches
   both to drawable immediately after `place()`. There is no separate
   pre-attach/commit stage yet. The current `observe()` is driven only by
   post-only `CanShow`; its native selection/show semantics must remain
   untouched.
4. **Previously observed acquisition route:** on the pinned host and UE4SS,
   global `BeginPlayPost` produced 34 ready exact actor → ExtendedWidget →
   TipHUD triples at normal save load: six Open, 18 Take, ten Check. Earlier
   exact parent `BaseGameEventObject_BP:ReceiveBeginPlay` and its widget
   getter/cast chain also passed a scoped natural Open experiment. These are
   credible early identity routes **for verified families**, not evidence
   that the merchant belongs to one of them or that the callback precedes
   the merchant's first native pixels. [Shared verified evidence](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/VERIFIED_RUNTIME.md#multi-action-native-owner-observation--2026-11-06)
   and [parent-call review](../open-binding/ROUTE_REVIEW.md).
5. UE4.27 documents `Collapsed` as non-rendering and occupying no layout
   space. Thus attaching *collapsed own children* is a defensible minimal
   containment hypothesis, not a game-tested no-side-effect guarantee.
   `CanvasPanel_6` sits inside native `HorizontalBox_4`, so making own
   children drawable may affect parent desired size/position; the layout
   must still be verified. UE4.27 also documents that `GetDesiredSize()`
   requires underlying Slate construction and at least one prepass, and
   `ForceLayoutPrepass` is not proof that all native layout/consumer
   inputs are ready. Do **not** proactively force host prepass as a
   speculative fix.
   [UE4.27 visibility](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SlateVisibility?application_version=4.27),
   [widget/prepass API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Widget?application_version=4.27),
   [Slate layout](https://dev.epicgames.com/documentation/en-us/unreal-engine/slate-architecture?application_version=4.27).

### Minimal prospective implementation shape — NOT READY

Separate (a) exact TipHUD/WidgetTree/CanvasPanel/stock-slot identity validation,
(b) creating/configuring *only two owned Collapsed children* and the existing
shared private resources, (c) computing reliable final geometry from native
inputs, and (d) activating the children no later than native first paint.
Preserve native action, button, input remapping, visibility, CanShow return,
show/hide, native slots/font and cleanup ownership. Do not assume the
serialized designer X=88 is the live position: earlier Open runtime measured
X=38. No actor scan, per-frame polling, screen prehide, early native
visibility change or duplicate prompt layer is part of this direction.

A pre-attached but still Collapsed label is **not a UX fix** if the native
action appears before a reliable final geometry/activation; that timing is a
separate evidence gate. Likewise, attaching while Collapsed is not enough if
turning it drawable shifts/clips stock UI. A neutral `ACTION` remains a
technical font check, not translated Aphes.

### Remaining smallest evidence and stopping rule

**BLOCKED for behavior change; static first-step complete.** Establish, using
existing local retained cooked/UHT exports and earlier observer evidence if
available, whether the **specific merchant TipHUD** is reachable before first
show through an already verified actor/ExtendedWidget/BeginPlay route; which
initial native text/slot/icon geometry fields are valid at that point; and
whether an unmodified native show can follow preparation before first paint.
Source-only output should identify the exact class/callsite and classify
proven versus unknown. Do not infer merchant coverage from Open/Take/Check.

If that evidence is insufficient, request a *separately authorized* bounded
read-only runtime observation of merchant early identity and the earliest
geometric inputs. Only after a positive early route and a credible first-paint
placement/activation path consider a narrow research-only pre-attach candidate
with offline checks and separate authorization for installation. Stop or
reconsider the mechanism if it requires new brittle host interception or
changes to native interaction semantics. Production remains BLOCKED.

## Merchant early owner and layout — local evidence (2026-11-19)

Review baseline `d391de9455c4f99e03f38511e7fda5756e3c688f`.
The local review used existing logs, retained TipHUD exports and two
targeted cooked NPC exports from Steam build 12996889. No live observation.

**Selected owner.** The [2026-11-09 selected-native survey](../world-space/tiphud-render-suppression/README.md#selected-native-survey--один-игровой-сеанс-2026-11-09)
logged `NPCInteract_Bp_C`, tag `Talk`, Screen `TipHUD_C` and nonempty
localized text (line 810, log SHA-256
`cdee10dc5436b35e5ffd66f46a37926ecf98a964eee15670717947a485e49daa`).
The reader checked reciprocal ownership of `TipHUDArgument` and
`ExtendedWidget`, then called `GetUserWidgetObject`. It required
`bVisible` and `bAddedToScreen`, so this is a selected/shown sample.
The S1 timing run records no actor or widget identity that can join it to
that earlier instance. This establishes a live NPC Talk route, with the
identity of the specific filmed merchant still open. Another line in the
same survey reports `Interact` on the same class.

**Cooked startup order.** The `NPCInteract_Bp_C:ReceiveBeginPlay` wrapper
enters its graph at 465 and calls `BaseNPCInteract_BP_C:ReceiveBeginPlay`.
The parent enters at 26 and calls `BaseGameEventObject_BP_C:ReceiveBeginPlay`
before character attachment. That graph enters at 92, reads the actor's
`ExtendedWidget.GetUserWidgetObject` at 102, and casts to `TipHUD_C`
at 144. Its component template assigns `TipHUD_C` as `WidgetClass`.
The widget getter reads the current pointer. The graph guards its cast
and supplies no live result for this merchant. Separately,
`BaseNPCInteract_BP:ExecuteAction` has a `SetNPCTip` branch (call at
1225) that writes `TipHUDArgument.msgTag`. A BeginPlay class match alone
therefore cannot establish the final Talk tag. The two NPC graph export
SHA-256 values, in child-to-parent order, are
`c1a14d000981667054c507d672d180e53073105e9621fdbeeef706c94822f0ed` and
`776fd47a30d000018ae91dd5125cefda12a5d914f227a47c849188987b93e07d`.

The existing global `BeginPlayPost` is the earliest supported candidate
for acquisition on this route. Open has a stronger precedent than mere
class load: [an actual unadded Screen TipHUD at BeginPlayPost](../../../docs/VERIFIED_RUNTIME.md#early-tiphud-identity--bounded-open-result-2026-11-08)
matched the later selected instance, and its brush changed before selection.
There is no equivalent early identity sample for the filmed merchant.
S1's own callback currently only registers the `CanShow` hook, so its
`READY` marker establishes function availability. The first observed S1
`CanShow` reached the layout guard with the tree intact. Cooked
`SetupTipMessage_Proxy` calls native `SetupTipMessage2` at 713 in the
TipHUD graph. `CanShow` calls the native parent predicate and checks input
mode. Neither exported body establishes native caller order against
Screen insertion, Slate prepass and first paint.

| Readiness layer | Current S1 requirements |
| --- | --- |
| Tree and slot identity | Exact `TipHUD_C`, valid stock `TextBlock_89`, reciprocal outer/parent relationships with the native WidgetTree and `CanvasPanel_6`, original autosized text CanvasPanelSlot, exact `RetainerBox_0` sibling with a CanvasPanelSlot. |
| Presentation and content | Drawable root and stock visibility, positive opacities, enabled root, nonempty localized stock text. Needed to commit to the current presentation. |
| Final placement | Live desired width/height of the native label, position/alignment/anchors and font size, plus icon position/alignment/anchors, size and autosize contract. `Layout.plan()` also checks ranges. |

The first timing callback passed the first two rows. Its combined
`native_measurement_unready` leaves every input in the third row
unresolved at that callback. The missing evidence is the first valid
tuple for the final localized action and icon, which individual guard
blocks it, and whether the tuple is already stable before the first native
frame. An early nonzero desired size may still describe a placeholder
or a prior presentation.

**Engineering gate: BLOCKED.** A plausible minimal implementation would
use the existing actor callback to validate exact actor/component/widget
and tree identity. It would create only the two owned children, hidden
before insertion with `Collapsed`, use owned fixed slots and prepare
private resources only when the verified donor/asset contracts hold.
At a proven final-geometry boundary it would revalidate identity, place
the children while collapsed and make them hit-test invisible together.
Current S1 proves construction from collapsed objects and cleanup after
ordinary attachment, while early insertion and the parent layout after
activation remain unverified. Limit a future trial to the exact owner
and its two children. On missing inputs leave stock behavior in place,
and on replacement, map change or manual stop remove only owned
children. No change to native slots, text, hint, input, visibility or
`CanShow` result is required by this design. First-paint activation is
blocked on the final-writer/consumer order. Acceptance would require
first-appearance frame evidence, equivalent native layout and cleanup
for the explicitly bounded case. The repeat timing result alone cannot
establish cold-start acceptance.

**One next experiment, subject to separate approval.** Run one read-only
load and first approach to the same merchant. Filter the existing
`BeginPlayPost` by exact NPC interaction class, collect a bounded
actor/component/widget identity and structure snapshot, and correlate
only the filmed Talk widget with the existing `CanShow` callback. At
both boundaries log screen-added/visible flags, native text readiness,
the first failed `Layout.plan()` check and the first valid inputs.
Keep a short capture of that approach. Frame claims across clocks need
an established common marker. Stop after the first valid Talk sample
or a missing early match on that approach. A matching early tree
justifies considering hidden preparation. If the first usable geometry
still arrives late, preparation alone cannot remove that wait and the
existing candidate stays blocked. No additional native hook, object scan,
polling, forced prepass or runtime writer is needed for this observation.

## Merchant read-only observer installed (2026-11-20)

Source `00d80fe6a016422b42df0cfa0c470166f8e19bdb`.
Three observer and 18 S1 tests passed locally. The full Windows runner
stopped on the existing resident World manifest path-separator check.
[Full hosted CI PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44614488916).

The observer replaces only installed `Scripts/main.lua` for this run.
The deployed entry bundles the reason-reporting layout function from
the same commit. SHA-256 of the installed entry is
`807a3b3bd6cf023543247a2cecaf0781c8c6a5107f397f737fa6347e3a4413d2`.
The payload manifest SHA-256 is
`c76359be2e346f0b4944c0185e71bf9cbdc400dc06bdad71f9eceeefcc8e0375`.
Other mods, loader, settings and saves were hash-checked before and
after deployment. The local deployment receipt and rollback backup
are outside the loader. The same swap routine restored the full active
`946f4d1` predecessor on a copy, including permission inheritance.

The observer uses existing BeginPlayPost, CanShow and map-pre boundaries.
It only observes exact NPC interaction actors, stores scalar identities
and joins a later Talk callback to its original widget by address, path
and reciprocal component ownership. `BEGIN_MISS` records unavailable
early identity. A missing early identity stays unpaired. For a joined
Talk widget the log records the first CanShow snapshot, first layout
rejection, first valid dimensions/slots and first presentation-ready
sample when available. Geometry sampling stops at eligibility for that
widget. There are no runtime writes, timers, scans or polling.

Launch normally, load while outside the merchant's prompt range, record
one approach until the stock prompt appears, then exit normally. Only
stock UI is expected during this run. Preserve the fresh UE4SS.log and
short capture before relaunching. Use the `IIP_S1_MERCHANT` markers for
event order. They carry no first-pixel timestamp. Runtime PENDING,
production BLOCKED.

## Merchant read-only observer result (2026-11-20)

One user-run approach, using installed observer entry SHA-256
`807a3b3bd6cf023543247a2cecaf0781c8c6a5107f397f737fa6347e3a4413d2`,
verified after normal exit. Archived UE4SS 83330635 log SHA-256
`5a1a878d7e08a5513864fb19df52e931091112dbf0fc082a35b3e712ff1ab3f4`.
External recorded video SHA-256
`c2900ff9de17cef9a0f633d5922b10286a341ff32f5bb455234363aa8cf39984`.

Map 3/id 1 matched the same `NPCInteract_Bp_C` owner, component and
`TipHUD_C` in `BeginPlayPost` and later `CanShow`. The tag was
`Interact` at BeginPlay and `Talk` on the matched CanShow path.
At the early sample the component was neither added to Screen nor
visible. The early tree and both stock slots passed structure checks.

| Event | Local log time | Desired text size | Text slot X | Icon slot size |
| --- | --- | --- | --- | --- |
| `BEGIN_SAMPLE` | 00:04:11.1372659 | 0×0 | 88 | 128×128 |
| `CANSHOW_FIRST` | 00:04:30.1758463 | 0×0 | 88 | 128×128 |
| `LAYOUT_FIRST_VALID` | 00:04:30.3754683 | 167.5×37.5 | 38 | 38×38 |

At first CanShow the component was already Screen-added and visible.
The first failed guard was `desired_size`, with `GetDesiredSize()`
returning zeros. The position and icon size also changed before the
first valid sample. Font size 22, alignment, anchors and icon autosize
matched across these samples. First CanShow was 19.039 s after the
BeginPlay snapshot. First valid was 199.622 ms after first CanShow
and 199.555 ms after `LAYOUT_FIRST_REJECT`. These are observed callback
intervals. They do not identify the underlying writer, first Slate
prepass, or intermediate changes between samples.

In the video the native button and «Поговорить» first appear together
in zero-based frame 338, PTS 6.124356 s. Frame 337 has no prompt.
Only stock UI was expected. Video and log lack a common frame marker,
so the video establishes the appearance independently of the Lua
callback order. This run does not provide an on-screen S1 latency.

**Gate:** Early tree acquisition is verified for this merchant.
Early insertion of collapsed children and unchanged layout after
activation remain unverified. Moving attachment work earlier can
address that stage only. The existing final-placement plan still has
an observed ~200 ms wait even with the read-only probe and no S1
decoration creation. BeginPlay geometry and its text tag are unsuitable
defaults for final placement. Before implementing a same-frame path,
determine whether an existing host boundary can provide the final
Talk text/slot state and usable measured extent earlier. The probes
so far do not justify forcing prepass or choosing a new runtime hook.
Production remains BLOCKED.

The live one-run observer was rolled back after the user exited.
The complete active `946f4d1` inventory, activation marker and
inherited script access entries were verified. Restored manifest
SHA-256 `16b4132fcc70309ce63903e3736931856aa30b992c70077f5ce40029d017b080`.

## Fixed Talk template installed (2026-11-20)

User authorized a one-merchant research run and adopted a divider width
independent of action, text and input geometry. This run uses 142.375 widget
units, the divider width from the measured merchant layout, with the
original 8:1 PNG aspect ratio. The Aphes preview remains `ACTION`.

At `BeginPlayPost`, the previously observed NPC interaction actor route
in the merchant's sublevel must resolve its exact hidden, not-yet-added
`ExtendedWidget` and original `TipHUD_C` tree. Only the two owned
`Collapsed` children are constructed and inserted with fixed slots.
Their resources and geometry are ready before showing. At the paired
post-`CanShow`, owner, widget and tree identity are checked again.
The native component must be shown and the stock drawable caption must
match Russian Talk. The callback changes visibility only on the two
own children, with no geometry sample or layout planning. Other prompts
stay stock in this candidate. Missing early preparation stays stock.
An ambiguous owner, identity change or fault stops the trial and uses
owned cleanup. Existing map cleanup and `Ctrl+Alt+F9` remain available.

**Research gate only.** Early identity is observed for this merchant.
The trial asks whether fixed placement and earlier preparation produce
the same first recorded frame as the native action, while preserving
native coordinates, button and show/hide. The UMG/Slate timing and effect
of early insertion on native layout still require video and log evidence.
Generic Talk or other action coverage is outside this trial.

Exact source `9b97a5456b5395f3dee5345b19cfc074c5d01585`.
Deployment assembled `Scripts/main.lua` by enabling its explicit
`TALK_TEMPLATE` research switch. Entry SHA-256
`a89784277b22d797eda63acc39205b81e4527f0011ac2b029d6cfb9c6d4b34c0`.
Four-file manifest SHA-256
`a05f39813c642d71670c83d464b1687043b701e3092af9f8210a3985b3f6f5d2`.
20 S1 tests and three observer tests passed locally.
[Full hosted CI PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44617091992).
Only the active `main.lua` was swapped with the game closed. Other mods,
loader files, settings and saves matched their preflight hashes.
The live predecessor was `946f4d1`. Its complete active payload was
backed up outside the loader and restored on a copy, including the
activation marker and permission inheritance.

Launch normally, load outside prompt range and record a single first
approach to the same merchant. Capture the first native caption/key,
header and divider, then withdraw until the prompt hides. Press
`Ctrl+Alt+F9`, exit normally and keep the original video and fresh
UE4SS.log. The log should show `TEMPLATE_PREPARED` from the early path
and `TEMPLATE_FIRST_CANSHOW` / `TEMPLATE_SHOWN` from the show path.
Runtime PENDING, production BLOCKED.

## Fixed Talk template runtime result (2026-11-20)

One first approach and withdrawal at the same merchant on the fixed
Talk candidate `9b97a5456b5395f3dee5345b19cfc074c5d01585`. Installed
entry hash matched after normal exit. Archived UE4SS 83330635 log SHA-256
`666b3d434fd047786ce0e6f7696d96648b1be54dbd16ef233dc7f7c106135632`.
External video SHA-256
`032d21348aa94b7758df5fd8ff21337f8ffaa947b27f9b97b40079f37918d4`.

At 00:21:58.9665429, `BeginPlayPost` started preparation.
`TEMPLATE_PREPARED own_children=2 collapsed=true` followed 28.608 ms
later, 16.006 s before the first observed CanShow. That CanShow at
00:22:15.0006931 logged `eligible=false reason=native_text_variant`.
Given the guard order, the matched actor and live action were Talk,
the component was added and visible, and the stock caption passed the
drawability and nonempty checks. Its readback differed from the exact
Russian string; the actual value was not logged.
`TEMPLATE_SHOWN geometry_reads=0` followed 204.013 ms later.

| First appearance | Zero-based recorded frame | Video PTS |
| --- | ---: | ---: |
| Native action/button, distorted transition | 383 | 7.159822 s |
| Native action/button, first clean frame | 384 | 7.176778 s |
| Aphes and divider | 396 | 7.376244 s |

Both elements were 13 recorded frames / 216.4 ms behind first visible
stock, or 12 frames / 199.5 ms behind its first clean frame. On withdrawal
the full composition is visible at frame 490, distorted at 491, and
entirely absent at 492. The log has no `TEMPLATE_COLLAPSED` marker,
so this establishes joint visible hide without determining which
native lifecycle transition hid it. Manual STOP logged
`CLEANED reason=user_stop own_widgets=0` before normal exit.
Video and log were not synchronized to a common frame marker.

Early preparation and fixed rendering worked in this case. Same-frame
appearance failed because the first CanShow did not pass the candidate's
exact-caption gate. The trace locates the remaining wait in that gate
instead of a geometry sample or creation on the show path. The bounded
next hypothesis is that matched merchant identity, Talk and the existing
native show guards suffice to use the known template without gating
that trial on the exact caption readback. This requires a separately
authorized candidate and a first-frame/withdrawal comparison to check
for premature or misplaced decoration. Production remains BLOCKED.

## Fixed Talk template tag-based show installed (2026-11-20)

User authorized the same-merchant experiment with the caption gate removed.
The show path uses the existing paired widget identity, `Talk` and native
visibility/opacity/enabled checks. It reads neither localized caption
contents nor geometry. Preparation, fixed slots, divider width 142.375,
`ACTION`, and owned cleanup use the previous candidate's path.
The mocks trap caption and geometry reads, check that a different tag stays
collapsed, and check visibility on the first eligible Talk callback.
First paint and alignment still need in-game evidence.

Exact source `8f1231d4bca04e8c2f73d4ab9903ceac67809c72`.
Installed `main.lua` with `TALK_TEMPLATE` enabled has SHA-256
`85f0d163c784b9e8f7b67b54c811845c324a9d4511cbb60c32dd7fc4dedddcff`.
Payload manifest SHA-256
`00d53aed6be0e97628cfa1fb9a75b4003d0aa94f3da23bfd349c72585f4d84b5`.
20 S1 tests and three observer tests passed locally.
[Full hosted CI PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44619139610).

Only the active entry was replaced, with the game closed. Other mods,
loader files, settings and saves matched their preflight hashes.
Backup is outside the loader. The rollback round trip on a copy restored
the active `9b97a54` template and its full manifest, including
activation-marker bytes and inherited script permissions.

Use the same merchant and capture one first approach from outside
prompt range, followed by withdrawal, `Ctrl+Alt+F9` and normal exit.
Compare the first recorded native prompt and own elements, alignment
and hide. Collect fresh UE4SS.log for `TEMPLATE_PREPARED`,
`TEMPLATE_FIRST_CANSHOW`, `TEMPLATE_SHOWN` and manual cleanup.
Runtime PENDING, production BLOCKED.
