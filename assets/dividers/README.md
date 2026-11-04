# Minimal braided divider — research visual asset

Authored ornament for the two-line world-space interaction prompt in *Asterigos: Curse of the Stars*. This is an **approved design** (2026-11-05); the research successor is installed and awaits its World-space user test.

## Files

- `aphes_divider_256x32.png`: intended game texture; **256×32 RGBA**, transparent background, antialiased.
- `aphes_divider_256x32.svg`: editable vector source (same 256×32 viewBox).
- `aphes_divider_preview_dark.png`: standalone dark-background preview only (opaque RGB; **not** the game texture).

The design is deliberately monochrome and flat: white ~3 px shaft, ~1 px dark outline on each edge, gently tapered symmetric terminals and a small, centered two-strand braided knot. No gradient, shadow, glow, faux relief, game-owned glyph or host asset.

## Intended use and limits

The [source-only successor](../../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md)
replaces the research prototype's imported **stock 570×16 ornament** with this
authored transparent PNG; authorized installation is complete, in-game testing remains pending.
The latest accepted research editor values are recorded in [live-editor-style](../../research/interaction-prompts-owner/world-space/live-editor-style/README.md): divider length 300 and vertical multiplier 2.5, among other settings. These refer to the old source texture and **must not be copied blindly** to the new image.

The asset geometry and alpha are checked offline; its sampling, world-space apparent pixel thickness, subpixel shimmer and halo/faded appearance are **not** runtime-verified. The mod's original localized action, native hint and interaction behavior must remain unchanged. Approval of the drawing does not establish World-space visual acceptance, readiness to install, VERSION change, or permission to merge experimental runtime behavior into `main`.

### Exact source-file SHA-256

```
b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969  aphes_divider_256x32.png
6ed91c02d5b275282494759d5d8992b9faed4f1be1b6eb8dcb02096006881fa7  aphes_divider_256x32.svg
e10ab64be0f7ced7fc338fe7045bbf030670ff4b08348d51d7e1431bb8827221  aphes_divider_preview_dark.png
```

All three image/vector files are newly authored for this project; the earlier game screenshot mockup is intentionally excluded from Git. These software-supporting authored graphics are covered by the repository MPL-2.0; no game-owned graphics are included.
