# Cheap native prompt events vs full owner scans — bounded research (2026-11-06)

> **Продолжение source-only исследования (2026-11-06):**
> [read-only event-correlation probe](PROBE.md), ветка
> `research/event-correlation-probe`, source/tests
> [`f03c571`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/f03c571f8fba9c88994a00f56daaa0ad54d95355),
> [CI 42219818296](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42219818296)
> (488 tests / 44 files PASS). Нет установленного/игрового результата.
> Ни один World-кандидат и native TipHUD не изменены.

**EXISTING_NATIVE_CALLBACK_CONFIRMED / EVENT_TO_VISIBLE_EDGE_UNKNOWN /
CURRENT_OWNER_EXCLUSIVITY_UNKNOWN / SOURCE_STUDY_ONLY / NOT_INSTALLED.**

This is a non-invasive research decision at
`research/event-driven-target-study`, based on the uninstalled
`research/auto-world-residency-latency` HEAD
`2e4c43bc6b9ca8168e84e95cf75f5a7ee1c90bb0`.
No source, hash manifest or test artifact of the prior World candidates
was changed. No game, UE4SS config, other mod or save was touched.

## 1. The user's actual success condition

Show the localized interaction and native remapped hint quickly enough to
feel immediate, preferably **well below 100 ms** from the game's
actual native show/selection (not merely the first observer sample),
with negligible CPU/render overhead and no perceptible frame-time spikes.
A measured 100–200 ms delay is already visibly undesirable to the user.
Neither a mandatory millisecond acceptance threshold nor a CPU budget
in milliseconds was separately set.

Depth-correct World occlusion remains the preferred design **if it can
satisfy latency and cost**. The user explicitly proposed **2D Screen HUD
as a conditional fallback** if this cannot be achieved cheaply/reliably:
visually position the composition where its intentional screen-space
presentation will not confusingly overlap Hilda. This is a permissible
alternative to investigate, *not a decision to drop World occlusion*.
Native actions, text, input hints, remapping, show/hide and unrelated HUD
behavior are unchanged.

## 2. Positive evidence already in the owning repository

| Seam | Actual established evidence | Crucial limit |
| --- | --- | --- |
| `TipHUD_C:CanShow()` Blueprint script post callback | Read-only `can-show-state` received **948 callbacks from three TipHUD identities** in a user-operated run; the exact non-native zero-argument callback returns `nil`, never changing the original CanShow bool. | Function asks *whether it can show*, not an authoritative event that the currently selected interaction became visible; actual bool not delivered to script callback. Repeated hidden-widget calls and return-to-visible ordering are unproved. |
| `BaseGameEventObject_BP_C:ReceiveBeginPlay` + CanShow identity join | `beginplay-probe` retained three ready Open owner/component/widget pairs and **joined one actually visible Russian Open** in 415 CanShow callbacks in the corrected runtime run. Reciprocal actor → ExtendedWidget → TipHUD checks passed. | One Open case, not every Open/Take/Check selection edge, hide edge or simultaneous native visibility guarantee. The TipHUD Outer is GameInstance and cannot alone identify its actor. |
| Global BeginPlayPost + read-only source.acquisition | A subsequent **normal-load** MultiActionProbe joined **34 ready native owners**: Open6/Take18/Check10. EndPlay retired all by normal exit. There is a unique primitive owner/component/widget record for each observed instance. | These records can seed an **indexed widget→owner map** without per-frame sweeping, but no confirmed global current-owner pointer or event→selection guarantee. |
| `ExtendedWidgetComponent:SetShow(bool,float,float)` | Exact native hook successfully registered; **0 callbacks in a 31.965-second natural run**. | Does not prove SetShow unused or permanently unhookable. Does not justify repeating the identical native-hook test or assuming events will arrive. |
| `ExtendedUserWidget:SetupTipMessage2` | Host UHT and Blueprint call at TipHUD ubergraph offset 713 identify a native consumer of localized text and textures. | Parameter-array frame address/lifetime through pinned UE4SS 83330635 → UEPseudo is **unproved** and already formally blocked. No new native-array hook/unsafe getter, no fabricated return or UI write. |
| Fixed Screen HUD-root Canvas | Prior user-operated viewport test rendered a distinct composition at HUD-root **50% X / 78% Y** and removed it cleanly. | It was a one-time sample, not automatic target/show/hide or cross-resolution production acceptance. |
| Augment *original* native TipHUD | Earlier `ui-child`, `aphes-text` and `composition` trials visibly added private label/divider/Aphes font to one real Open TipHUD, preserved the stock action/hint and removed only own children. | One original widget only; no established automatic N-owner lifecycle, hide/show and cross-map cleanup. But native TipHUD already owns its Screen visibility and the native action/icon, which is the strongest opportunity to avoid target synchronization entirely. |

Evidence: `research/interaction-prompts-owner/{can-show-state,
open-binding/beginplay-probe,open-binding/ROUTE_REVIEW.md,ui-child,
aphes-text,composition,viewport}/`, plus
`docs/VERIFIED_RUNTIME.md`, `research/.../multi-action/README.md`
and
`research/.../auto-world/README.md#runtime-result--2026-11-06`.
These are prior accepted observations, **not a new host run**.

## 3. Why current 3-frame sampling is not an adequate final architecture yet

The successor (`auto-world-successor/Scripts/IIPInteractionEvents.lua`)
performs a **full traversal** of the registered native owners every three
frames, at most 48 per scan. Each
`IIPInteractionSource.snapshot()` resolves **three** UObject paths
through `StaticFindObject`, checks class/path/address/parent ownership,
native `IsValid`, screen component state, and if shown, TipHUD
Visibility/RenderOpacity and localized `GetText` plus argument.
This is **not** one Lua `if`. At 60 real FPS and 34 owners,
there are nominally **20×34 = 680 owner snapshots per second**
(excluding native bookkeeping and separate World-frame updates).
This is an *operation-count estimate*, **not measured CPU time**,
frame-time impact, or proof of FPS loss. Multiplying rate tenfold
does not imply tenfold FPS loss.

Two complete native samples are currently required to bind; a *new*
owner additionally needs confirmation before releasing old resources
and two **fresh** complete samples afterwards. At three-frame
intervals that can consume much of a ~100 ms UX target before native
WorldComponent creation/render. At one-frame intervals with the
same full sweep, expensive owner checks would be repeated up to
60 times per second. Merely reducing the interval does not solve
the design problem.

## 4. Feasible event-first fast path (HYPOTHESIS, NOT READY)

1. **Initialize once** from the already verified natural BeginPlay
   source, keeping a primitive `actor_id→record` and
   `widget_id→actor_id` map. Update on EndPlay/map. Distinct
   duplicate widget-to-owner bindings are a conflict, **never**
   first-match selection. Handle not-ready initialization explicitly.
   No FindAllOf or scene-wide search in a hot path.
2. **Listen to the exact proven non-native `CanShow` post callback.**
   The callback supplies the widget context, not the source actor
   or true returned bool. Resolve its immutable identity and perform
   an **O(1) Lua map lookup**, without trying to create UI or
   changing any original native state. Unmatched or inconsistent
   widgets remain unknown. Its invocation may happen *before* or
   *without* a native show.
3. From the next verified game-thread boundary, read **at most that
   one indexed candidate** via the existing full reciprocal
   `source.snapshot` contract. Never call the native CanShow
   function. Keep only primitive identifiers across callbacks.
   Once a native owner is established, a **single-owner** fast
   visibility check each frame may detect hiding without revisiting
   all 34. It must be backed by actual runtime event coverage, not
   the assumption that every hide event has a corresponding
   CanShow call.
4. **Unique currently selected owner remains the hard gate.**
   An event for widget B and `B.shown=true` is **not proof that no
   other widget is shown**. An authoritative host current-target
   field, provable exclusivity invariant or independently verified
   event-source ordering is needed before the full registry audit
   can be removed from production. Until then an event is only a
   candidate and does not authorize a new World bind.
5. Keep periodic *complete* scans available **only for diagnostic
   cross-checking** while proving the event hypothesis. They must
   never be hidden inside a claimed O(1) production fast path.
   Measure callback counts, false positives, missed show/hide
   transitions and frame-count latency. Separately measure native
   frame-time/load; `os.clock` overhead and logs do not prove
   actual GPU/frame cost.
6. The WorldComponent `CLEANED→RELEASED→BOUND` protocol and
   fourth-host class residency failure are **independent** of
   target selection. Successful events would not automatically
   fix resource lifecycle or on-screen user experience.

**Not accepted:** using each `CanShow` callback as a new target,
calling a native visibility setter to manufacture the event,
hooking arbitrary global UMG SetVisibility/ProcessEvent, guessing
a player-controller target field by name, or dropping uniqueness
proof to improve benchmark results.

## 5a. Native Screen suppression must preserve event evidence

**User requirement clarified after this source study:** the final
composition must **replace** the visible stock prompt; a simultaneous
native Screen prompt and own World/fixed-HUD prompt is not acceptable.
This is a *display* requirement, not permission to disable native
`CanShow`, action selection, localized text/hint, input or the source
widget lifecycle.

The current World candidate's read-only
`IIPOpenVisibility.visible` depends on effective native properties:
`TipHUD.Visibility`, `TipHUD.RenderOpacity==1`, and the same
visibility/opacity checks for `TextBlock_89`, `RetainerBox_0`
and its own icon leaf. Changing these properties to suppress the
stock display would make our **existing selector itself return
false**, independently of whether `CanShow` keeps firing. This
conflict is established by current Lua source; the effect of native
hidden state on CanShow frequency and other host consumers is
**NOT TESTED**. Do not put `SetVisibility(Hidden)` or
`RenderOpacity=0` on the native widget/descendants into the
production path as an unverified convenience.

For **World**, research a presentational suppression seam that
does not change the observed native state and safely restores
the old appearance on failed creation, cleanup, EndPlay and
STOP. If only visibility-changing writes are available, first
prove an *independent* authoritative native selection/show signal
and exact consequences for game state. Hook registration alone
cannot prove visual suppression. The new read-only event probe
must keep native UI visible as an external truth source.

For **Screen S1**, instead of hiding the entire native TipHUD,
treat its native lower action/icon and own upper/divider children
as **one coherent replaced prompt**. Own visually redundant
stock panels/decoration must be retired or relaid out only after
separate safe ownership/readback testing, without moving or
disabling native selection/text/hint semantics. The previous
label/divider experiments were *additive prototypes*, not final
replacement acceptance. For **Screen S2**, a fixed overlay needs
both the accurate current-target signal and native Screen
presentation suppression, so its total complexity can exceed S1.

**New independent gate:** prove *one visible interaction prompt
only* in natural Open/Take/Check gameplay, with original
logic/events intact, and a full reversible failure/rollback path.
Neither the existing World runtime nor the source-only event
research has passed this gate.

## 5. Screen-space fallback is genuinely viable, with two variants

**Variant S1 — decorate the original Screen TipHUD.**
This is the shortest path to native-lifecycle coupling: draw an
author-owned upper glyph line and divider **as children of the
native TipHUD**, retaining its original localized action and
remapped key hint. Native Screen show/hide and object selection then
already control the parent widget. It avoids repeated World host
allocation, manual billboarding, native owner sweep and duplicate
display (the same parent contains both rows). Prior visual runtime
proves the *primitive* child/font/ornament operation for one Open.
It does **not** prove the N-owner lifecycle, fixed positioning or
global visual/performance acceptance. Because its position is
still projected from the world via the existing **Screen**
WidgetComponent, Hilda will not depth-occlude it; the user may want
a deliberate safer on-screen placement instead.

**Variant S2 — a dedicated fixed HUD-root Canvas.**
A separate Canvas at an agreed screen-space anchor makes it
obvious this is a HUD, not a faux-world marker. Prior 50%/78%
screen prototype rendered and cleaned. But it still needs an
authoritative cheap native current-target/show/hide signal,
otherwise its synchronization problem is equivalent to World.
Changing the existing Screen component's Space/position is not an
acceptable shortcut; the old rendering/layer/ownership study
already ruled out setter-only migration.

**Decision:** World remains preferred conditionally. S1 is the
cheapest native-lifecycle fallback if event/selection gating stays
unresolved; S2 remains useful for deliberately relocated HUD design
after a reliable target source is found. No fallback is implemented
or promoted to the accepted design by this study.

## 6. Next *sufficient* evidence; bounded proposed local experiment

Source static review cannot prove event→visible edge ordering,
completeness for **Open, Take and Check**, hide transitions,
simultaneous selection, or actual callback cost in the installed
game. No code has been installed or executed.

Prepare **one read-only event-correlation diagnostic**, not a full
World or Screen renderer, using only already verified callbacks,
host build and source identity:

- Normal user-launched load: record all three supported native
  owner families via BeginPlayPost and index exact
  widget→owner identity. If the exact CanShow UFunction is not
  loaded/verified before an expected interaction, report that
  explicit state and stop making coverage claims (no forced load
  or guessed fallback).
- Observe natural `TipHUD_C:CanShow` (one script post callback,
  `nil` return); capture primitive widget key and frame index.
  Determine whether and when a *subsequent* read-only
  native-visible/ready state follows for the **same** widget.
  For hiding, read **only the current candidate** once per frame.
  Use a slow full-owner snapshot as a separately labelled
  *diagnostic truth audit* at a bounded low frequency;
  refuse a unique-target claim from partial sweeps.
- User walks naturally through **Open → leave → Take → leave →
  Check → leave → return**. The observer records event count,
  matched/unmatched callbacks, event→native-visible frames,
  hide transitions, cases where the audit sees a visible native
  prompt **without a prior usable event**, and any two-visible
  ambiguity. A transient event between sparse audits remains
  `UNKNOWN`, not a false negative certainty.
- Report actual CPU/frame-time impact and perceptual response
  separately; avoid per-callback log flooding or fabricated
  microsecond/FPS claims. The probe must **not** modify native
  TipHUD, World UI, saves/settings, input or other mods.
  It must be disableable with proven closed-host rollback;
  no arbitrary gameplay timeout/total sample cap.
- **Positive gate:** each naturally tested action has a
  demonstrably timely, matched event and no false-positive bind
  or missed native-visible edge in the *observed* intervals.
  This establishes event coverage only for those intervals;
  it does not on its own prove global exclusivity or all levels.
  **Negative gate:** missing/late callbacks, ambiguous
  correspondence or prohibitive callback/read cost means this
  specific fast path is unsuitable; switch study to S1 before
  increasing global polling again.

The smallest next execution is preparing that standalone
**read-only** probe and offline failure-policy tests, then a
**separately authorized, user-started local Codex** runtime trial.
No unproved native target or UE4SS ABI is presumed. Current
`auto-world-successor` may remain a separate, uninstalled
resource-recovery/latency experiment; its 3-frame scan is not
an adopted final performance strategy.
