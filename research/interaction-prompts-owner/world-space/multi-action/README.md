# Multi-action read-only native prompt observer — 2026-11-05

**SOURCE-ONLY / NO INSTALLATION / NO LIVE Take/Check ACCEPTANCE.**

This is a **new, separate, read-only** research successor on
`research/multi-action-observer`, branched from IIP
`74ec3a4247feed0be9c8bf8788f5839c6cad20ae`. It does not mutate,
repackage or replace the installed-and-rolled-back
`auto-target/` source `db89283747f2e25c206b1fc762b68aeabdbcb771`,
the archived evidence, the accepted frozen CompactLayoutProbe
(`2981375afadb968fb272eeab33aab8d384e639ef`), `main`, `VERSION`,
game files or installed activation markers.

## Evidence and bounded hypothesis

- **Live confirmed:** the one Nov05 normal-save-load test observed
  six `Open` actor→ExtendedWidget→TipHUD triples ready at global
  `BeginPlayPost`, and one native-visible owner appearing twice and
  disappearing twice. It did **not** observe distinct-owner handover,
  `Take` or `Check` acquisition, or EndPlay eviction of a joined owner.
  [Exact previous run](../auto-target/README.md#normal-load-runtime-result--2026-11-05).
- **Static host evidence:** `BaseLoot2_BP` (inherited `msgTag=Take`),
  `BaseLoot_BP` (`msgTag=Open`) and `BaseDocumentObject`
  (`msgTag=Check`) use descendants of `BaseGameEventObject_BP`
  with the same `ExtendedWidget`/TipHUD argument chain.
  [Verified owner inventory](../../../../docs/VERIFIED_RUNTIME.md#1-подтверждённый-ui-owner-и-цепочка).
  This is *not* live verification of those two additional actions in the
  installed game, nor support for every placed object/class.
- `Ladder/Descend`, bonfires and arbitrary `Interact` are **excluded**
  until their own actor/UI contract is observed. The upper technical
  `OPEN` glyph is not a verified translation, and no product glyph
  mapping is implemented here.

## Source and resource discipline

Four co-located Lua research files:

1. [`main.lua`](main.lua) registers global BeginPlayPost, EndPlayPre
   and LoadMapPre and an EngineTick-loop callback. No manual activation
   chord, CanShow hook, World UI or native setter.
2. [`IIPInteractionSource.lua`](IIPInteractionSource.lua) classifies only
   *exact* `Open`, `Take`, `Check` action tags with existing
   `ActionName=Interact(25)`, and checks the reciprocal
   actor/component/argument/TipHUD ownership and native localized text.
   A read-only snapshot preserves the native text only when ready.
3. [`IIPInteractionEvents.lua`](IIPInteractionEvents.lua) maintains
   primitive identities supplied by natural BeginPlay, releases them by
   EndPlay/map clear and observes native UI for known actors. A pending
   widget is retried without forced BeginPlay/InitWidget/asset creation.
   A vanished owner is retired without native writes; unexpected identity
   changes fail closed.
4. [`IIPOpenVisibility.lua`](IIPOpenVisibility.lua) is the unchanged
   earlier read-only native TipHUD/retainer/image visibility reader.

**No arbitrary session timeout, total sample count, total BeginPlay count
or maximum world candidate count.** The game/user sets the session length.
The loop runs every **30 game frames** (same rate as the previous
bounded probe; shorter transient UI can still be missed). At most
**48** registered/pending owner identities are read during one callback,
limiting game-thread work. Up to 40 JOIN events include detailed paths,
then repeated initial-owner detail is throttled; an actually visible
owner's action, path and localized text are logged on its first
observation, even beyond the join-detail threshold.
State transitions are logged on change, not every frame.

When more than 48 identities exist, the observer rotates through them
across ticks and marks every such sample `incomplete_snapshot`.
When a pending/unresolved, newly joined, or vanished owner interrupts a
complete sweep, it also marks the sample incomplete. **Neither a
partial sweep nor a simultaneous multiple-visible native set may yield
a unique target claim.** Even `unique_observed` from two complete
snapshots is *observational evidence*, not a verified game-selected
target or authority to bind World UI.

Any material broken ownership/native identity or hook contract stops
the read-only observer, makes registered callbacks inert and requests
the verified loop cancellation. No game, UI, save or settings writes
are performed. The old `IIPTargetPolicy.lua` bind/release-ack contract
is deliberately not invoked: there is no renderer attached to this
read-only probe.

## Offline gates and acceptance boundary

- [`tests/test_multi_action_observer.py`](../../../../tests/test_multi_action_observer.py)
  covers Open→Take→Check visibility under Lua mocks; two visible
  owners; repeated same owner; untimed operation and >8192 unrelated
  BeginPlay callbacks; more than eight candidates; incomplete rotating
  snapshots; not-ready widgets, owner loss, map/EndPlay, strict action
  and alias contract faults, inert callbacks and no native writes.
- [`tests/test_multi_action_entrypoint.py`](../../../../tests/test_multi_action_entrypoint.py)
  covers the standalone `require` path, normal UE4SS event
  registration and missing-API failure.
- The prior `auto-target/` tests remain unchanged regression
  coverage for the **old immutable candidate**, not normative
  requirements on the new observer.

**Before any installed trial:** capture exact new source HEAD, run the
offline suite, establish a frozen source manifest, inspect host-closed
installation and conflict with `CompactLayoutProbe`, get distinct
permission and prepare rollback outside loader paths. Local Codex is
only needed for that installed-host segment, not source engineering.
Do not silently install over the earlier test or claim engine acceptance.

**Next sufficient native question:** after authorized user-paced
run, do `Take` and `Check` acquire naturally with ready TipHUD and
localized text, and are their active visible/native owner sets
unambiguous in nearby Open/Take/Check transitions? If registration
is so large that only partial snapshots can be collected, the
observer returns `incomplete_snapshot`: use that finding to refine
the observation seam, not to assert chosen focus. Separately
establish repeatable native World-component release/creation
before linking any target policy to a renderer.

No additional host/runtime evidence has been collected by this source
work. Candidate is **NOT_INSTALLED / NO_PRODUCTION_ACCEPTANCE**.
