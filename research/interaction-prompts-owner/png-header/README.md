# Local Aphes PNG → transient Texture2D → TipHUD experiment

**READY for one separately authorized narrow runtime test.** Source preparation
and offline rasterization only; not installed/run. No import, texture display,
alpha or texture-unbinding result is yet claimed in Asterigos. Production BLOCKED.
OPEN is technical glyph input, not a translation into the Aphes language.

## Recovered state and reused evidence

Started clean at `8db6e87472257744e83edb29800515ab0870060e`, single worktree,
`research/interaction-prompts-owner`, same live remote. Current DevRules remote
`c9a90c0`, project contract, applicable rules/deltas, status/runtime, licensing and
[completed divider](../DIVIDER_READINESS.md) were consulted. The native child/
slot/cleanup and resource-free divider are accepted narrow baselines, not new
questions to repeat. Their exact source remains unchanged. Installed old probe
stays disabled; its bytes and nine other mod files/settings were rechecked.

## Exact installed-build API and binding

The retained UHT output from UE4.27 / UE4SS `83330635` declares:

```cpp
static UTexture2D* ImportFileAsTexture2D(UObject* WorldContextObject, const FString& Filename);
void SetBrushFromTexture(UTexture2D* Texture, bool bMatchSize);
void SetBrushResourceObject(UObject* ResourceObject);
int32 Blueprint_GetSizeX() const;
int32 Blueprint_GetSizeY() const;
```

Owners: `/Script/Engine.KismetRenderingLibrary`, `/Script/UMG.Image`,
`/Script/Engine.Texture2D`. The first function is in the runtime Engine module,
not an editor asset-import/cook API. Official 4.27 contracts describe
[disk-file import into Texture2D](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Kismet/UKismetRenderingLibrary/ImportFileAsTexture2D?application_version=4.27)
and [SetBrushFromTexture](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/UMG/Components/UImage/SetBrushFromTexture?application_version=4.27):
false bMatchSize uses the image region rather than resizing it to texture pixels.
Generated `.cpp` bodies return stubs (including NULL); they are not engine
implementation or evidence that real import always returns null/succeeds.

Pinned [LuaMod.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp)
1245–1275 routes StaticFindObject through auto_construct_object.
[LuaUObject.cpp](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/LuaType/LuaUObject.cpp)
373–386 makes an unbound UFunction wrapper with null base. Its __call routes
through call_ufunction_from_lua (LuaUFunction.cpp): 93–145 consumes the explicit
calling UObject; 210–280 marshals Parm values then ProcessEvent; 342–361 returns
the result via GetNonTrivialLocal. Thus the chosen call is:

```lua
local fn = StaticFindObject("/Script/Engine.KismetRenderingLibrary:ImportFileAsTexture2D")
local cdo = StaticFindObject("/Script/Engine.Default__KismetRenderingLibrary")
local texture = fn(cdo, current_tip_hud, absolute_png_filename)
```

The CDO is the calling context, TipHUD the WorldContextObject; they are not
interchangeable. Exact paths/classes/function identities are checked. Missing
CDO/function/image methods stop without force-loading or an alternate target.
No native hook/frame/array reader is used. Do not call fn with only the two game
parameters: an unbound wrapper needs its explicit calling object first.

LuaUObject.cpp 1758–1790 supports Lua string → FString. 445–467 handles UObject
values/nil; its return handler constructs an object wrapper from the returned
pointer, not a borrowed pointer into the temporary parameter frame. UObject.hpp
679–701 provides HasAnyFlags; the prototype requires RF_Transient and actual
Texture2D class/size. Source hashes for these snapshots already live in the
earlier API reports; local PNG api-audit.json records the checked headers/hashes.

## One locally generated PNG

[render_open.py](render_open.py) is original source, requiring existing Pillow /
FreeType only. It checks the exact retained font SHA256 before rendering; no
system font fallback, extraction, network or installation. Repeatable command:

```text
python render_open.py --font <local-original-Aphes.ttf> --out <ignored-local-folder>/OPEN.png
```

Output overwrite is refused. Pillow 12.3.0 / FreeType 2.14.3 were available locally;
no FontTools/UE editor/tool installation was needed. One PNG was created and
reloaded/validated; alpha was visually inspected in memory without another asset.

| Property | Actual result |
| --- | --- |
| Original TTF SHA256 | `443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0` |
| PNG | 560×112, non-interlaced 8-bit RGBA, 6917 bytes |
| Sampling | 4× the fixed 140×28 widget region; same 5:1 aspect ratio |
| Glyph input | OPEN, Pillow BASIC layout, font size107; ink bounds `(17,8,321,103)` |
| Alpha/RGB | alpha min0/max255 with antialias levels; white RGB also at alpha0 to avoid black interpolation fringe |
| PNG SHA256 | `6c6fdd18a18d5215fe840e4a35ee86e87673086a10d46385927e335f45b20ad9` |

PNG, font, manifest and local IIPPNGConfig.lua remain ignored under
`.local/research/interaction-prompts/png-header/`. They are not distributed.
The image was checked as glyph shapes/transparent coverage, not a language word
or a verified engine render. Raster text is not an editable UMG font resource.

## Experiment and lifetime

[Scripts/main.lua](Scripts/main.lua), SHA256
`e1ce1f3e6cdb866e7ef39fa34fea31ac4c3f6c28b50886ebcd9fd3b0abb6a1a3`.
Separate research implementation reuses the tested child/divider policy. Chord
Ctrl+Alt+F8, one natural «Открыть», measured slot/identity/font-size guards, one
attempt and 30-second stop. Original TextBlock_89/slot/font, native arrays,
input/hold/lock and ancestor state are not assigned.

- A local `IIPPNGConfig.lua` supplies an absolute disk filename. The unique own
  module is found through the Scripts search path added in LuaMod.cpp 1082–1110.
  An example only is tracked; the actual private config is not. Missing config
  stops before key registration. No game file/config is changed by preparation.
- Before import, a bounded read validates PNG signature/IHDR/dimensions/RGBA,
  ≤1MiB and local path shape. File closes even on failure. Native decoding still
  validates real contents; preflight is not a decoder/security guarantee. Future
  installation must independently check the recorded PNG hash.
- An owned transient UImage replaces only the experimental upper TextBlock.
  Import is attempted at most once per session, entirely synchronously on the
  game thread, with IMPORT_BEGIN/TEXTURE_BOUND markers. Null/wrong-type/size/
  non-transient result fails closed; no stock-font fallback or retries.
- Explicit white brush tint and image opacity avoid theme-dependent foreground
  tint. SetBrushFromTexture(texture,false) binds the returned Texture2D; readback
  requires Brush.ResourceObject identity equality and Image draw mode. Reflected
  Image.Brush → FSlateBrush.ResourceObject is the engine reference chain retaining
  it while attached. Lua wrappers/CDO/Outer are not claimed to be GC roots.
- Header slot remains140×28; same resource-free divider remains140×2. No extra
  original-UI writes. Both stay collapsed until setup succeeds. Failure restores
  the original prompt by independently removing only the experiment's children.
- Cleanup detaches each child and checks GetParent. For the header, only after
  detachment it clears its own resource with SetBrushResourceObject(nil), verifies
  the reference is absent and logs TEXTURE_UNBOUND. The pointer/nil pusher is
  source-confirmed; this new native bind/unbind path still needs runtime evidence.
  Failure is reported and retains only failed identity metadata for explicit
  cleanup retry, never another load. No forced GC/Destroy/texture-package save.
  Releasing this reference is not proof of immediate GPU/UObject deallocation.

Offline: **30 tests pass** (7 CanShow, 15 existing ui-child, 8 PNG policy groups).
New tests cover explicit CDO/world/filename argument order, one import, texture
reference/unbind, missing config/file/CDO/function/image methods, malformed size,
null/wrong size/non-transient import, bind/clear failures, retry and timeout.
They mock the engine: no claim of real file decoder, alpha, GPU upload, GC or
static call execution. Original installed scripts/settings and VERSION unchanged.

## Nexus applicability — assessment, not an installer

A source-only release could generate images locally from each user's game data:
choose installed game → read only the known stock font entry → validate identity
→ run the rasterizer → keep PNG in a local mod cache and write local path config.
Publish original scripts/tools/recipe, not TTF, PNG, cooked fonts, glyph outlines
or game-derived packages. No need for UE editor/cooker in that proposed route.

The TTF is packaged at `Genesis/Content/Fonts/Aphes.ttf`; no loose file was found
at that installed path. Simply telling users to copy a loose Fonts file is not
a complete setup. Existing local CUE4Parse 1.2.2 successfully supplied the font
in prior research; cached NuGet metadata declares Apache-2.0. This does not clear
every dependency or game-data redistribution right. A future targeted extractor
must resolve supported container versions, locally required keys/codecs and all
dependency notices/redistribution terms. No private key or proprietary codec is
published/assumed distributable here. An explicit local-font-file input remains
a fallback setup option, not a finished one-click Nexus workflow.

An original small preparer could eventually bundle approved rendering/parser
dependencies so users need not install Python; it is not implemented now. Font
extraction automation, packaging/usability, game-version checks and distribution
review remain **BLOCKED for a standalone release**, alongside unresolved Aphes
word semantics and production lifecycle. Local generation avoids shipping the
derived payload; it is not a legal clearance claim. Existing LICENSING.md limits
remain in force; no new contact/permission workflow is imposed.

## Next sufficient runtime question

After separate exact-source/config/PNG installation permission and closed-host
rollback preparation, one Open prompt / Ctrl+Alt+F8: does native import produce
the original Aphes glyphs with transparent background, legible sizing and the
existing divider/original action/icon? Second chord should detach both and
produce TEXTURE_UNBOUND plus CLEANED. Observe no opaque rectangle; inspect actual
IMPORT/size/bind/unbind failures before expanding scope. Do not repeat the old
label/divider experiment or add a font cooker/native observer. No installation,
game execution, full installer or production release occurred in this stage.
