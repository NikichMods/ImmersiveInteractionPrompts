# Multi-action read-only native prompt observer — 2026-11-05

## Runtime result — 2026-11-06

Steam 1.09/build 12996889, UE4.27, UE4SS 83330635. Source
`1780f0a8230149135b61bafcdb81c61e2f1d4e36`, installation `f3212f6`.
All four installed Lua hashes and the marker matched before rollback.
Private archive `runtime-20261105T224845Z` contains the full logs and installed
manifest. UE4SS.log SHA-256
`5f767ab83417bb8701aae5b1dfe39c3934278d92b373c200632d97d757e0fb35`.
Genesis.log SHA-256
`453bed403a1f5011d85b0ae4044f99f34933a9dbfcaae95a82da09a982d67a27`.
Genesis recorded normal exit at 01:48:14 Moscow.

| Gate | Result |
| --- | --- |
| Discovery and readiness | **PASS** in this session. 34 distinct joins at BeginPlayPost: Open 6, Take 18, Check 10. All logged `ready_at=beginplay`. Pending recovery **NOT_TESTED**. |
| Native text | **PASS** for the three sampled owners. Open #10 displayed «Открыть», Check #3 «Проверить», Take #19 «Взять». The user described the pickup as «подобрать». Exact display of that word is **UNKNOWN**. |
| Visibility and owner changes | **PASS** for sampled distinct owners separated by withdrawal. UE4SS lines 763–790 show #10 → #3 → #19 → #3 → #10 with zero shown owners between and after. Each visible interval reached two complete sweeps with one shown/ready owner out of 33. |
| Additional approach and selection | **UNKNOWN** for the third «Открыть» reported by the user, which has no separate logged interval. Its absence has no established cause. A direct handoff without withdrawal and the game's authoritative selection remain **UNKNOWN**. |
| Lifecycle | **PASS** for EndPlay eviction. Owner #2 left during load (line 696), then 33 distinct owners left on normal exit and the registry reached zero (lines 791–823). Three LoadMapPre events occurred before acquisition. Clearing a populated registry on travel **NOT_TESTED**. |
| Safety and log scope | No identity fault, Lua exception, stale-owner fallback, incomplete sweep or observer STOP appears in the archived log. 34 joins, 34 owner removals, 10 visibility changes and 20 selection transitions were logged. The host exited normally. |

The reported order was Open, Check, pickup, Check, Open, Open, with withdrawal
between approaches. Five intervals correlate in order. The final reported Open
has no independently matched owner ID. Sampling every 30 frames limits the
claim to recorded states. The visibility evidence covers registered owners in
these complete sweeps.

After archiving, rollback restored the original CompactLayoutProbe marker.
Its 12 original file hashes matched across the payload and restored marker.
MultiActionProbe is disabled and its payload is retained.

## Local payload preparation

The four Lua files match the tested source `1780f0a8230149135b61bafcdb81c61e2f1d4e36`
byte for byte. Local verification passed 403 tests across 31 files. The installed
UE4SS hash matches the prior 83330635 runtime. The observer samples up to 48
owners per sweep and runs at the user's pace through normal game exit.
[Source and SHA-256 manifest](SOURCE_MANIFEST.json).

The prepared destination is a separate MultiActionProbe. CompactLayoutProbe is
the active IIP probe at preflight. Its complete installed payload and marker
have a hash-verified backup outside UE4SS under `multi-action/prepare-1780f0a`.
After explicit authorization the four Lua files and empty marker were installed
and verified with the host closed. The switch temporarily disabled the
CompactLayoutProbe marker and preserved the hashes of 181 existing files.
The installed manifest and rollback are in the private preparation archive.
The native Open/Take/Check run is pending.

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
Per-owner native visibility changes are logged independently, including
hidden-after-visible transitions. Rotating partial sweeps log only the
incomplete state and genuine owner transitions: merely scanning a different
batch does not manufacture a hide/show or spam logs every tick.

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
