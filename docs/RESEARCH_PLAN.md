# План исследования — contextual prompts и письменность

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
