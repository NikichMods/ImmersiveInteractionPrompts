# Native World experiment for one Quintus prompt

## Why the early write should survive

The [read-only run](../native-world-observer/README.md#runtime-result--2026-11-20)
matched a callback with CreationMethod=Native and empty WidgetClass to the
same ExtendedWidget and TipHUD at BeginPlay and Talk. UE4SS delivered it before
SCS assigned the creation method and registered the scene component.

The cooked `NPCInteract_Bp_C` export omits
`bHasCookedComponentInstancingData`, whose UE4.27 class constructor defaults
to false. Base `SCS_Node_7` also has no exported cooked instancing data.
For the shipped exports this points to the ordinary
`CreateComponentFromTemplate` branch. `StaticDuplicateObjectEx` constructs
the destination and then serializes the source template. The duplicate
archives use delta serialization, and reflected tagged saving skips properties
identical to the source object's archetype defaults. The ExtendedWidget
template has no serialized Space override against the Genesis Screen default.
The expected stream therefore transfers WidgetClass and other authored
overrides while omitting Space. Loading those tags into the already
constructed destination should leave the early World write intact.
This is a source prediction. The host binary's later Genesis callbacks have
not been observed with World in this path.

Sources: [BlueprintGeneratedClass.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/BlueprintGeneratedClass.cpp#L1230),
[ActorConstruction.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/ActorConstruction.cpp#L970),
[UObjectGlobals.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/UObject/UObjectGlobals.cpp#L2014),
[Archive.cpp defaults](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Core/Private/Serialization/Archive.cpp#L161),
[Obj.cpp property serialization](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/UObject/Obj.cpp#L1435),
[Class.cpp tagged delta](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/UObject/Class.cpp#L1548).

## Stable scope

- Cooked `1-1_plot_slumB1_main1` contains one authored Quintus creator,
  `1-1_QB_Quintus_creator`, with character `quintus`,
  `InitialCanInteract=true` and tag `1-1_Quintus_QB`. Its map export has
  no preplaced `NPCInteract_Bp_C`. A prior runtime log records a live
  `quintus_BP_C` in this exact sublevel alongside the matched interaction
  actor. The guard uses exact class and sublevel for both objects plus the
  actor's reciprocal ownership chain. Generated numeric names are used only
  to recognize the expected form and correlate within one session.
- `BaseCharacter_BP_C` passes self into
  `CharacterFunctionLibrary_C:CharacterSetCanInteract`. At bytecode
  offset 501 the function calls `GameGlobal:SpawnObject(caller_character,
  NPCInteract_Bp_C, transform)`; offset 548 stores the result in
  `NPCInteractObject`. In the exact Shipping binary, the
  reflected `SpawnObject` thunk at RVA `0x128CFE0` calls through
  `0x11137A0` to `0x113A4A0`. This body passes the first argument as
  `FActorSpawnParameters.Owner` at `0x113A4E8` and calls the
  `UWorld::SpawnActor` entry at `0x2EAB560`. UE4.27 chooses the owner
  level and sets the owner in `PostSpawnInitialize` before SCS. The
  candidate checks that relationship at the point of mutation.
  [LevelActor.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/LevelActor.cpp#L384)
  · [Actor.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Actor.cpp#L3102).

The map and spawn-function exports remain local. Their SHA-256 values are
`344e9b5cdcbb9d2a3be386f7e20297aa5b54378f317ffa3191235a60b3003446` and
`7a6018817757cabcceb06fa3c819085862b690c57c9b6c4e9e051ef3067ef611`
respectively.

## Candidate and one-run criterion

`Scripts/main.lua` applies NoCollision and then World to one original
component while the observed early construction signature still matches.
World geometry can have collision, so the candidate sets NoCollision first
and aborts before the World write if the readback differs. It keeps the
authored attachment, draw size and geometry. It logs the resulting native
widget in BeginPlayPost and takes one manual render-target sample. No extra
component, renderer, widget, visibility controller or repeated sampling.
Screen S1 stays installed and active. Its own Screen visibility gate can
leave Aphes and the divider collapsed on this World component.

Load the same save, approach the same merchant once, pause briefly at
interaction distance, press **Ctrl+Alt+F5** once even if no prompt appeared,
and exit normally. Record whether the stock action/button was visible or
occluded if apparent. Check `IIP_NATIVE_WORLD_QUINTUS`:

- `SET_WORLD` confirms the scoped early write. A missing event or `SKIP`
  is a target/guard result and provides no survival evidence.
- `BEGIN space=1` after `SET_WORLD` shows that the early write was lost.
  `BEGIN space=0 collision=0` checks both values after normal initialization.
- `SAMPLE space=0 render_target=true` for the native TipHUD supplies
  evidence of actual World draw infrastructure on the original component.
  A missing render target leaves drawing unconfirmed. World positioning,
  projection and readability require direct observation even with a target.

## Installed for one run — 2026-11-20

Candidate source `e2e9aa98bfa034e220aa21a05c93d4f2e1269331`.
Seven offline Lua scenarios passed with mocked UE4SS callbacks: survival,
overwrite, wrong owner, late delivery, collision setter failure, sample-key
conflict, and identity loss. The cases exercised control flow and guards.

Installed with the game closed in its own
`ImmersiveInteractionPromptsNativeWorldQuintus` folder. The SHA-256 of the
installed entry is
`fb20e419f3b2103ace49f7d3d512f36266de23cd39d45978c9184ab0f73da30c`.
The full Screen S1 installed inventory matched before and after, as did
the existing loader files, other mods, game settings and saves. The
pretest log and receipt were archived outside the loader. The two-file
rollback to the S1-only configuration passed on a copy. Runtime pending.
Production BLOCKED.
