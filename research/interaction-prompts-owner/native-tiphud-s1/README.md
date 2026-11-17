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
