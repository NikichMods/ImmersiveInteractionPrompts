# Immersive Interaction Prompts

A planned standalone interface mod for **Asterigos: Curse of the Stars**.

Contextual world-object prompts will gain a visually prominent upper line in fitting Aphes-world lettering, with a clearly readable localized interaction action below. A delicate divider is under consideration. The actual action, native input icon and prompt visibility must stay correct.

Examples: pick up, open, read, descend; other context actions only when supported by the verified presentation path.

**Status: research; production gate BLOCKED. No production build or release exists.** Native Aphes text through a private transient UFont passed OPEN→READ and manual cleanup in one TipHUD prompt, with user visual confirmation. The probe is disabled. Composition, wider lifecycle/compatibility and production action mapping remain open. Native-array observation/UEPseudo work stays deferred; technical glyph strings are not verified Aphes translations.

- [Requirements](docs/REQUIREMENTS.md)
- [Status](docs/STATUS.md)
- [Research plan](docs/RESEARCH_PLAN.md)
- [Verified runtime and evidence gaps](docs/VERIFIED_RUNTIME.md)
- [TipHUD layout and visual prototype readiness](research/interaction-prompts-owner/VISUAL_READINESS.md): additive native glyph path verified narrowly; final composition and full lifecycle remain open.
- [First stock-font child experiment](research/interaction-prompts-owner/ui-child/README.md): one stock-font OPEN label visibly rendered and manually removed; original action/icon stayed in place. Completed prerequisite, probe disabled.
- [Resource-free divider result](research/interaction-prompts-owner/DIVIDER_READINESS.md): UImage Box line visibly rendered, both added elements detached through user control; completed prerequisite, probe disabled.
- [Local Aphes PNG experiment](research/interaction-prompts-owner/png-header/README.md): glyph image and dynamic Texture2D import source prepared, not installed/run. No font/image payload distributed.
- [Dynamic UMG font assessment](research/interaction-prompts-owner/DYNAMIC_FONT_READINESS.md): shared replacement rejected; private Template UFont route subsequently passed the bounded Aphes rendering experiment without a new C++ bridge.
- [UFont Template creation result](research/interaction-prompts-owner/font-template/README.md): one transient copy and distinct inspected native storage verified in-game; probe disabled, no font-data/UI writes.
- [Dynamic Aphes TextBlock result](research/interaction-prompts-owner/aphes-text/README.md): native Aphes OPEN→READ/manual cleanup passed with user visual confirmation; probe disabled. Final design remains open.

This module will have its own version and independently installable payload if implementation proves feasible.

## Independent repository

[Migration and exact source provenance](docs/MIGRATION.md) · [Shared Asterigos Research](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/RESEARCH_INDEX.md) · [Local external dependencies](docs/LOCAL_DEPENDENCIES.md). Original release URLs and frozen artifacts remain in AsterigosMods.
