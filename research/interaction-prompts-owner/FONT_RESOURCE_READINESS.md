# Aphes UMG font resource: tooling checkpoint — 2026-10-28

**PNG alternative:** [local PNG → Texture2D](png-header/README.md) is prepared,
not installed/run. It avoids a cooked UFont for this fixed glyph sample; the
native-font toolchain blocker below remains specific to that older route.

**Scope update:** Aphes tooling remains deferred. The independent
[stock-font child experiment](ui-child/README.md) created/rendered/manually
detached one label in-game without this dependency. This does not establish
Aphes rendering; the BLOCKED result below applies to the Aphes font resource.

**BLOCKED: no UE4.27 editor/cook toolchain located in the checked environment.**
No FontFace/composite UFont, cooked payload or executable UI prototype was created.
No installation, game execution, hot reload or internal-structure workaround.

This continues [VISUAL_READINESS.md](VISUAL_READINESS.md), source baseline
`e6592818452b007159be9d84a407e865483f5b11`. The project checkout was clean, on
`research/interaction-prompts-owner`, one worktree, identical live remote HEAD.
DevRules origin/main remains `c9a90c0`; applicable rules and current deltas were
consulted. Existing CanShow/layout/native-signature evidence was reused.

## Tools and precise missing dependency

The bounded read-only lookup checked PATH for UE4Editor/UE4Editor-Cmd,
UnrealEditor, UnrealPak and RunUAT; Epic engine registrations in HKCU and HKLM
(including x86), the launcher's installed-engine manifest, Program Files,
development/archive/download/tool directories and game libraries. File searches
targeted editor executables, RunUAT.bat, UnrealPak.exe, Build.version, uproject
and existing UAssetGUI/UAssetAPI/repak tools. Absolute paths/scope remain in
ignored local evidence.

| Found | What it proves | Missing capability |
| --- | --- | --- |
| Existing Aphes.ttf | TrueType sfnt header `00010000`, 14 tables, retained SHA256 below | Cooked UE4.27 FontFace/composite |
| repak_cli 0.2.3 | Existing executable; version/help succeed, commands info/list/hash-list/unpack/pack/get | Font import, asset creation, UE cook |
| Existing CUE4Parse reader/UHT dump | Prior offline inspection/reflection contracts | Font editor, cooker or real native implementation |
| Shipping-game Build.version in a library | Runtime engine metadata | Installed editor/cook toolchain |

No suitable editor/cooker or authoring uproject was located in those scopes.
This is not an exhaustive assertion about every disk location. The precise
missing dependency is **an available UE4.27 editor installation or verified
source build with font import/cook commandlets and Windows target support**.
A standalone packager/.NET runtime cannot substitute. No engine, SDK, tool or
plugin was downloaded/installed; no alternative manual asset reconstruction.

## Isolated resource contract — not yet an executed recipe

The standard [UE4.27 runtime composite font path](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-fonts-with-umg?application_version=4.27)
remains recommended. Once the missing toolchain is supplied:

1. Record its Build.version/build identity and executable hashes. Use a separate
   local content-only authoring project, without reconstructing TipHUD/Genesis
   native classes.
2. Import the retained TTF as a new FontFace at
   `/Game/Mods/ImmersiveInteractionPrompts/Fonts/Aphes_Probe_Face`; create runtime
   UFont `/Game/Mods/ImmersiveInteractionPrompts/Fonts/Aphes_Probe_Font`, with
   default typeface entry `Default` referencing only that face. Do not change
   `/Game/Fonts` or stock widget assets. Inspect the actual import result.
3. Cook for the applicable UE4.27 Windows target. Collect actual dependencies and
   any separate face payload; record loading policy. Copying an uncooked uasset
   is not a demonstrated cooked-resource workflow.
4. Inspect cooked version/package metadata, runtime cache mode, exact FontFace
   reference and internal object paths. Hash all produced files and preserve
   actual build/import/cook commands. Only then determine a compatible package/
   mount layout; repak availability proves neither mounting nor Lua asset loading.
5. Keep the TTF, derived assets/packages, authoring project and raw metadata
   local/ignored. A future original build recipe can be public without font
   payload. Cooked glyph data still contains derived game content; no permission
   to publish it is established here.

These unique paths avoid intentional stock replacement; actual isolated loading
and Asterigos compatibility remain **unverified**. Matching engine version is
a prerequisite, not runtime acceptance. No resource exists yet whose cooked
version, FontFace links or load paths could be validated. This contract is not
claimed as a successfully reproduced build recipe.

## Identity, artifacts and checks

- Original TTF SHA256 rechecked:
  `443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0`.
- Existing repak SHA256:
  `fcd538e5994b9bb833622d425ae346f4e0692f02d4b0025114a559f9b6286022`.
- Ignored lookup/TTF manifest:
  `.local/research/interaction-prompts/font-toolchain/inventory.json`, SHA256
  `2428558cfe09b865844f1d20223ae159f1f20abfec53c504c40999c0ca1735d6`.
  This is diagnostic evidence, not a generated font asset. Existing TTF stays local.
- Changed links, diff hygiene and preservation of observer/VERSION are checked.
  Existing CanShow tests are not rerun as new font evidence; there is no new
  executable runtime mechanism to test.

**Next visual experiment: BLOCKED.** Supply the path to an existing compatible
UE4.27 editor/cook installation, or separately authorize obtaining one. Then
build/validate the isolated font before preparing the bounded sibling-label/
divider prototype. OPEN remains technical glyph input, not an Aphes translation.
No reason to reopen UEPseudo/native arrays or repeat CanShow. Geometry/child
lifecycle remain later checks in VISUAL_READINESS. No game test requested now.

## Shared Research history reconciliation

`codex/ue4ss-metadata-api` started clean at `cf9ef9c`, origin/main at `766e79c`:
four branch-only commits, one main-only commit. A normal two-parent merge
preserved both histories, without reset/rebase/force-push or changing main.
The main-side short UHT declaration is retained alongside detailed R-010;
CanShow, slot tree, UMG font limits and TArray R-011 remain. The index's obsolete
static-only description is reconciled.

Merge `b64e08942666c295d67da0e9941e83d44db87be5` was pushed to the same Research
branch; both original heads are ancestors, no unmerged paths remain. No new
reusable engine capability was proved by a local missing-tool result, so it is
recorded here rather than generalized to Asterigos installations.
