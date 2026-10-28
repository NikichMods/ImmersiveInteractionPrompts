# Immersive Interaction Prompts

A planned standalone interface mod for **Asterigos: Curse of the Stars**.

Contextual world-object prompts will gain a visually prominent upper line in fitting Aphes-world lettering, with a clearly readable localized interaction action below. A delicate divider is under consideration. The actual action, native input icon and prompt visibility must stay correct.

Examples: pick up, open, read, descend; other context actions only when supported by the verified presentation path.

**Status: research; production gate BLOCKED. No production build or release exists.** A [minimal CanShow observer](research/interaction-prompts-owner/can-show-state/README.md) read live text/state from three TipHUD instances; it is now disabled after the successful first observation. Native-array observation and UEPseudo investigation are deferred. Live final writer, input texture producer and a usable UMG glyph path remain open. Invented decorative symbols must not be presented as a genuine fictional language.

- [Requirements](docs/REQUIREMENTS.md)
- [Status](docs/STATUS.md)
- [Research plan](docs/RESEARCH_PLAN.md)
- [Verified runtime and evidence gaps](docs/VERIFIED_RUNTIME.md)
- [TipHUD layout and visual prototype readiness](research/interaction-prompts-owner/VISUAL_READINESS.md): additive UI path selected; the Aphes-specific font bridge remains blocked.
- [First stock-font child experiment](research/interaction-prompts-owner/ui-child/README.md): one OPEN label created, visibly rendered and manually removed in-game; original action/icon stayed in place. Probe disabled after the completed test. Aphes remains deferred.
- [Resource-free divider result](research/interaction-prompts-owner/DIVIDER_READINESS.md): UImage Box line visibly rendered, both added elements detached through user control; probe disabled. Aphes remains deferred.
- [Local Aphes PNG experiment](research/interaction-prompts-owner/png-header/README.md): glyph image and dynamic Texture2D import source prepared, not installed/run. No font/image payload distributed.
- [Dynamic UMG font assessment](research/interaction-prompts-owner/DYNAMIC_FONT_READINESS.md): shared replacement rejected; private Template UFont copy is a source-supported candidate before a C++ bridge. No new runtime result.
- [UFont Template creation probe](research/interaction-prompts-owner/font-template/README.md): one-copy native storage inspection source prepared; no font-data/UI writes or installation.

This module will have its own version and independently installable payload if implementation proves feasible.

## Independent repository

[Migration and exact source provenance](docs/MIGRATION.md) · [Shared Asterigos Research](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/RESEARCH_INDEX.md) · [Local external dependencies](docs/LOCAL_DEPENDENCIES.md). Original release URLs and frozen artifacts remain in AsterigosMods.
