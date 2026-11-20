# Immersive Interaction Prompts

A planned standalone interface mod for **Asterigos: Curse of the Stars**.

Contextual world-object prompts will gain a visually prominent upper line in fitting Aphes-world lettering, with a clearly readable localized interaction action below. An independently authored braided divider has been approved for the compact visual baseline. The actual action, native input icon and prompt visibility must stay correct.

Examples: pick up, open, read, descend; other context actions only when supported by the verified presentation path.

**Current research direction (2026-11-20): native World from one shared SCS template.** On installed `5fd1f2f`, the original `BaseGameEventObject_BP_C:ExtendedWidget_GEN_VARIABLE` template was set to World/NoCollision once, and the placed Open, Take and Check actors inherited it. All three presented their original TipHUD and World RenderTarget without Screen insertion. [Exact runtime evidence](research/interaction-prompts-owner/world-space/native-world-template/README.md#placed-world-inheritance-runtime-result-2026-11-20).

The next **source-only, uninstalled** successor applies the accepted Quintus appearance to original native World prompts: ×0.400 scale, +36 UE world-Z lift, RGB×0.35, native 1000×1000 resolution, original hold cadence correction, and a transient Aphes-font test line plus braided divider inside the original TipHUD. [Implementation and limits](research/interaction-prompts-owner/world-space/native-world-template/README.md#full-quintus-appearance-successor--source-only-2026-11-20). Interaction, switching and hiding are working assumptions for this visual iteration, not separate runtime PASS. The compact Screen S1 remains installed as its original separate candidate. **Production BLOCKED; no release.** The prior Screen-only direction and older World experiments below are historical evidence, not the current implementation plan. One World-space Open prompt with native Aphes header, ornament, localized action, current input hint and live editor completed its research stage on2026-11-04. The probe is disabled. [Result and recorded settings](research/interaction-prompts-owner/world-space/live-editor-style/README.md) preserve the exact source and remaining questions: better divider artwork, unexplained halo/faded appearance, wider action/lifecycle/compatibility support. Technical glyph strings are not verified Aphes translations.

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

The [compact-layout research successor](research/interaction-prompts-owner/world-space/compact-layout/README.md)
completed one user run with closer spacing, hide/resume and manual STOP confirmed
in the log. Latest tuning is recorded for the next candidate; production remains blocked.

The approved [authored divider and one color-metadata snapshot](research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md)
now have a separately installed research successor whose one metadata snapshot
and manual STOP passed. Closer vertical layout remains requested; final visual
acceptance, a color fix and a production release are not claimed.

## Independent repository

[Migration and exact source provenance](docs/MIGRATION.md) · [Shared Asterigos Research](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/RESEARCH_INDEX.md) · [Local external dependencies](docs/LOCAL_DEPENDENCIES.md). Original release URLs and frozen artifacts remain in AsterigosMods.
