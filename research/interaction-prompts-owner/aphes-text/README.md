# Private UFont Aphes TextBlock — setter review and visual probe

**READY for one separately authorized visual experiment; not installed/run.**
Production BLOCKED. OPEN/READ are technical glyph strings, not verified Aphes
translations. No PNG, cooked font, editor, C++ bridge or shared font replacement.
The completed [Template storage result](../font-template/README.md) is reused.

Source [Scripts/main.lua](Scripts/main.lua), SHA256
`9042d9daebe65681c80e445a963e15ec6bd0b4c1a68d9825cb1b62284b8a6306`.
Only its example config is tracked; the real IIPAphesConfig.lua and TTF stay
ignored/local. Initial clean worktree/remote: `4f660f41fd6564cfa0197b15e069ea23440a1089`,
branch research/interaction-prompts-owner; Research main
`edd836170285e9bd2f7ad430f49c292dc20341e0`. DevRules origin/main0f4888b and the
project contract/evidence were consulted. No unpublished work was overwritten.

## 1. Setter and ownership gate

**Confirmed by source and bounded static inspection, not a write test in-game.**
Target: Steam1.09/build12996889, UE4.27, UE4SS83330635, installed DLL SHA256
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`.

| Write / lifetime question | Evidence and consequence |
| --- | --- |
| Nested field destination | LuaUScriptStruct.cpp167–218 derives params.data from start_of_struct and the reflected property's offset; NewIndex dispatches Operation::Set. Ordinary Get wraps native storage. No raw memory API or handwritten offset is used by the probe |
| FontFaceAsset=nil | LuaUObject.cpp445–480 object-property Set stores nullptr into that particular pointer slot. It does not mutate/destroy the referenced FontFace or its font data |
| FontFilename from Lua string | LuaUObject.cpp1758–1790 constructs a temporary Unreal::FString from the Lua string, then invokes copy assignment on the destination field. The FString-userdata SetCharArray branch is intentionally not used |
| FString buffer ownership | Exact installed DLL exported FString copy constructor and assignment were statically inspected with the existing dumpbin, plus their bounded resize/copy callees and wchar constructor. They construct/resize destination storage and copy character bytes; this is not borrowing the temporary input buffer. No code/address was invoked/injected, no installed file was changed |
| Native Template's existing FString | Upstream UE4.27.2 Class.cpp3029ff CopyScriptStruct uses native copy or property-wise copies for non-POD state. UnrealString.h defaulted FString copy owns its Data TArray; Array.h copy/CopyToEmpty resizes and constructs destination elements. Nontrivial font data is not safely replaced by a Lua zero-filled table. Existing readback equality alone was not used to infer this ownership |
| Hinting/LoadingPolicy/SubFaceIndex | LuaUObject.cpp1542–1635 enum Set writes through reflected underlying width; LuaUObject.hpp975ff integer Set writes the int32 field. Installed enums are Default0, LazyLoad0; subface0. Values are explicit and bounded, not arbitrary enum integers |
| Assigning to UMG | Installed SetFont(FSlateFontInfo) and mirror TextBlock.cpp94–100 copy FontInfo then update STextBlock. Matching typed struct userdata uses CopyCompleteValue. Only the new label's native-initialized FontInfo is edited; original FontInfo is read/copied synchronously |
| Retention and release | FontInfo.FontObject is UPROPERTY and FSlateFontInfo.AddReferencedObjects includes it. The attached owned label provides the engine reference to its own Font. Outer and Lua wrappers are not claimed as GC roots. Cleanup detaches the label then uses native SetFont with a typed read of original FontInfo, replacing the owned reference and Slate state together |

Primary source links: [pinned LuaUObject](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp),
[pinned struct dispatch](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUScriptStruct.cpp),
[UE4.27.2 FString](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Core/Public/Containers/UnrealString.h),
[native struct copy](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/UObject/Class.cpp),
[TextBlock setter](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/TextBlock.cpp).
Engine source is the previously identified upstream4.27.2 mirror, not the game's
private fork. The installed UHT, actual DLL and accepted storage/UMG results bind
this review to the tested environment. Bounded disassembly/export text and hashes
remain ignored under `.local/research/interaction-prompts/aphes-text/`; addresses
from static analysis are not payload call targets or a public ABI.

This evidence is sufficient to prepare the limited writer, not production safety
or runtime acceptance. No further UEPseudo source/toolchain installation was needed;
its missing source was not filled with a guessed FString implementation.

## 2. What is prepared

The accepted ui-child source is preserved. This separate implementation reuses its
exact CanShow Blueprint post-only hook, one natural «Открыть», original tree/slot/
identity/visibility/font-size guards, X38 placement, 140×28 label and resource-free
140×2 divider. No original text, font, slot, input/icon/hold/lock or native-owned
array is written. These established mechanisms are not a new research question.

- Ctrl+Alt+F6 first arms one 30-second attempt; missing config/API or key collision
  disables startup. Only when the guarded prompt is reached is the local TTF read.
- Unique own TextBlock starts collapsed. A typed SetFont copies original settings;
  distinct original/own FontInfo storage is checked before editing the latter.
- Exact naturally loaded Garamond Font is the Template; no donor fallback/load or
  all-object scan. One RF_Transient UFont uses the donor's resident package as
  Outer, reusing the completed native construction contract. Only the label's
  FontObject property retains it for display. Class/identity/outer and shape/count
  are checked. The existing storage
  comparisons are cheap allocation-specific guards before writes, not a repeat
  of the completed standalone storage experiment. No indexed read before Num1.
- Only that copy's existing FFontData is configured: face nil, absolute filename,
  LazyLoad0, Default hinting0, SubFaceIndex0. Its metadata readback/storage is checked;
  selected donor state is compared even after a caught partial failure. The donor
  and original face receive no assignments. No typeface array is rebuilt.
- The new label's FontObject points to the private Font, typeface Default; native
  SetFont applies its typed FontInfo. Configuration precedes its first consumer,
  so no live shared font-cache mutation/invalidation is attempted. UFont's normal
  BeginDestroy flushes its composite/object font cache when eventually collected.
- OPEN is shown only after label and divider setup succeeds. Second chord resolves
  the same owned label/font afresh and SetText changes OPEN→READ. No delayed text
  reader or borrowed struct/frame persists; only primitive identities are stored.
- Third chord, target-state change, failure or timeout cleans up both own elements.
  Detachment is independent for each child. The detached label's native SetFont
  restores its own FontInfo from an original typed read, then verifies the stock
  reference. This does not set anything on the original widget/font. Release is
  not done by clearing FontObject before a possibly failing native call.
- If release fails, the private font remains held by the own label's property and
  cleanup reports failure/retains primitive identity for explicit retry. If the
  original FontInfo source is gone, it fails rather than constructing an unproved
  replacement struct. No manual destruction, AddToRoot/RemoveFromRoot or forced GC.

All FontData/FontInfo wrappers are callback-local. Mutation and readback happen on
the game thread before rendering; reentrancy guard prevents nested allocation.
No hide/show/world-travel/GC lifecycle acceptance is claimed. Native decoder/fallback
behavior cannot be proved by FONT_CONFIGURED or FONT_BOUND log messages.

## Local input and offline checks

Existing original Aphes.ttf: 13920 bytes, sfnt00010000, SHA256
`443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0`.
Future authorized installation must verify that exact identity. Runtime preflight
only checks readable size/header and closes the file on error; it is not a hash
or a FreeType decoder test. IIPAphesConfig.lua supplies an absolute ASCII Windows
filename (≤1024 characters). No TTF is copied/extracted/installed by preparation.
It must remain available through normal game exit because loading is lazy; do
not replace/delete it live. [Example config](Scripts/IIPAphesConfig.example.lua)
contains no real machine path. This stage does not implement a Nexus installer.

`python tests/test_aphes_text.py`: **10 new groups pass**, using existing Lua5.4
test dependencies. Tests cover OPEN→READ on one element, font reference/release,
missing config/file/donor, storage/count/type/constructor guards, each setter's
partial failure, wrong readback, bind failure, donor post-check fault injection,
state/timeout cleanup and release-failure/retry without another font creation.
The engine is mocked: native allocator behavior, real font load, glyphs, GC and
Slate rendering are not test results. Old visual/storage tests were not repeated.

Source/doc links, diff hygiene, actual source/TTF/DLL hashes, prior probe hashes,
VERSION and installed mod/settings preservation are checked separately. No game,
software installer, new DLL, hot reload, production release or installed revision
was created by this stage. Original source/example/tests are public; font, config,
raw engine/tool text and evidence manifests remain local/ignored.

## One next sufficient experiment

After separate installation permission and closed-host rollback/hash preparation:
one natural Open prompt; first Ctrl+Alt+F6 shows Aphes-shaped OPEN plus the established
divider, second changes the same element to READ, third removes both. Complete
within30 seconds; original localized action/icon should remain throughout. Record
the two visual states and inspect FONT_CONFIGURED/FONT_BOUND/DONOR_UNCHANGED,
TEXT_CHANGED and FONT_RELEASED/CLEANED after normal exit. A Latin fallback or
missing glyphs is not success even with correct property readback. Missing donor
or decode failure is recorded honestly; no forced load/alternative mechanism.

This would prove the new write/render/dynamic-change seam in one bounded run.
Production and wider lifecycle remain BLOCKED until their own real acceptance.
