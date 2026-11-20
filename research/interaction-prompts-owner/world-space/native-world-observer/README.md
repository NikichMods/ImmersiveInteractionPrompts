# Read-only observer of native TipHUD construction

[Question and static evidence](../event-driven/NATIVE_WORLD_PREREGISTRATION.md).
Target: Steam 1.09/build12996889, UE4SS 83330635, one first approach to the
same merchant in `1-1_plot_slumB1_main1`.

Install only the committed `Scripts/main.lua` in its own
`ImmersiveInteractionPromptsNativeWorldObserver` folder with an empty
`enabled.txt`. Keep the existing Screen S1 active. The probe registers
UE4SS callbacks and writes diagnostic log lines. It reads component
properties directly during the construction callback and calls existing
getters for the reciprocal binding after BeginPlay. It performs no
game-state writes, deferred actions, polling, or new rendering.

Load the same save, approach the merchant until the Talk prompt appears,
then exit normally. Capture the fresh UE4SS.log. The observer stops
recording automatically after the first matched Talk callback or on a
guard failure. Remove the observer folder from the loader path with the
game closed before the next unrelated session.

Read `IIP_NATIVE_WORLD` in order:

- `ARMED` establishes subscription. `CONSTRUCT` records CreationMethod,
  Space and WidgetClass for the matching NPC sublevel's exact component name.
  The probe bounds both construction and BeginPlay samples to 16.
- `BEGIN` joins the live component path and address to the early record and
  identifies the native widget. `TALK_MATCH` revalidates the identity in
  the native `CanShow` callback and identifies the record to interpret.
  A later `latest_construct_seq` can expose notification delivery after
  BeginPlay. Treat ambiguous records as inconclusive.
- A joined construction sample with CreationMethod still before SCS
  assignment supports a callback before SCS registration on this path.
  A missing sample with a valid Talk match gives no usable early callback
  in this run. `UNAVAILABLE`, `LIMIT`, `AMBIGUOUS` or a missing Talk match
  leaves the result inconclusive. The probe observes neither the actual
  `OnRegister` entry nor survival of a hypothetical Space write.

Runtime observation pending. Production BLOCKED.
