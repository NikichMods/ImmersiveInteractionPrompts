# Independent UserWidget probe — READY_SOURCE, runtime NOT_TESTED

## Authorized installation — 2026-10-29, runtime PENDING

Prepared source commit a23635b95b029ff8d73dec4f940e1aa54c213d37 installed unchanged
as ImmersiveInteractionPromptsUserWidgetHostProbe (main.lua + empty enabled.txt).
Host closed before copy/enable; installed source hash matches below. All22 prior
mod/loader files and63 config/save files retained hashes. Old IIP probes disabled.
Rollback to prior absent target, source copy, prior log/settings and hash manifests
are outside loader in ignored host-probe/install-20261029T081829Z.
No launch/hot reload or runtime observation. Source preparation comments remain
unchanged to preserve exact tested bytes. Follow the test procedure below;
installation authorization has now been received and executed.

## Preparation record

2026-10-29. Research-only [source](Scripts/main.lua), not installed or executed.
Steam1.09/build12996889, UE4.27, UE4SS83330635. Production/World gates remain BLOCKED.
The [candidate audit](../README.md) remains the source for Blueprint callbacks,
private tree structure and native Create/Slate contracts. No new Blueprint,
cooker, C++ bridge, font or game asset is distributed.
Lua source SHA256: `66ffdce4fecdf954981a5364320bc78f3f67df717ee16175673558bac9543186`.

## Exact loading contract

An offline targeted read of the installed `Genesis/AssetRegistry.bin` found both
the WidgetBlueprint entry and a separate WidgetBlueprintGeneratedClass entry at
`/Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C`.
The latter has UMG.UserWidget ParentClass/NativeParentClass and chunk0. The original
registry SHA256 is `9ba7a655f82877869145de2bc62c2fa76b392fd3d8e7ec67b6b9667784f1ac92`.
Raw records and the small offline reader remain ignored/local. Existing dotnet8 /
CUE4Parse1.2.2 cache was reused; no software/package installation was performed.

Pinned UE4SS LuaMod.cpp3334ff resolves LoadAsset through this registry and returns
object, was_found, did_load; it requires the game thread. The probe first checks
the exact class with StaticFindObject. If absent, it makes one LoadAsset call to
the exact generated-class path, then checks both booleans, returned-object identity,
UClass type, exact path and direct UMG.UserWidget superclass. There is no guessed
Blueprint fallback, alternate class search or unload operation. A registry record
establishes an available offline route, not successful live loading.

Create uses the reflected `/Script/UMG.WidgetBlueprintLibrary:Create` UFunction,
its exact library CDO as explicit receiver, an existing gameplay HUD as read-only
WorldContextObject, the checked class and nil OwningPlayer. This mirrors the native
Create contract; the new marshaled call itself is still untested in this game.

## Bounded lifecycle

- Ctrl+Alt+F6 dispatches through the already proven EngineTick mechanism. Collision
  or missing startup API disables the probe. One load/Create attempt per process;
  no hook, per-frame monitor, rearm or automatic retry.
- One bounded class lookup of HUDMainUMG_BP_C (max8 results) supplies context and
  an original-tree fingerprint. Another exact candidate-class lookup (max32)
  records existing identities. Neither is an all-object/actor inventory.
- Create must return a fresh exact-class instance, absent from existing instances,
  without CDO/archetype flags. Its tree must be outered to that instance, with the
  exact four-widget hierarchy and reciprocal slots. Checks precede tree writes.
- Collapse only the new host's Main_Panel placeholder. Add one transient TextBlock
  under its private tree/root, with an independent FontInfo copied from its own
  Value_Text. Show `USERWIDGET HOST` in a small centered viewport composition.
- AddToViewport builds Slate. Require the expected Construct Hidden state, then
  set only this own host to HitTestInvisible. No shipped SetText helper is invoked.
- Second Ctrl+Alt+F6 removes only the label and own viewport holder. A single
  delayed callback requests cleanup after60s. The deadline starts before load;
  an over-budget synchronous creation aborts before attachment. Native synchronous
  loading cannot be preempted by Lua; this is not a hard interrupt guarantee.
- Cleanup hides the identified own instance first, checks label outer/parent,
  detaches it, calls own RemoveFromParent, checks viewport/parent release and drops
  primitive identities. No AddToRoot, forced GC, UObject destruction or package
  unload. A cached loaded class may remain resident; this is not a leaked UI owner.
- Weak Slate liveness can briefly remain after removal. In that case the probe
  records CLEANUP_FAILED and keeps identities for another explicit F6 cleanup;
  it never claims release or creates another instance. An expired/gone own object
  is already free of live UI ownership. Stopped key/timer callbacks are inert.

Own viewport ownership is native Slate/UserWidget ownership after attachment;
Lua UObject wrappers and Outer are not assumed to root objects. Create/build run
synchronously in one game-thread callback. No long-term raw wrapper is retained.

## Future test, only after separate installation authorization

1. Start normal gameplay with original HUD visible. Press Ctrl+Alt+F6 once.
   One `USERWIDGET HOST` label should appear at screen center. Original interaction
   prompts, controls and other UI should continue normally.
2. Press the same chord again before60s. Only the test label should disappear.
   Do not repeat a failed creation in the same process; retain the diagnostic log.
3. Exit normally. Review the log for INSTANCE_VALIDATED → CONSTRUCT_HIDDEN →
   VISIBLE → LABEL_REMOVED → OWNERSHIP_RELEASED → CLEANED reason=user, with
   ORIGINAL_TREE_UNCHANGED. CLEANUP_FAILED permits one further explicit cleanup.

The foreign fingerprint covers HUD/tree/root identity and root child count, not
every UI property or every interface. PRESERVATION_UNVERIFIED/CHANGED is reported
without repairing foreign state. User observation is still needed for original UI
preservation, visible text, input behavior, ownership over callbacks and teardown.
There is no claim of native GC completion or a production lifecycle.

## Offline checks and next boundary

`python tools/test.py`:74 tests in8 suites pass, including8 new host-policy tests
using Lua mocks. New cases cover exact/resident/missing/wrong class, invalid parent,
existing/CDO returns, foreign tree alias, unexpected Construct, partial attachment,
timeout and cleanup-release retry. Mocks execute Lua and assert own-only mutations;
they do not execute engine loading/Create/Slate/rendering/GC.

The next sufficient experiment is this host-only create/show/manual-cleanup run.
World-space registration/materials and exact natural Open component/pose remain
separate gates. Aphes, TipHUD, chest selection and accepted divider/viewport tests
are deliberately absent from this probe.
