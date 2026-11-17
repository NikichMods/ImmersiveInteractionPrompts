# Native TipHUD S1 — compact C source-only pilot (2026-11-17)

**State:** SOURCE-ONLY research candidate, not installed or runtime-accepted.
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
Do not touch the installed game until separately authorized.
After source/CI review and exact-hash installation with game closed and
rollback ready, the human visual check should cover one Open, Take and
Check/Read natural object when available, direct switching/return,
keyboard/gamepad remapping, light/dark background, first visible frame
and load of another save/map. Record \`IIP_S1\` diagnostics and user
visual verdict. Unsupported cases must leave the stock prompt intact.
An offline PASS is not permission to merge to main, mark VERSION
released, or claim production readiness.
