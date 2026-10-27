# Immersive Interaction Prompts — project contract

Follow root [AGENTS.md](../AGENTS.md), [NikichMods/DevRules](https://github.com/NikichMods/DevRules), and root docs/WORKFLOW.md. Before implementation read this module's docs/REQUIREMENTS.md, STATUS.md, VERIFIED_RUNTIME.md and RESEARCH_PLAN.md. This module owns only **Immersive Interaction Prompts**; no changes to sibling mods without a separate gate.

Canonical per-game shared research: [NikichMods/Asterigos-Research/docs/RESEARCH_INDEX.md](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/RESEARCH_INDEX.md). Consult it before host research and promote accepted reusable game-level facts there automatically under DevRules. This module owns its behavior, evidence, tests and candidate identity.

Target baseline: Steam 1.09/build 12996889, UE4.27, Windows x64, UE4SS v3.0.1-1181-g83330635 + UEHelpers as accepted by root. The prompt owner, final writer, data path and fictional lettering are **not verified**. Production gate BLOCKED; research-only until ENGINEERING_RULES gate passes.

Preserve localized actions, native keyboard/gamepad hints, interaction mechanics, other UI and vanilla fallback. Do not claim arbitrary glyphs are canonical Aphes language. No host assets, fonts, extracted UI, dumps, proprietary tools, credentials or saves in public Git. Host-derived distribution requires separate provenance review.

Main is stable; new runtime behavior uses feature/* or research/* and needs explicit in-game acceptance before promotion. VERSION is the only semantic-version owner for this module; 0.1.0 is initial metadata, **no candidate/build/release yet**. Numbered artifacts immutable. No game launch/termination, loaded-file replacement or UI hot reload without explicit authorization and safe lifecycle. Use separate Git worktrees for concurrent writers. Original code will follow root MPL-2.0 scope.
