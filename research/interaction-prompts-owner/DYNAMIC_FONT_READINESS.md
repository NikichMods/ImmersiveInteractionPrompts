# Aphes as a dynamic UMG font without an editor — 2026-10-28

## Decision

**No dynamic-font write/render payload exists.** A read-only
[Template-copy creation/storage probe](font-template/README.md) is prepared,
installed after explicit permission, host closed and user run pending. Replacing an existing
shared font is **BLOCKED** by real consumers or unknown blast radius. The UE4.27
C++ path-to-TTF constructor exists, but a directly injectable native bridge is
**BLOCKED** by missing verified engine linkage/ABI and pinned build dependencies.

A narrower **source-supported candidate** emerged: construct a private transient
UFont using a small existing runtime UFont as Template, then change only the
copy's existing FFontData entry to a local TTF filename. This is not replacement
of the donor package or stock object. **The first creation/storage probe is READY;
FFontData mutation and rendering remain unprepared/unverified.** Evaluate this
candidate before paying for a native bridge. The initial assessment at 872929c
was doc-only; the linked follow-up now contains the bounded read-only probe.

The [PNG experiment](png-header/README.md) remains independently READY for its
previously specified, separately authorized runtime test. It supplies a fixed
raster label, not arbitrary dynamic TextBlock text. OPEN has no established Aphes
translation. Coherent remains a separate overlay route with prior font evidence.

## Recovery and scope

Clean single worktree, branch `research/interaction-prompts-owner`, HEAD and live
remote `135d0ed33c2b697051b63e079a6190da862e8862`; shared Research main
`d9bc8565eb9e32ae2c3c0de962dd5c7e8929c234`. No unpublished edits were overwritten.
Current DevRules origin/main `0f4888b` (including updated Engineering), Git/Codex,
runtime/licensing guidance and local project contract were read. Prior label and
divider success is reused, not repeated. Steam1.09/build12996889, UE4.27,
UE4SS v3.0.1-1181-g83330635 remains the evidence envelope.

Existing CUE4Parse1.2.2 reader was run read-only against only the known game Fonts
and EngineFonts package paths. Raw JSON, source snapshots and audit hashes stay
ignored under `.local/research/interaction-prompts/dynamic-font/`. No engine,
software, DLL, package or font was built/installed. Game files/settings/mods were
not written; the game was not launched or terminated. VERSION and all executable
project sources, including the accepted ui-child and prepared PNG probe, unchanged.

## A — bounded inventory and replacement

Scope: retained container index plus **17 known font packages** under the two
directories: **5 UFont, 12 FontFace**. This is not an all-game referencer graph or
a claim that fonts cannot exist outside these paths. The root DroidSansMono Font
and Faces/DroidSansMono FontFace were inspected separately to avoid basename
collision in the reader's output. Existing static widget JSON was searched for
known object references; no new all-widget/world scan.

| Resource | Confirmed contents / known consumers | Consequence |
| --- | --- | --- |
| `/Game/Fonts/Umg_Font` | Runtime UFont: Default→EBGaramond-SemiBold, Desc→FiraSans-Regular; fallback→_ZH-HANT_NotoSansCJKtc-Medium; subfonts→NotoSansJP-Medium and NotoSansSC-Medium. Existing IndicateTipItemWidget_BP exports Desc_Text, Desc_Text_Steam, Zone_Text reference it | Shared UI family; no replacement |
| `/Game/Fonts/EBGaramond-SemiBold_Font` | Runtime UFont, one Default face→EBGaramond-SemiBold. HudUmg DamageDigits0…19 reference it | Not unused; best small Template candidate for a separate copy, not in-place edits |
| Five `/Game/Fonts/` FontFaces | EBGaramond-SemiBold, FiraSans-Regular, _ZH-HANT_NotoSansCJKtc-Medium, NotoSansJP-Medium, NotoSansSC-Medium; all referenced by Umg_Font, Garamond also by its separate Font | Replacing any sidecar affects known shared consumers, potentially more |
| `/Engine/EngineFonts/Roboto` | Runtime UFont; Regular/Bold/Italic/BoldItalic/Light faces and DroidSansFallback | Engine family, independence not established |
| `/Engine/EngineFonts/DroidSansMono` | Runtime UFont; Faces/DroidSansMono plus DroidSansFallback | No direct widget consumer found in the limited saved corpus; that is not absence of consumers |
| `/Engine/EngineFonts/RobotoDistanceField` | Characters and a texture export; FontCacheType omitted, Offline default in enum | Atlas font; replacing a TTF is not rebuilding the atlas |
| Seven `/Engine/EngineFonts/Faces/` FontFaces | DroidSansMono, DroidSansFallback, RobotoRegular, RobotoBold, RobotoItalic, RobotoBoldItalic, RobotoLight | Referenced by the above runtime Fonts; no free sidecar |
| `Genesis/Content/Fonts/Aphes.ttf` | Original loose-in-container TTF; no matching Aphes Font/FontFace in these package paths | Not an assignable UFont by itself |

Other retained loose source files include HanaMinA.ttf, NotoSansKR-Medium.otf,
NotoSansTC-Medium.otf and the source OTF for traditional Chinese; they are not
independent UFont assets. FontObject in SetFont expects a font provider object,
not an arbitrary file path. Assigning a known UFont to our new label is separate
from replacing its shared data. No stock TipHUD FontObject identity is inferred
solely from another widget's JSON.

**A result:** no safe in-place donor found. Known consumers reject the game Fonts;
unknown native, style, localization and soft-reference consumers reject treating
the remaining engine resources as unused. A full absence proof would cost more
than creating an isolated resource and is not warranted for this goal.

### Font replacement tools

The author of [UNREAL ENGINE Font Tool](https://www.nexusmods.com/blackmythwukong/mods/1529)
advertises standalone .ufont/.ttf/.otf replacement in PAKs without an editor,
with an in-game result specifically for Black Myth: Wukong. Its stated limits
include IoStore-embedded fonts and baked atlases. These claims fit a replacement
workflow, not proof of creating an independent Asterigos Font provider. Asterigos
has .ufont entries, so file replacement is a plausible tooling family; loading
policy, package/sidecar mapping, container priority and actual compatibility are
not established. No tool was downloaded or executed. Upload/modify permissions
must not be inferred from availability on Nexus.

The separately authored [h5d7r tool](https://github.com/h5d7r/Unreal-Engine-4-5-Font-Tool)
describes recursively substituting .ufont contents while retaining filenames.
It is not an identified mirror of that Nexus download. Such substitution cannot
isolate other users of the same resource. Same-name payload replacement does not
by itself verify cooked package metadata or create a new UFont object/path.
Cloning/renaming a cooked package is another serialization task, not an accepted
recipe here. No asset override was prepared.

## B — native TTF constructor and the actual integration boundary

The [4.27 API page](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/SlateCore/Fonts/FSlateFontInfo?application_version=4.27)
is not sufficient for layout: its current rendering includes TObjectPtr/float
information inconsistent with the installed dump. The official
[Python4.27 reflection listing](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SlateFontInfo?application_version=4.27)
and actual UHT agree on int32 Size and the six reflected fields.

Specific implementation evidence is an upstream engine-source mirror, **not
Asterigos's private engine fork**: AlexMercer-MA/UnrealEngine-4.27 commit
`306a7e9f7fb53f14c2cb3bfd3854ad906710a17e`, Build.version4.27.2 / branch
++UE4+Release-4.27 / CompatibleChangelist17155196. Only relevant text was retrieved.

- [SlateFontInfo.h/.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/SlateCore/Private/Fonts/SlateFontInfo.cpp)
  has the deprecated but runtime-compiled FString filename constructor (uint16
  size, hinting, outline). Lines95–111 call UpgradeLegacyFontInfo, 213–220 select
  the legacy font cache. This is not an editor-only import or a UE5 inference.
- [LegacySlateFontInfoCache.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/SlateCore/Private/Fonts/LegacySlateFontInfoCache.cpp)
  54–90 resolves a filename and builds/caches FStandaloneCompositeFont with
  LazyLoad. An absolute local TTF path avoids relative project/engine ambiguity.
  The file must remain available while its glyph data may be loaded; caching is
  not a promise that deleting/replacing it is safe.
- FSlateFontInfo's runtime CompositeFont is a non-UPROPERTY shared pointer.
  GetCompositeFont first checks the FontObject provider, then that shared pointer,
  then fallback. Lua cannot call a C++ constructor simply by filling a table.
- Installed UHT: `UTextBlock::SetFont(FSlateFontInfo InFontInfo)`. Mirror
  TextBlock.cpp94–100 copies it into Font and passes it to STextBlock. UE4SS
  LuaUObject.cpp748–826 accepts a matching typed struct (CopyCompleteValue) or
  writes reflected table fields. It has no constructor/field for that native
  shared pointer. A FontFilename key in SlateFontInfo is not a valid Lua API.

**B result:** UE4.27 supports the mechanism inside properly linked native code;
neither safe injection nor Asterigos rendering follows from the constructor's
existence. A read-only dumpbin export check on the installed Shipping executable
found no named FSlateFontInfo/UTextBlock/SlateFont constructor exports. This is
not proof that the internal functions do not exist; it means no ordinary named
linkage seam was established. UE4SS reflection does not turn non-UFUNCTION
constructors into callable functions. UHT stubs cannot supply their real bodies.

### What a native bridge would actually need

Pinned [UE4SS CMake](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/CMakeLists.txt)
requires CMake≥3.22, C++23 and ASM_MASM; its VersionChecks.cmake sets MSVC≥19.43
(toolset14.43) and Rust≥1.73 for the full dependency build. Local VS2022 has
MSVC14.34 and Windows SDK10.0.22000; cl/cmake are absent from PATH, and no adequate
pinned build environment is verified. The old compiler does not meet that build's
declared minimum. No software/toolchain update was performed.

The pinned cpp-mod guide requires source/submodules; .gitmodules names UEPseudo,
whose exact gitlink was previously recorded as
`fbb4fdd3fffc59d5b5268b23a643f500f702115e`. Its usable source/import-library build
remains unavailable in the retained environment. A matching UE4SS.lib/headers,
CRT/configuration and Lua registration seam are required, not a loader upgrade.

More importantly, compiling a UE4SS mod does not supply SlateCore/UMG engine
constructor linkage. One needs a verified supported engine integration seam and
native type/copy/allocator compatibility for this Shipping build. An Unreal project
plugin normally obtains these via engine modules (Core/CoreUObject/Engine/SlateCore/
UMG and UBT); that is not automatically loadable as a dlls/main.dll UE4SS mod.
No raw-address/offset workaround, replacement Slate runtime or guessed struct
layout is proposed. A bridge should set only the owned TextBlock on the game
thread and retain/release native font data correctly. Version-pinned deployment,
rollback, compatibility and maintenance then become additional responsibilities.
Editor/cook can be avoided in principle; those native integration costs remain.
Do not call this route a ready small DLL merely because its hypothetical API is
small. No DLL/source bridge was created.

## A narrower Lua candidate: template copy, not shared replacement

Relevant source facts change the next choice:

1. LuaMod.cpp1916–2023 in **83330635** explicitly parses Template as argument8
   (after class, outer, name, flags, internal flags, two booleans) and assigns it
   to FStaticConstructObjectParameters.Template. Existing primitive creation proves
   the basic construction route, not this optional Template branch.
2. UE4.27 UObjectGlobals.cpp2999–3099 copies reflected properties from a non-CDO
   template; PropertyStruct.cpp309–311 invokes CopyScriptStruct, and
   PropertyArray.cpp616–647 allocates destination storage and copies elements.
   Font-face object references remain shared until replaced; array/struct value
   storage is copied. This supports isolation, but is not an Asterigos runtime test.
3. Installed UHT exposes UFont.CompositeFont.DefaultTypeface.Fonts and
   FFontData.FontFilename/Hinting/LoadingPolicy/SubFaceIndex/FontFaceAsset.
   CompositeFont.cpp73–80 returns the filename directly when FontFaceAsset is null;
   with an asset still set the filename field is ignored. UFont::GetCompositeFont
   returns its own composite only in Runtime cache mode.
4. Therefore a one-entry runtime UFont copy could retain native initialization,
   edit only its existing in-range FFontData: clear its face reference, set the
   exact local filename, keep SubFaceIndex0, explicitly use LazyLoad/default hinting.
   A FontInfo belonging to the new label would reference that private FontObject
   and its Default typeface. No shared-pointer constructor is needed by this form.

Do not instead assemble a brand-new typeface array blindly: pinned LuaUObject
array conversion uses lua_rawlen at stack slot1 and AddZeroed; TArray Get can
grow an empty/out-of-range array. Native initialization and correct Lua stack
behavior are separate questions. The Template candidate avoids that allocation
route, using a confirmed existing one-entry array with a count guard first.

**Remaining gates:** exact optional-Template behavior through installed UE4SS/
UEPseudo, independent storage/readback in the game, reflected string/nil mutation
on the copy, no donor changes, filename decoding, glyph rasterization and font-cache
lifetime. Absence of an exposed constructor is not proof that every Lua font
provider route is impossible. This candidate is source-supported, not a validated
recipe. No stock Font/FontFace, native-owned array or installed file was modified.

## Comparison and minimal next step

| Route | True dynamic text? | State / main cost | Fits native TipHUD? |
| --- | --- | --- | --- |
| Shared donor + file/data replacement | Yes, potentially | BLOCKED: affects known/unknown other consumers; tool compatibility unproved | Potentially, but violates isolation |
| Private transient Template UFont copy + local TTF | Yes, if filename path renders | First creation/storage probe prepared; Template/copy runtime and write/render/cache gates open | Future assignment would use the existing owned TextBlock mechanism |
| Direct FString→FSlateFontInfo in C++ | Yes in UE4.27 | Engine feature confirmed; bridge BLOCKED by native linkage, dependencies and compatible build | Possible in principle, not demonstrated as injectable |
| PNG→Texture2D | No; prepared fixed glyph image | Source READY, actual import/alpha/unbind untested; requires local raster generation | Own UImage + accepted divider |
| Coherent @font-face | Yes in prior Coherent context | Existing Aphes evidence; prompt mapping, placement and lifecycle would be a separate integration | Overlay, not a native TipHUD TextBlock |

For the present **dynamic UMG text** goal, first use the prepared private-copy
creation/storage probe before C++ or shared replacement. It checks one copy's
type/cache/typeface count and addresses, then donor values; no entry is written.
It uses exact naturally loaded EBGaramond-SemiBold_Font or records NOT_LOADED,
without force load or scans. That read-only slice is now installed and awaits
one user-operated run; later font-data writes still require separate review/permission.

Only after this result and a further setter/ownership review may a later prototype
change the copy's entry, bind it to the established own TextBlock and test dynamic
strings/sizes. Keep the local TTF available until exit, no forced GC or live file
replacement. Neither full deep-copy independence nor Aphes rendering follows from
distinct addresses on the inspected path. Those later writes are not in this probe.

If the goal is only the first visual Aphes label, the existing PNG test is the
cheapest prepared option and does not answer the dynamic-font question. No product
choice to replace native UMG with Coherent or to settle for raster text is made here.

Key local source SHA256 identities (full file list in ignored audit.json):

| Mirror file | SHA256 |
| --- | --- |
| SlateFontInfo.cpp | `ec58a079f09132996e7b278a77c67b3016281d3d0fa2b738b0c6c71621fa5bbc` |
| CompositeFont.cpp | `1d4194a0c3d3b07d65a77de98d33c8b21372b4b6fbf25945b51ab0d70f184a7d` |
| UObjectGlobals.cpp | `4827289439e340a253b9d8447d970a4a9bc3c66badb5b5f1e29dc4a621ccba47` |

Checks: source identities and UHT declarations, 17-package class/reference summary,
changed-document links and diff hygiene, executable/VERSION preservation. Existing
mock UI tests are not rerun as purported proof of a new font mechanism. Source/raw
data hashes are retained in ignored audit.json; no runtime acceptance is claimed.
