# SetupTipMessage2 — built-in UHT declaration, 2026-10-28

**Follow-up:** [observer marshalling review](OBSERVER_READINESS.md) found an
unverified native frame/lifetime boundary and stopped before creating/registering
the observer. The declaration below remains established; “sufficient to proceed
to preparation” did not mean the callback memory contract was already verified.

**Result: exact reflected declaration obtained from the installed UE4SS UHT
generator. The missing-declaration blocker is closed; production remains BLOCKED.**
This is a generated declaration of a loaded native class, not original game
source, a full numeric reflection dump, proof of callback marshalling or a final
UI-writer observation. No observer/C++ mod was created or installed.

## Method, provenance and actual run

Continued the clean independent checkout at
`46d220083263dd12017f071b4af9b48d9d710bf1`, existing
`research/interaction-prompts-owner`, equal to fresh origin; no local-only commits
or staged/unstaged/untracked work. Ignored evidence preserved. Current DevRules
origin/main `c9a90c0` and project/shared evidence were consulted. No history rewrite,
main/production/VERSION changes or alternate generators.

The bounded lookup of retained research/tool inputs and installed generator
locations found no existing ExtendedUserWidget declaration or UHT/CXX SDK.
`UHTHeaderDump` did not exist at the verified working directory. Thus there was no
previous dump to delete or back up. Before execution, the prior log/config and
hash manifests for installed mod files, loader files and save/config files were
preserved in ignored storage.

Source reviewed at installed revision `83330635`:

- [Dumpers button](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/GUI/Dumpers.cpp#L720)
  calls `UE4SSProgram::generate_uht_compatible_headers()`.
- [UHT entry](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/UE4SSProgram.cpp#L2324)
  passes working-directory/UHTHeaderDump to UEHeaderGenerator and calls
  dump_native_packages. [That implementation](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/SDKGenerator/UEHeaderGenerator.cpp#L3825)
  removes an existing output tree, enumerates loaded native types and generates
  files. This broad **built-in** generation was explicitly authorized for this
  stage; it was excluded by the earlier narrower Lua-capture task.
- The distinct CXX path (UE4SSProgram.cpp 2341+) can LoadAllAssets and calls
  FreeAllForcefullyLoadedAssets. Neither CXX/GenerateSDK nor that path was used.

Installed GUI was disabled. To access the existing button, changed only
GuiConsoleEnabled and GuiConsoleVisible from 0 to 1 while the game was closed,
with an exact-byte backup. ConsoleEnabled, graphics backend, game settings,
UHT settings and mod activation were not changed. Source SettingsManager.cpp
confirms the two INI keys; UE4SSProgram.cpp 228+ starts the existing external GUI.
Computer Use could list windows but twice timed out capturing Steam; no game
input was automated. The user was given the single built-in-button procedure.

**Observed log:** one game process/session, 02:24:30–02:25:39 Moscow, UE4.27,
UE4SS v3.0.1 Beta #0 / 83330635. The user reported generation finished and game
closed. The log records **three**, not one, sequential UHT starts/completions:

| Start, Moscow | Completed | Duration |
| --- | --- | --- |
| 02:25:02.072 | 02:25:06.653 | 4.5801505 s |
| 02:25:26.559 | 02:25:31.788 | 5.2290793 s |
| 02:25:31.817 | 02:25:36.900 | 5.0829033 s |

The reason for repeated activation is unknown. Only the final completed tree
survives; earlier generated trees were replaced by the generator. No further run
was requested/performed. The transient first read overlapped replacement; analysis
uses the final stable copy after process exit. No CXX asset load/free markers
appear in the preserved session log. No process was forcibly terminated.

## Found declaration and interpretation

Found `Genesis/Public/ExtendedUserWidget.h`, class
`GENESIS_API UExtendedUserWidget : public UUserWidget`, at line 28:

```cpp
void SetupTipMessage2(
    TArray<UTextBlock*> utexts,
    TArray<UPanelWidget*> imgContainers,
    ETipWidgetMode display_mode,
    TArray<FText> msgs,
    TArray<UTexture2D*> base_textures);
```

The matching generated .cpp stub has the identical parameter list. **Its empty
body is a generated placeholder, not the game's native implementation.**

| Position | Name | Reflected declaration type | Direction supported by generator |
| --- | --- | --- | --- |
| 1 | utexts | TArray of UTextBlock pointers | Input value |
| 2 | imgContainers | TArray of UPanelWidget pointers | Input value |
| 3 | display_mode | ETipWidgetMode | Input value |
| 4 | msgs | TArray of FText | Input value |
| 5 | base_textures | TArray of UTexture2D pointers | Input value |

**Evidence for flags, not just C++ spelling:**
[generate_function_parameter_list](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/SDKGenerator/UEHeaderGenerator.cpp#L3292)
iterates FProperties in field order and emits only CPF_Parm excluding
CPF_ReturnParm. It emits const for CPF_ConstParm and & for either CPF_ReferenceParm
or CPF_OutParm. Its forced const-reference exception applies only to string
properties; none of these five is a string property. Therefore for these inputs
the generated result supports **Parm set; ConstParm, ReferenceParm, OutParm and
ReturnParm clear**. [Return generation](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/SDKGenerator/UEHeaderGenerator.cpp#L986)
uses void only when GetReturnProperty is null: there is no return parameter.
No full numeric property mask, offset, array dimension or function pointer was
captured. This is a reflected declaration, not a reconstructed x64 calling ABI.

Header emits UFUNCTION(BlueprintCallable), but the existing generator setting
MakeAllFunctionsBlueprintCallable=1 can add that annotation. It does **not** prove
the original FUNC_BlueprintCallable bit; the full UFunction mask/FUNC_Native is not
certified by that macro. MakeAllPropertyBlueprintsReadWrite and
MakeEnumClassesBlueprintType are also enabled, unchanged: generated macros/enum
underlying types must not be blindly treated as original flags. They do not alter
the parameter qualifier rules above. No need to change generator configuration
or rerun to answer this stage's question.

## Comparison and next boundary

The five declared positions exactly match the prior TipHUD ubergraph call at 713:
TextBlock array (built from TextBlock_89), ImagePanels (PanelWidget array),
display mode, ConvertMsgTagToTextArray output (FText array), and base_texture
(Texture2D array). Caller-local reference/const flags in that AST are **not** the
callee's flags; the new reflected declaration supplies the missing distinction.
The same header also emits the expected proxy with six const-reference arrays
and a bool-returning CanShow. Native parent declarations are not runtime
observations of the TipHUD Blueprint overrides.

**Sufficient to proceed to preparation of one narrow observer:** the missing
native declaration is now established. A subsequent observer must still check the
exact loaded UFunction/actual native flags before registering, preserve nil
callback returns, and verify this UE4SS revision's array/FText/enum wrapper
handling and bounded readback. This run registered no target hooks and proves
neither their safety/activation nor actual caller/widget identity, write ordering,
later overwrites, input-device transitions or ladder ownership. Production gate
remains BLOCKED; no further runtime action is part of this result.

## Evidence identity, checks and final installed state

Raw 12,477-file dump, source snapshots, logs, copy manifests and verification
scripts remain ignored under `.local/research/interaction-prompts/uht-run` and its
parent. Copied final dump verified file-by-file by SHA256; no raw header tree or
game log is tracked/public. Only this small derived signature and analysis are
published.

| Evidence | SHA256 |
| --- | --- |
| Game EXE (matches accepted baseline) | ddea6b5ca5d34836f01702993d20209c2595367287e6cd5a135a7ace1958b1c0 |
| Installed UE4SS.dll | ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290 |
| ExtendedUserWidget.h | f70d18591773056071ee7157e9ddc62f70ea64c949457a92c9d0fd94ec83a793 |
| ExtendedUserWidget.cpp generated stub | 52da7f31f06de96691454585375014335401223d52410eeebff839bc100659a9 |
| Final session log | 94416c6a3353429ecc46e079918fcecf1837c515dab6b21e0ea5fc40f6cd1502 |
| Copied-output/after manifest | 642a3862ea34af90d9c3af817fe4d2d2812ad202ebff9bcac16fa79583aa445d |
| UEHeaderGenerator.cpp source snapshot | e1e2e68fc4dea35933c504f6416843571a80d38675be4ab85edc26367460e18b |

Offline verification compared header/stub declaration, five argument types/order
against the retained Blueprint AST, three completion markers, copy hashes and
installed/protected-file deltas. `tools/test.py` reports no automated runtime test
suite; document checks do not establish gameplay/visual acceptance.

After confirming the game closed, restored original loader config bytes/hash
`631485c0a44eb506dbe1e7d81ebc96fc3e6a0aeab5647b324ef18d1927e65c84`.
All eight original installed mod files and all 55 pre-existing save/config files
remain hash-identical; no mod file added. The new GUI imgui.ini was archived,
hash-verified and removed after exit. Generated UHTHeaderDump remains locally at
the loader working directory, with a verified ignored copy; it is data, not an
active mod. Normal session logs remain. One new per-session CrashReportClient.ini
was created at startup and is left intact; no pre-existing gameplay settings or
saves changed. That file's name alone does not establish a crash; the latest
crash-directory timestamp predates this run. No temporary loader-config change,
new payload, native hook or running game process remains.
