# Committed owner +0x410 — read-only runtime correlation candidate

**SOURCE ONLY / NOT INSTALLED / NO RUNTIME CORRELATION YET /
NO PRODUCTION OWNER READER / NO GAME CHANGES.**

## Candidate controller acquisition without global enumeration — source-only, 2026-11-07

The earlier `fdee186` installation is correctly **BLOCKED** by the preflight
below. The revised research source replaces the installed
`UEHelpers.GetPlayerController()` call, and with it
`FindAllOf("PlayerController") / FindAllOf("Controller")`, with an
**event-captured identity**:

1. A global `RegisterBeginPlayPostHook` callback observes ordinary actor
   lifecycle (already exercised for IIP Open/Take/Check), but **does not
   enumerate the object array**. It only considers actors whose ancestry
   reaches `/Script/Engine.PlayerController`, then checks the existing
   reflected `IsLocalPlayerController()` used by pinned UEHelpers.
2. Only the observed controller's **path, class, and address** are retained;
   no borrowed UObject wrapper survives the event callback. In the game-thread
   sample, a `StaticFindObject(exact_path)` re-resolution must still match
   all three fields and be native-valid/local. This is an exact identity
   lookup, **not** `FindAllOf`, class enumeration, or a search for a new
   controller. Then the unchanged pawn→PlayerActionComponent→+0x410
   weak-property read runs.
3. `RegisterEndPlayPreHook` and `RegisterLoadMapPreHook` invalidate the
   captured identity; failures stop or yield `GAP`, never fabricated
   hide-to-null. Two simultaneously observed different local controllers
   fail closed. Native TipHUD remains visible.

**Remaining uncertainty:** whether controller `BeginPlayPost` is delivered
after this Lua observer registers during the user's natural saved-game load.
If the controller pre-exists, `CONTROLLER_PENDING` remains with no
`CONTROLLER_ACQUIRED`, and the observer collects **zero** selected-owner
evidence; it does not bypass this with a scan. Presence of the reflected
`IsLocalPlayerController` on that actual controller is also subject to
native integration testing. Per-actor callback and exact-lookup costs
are not measured. This is a source-only candidate, **not** a tested installed
replacement or a change to the authorization boundary.

New offline tests explicitly deny `FindAllOf`, check no-capture behavior,
unrelated/nonlocal actors, acquisition, EndPlay, map reset, stale identity,
and the original selected owner/TipHUD correlation.
**Exact source/test commit:** [`df238c7`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/df238c7b30f666d13669bc5e31970fa2a0d0288a).
[GitHub Actions 42372741024](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42372741024):
**515/515 offline tests PASS, 47 files, 16 selected-owner tests**. No game
install/run or runtime callback evidence. Existing installation permission
referred to the **earlier exact** candidate: the revised bytes require a new
closed-host installation authorization.

## Local deployment preflight — 2026-11-07

**BLOCKED by the no-full-object-scan constraint.** Game was closed.
Steam shipping executable and UE4SS DLL matched the hashes below.
The four worktree Lua files matched Git blobs from the authorized commit
`fdee186ac6b064c1dce50d09eccc550cb0ed34cc`. GitHub confirmed success for
[run 42323045068](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42323045068)
at `0c5ff3c7eb0a0b5ffa610af9aac29cdb0e88bb08`; the two commits differ
only in status documentation.

The installed external UEHelpers, SHA-256
`7476f02eef0c87bfeab169f2ffe2e704363faeaae4bf9f1bda574b1e34f4a0e9`,
implements `GetPlayerController()` via `FindAllOf("PlayerController")`
with a fallback to `FindAllOf("Controller")`. The
[pinned UE4SS API](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/docs/lua-api/global-functions/findallof.md)
documents a complete pass over the global object array per call.
`main.lua` retries controller acquisition on each sampled frame while the
cached controller is invalid and resets it on map pre. The selected-owner
lookup itself is scoped to a pawn component, but its controller acquisition
dependency can perform repeated global scans. Offline mocks do not exercise
the installed helper's implementation.

No game or loader files were written. CompactLayoutProbe remains the sole
active IIP mod. No new rollback snapshot was required. Deployment requires
a separately authorized candidate or an explicit exception for this
controller acquisition behavior.

## Question and source contract

The [local native trace](../event-driven/TARGET_AUTHORITY_STUDY.md#selected-owner-read-seam--local-native-trace-2026-11-07)
identified `UPlayerActionComponent` as the actual UObject stored at
`GenesisCharacter+0x560`; the committed, pre-input selected
`ABaseGameEventObject` is its 8-byte weak pair at **component+0x410**.
The proposed +0x418 field is **not** the accepted owner, and
`GameGlobal:GetActionTarget` reads unrelated state.

The pinned UE4SS `83330635` source permits a class-scoped
`RegisterCustomProperty(PropertyTypes.WeakObjectProperty)`; the returned
Lua weak-object wrapper **copies** the pair and exposes `Get()`.
The exact component can be found through reflected
`AActor:GetComponentByClass`, whose native call uses the same component
lookup slot as the character's setup.

The open question: does this exact, build-pinned composition return
the correct selected actor through normal Open, Take and Check approach,
withdrawal, A→B switch and map/pawn transitions *without changing*
stock visibility or adding meaningful per-frame cost?

## Standalone source

Copy these **four files together** under the Scripts directory of a
separate, research-only UE4SS mod, but **only after separate installation
authorization and closed-host preflight**:

- `Scripts/main.lua` — exact reflected component/weak-property registration;
  obtains the local controller **only** from natural `BeginPlayPost`, stores
  primitive identity, re-resolves that one exact controller per frame, checks
  native validity and component ownership; one `GetComponentByClass` + weak
  `Get` per ready tick.
- `Scripts/IIPSelectedOwnerObserver.lua` — state machine for actual
  committed-owner transitions; never determines a winner from spatial
  geometry, CanShow, visibility or heuristic target ranking.
- `Scripts/IIPInteractionSource.lua` — byte-identical copy of the
  previously tested Open/Take/Check actor↔widget resolver.
- `Scripts/IIPOpenVisibility.lua` — byte-identical copy of the previously
  tested native screen visibility reader.

The revised entrypoint does **not call UEHelpers**. It uses the same reflected
`IsLocalPlayerController()` method visible in the installed UEHelpers
source. The existing external dependency is untouched; no extra helper or
host assets are installed/force-loaded.

Custom property `IIPResearchCommittedTipOwner_83330635` belongs only to
`/Script/Genesis.PlayerActionComponent`, offset `0x410`, weak size 8.
Registration only extends UE4SS metadata; it does **not** set that field.
It is not safe to use this private layout on an unidentified/changed game
binary. Exact installed Steam 1.09/build 12996889 shipping hash must match
`ddea6b5ca5d34836f01702993d20209c2595367287e6cd5a135a7ace1958b1c0`
and the UE4SS DLL identity must match
`ce5e3c46a920cc00b2817ac61e438c9162830290379d0b5b9c4dfc2b29459290`
**before any installation**.

### Observation boundaries

- The game-thread observer performs one selected-owner read per frame **only
  after a local controller has been observed in BeginPlayPost**. No global
  `FindAllOf` call, all-interactables enumeration, global `ProcessEvent`, synthetic
  interaction, hook on native show/hide or UMG mutation.
- On a selected-owner change it samples **only** previously selected
  and newly selected *supported* Open/Take/Check owners, using independent
  `IIPInteractionSource.snapshot` and native TipHUD visibility/ready checks.
  The visibility correlation is sought 1–12 observer frames later, up to
  16 concurrent transition records to bound work. These are **diagnostic
  response windows**, not a session timeout or a production scan budget.
- Logs `IIP_SELECTED_OWNER event=TRANSITION`, `CORRELATED`,
  `NO_MATCH`, `CONTEXT`, `CONTEXT_REPLACED`, `CONTEXT_GAP`,
  `MAP_RESET`, `STOP`, or `UNAVAILABLE`. Correlated means a **later
  readback**, not a pixel or native call timestamp.
- A null weak read with a valid pawn/component is **NONE**; a missing
  controller/pawn/component is a **GAP** and does not prove hide-to-null.
  Component replacement and map change reset pending comparisons.
  Unsupported action owners are excluded from Open/Take/Check evidence.
- State carries only primitive actor/component/widget identities between
  ticks. All UObject/weak wrappers are read and discarded in the same tick.
  Native lifecycle beyond checked identity and the full 12-frame response
  window is not proven; this test never writes prompt state.
- One fresh component lookup each sample and native visibility readbacks
  may have non-negligible cost. Counts in STOP are **work counters**, not
  frame-time measurements. A separate profiler/native frame-time check
  would be required before production performance acceptance.
- The observer does not independently inspect visibility of *all* other
  prompt actors. It cannot prove all-frame global uniqueness or absence
  of other simultaneous on-screen prompts.
- A failing read, mismatch or callback contract stops future observation
  with `STOP`. Map-pre and callback registrations remain inert after STOP;
  explicit loop cancellation is attempted.

## Offline verification and current gate

`tests/test_committed_owner_observer.py` checks the Lua state machine
against a strict synthetic owner stream and entrypoint registration against
a read-only UE4SS mock. It exercises true vs mismatched native visibility,
Open→Take direct switch, hide-to-NONE, map gap, component replacement,
not-ready widget retry, out-of-scope owner, contract errors, cancellation
and no arbitrary session timer. **Mock results are not live proof**.

After CI/source checks, the next independent gate is **separate user
authorization** for local Codex to prepare a rollback outside all
loaders, close-host install this exact source, disable only the previously
active IIP probe marker, hash-check all touched files, and leave the game
closed. Do not infer that creating this branch authorizes deployment.

After separate user-started normal game session, visit:
Open → leave → Take → leave → Check → leave; also move A→B directly if
two eligible objects are adjacent. Record logs including `NONE`, show/hide
and context replacements. Do not treat absence of an observed transition
as proof it cannot occur. After host closes, restore the prior IIP marker
and verify hashes/other mods, save and settings unchanged.

**Decision:** if correlation and lifecycle pass, evaluate the World path's
separate render latency, resource creation/reuse and independent native
visual suppression gates. If this selected-owner route fails decisively,
prioritize a native TipHUD-owned Screen S1 source design and seek user
acceptance of the changed depth occlusion. Production remains BLOCKED.
