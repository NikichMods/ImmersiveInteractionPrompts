# План исследования — contextual prompts и письменность

## Проверка подавления изображения TipHUD

[Статический аудит](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md)
и игровой этап A установили, что корневой alpha скрывает и Screen, и
World-кнопку на проверенном Open. Сначала локализовать момент обновления
Retainer (B). Искомая граница должна позволить захватить актуальный значок
при исходном alpha и сохранить нулевой alpha для экранной композиции.
Если такой границы не удаётся подтвердить, проверить независимый источник
изображения из native-состояния кнопки (C). Выбор владельца продолжает
опираться на существующий readback.

## Selected-owner World — результат реального прогона и следующий гейт (2026-11-07)

[Отчёт `66912dd`](../research/interaction-prompts-owner/world-space/selected-owner-world/README.md#bounded-installed-game-result--2026-11-07):
34 новых World-композиции и 3 повторных показа без зарегистрированных
ошибок IIP, все обычные смены через NONE очищали предыдущий компонент.
Зафиксированные интервалы SELECTION→SHOWN — 57,51–67,96 мс при
создании и 34,21–35,14 мс при повторном показе. Это **не** latency
видимых пикселей, input-to-pixel или FPS/CPU замер. Прямой A→B,
контролируемое влияние на frame-time и пользовательская визуальная
приёмка остаются открытыми. Откат восстановил CompactLayoutProbe.

**Уточнение приоритета после оценки риска:** отсутствие
`CLEANED/RELEASED` у последнего скрытого World-компонента после
контроллерного EndPlay при **нормальном завершении процесса** не
считать самостоятельным блокером. EndPlay в штатном shutdown
не гарантирует ещё один игровой Tick: код только выставляет
`invalidate`, а освобождает World в следующем game-thread `step`.
Отсутствие этого кадра не доказывает утечку в продолжающейся игре;
операционная система освобождает ресурсы завершённого процесса.
Не вмешиваться в EndPlay callback native-destroy ради последней
строки лога: при teardown это может быть опаснее. Сохранить
неподтверждённость последнего cleanup как **низкоприоритетное
наблюдение**, без искусственного обязательного теста на выходе.

**Следующий приоритет — реальный UX и безопасность в продолжающейся
игре:** проверить визуальную отзывчивость, frame-time/микрофризы,
прямое переключение A→B и карту/контроллер во время продолжающейся
сессии при доступном естественном сценарии. 33 обычных межобъектных
освобождения уже подтверждены и повторять их в отдельном длинном
прогоне незачем. Исследовать lifecycle дополнительно только при
симптоме зависшего собственного компонента, живой утечке/дублировании,
ошибке перехода карты или новом evidence, а не ради очистки
последнего скрытого компонента в завершающемся процессе.

Независимый следующий инженерный gate — безопасно подавить только
дублирующую **отрисовку** stock TipHUD при сохранении штатного
owner/selection/локализации/input/show/hide. До отдельного теста
его не модифицировать. Screen S1 — лишь условный fallback, не
принятое изменение World UX.

## История: Selected-owner World — проверка интеграционного кандидата

После офлайн-проверки точного кандидата следующий отдельный шаг —
разрешённый игровой прогон Open/Take/Check со штатным TipHUD. Проверить
отклик, возврат к владельцу и порядок RELEASED→BOUND; прямой A→B только
если естественно доступен. [Протокол](../research/interaction-prompts-owner/world-space/selected-owner-world/README.md#next-sufficient-runtime-check).

## Selected-owner-driven World — следующий источниковый кандидат (2026-11-07)

**Цель:** быстрый контекстный двухстрочный World prompt над выбранным
игрой объектом без полного обхода 34–48 native owners, с native
локализацией, input hint, неизменным взаимодействием и без заметной
дополнительной нагрузки. Важнее реальная воспринимаемая задержка
(ориентир существенно меньше 100 мс), а не сокращение интервала между
двумя лог-записями.

**Новое положительное доказательство:** read-only `e240150` получил
local controller через `BeginPlayPost`, разрешил committed weak owner
`PlayerActionComponent+0x410`, и в игровом прогоне
[`4875f87`](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md#runtime-result--2026-11-07)
зафиксировал `NONE→Open→NONE→Take→NONE→Check→NONE`: все 6
переходов совпали с native TipHUD на первом последующем кадре.
Наличие прямого A→B, глобальная уникальность, фактический input→pixel
latency и CPU/frame-time не доказаны. После прогона установленный
`CompactLayoutProbe` восстановлен; текущий наблюдатель отключён.

**Переоценка решений:**
- Старый [AutoWorld](../research/interaction-prompts-owner/world-space/auto-world/README.md)
  делал полные native snapshots по 34 владельцам и требовал два
  последовательных подтверждения. Он показал Open/Check/Take и
  безопасные `CLEANED→RELEASED`, но пользователь отверг задержку
  0,531–1,568 с и четвёртый HOST-create дал `ABSENT_NULL`.
- [Successor с выборкой каждые 3 кадра](../research/interaction-prompts-owner/world-space/auto-world-successor/README.md)
  увеличивает частоту потенциально дорогостоящего обхода примерно
  в 10 раз; его runtime-стоимость неизвестна. Теперь этот подход
  **не предпочтителен как следующий эксперимент** и не должен быть
  установлен только ради проверки скорости.
- **Выбранный путь:** source-only owner-driven successor. Один
  authoritative committed actor per game-thread sample, проверка
  только выбранного и прежде привязанного native TipHUD; событие
  `BeginPlayPost` используется лишь для controller acquisition.
  Не добавлять глобальные `FindAllOf`, полные native surveys,
  `CanShow`-эвристику или обязательные два полных снимка реестра.
  При `GAP` не изображать `hide-to-NONE`.

**Граница архитектуры следующего source-only этапа:** использовать
подтверждённый read-only accessor + Source.acquire/snapshot вместе с
действующим World renderer и принятыми 17 стилевыми параметрами.
Отдельная game-thread сессия обрабатывает один текущий owner и одно
previous own lease. Для нового owner допускается bind только после
проверки `shown & ready` и после `hide→cleanup→empty proof→RELEASED`
прежнего own host; без перекрывающихся компонентов или сохранения
Lua UObject wrappers через кадры. Пока новый owner ждёт cleanup,
его нужно заново сверять с текущим committed owner, а не использовать
устаревший ticket. `NONE`, `GAP`, EndPlay, map-pre и ошибки
native identity требуют fail-closed hide/release/STOP по действующим
границам. Host-class `ABSENT_NULL` — реальный runtime блокер, не
доказательство GC; можно отдельно проверить уже подготовленное
одноразовое recovery exact class на чистой границе create,
не расширяя кэширование/GC/rooting.

**Доказательства и стоп-гейты:** сначала сделать отдельный research
source-only код и тесты (включая прямой A→B, быстрый transient NONE,
смену pawn/controller, stale actor, asset absence, map reset,
cleanup failure, no UI writes, одну owner read/кадр, no enumeration,
локализованный action/hint и отсутствие дублирующих own hosts). После
CI отдельно запросить установку при закрытой игре, rollback и
пользовательский прогон Open/Take/Check + повторный переход
Take→Check, сравнение первых показов/повторных показов по
time-to-World-visible и измерение реального frame-time влияния.
Записи `age_frames=1` **не** заменяют ни input-to-pixel, ни
производительность. Нативную Screen-подсказку в первом исследовании
не скрывать. Без доказанного независимого безопасного способа
подавления только её отрисовки production всё ещё BLOCKED.
При повторной неустранимой высокой цене/задержке World
снова сравнить с условным Screen S1, но не выбирать изменение
depth-occlusion без пользователя.

## Committed owner — событие контроллера вместо глобального поиска (2026-11-07)

Сохранить блокировку старого `fdee186`: `UEHelpers.GetPlayerController`
сканирует все объекты. Новый source-only кандидат получает local controller
из native `BeginPlayPost`, хранит только идентификатор и проверяет точный
`StaticFindObject` при чтении `PlayerActionComponent+0x410`.
Следующее действие — исходники/CI, затем **отдельное разрешение** на установку
нового SHA при закрытой игре. Если controller BeginPlay не наблюдается,
результат — `GAP` и остановка этого направления; не заменять поиск
глобальным `FindAllOf`.
[Причина и ограничения](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md).

## Selected owner — read-only корреляционный наблюдатель подготовлен (2026-11-07)

Следующее доказательство — офлайн-тесты и CI по отдельной исследовательской
ветке. После них **отдельно согласовать установку при закрытой игре**,
пользовательский естественный Open → Take → Check, выход из диапазона,
при возможности A→B, и откат. Собрать `TRANSITION/CORRELATED/NO_MATCH`,
не объявлять редкие статические кадры пиксельной или performance-приёмкой.
[Протокол и ограничения](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md).

## Selected owner — локальная статическая проверка завершена (2026-11-07)

При отдельном разрешении провести одну read-only корреляцию
committed `PlayerActionComponent+0x410` со штатной видимостью и
сменой компонента. При непрохождении переходить к проектированию native
Screen S1 с отдельным согласованием визуального компромисса.
[Доказательства](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#selected-owner-read-seam--local-native-trace-2026-11-07).

## History: ShowTipEvent — source-only observer (2026-11-07)

Подготовлен узкий read-only observer кандидата на штатный actor-event с
сопоставлением последующей native-видимости; не принимает INTENT за пиксели.
Сначала пройти офлайн-тесты/CI. После них **отдельно разрешить** установку
при закрытой игре и пользовательский естественный тест Open/Take/Check
с исходным TipHUD видимым. Точная доставка BlueprintImplementableEvent
через UE4SS 83330635 заранее не доказана.
[Протокол и стоп-условия](../research/interaction-prompts-owner/world-space/show-tip-event-observer/README.md).

## Native show/hide — статический поиск завершён, 2026-11-07

Найдена смена одного владельца в штатном update и точный actor-event.
Если нужен World-путь, отдельно проверить доставку `ShowTipEvent(bool)`
и соответствие последующей штатной видимости. [Доказательства и границы](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#native-tiphud-show-and-hide--2026-11-07).

## Current target authority — API inventory completed, 2026-11-07

Следующая отдельная проверка, если нужна World-цель, — найти штатного
native-вызывающего `ExtendedWidgetComponent:SetShow` и источник его
аргумента показа. Это различит единственного победителя и независимый
показ по объектам. [Карта деклараций и ограничения](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#genesis-reflected-api-inventory--2026-11-07).

## Current target authority — GetLastInteractObject closed, 2026-11-06

Native-трассировка закрыла getter как кандидат для выбора до нажатия.
Его слот заполняют ветки Begin/Fail и он переживает очистку Doing на End.
Поиск штатного победителя остаётся отдельным вопросом.
[Доказательства](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#native-getlastinteractobject--2026-11-06).

## History: Current target authority — local static audit, 2026-11-06

Финальный источник выбора не установлен. Если World требует такого
источника, ближайшая узкая проверка — проследить native
`GameGlobal:GetLastInteractObject` до хранилища и его писателя. Это отличит
выбор до нажатия от следа уже выполненного взаимодействия.
[Локальный статический отчёт](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#local-static-follow-up--2026-11-06).

## History: Current target authority — bounded source audit, 2026-11-06

Reviewed the current indexed CanShow observer, source owner/snapshot contracts,
the former full-visibility policy and source/runtime reports. **No established
authoritative engine-selected owner** was found in the *committed evidence*.
This is not a proof of absence from private cooked/native game code.
[Decision and smallest remaining static gap](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md).

Do **not** infer selected-target uniqueness from six correlated shows or
85 sparse full audits; do not raise 34-owner sweep frequency to compensate.
Next independently useful remote task: source-design review of **S1 inside
native TipHUD**, preserving original localized lower action/button and one
visual prompt, with World occlusion tradeoff still explicit. If World depth is
still required, hand off only the narrow **local static final-writer search**
described in the study; no runtime probe/install is approved by this review.
Production World and Screen S1 remain BLOCKED.


## Event correlation observer — игровой прогон завершён

Получен быстрый сигнал-кандидат для шести наблюдавшихся показов Open/Take/Check.
Следующий технический вопрос — можно ли независимо установить единственного
текущего владельца и измерить стоимость проверок на кадр. Редкий аудит этого
не доказывает. Протокол World-ресурсов и подавление штатного изображения
остаются отдельными гейтами. [Результат и ограничения](../research/interaction-prompts-owner/world-space/event-driven/PROBE.md#runtime-result--2026-11-06).

## История: Event correlation observer — подготовка исходников

Ветка `research/event-correlation-probe`, проверенный код и тесты
[`f03c571`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/f03c571f8fba9c88994a00f56daaa0ad54d95355):
[CI 42219818296](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42219818296)
**488 тестов / 44 файла PASS**. Новый наблюдатель сопоставляет событие
`CanShow` с реальным read-only `snapshot` только индексированного
кандидата, держит отдельный одновладельческий контроль скрытия и
отмечает неполные/неоднозначные редкие аудиты всех зарегистрированных
владельцев. Проверено на mock Lua и точке входа, **не в игре**.

Следующий этап уже **не** написание очередной World-перерисовки
и не ускорение 34-owner polling: только отдельно разрешённый
локальный read-only runtime probe с Open→нет→Take→нет→Check→нет→возврат,
логами событий и сравнением реального frame-time/читаемости;
исходный TipHUD должен оставаться видимым. Инструкции и границы:
[PROBE.md](../research/interaction-prompts-owner/world-space/event-driven/PROBE.md).
После него решать World fast path или native TipHUD Screen S1.
Подавление штатной подсказки — отдельный обязательный гейт.
До разрешения игровой установки никаких изменений активного
CompactLayoutProbe, `main`, VERSION, сохранений или настроек.

## Визуальная замена штатной подсказки — самостоятельный обязательный гейт

Пользователь уточнил: **не должно одновременно показываться две
подсказки**. Сохранять native `CanShow`, выбор объекта,
локализованное действие, контроллерную/клавиатурную кнопку,
show/hide и семантику взаимодействия. Скрытие исходного
`TipHUD` целиком через Hidden/RenderOpacity=0 противоречит
текущему `IIPOpenVisibility.visible` и не проверено в отношении
native CanShow. **Пока никакого подавления не выполнять.**
[Полное обоснование и ветки World / Screen S1 / S2](../research/interaction-prompts-owner/world-space/event-driven/README.md#5a-native-screen-suppression-must-preserve-event-evidence).

Ближайший read-only event probe **оставляет штатную подсказку
видимой** как наблюдаемый эталон и проверяет пригодность
`CanShow` для выбора цели. После установления этого
контракта — отдельный source+runtime gate безопасного
визуального подавления без разрушения сигнала, восстановления
после ошибки/STOP и проверки одного видимого промпта.
Для Screen S1 допускается единая переработанная native
`TipHUD`-композиция вместо отдельного дублирующего UI;
скрытие всего TipHUD для S1 не требуется. Если доказать
безопасную визуальную замену нельзя, production BLOCKED.

## Быстрая реакция на штатную подсказку — event proof, 2026-11-06

После пересмотра целевых UX/производительности **следующий
достаточный гейт — доказать native event→visible связь**, а
не запускать очередной вариант из 17 World Lua, который
опрашивает все 34 объекта каждые три кадра.
[Точный source-only аудит с приоритетом
доказательств](../research/interaction-prompts-owner/world-space/event-driven/README.md).

**Подтверждённое:** `TipHUD_C:CanShow` Blueprint post callback
срабатывает естественно в игре и выдаёт identity виджета;
один Open был сопоставлен с актором по BeginPlay/CanShow,
а глобальный BeginPlayPost получил Open6/Take18/Check10
при обычной загрузке. Возможен O(1) Lua индекс
widget→owner без полного native-sweep на каждом событии.
**НЕ подтверждено:** CanShow = selected-target/show/hide
или точное время, одновременная видимость только одного
TipHUD, полнота сигнала для Take и Check. Native SetShow
вернул 0 callback в прежнем тесте; не повторять его
идентично. Не использовать native SetupTipMessage2 arrays
без pinned UEPseudo ABI. Ошибка старого четвёртого World
host и ресурсное владение — отдельная проблема.

**Следующее самостоятельное source-only задание:** отдельный
малый read-only `CanShow`/BeginPlay identity-correlation
observer, а не World мод и не native UI patch. Использовать
только exact known script hook/normal global BeginPlay,
EndPlay/map, примитивные IDs, nil return. При callback
переносить в следующий подтверждённый game-thread pulse
кандидата; проверять *один* TipHUD/его native action/
screen-membership/readiness. Показ/скрытие реальной штатной
подсказки сопоставлять по кадрам, не угадывать native bool.
Отдельная редкая полноценная диагностика всех owner
показывает ложные кандидаты/пропущенные переходы —
**не часть предполагаемого дешёвого финального пути**;
если >48/неполный снимок, статус UNKNOWN.
Вывести компактные события и счётчики, без user-visible
World UI и без автоматического game launch/hot reload.
Test cases: Open→нет→Take→нет→Check→нет→возврат,
map/EndPlay, unmatched callbacks, duplicate widget ID,
сбой/отсутствие CanShow, полная vs неполная аудит-выборка,
сохранение native control/UI. Off-line tests проверяют
policy, не latency/performance.

**Итоговая развилка:** только если реальный event покрывает
эти естественные переходы и нет неоднозначности,
реализовать fast-path World selection c native собственным
single-component cleanup и измерить cost. Если событие
редкое/позднее/ненадёжное или нельзя установить
global selected-owner без тяжёлого аудита, перейти к
**Screen fallback S1 (собственные дети штатного TipHUD)**
как более простой native-owned show/hide путь.
Отдельный фиксированный HUD Canvas S2 потребует своего
доказанного выбора цели; позиция 50%/78% — только
предыдущий испытанный baseline, не новое принятие.
**Новый игровой тест только по отдельному разрешению через
user-started local Codex**. До него изменять активный
CompactLayoutProbe, saves/settings и другие моды нельзя.

## История: AutoWorld successor: исходники готовы, следующий гейт игровой — 2026-11-06

После отказа AutoWorld `be1827d` сравнили (a) повторное создание
actor-owned World-компонента с точной повторной загрузкой пропавшего
HOST и (b) постоянный World-компонент, переносимый между акторами.
Для (b) пока нет доказанного безопасного native owner/attach/EndPlay
контракта; выбран более узкий (a), уже дважды успешный в игре.
[Trade study, отказ от непроверенных API и
границы](../research/interaction-prompts-owner/world-space/auto-world-successor/README.md).

На новой ветке `research/auto-world-residency-latency` сохранён
старый `auto-world/` без модификаций, создан отдельный 17-Lua
преемник `auto-world-successor/`. Только две функциональные
поправки: (1) **одна точная попытка восстановить исчезнувший
generated host class** на очередном чистом game-thread
create с full identity/superclass proof; любая неудача STOP;
(2) **3 кадра между полными native owner-проверками вместо 30**,
не более 48 регистраций за callback, прежние две устойчивые
полные выборки и подтверждённый release перед bind.
Не вводились GC root, альтернативный World owner,
принудительный GC, native Screen writes или таймеры сеанса.

[CI 42209313867](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42209313867)
на `d48ca6032ab75dec29eec16be4c7a6a741930ac2`:
**473 офлайн-теста/42 файла PASS**, включая `ABSENT_NULL`
генерируемого класса при следующем create, точный reload,
failed-load/foreign-class, быстрые наблюдения, EndPlay/map,
handoff/cleanup-фолты. Все 17 исходников заморожены по
SHA-256-манифесту. **Ни один из этих тестов не показывает
реальную живучесть класса, производительность или визуальную
скорость в UE4.**

**Следующий достаточный эксперимент** — один обычный прогон
после отдельного разрешения на установку через локальный
Codex: verified closed-host install, hash/rollback, user-started
игра, Open→нет→Check→нет→Take→нет→Check (четвёртый
create), ещё 1–2 natural перехода при возможности и возврат
к тому же owner. Зафиксировать: (a) появление и порядок
`HOST_RECOVERY_ATTEMPT/RESULT/RECOVERED` при реальной
недоступности класса; при непропаже класса результат
`recovery NOT_TESTED`, а не PASS; (b) `CLEANED` перед
`BOUND` и отсутствие двух активных own компонентов;
(c) задержку от первой sampled native visibility и
пользовательское ощущение быстроты, без выдуманного
числового порога; (d) влияние более частых проверок
на плавность/нагрузку в той же игровой сессии;
(e) сохранение штатной localized action и input hint.
После штатного выхода точный rollback, приватные логи
вне Git, компактный отчёт, commit/push и обновление
канонической документации. Игру не запускать и не
закрывать силами Codex. Не модифицировать другие моды
или host settings/saves.

При повторном HOST/GC сбое, недопустимой нагрузке
или неудовлетворительном отклике **снова открыть
архитектурный выбор** на реальном доказательстве,
не расширять автоматически список fallback-операций.
Production gate остаётся BLOCKED.

## История: Автоматическая World-сессия — первый игровой прогон 2026-11-06

Три действия показаны, две передачи владельца завершились новой композицией
после очистки прежней. На четвёртом создании пропал результат поиска класса
World-хоста, и кандидат штатно отключился. Пользователь отдельно отклонил
задержку появления для финальной версии. Для дальнейшего решения это два
отдельных вопроса: доступность класса при повторных передачах и вклад
выборки/подтверждения владельца в задержку. Причина исчезновения класса
не доказана. Исследовательский кандидат отключён, CompactLayoutProbe
восстановлен. [Игровые доказательства](../research/interaction-prompts-owner/world-space/auto-world/README.md#runtime-result--2026-11-06).

## История: автоматическая World-сессия, исходники и CI — 2026-11-06

Новая ветка `research/automatic-world-session` завершила
source-only объединение наблюдателя `Open/Take/Check`,
контроллера handoff, свежего native owner resolver и
повторно используемого World renderer.
[Точный кандидат и границы](../research/interaction-prompts-owner/world-space/auto-world/README.md).
[CI 42133071798](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42133071798)
прошёл **446 офлайн-тестов/38 наборов** на `5af99f7`.
Ровно 17 Lua-файлов проверены по SHA-256-манифесту.
Никакие тесты не подтверждают пока runtime-передачу World-компонента.

**Следующий достаточный шаг — один пользовательский игровой прогон**
после отдельного разрешения на установку, а не ещё одно
неограниченное исследование внутренних событий.
Локальный Codex проверяет установленную сборку, сохранённую
снаружи loader откатную копию, независимость от остальных модов,
точное совпадение 17 исходников и приватного конфига.
Сама игра запускается пользователем; обычная загрузка,
подход `Open`, отход, `Take`, отход, `Check`,
проверка штатного Screen UI и вновь создаваемого World UI,
стабильности и очистки собственной композиции. Запрещены
hot reload, изменение сохранений/настроек и придумывание
таймера завершения теста.

**Приёмка только по доказательствам:** должны быть реальные
`CLEANED` старого компонента, проверенное отсутствие
одновременных собственных компонентов, свежий `BOUND` нового
владельца, сохранение native локализованного текста и кнопки,
отсутствие сбоев ресурсов, читабельная визуальная композиция
и точный rollback. Прямой A→B без промежуточного отсутствия
подсказки, GC/native lifetime, перевод декоративных глифов
и решение о дублировании оригинального Screen prompt
нельзя помечать PASS без отдельного подтверждения.
Продакшен-приёмка остаётся заблокирована.

## История: после World reuse CI PASS — интеграционный source gate

В `research/world-renderer-reuse` реализована отдельная
повторно используемая World-композиция и адаптер владения:
сохранены 17 актуальных визуальных параметров, оригинальные
локализованные подписи и input hints. Новый World-host
не создаётся до подтверждённой очистки предыдущего;
обычный hide/resume одного owner не создаёт ресурс заново.
Пройден [CI42130699221](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42130699221):
430 офлайн-тестов/35 наборов PASS на `4963296`.
Протоколы ресурсов проверены на UE4SS-моделях, реальная GC
и второй World-host в игре остаются UNKNOWN.
[Реализация и границы](../research/interaction-prompts-owner/world-space/world-reuse/README.md).

**Следующий достаточный шаг — source-only auto entrypoint**,
связывающий текущие проверенные read-only Open/Take/Check source
и event observer, primitive `IIPWorldHandoffBridge`,
`IIPWorldHandoff` и `IIPWorldRenderer`.
Передавать в native renderer только свежие проверенные UObject,
не хранить их после цикла; подключать собственный World UI
только по двум последовательным *полным* уникальным штатным
снимкам. Выполнять native World operations исключительно на
проверенной игровой границе; никакие события BeginPlay/EndPlay
не вызывают создания/удаления UI напрямую.
После `cleanup` требовать отдельный readback `empty=true`
до `RELEASED(ticket)`. При partial creation/failure
сохранять блокировку второго bind. Не заменять оригинальный
Screen prompt и не изменять штатное управление.

Добавить офлайн end-to-end тесты нормальной смены
Open→нет→Take→нет→Check, same-owner hide/resume,
многих native owners, map/EndPlay и ошибок partial create/
cleanup, отсутствие двойного WorldComponent, отсутствие
навязанных таймеров/лимитов событий. Сохранить разделение
незавершённых runtime гейтов и source-only доказательств.

**Никакой автоматической установки:** после зелёного CI и
проверенной идентичности исходников потребуется отдельное
разрешение и локальный Codex для host-closed install,
reversible rollback, реального A→none→B теста и визуальной
приёмки. Прямой A→B, карта с уже наполненным реестром и
авторитетный выбранный движком объект остаются NOT_TESTED
или UNKNOWN по последнему runtime отчёту.

## История: World handoff controller complete — source-only renderer step

`research/world-owner-handoff` implements a pure single-owner lifecycle
controller and a primitive event-observer bridge. Its checked sequence is
hide/retain on same-owner focus loss, and, for different owners,
hide → native cleanup → independently confirmed empty → RELEASED(ticket)
→ two fresh complete unique snapshots → bind. Incomplete, ambiguous,
faulted or stale snapshots never authorize a new World owner.

[CI 42126709589](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42126709589)
on `bff0d3cb5e023e8c97b7d577404f5e380f64b923` passed
422 offline tests across 33 scripts. This is mock evidence only;
no new game activity or installation was performed.

**Remaining source blocker:** the frozen compact World renderer is
one-shot. Its module-global `import_attempted` refuses a second
ornament import; native names use second-resolution timestamps and
automatic `create()` opens the editor. Native resource lifetime and
repeated World allocation are not established. Do not bypass these
guards, fabricate a CLEANED acknowledgement, or modify frozen source.

**Next sufficiently bounded work:** a separate research-only,
reentrant World renderer adapter satisfying the controller's
`empty/create/hide/resume/refresh/cleanup` contract. Derive from
the verified compact host/resource methods, preserve the accepted
17 layout defaults, native localized action and button hint,
and prove sequential own allocation, release and error containment
offline before requesting a host trial. The current source-only
coordinator is not an installable World candidate.
[Details](../research/interaction-prompts-owner/world-space/owner-handoff/README.md).

## История: следующий source-only World lifecycle gate, 2026-11-06

**Автоматическое приобретение Open/Take/Check и корректное удаление owner через
EndPlay подтверждены в игре.** [Точный отчёт и ограничения](../research/interaction-prompts-owner/world-space/multi-action/README.md#runtime-result--2026-11-06):
`1780f0a` увидел 34 готовые связки (Open6/Take18/Check10), пять
эпизодов одного видимого/готового владельца из 33 с переходом
`Open#10 → Check#3 → Take#19 → Check#3 → Open#10` **через уход из зоны**;
34 EndPlay-удаления к штатному выходу. Реальные строки этих трёх действий
проверены. Последний сообщённый `Open` не имеет отдельной записи:
причина UNKNOWN. Прямой A→B без состояния «никого» и map-reset
уже наполненного реестра NOT_TESTED. Установленный MultiActionProbe
отключён, CompactLayoutProbe восстановлен; это не новый runtime
acceptance World-рендерера.

**Следующий достаточный самостоятельный шаг ChatGPT:**
на новой research-ветке изучить фактический `IIPWorldChild.lua`,
`IIPComposition.lua`, `IIPHintSource.lua`, native resource cleanup,
`IIPTargetPolicy.lua` и принятую композицию. Подготовить отдельную
source-only адаптацию для многократного own-component жизненного цикла:
сохранять ресурсы только при hide/resume **того же владельца**;
при уходе к другому владельцу сначала скрывать и освобождать
собственный World UI; выдавать `released(ticket)` **только после
подтверждённого `CLEANED`**, а затем требовать новую полную свежую
visibility-снимок и устойчивую однозначную цель перед `bind`.
Ошибки частичного создания/освобождения не должны разрешать вторую
аллоцированную композицию. Сохранять native localized action/input hint,
original TipHUD, существующий собственный визуальный дизайн и принятые
layout-настройки; не переключать native действия/ввод/сохранения.

Не внедрять произвольные таймеры и total-event caps (уже принято
в `docs/REQUIREMENTS.md`); ограничивать только стоимость проверок
и количество подробных сообщений. Старый компактный research-кандидат,
его installed bytes, `main`/`VERSION` и другие моды неприкосновенны.
Начать с офлайн-тестов A→none→B, B→none→A, hide/resume, EndPlay/map,
недействительных UObject и cleanup-failure; не представлять это как
host acceptance. Экспериментальный прямой A→B и совпадение native
chosen-owner остаются отдельным игровым гейтом, если алгоритм
предполагает такой переход. Не требовать двух соседних сундуков:
подтверждённые семейства действий уже доступны естественно.

**Граница решения:** доказанные 33-owner complete snapshots покрывают
только тот конкретный уровень/сеанс; `incomplete_snapshot` или
несколько одновременно видимых native подсказок должны оставлять
`UNKNOWN`, а не запускать создание World-компонента. Популяризацию
нового билдa или установку до явного разрешения не проводить.
Вопрос об экранном дублировании оригинального TipHUD/его suppression
отдельно решать по согласованному UX, не делать скрытые native writes.
Верхние глифы не считать переводом Aphes.

## История: после multi-action source — native handoff gate, 2026-11-05

**Source-only slice delivered by ChatGPT.**
[Read-only Open/Take/Check candidate](../research/interaction-prompts-owner/world-space/multi-action/README.md)
on `research/multi-action-observer` with
[CI 42069984702](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42069984702)
at `1780f0a8230149135b61bafcdb81c61e2f1d4e36`:
403 tests/31 scripts PASS. No game/user acceptance or installed change.

**New evidence boundary:** normal-load `Open` actor→TipHUD acquisition
already passed for six objects; `Take` and `Check` currently share
the *static* BaseGameEventObject_BP owner path only.
For next native observation use **naturally available different
actions** (Open → Check → Take → no prompt) and compare the displayed
native prompt against actor ID/action/text and the **complete** visible
owner set, without requesting two nearby Open chests or using game
progression as setup. If more than48 relevant owners are registered,
the source explicitly reports incomplete snapshots; do not claim
uniqueness or increase sampling by guessed global scans.

The next user-started local Codex task, **only after separate permission**,
is to verify installed environment, close host/rollback and install a
new independently frozen hash-verified read-only payload, then collect
one ordinary user-paced gameplay run and concise evidence. Codex does
not redesign the action observer or write World/UI code. No manual
reload/arm, hot reload, forced object spawn or save/config mutation.
Restore the previous installed source after evidence capture.

**When the live different-owner selection seam is accepted**, ChatGPT
next evaluates repeatable own World-component cleanup/creation and
the one-at-a-time `release`→`CLEANED`→`bind` protocol. Previous compact
renderer only passed same-owner hide/resume and explicit teardown,
not A→B rebind. Preserve native action/hint/localization, interaction
behavior, original Screen prompt until separate UX decision, and
no unverified Aphes translations. Bonfire and Ladder remain unsupported.
Do not return to speculative timed probes.

## История: после локального Open-only прогона, 2026-11-05

Обычная загрузка дала шесть готовых Open-владельцев через BeginPlayPost.
Два зарегистрированных эпизода видимости относятся к одному владельцу.
Для проверки A→B нужны два независимо различимых объекта «Открыть» и две
разные привязки owner ID, сопоставленные с увиденными подсказками.
Для проверки удаления записи нужен EndPlay или LoadMapPre после регистрации
владельцев. Эта работа ограничилась одним сеансом и завершённым откатом.
[Результат и идентичность](../research/interaction-prompts-owner/world-space/auto-target/README.md#normal-load-runtime-result--2026-11-05).

## Следующий gate после automatic Open event observer, 2026-11-05

**ChatGPT completed current source-only slice.** [Auto-event code and
limits](../research/interaction-prompts-owner/world-space/auto-target/README.md#automatic-ue4ss-lifecycle-observer--source-only-2026-11-05),
[run42003357042](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42003357042)
(`eb251161d067482fca362f0a418eb736a449f491`, 385/29 offline PASS).
Separate `research/auto-open-events` branch is **not installed**; frozen
World candidate, stable branch and game unchanged.

**Nearest decisive unknown is now native:** Does the global BeginPlayPost
callback fire *after or before* the verified Open actor's `TipHUD` is ready?
Can bounded pending→joined observation recover it? When gameplay moves across
two known Open prompts A→B→none, does the complete set of native visibly
shown owner components uniquely identify the actually chosen object, or
are multiple components concurrently shown? Does EndPlayPre/map pre
invalidate the corresponding identities safely? The event-seam reader
proves none of this by mock tests.

**Only sufficient next trial:** after separate permission, user-started local
Codex prepares hash-guarded **one distinct read-only probe** with the five
source files; verify host closed, existing installed IIP/other mods unchanged,
explicit rollback and no dual active IIP owners. The user launches game,
loads normally, approaches A, B and neither, optionally normal map travel,
then exits normally; Codex only collects and commits compact conclusions
and evidence hashes. On any contract fault, ambiguous owner, over-budget,
or missing callback, STOP and do not add alternate scans/native writers.
No auto installation, game process/saves/settings manipulation, hot reload,
or release authorization inferred from this document.

**If supported A→B→none selection is shown:** ChatGPT next develops
a *new* own-only, repeatable World lifecycle successor with strict
release-cleaned-before-bind (not a simulated ack) and exact action/widget
resources, then separate in-game visual acceptance. If not, revisit only
the missing authoritative active-owner seam. Vanilla Screen fallback and
upper Aphes semantics remain explicit unapproved production questions.
Glow/overall scale stay deferred.

## После offline Open-target policy — next runtime boundary (2026-11-05)

[Новый исходный policy/owner bridge](../research/interaction-prompts-owner/world-space/auto-target/README.md)
подготовлен силами ChatGPT в ветке `research/auto-open-target-policy`.
[CI run41937982403](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/41937982403)
на исходном code+test `97283bb6`:370/27 offline PASS. Это
**не** новый runtime mod/candidate; его модули пока не подсоединены к
старому однократному `main.lua`. Замороженный source2981375 и установленный
CompactLayoutProbe не трогать.

1. **Следующий достаточный source-only этап (ChatGPT):** выбрать минимальный
   жизненный цикл регистрации глобальных BeginPlayPost/EndPlayPre и получения
   готового `TipHUD`, опираясь на pinned UE4SS83330635 и принятый Open join.
   Определить безопасный источник **полного** наблюдения актуальных
   зарегистрированных Open-candidates, не делая FindAllOf/world scans,
   последнего-CanShow selector или дорогого per-frame обхода. Проверить
   ресурсную/переиспользуемую жизненную модель current WorldChild перед
   созданием второго компонента; fail-closed и acknowledgement после native
   `CLEANED` уже смоделированы в policy.
2. **Доказательство, которое может потребовать локальной среды:** когда рядом
   объекты A/B, является ли native effective `source.bVisible && bAddedToScreen`
   + показанный `TipHUD` однозначным сигналом *выбранного* объекта?
   При A→B→none — сколько виджетов действительно одновременно видны,
   каков их owner identity и готовы ли они к global BeginPlayPost? Простое
   `CanShow` не возвращает в Lua исходный bool. Если source-only не отвечает,
   один narrow read-only user-started Codex test, а не передача разработки.
3. После положительного gate подключать policy к **новому** research-source
   successor (не менять frozen старый): простая one-owner World-композиция,
   строго один pending transition за раз; для retarget сначала native teardown
   с подтверждением, затем bind; оригинальный TipHUD остаётся видимым,
   недоказанные классы не поддерживать. Измерять нормальный startup, целевой
   handover, target loss, map change, input hint/device и собственные ресурсы
   на пользовательском run только после отдельной авторизации установки.
4. Финальная production-приёмка: решённый пользовательский UX
   native Screen/World fallback; настоящий Aphes semantic mapping либо
   явно нейтральная верхняя строка; поддержка Take/Check только после
   положительной owner+text/hint связки; отдельный лестничный путь;
   lawful private game font dependency + installable packaging + CI/UX gates.

Не возобновлять gamma/glow/scale, не менять game controls, локализацию,
старые версии, `main` или другие моды в рамках этого этапа.

## Автоматическое обнаружение и переключение цели — source-only review, 2026-11-05

**SOURCE_ROUTE_REVIEW_COMPLETE / NO_NEW_RUNTIME_ACCEPTANCE.** Перепроверены текущие
`compact-layout/Scripts/main.lua`, `IIPWorldChild.lua`, `IIPHintSource.lua`,
[Open join](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md),
[route comparison](../research/interaction-prompts-owner/open-binding/ROUTE_REVIEW.md),
[CanShow runtime](../research/interaction-prompts-owner/can-show-state/README.md)
и [канонические host findings](VERIFIED_RUNTIME.md#1-подтверждённый-ui-owner-и-цепочка).
Сохранённый успешный Run source2981375 не расширяется до новых объектов.

**Два разных owner-условия:**

1. `BaseGameEventObject_BP_C:ReceiveBeginPlay` (script post) уже доказал
   приобретение одного Open actor→ExtendedWidget→TipHUD после ручной загрузки
   и совпадение по identity при `TipHUD_C:CanShow`. Это связь объектов,
   **не доказательство**, что каждый callback `CanShow` означает фактически
   выбранную игроком цель: return bool не передан Lua script post;948
   callbacks для3 live widgets в прежнем опыте не означают948 показов.
   `widget.Outer` принадлежит GameInstance, а не интерактивному актору.
2. У текущего research source есть жёсткий `msgTag=Open / ActionName=25`,
   `phase=bound` фиксирует одну цель, отбрасывает остальных кандидатов,
   `automatic_retarget=false`. Per-frame World проверяет только native
   visibility/source ownership текущей цели. При смене цели нет протокола
   восстановления списка и transfer; не следует просто выбирать последний
   `CanShow` или ближайший актор.

**Новый проверенный исходниками UE4SS путь для автоматического lifecycle:**

- В точном [UE4SS LuaMod.cpp @83330635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L2565)
  `RegisterBeginPlayPostHook` регистрирует callback без поиска загруженной
  игровой UFunction; dispatcher [6602–6617](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L6602)
  передаёт `AActor*` в callback.
  `RegisterEndPlayPreHook` [2593–2612](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L2593)
  и [6619–6635](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L6619)
  передаёт актор + причину; это source-level кандидат для cleanup/level loss.
- `RegisterHook` по-прежнему требует уже resident `TipHUD_C:CanShow`
  UFunction [4242–4248](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L4242).
  Дополнительно [NotifyOnNewObject, 2304–2366](https://github.com/UE4SS-RE/RE-UE4SS/blob/83330635/UE4SS/src/Mod/LuaMod.cpp#L2304)
  умеет регистрировать callback по имени класса без `UFunction`; допустим
  только как *кандидат* на bounded естественный trigger резидентности, с
  проверкой exact class/порядка и однократной регистрации. Не force-load,
  не вызывать игровые методы для создания события.
- Наличие данных API в версии UE4SS и C++ callback-контракт **не доказывают**
  что game-specific обработка `TipHUD` полностью завершена в момент
  глобального `BeginPlayPost`, что он достигает всех relevant actor-классов
  или что нужные объекты уже не созданы до загрузки мода. Это отдельный
  readiness-гейт. Не считать `EndPlay` подтверждённым в данном host без run.

**Минимальный дизайн-кандидат к следующей source-only реализации ChatGPT:**
при старте мода bounded global BeginPlay/EndPlay callbacks с дешёвым exact
type/ancestor guard; сохранение *только* проверенных primitive owner identities
(actor/component/widget), без FindAllOf/мирового сканирования или per-frame
actor enumeration. Инициализацию после callback выполнять в безопасной фазе
при фактической готовности widget (без повторного BeginPlay/InitWidget).
Проверенный `CanShow` оставлять информационным событием и сверять
native component+widget visibility, effective input mode и соответствие
identity; если кандидатов0 или несколько неоднозначных — не создавать новую
World подсказку, штатный Screen остаётся. Для единственного подтверждённого
текущего target предусмотреть state machine hide→release/switch→show и
cancellation при EndPlay/смене уровня. Любой native Screen hide/замена и
подмена Top `OPEN` для других действий запрещены до отдельных UX/semantic
решений. Начальный scope — доказанный Open; Take/Check имеют static
общий owner-путь, но ещё не runtime proof; Ladder/Descend не подтверждены.

**Что может решить следующий один игровой прогон, если source-only гейты
пройдены:** приход глобального BeginPlay/EndPlay на нужном owner; ready-тайминг
`TipHUD`; *однозначность* native visible/selected при двух рядом стоящих
объектах, переход focus A→B→none и возврат, без мнимых показов на каждый
`CanShow`. Если не существует наблюдаемого признака выбранной цели — STOP
и новый ограниченный owner/event вопрос, а не автоматический global scan.
Следующий исполнитель исходников и offline tests — ChatGPT; local Codex только
для отдельно разрешённого installed-host разрыва. Никакого нового кандидата,
установки, runtime-теста, `main`/`VERSION` или игры в этом source-only шаге.

## Production transition — next bounded slice, 2026-11-05

[Production source/evidence audit](STATUS.md#production-readiness--sourceevidence-audit-2026-11-05)
completed remotely on compact-layout branch, without Codex, host changes or new
runtime claims. The accepted visual research baseline remains frozen. **Do not
continue appearance tuning, glow/gamma work or optional scale.** This is an
integration/lifecycle problem, not a rendering blocker.

**Next ChatGPT-owned source-only slice:** determine the smallest
production-compatible acquisition/selection mechanism that starts in normal
gameplay without Ctrl+Alt+F11 + manual reload, follows the *currently active*
context prompt, and can release or switch own World UI between eligible actors
without modifying native interaction semantics. Before implementation, compare
the established BeginPlay actor/component/widget join, CanShow post, native
visibility and any other already documented owner/event seams in this repo and
[Asterigos-Research](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/RESEARCH_INDEX.md).
Identify who chooses the currently displayed target, when it is valid and how
loss/replacement/map travel are distinguished. A callback name existing is not
proof it identifies the active target; no fuzzy actor scans or per-frame UObject
enumeration by default. First choose a bounded supported interaction family;
generalize only to independently evidenced adjacent families.

**Decision/acceptance boundary before new behavior:** specify whether the
production presentation is World-only with vanilla Screen fallback or another
explicitly accepted approach; current research deliberately shows both. Do not
hide the native TipHUD as an incidental implementation detail. The upper
technical `OPEN` glyph must also be addressed before multi-action claims;
lower text continues to come from the actual localized native label, and an
invented top glyph must never be called a verified translation.

**First exit gate:** evidence-backed owner/state design with explicit source
locations, observed versus unknown transitions and a minimal safe implementation
slice. If existing source evidence suffices, implement the own-code portion in a
new research/development branch with targeted offline tests and frozen candidate
identity. If a particular native transition cannot be established without the
installed host, prepare **one narrow user-started local Codex read-only task**
for only that gap; do not hand off the whole coding/audit job. No installation,
automatic run, hot reload, save/settings changes, main merge or VERSION release
until relevant user authorization and game acceptance.

**After the mechanism is proven:** extend supported action types and candidate
selection only as evidence warrants; test target switching, level/load lifecycle,
native input/remap and locale, viewport readability and fallback. In parallel,
plan original-code distribution around the non-redistributable game font and
private absolute paths; ship no proprietary host asset. Decide explicit
support envelope and user visual/behavioral acceptance before promotion.
Optional generalized compatibility/extra settings and renewed color diagnosis
remain deferred. Do not manufacture a release candidate before the actual
integration source is READY.

## Compact-прогон завершён; текущая база обновлена — 2026-11-05

[Сближение/hide-resume/manual STOP PASS](../research/interaction-prompts-owner/world-space/compact-layout/README.md#user-run--compact-spacing-hide-resume-and-manual-stop-pass-2026-11-05).
Повторный run ради этих же гейтов не нужен. Последние17 NumPad9 значений
[приняты как текущая база следующего кандидата](REQUIREMENTS.md#актуальная-база-после-compact-layout-прогона--2026-11-05).
Сейчас только разобрать и сохранить результат: без нового кода/установки;
source2981375 и installed payload/config/marker остаются прежними. Нет отдельного
разрешения на production-продвижение; масштаб и color-work не возобновляются.

## История подготовки compact-layout

## Подготовлен compact-layout — 2026-11-05

Source2981375 уже установлен по поправке пользователя;
[identity/rollback](../research/interaction-prompts-owner/world-space/compact-layout/README.md#authorized-installation--2026-11-05).
На момент установки следующим шагом был один пользовательский run; его узкий
технический результат теперь записан выше.

[READY_SOURCE и сценарий](../research/interaction-prompts-owner/world-space/compact-layout/README.md):
alpha-envelope + полные native text metrics, gap0, прежний отказ на−3 снят,
реальные пересечения/bounds и rollback сохранены. Full345/25 PASS. Установка
выполнена; далее один run для сближения/
hide-show/Num9/NumMultiply. Масштаб не задерживает этап и отложен; цветовая
ветка закрыта по принятому визуальному решению, не повторять снимок/A-B.

## Следующий этап — компактная вертикальная композиция (решение 2026-11-05)

[Принятое требование](REQUIREMENTS.md#визуальная-допустимость-свечения-и-приоритет-компактности--решение-2026-11-05):
текущий слабый glow/fade World UI визуально допустим; причины не установлены,
дальнейшее color/gamma/material/post-process исследование отложено. Не включать
переключатели HDR/sRGB/TargetGamma/Masked в новый кандидат и не повторять
закрытый metadata snapshot и material A/B.

**Один новый source-only successor** к фактически принятому и завершившему
runtime-сессию `51b9f265c8b6d6b79ff48513a51a84087eeee6be`:
применить принятые17 значения NumPad9 как начальные, аккуратно сократить
вертикальные отступы между верхом/орнаментом/низом. В существующем
`IIPTuning.plan` отклонение `divider_y=-3` при `gap=2` связано с guard,
сравнивающим **полный слот** divider с нижней границей верхнего текста.
У авторского PNG256×32 альфа-огибающая из офлайн-проверки:
nonzero bbox `(3,8)-(253,24)`; уверенная область (`alpha>127`)
`(4,11)-(252,21)`; полные прозрачные верхние/нижние поля не должны
считаться видимыми штрихами. Использовать подтверждённую и достаточно
консервативную видимую область при проверках и расположении строк, отдельно
учесть фактические текстовые измерения/обводки, в том числе для экстремальных
значений live-редактора. Не обходить защиту пересечений; обратимый reject/
rollback остаётся обязательным. Общий масштаб — только если простой локальный
проверенный механизм, иначе отложить без блокировки основной задачи.

Сначала действующий worktree/remote/доказательства/gates, затем source-only
реализация и scoped offline-тесты с фиксированной идентичностью. Не менять
старый source/manifest, установленный payload/marker, native TipHUD, игру,
настройки, сторонние моды, `main`/`VERSION`. Установка и игровые действия
только после отдельного разрешения/закрытого хоста/rollback. Критерий выхода
первого этапа — готовый к отдельной установке исследовательский кандидат,
не runtime/visual/production acceptance.

## Завершённый шаг — один преемник с PNG и диагностикой, 2026-11-05

Пользовательский сеанс завершён: [snapshot/manual STOP PASS](../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md#user-run--snapshot-and-manual-stop-pass-2026-11-05).
Повторять его ради снимка/cleanup не нужно. [Последние17 значений и будущие
пожелания](REQUIREMENTS.md#новая-база-настроек-и-будущая-компактность--2026-11-05)
сохранены: более тесная вертикальная компоновка, опционально общий масштаб при
простом надёжном механизме. Текущее задание ограничено разбором лога/фиксацией;
никакой новой реализации или установки сейчас. Новый этап — по будущему заданию.

### История подготовки и установки этого кандидата

Кандидат source51b9f26 уже отдельно разрешённо установлен и хэш-проверен;
[identity/ограничения](../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md#authorized-installation--2026-11-05).
На момент установки следующий шаг был один пользовательский сеанс; его результат
теперь зафиксирован выше.

По новому заданию подготовлен [authored divider + color snapshot](../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md):
Исходная source-only подготовка завершена, установка выполнена. Далее один
сеанс для разделителя/толщины/небольшого движения/hide-show/
NumPad9/явного NumMultiply и однократного RT/MID-снимка. Не повторять архивный
аудит, Masked/Translucent A/B и не исправлять цвет наугад. Дизайн PNG принят;
World-рендер, runtime readback и новый cleanup ещё не проверены.

## История: этап завершён, работа остановлена 2026-11-04

2026-11-04: пользователь принял source da83080 как успешный исследовательский
World-space прототип с live-редактором. [Итог/параметры/остаточные вопросы](../research/interaction-prompts-owner/world-space/live-editor-style/README.md#accepted-research-result-and-recorded-values--2026-11-04)
сохранены; marker отключён при закрытой игре, payload и откат остаются.
Не готовить новую пробу или повторный тест ради формального закрытия этапа.

Отложенные самостоятельные задания: новая более удачная текстура divider
(идею только зафиксировать, сейчас не генерировать); установить/устранить источник
ореола и выцветания, не подменяя его RGB-яркостью. Последний набор NumPad9 —
research/resume baseline, не production default. Manual STOP/широкий lifecycle и
остальные production gates не доказаны общим пользовательским «успешно».
Возвращаться к работе только по новому заданию пользователя. Main/VERSION/release
не продвигать на основании принятия этого исследовательского этапа.

## История предыдущих планов

## Пользовательский прогон — установлен Style editor

2026-11-04: exact source `da830808912b38527fb5088a6543d6a070b5f3f7`
[установлен/хэш-проверен](../research/interaction-prompts-owner/world-space/live-editor-style/README.md#authorized-installation--2026-11-04),
прежняя Expanded отключена. Дальше дополнительная source-подготовка не нужна:
пользователь запускает, Ctrl+Alt+F11 → один reload/Open; сравнивает толщину линии,
button Y и четыре яркости отдельно, возвращая1 для исходной интенсивности. Num8/2
сам прокручивает17 параметров. Optional Action outline0 — отдельная проверка
читаемости. Num9 логирует набор, явный NumMultiply закрывает пробу; агент читает
локальный лог и сверяет новую installed identity. Не выдавать dimming за настоящий
контраст/доказанную glow-коррекцию. Без таймера и без production продвижения.


## Текущий этап — style controls после успешного expanded run

2026-11-04: повторять исправление таймера/focus/overflow не нужно — новый лог
подтвердил12 возвратов и5 отклонений без аварии. Пользователь просит толще линию,
подъём/опускание кнопки (пробно на уровне divider) и осознанное сравнение четырёх
яркостей. [Style source](../research/interaction-prompts-owner/world-space/live-editor-style/README.md)
готов offline318/23. Дальше безопасно установить exact successor и проверить
эти регулировки в игре; Num9 логирует17 параметров. Попросить явный NumMultiply
для новой manual cleanup-проверки. Истинное независимое подавление ореола/контраст
штрихов — открытый вопрос общего Emissive-пути; не превращать brightness/outline
в заявление о решённой причине выцветания. Ни production, ни глобальные настройки
не изменять. Последний52/30/tracking400 набор — старт пробы, не final design.


## Пользовательский прогон — установлен расширенный редактор

2026-11-04: exact source `19d35a5a0238a3b228f7058bfcd7234e647ede7e`
[установлен и хэш-проверен](../research/interaction-prompts-owner/world-space/live-editor-expanded/README.md#authorized-installation--2026-11-04).
Дальше дополнительная source-подготовка не нужна: пользователь запускает,
Ctrl+Alt+F11 → один reload/Open; увеличивает upper/lower, в том числе за прежние
36/23, проверяет крупный текст и hide/return. Num5 переключает coarse4 для шрифтов,
Num9 пишет значения в лог; NumMultiply завершает. При пределе ожидается сообщение
и последний рабочий набор, не исчезновение панели. Тестового таймера нет.
Агент затем архивирует/читает лог; actual expanded rendering/UX и production ещё
не приняты. Старый source dbd1a03 остаётся сохранённым, его marker отключён.


## Текущий этап — расширить поверхность и не завершать сессию на плохой настройке

2026-11-04: прежний recurring mechanism сработал дважды в native run, затем
тюнинг упёрся в512×128. Проблема локализована в границе собственного Canvas,
не в таймере/focus lifecycle. По запросу пользователя подготовлен
[expanded source](../research/interaction-prompts-owner/world-space/live-editor-expanded/README.md):
1024×512, крупные шрифтыдо96/64, recoverable edit rejection. Full offline309/22
PASS. Дальше установить exact successor с сохранением предыдущего payload,
пользователь сам запускает и настраивает крупный текст без дедлайна; проверить
нативную большую поверхность/метрики, сохранение UI при ограничении и NumMultiply.
Не повторять отдельные hint-size/material эксперименты; production не продвигать.


## Пользовательский прогон — установлен untimed WorldSession

2026-11-04: exact source `dbd1a033be6ee860caf0aef93cb304652c0cbb9d`
[установлен и проверен](../research/interaction-prompts-owner/world-space/live-editor-session/README.md#authorized-installation--2026-11-04),
предыдущая own-проба отключена. Дальнейшая source-подготовка перед этим тестом
не нужна. Пользователь запускает игру: NumLock, закрытый HildaSoftLight editor,
Ctrl+Alt+F11 → один reload → natural Open → несколько focus-away/return к тому
же сундуку → спокойная настройка/Num9 → NumMultiply. Таймера и счётного дедлайна
нет. Агент затем читает доступный лог, сверяет новую установленную идентичность и
HIDDEN/RESUMING/SHOWN/STOP/cleanup; пользователь даёт визуальную оценку.


## Текущий этап — повторяемый session-кандидат без тестовых дедлайнов

2026-11-04: первый полный editor source показался на~0.944s и завершился на
ordinary visibility guard, не таймере; очистка подтверждена логом. Повторять
одноразовую пробу незачем. [Новый источник](../research/interaction-prompts-owner/world-space/live-editor-session/README.md)
проверен offline301/21: own hidden→warm→shown, те же ресурсы и параметры, без
временных/счётных STOP. Дальше — закрытая безопасная установка нового exact source,
отключение старой own-пробы с rollback; пользователь сам запускает игру и проверяет
несколько уходов/возвратов к тому же сундуку, затем спокойно настраивает и явно
останавливает NumMultiply. Actual recurring visibility/render/controls остаются
непроверенными; никакого production/main/release продвижения до приёмки.


## Текущий handoff — World editor установлен, ожидается пользовательский прогон

2026-11-04: source `c2e36f90d82540bd3e23f25648e16a54c53699b8`, installed hashes и
безопасность установки подтверждены; код/сроки не менялись.
[Установка, rollback и сценарий](../research/interaction-prompts-owner/world-space/live-editor/README.md#authorized-installation--2026-11-04).
Достаточно одного natural Open: NumLock on, HildaSoftLight editor закрыт;
Ctrl+Alt+F11 → один reload → подойти к Open → Num6/7, Num2/6, Num9 → Num0,
Ctrl+Alt+F11 → NumMultiply до45s timeout. Штатная Screen-подсказка остаётся.
Затем агент читает/архивирует доступный локальный лог и сопоставляет source/installed
identity; пользователь сообщает визуальный результат. До этого не готовить новую
пробу и не считать установку runtime-приёмкой.


## Текущий этап — World prompt + live editor подготовлен source-only

**2026-11-04: READY_SOURCE, NOT_INSTALLED; runtime и production BLOCKED.**
[Один кандидат, exact manifest, подтверждённые setters и сценарий](../research/interaction-prompts-owner/world-space/live-editor/README.md).
Вопрос source-интеграции закрыт на уровне исходников/offline-моделей: четыре own
элемента, независимая панель,10 относительных параметров, current localized value
и native hint refresh, frame-Yaw, отказоустойчивый cleanup и отсутствие original
UI writes. Полная suite290/20 PASS не является доказательством отрисовки в игре.
Причина голубоватого native World-hint открыта, компенсаций/новых A/B нет.

Следующий достаточный шаг требует отдельного разрешения: при закрытой игре
установить exact candidate с rollback вне loader и installed hashes; затем один
natural Open, Ctrl+Alt+F11/NumPad edit→log→close→reopen→NumMultiply cleanup в
сохранённом45s бюджете. HildaSoftLight editor закрыт, NumLock включён; оригинальный
Screen prompt виден и рабочий. Проверить четыре World элемента и actual native
контроль/cleanup; device switch — если доступен в этом же ограниченном сценарии.
Текущие mapping/registry проверяет кандидат fail-closed при открытии; raw polling
двух редакторов registry не видит. Настройки не сохраняются автоматически.
Нет разрешения на установку, запуск/закрытие игры или hot reload в этом source-only
этапе. Более широкий lifecycle, типы действий, языки и окончательный дизайн —
дальнейшие gates после фактического combined результата, не программа новых проб
до него. Ни VERSION, ни main/релизы не изменять.

## История предыдущих этапов

## Текущий результат — технический size-тест завершён

[Size1.0→1.5 и ручной F7 PASS](../research/interaction-prompts-owner/world-space/hint-mirror/size/README.md).
Нативная смена own slot, неизменный центр/сопоставимые условия и видимое увеличение
подтверждены; пользователь отмечает читаемость. Не повторять этот этап. Rebind
после1.5 в runtime не наблюдался; не повышать его evidence gate по офлайн-тесту.
1.7–2× сохранить только как предварительное пожелание: дизайн обсуждается
отдельно, новой реализации/установки/прогона не готовить. Цвет не диагностирован,
финальная композиция/production BLOCKED. Текущая проба отключена, source frozen.

## Текущий handoff — проба размера установлена по разрешению пользователя

[Exact source9954b04 / installed hashes / rollback](../research/interaction-prompts-owner/world-space/hint-mirror/size/README.md).
Один Open: F8 start, один reload, выбрать ракурс/остановиться, F8/A1.0×,
F6/B1.5× без движения, F7 cleanup. F6 меняет только own extent, не материал.
Получить кадры/лог этого теста; не возвращаться к материал-A/B и не менять
gamma/tint/сроки ради результата. Установка не является runtime-приёмкой.

## Подготовлен следующий gate — только own icon extent1.0×/1.5×

[READY_SOURCE, NOT_INSTALLED](../research/interaction-prompts-owner/world-space/hint-mirror/size/README.md).
Следующий отдельно разрешённый игровой тест: F8 start → один reload/Open →
выбрать ракурс/остановиться → F8/A1.0× → F6/B1.5× без движения → F7. Оригинальный
Screen hint остаётся видимым. Проверять размер/читабельность/центр/обрезание и
цвет отдельно, не объявлять увеличение объяснением голубизны. Повторный
SOURCE_BOUND применяет сохранённый factor; офлайн проверено, native исполнение
этой ревизии ещё не принято. Не менять component scale/DrawSize/anchor/material/
gamma или deadlines, не возвращаться к закрытому материал-A/B.1.5 не принят как
финальный размер; FGeometry и предполагаемые pixels оригинала не использовать.

## Текущий результат — A/B закрыт без видимого исправления

[Same-source retry](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md):
native material switch, comparable-state pair и F7 cleanup прошли. Masked→stock
Translucent не дал заметного улучшения по пользовательским кадрам/отчёту. Не
повторять тот же тест и не объявлять проблему цвета решённой. Known Masked
baseline остаётся, новая Translucent occlusion отдельно не принята. Рекомендуемый
следующий самостоятельный шаг — согласовать проверку только own icon extent на
одном ракурсе; это не финальный размер/дистанционный scaling и не доказанный
color fix. Если цвет останется проблемой при сопоставимом размере — отдельно
обосновать следующий seam, без случайных gamma/tint/shader правок. Проба отключена.

## Текущий handoff — тот же A/B снова включён по разрешению пользователя

[Source/хэши и запись повторного включения](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
F8 start → один reload/Open → выбрать ракурс и остановиться → F8/A → F6/B без
движения → F7. Код, guards и сроки прежние; первый camera-guard результат не
перезаписан. Далее нужен только пользовательский прогон, не новый payload.

## Текущий результат — A измерен, сравнение материалов ещё не началось

[Точная запись](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
Получены native own-slot projection и RT/gamma/tint readback. На F6 camera guard
остановил пробу до самого переключения; B — кадр после cleanup. Не считать это
провалом Translucent и не создавать исправление/новый shader. Для закрытия
оставшегося вопроса достаточно прежнего A/B при фиксированной камере после A;
повтор/установка только по отдельному разрешению. Текущая проба отключена,
sourcecaf955f неизменён; ручной F7 в этом run не записан. Никакого расширения
guard/времени, повторения принятых renderer/Yaw или переноса полной композиции.

## Текущий handoff — A/B установлен, ожидается один пользовательский тест

[Exact caf955f / installed hashes / rollback](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
Один keyboard Open: F8 start, один ручной reload, остановиться и выбрать ракурс,
F8 sample A/снимок, F6 один раз/снимок B без движения между ними, F7 cleanup.
Игру запускает/закрывает пользователь. При early guard stop не продлевать сроки
и не повторять автоматически. Сначала получить скриншоты/логи этого изменения,
не возвращаясь к принятым binding/Yaw/renderer исследованиям. Visual gate OPEN,
production BLOCKED; дальнейшая установка сейчас не требуется.

## Подготовлен следующий gate — один own material A/B

[READY_SOURCE, не установлен](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
Сохранить keyboard/ракурс: F8 start → один reload/Open → остановиться → F8 sample A
и screenshot A → F6 → screenshot B → F7. Проекция своей геометрии измеряется;
original Screen размер — только визуальная оценка снимков, opaque FGeometry не
round-trip через pinned Lua UFunction return. Два сравнимых состояния и один
native SetMaterial, без второй регистрации/renderer, gamma/tint компенсации или
ослабления guard. Если пара не успела до early stop — неполный результат, не
автоматический повтор. Следующее разрешение относится к установке/игровому тесту;
статическая готовность не закрывает visual/production gate. Нижние записи —
история подготовки, не параллельные активные установки.

## Следующий gate — измеренный fixed-pose alpha/material A/B

[Source review завершён](../research/interaction-prompts-owner/world-space/hint-mirror/VISUAL_FIDELITY.md).
Не повторять принятые binding/device-source/renderer/Yaw/F7 исследования.
Следующая отдельная подготовка: один own component, исходная Screen-подсказка
видна; измерить проекцию и реальные RT/gamma/tint/material параметры, сравнить
Masked и stock Translucent при одинаковых остальных условиях. Проверить края
отдельно от цвета/просвечивания. Поменять только enum недостаточно из-за explicit
material override. Никаких случайных gamma/power/tint компенсаций. Если
Translucent не подходит, остановиться на gate внешнего RGB/alpha/scene path;
не создавать автоматически custom material. Новый source/runtime probe сейчас
не готовился. Следующие разделы сохраняют историю handoff, не активный install.

## Текущий результат — live hint source частично подтверждён, внешний вид открыт

[Сохранённый run](../research/interaction-prompts-owner/world-space/hint-mirror/README.md) подтвердил retained MID/Icon и controller→keyboard F,
а также guard cleanup. Не повторять эти upstream операции ради перепроверки.
Полный цикл не записан, small/faded/bluish вид не принят. Следующий отдельный
узкий вопрос — source/own paint alpha-gamma и размер в разных координатах;
причина ещё неизвестна. Новая реализация/повторный игровой тест сейчас не
готовятся. До разбирательства не объявлять полную композицию READY_SOURCE и не
смешивать это с Aphes/орнаментом. Ранее пройденный F7 gate остаётся принятым.


## Текущий handoff — hint mirror установлен, ожидается пользовательский прогон

Точный7c2aa07 установлен по разрешению с закрытой игрой/откатом. [Один сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/README.md):
F8→один reload→natural Open→keyboard/controller/keyboard→F7 до30s. F8 на controller
не нужен и может переключить ввод; source/device изменения записываются сами.
Сравнить символ/прозрачность с Original Screen, settings специально не менять.
До результата новая проба runtime PENDING, полная композиция BLOCKED.


## Следующий достаточный gate — один native hint mirror

[READY_SOURCE, не установлен](../research/interaction-prompts-owner/world-space/hint-mirror/README.md). Один будущий разрешённый прогон с Original
Screen как эталоном: после прежнего F8/reload/Open сравнить keyboard→controller→
keyboard, затем F7 до30s. Смена device/resource логируется автоматически: F8 во
время controller-фазы не нажимать, он сам может переключить ввод на keyboard.
Проверить символ текущей Interact/уже имеющийся remapping, прозрачность, crop/color,
обновление ссылки и отсутствие вмешательства; settings специально не менять.
Источник сперва проходит flags/MID/Icon readiness gate; отказ записывается до
собственного component allocation. Binding/renderer/Yaw/F7 не переоткрывать как
самостоятельные исследования. После hint acceptance можно готовить полную Aphes
композицию, но сейчас её блокер визуального input hint ещё не закрыт.


## Текущий интеграционный блокер — актуальный native input hint

[Обоснование и границы](../research/interaction-prompts-owner/world-space/composition/README.md). Сначала подтвердить read-only воспроизведение
конечного hint (Retainer effect MID→own Image), не пересобирать keymap и не
переносить оригинальный Slate. Один будущий hint-only тест на exact Open:
keyboard→controller→keyboard/current configured Interact→F7. Уже переназначенный
binding проверить там, где он есть; новых изменений settings не подразумевать.
Полный World Aphes payload до этого не объявлять READY_SOURCE. Текущая подготовка
ограничена source review и чистым планом слотов, без нового runtime probe.
После прохождения hint gate — four-child composition и own-text clipping gate,
с прежним RT512x128/anchor/scale/material/Yaw. Повторять renderer/font/orientation/
F7 как самостоятельные принятые эксперименты не требуется.


## Завершённый gate — vertical frame-Yaw и ручной F7 PASS

[Подтверждённый результат](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md):1068 guarded yaw writes, Pitch/Roll0,
успешные cancellation/native destruction по F7. Не повторять этот опыт ради
перепроверки. Проба отключена, source сохранён. Новое исследование/установка
не назначены; финальная композиция и полный production lifecycle остаются
отдельными решениями, без расширения текущего теста.


## Текущий handoff — vertical yaw установлен, ожидается один пользовательский тест

Точныйf1eb635 установлен по прямому разрешению с закрытой игрой и откатом.
[Процедура](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md): F8→один reload→natural Open→короткая проверка вертикального
Yaw→один F8→F7 до timeout. Не уходить из зоны штатного Open до F7, чтобы потеря
цели снова не заменила ручной cleanup. Runtime результата новой пробы ещё нет.


## Следующий достаточный шаг — вертикальный frame-Yaw + F7

[READY_SOURCE, не установлен](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Один будущий разрешённый прогон на прежнем
natural Open:10–15s небольших перемещений камеры с изменением высоты, один F8,
затем F7 до25–30s. Проверить вертикальность, горизонтальный поворот/видимую
ступенчатость, loop cancellation и native own cleanup. Это новый gate scheduler/
компоновки плоскости, не повторение binding/renderer/occlusion. Aphes, орнамент,
локализацию/hints и production lifecycle не переносить в эту пробу. Минимальный
резерв initial vertical yaw описан в REQUIREMENTS; actor-facing не выбран.


## Завершённый orientation run — техническая запись, без дизайна

[Результат](../research/interaction-prompts-owner/world-space/orientation/README.md): native registered-component rotation и cleanup после потери
видимости цели подтверждены ограниченно; probe отключён. F7 остаётся непроверенным,
итоговый follow angle/write count не записан. Этот шаг не назначает новый прогон,
не выбирает дизайн и не меняет payload. Production lifecycle остаётся BLOCKED.


## Текущий handoff — orientation установлен, ожидается пользовательский прогон

Точный6d44daa установлен по разрешению, source bytes не менялись. [Один сценарий](../research/interaction-prompts-owner/world-space/orientation/README.md):
fixed arc → F6 follow arc → F7 до30s. Только два пользовательских F8 после создания;
не доводить до четвёртого снимка/timeout вместо ручного cleanup. Результат pending.


## Следующий достаточный шаг — fixed/follow и ручной F7

[Orientation source READY_SOURCE](../research/interaction-prompts-owner/world-space/orientation/README.md), не установлен. Однократный look-at
оставлен контрольным режимом; ограниченный follow нужен для сравнения читаемости
при обходе объекта, а не как заранее принятое production-поведение. Один будущий
прогон: fixed arc → F6 follow arc/небольшое near-far → F7 до30s, максимум два
пользовательских F8 после стартового снимка. Это закрывает новый setter/UX и
оставшийся ручной cleanup, не переоткрывает binding/render/occlusion. Size/scale,
Aphes, ornament и полный lifecycle в этом изменении не трогаются.

## Текущий результат — один World render / Hilda occlusion / timeout cleanup PASS

[V3 runtime](../research/interaction-prompts-owner/world-space/probe/deferred/README.md)
доказал выбранный отдельный World renderer на одном natural Open: пользователь
подтвердил частичное перекрытие букв и их возвращение; native STATE и timeout
cleanup завершились. Проба отключена. Не повторять тот же rendering/binding/host
опыт. F7 в этом прогоне не выполнен; его можно совместить со следующим реальным
изменением, не создавать отдельный повтор ради уже доказанного renderer.

Предлагаемый следующий независимый вопрос — читаемость/ориентация при обычном
движении камеры и изменении дистанции. Текущая плоскость получает один look-at
при создании; ощущения раннего поворота не объяснены двумя поздними снимками.
Полное production-решение о динамическом camera-facing/lifecycle ещё не принято
за production-поведение. Aphes/орнамент/нативные hints и полная композиция остаются
отдельной интеграцией. Первый hang не диагностирован; production BLOCKED.

## Предыдущая установка

Пользователь разрешил установку; точный6ad93fc source установлен при закрытой
игре2026-10-30 с verified hashes и откатом. Следующий шаг — один пользовательский
прогон ниже; успешная загрузка ресурсов сама по себе не подтверждает renderer.

## Подготовка исходников V3

Подготовлена [ограниченная post-reload refresh ревизия](../research/interaction-prompts-owner/world-space/probe/deferred/README.md):
до hooks только проверка API, после MATCH максимум один точный LoadAsset HOST/MASK
на EngineTick; статусы недоступности/identity раздельные. После загрузки свежая
проверка actor/component/TipHUD/Open/UI/anchor, без старых wrappers; затем прежнее
создание/очистка.158 offline tests PASS. Установка пары разрешена и завершена;
следующий достаточный шаг — один тот же ограниченный сценарий для нового
resource gate и, если пройден, первого реального World renderer. Никакой смены
anchor/материала/композиции. Native hang может повториться; runtime/production BLOCKED.

## Предыдущий результат V2 — NOT_LOADED guard, probe отключён

Первый отложенный прогон дошёл из MATCH в EngineTick, но после reload точный
живой host-class gate не прошёл. World-компонент ещё не создавался. Следующая
минимальная правка — одно ограниченное разрешение/LoadAsset точных ресурсов
после reload в EngineTick, затем новая проверка actor/component/widget/UI и pose.
Никакой загрузки внутри CanShow или смены anchor/материала. Это план следующей
ревизии, не установленное исправление и не World runtime PASS.

## Предыдущая установка

Отдельное разрешение на установку получено; точный2941123 source установлен
при закрытой игре2026-10-30, с rollback/installed hashes. Следующий шаг — один
пользовательский сценарий ниже и анализ фазовых логов; запуск агентом не выполнялся.

[Source-only follow-up](../research/interaction-prompts-owner/world-space/probe/deferred/README.md)
подтвердил различие контекстов/lock, но не причину зависания. Новая отдельная
ревизия: preload через EngineTick до own hooks; MATCH только ставит создание в
очередь; fresh identity/UI/native validity; lookup-only после reload; фазовые
BEGIN/END и отложенная очистка.139 offline tests PASS. Установка новой пары уже
разрешена и завершена; следующий шаг — один прежний пользовательский сценарий с
анализом последней фазы. Native hang может повториться; таймер/pcall не прерывает
невернувшийся вызов. Не менять anchor/материал и не переносить полный дизайн.
World rendering/visual acceptance/production BLOCKED.

## Предыдущий результат — первый World prototype BLOCKED после зависания

Первый разрешённый запуск завершился пользовательским сообщением о зависании:
точное Open MATCH есть, завершения World.create/отрисовки/очистки нет. Проба
отключена при закрытой игре; логи сохранены. Следующий достаточный шаг — узко
проверить контекст создания из script callback/загрузку и определить фазовые
границы для диагностики. Не повторять текущий payload и не устанавливать новую
версию автоматически. Причина неизвестна; World/production BLOCKED.

## Предыдущая подготовка и процедура

[Один собственный World WidgetComponent](../research/interaction-prompts-owner/world-space/probe/README.md)
подготовлен на подтверждённых host/binding маршрутах и точном engine/UHT контракте
создания/регистрации/очистки. По разрешению пользователя установлен2026-10-30
при закрытой игре, с verified hashes/rollback. Следующий шаг — один manual-reload тест
WORLD TEST над естественным Open. Нужны видимые буквы→частичное перекрытие Хильдой→
их возвращение при смещении→F7 удаление только своего renderer при сохранённом
оригинале. Лог RT/material/visibility не заменяет визуальное доказательство.
Не добавлять billboard, новые offsets, Aphes/орнамент или production lifecycle до
этого результата.124 offline tests PASS; runtime/production BLOCKED.

## Предыдущее основание — natural Open join/pose PASS

[Исправленный прогон](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
подтвердил точное соответствие одного item_lootbox02_C Open actor/компонента/TipHUD
и2 finite world-pose снимка. Acquisition cap128 сохранил3 пары для CanShow;
оба script readers работали после одного ручного reload. Проба отключена.
Не повторять этот binding/host/font тест. Следующая независимая задача — source
подготовка одного своего World WidgetComponent при сохранённом оригинальном
prompt: native registration/ownership/resources, camera-facing pose, масштаб и
очистка. Затем отдельно разрешённый runtime должен проверить реальную глубину и
перекрытие Хильдой. Здесь новый World payload не создавался/не устанавливался.
World runtime acceptance и production остаются BLOCKED.

## История исправления acquisition-only budget

Поправка подготовлена,108 offline tests PASS, точный603ab6b source установлен
по разрешению пользователя при закрытой игре; runtime pending.
При128 закрывается только acquisition; сохранённые≤8 пар доступны CanShow в
исходном120s окне. Следующий достаточный тест — один ручной reload после arm,
появление Open и MATCH/POSE либо точный отрицательный итог. Больше init callbacks,
новых hooks, объектов или автоматических повторов не добавлено. Production/World BLOCKED.

## Основание поправки —3 пары приобретены, selection прерван init budget

[Прогон](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
подтвердил BeginPlay после reload и3 точные Open actor/component/TipHUD пары.
Весь observer остановился на128 init callbacks до первого CanShow, за20.789s;
active join/pose не получены, причина остановки известна и не является identity error.
Проба отключена. Не повторять без изменений и не повышать лимиты автоматически.
Выбранная source-поправка: по128 закрыть только
acquisition, оставить≤8 уже проверенных пар и selection в исходных120s/4096
CanShow/4 poses. Она подготовлена и проверена, её установка разрешена; фактический
deployment фиксируется отдельно. World rendering/production остаются BLOCKED.

## История подготовки и установки первого dual-script probe

[Подготовленный исходник и процедура](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
проходят105 offline tests.8 Open attempts/128 init/4096 CanShow/120s/4 poses;
нет игровых записей или сохранённых UObject wrappers. Следующее достаточное
доказательство требует одного ручного reload сохранения после arm. Отдельное
разрешение на установку получено; точный3497ab5 payload установлен closed-game.
Игра/reload агентом не запускались, приёмка остаётся pending.
Проверять реальные callbacks после reload, точный join и pose; не повторять Aphes,
UserWidget или CanShow-only acceptance. Любой отрицательный итог завершает этот
run без нового наблюдателя. World rendering/production остаются BLOCKED.

## Основание выбранного маршрута — parent Blueprint BeginPlay + CanShow

[Сравнение и точный контракт](../research/interaction-prompts-owner/open-binding/ROUTE_REVIEW.md)
подтвердили explicit BaseLoot BeginPlay→parent BeginPlay→own widget цепочку.
Подготовлен отдельный read-only прототип двух точных script hooks:≤8 временных
Open attempts при естественном BeginPlay, затем exact pointer join с известным
CanShow. Будущий один тест требует arm до ручного reload текущего
сохранения; просто подойти к уже инициализированному сундуку недостаточно.
Исходник READY_SOURCE, установки/запуска нет; исходный route review был source-only.
Setup/SetArrayData не выбраны без подтверждённого natural callsite. World B остаётся
предпочтительным условным направлением; Screen не удовлетворяет принятому occlusion.
Live mapping/pose, World rendering и production BLOCKED.

## Принятый отрицательный результат — Open binding NO_EVENTS

[Первый event-scoped тест](../research/interaction-prompts-owner/open-binding/README.md)
завершён: SetShow hook зарегистрирован, но за31.965s до user stop callbacks=0,
MATCH/POSE нет. Проба отключена. Это не ошибка getter или доказанный native bypass:
причина отсутствия событий неизвестна. Повтор того же опыта без новой причины
не запланирован. Источник для следующего ограниченного теста выбран выше;
не ставить автоматически ещё один hook.
Host/CanShow результаты сохраняются. Live mapping, World и production BLOCKED.

## История первого Open binding прототипа

[Open binding](../research/interaction-prompts-owner/open-binding/README.md)
содержит проверенные source/API контракты и отдельный прототип: естественный
SetShow context → GetWidget/GetOwner → взаимные ссылки actor/component/TipHUD →
world transform. Никакого поиска первого сундука или сканирования объектов.
Следующее достаточное доказательство — один отдельно разрешённый тест входа в
зону Open, ручного snapshot и выхода/stop. MATCH закроет одну live mapping/pose
границу; no-match за60s/64 callbacks означает недостаточность этого event route,
без автоматического расширения исследования. Точный148e5c0 исходник теперь
установлен по отдельному разрешению пользователя; игра не запускалась, тест pending.
World WidgetComponent/Aphes/скрытие оригинала в этот тест не входят.

## Принятое основание — host runtime PASS

[Независимый UserWidget](../research/interaction-prompts-owner/userwidget-host/probe/README.md)
загружен, создан с отдельным деревом, показан после Construct Hidden и вручную
удалён в игре; пользователь подтвердил сценарий. Проба отключена, повторять её
не нужно. Следующая независимая неизвестная — exact natural Open
actor/component/pose. Её доказательство позволит привязать будущий отдельный
World WidgetComponent к реальному взаимодействию; до этого World payload и
production BLOCKED. Новый observer/установка этим результатом не разрешены.

## Источники завершённой проверки host

[Статический audit](../research/interaction-prompts-owner/userwidget-host/README.md)
и [runtime result](../research/interaction-prompts-owner/userwidget-host/probe/README.md)
фиксируют класс, registry/loading, source identity, отдельное дерево, Construct и
ручное освобождение. World source/material review остаётся в
[World report](../research/interaction-prompts-owner/world-space/README.md).
Предпочтительный объектный дизайн и fallback X50%/Y78% неизменны.

## История композиции после технического Aphes runtime PASS

Aphes OPEN→READ/manual cleanup, ornamental TipHUD composition и отдельный
viewport root sample имеют свои принятые узкие результаты и сохранённые артефакты.
Полный production lifecycle/GC/input/DPI/localization остаётся отдельным gate.

## Template-copy creation/storage завершён; setters рассмотрены в следующем отчёте

[Font-template](../research/interaction-prompts-owner/font-template/README.md)
подготовлен: один Ctrl+Alt+F7, naturally loaded donor, один новый RF_Transient UFont,
проверки классов/структуры и native storage addresses, donor post-check. Один
пользовательский запуск дал STORAGE_CHECK_PASS: Template forwarding и раздельный
observed storage подтверждены. Probe отключён после выхода; повторять этот тест
не нужно. Setter/ownership review и минимальная настройка только FFontData копии
были подготовлены отдельно и затем прошли ограниченный runtime выше.

## Выбор механизма — private UFont copy для dynamic text

[Dynamic font readiness](../research/interaction-prompts-owner/DYNAMIC_FONT_READINESS.md)
сравнивает shared donor, C++ path constructor, PNG и Coherent. In-place font
replacement отвергнут из-за потребителей; прямой C++ не готов по linkage/build.
Read-only construction/storage и Aphes-text write/render/reference-release
проверены в одном сценарии; полный cache/GC lifecycle остаётся открытым.
Старое разрешение установки касалось только завершённого
read-only probe. Нынешнее отдельное разрешение позволило установить Aphes-text;
его игровой запуск агентом не выполнялся, пользовательский run теперь принят технически.

## Отдельно подготовленный PNG-header — READY к import/alpha/unbind test

[PNG-header](../research/interaction-prompts-owner/png-header/README.md) подготовлен
offline: local glyph PNG, explicit CDO/ImportFileAsTexture2D, UImage texture binding,
проверенный divider и pair cleanup. Не установлен, editor/cooker не нужен для
этой гипотезы. После отдельного разрешения проверить native import, прозрачность
и unbind в одном Open prompt. Не повторять успешные primitive/divider tests.
Нexus setup/extraction и словарь Aphes остаются отдельными вопросами.

## Завершённый divider — resource-free линия видна, pair detachment доказан

[Divider result](../research/interaction-prompts-owner/DIVIDER_READINESS.md)
сохраняет кадр/логи/хэши: Box без ресурса отрисован, оба элемента удалены по
key-control через ~5.5 с. Пользователь не уверен в наблюдении исчезновения;
этот пробел не подменяется словами об уверенной visual cleanup acceptance.
Probe отключён. Повтор ради общего подтверждения механизма не нужен; следующий
вопрос выбирать отдельно для Aphes/дизайна/production lifecycle.

## Историческая подготовка разделителя

[Divider readiness](../research/interaction-prompts-owner/DIVIDER_READINESS.md)
выбирает UImage + color-only Box, 140×2 layout units под OPEN, без нового ресурса
и без изменения исходного prompt. Source подготовлен с default/readback checks
и независимой очисткой двух элементов. Установлен по прямому разрешению при
закрытой игре, 22 offline groups проходят. Следующий достаточный шаг — один визуальный тест
линии/удаления пары, а не повтор доказательства TextBlock. Actual brush defaults,
видимость/толщина, clipping/reflow в этой ревизии ещё не проверены.

## Завершённая основа — один native child добавлен, показан и удалён

[ui-child результат](../research/interaction-prompts-owner/ui-child/README.md)
подтвердил primitive TextBlock/typed Font copy/AddChildToCanvas/RemoveChild на
одном Open prompt; пользователь увидел OPEN и удаление без заметного смещения
оригинальной строки/иконки. Probe отключён. Повтор этого опыта не нужен.
Следующий этап выбирать по отдельному вопросу Aphes/разделителя, не превращая
один успех в production/lifecycle/GC acceptance и не возобновляя native observer.

## Историческая подготовка измеренного slot

Второй прогон дал Position=(38,0), Alignment=(0,0.5), table shape. Designer X=88
больше не используется как live baseline: source проверяет измеренный Open X=38
и размещает только свой новый label относительно текущего слота. Оригинал не
меняется. Исправление установлено по прямому разрешению при закрытой игре;
следующий шаг — пользовательский creation/attachment/removal test. Сбор координат
завершён, новый observer не нужен.

## Исторический разбор первого slot guard

CanShow и выбор цели сработали, но старый guard Position/Alignment остановил
прототип до создания нового TextBlock. Следующий минимальный вопрос — фактические
четыре значения и формат результатов getters. В source добавлен однократный
LAYOUT_OBSERVED перед неизменённым guard; новая ревизия установлена по прямому
разрешению при закрытой игре, предыдущая отключённая версия сохранена для отката.
После получения чисел пересмотреть live layout contract, не угадывать смещение
и не ослаблять проверку ради показа. Создание/удаление UI остаётся непроверенным.

## Историческая подготовка первого stock-font прототипа

Пользователь выделил независимый [stock-font child experiment](../research/interaction-prompts-owner/ui-child/README.md).
Исходник подготовлен и установлен по прямому разрешению при закрытой игре:
новый TextBlock в CanvasPanel_6 одного «Открыть», полный
typed Font copy, без изменения оригинала; один запуск, stop/timeout/own-child
cleanup. Разделитель исключён до подтверждения brush path. Следующий достаточный
шаг — первый пользовательский UI attach/detach test и анализ сохранённого лога; не нужно
решать Aphes/cooker или повторять старый CanShow-read probe. Native rendering/GC/
влияние на desired size остаются вопросами этого опыта. Production BLOCKED.

## Исторический cooked Aphes-вариант — toolchain BLOCKED

[Visual readiness](../research/interaction-prompts-owner/VISUAL_READINESS.md)
подтвердил slot ownership. Выбран узкий путь: добавить верхний label/разделитель
соседями TextBlock_89 в CanvasPanel_6, сохранив исходные localized text/input/
hold/lock и родителей. Полная замена TipHUD/overlay не оправданы.
Этот первоначальный путь не дал cooked Aphes font object/prototype. Текущий
transient-provider source описан выше и рассматривается отдельно.
Проверка доступного toolchain [завершена](../research/interaction-prompts-owner/FONT_RESOURCE_READINESS.md):
UE4.27 editor/cooker в проверенных местах не найден. Только для возврата к cooked route —
получить доступ к совместимому toolchain, затем подготовить локальный companion
runtime UFont/FontFace из уже имеющегося TTF,
не меняя общие шрифты и не публикуя игровые ресурсы. Только затем — подготовка
одного bounded additive prototype и отдельное разрешение на runtime.
Не повторять CanShow-read test и не возвращаться к полному observer для этой
шрифтовой зависимости. Планы полного observer ниже остаются отложенной историей,
не обязательной программой следующих действий.

**Накопленные результаты, 2026-10-28:** [штатный UHT-генератор](../research/interaction-prompts-owner/UHT_SIGNATURE.md)
дал точную отражённую декларацию SetupTipMessage2, без собственного C++-мода.
Порядок/типы пяти входов и отсутствие const/ref/out/return установлены; полный
numeric flags dump и регистрация hooks не выполнены. Предыдущее ограничение
Lua EPropertyFlags API сохраняется, но больше не требует reader для получения
этой декларации. Полный native observer остановлен на callee frame/Locals lifetime.
Пользователь принял уменьшенный эксперимент: текущие поля TipHUD в одном
безаргументном CanShow callback. [CanShow observer](../research/interaction-prompts-owner/can-show-state/README.md)
подготовлен, проверен offline и установлен по отдельному разрешению пользователя
при закрытой игре; native-массивы, отложенный readback и UEPseudo отложены.
Первый пользовательский прогон завершён: script hook сработал, три TipHUD,
шесть снимков, локализованные строки доступны. [Точный результат](VERIFIED_RUNTIME.md)
и ограничения сохранены, probe отключён. Не повторять этот положительный этап
без новой причины; дальнейший эксперимент выбирать под конкретный остаточный
вопрос реализации. Подробности первого этапа и хэши —
[VERIFIED_RUNTIME.md](VERIFIED_RUNTIME.md), разделы 1–8. Production gate **BLOCKED**:
живой final writer, lifecycle, фактическое соответствие действий и шрифтовый
render path ещё не доказаны. Никакого production-кода и runtime-кандидата нет.

## Завершённый статический этап

Подтверждены component-владелец `BaseGameEventObject_BP` → `ExtendedWidget` →
`TipHUD_C`, native consumer `SetupTipMessage2`, локализационные пути для
Take/Open/Check, отдельная пока не связанная ветка `Ladder_BP`, сырой
`Genesis/Content/Fonts/Aphes.ttf` с проверенной латинской cmap. Это **не**
доказательство реального порядка UI-записей, всех live instances или UMG-рендера
символов. Общие выводы уже перенесены в Asterigos-Research (R-006/R-007).

## Выполненный минимальный эксперимент — CanShow

Проверить, достигается ли callback нужного живого TipHUD и как меняются его
текущее Text-поле/visibility/opacity/enabled при обычном подходе/уходе и меню.
Без actor mapper, textures, исходного результата CanShow и final-writer claims.
Если этих наблюдений хватит для следующего решения, не возвращаться автоматически
к полному probe. Если не хватит — назвать конкретный остаточный вопрос и только
затем выбирать более сложный механизм. Первый runtime подтвердил чтение
текста/состояния, но не покрытие полного lifecycle или final writer.

## Отложенная программа полного observation-only probe

**Вопрос:** кто действительно пишет и обновляет живой prompt после
`SetupTipMessage_Proxy`/`SetupTipMessage2`, и как связаны конкретный actor,
`ExtendedWidget`, локализованная строка, кнопка и показ/скрытие?

1. В локальном Codex открыть checkout **нового самостоятельного репозитория**;
   при параллельной работе выделить отдельный worktree. Проверить HEAD/изменения,
   текущие DevRules, `AGENTS.md`,
   `docs/STATUS.md`, этот план, `VERIFIED_RUNTIME.md` и Research index.
   Ветку `research/interaction-prompts-owner` продолжать без переписывания
   принятой статической истории. Не трогать чужие worktrees или установленную игру.
2. Прежде чем писать probe, проверить отражённые сигнатуры и реально доступную
   форму UE4SS callbacks точных seams из [раздела 7](VERIFIED_RUNTIME.md):
   `TipHUD_C:SetupTipMessage_Proxy`, `ExtendedUserWidget:SetupTipMessage2`,
   `TipHUD_C:CanShow`. При неизвестном ABI сохранить конкретный разрыв;
   не угадывать параметры и не расширять эксперимент глобальными hooks.
3. Используя полученную UHT-декларацию, подготовить минимальный read-only observer только для этих объектов и их
   реальных владельцев. Записывать native pre/post, Blueprint post-only и последующее ограниченное
   readback `TextBlock_89`, `RetainerBox_0`, текст/FText, textures, input state,
   visibility/opacity/enabled и identity. Ограничить частоту и длительность;
   локализовать ошибки по объектам; не делать writes или переиспользовать
   production-mod loaders без проверки необходимости.
4. После отдельной разрешённой безопасной установки при закрытой игре пользователь
   сам запускает игру и проходит доступные pickup/chest/document/ladder,
   смену цели, уход из радиуса, клавиатуру/геймпад и меню. При недоступном виде
   объекта записать именно этот пробел, не имитировать его создание.
5. По полученным наблюдениям обновить `VERIFIED_RUNTIME.md`, затем
   `STATUS.md`/gate. Геймплей и шрифты не менять. Только переиспользуемые новые
   факты переносить в общий Research; не дублировать мод-специфическую приёмку.

**Stop condition:** удалось связать реальный owner с native update → readback,
показом/скрытием, устройством ввода и целями; либо установлен точный недоступный
seam, ограничивающий текущий механизм. Отсутствие события само по себе не
доказывает скрытие. Не делать цикл новых probe ради неопределённых рисков.

Подготовка probe может выполняться как отдельный research-only этап после проверки
локальных зависимостей. Установка и пользовательский runtime-прогон — отдельная
граница безопасности. Не запускать/закрывать игру, не заменять загруженные файлы,
не применять hot reload без специального разрешения.

## Историческая гипотеза механизма и визуальный ориентир

Эта гипотеза уточнена текущим Visual readiness report: узкое расширение
CanvasPanel_6 с отдельным локальным font resource; asset override остаётся
резервом, отдельный overlay требует больше недоказанных связей. Это **не**
разрешение на production implementation.

Внешний вид ориентируется на реальное внутриигровое появление названия локации
«Пограничная застава» (см. `REQUIREMENTS.md`), но связь его шрифта/разделителя
с техническими UI-ресурсами пока не подтверждена. Визуальный font/layout тест —
отдельная последующая гипотеза: не смешивать её с observation-only probe.

## Исторический результат отложенного полного observer

Точный branch/commit и статус push; probe identity и hash только если он был
создан; logs/evidence локально вне публичного Git; краткий вывод о показе,
поздних writers, устройстве ввода и climb-owner, обновлённый production gate.
Research-only: никаких production edits, релизов и изменения `VERSION`.
