# Статус Immersive Interaction Prompts

## Универсальные подсказки: native selected-owner survey — source-only (2026-11-09)

Приоритет — реальный World-охват всех подходящих штатных взаимодействий,
а не дальнейшая полировка трёх точных объектов или отдельное расширение
исследования переходов между сейвами. Текущий доказанный
`PlayerActionComponent+0x410` уже определяет выбранный игрой объект:
повторять игровой target selection нет оснований. Ограничители находятся
ниже: `IIPInteractionSource` распознаёт только `Open/Take/Check`,
`IIPComposition` и World предполагают те же действия, а раннее
скрытие Screen требует проверенного native/World размещения.

Исследовательская ветка `research/native-selected-capability-01`
добавляет **только** однократное, ограниченное чтение
неизвестного *уже выбранного* owner через штатный selected-owner path:
его class/tag, фактически видимый native widget class и наличие
локализованного текста, без копирования текста в логи. Это не новый
поиск владельцев, не скрытие Screen и не разрешение на World у новых
объектов. Для неготового UI до 8 последовательных выбранных чтений,
с ограничением в 128 identities на карту; остальные остаются stock.
Существующий `wide_safe`-блокер на смене сейвов остаётся известным,
но не превращается в отдельный приоритет без препятствия основной
цели. Ни один новый runtime результат не предполагается.

Следующий достаточный внешний результат, если офлайн-сборка прошла:
один разрешённый естественный игровой маршрут с *разными* действиями
и геометрией, без обязательной загрузки второго сейва. Сопоставить
native selected action/widget и реальные видимые Screen-подсказки;
только затем убрать искусственные action allowlists, добавляя
capability-check и подтверждённый geometry-safe World fallback.
Для установки/запуска необходимо отдельное разрешение.

## wide_safe — игровой lifecycle-блокер (2026-11-09)

На переходе между сейвами в одном процессе новый контроллер был
захвачен, затем незавершённое восстановление старого контекста
привело к `CLEANUP_PENDING` и `STOP`. Второй сейв не обследован,
ручная очистка по F4 не подтверждена. Проба выключена при закрытой
игре. Следующий шаг — воспроизвести наблюдавшийся порядок teardown
и повторного захвата в существующей проверке перед новой установкой.
[Последовательность и инвентаризация](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#wide_safe--игровой-прогон-двух-сейвов-2026-11-09).


## Смена двух сохранений за один запуск — офлайн-гейт (2026-11-09)

**Офлайн-гейт пройден:** исходники `21931264ff7ecd6a63c2ee0c90bb87ba66aab1b8`,
[CI 42535860501](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42535860501)
PASS: все тесты репозитория, включая 10 `test_tiphud_wide_safe.py`
сценариев. Проверена **модель** двух сохранений в одном Lua VM,
сброса прежнего lease, возвращения native transform,
повторной регистрации и stock-only нового объекта, а также
фактическая сборка Lua entrypoint и доставка мокированных
LoadMapPre/BeginPlayPost callbacks. Это **не** проверка
на установленном UE4SS или реального порядка EndPlay и карты.



Принят пользовательский маршрут: первый сейв с тремя ранее проверенными
Open/Take/Check, второй сейв с дверью/настенным объектом/предметом,
без F4 и без завершения игры между загрузками. Подготовлены
модульные проверки `map_pre → restore → BeginPlay новой карты`
и проверка **собранного** `main.lua` с реальным
`RegisterLoadMapPreHook` и повторным захватом контроллера.
Событие `MAP_PRE` теперь явно отделяет фрагменты журнала.
Результат CI — отдельное офлайн-доказательство, не runtime PASS.

Критический runtime gate остаётся открыт: действительная доставка
`LoadMapPre` и `BeginPlayPost` при загрузке другого сейва,
сохранность observer/ресурсов и отсутствие `STOP` либо
`CLEANUP_PENDING`. Если новый контроллер не перехвачен, второй
сейв нельзя считать обследованным. F4 — один раз в самом конце;
после него наблюдатель не перевзводится. Никакой установки пока.


## Wide-safe source candidate — 2026-11-09

Следующий source-only срез `wide_safe` добавляет ограниченную
регистрацию всех распознаваемых native `Open/Take/Check`
владельцев в проверенной цепочке BeginPlayPost, но **не
выдаёт непроверенную геометрию за безопасность**. Для трёх
точных проверенных объектов прежний `first_and_fast`
остаётся первым World. Все прочие обнаруженные пары
временно работают stock-only; на первом штатно
показанном выбранном owner однократно логируются
класс, координаты native anchor и камеры, локализованный
native ready. Никакого смещения новых корней.
Регистрация охватывает не только проверенные Open/Take/Check:
неизвестные native action tags с `ActionName=25` собираются
read-only и отмечаются `OTHER_ACTION_STOCK` (ограничение
128 уникальных class/tag), без попыток World и без смены
штатного widget. Это ещё не объявление их поддержанными.

Это **частичный инженерный прогресс в универсализации**,
не принятие game-wide World. Прямые A→B, карта,
устройство/remap и размещение дверей всё ещё требуют
нативного/визуального гейта. [Границы кандидата](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#wide_safe--универсальная-регистрация-без-слепого-скрытия).

Кандидат не установлен, никаких игровых запусков/изменений.
Исходная `first_and_fast` остаётся проверенной визуальной базой,
а дополнительные микрооптимизации отложены.


## Новый приоритет: универсальный World и видимость у стен — 2026-11-09

Пользователь **принял `first_and_fast` как рабочую визуальную
основу** по трём точным Open/Take/Check. Это достаточный уровень
визуала для перехода к следующему этапу, но не общий runtime
или production PASS. Дополнительное ускорение и устранение
редкого неполного первого кадра отложены как необязательная
полировка до реальных жалоб по ходу игры.

Ближайшая цель — **все подходящие интерактивные объекты игры**,
не три allowlisted пути. Отдельный неиспытанный риск —
World виджет на дверях/в стенах/нишах: текущий
`source location + 32 Z` с depth-test может быть загорожен
геометрией, хотя штатный Screen был видим. Не объявлять дефект
у конкретной двери без проверки. Не отключать depth test,
поскольку перекрытие Хильдой — часть принятого дизайна.
Если безопасная World-композиция не подтверждена для цели,
не скрывать доступный штатный Screen. [Требования](REQUIREMENTS.md#рабочая-визуальная-база-и-геометрическая-видимость--решение-2026-11-09)
· [план](RESEARCH_PLAN.md#общий-охват-и-геометрическая-видимость--2026-11-09).

Текущий `first_and_fast` по отчёту `6a54499` отключён,
других активных IIP нет; новая установка/сеанс не разрешены.


## Three-mode runtime checkpoint — 2026-11-09

The exact three-object `first_and_fast` mode proved in-game that
early RenderTranslation and native `NAME_None` fast child construction
can coexist: Open/Take/Check World was first; selection-to-SHOWN logs
24–34 ms; `private_ui` ~10–11 ms; three F4 restorations passed.
Each first World presentation still showed one weak/partial frame.
This is **three allowlisted objects only**, not general first approach.
The candidate was disabled after testing; no IIP active per report.
[Canonical runtime evidence](VERIFIED_RUNTIME.md#first-approach--fast-world-ui--three-bounded-modes-2026-11-09).

Next sufficient step: source-only investigation of the weak/partial first
World frame and bounded expansion of first-approach eligibility, with
separate direct-target handoff/remap and engine frame-time gates.
Keep the simple fast construction path. Do not add a persistent
pawn-owned World without evidence that the remaining 10–11 ms
`private_ui` cost materially fails the UX or lifecycle demands it.
No new installation or gameplay authorization is implied.


Подготовлен source-only преемник `911d5ea` с раздельными режимами
первого подхода и сокращённого создания дочерних виджетов. Первый
режим ограничен тремя точными проверенными объектами. Постоянный
pawn-owned World между целями пока не реализован. На `7b2dbc4`
режим `first_approach` показал World первым на трёх проверенных
Open, Take и Check, с возвратом Screen по F4. Измерение времени
кадров остаётся открытым. Отдельный прогон `fast_create` сократил
время от выбора до SHOWN с 54–65 до 25–33 мс на тех же целях.
В совместном режиме `first_and_fast` World появился первым на тех же
трёх целях, время до SHOWN составило 24–34 мс. Кандидат отключён
после прогона. Production acceptance остаётся открытым.
[Протокол и границы](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#первый-подход-и-сокращённое-создание-world).

Coverage `8399687` увидел шесть эпизодов выбора, но не квалифицировал
ни одной цели. Исправлена область видимости callback в собранном
entrypoint, ошибки квалификации теперь видны в журнале. Повторный
игровой прогон `911d5ea` подтвердил Open, Check и Take на одном
маршруте и возврат Screen по F4. Пользователь заметил задержку
перед World. Пять созданий дали 53,87–66,22 мс до SHOWN, повтор
без пересоздания — 1,82 мс. Производительность остаётся открытой.

## Принято: общий цикл — видео A, охват действий, холодный World (2026-11-08)

После одного успешного Open с RenderTranslation пользователь выбрал
**параллельную работу** над тремя результатами, а не три последовательных
исследовательских проекта: (1) покадровая визуальная проверка A и F4;
(2) расширение безопасного раннего скрытия на подтверждённые Open/Take/Check
и переходы целей; (3) уменьшение холодной стоимости World.

**Разделять нужно доказательства и режимы**, а не работу:
существующий `0a74d8a` / отчёт `85bde00` остаётся контрольной базой A;
универсальная политика раннего перемещения и быстрый World не должны
зависеть от совпадения их результатов. Отдельные runtime gates должны
показывать, какой механизм вызвал изменение. Первым не создавать
массовые actor-owned World-компоненты и не скрывать unsupported.
Текущая установка — RenderTranslation A; без нового отдельного
разрешения не ставить общий кандидат и не запускать новую игровую сессию.
[Единый рабочий контур](RESEARCH_PLAN.md#единый-цикл-проверки-а-масштабирования-и-холодного-world--2026-11-08).


## RenderTranslation A — один Open, 2026-11-08

Пользователь увидел только World. Журнал подтвердил раннее смещение,
его сохранность при обоих выборах, актуальную кнопку и возврат
трансформации по F4 с очисткой. Видео нет, первый кадр и frame time
не измерены. Файлы A сохранены, маркер отключён, B не активировался.
[Результат](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#игровой-результат-rendertranslation-a).

## Source-only кандидат: смещение штатного TipHUD за экран (2026-11-08)

По решению пользователя следующий ограниченный UX-тест проверяет
**отдельную от root alpha ветку**: `UWidget::SetRenderTranslation`
на `TipHUD.WidgetTree.RootWidget` только если это идентичный
`CanvasPanel_0` проверенного Open-сундука. Серийная иерархия
подтверждает, что в корне лежат TextBlock_89, RetainerBox_0
и locked CanvasPanel_2; отличие от смещения `ExtendedWidgetComponent`
сохраняет native Screen membership/CanShow. Видимость, ColorAndOpacity,
RenderOpacity и контролы не меняются. Экспериментальное смещение
`+16384px X` рассчитано только на известный 2560x1440 runtime.
[Исходники и границы](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#эксперимент-translation--исходный-кандидат).

Кандидат source-only: `IIPPrehideTranslation.lua` +
`prehide-translation.patch`, отдельно от прежнего tint
`IIPPrehideOpen.lua`. Game-render, Slate offscreen culling,
native text/icon обновление, persistence и restore ещё **UNKNOWN**.
Установленный `f93867e` по последнему сообщению пользователя
не изменялся; ни установка, ни игровой запуск новым кодом не
разрешены. Режим B с ранними assets/World по-прежнему отложен.


## Проверка альтернативы: штатный TipHUD как World — source-only (2026-11-08)

По запросу пользователя рассмотрен вариант **одного** native-owned
TipHUD в World-space вместо пары Screen+own World. Гипотеза
простого переключения **не подтверждена**: в UE4.27
`SetWidgetSpace` только присваивает `Space`, тогда как
`FWidgetRenderer` для World создаётся в `OnRegister`.
Зафиксированный `ExtendedWidgetComponent` уже зарегистрирован в
Screen-space при доступном `BeginPlayPost`; просто сменить `Space`
недостаточно для полноценного рендера. Перерегистрация потребовала бы
недоказанного native lifecycle seam и восстановления Screen/рендер
состояния, а API `RegisterComponent`/`UnregisterComponent`/
`ReregisterComponent` в UE4.27 C++ не являются `UFUNCTION`.
Нельзя считать этот путь более простой заменой существующего World.
[Исходники и пределы](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#native-tiphud-as-single-world-widget--source-only-check-2026-11-08).

Исследование не разрешает изменение штатного компонента и не отменяет
World/depth требования. Native Screen S1 остаётся другой дизайнерской
архитектурой (без настоящей occlusion), требующей отдельного решения
пользователя. Пока для настоящего World предпочтительнее завершить
узкую проверку writer, который возвращает root RGBA до первого Open.

## Source-only уточнение: куда мог исчезнуть ранний alpha (2026-11-08)

В проверенном UE4.27 `UUserWidget::SetColorAndOpacity` присваивает
`ColorAndOpacity` переданное значение и обновляет Slate; 
`UUserWidget::SynchronizeProperties` читает это свойство и передаёт
`ColorBinding` в `SObjectWidget`. В её собственном теле нет присваивания
`ColorAndOpacity=(1,1,1,1)`. Поэтому **одна обычная синхронизация
Slate не объясняет** документированный возврат *UObject readback*
к единице на `f93867e`. Не установлен ни внешний writer, ни
обязательная поздняя инициализация как причина.

Следующий достаточный локальный read-only шаг — узкий статический
поиск фактических записей корневого `TipHUD.ColorAndOpacity` через
`SetColorAndOpacity`, прямые Blueprint property writes и вызовы
`PreConstruct/Construct`, включая релевантных родителей/потребителей.
Если точный writer не найден, только тогда ограниченно определить
интервал потери alpha на одном объекте в runtime. Без новой записи
alpha каждый кадр и без прогона B до результата A.
[Обоснование](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#источник-потери-раннего-alpha--статический-дискриминатор).


## Новое UX-направление: скрывать stock до первого paint (2026-11-08)

Пользователь не считает полезной целью побитовое/покадровое совпадение
двух рендереров. По видео `6bfc676` холодный Screen опережает
полный World на 117,23 мс, повторный — на ~16 мс. **Нормальная
подмена Screen→World отклонена** даже на одном кадре. Пользователь
предпочитает короткую задержку только World и предложил ранний
`ColorAndOpacity.A=0` для поддерживаемого native TipHUD, с
аварийным восстановлением stock примерно через 0,5 с, если World
не готов. Порог пока гипотеза; fallback нельзя превращать в
штатное переключение при каждом показе.

На одном сундуке `d8a9182` подтвердил раннюю идентичность:
BeginPlayPost увидел ещё не добавленный в Screen TipHUD, который
совпал с экземпляром в обоих эпизодах. RGBA и пустой binding
совпали в снимках. Кисть сменилась с PS4-заглушки на Xbox.
Подготовлен source-only тест раннего tint на этом сундуке. Отдельный
вариант переносит проверку и загрузку host-ресурсов до подхода.
Первый paint, возврат в игре и выигрыш по кадрам остаются непроверенными.
Игровой A `7f497fc` не дошёл до pre-hide. Исправлена блокировка
на переходе загрузки без активной записи. Исправление требует прогона.
В повторном прогоне `af12878` ранняя запись прошла, но первый выбор
закончился fallback `native_contract_lost`. Уточнены причины в логе.
На `f93867e` к первому выбору тот же TipHUD уже имел исходный
RGBA. Однократная ранняя запись не сохранилась в проверенном прогоне.
Момент и писатель изменения ещё не установлены. B не проверялся.
[Сборка и протокол](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#read-only-кандидат-ранней-пары).
Историческая запись о `6bfc676` устарела. По последнему сообщению
пользователя установленный исследовательский кандидат — `f93867e`,
он оставлен без изменений. Текущий факт закрытия игры в этом
сообщении не подтверждён; перед установкой проверить host и откат.

## Новый блокер UX — native Screen появляется раньше World (2026-11-08)

Пользователь в реальной игре наблюдает заметное опережение штатного
Screen-показа относительно нашего World. Автоматическая схема
`stock visible → World SHOWN → stock alpha=0` **неприемлема**:
в нормальном приближении к объекту возникнет краткая видимая
смена двух дизайнов. Простая готовность `World SHOWN` не
решает этот дефект. Нельзя обменивать его на заметное пустое
окно с обеими скрытыми подсказками. Точное время первых пикселей
не измерено; прошлые 57–68 мс — только интервалы логирования.

**Подготовлена надстройка наблюдения первого показа.** В журнале
прямой кисти SHOWN пришёл в том же проходе, что и первая привязка,
без выдержки Retainer. Из 60,25 мс SELECTION→SHOWN около 39,67 мс
занял private UI. Для возврата к той же цели убрана принудительная
раскладка при совпадении входов. Следующий гейт — измерить первые
пиксели Screen и World и локализовать затраты внутри private UI.
Игровая запись `6bfc676` показала Screen на 117 мс раньше полной
World-подсказки при холодном подходе и на один кадр записи (~16 мс)
при повторном подходе. Повторный путь использовал готовую раскладку.
Бесшовный первый кадр остаётся открытым.
[Покадровый результат](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md#игровой-результат-первого-показа).

## Подавление изображения TipHUD — этап A проверен на одном Open (2026-11-07)

**BLOCKED.** Tint корневого `UUserWidget` отделён от полей native readback,
но его стиль участвует и в захвате Retainer, из которого World получает
значок кнопки. Безопасность подавления и возврат штатного изображения
на границе кадра не доказаны. Поверх точного Selected-owner World подготовлено
ручное окно A для одного Open с проверкой RGBA и условным восстановлением.
В игре Screen и World-кнопка исчезли, World-текст и разделитель остались.
Журнал подтвердил два восстановления RGBA и смену устройства до записи.
Откат при закрытой игре вернул CompactLayoutProbe. Для B в закреплённых
UE4.27 и UE4SS не найдена доступная граница между захватом и экранной
отрисовкой. На этапе C один Open показал девять смен входной Texture2D
вместе с устройством. MID и RT сохранили идентичность внутри окна.
Кандидат с прямой кистью подтвердил смену World-значка под alpha=0
на одном Open без удержания, ручной возврат Screen и отсутствие
замеченного пользователем мерцания. CompactLayoutProbe восстановлен.
Remap, удержание и более широкий lifecycle остаются открыты.
[Аудит и игровой результат](../research/interaction-prompts-owner/world-space/tiphud-render-suppression/README.md).

## Selected-owner World — игровой прогон и откат (2026-11-07)

Точный source `2e167227e8b29c692fdd9157de06c5cf7ed4660f`, все 13 Lua и
локальная конфигурация сверены перед откатом. В журнале 34 создания
(Open 13, Take 6, Check 15), три показа повторно использовали прежний
компонент, все 37 показов завершились скрытием на NONE. Все 33 смены
владельца прошли через NONE и `CLEANED → RELEASED` до нового создания.
Шрифт и PNG подключились во всех 34 композициях. HOST recovery и
ошибки IIP не зарегистрированы.

От первого наблюдения выбранной цели до команды `SHOWN` прошло
57,5–68,0 мс при создании и 34,2–35,1 мс при повторном использовании.
Это время между отметками журнала, без замера пикселей, FPS и CPU/GPU.
После последнего скрытия зафиксирован EndPlay контроллера и штатный
выход. Последний скрытый компонент не получил `CLEANED/RELEASED` в логе.
Очистка на выходе остаётся UNKNOWN, прямой A→B не проверен.

SelectedOwnerWorldProbe отключён, CompactLayoutProbe восстановлен, все
12 файлов вместе с маркером проверены. Снимки журналов сохранены локально.
[Хэши и детали](VERIFIED_RUNTIME.md#selected-owner-world--bounded-runtime-2026-11-07).

## История: Selected-owner World — установка (2026-11-07)

По отдельному разрешению при закрытой игре установлен source
`2e167227e8b29c692fdd9157de06c5cf7ed4660f`. Все 13 Lua совпали с
манифестом по SHA-256. Проверены локальные конфигурация, шрифт и авторский
PNG. Единственный активный IIP-мод — SelectedOwnerWorldProbe. У
CompactLayoutProbe временно снят маркер, его 12 файлов вместе с маркером
сверены в резервной копии вне UE4SS. Остальные 252 проверенных файла
совпали с исходными хэшами. Откат при закрытой игре восстанавливает
прежний маркер и выключает новый. Игровой прогон ожидается.
[Сценарий](../research/interaction-prompts-owner/world-space/selected-owner-world/README.md#next-sufficient-runtime-check).

## Selected-owner World — исследовательский source-only кандидат (2026-11-07)

Штатный committed owner теперь ведёт отдельный World-координатор.
Снимки всех объектов и задержка на подтверждение полного реестра убраны.
Сохранены World-композиция и штатный видимый TipHUD. Точный исходный
коммит `2e167227e8b29c692fdd9157de06c5cf7ed4660f` прошёл локально 525
тестов в 48 наборах и [полный CI](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42375931783).
Кандидат готов к отдельному согласованию установки. Runtime-показ и
производительность остаются UNKNOWN.
[Исходники, манифест и границы](../research/interaction-prompts-owner/world-space/selected-owner-world/README.md).

## Выбранный владелец → быстрый World: следующий исследовательский этап (2026-11-07)

Реальный прогон [`4875f87`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/4875f87251e5abf2d1d59d7b636389139ccad593)
подтвердил `PlayerActionComponent+0x410` для Open/Take/Check: шесть
переходов через NONE согласованы с native TipHUD на первом следующем
проверенном кадре; `CompactLayoutProbe` восстановлен. Поэтому глобальная
выборка 34–48 объектов каждые 3 кадра **не нужна для выбора** в
следующем World-прототипе. Это решение об исследуемом механизме,
а не production acceptance, доказательство глобальной уникальности или
замер задержки/CPU.

**Следующий достаточный шаг, без установки:** подготовить отдельный
source-only successor на основе подтверждённого чтения committed owner,
привязать его к уже проверенному владению одним World-компонентом,
ресурсам и `CLEANED → RELEASED → BOUND` с проверкой нового owner и
только его native TipHUD. При `NONE`, `GAP`, EndPlay или смене карты —
скрытие/безопасное освобождение собственного World, без переписывания
штатной подсказки и без `FindAllOf`/полного реестра. Создание компонента
только из отдельного game-thread pump, не из callback.

Открытые гейты: стоимость одного выбранного чтения/кадр; быстрый
World SHOWN от *реального выбора*, а не только от snapshot; потеря
HOST-класса на повторном создании; прямой A→B и жизненный цикл;
самостоятельное безопасное подавление только штатной **отрисовки**
при сохранении native-состояния. Последний пункт — отдельный дизайн/
runtime gate: **не внедрён**. UI-композиция и принятые 17 значений
сохраняются; Screen S1 — лишь условная альтернатива.
[Основания и конкретный следующий эксперимент](RESEARCH_PLAN.md#selected-owner-driven-world--следующий-источниковый-кандидат-2026-11-07).

## Committed owner observer — игровой прогон завершён (2026-11-07)

На `e240150` подтверждены три показа и три скрытия Open/Take/Check через
`PlayerActionComponent+0x410`. Все шесть смен совпали со штатной видимостью
на первом проверенном кадре. Прямой A→B, замена игрового компонента и цена
чтения не проверены. CompactLayoutProbe восстановлен.
[Прогон и границы](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md#runtime-result--2026-11-07).

## История: Committed owner observer — установка (2026-11-07)

Установлена разрешённая ревизия `e240150161ecc6dea2d87cc35636842015bdaaed`.
Четыре Lua сверены, единственный активный IIP-мод — CommittedOwnerObserver.
CompactLayoutProbe временно отключён маркером, точный откат подготовлен.
[Хэши и границы](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md#verified-installation--2026-11-07).

## Committed owner observer — scan-free controller candidate, source-only (2026-11-07)

The `fdee186` installation remains blocked and **no game files were changed**.
The successor replaces global `UEHelpers.GetPlayerController()`/`FindAllOf`
with natural `PlayerController` `BeginPlayPost` capture, exact path/identity
re-resolution and EndPlay/map invalidation. No actor-array enumeration or
heuristic selection; if the event is missed, observation remains `GAP`.
Exact source/tests: [`df238c7`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/df238c7b30f666d13669bc5e31970fa2a0d0288a);
[CI 42372741024](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42372741024)
**515/515 PASS across 47 files (16 selected-owner tests)**.
Native controller event delivery, exact lookup cost and owner correlation
remain **UNKNOWN**. A **separate approval for revised source installation**
is still required.
[Revised source boundary](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md#candidate-controller-acquisition-without-global-enumeration--source-only-2026-11-07).

## Committed owner observer — установка заблокирована (2026-11-07)

Четыре Lua-файла `fdee186ac6b064c1dce50d09eccc550cb0ed34cc`, CI и хэши
игры/UE4SS сверены. Установленный `UEHelpers.GetPlayerController()` выполняет
глобальный `FindAllOf`, что нарушает ограничение прогона. Установку остановили
до переключения маркеров. CompactLayoutProbe остаётся активным.
[Проверка зависимости](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md#local-deployment-preflight--2026-11-07).

## Committed owner +0x410 — read-only observer source (2026-11-07)

Separate research-only `committed-owner-observer` now reads the
build-pinned `PlayerActionComponent` weak pair through exact reflected
component lookup and UE4SS custom `WeakObjectProperty`, and correlates
only selected Open/Take/Check transitions with independent stock TipHUD
readback. The observer and offline mocks are **source-only**: not installed
or run in the game. Exact source/test commit [`0c5ff3c`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/0c5ff3c7eb0a0b5ffa610af9aac29cdb0e88bb08),
[GitHub Actions run 42323045068](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42323045068):
**511/511 offline tests PASS across 47 files**, including **12 new selected-owner tests**.
These tests are Lua mocks, not real-game evidence; runtime owner correctness,
native show/hide timing, lifecycle, CPU cost and production acceptance remain
**UNKNOWN/BLOCKED**. Before deployment, obtain **separate user approval** for
closed-host installation and rollback.
[Exact recipe and limits](../research/interaction-prompts-owner/world-space/committed-owner-observer/README.md).

## Selected owner +0x410 — локальная статическая проверка (2026-11-07)

`GetActionTarget` читает отдельную weak-ссылку. Штатный поиск компонента
даёт `PlayerActionComponent`, где хранится committed owner. Для закреплённой
сборки есть статически обоснованный кандидат на чтение через custom
WeakObjectProperty. Надёжность в игре и стоимость остаются непроверенными.
[Native-трассировка и границы](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#selected-owner-read-seam--local-native-trace-2026-11-07).

## History: Selected owner +0x410 — UE4SS source audit (2026-11-07)

Pinned UE4SS `83330635` exposes reflected class members and
`RegisterCustomProperty` with a single-class offset, **not** a proved
pointer-chase/read of unreflected `character+0x560 -> state+0x410`.
The exact stock current prompt-owner weak pair is known from native
static evidence, but **no safe cheap Lua reader is established**.
The reflected `GameGlobal:GetActionTarget` native getter/setter remains
the one bounded local static discriminator: trace whether its actual body
reads the **committed** prompt owner, and whether the state is exposed as
a reflected class/struct. No runtime probe, installation or change of
game/mod files. If this does not provide a safe route, prioritize native
Screen S1 design without silently accepting loss of World occlusion.
[Scope, source references, exact next gate](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#selected-prompt-owner-read-seam--remote-source-only-audit-2026-11-07).

## ShowTipEvent — игровой прогон и откат (2026-11-07)

Точный hook зарегистрирован, но в завершённом пользовательском прогоне
наблюдатель не записал ни одного callback. Сопоставление с видимостью
не состоялось, причина отсутствия доставки не установлена. Наблюдатель
отключён, CompactLayoutProbe восстановлен с проверкой хэшей.
[Результат и границы](../research/interaction-prompts-owner/world-space/show-tip-event-observer/README.md#runtime-result--2026-11-07).

## История: ShowTipEvent — установка (2026-11-07)

Точный source `e4c8164093a7a8c5338e5bd30e6ec3a9debcd303` установлен при
закрытой игре отдельным UE4SS-модом `ImmersiveInteractionPromptsShowTipEventObserver`.
Все четыре Lua совпали по SHA-256. CompactLayoutProbe временно отключён
снятием маркера. Снимок и откат проверены вне загрузчика. Доставка
`ShowTipEvent` остаётся UNKNOWN до пользовательского запуска.
[Установка и протокол](../research/interaction-prompts-owner/world-space/show-tip-event-observer/README.md#verified-installation--2026-11-07).

## История: ShowTipEvent — read-only observer source candidate (2026-11-07)

Подготовлен автономный research-only наблюдатель: точный Lua hook на
`BaseGameEventObject:ShowTipEvent(bool)` после появления известного owner,
синхронное чтение actor/bool, независимый снимок штатной видимости только
событийного владельца. Для `BlueprintImplementableEvent` поддержка точного
script-hook и доставка callbacks остаются НЕПРОВЕРЕННЫМИ. Никакой установки,
запуска игры или изменений других модов. [Исходник и ограничения](../research/interaction-prompts-owner/world-space/show-tip-event-observer/README.md).

## Native show/hide — статическая цепочка найдена, 2026-11-07

Штатный update сравнивает текущего владельца подсказки с новым, вызывает
`ShowTipEvent(false/true)` на соответствующих объектах и напрямую вызывает
`ExtendedWidgetComponent:SetShow`. Доставка actor-event в Lua неизвестна.
[Цепочка и RVA](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#native-tiphud-show-and-hide--2026-11-07).

## Genesis interaction API inventory — 2026-11-07

Инвентаризация отражённых объявлений и Blueprint-метаданных не выявила
доказанного источника текущей цели. `GetActionTarget` остаётся общим getter
без связи с TipHUD. Для Open/Take/Check подтверждены конкретные шаблоны
зон взаимодействия. [Карта и следующий шаг](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#genesis-reflected-api-inventory--2026-11-07).

## GetLastInteractObject — native static rejection, 2026-11-06

Getter читает слабую ссылку на объект из веток выполнения взаимодействия,
включая отправку Fail. Штатный End очищает отдельный слот Doing и оставляет
Last. Getter отклонён как источник цели TipHUD до нажатия. Штатный источник
текущего выбора остаётся неизвестным.
[Native-цепочка и RVA](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#native-getlastinteractobject--2026-11-06).

## History: Current selected target — local static result, 2026-11-06

В локальных Blueprint-экспортах и UHT найдены два отражённых getter объекта
и `ShowTipEvent(bool)`. Связь с финальным выбором штатной подсказки
не установлена. Граница проходит через native Genesis: обновление
состояния взаимодействия, показ компонента и родительский `CanShow`.
[Статическая цепочка и один следующий шаг](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md#local-static-follow-up--2026-11-06).

## History: Current selected target seam — existing-evidence audit, 2026-11-06

**NO_ESTABLISHED_AUTHORITATIVE_SELECTED_OWNER / CANSHOW_INDEXED_CANDIDATE_RUNTIME_PASS / WORLD_PROMOTION_BLOCKED.**

Source/runtime reports and current Lua adapters were reviewed at `d5e6def`.
The 528 matched CanShow callbacks and six one-frame sampled shows prove a fast
candidate signal, **not** the native final selected actor or all-frame exclusivity.
Neither the existing BeginPlay chain, ExtendedWidget visibility, SetShow, nor
SetupTipMessage2 is a demonstrated authoritative selector. A 60-frame sparse
audit cannot certify intervening states. No game or local-only host exports were
inspected in this source-only review.
[Exact mechanism comparison and minimum static gap](../research/interaction-prompts-owner/world-space/event-driven/TARGET_AUTHORITY_STUDY.md).

**Next sufficient source step:** examine a *single native TipHUD* Screen S1
composition/one-prompt ownership design using already observed child primitives.
S1 would inherit host selection/show/hide but sacrifice Hilda's depth occlusion;
it is still a conditional fallback requiring visual approval, not an adopted
production implementation. If preserving true World occlusion is essential,
a narrowly bounded local static final-writer trace is necessary before any
further World selector test. Native suppression, resource lifecycle and actual
frame-time remain independent BLOCKED gates. No code or installation changed.


## Event correlation observer — игровой прогон и откат, 2026-11-06

Шесть показов Open/Take/Check с возвратами подтверждены через один кадр
наблюдателя после последнего `CanShow`. Все 528 записанных callback
сопоставлены с индексированными владельцами. Глобальная эксклюзивность
и стоимость остаются UNKNOWN. Штатная подсказка видима. Наблюдатель
отключён, CompactLayoutProbe восстановлен и проверен.
[Игровой результат](../research/interaction-prompts-owner/world-space/event-driven/PROBE.md#runtime-result--2026-11-06).

## История: Event correlation observer — source-only CI PASS, 2026-11-06

**READ_ONLY_OBSERVER_AND_ENTRYPOINT_OFFLINE_PASS / CANSHOW_TO_VISIBLE_GAME_EDGE_UNKNOWN /
NATIVE_EXCLUSIVITY_UNKNOWN / NOT_INSTALLED / PRODUCTION_BLOCKED.**

An independent `research/event-correlation-probe` branch now contains the
standalone, four-file, read-only `event-driven/Scripts` recipe.
It uses the already proven Open/Take/Check BeginPlay owner chain,
lazy exact `TipHUD_C:CanShow` Blueprint post-hook and indexed
widget→owner candidates. It reads at most one queued event candidate
plus one active owner per frame; a separately labelled 60-frame
**diagnostic** full-owner audit (max 48) detects missing events,
ambiguity and incomplete native snapshots. It does **not** select
a production target, create World UI, hide/alter native TipHUD,
replace CanShow, force-load host assets or change saves/settings.

**Exact tested source/test commit:** [`f03c571`](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/f03c571f8fba9c88994a00f56daaa0ad54d95355).
[CI 42219818296](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42219818296):
**488 Python/Lua tests in 44 files PASS**, including 12 correlation
and 3 entrypoint tests. Strict mock/offline only: event delivery and
order on real Take/Check, authoritative selected target, actual
frame-time/FPS cost and source visual suppression all remain UNKNOWN.
Existing `auto-world-successor`, installed CompactLayoutProbe,
`main`, VERSION and active game were not changed.

**Next sufficient gate:** separately authorized, closed-host, user-started
local Codex installation of the exact research source and natural
Open→leave→Take→leave→Check→leave→return run, logging event-to-visible
frames and an independent frametime/perception check. Restore existing
installed probe with verified closed-host rollback. If event coverage or
exclusive target cannot be proven cheaply, examine native TipHUD
Screen-child S1 instead of increasing global native polling. Even
positive event results leave the independent single-visible-prompt
suppression/restore gate and World resource lifecycle unaccepted.
[Probe source, boundaries and test recipe](../research/interaction-prompts-owner/world-space/event-driven/PROBE.md).

## One visible prompt — requirement confirmed, implementation BLOCKED

The user requires the final UI to **visually replace** the default
interaction prompt: one presentation only for Open/Take/Check, never
simultaneous separate native Screen and own World/Screen prompts.
The stock TipHUD's selection/CanShow, action localization, input
hint/remapping, native show/hide and interaction behavior **must still
work**. [Source-grounded rendering/signal distinction](../research/interaction-prompts-owner/world-space/event-driven/README.md#5a-native-screen-suppression-must-preserve-event-evidence).

Current `IIPOpenVisibility.visible` explicitly checks the original
TipHUD/TextBlock/Retainer/icon `Visibility` and `RenderOpacity`.
Making any of these Hidden/transparent would cause the **current
observer to miss the native visible state**. Whether such writes
also interfere with native CanShow/other host logic is UNKNOWN;
do not blindly change them. World visual-only suppression has
not been proved. Screen S1 may instead recompose one native
TipHUD using its original localized lower row/hint and private
upper/divider; prior additive child tests do not prove full
replacement. The next read-only diagnostic intentionally leaves
stock visuals shown as a control; the *later* integration must
pass a separate no-duplicate + safe restoration runtime gate.

## Native event fast-path — source review, 2026-11-06

**CANSHOW_SCRIPT_CALLBACK_RUNTIME_PASS /
NATIVE_CURRENT_TARGET_EVENT_UNKNOWN /
NO_NEW_RUNTIME_PROBE / PRODUCTION_BLOCKED.**

Source-only [event selection and 2D fallback study](../research/interaction-prompts-owner/world-space/event-driven/README.md)
reused existing exact runtime evidence: `TipHUD_C:CanShow`
is an actually firing read-only Blueprint callback (948 calls
on 3 TipHUD widgets in its prior test); a separate BeginPlay/CanShow
join mapped one native visible Open to a verified
actor/ExtendedWidget/TipHUD chain. Normal-load multi-action
BeginPlay recorded **34** distinct ready Open/Take/Check owners.
This supports a cheap **indexed widget→owner candidate signal**,
not the conclusion that a CanShow call equals the engine's
authoritative current selected target, show or hide edge. A
previous native `ExtendedWidgetComponent:SetShow` hook returned
**zero callbacks** in its 31.965 s test. `SetupTipMessage2`
native-array hook remains blocked by missing pinned ABI/frame
provenance. Do not invent another native event or use global
ProcessEvent/SetVisibility hooks to bypass evidence gates.

Potential design: read owner identities once at native BeginPlay;
on exact CanShow callback use one primitive widget lookup,
then validate at most one candidate on game thread. A
single-active visibility read can handle loss of focus. BUT
**complete coverage, hide timing, one-visible global exclusivity,
callback cost and event→native show ordering are NOT TESTED**.
Without reliable global target selection, an event cannot
authorize new World rendering. The 3-frame 34-owner survey is
**not the adopted production path**; its CPU cost remains unknown.

The user's primary UX constraint now explicitly prioritizes
sub-100-ms-feeling appearance, negligible rendering/CPU impact
and no frame spikes. Preferred World depth remains conditional;
an **intentional Screen-space presentation is an agreed
fallback to examine, not an already selected replacement**.
The already game-tested original TipHUD child/Aphes/divider
primitives offer an S1 variant inheriting native visibility and
input without extra target polling; separate HUD-root Canvas
was also visually tested at 50%/78%, but still needs target
synchronization. Neither variant has automatic production
acceptance.

**Next sufficient evidence:** a separately authored,
non-installable until authorized **read-only event correlation
probe** observing exact CanShow callbacks for Open/Take/Check,
per-widget native show/hide timing and a slow explicitly
diagnostic full-sweep truth audit. Compare event-to-visible
frames, missing or spurious signals, ambiguity and measured
game frame-time before any event-based World bind.
If event coverage fails, prioritize the proven native TipHUD
Screen-child S1 architecture over faster brute-force scanning.
The exact 17-file `auto-world-successor` SHA-256 candidate,
`research/automatic-world-session` and frozen runtime source
remain unchanged; no installed game files were modified here.

## История: AutoWorld successor — source-only PASS, 2026-11-06

**EXACT_HOST_RECOVERY_AND_FAST_OBSERVER_OFFLINE_PASS /
NOT_INSTALLED / REAL_WORLD_RETRY_AND_FRAME_TIME_UNKNOWN /
PRODUCTION_BLOCKED.**

Separate branch `research/auto-world-residency-latency` forks **all 17**
source files of the immutable runtime-tested, failed
`auto-world/` candidate `be1827d`. The original candidate and installed
CompactLayoutProbe are unchanged.

**Architecture re-evaluation after failed native acceptance:** retain
sequential **actor-owned** World components with proven
`CLEANED → RELEASED → fresh unique owner → BOUND`.
Do **not** repurpose/reparent a component from actor A onto actor B
without a verified native ownership lifecycle. At a clean new create
boundary, if the exact previously live World host class is missing
(`ABSENT_NIL`/`ABSENT_NULL`), the successor attempts **one**
`LoadAsset` call on the verified game-thread callback and validates
returned class, fresh path/address and `UserWidget` ancestry.
No GC-root/fallback/loop; failures remain terminal. The first-game
disappearance cause including GC remains **UNKNOWN**.

**Responsiveness trial:** native read-only complete owner sampling
interval reduced from **30 to 3 frames**, retaining the
**48 records per call** bound, two stable complete unique snapshots
and the one-frame World rendering pump. This is about **10× more**
sampling work per second at a given FPS: real frame-time cost
and user responsiveness still require a game run. No artificial
time/event cap, no takeover of original TipHUD, no alteration of
localization, native hint, input semantics or 17 visual defaults.

[CI 42209313867](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42209313867)
at code/test commit `d48ca6032ab75dec29eec16be4c7a6a741930ac2`
**473 offline tests / 42 suites PASS**.
This includes the real new Lua World module at the fourth attempt
with simulated exact `ABSENT_NULL`, rejected wrong/absent assets,
the accelerated normal-load entrypoint, A→B lifecycle and error
containment. The 17-file SHA-256
[`SOURCE_MANIFEST.json`](../research/interaction-prompts-owner/world-space/auto-world-successor/SOURCE_MANIFEST.json)
is independently checked in CI.
[Exact rationale, constraints and next gate](../research/interaction-prompts-owner/world-space/auto-world-successor/README.md).

**Next sufficient step:** after fresh explicit user approval,
user-started local Codex performs a closed-game, hash-verified,
rollback-safe installed trial. User operates the game through the
previous Take→Check (fourth host) failure path and additional
rebinds, judges perceived responsiveness **and frame-time/FPS
impact**, then exits normally; logs and hashes determine PASS/FAIL.
No runtime claims from offline CI and no promotion to `main` yet.
No game, installed mod, saves, config, release artifact or other
NikichMods project was modified by this GitHub-only work.

## История: AutoWorld — игровой результат и откат, 2026-11-06

Open → Check → Take отрисовались, Open пережил отход и возврат. Лог подтвердил
освобождение старого компонента до следующего создания. При повторном Check
класс World-хоста оказался `ABSENT_NULL` на четвёртом создании. Диагностика
завершилась через `stopped_clean`. Причина исчезновения класса неизвестна.
Вид трёх подсказок пользователю приемлем, задержка неприемлема для финальной
версии. AutoWorld отключён, CompactLayoutProbe восстановлен и проверен.
[Точные события, хэши и матрица](../research/interaction-prompts-owner/world-space/auto-world/README.md#runtime-result--2026-11-06).

## История: Auto World source integration — offline PASS, 2026-11-06

**SOURCE_AND_CI_PASS / NOT_INSTALLED / REAL_GAME_WORLD_HANDOFF_UNKNOWN.**
The branch `research/automatic-world-session` contains a complete,
separately named source-only candidate. It joins Open/Take/Check
observation, native owner revalidation, handoff state machine and
reusable four-element World rendering.

[CI 42133071798](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42133071798)
passed **446 tests in 38 suites** at
`5af99f7f6710eb81ab838d6fa0d6a9a6c500e373`.
Seventeen co-located Lua scripts have an exact SHA-256
[`SOURCE_MANIFEST.json`](../research/interaction-prompts-owner/world-space/auto-world/SOURCE_MANIFEST.json),
checked independently in CI. Last Lua edit:
`1bf1cd2cb0b8a17a739d9de8a5cb2b23e9445ae5`.

Two engine-thread loops run independently: native read-only 30-frame
observation and own World UI 1-frame pump. Owner changes require
confirmed cleanup and fresh complete native snapshots. Incomplete
or ambiguous observations cannot bind a target. No automatic editor,
manual arm, arbitrary lifetime timer or event caps. Original
Screen TipHUD, localized action and button hints are preserved.

**Not accepted in UE4:** repeated native component creation,
real resource import/GC, real A-to-B World ownership, direct A-to-B
without withdrawal, in-game presentation and end-user UX.
Technical upper labels are not verified Aphes-world translations.
The user-owned `IIPLiveConfig.lua` and local authored resources
remain external. The already installed CompactLayoutProbe, frozen
sources, `main`, `VERSION`, game, saves and settings are unchanged.

**Next gate:** separate explicit authorization for local Codex
closed-host install/rollback and normal user-operated Open, Take,
Check runtime and visual test. See
[full candidate notes](../research/interaction-prompts-owner/world-space/auto-world/README.md).
Offline tests are not production or real-game acceptance.

## История: Reentrant World renderer source-only — OFFLINE PASS, 2026-11-06

**REPEATED_OWN_COMPONENT_TESTS_PASS / ENTRYPOINT_NOT_INTEGRATED /
NOT_INSTALLED / RUNTIME_A_TO_B_UNKNOWN.** The new isolated
`research/world-renderer-reuse` fork reuses the approved compact
four-element World composition and all 17 accepted defaults.
`IIPWorldRenderer.lua` satisfies the existing ownership controller
renderer API; the unfrozen `IIPWorldChild.lua` exposes native
hide/resume/refresh and allows sequential allocation only after
confirmed own-child, WorldComponent, host and ornament lease cleanup.
The private component/font names are unique within the Lua session,
and normal interaction does not open the calibration editor.

**CI PASS:** [42130699221](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42130699221)
on source/test SHA `49632960719808bcc2673cb81af5b0f3f23bf464`,
**430 tests /35 scripts**. Tested the real forked WorldChild,
Composition, HintSource and Tuning under native host mocks,
including sequential World components and an interrupted cleanup.
The mock importer does not prove real UE4 resource re-import/GC or
actual A→B World ownership/visual acceptance.

**Next source gate:** new automatic main.lua tying together
`IIPInteractionSource`, read-only event observer
`IIPInteractionEvents` from `owner-handoff`,
`IIPWorldHandoffBridge`, `IIPWorldHandoff` and this
`IIPWorldRenderer`, with verified game-thread resolving and pump,
fail-closed cleanup and offline end-to-end tests.
No integrated installable candidate, hash manifest or game acceptance
yet. Source-only technical status and remaining proof boundary:
[World reuse research](../research/interaction-prompts-owner/world-space/world-reuse/README.md).
Frozen previous packages and the restored CompactLayoutProbe
were not modified. No game launch, install or settings/save change.

## World owner handoff source-only — CI PASS, 2026-11-06

**PURE_LUA_HANDOFF_AND_EVENT_GLUE_PASS / REAL_REENTRANT_WORLD_BLOCKED /
NOT_INSTALLED / PRODUCTION_BLOCKED.**
New independent `research/world-owner-handoff` from
`research/multi-action-observer` `d0d72b07d9dd1b3fe390fc311966840544865aa1`.

[`IIPWorldHandoff.lua`](../research/interaction-prompts-owner/world-space/owner-handoff/IIPWorldHandoff.lua)
implements single-owner retain/hide/resume and
`hide → cleanup → independently confirmed empty → CLEANED → RELEASED(ticket)`
before another owner can bind. It requires **two fresh complete
unique-native-visible snapshots after release**. An incomplete/
ambiguous sweep never selects a target. Partial creation, EndPlay/map,
bad identity and cleanup failures cannot grant overlapping World
allocations. Cleanup failure blocks the session; explicit retry
does not silently resume automation. No arbitrary timer/event count.
The forked read-only event adapter and bridge pass **primitive owner
facts** into the pure coordinator; no native writes occur in hooks.
A renderer must still be injected and pumped from a separately
verified game-thread boundary.

[CI 42126709589](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42126709589)
at code/test SHA `bff0d3cb5e023e8c97b7d577404f5e380f64b923`:
**422 offline tests /33 files PASS** (19 new handoff/bridge tests).
This is Lua state-machine/mock acceptance **only**, not native UE4
allocation, render, GC or automatic A→B acceptance.

**Native next gate:** the frozen `compact-layout` source is
**one-shot**: `IIPResources` refuses a second ornament import;
World/module initialization is one-time; `os.time()`-based component/
font names may collide within a second; `create` automatically opens
the tuning editor. Safe repeated native World allocations and resource
lifetimes require a separate source-only renderer successor and game
validation, not reuse of the frozen source by simply calling `create`
again. [Source evidence and exact boundary](../research/interaction-prompts-owner/world-space/owner-handoff/README.md).
Old CompactLayoutProbe remains the restored active installed
IIP research candidate. No source `main`/`VERSION`, game files,
activation markers or other mods were changed by ChatGPT.

## История: перед source-only World handoff — MultiActionProbe PASS

Игровой прогон `1780f0a` закрыл обнаружение и EndPlay для трёх
семейств `Open/Take/Check`. Следующий шаг — **source-only**
интеграция однозначного наблюдаемого владельца с собственным World
компонентом: hide/resume для прежнего владельца, а для нового
`release → подтверждённый CLEANED → fresh snapshot → bind`.
Повторный A→B World lifecycle **не проверен в игре**; прямой переход
без выхода из зоны и authoritative selected-target **UNKNOWN**.
Новый runtime-кандидат не устанавливался, замороженный
CompactLayoutProbe/остальные моды не изменялись.
[Точный план и safety gate](RESEARCH_PLAN.md#после-multiactionprobe-runtime-pass--следующий-source-only-world-lifecycle-gate-2026-11-06).

## MultiActionProbe — результат прогона 2026-11-06

`1780f0a` автоматически обнаружил 34 готовых владельца Open/Take/Check.
Пять эпизодов видимости сменили три разных ID через отход. Последний
сообщённый эпизод «Открыть» остался без отдельной записи. EndPlay удалил
34 записи, включая 33 при штатном выходе. CompactLayoutProbe восстановлен.
[Доказательства, хэши и границы](../research/interaction-prompts-owner/world-space/multi-action/README.md#runtime-result--2026-11-06).

## История: MultiActionProbe был установлен, затем отключён

Пользователь разрешил установку `1780f0a` и временное переключение маркера
CompactLayoutProbe. При закрытой игре сверены четыре Lua-файла и новый маркер.
Сохранены хэши 181 существующего файла. Этот этап ожидал пользовательского прогона; прогон завершён 2026-11-06
и исходный CompactLayoutProbe восстановлен, см. текущий статус выше.
[Манифест и границы](../research/interaction-prompts-owner/world-space/multi-action/README.md#local-payload-preparation).

## История: multi-action observer — ChatGPT source + CI, 2026-11-05

**ИСТОРИЧЕСКОЕ SOURCE-ONLY СОСТОЯНИЕ ДО ПРОГОНА** (ныне Take/Check подтверждены в настоящей игре, см. верхний runtime-раздел).
Source developed in `research/multi-action-observer` from
`research/auto-open-events` `74ec3a4247feed0be9c8bf8788f5839c6cad20ae`.
[Independent research candidate and boundaries](../research/interaction-prompts-owner/world-space/multi-action/README.md).
The earlier game run established normal-load `Open` detection:
six ready native Open actor/component/TipHUD owners and two
same-owner shown/hidden episodes. `Take`/`Check` remain **static BP
contract only**, not new live acceptance. Bonfires, arbitrary Interact
and Ladder/Descend are excluded.

New source: read-only `IIPInteractionSource.lua` supports exact
`Open`/`Take`/`Check` tags and native localized text,
`IIPInteractionEvents.lua` observes these owners across
BeginPlayPost/EndPlayPre/LoadMapPre; a new standalone `main.lua`
registers the global hooks. Native visibility reader is copied
unchanged. No World UI, actor/game/control/save/settings writes,
CanShow return override, or policy bind/release commands.

**No session-time deadline, total BeginPlay/sample count or hard
eight-actor cap.** Each 30-frame observation checks at most48
known candidates; when the full owner set cannot be observed in one
callback, it explicitly logs `incomplete_snapshot` and makes **no
unique-owner claim**. Unexpected identity contradictions still
stop safely. Logs are change-oriented, with owner details and native
localized action captured on first actual visibility. This follows
the adopted no-timer decision in `docs/REQUIREMENTS.md` and
updated DevRules.

**CI:** [run42069984702](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42069984702)
at source+tests `1780f0a8230149135b61bafcdb81c61e2f1d4e36`
(**403 offline tests /31 test scripts PASS**, including18 new
multi-action/entrypoint scenarios). Later source-independent
documentation edits do not change this code evidence.

**Next gate:** separately approved user-started local installation
of a new exact, hash-guarded read-only candidate to establish
`Take`/`Check` ready/visible behavior and different-owner
Open↔Take↔Check focus in natural gameplay. The previous
AutoOpenEventsProbe was disabled and the accepted
CompactLayoutProbe restored after Codex's closed-host rollback;
**no installed file or activation marker changed** in this
GitHub-only source step. Reusable World component teardown,
rebind and native Screen UX remain independent production
blockers; `main`/`VERSION` stable branch unchanged.

## Auto Open observer — результат одного прогона

Source `db89283` автоматически обнаружил шесть владельцев Open при обычной
загрузке. Все шесть TipHUD готовы в BeginPlayPost. Дважды виден только владелец
№1, после каждого эпизода видимых Open-владельцев ноль. Межобъектный A→B остаётся
UNKNOWN. LoadMapPre и EndPlayPre пришли, удаление уже зарегистрированного
владельца в этом сеансе не наблюдалось. Лимит остановил цикл с подтверждённой
отменой. После архивирования восстановлен CompactLayoutProbe.
[Точный результат и границы](../research/interaction-prompts-owner/world-space/auto-target/README.md#normal-load-runtime-result--2026-11-05).

## История: локальная подготовка Auto Open observer (закрыта)

Проверен установленный UE4SS. Подготовлена отдельная пятифайловая диагностика
с идентификаторами владельцев и логом видимого, скрытого и ожидающего набора.
Локально прошли 385 тестов в 29 файлах. Пользователь разрешил установку source
`db89283747f2e25c206b1fc762b68aeabdbcb771` и переключение маркера.
Пять Lua-файлов и маркер проверены по SHA-256 после установки при закрытой игре.
Сохранены хэши 175 существующих файлов. На этапе установки был активен AutoOpenEventsProbe; после прогона он отключён, CompactLayoutProbe восстановлен.
Игровые A/B и lifecycle результаты ожидают одного пользовательского прогона.
[Точный payload и сценарий](../research/interaction-prompts-owner/world-space/auto-target/README.md#local-runtime-candidate).

## Auto Open lifecycle — event observer source + CI PASS, 2026-11-05

**AUTOMATIC_READ_ONLY_OBSERVER_READY_SOURCE / NOT_INSTALLED / PRODUCTION_BLOCKED.**
Branch `research/auto-open-events` based on
`research/auto-open-target-policy` `f5c7e4d89519f9d1e088e90506cf23e337e7da78`.
[Owner/selection/event observer](../research/interaction-prompts-owner/world-space/auto-target/README.md#automatic-ue4ss-lifecycle-observer--source-only-2026-11-05)
now uses global `RegisterBeginPlayPostHook` and `RegisterEndPlayPreHook`
to discover/remove native Open actor identities automatically, plus
`RegisterLoadMapPreHook` for map-boundary reset, *all read-only*.
A bounded 30-frame loop rechecks at most8 previously observed Open
identities, including pending post-BeginPlay widget initialization.
No manual F11 arm, native CanShow return guess, global actor scan,
native action/TipHUD write, World creation or synthetic release ack.

**Source/test identity:** commit
`eb251161d067482fca362f0a418eb736a449f491`;
[CI run42003357042](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/42003357042)
executed `python tools/test.py`: **385 tests /29 test scripts PASS**,
including12 event-lifecycle and3 standalone visibility/entrypoint cases.
This proves offline Lua policy/wiring against mocks, **not** global hook
delivery, actual Asterigos actor selection, endplay/map ordering, native
performance, visual output or installed runtime. Docs-only subsequent commits
do not retroactively change the tested source. The accepted frozen compact
World source and its actual user-run proof remain separate and unchanged.

**Remaining decisive gate:** a separately authorized, one-session
user-started local Codex **read-only** observer installation/test with
known Open A→B→none, exact component/widget IDs, pending/ready transitions,
native visibility and endplay/map events; confirm actual single-current-target
semantics, not merely callback frequency. Until then no multi-object World
binding, original TipHUD suppression or production release. Installed research
marker is not touched by these GitHub edits. A separate static/runtime gate
must establish repeatable World resource lifecycle before enabling retargeting.
Current `main`/`VERSION`, game, other mods, settings and saves unchanged.
No new game-level runtime fact to promote to Asterigos-Research.

## Auto Open-target policy — ChatGPT-only offline implementation, 2026-11-05

**OFFLINE_POLICY_AND_OPEN_ADAPTER_PASS / RUNTIME_NOT_TESTED / PRODUCTION_BLOCKED.**
[Research source, exact seams and missing runtime proof](../research/interaction-prompts-owner/world-space/auto-target/README.md).
New `research/auto-open-target-policy` branch from the audited
`7438fa763859457f7897f9d3e8452b0ddc870c51`. ChatGPT authored two
**new**, separate Lua modules: `IIPTargetPolicy.lua` (complete-snapshot
candidate arbitration, fail-closed identity guards, EndPlay/world invalidation,
atomic release-ack→bind handover) and `IIPOpenSource.lua` (read-only exact
Open actor↔component↔TipHUD acquisition and fresh native screen/hint/action
readback). The frozen compact World prototype, its configuration/manifest and
installed marker are untouched. These new modules are **not wired** into
the research main/renderer and are **not** a runnable/installed mod.

**Automated evidence:** GitHub Actions
[run41937982403](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/41937982403)
from exact code+combined-test commit
`97283bb6ebe4a1bf8a2d8ceb37adeb125b7cd27e`:
Python3.12 + lupa2.8, `python tools/test.py`, **370 tests/27 scripts PASS**,
including 25 new policy/adapter tests (15 selector + 10 adapter,
including one combined handover case). This is a tested Lua policy, **not** a game/UE4SS render or
target-switch acceptance.

**Decisive missing runtime facts:** whether effective native source/widget
visibility uniquely identifies the actively selected world interaction when
two nearby actors qualify; whether global BeginPlayPost reports the supported
Open actors after their widget is ready (or needs a bounded readiness event);
and EndPlay/map teardown delivery. Pinned UE4SS event APIs exist, but are not
yet wired/game-proven. Do not guess target from the last CanShow call.
Existing single-creation World renderer/resource lifecycle would need an
independently verified repeatable teardown/rebind route.

**Next:** ChatGPT-owned minimal read-only event/visibility integration design
and offline verification; only request one user-started local Codex probe if a
specific indispensable selection/initialization property cannot be established
from existing records/source. No production/vanilla Screen suppression or
runtime installation authorized. `main`/`VERSION`, native game and other mods
unchanged; slight glow and optional overall scale remain deferred.

## Production readiness — source/evidence audit, 2026-11-05

**REMOTE_SOURCE_AUDIT_COMPLETE / RESEARCH_PASS / PRODUCTION_BLOCKED.** This is
a source-and-repository audit, not new installed-runtime proof or approval to
install. Evidence baseline: research/compact-world-layout HEAD
`8e5ddda598857404e638626ebce1ca09b166038f`, frozen tested
source `2981375afadb968fb272eeab33aab8d384e639ef`, its [run and limits](../research/interaction-prompts-owner/world-space/compact-layout/README.md#user-run--compact-spacing-hide-resume-and-manual-stop-pass-2026-11-05),
current REQUIREMENTS and shared Asterigos-Research index. No code, game,
installed files, versions, third-party resources or main branch changed.

**Verified on the narrow tested path:** one own World WidgetComponent/vertical
frame-Yaw, natural Hilda occlusion, one native localized action and borrowed
current input-hint source, authored PNG, bounded compact layout with rollback,
same-object hide/resume, explicit manual STOP/cleanup. Reported offline
345 tests/25 suites PASS for the frozen source. Neither that suite count nor
logged yaw writes is a production/performance/other-action acceptance.

**Current-contract blockers (evidenced by exact current source):**

1. `compact-layout/Scripts/main.lua`: Ctrl+Alt+F11 arms the research hook,
   `reload_manually_once=true`; no automatic ordinary-play activation.
   `relations()` requires `msgTag=Open` and `ActionName=25`; candidate acquisition
   filters the same Open tag. Once matched it commits to one actor/widget and
   `automatic_retarget=false`. No general target handover or re-arm path.
2. `IIPComposition.lua` initializes upper font text to literal technical `OPEN`
   and refreshes lower text from stock `TextBlock_89`. There is no accepted
   per-action upper-glyph mapping or validated Take/Read/Descend producer chain.
   The technical upper text is not a verified Aphes-language translation.
3. One same-target hide/resume and manual cleanup passed; focus changes to
   different actors, map travel, shutdown/reinitialization, input mode changes
   and wider visibility/progression states have no accepted end-to-end contract.
   Guarded fail-closed behavior is useful but not automatic continuity.
4. Original Screen TipHUD intentionally remains visible throughout research;
   final duplicate-prompt presentation/vanilla fallback policy is unresolved.
   Do not hide or modify the host UI without an agreed UX and verified reversible
   mechanism.
5. Installable distribution is not prepared: research-only Lua and temporary
   editor/probe entry, private absolute-path IIPLiveConfig, game-derived Aphes.ttf
   excluded from public artifacts by LICENSING. Need a lawful user-side resource
   resolution/install/disable/rollback mechanism and tested packaging before release.
6. Acceptance still needs representative interaction families, RU and another
   available locale, keyboard/controller and switching/remap, target loss/return,
   long localized strings, resolution/readability and host/other-mod invariants.
   Exact supported envelope to be accepted explicitly. No `.github/workflows`
   present in this research tree; offline tests exist but hosted CI/status is
   not claimed.

**Not current blockers by themselves:** accepted slight glow (color correction
DEFERRED), optional overall scale, unknown host builds without a support claim,
theoretical compatibility machinery, unrelated gameplay mods and re-running
completed A/B or manual STOP tests.

**Next sufficient action:** ChatGPT-owned *source-only* integration design,
starting with current target acquisition/automatic re-targeting and verified
native owner/visibility seams, consulting [RESEARCH_PLAN](RESEARCH_PLAN.md#production-transition--next-bounded-slice-2026-11-05).
Do not build a generalized scanning framework or new local probe before
reusing accepted evidence. Codex only for an essential installed-host check.
Research source, installed marker, defaults and `main` unchanged; no production
release authorized.

**2026-11-05 — compact-layout: сближение, hide/resume и NumMultiply STOP PASS.**
[Source2981375, точный лог/метрики и границы](../research/interaction-prompts-owner/world-space/compact-layout/README.md#user-run--compact-spacing-hide-resume-and-manual-stop-pass-2026-11-05).
Все12 installed hashes совпали;130 layout,97 из них gap0/Y−6, один корректный
overlap rejection с восстановлением. HIDDEN→RESUMING→SHOWN на том же компоненте,
последние17 значений сохранены. LOOP_CANCELLED→STOP reason=user/hooks0→RELEASED→
COMPONENT_DESTROYED→CLEANED, без FAILED/CLEANUP_PENDING. Последний Num9
[закреплён как актуальная будущая база](REQUIREMENTS.md#актуальная-база-после-compact-layout-прогона--2026-11-05):
tracking350, gap0, dividerY−6/thickness1.25, hintGap10, brightness.6/.5/.5/.5,
остальные значения в таблице. Новый код/установка не выполнялись, marker/config/
payload прежние; host закрыт. Финальная визуальная приёмка/production не следуют
автоматически; общий масштаб и цветовая коррекция не открываются этим результатом.

**2026-11-05 — compact-layout INSTALLED, RUNTIME_PENDING.**
Source `2981375afadb968fb272eeab33aab8d384e639ef`
[установлен после пользовательской поправки](../research/interaction-prompts-owner/world-space/compact-layout/README.md#authorized-installation--2026-11-05).
12 installed hashes проверены; включён только CompactLayoutProbe,22 прежние
IIP-пробы отключены. У старого51b9f26 изменён только activation marker: Lua/PNG/
private config/source/manifest сохранены.115 других mod/loader/log и46 config/
save файлов хэш-сохранены, внешний rollback подготовлен; игра закрыта и не
запускалась/не завершалась агентом. Далее один пользовательский Open/run для
gap0/divider_y ниже−2, реального overlap rejection, hide/show, Num9 и NumMultiply.
345/25 offline PASS не заменяют игровой приёмки; VERSION/main прежние.

**2026-11-05 — compact-layout READY_SOURCE, NOT_INSTALLED.**
[Кандидат, evidence-gate, manifest и один будущий run](../research/interaction-prompts-owner/world-space/compact-layout/README.md).
Ветка research/compact-world-layout от f2bc83d; source51b9f26/его установка
сохранены.17 новых source-defaults взяты из принятого Num9. Guarded alpha7–25/32
вместо полного PNG при проверке расстояний; full native TextBlock metrics без
двойного outline. gap0 и divider_y−3 теперь допустимы, реальные overlap/bounds
по-прежнему отвергаются с rollback; широкая верхняя строка проверяется против
кнопки. Full offline345/25 PASS,12 новых случаев. Масштаб отложен, цветовое
логирование завершённого эксперимента удалено из нового преемника; ни цвет,
ни World-поза не менялись. Пользователь разрешил последующую установку сразу
после подготовки; игровой render/новая компактность ещё не приняты.

**2026-11-05 — visual glow acceptable / color correction DEFERRED; next: compact layout.**
[Принятое решение и границы следующего кандидата](REQUIREMENTS.md#визуальная-допустимость-свечения-и-приоритет-компактности--решение-2026-11-05).
Текущий World-space вид со слабым свечением пользователь считает визуально
допустимым; корневая причина блеклости/ореола неизвестна, эффект не объявлен
намеренным. Не тратить сейчас дополнительные циклы Codex на gamma/sRGB/материалы/
постобработку. Следующий source-only research successor — сблизить вертикальные
строки и разделитель с учетом прозрачных полей PNG256×32 и реальных видимых
границ, сохранить проверку пересечений и rollback; взять принятые17 NumPad9
значений из REQUIREMENTS. Общий масштаб — лишь при простом и доказанном
механизме, иначе отложить. Source51b9f26, существующая установка, manifest,
VERSION/main и прочие моды без изменений; production BLOCKED. Новая ветка/
кандидат/установка в этом статусном решении ещё не созданы.

**2026-11-05 — diagnostic snapshot и явный NumMultiply STOP PASS.**
[Сеанс source51b9f26, поля снимка, точный лог и границы](../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md#user-run--snapshot-and-manual-stop-pass-2026-11-05).
13 installed hashes совпали; снимок один,4 scope, complete=true. Own1024×512:
sRGB=true/TargetGamma0/force-linear=false/format6/override2; native51×51:
sRGB=false/TargetGamma1/force-linear=false/format3/override2. MID/SlateUI проверены,
RHI/причина ореола не установлены. LOOP_CANCELLED→STOP reason=user/hooks0→
RELEASED→COMPONENT_DESTROYED→CLEANED, без FAILED/CLEANUP_PENDING.
161 layout,2 hide/resume,8 recoverable overlap-rejection. Последние17 значений
Num9 [приняты как будущая база](REQUIREMENTS.md#новая-база-настроек-и-будущая-компактность--2026-11-05).
Следующие пожелания: сильнее сблизить строки; общий масштаб — если просто/
надёжно. Сейчас только лог/фиксация: новый код/кандидат/установка не выполняются,
старый payload/config/marker неизменны. Игра закрыта, production BLOCKED.

**2026-11-05 — divider/color кандидат INSTALLED, RUNTIME_PENDING.**
По явному разрешению пользователя source `51b9f265c8b6d6b79ff48513a51a84087eeee6be`
[установлен при закрытой игре](../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md#authorized-installation--2026-11-05).
13 installed hashes проверены:10 Lua, новый PNG, private config, own empty marker.
21 прежняя IIP-проба отключена;103 существующих mod/loader/log и46 config/save
файлов сохранены и хэш-проверены. Внешний rollback подготовлен; старый Style
payload/config сохранён. Игра не запускалась/не завершалась, hot reload не было.
Далее один пользовательский run: Ctrl+Alt+F11, manual reload/Open, новый рисунок/
толщина/небольшое движение/hide-show, Num9 и явный NumMultiply. RT/MID-снимок и
visual/manual cleanup ещё не проверены; production BLOCKED, VERSION/main прежние.

**2026-11-05 — authored divider + one color snapshot: READY_SOURCE / NOT_INSTALLED.**
[Один новый кандидат, manifest и сценарий](../research/interaction-prompts-owner/world-space/divider-color-snapshot/README.md)
на ветке `research/divider-color-snapshot`, непосредственно после asset7ff9d6e
и research audit adedeef; принятый Style da83080 не изменён. PNG256×32 с точным
утверждённым SHA, старт length300/thickness1×, полный слот37.5; остальные15
source-defaults Style сохранены. Диагностика один раз при ready-visible own RT:
component/RT/MID и native Retainer/Icon, optional UNAVAILABLE, RHI UNKNOWN.
Охранные ошибки identity/ownership остаются STOP. Full offline333/24 PASS,
из них15 новых; это не native render/visual/cleanup acceptance. Прототип не
установлен/не включён, игра и её окружение не менялись. Далее отдельно разрешённая
closed-game установка с hash/внешним rollback и один пользовательский сеанс.
Рисунок принят; World-прочтение/ореол/реальные метаданные ещё не проверены.
Production BLOCKED, VERSION/main/releases без изменений.

**2026-11-04 — read-only проверка локальных color-доказательств COMPLETE.**
[Матрица значений, точные архивы и граница выводов](../research/interaction-prompts-owner/world-space/hint-mirror/VISUAL_FIDELITY.md#local-archive-audit--2026-11-04-read-only).
В октябрьских512×128 A/B и size-логах реально записаны own sRGB=true,
TargetGamma0, force-linear=false, transparent clear, white/unit component/MID.
RenderTargetFormat6 — поле enum, не доказанный GPU/HDR-формат. В принятом
Style1024×512 own RT/MID-снимка нет;42 записи format3 относятся к native Icon.
Конкретный цветовой конфликт и минимальная правка не доказаны. Архивный шаг
закрыт; минимально недостаёт отдельно разрешённого read-only снимка точного
Style RT/MID и native Retainer, без нового тестового мода. Ничего не запускалось,
не устанавливалось и не включалось; executable source неизменен, production BLOCKED.

**2026-11-04 — узкий color-pipeline audit COMPLETE, source-only; no fix or game changes.**
[Техническая проверка, версионные источники, неопределённости и следующий
минимальный шаг](../research/interaction-prompts-owner/world-space/hint-mirror/VISUAL_FIDELITY.md#color-pipeline-audit--2026-11-04-source-only-no-runtime-writes).
Проверены native Retainer gamma/alpha, собственная UMG-композиция, создание
RT через UWidgetComponent и эффективный stock Masked material против исходников
UE4.27. Явно неверного переключателя гаммы/двойного умножения alpha не найдено;
actual World RT SRGB/format/TargetGamma, финальный cooked material graph и
scene/postprocess output не доказаны. HDR/Emissive остаётся обоснованной
гипотезой, но не установленной причиной засветки. Gamma/tint/материал
наугад не менять; повторять A/B Masked↔Translucent не нужно. Этот
архивный шаг выполнен и уточнён выше; runtime capture лишь для недостающих
полей и после отдельного разрешения.
Старый accepted Style source, marker DISABLED, production BLOCKED и отдельная
задача художественного divider без изменений.

**2026-11-04 — USER_ACCEPTED_RESEARCH; этап завершён, probe DISABLED.**
[Принятый результат и точные17 параметров](../research/interaction-prompts-owner/world-space/live-editor-style/README.md#accepted-research-result-and-recorded-values--2026-11-04).
Source `da830808912b38527fb5088a6543d6a070b5f3f7`; пользователь подтверждает работу
и успешность прототипа, с оставшейся визуальной полировкой. Лог без IIP FAILED:
10 возвратов,589 layout,5 recoverable rejection,2 NumPad9. Последняя запись
19:05:13 совпадает с последним layout; сохранена как research/resume baseline.
Manual STOP в этом сеансе не выполнен, не объявлять его PASS. При закрытой игре
снят только собственный marker; исходники/config/откат сохранены, все IIP-пробы
отключены.103 других mod/loader/log и47 config/save файлов хэш-сохранены.
Новая текстура разделителя — отдельное будущее задание, сейчас только записать.
Непонятный ореол/блеклость/F — открытый нежелательный вопрос, не решённый яркостью.
Дальнейшая работа остановлена по запросу. Production BLOCKED, VERSION/main/релизы
не менялись; принятие research-этапа не является разрешением на stable promotion.

## История выполненных шагов

**2026-11-04 — style-кандидат INSTALLED, новый визуальный тест PENDING.**
Source `da830808912b38527fb5088a6543d6a070b5f3f7`, own WorldStyleProbe;
[идентичность и сценарий](../research/interaction-prompts-owner/world-space/live-editor-style/README.md#authorized-installation--2026-11-04).
11 файлов проверены, предыдущая Expanded отключена;20 старых IIP-проб неактивны.
93 остальных mod/loader/log и46 config/save хэш-сохранены, rollback вне loader.
Игра закрыта; запуска/завершения/hot reload агент не выполнял. Четыре яркости1,
optional lower outline0; старт52/30 и последние настройки, линия пробно2×,
button Y0=divider center. Панель17 параметров с прокруткой9 строк. Offline318/23
PASS; native новые стили/снижение ореола/читаемость и explicit manual STOP ещё
не приняты. Истинная раздельная glow/contrast коррекция остаётся открытой.


**2026-11-04 — expanded run без ошибок; style controls READY_SOURCE.**
[Точный результат](../research/interaction-prompts-owner/world-space/live-editor-expanded/README.md#user-run--large-font-editing--recurring-presentation-passed-narrowly):
~492s,12 возвратов,202 успешных layout,5 recoverable rejection,2 Num9; IIP FAILED
и STOP отсутствуют. Новый кадр показывает композицию и штатный Screen prompt.
Пользователь вышел без manual STOP, поэтому эта очистка в сеансе не проверена.
[Следующий style source](../research/interaction-prompts-owner/world-space/live-editor-style/README.md):
независимая толщина линии, button Y от уровня divider, четыре brightness для
осознанного сравнения и optional lower outline0. Старт52/30/tracking400 и прочие
последние значения, новая пробная толщина2×; яркости1. Панель17 параметров с9-row
window. Полная offline318/23 PASS; actual новый стиль/яркости ещё не приняты.
Причина ореола/выцветания F неизвестна; отдельного доказанного glow/contrast seam
нет. Материал/gamma/глобальные настройки не менялись, production BLOCKED.


**2026-11-04 — Expanded editor INSTALLED, RUNTIME_PENDING.**
Source `19d35a5a0238a3b228f7058bfcd7234e647ede7e`, own WorldExpandedProbe;
[установка/сценарий](../research/interaction-prompts-owner/world-space/live-editor-expanded/README.md#authorized-installation--2026-11-04).
11 файлов проверены; прежняя WorldSession отключена,19 старых IIP-проб неактивны.
83 остальных mod/loader/log файлов и45 config/save сохранены по хэшам, rollback
вне loader. Игра закрыта, не запускалась/не завершалась агентом, hot reload нет.
Текущий кандидат1024×512 с начальными48/28 и диапазонамиupper20–96/lower16–64;
неподходящая ручная компоновка отклоняется без закрытия редактора. Offline309/22
PASS; actual большая поверхность/крупные шрифты/сообщение о пределе ещё не приняты.
Далее один обычный run: Ctrl+Alt+F11/reload/Open, крупные размеры и hide/return,
Num9 и NumMultiply без тестового таймера. Production остаётся BLOCKED.


**2026-11-04 — recurring hide/show подтверждён логом; расширенный редактор READY_SOURCE.**
[Session run](../research/interaction-prompts-owner/world-space/live-editor-session/README.md#user-run--recurring-visibility-worked-tuning-exceeded-old-canvas):
два HIDDEN→RESUMING→SHOWN с тем же компонентом, device4→1 rebind, upper32→36 и
lower22→23. Через~82.305s переполнение512×128 при следующей настройке вызвало
STOP; cleanup CLEANED, таймер не участвовал. Пользователь запросил крупнее текст
и расширение границ. [Новый кандидат](../research/interaction-prompts-owner/world-space/live-editor-expanded/README.md):
own RT1024×512, начальные шрифты48/28 и диапазоныдо96/64, исходная привязка/scale
сохранены. Неподходящая ручная настройка восстанавливает последний валидный набор,
сообщает ограничение в панели и не завершает сессию; настоящие native ошибки
сохраняют безопасный STOP. Full offline309/22 PASS. Expanded native render,
rejection UX/performance и окончательный дизайн ещё не приняты; production BLOCKED.


**2026-11-04 — session-кандидат INSTALLED, повторный hide/show RUNTIME_PENDING.**
Source `dbd1a033be6ee860caf0aef93cb304652c0cbb9d`, новый WorldSessionProbe;
[установка/сценарий](../research/interaction-prompts-owner/world-space/live-editor-session/README.md#authorized-installation--2026-11-04).
Девять Lua, private config и enabled marker проверены (11 файлов); старая
WorldEditor-проба отключена, ещё17 старых IIP остаются отключёнными.73 остальных
mod/loader/log файлов и44 config/save файлов сохранены по хэшам; изменение
предыдущего собственного marker намеренное, rollback подготовлен вне loader.
Игра закрыта, не запускалась/не завершалась агентом, hot reload отсутствует.
Новые time/count guards не добавлялись, runtime-показ/редактор без дедлайна.
Следующий достаточный шаг: тот же natural Open, несколько уходов/возвратов,
настройка в удобном темпе, Num9 лог и явный NumMultiply STOP. Actual recurring
native rendering/controls ещё не приняты, production BLOCKED.


**2026-11-04 — первый editor run: короткий показ, visibility STOP; successor READY_SOURCE.**
[Фактический результат](../research/interaction-prompts-owner/world-space/live-editor/README.md#first-user-run--brief-appearance-one-shot-visibility-stop-2026-11-04):
ожидаемая надпись появилась, через~0.944s old visible-Screen guard окончательно
остановил пробу; таймер не сработал.56 frame-Yaw writes, editor/current-key audit,
private font/PNG/layout прошли до остановки; loop/resource/native cleanup CLEANED.
Полная визуальная приёмка/тюнинг не состоялись. Причина самого изменения native
visibility неизвестна; одноразовая STOP-политика объясняет невозврат при refocus.
[Новый session source](../research/interaction-prompts-owner/world-space/live-editor-session/README.md)
сохраняет ту же композицию и настройки при обычном скрытии/повторном показе того же
сундука. Таймеры и счётные лимиты теста сняты по прямому указанию пользователя;
identity/resource/STOP/cleanup guards сохранены. Полная offline suite301/21 PASS;
actual hide/resume и новый игровой тест ещё не приняты, production BLOCKED.


**2026-11-04 — World editor candidate INSTALLED, RUNTIME_PENDING.**
По прямому разрешению пользователя при закрытой игре установлен source
`c2e36f90d82540bd3e23f25648e16a54c53699b8` в новый WorldEditorProbe.
[Установка и короткий сценарий](../research/interaction-prompts-owner/world-space/live-editor/README.md#authorized-installation--2026-11-04).
Девять Lua source/installed SHA256 совпали, private config и own empty enabled
проверены;17 прежних IIP-проб отключены.63 прежних mod/loader/log и42 config/save
файла сохранены и хэш-проверены. Rollback вне loader. Игра не запускалась и не
завершалась агентом; hot reload не выполнялся. Source/guards/бюджеты неизменны.
Далее пользовательский45s run: Ctrl+Alt+F11 → один reload/Open → NumPad → Num9 →
NumMultiply. Штатный Screen prompt остаётся видимым; HildaSoftLight editor закрыт.
Installation PASS не означает runtime/visual acceptance; production BLOCKED.


**2026-11-04 — полный World prompt + live editor: READY_SOURCE, NOT_INSTALLED.**
[Кандидат, source manifest, setters/ownership и короткий будущий тест](../research/interaction-prompts-owner/world-space/live-editor/README.md).
Один собственный World-компонент: Aphes OPEN, stock ornament, актуальное прочитанное
локализованное действие и read-only native hint; отдельная экранная панель с10
относительными настройками. Ctrl+Alt+F11 — arm/toggle; NumPad только при открытой
панели, Num9 — лог без файла, NumMultiply — полный STOP. Собственный layout сохраняет
настроенный размер при смене native source. Frame-Yaw без углового порога, native
cleanup, прежние guards/бюджеты и исходный Screen TipHUD сохранены.
Полная offline suite:290 тестов/20 файлов, PASS; это не игровая приёмка.
Native input/source contracts и игровые ресурсы проверены по имеющимся источникам;
runtime-аудит текущих mapping/registry и новый игровой прогон ещё не выполнены.
Одновременные редакторы IIP/HildaSoftLight не поддерживаются. Причина бледного
World-hint неизвестна, gamma/tint/material не подбирались. VERSION/main/релизы и
установленная игра не менялись. Следующий достаточный шаг — отдельно разрешённые
безопасная установка и один45-секундный combined test; production остаётся BLOCKED.

## История предыдущих этапов

**2026-10-30 — выбран этап полной World-space композиции с live-тюнером; SOURCE NOT PREPARED.**
[Принятая граница и UX](REQUIREMENTS.md#live-настройка-полной-world-space-композиции--решение-2026-10-30):
четыре собственных элемента (Aphes, разделитель, текущая локализованная нижняя
строка и native-live icon), самостоятельная экранная панель для регулировки
типографики/отступов/разделителя/иконки. Исходный TipHUD не редактировать;
видимый размер иконки целится в штатный, без утверждённого коэффициента.
HildaSoftLight теперь имеет [один пользовательский 69-минутный runtime-прогон](https://github.com/NikichMods/HildaSoftLight/blob/research/live-light-tuner/docs/COMPARISON_RESULT_2026-10-30.md)
для отдельного одноциклового тюнера с Ctrl+Alt+F10 и обычным NumPad;
неизвестная UE4SS registry-ошибка и межмодовое взаимное исключение остаются открытыми.
Для IIP выбран отдельный Ctrl+Alt+F11 и обычный NumPad только при активной панели;
одновременная настройка двух редакторов не поддерживается без отдельного
доказанного механизма. Следующая работа — source-only интеграция и минимальная настройка
собственных параметров, затем отдельно разрешённый игровой тест. Размер1.5×
был технической пробой, не финальным дизайном. Full composition, color and
production BLOCKED; установленная ранее size-проба отключена.

**2026-10-30 — own-size1.0×→1.5× runtime PASS, F7 PASS, probe DISABLED.**
[Технический результат, кадры и хэши](../research/interaction-prompts-owner/world-space/hint-mirror/size/README.md).
Slot38×38→57×57; проекция26.795×24.603→40.238×36.903px, центр одинаковый,
PAIR_READY. View/source/component/MID/RT/Masked/gamma/tint/opacity неизменны;
F7 loop-cancel/release/native destroy/CLEANED прошёл без FAILED. Пользователь
подтвердил увеличение и лучшую читаемость. Runtime rebind после увеличения не
случился: persistence остаётся офлайн-проверкой.1.7–2× — предварительная заметка
для отдельного дизайна, не принятое значение/задание. Код и требования не менять.
Снят только own marker при закрытой игре;111 других файлов/42 baseline hashes
сохранены. Технический этап завершён, color/design/full production не приняты.

**2026-10-30 — own-size1.0×/1.5× probe INSTALLED, RUNTIME_PENDING.**
По прямому разрешению при закрытой игре установлен source9954b04828706820f94774a95f29cbb10f93629c
в новый WorldHintSizeProbe. [Хэши, откат и сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/size/README.md).
Четыре source/installed Lua SHA256 совпали, только own empty enabled.txt включён;
16 предыдущих IIP-проб отключены.40 старых Mods файлов сохранены,44 baseline
файла/64 config-save hashes совпали. CombatHUD/SoulsEnemyHUD и mods.txt неизменны,
откат вне loader. F8 start → один reload/Open → выбрать ракурс → F8/A1.0× →
F6/B1.5× без движения → F7. Игра не запускалась агентом, guards/код не менялись.
Runtime и production остаются без приёмки; ниже сохранена история подготовки.

**2026-10-30 — fixed own-hint size calibration READY_SOURCE, NOT_INSTALLED.**
[Четыре Lua, source/hash-контракты и один сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/size/README.md).
Один Masked-компонент; F8 запрашивает A/1.0×, F6 один раз меняет только own
CanvasPanelSlot extent на1.5× (38×38→57×57), затем B/F7. Коэффициент отдельный
от source binding и сохраняется при повторном SOURCE_BOUND; исходный slot не
меняется. Проверки aspect/center/Canvas envelope/readback, реальная проекция
своих углов; original Screen pixels остаются UNAVAILABLE, сравнение по кадрам.
Материал/MID, RT512×128, component scale0.25/anchor/Yaw, gamma/tint/opacity и
прежние guards/сроки/native cleanup сохранены.1.5 — диагностический вариант,
не продуктовый размер или color fix. Новый код не установлен, игра не тронута.
Runtime размер/читабельность/цвет ещё не приняты; production BLOCKED.

**2026-10-30 — A/B pair runtime PASS, заметного улучшения нет; probe DISABLED.**
[Парные записи, порядок кадров и границы](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
09:57:49=A/Masked;09:57:58=B/Translucent. Между ними native switch BEGIN/END,
новый own MID, BlendMode2 и PAIR_READY. Camera/source/RT/settings совпали;
проекция slot27.991×23.797px в обоих состояниях. Пользователь не видит отличия,
маленький голубоватый вид сохранился. Смена режима одна не дала исправления;
общий base/RT/scene-color path этим не оправдан. F7 native cleanup reason=user
прошёл. Снят только own marker при закрытой игре;105 других файлов/38 baseline
hashes сохранены. Lua неизменён. Эту A/B-проверку не повторять. Следующим отдельно
согласовать только размер own icon; цвет остаётся открыт, production BLOCKED.

**2026-10-30 — same-source A/B REENABLED, повторный тест PENDING.**
По явному разрешению пользователя возвращён только own empty enabled.txt при
закрытой игре. Четыре Lua sourcecaf955f и pinned loader неизменны,40 прежних Mods
files сохранены, другие IIP-пробы отключены. [Точная запись](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
Первый неполный результат/кадры сохранены. Guards/сроки не менялись; выбрать
ракурс до A, затем не двигаться до B. Установка/повторное включение не приёмка.

**2026-10-30 — Masked capture PASS; A/B INCOMPLETE_CAMERA_GUARD, probe DISABLED.**
[Лог, кадры, измерения и пределы](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
A записал проекцию своего slot25.949×25.027px при2560×1440, gamma=false,
white tint/unit opacity. Пользовательский кадр подтверждает маленький голубоватый
значок; причина цвета не установлена. F6 остановлен на `AB camera moved` ДО
material-switch BEGIN и записи BlendMode/SetMaterial. Значок на B исчез из-за
успешного native cleanup, не из-за Translucent: этот материал не проверен.
Логи/два PNG сохранены локально; при закрытой игре снят только own enabled.txt.
104 других текущих файла и38 historical mod/loader hashes сохранены. Lua не
менялся. Следующий достаточный шаг — тот же A/B без движения между A и B,
после отдельного разрешения; guards/timeout не ослаблять. Production BLOCKED.

**2026-10-30 — World hint A/B INSTALLED, RUNTIME_PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точный
source`caf955fb271558df1ddd5c991cf5b53217da2ef4` в новый WorldHintABProbe.
[Установка, хэши, откат и сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
Четыре Lua совпали с source SHA256; включён только собственный empty enabled.txt.
15 прежних IIP-проб отключены, mods.txt/CombatHUD/SoulsEnemyHUD неизменны.
Откат/резервные копии вне loader;40 прежних файлов и60 config/save hashes
совпали после установки. Игра не запускалась/не закрывалась агентом. Далее:
F8 → один reload/Open → остановиться → F8/screenshot A → F6/screenshot B → F7.
Guards/сроки не ослаблены; early stop оставляет неполную пару. Никакой новой
визуальной приёмки; production BLOCKED. Ниже сохранена история подготовки.

**2026-10-30 — World hint material A/B READY_SOURCE, NOT_INSTALLED.**
[Четыре Lua, контракты, хэши и один сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/ab/README.md).
Один собственный компонент: Masked1 → reflected BlendMode2 + virtual SetMaterial
stock Translucent; native путь пересоздаёт только own MID/render state. F8 после
появления запрашивает A, F6 один раз переключает B; две записи actual RT/gamma/
material и проекции углов своего slot. Оригинальный Screen pixel-size не получен:
pinned Lua struct-return теряет неотражённые данные FGeometry. Вместо поддельной
геометрии — явный UNAVAILABLE и два сопоставимых скриншота. Ни размер, ни gamma/
tint/anchor/DrawSize/Yaw не меняются. Прежние guards,45s/120s и native cleanup
сохранены; прежний early visibility stop может не дать закончить пару. Офлайн
проверки не доказывают Translucent pixels/occlusion. Parent Lua, VERSION и игра
не менялись; полная композиция/визуальная приёмка/production BLOCKED.

**2026-10-30 — hint visual source review COMPLETE; visual equivalence OPEN.**
[Разбор цепочки и один следующий A/B](../research/interaction-prompts-owner/world-space/hint-mirror/VISUAL_FIDELITY.md).
UI MID сам выбирает AlphaComposite blend; отсутствие premultiplied-флага у Image
не доказывает double-alpha. При ожидаемом gamma=false этот paint stage уже gamma1;
слепое включение коррекции не обосновано. Подтверждены отличия внешнего Masked
coverage и размера:38×38 при scale0.25 =9.5 мировых единиц, не38 экранных pixels.
Рекомендуются измерение экранных прямоугольников и один fixed-pose A/B Masked ↔
stock Translucent с согласованными own BlendMode/material. Это план сравнения,
не доказанное исправление цвета: полный cooked shader graph/фактические own RT
и gamma/итоговые pixels неизвестны. Новый payload не создавался/не установлен,
принятые Lua и VERSION неизменны. Полная композиция/production BLOCKED.

**2026-10-30 — hint mirror partial runtime PASS; visual equivalence OPEN, probe DISABLED.**
[Точные логи и границы](../research/interaction-prompts-owner/world-space/hint-mirror/README.md). Active Retainer/global1, Icon RT51x51/slot38x38,
AlphaComposite5/RGBA8_SRGB3. SOURCE_BOUND device4→1 с тем же MID/RT; пользователь
увидел корректную смену controller glyph→keyboard F. Обратный переход не записан
до visibility-guard stop через~3.764s; причина конкретного visibility predicate
неизвестна. Loop cancelled, own resource RELEASED и native CLEANED прошли.
Размер/выцветший полупрозрачный голубоватый вид — наблюдение пользователя, не
визуальная приёмка и не доказанный gamma/alpha диагноз. Этот run не зафиксировал
F7; ранее принятый vertical F7 остаётся PASS. Логи архивированы, при закрытой игре
снят только own enabled.txt;35 baseline hashes совпали,91 текущий файл сохранён.
Новый payload/установка не готовились. Полная композиция/production BLOCKED.


**2026-10-30 — native World hint mirror INSTALLED, runtime PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точный7c2aa07
в новый ImmersiveInteractionPromptsWorldHintProbe: три Lua и enabled.txt.
[Хэши, откат и один сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/README.md). Lua не менялся; source/installed hashes совпали.
Только новая IIP-проба включена,14 старых отключены.29 исторических mod/loader
hashes совпали;35 текущих mod/loader и55 существующих tracked config/save файлов
сохранены по хэшам. UE4SS DLL совпал; backup/manifest/guarded rollback вне loader,
syntax PASS. Игра не запускалась/не закрывалась агентом, hot reload не применялся.
Далее keyboard→controller→keyboard→F7 без F8 на controller. Runtime pixel/device/
current remapping ещё не принят; полная композиция/production BLOCKED.


**2026-10-30 — native input-hint World mirror READY_SOURCE, NOT_INSTALLED.**
[Три Lua, точные контракты/хэши и один тест](../research/interaction-prompts-owner/world-space/hint-mirror/README.md). Перед own allocation проверяется
selected Retainer: при bRetainRender/global1/phase0-count1 и готовом UI MID/Icon RT
свой Image ссылается на существующий MID; при выключенном bRetainRender допускается
только одиночный untransformed Texture2D Image Brush. Global0/missing/change и
неподдерживаемые источники отвергаются. Второго Retainer/записи параметров нет.
Каждый кадр проверяются ресурс/device/identity; own stale reference скрывается/
снимается до bounded settling/rebind. Максимум8 поколений, прежний World/Yaw/F7/
timeout сохранён; никаких Aphes/текста/PNG.232 tests/16 suites PASS,25 новых.
Фактическая активность/пиксели/alpha-gamma/device/remapping ещё не проверены в игре.
Следующий отдельный тест: keyboard→controller→keyboard (без F8 на controller),
F7 до30s. Полная композиция/production BLOCKED. Ничего не устанавливалось.


**2026-10-30 — World Aphes composition integration BLOCKED: live input hint.**
[Source-only review / partial pure plan](../research/interaction-prompts-owner/world-space/composition/README.md). Текст действия можно читать из
оригинального GetText и обновлять собственный TextBlock текущим локализованным
значением; pinned FText setter не сохраняет полную string-table history. Прежний
скопированный F brush был только снимком. RetainerBox_0/TipIconMat добавляет слой
Icon render-target и hold-параметр t; второй Retainer с оригинальным MID сам писал
бы в shared Icon — такой путь отвергнут. Own Image с read-only final MID — кандидат,
его alpha/gamma/актуальность при смене устройства и remapping ещё не доказаны.
Исполняемый композиционный payload не создан, заглушки F нет. Подготовлен только
pure slot-envelope512x128 и8 тестов;207 tests/15 suites PASS. Aphes/PNG локальны,
renderer/anchor/material/Yaw/cleanup и прежние исходники не менялись. Следующий
достаточный тест после отдельной подготовки/разрешения — узкий hint-only mirror
keyboard→controller→keyboard, затем F7. Финальный дизайн/full lifecycle/production
BLOCKED; ничего не устанавливалось и игра не запускалась.


**2026-10-30 — vertical frame-Yaw / manual F7 bounded runtime PASS; probe DISABLED.**
[Точная запись](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Пользователь подтвердил почти идеальную работу и F7.
Один loop handle3,1068 frames/1068 writes за~17.796s, no degeneracy/errors;
STATE Pitch/Roll0, world position/scale неизменны, RT512x128/stock depth material.
F7: LOOP_CANCELLED→STOP user/hooks_remaining0→native destroy/CLEANED user.
Снято только own enabled.txt при уже закрытой игре;33 прежних mod/loader hashes
совпали,88 текущих файлов сохранены. Sourcef1eb635 неизменён. Закрыт узкий gate
вертикального покадрового Yaw и ручной очистки. Точный FPS/latency не измерены,
финальная композиция/full lifecycle/production BLOCKED; нового payload/теста нет.


**2026-10-30 — vertical world-Z yaw INSTALLED, runtime PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точныйf1eb635
в новый ImmersiveInteractionPromptsWorldYawProbe: два Lua и enabled.txt.
[Хэши, откат и один сценарий](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Source/installed SHA256 совпали, Lua неизменён.
Только новая IIP-проба включена;13 прежних отключены.29 исторических mod/loader
hashes совпали;33 текущих mod/loader и56 существующих tracked config/save файлов
сохранили hashes. UE4SS83330635/DLL совпал, backup/manifest/guarded rollback вне
loader, syntax PASS. Игра не запускалась/не закрывалась, hot reload не применялся.
Следующий шаг — один пользовательский vertical-yaw/F7 тест; runtime/production
acceptance остаётся BLOCKED, установка не является его прохождением.


**2026-10-30 — vertical world-Z yaw READY_SOURCE, NOT_INSTALLED.**
[Отдельная ревизия, контракты, хэши и один будущий тест](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Решение пользователя
зафиксировано в REQUIREMENTS: каждый EngineTick только горизонтальный Yaw,
Pitch/Roll0, без1° threshold/интерполяции; fixed initial vertical — минимальный резерв.
Pinned LoopInGameThreadAfterFrames(1) подтверждён вместе с ownership/cancel/unref.
Один own loop после регистрации, нативный lifetime каждый кадр, полная topology/
anchor проверка каждые12 callbacks;12000 updates/45s, прежние пределы сохранены.
8 точечных lookups/13 UE calls в обычном follow-кадре — не замер производительности.
199 tests/14 suites PASS,22 новых. Не установлен, игра и прежний payload не менялись.
Следующий отдельный runtime gate: вертикальность/покадровый Yaw и F7 до30s в одном
коротком прогоне. Cadence/camera phase/performance и manual cleanup ещё не приняты;
production BLOCKED. Старые результаты rendering/occlusion/setter не повторять.


**2026-10-30 — bounded World rotation / target-loss cleanup PASS; probe DISABLED.**
[Технический результат и границы](../research/interaction-prompts-owner/world-space/orientation/README.md). Fixed:103 polls/0 writes/error27.383°;
F6 включил follow, первый native setter вернулся, ошибки setter/readback нет.
Через42.629s после создания stop по потере видимости Screen Open (CONTRACT_ERROR),
затем hooks_remaining0, native destruction и CLEANED. Конкретный visibility
predicate/причина неизвестны; F7 в логе отсутствует и не принят. Итогового follow
sample/числа поворотов нет. Пользователь сообщил общую успешность; дизайн,
предпочтение режимов и плавность не оцениваются. Логи архивированы; при закрытой
игре снят только own enabled.txt,31 прежний mod/loader hash совпал,87 текущих
файлов сохранены при отключении. Production BLOCKED, нового payload нет.


**2026-10-30 — World orientation comparison INSTALLED, runtime PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точный6d44daa
в новый ImmersiveInteractionPromptsWorldOrientationProbe: два Lua и enabled.txt.
[Идентичность, откат и сценарий](../research/interaction-prompts-owner/world-space/orientation/README.md). Source/installed hashes совпали;
только новая IIP-проба включена,12 прежних отключены.29 исторических и31 текущий
mod/loader hash сохранены,59 config/save hash неизменны. DLL83330635 совпал;
backup/manifest/guarded rollback вне loader, syntax PASS. Игра не запускалась,
hot reload не применялся. Далее один пользовательский fixed/follow/F7 тест;
плавность, native rotation/marshalling и ручной cleanup ещё не приняты.


**2026-10-30 — World orientation comparison READY_SOURCE, NOT_INSTALLED.**
[Исходники, контракты, хэши и будущий тест](../research/interaction-prompts-owner/world-space/orientation/README.md).
Отдельная ограниченная ревизия сохраняет принятый V3 renderer/anchor/material и
начальную фиксированную ориентацию. F6 переключает fixed/follow: не чаще10Hz,
поворот при ошибке>=1°, только собственный компонент через K2_SetWorldRotation
на EngineTick, с readback и свежей проверкой цели/UI. Максимум450 проверок/45s;
при потере/смене известной цели, уходе за экспериментальные bounds или F7 — stop
и own cleanup. Нет сканирования мира, изменения размера/положения/оригинального UI.
177 tests/13 suites PASS,19 новых; setter/marshaling/плавность ещё runtime PENDING.
Динамический billboard не принят как production-дизайн. Следующий достаточный
шаг после отдельного разрешения установки — один fixed/follow camera comparison
и ручной F7 до timeout. Принятый rendering/occlusion опыт не повторять. Игра и
установленный payload не менялись; production BLOCKED.

**2026-10-30 — bounded World rendering / Hilda occlusion / timeout cleanup PASS.**
[Полный результат](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Точный6ad93fc V3 загрузил host одним LoadAsset после reload, создал собственный
World-компонент; пользователь подтвердил видимость, частичное перекрытие букв
Хильдой и возвращение букв при смещении. Два STATE: одинаковые world position/
rotation, RT512×128, штатный masked/depth материал. Через45s world_timeout:
hooks_remaining0, native COMPONENT_DESTROYED и CLEANED, ошибок probe нет.
F7 до timeout не выполнен — ручной World cleanup-key не принят. Первые22s не
покрыты снимками; ощущение начального поворота не диагностировано. В коде только
начальная ориентация, динамический billboard пока не реализован/не проверен.
Логи сохранены, при закрытой игре снят только own enabled.txt;29 прежних mod/loader
hashes совпали,91 текущий файл не изменился при отключении. Проба DISABLED.
Механизм реального перекрытия в одном Open доказан; причина первого зависания
неизвестна. Не повторять этот этап. Следующий отдельный вопрос — поведение при
движении камеры/дистанции; финальная композиция и production lifecycle BLOCKED.

## История установки V3

**2026-10-30 — Deferred World V3 INSTALLED, runtime PENDING.**
По разрешению пользователя при закрытой игре установлен точный6ad93fc source
в новый ImmersiveInteractionPromptsWorldRefreshProbe: два Lua и enabled.txt.
[Хэши/откат/процедура](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Другие IIP probes сохранены/отключены;29 старых mod/loader и59 текущих config/save
файлов сохранили хэши, UE4SS DLL совпал. Backup/manifest/guarded rollback вне
loader в local post-reload-refresh/install-20261029T220606Z. Lua не менялся.
Игра не запускалась/не закрывалась, hot reload не выполнялся. Следующий шаг — один
пользовательский F8→reload→Open→F7 тест новой загрузки и, если пройдена, renderer.
Причина первого зависания неизвестна; World/production acceptance BLOCKED.

## Подготовка V3

**2026-10-30 — Deferred World V3 post-reload refresh READY_SOURCE, NOT_INSTALLED.**
[Текущие исходники/хэши/проверки](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
F8 проверяет только API, без преждевременной загрузки. После MATCH отложенная
EngineTick-задача различает nil/null-wrapper/Lua-invalid/native-invalid/identity
mismatch и разрешает максимум один точный LoadAsset каждого HOST/MASK за сессию.
После загрузки заново проверяются actor/component/TipHUD/UI/Open/native validity
и текущий anchor; только затем прежний путь создания. Отмена/срок/reentry/cleanup
сохранены, геометрия и материал неизменны.158 tests/12 suites PASS; deferred34.
Установленная V2 и старый World probe отключены и не изменены. Игра не запускалась,
новая ревизия не устанавливалась. Следующий шаг — отдельно разрешённая установка
новой пары и один ограниченный фазовый тест. Загрузка класса не доказывает World
renderer; причина первого зависания неизвестна, production/World acceptance BLOCKED.

## Предыдущий результат Deferred V2

**2026-10-30 — deferred World run: NOT_LOADED после reload, probe DISABLED.**
[Точный результат](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Host load/PREPARED прошли до own hooks; после reload MATCH→CREATE_QUEUED→
CREATE_DISPATCHED(EngineTick) и anchor/camera/math-фазы завершились. Затем gate
resident_assets отказал: живой точный PostionItemUMG_BP_C не подтверждён.
STOP result=NOT_LOADED/hooks_remaining0; component_construct не начат, World
renderer не создавался. GC/unload как причина и исправление первого зависания
не доказаны. Логи сохранены; при закрытой игре снят только own enabled.txt.
27 старых mod/loader и88 текущих файлов сохранили хэши при проверке/отключении.
Текущий lookup-only вариант BLOCKED; минимальная следующая правка — одно точное
обновление ресурсов через EngineTick после reload, затем свежая проверка цели/UI.
Новая ревизия не установлена; World/production acceptance BLOCKED.

## История deferred-установки

**2026-10-30 — deferred World revision INSTALLED, runtime PENDING.**
По разрешению пользователя при закрытой игре установлен точный2941123 source
в новый ImmersiveInteractionPromptsWorldDeferredProbe: два Lua и enabled.txt.
[Хэши, откат и сценарий](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Старая зависшая ревизия сохранена и отключена; включён только новый IIP probe.
UE4SS DLL совпал;27 прежних mod/loader и59 текущих config/save файлов сохранили
хэши. Backup/manifest/guarded rollback вне loader в local deferred/
install-20261029T214003Z. Игру не запускали/не закрывали, hot reload не применяли.
Следующий шаг — один пользовательский F8→reload→Open→F7 тест с фазовыми логами.
Причина прежнего зависания ещё не доказана; runtime/production acceptance BLOCKED.

## Подготовка отложенной ревизии

**2026-10-30 — deferred World diagnostic revision READY_SOURCE, NOT_INSTALLED.**
[Разбор и отдельные исходники](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Причина первого зависания не доказана. Точный UE4SS source подтверждает: script
callback удерживает общий recursive mutex, а простая EngineTick action выполняется
после освобождения очереди/lock. Синхронный LoadAsset на miss вызывает LoadObject.
Новая ревизия разрешает класс/материал до регистрации своих hooks, создаёт только
через EngineTick после свежей проверки identity/UI/native validity, не загружает
ресурсы при создании/после reload; cleanup тоже отложен. BEGIN/END-фазы отделяют
load/construct/Create/first Slate/register/cleanup. Anchor/визуальные параметры и
материал прежние.139 offline tests/12 suites PASS;15 новых policy cases.
Зависшая ревизия/установленные Lua не изменены и отключены. Новой установки,
игрового прогона или runtime PASS нет; World/production acceptance BLOCKED.
Следующий достаточный шаг — отдельное разрешение на установку новой пары файлов
и один ограниченный пользовательский фазовый тест.

## Предыдущий отрицательный игровой результат

**2026-10-30 — первый World-прогон: пользователь сообщил зависание; probe DISABLED.**
[Логи, границы и следующий шаг](../research/interaction-prompts-owner/world-space/probe/README.md).
Точное Open MATCH получено00:15:12.150; это последняя строка UE4SS.log.
CREATED/STATE/FAILED/CLEANED/STOP отсутствуют; Genesis.log заканчивается через8ms
на FlushAsyncLoading. Конкретный зависший вызов и причина не доказаны. World
отрисовка/перекрытие/очистка не приняты. Процесс уже отсутствовал при проверке;
агент его не завершал. Оба лога и exact source сохранены локально. При закрытой
игре снят только собственный enabled.txt;25 прежних mod/loader hashes совпали,
86 текущих файлов не изменились при отключении. Исходники/другие моды сохранены.
Эта ревизия BLOCKED для повторного теста; следующий шаг — узкая проверка контекста
создания/загрузки и фазовая диагностика, без автоматической установки исправления.

## История установки

**2026-10-30 — World TEST prototype INSTALLED, runtime PENDING.**
По разрешению пользователя при закрытой игре установлен точный d4a1ac6 source:
два Lua-файла и enabled.txt в новом ImmersiveInteractionPromptsWorldProbe.
[Хэши, откат и инструкция](../research/interaction-prompts-owner/world-space/probe/README.md).
UE4SS83330635/DLL совпали;25 старых mod/loader и58 текущих config/save files
сохранили хэши. CombatHUD/SoulsEnemyHUD сохранены; остальные IIP probes отключены.
Backup/manifest/guarded rollback вне loader: local world-space/probe/
install-20261029T211023Z. Исходники не менялись, игру не запускали/не закрывали.
Следующий шаг — один пользовательский reload/Open/partial-occlusion/F7 test.
World rendering/очистка в игре и production BLOCKED до результата.

## Подготовка исходников

**2026-10-29 — отдельный World-component прототип READY_SOURCE, не установлен.**
[Исходники, точные хэши и процедура](../research/interaction-prompts-owner/world-space/probe/README.md).
Проверенные OpenJoin и независимый host переиспользованы. Один собственный
RF_Transient UMG.WidgetComponent: World0 до FinishAddComponent(manual=true),
stock masked depth-tested material, WORLD TEST, фиксированная плоскость512×128
со scale.25 и live anchor+32Z, без collision/overlaps/input/focus. Оригинальный
TipHUD и его компонент остаются Screen и не изменяются.45s после создания,
общие120s, явный F7 cleanup с native PendingKill-aware проверкой и retry отказа.
16 новых policy tests PASS; весь suite124 tests PASS. Source/UHT audit и mocks
не доказывают реальную отрисовку/перекрытие/teardown. Следующий шаг — отдельно
разрешённая установка и один визуальный тест частично закрытых Хильдой букв.
Установки/запуска игры не было; World runtime acceptance и production BLOCKED.

## История binding-проверки

**2026-10-29 — один natural Open actor/component/TipHUD join и world pose PASS;
probe отключён.** [Полные identity/координаты](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md):
603ab6b сохранил3 пары после ACQUISITION_CLOSED init128; CanShow после reload
выбрал0-1_lootbox_01_mat_ST001 класса item_lootbox02_C и его exact ExtendedWidget/
TipHUD.2 конечных world-pose снимка, затем user STOP result=MATCHED за46.394s,
show415/unmatched0/match1/poses2/hooks_remaining0. Ошибок probe нет.
Прямая live связь и один anchor доказаны; обе script routes пригодны в этом reload.
Лог сохранён; игра закрыта, снят только собственный enabled.txt.24 прочих baseline
mod/loader hashes совпали,88 текущих файлов сохранили хэши при отключении.
Следующий отдельный шаг — подготовить собственный World-component тест на этом
anchor, не менять оригинал. World rendering/occlusion и production BLOCKED.

**2026-10-29 — исправленная OpenJoin ревизия INSTALLED, runtime PENDING.**
Source603ab6be645bbc2b552f3e88e0d2448c981485b1, installed SHA256
932901d8766bfb3640ddd48f1d7811e8ccadbf83df2b63bc597dfece225ea664.
При закрытой игре заменён только own main.lua и добавлен enabled.txt;24 остальных
mod/loader и62 текущих config/save files сохранили хэши. Старый995a581f payload
и disabled-state сохранены для отката вне loader в локальном
beginplay-probe/budget-fix/install-20261029T165639Z. Только OpenJoin включён.
Игра/reload не запускались; [один пользовательский тест](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
проверяет продолжение CanShow после ACQUISITION_CLOSED и MATCH/POSE.
Это research handoff, не production release; VERSION/World gate не менялись.

**2026-10-29 — acquisition-budget correction READY_SOURCE, installation authorized.**
[Ревизия](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
закрывает только BeginPlay acquisition при128, сохраняя проверенные пары и CanShow.
Общие120s/4096 callbacks/4 poses и≤8 кандидатов прежние; лишние init contexts не
читаются даже при отложенном снятии hook.108 offline tests PASS, включая replay
3-пар/128-callback сценария с последующим MATCH. Lua SHA256
932901d8766bfb3640ddd48f1d7811e8ccadbf83df2b63bc597dfece225ea664.
Runtime новой ревизии не проверен; production/VERSION/World не меняются.

**2026-10-29 — OpenJoin: acquisition PASS, selection cut off by init budget;
probe отключён.** [Точный результат](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md):
после ручного reload получены3 реальные Open actor/component/TipHUD пары с
проверенными взаимными ссылками. Затем STOP init_budget за20.789s: init=128,
open/ready=3, show/matches/poses=0; ошибок probe нет.128 — callbacks, не число actor.
Подтверждён BeginPlay dispatch после reload; CanShow survival/visible join и pose
ещё не установлены. Лог сохранён, игра закрыта, снят только собственный enabled.txt;
24 старых mod/loader hashes совпали,87 остальных текущих файлов не изменились при
отключении. Код не менялся. Предложение следующего этапа — закрывать только
acquisition при128, сохраняя3 пары и прежние общие лимиты; не реализовано/не установлено.
World rendering и production BLOCKED.

## История подготовки и установки

**2026-10-29 — BeginPlay + CanShow OpenJoin probe INSTALLED, runtime PENDING на момент установки.**
По разрешению пользователя при закрытой игре установлен точный3497ab5 исходник,
Lua SHA256995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3.
Добавлены только main.lua/enabled.txt в новом ImmersiveInteractionPromptsOpenJoinProbe.
24 старых mod/loader и61 текущий config/save files сохранили хэши. Другие моды и
CombatHUD сохранены, старые IIP probes отключены. Вне loader сохранён rollback,
снимки и манифесты в локальном beginplay-probe/install-20261029T163735Z.
Игра/reload не запускались; следующий шаг — [один пользовательский reload/test](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md).
Live mapping/pose, World rendering и production остаются BLOCKED.

**2026-10-29 — BeginPlay + CanShow join probe READY_SOURCE, runtime NOT_TESTED.**
[Исходник/процедура](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md):
два точных single-callback script hooks,≤8 Open attempts,≤128 init/4096 CanShow,
120s wall-clock,≤4 pose snapshots только после взаимного identity join.
Проверены partial registration rollback, nil-return всех callbacks, source lifetime
script registry через LoadMap и cleanup при отсутствующей metadata.105 offline
tests/10 suites PASS. Lua SHA256995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3.
Установки, запуска игры/reload/hot reload не было; production/VERSION не менялись.
Реальная сохранность двух hooks через ручной reload и live actor/component/pose
остаются непроверенными. Следующий шаг — отдельно разрешённая closed-game установка
этих байтов и один пользовательский reload/test. World/production BLOCKED.

**2026-10-29 — после NO_EVENTS выбран source-only маршрут: parent Blueprint
BeginPlay → точный join с CanShow. Новый payload не создан.**
[Переоценка архитектуры и контракт](../research/interaction-prompts-owner/open-binding/ROUTE_REVIEW.md):
BaseLoot/Open ReceiveBeginPlay входит в ubergraph2152 и явно вызывает родительский
BaseGameEventObject_BP.ReceiveBeginPlay; родитель получает own ExtendedWidget's
widget на102. Это более сильное callsite-доказательство, чем декларации native
Setup/SetArrayData. Для них natural timing/dispatch всё ещё неизвестны.
Предпочтительный следующий тест — ограниченный захват≤8 Open-пар на естественном
BeginPlay после ручного reload и сопоставление с уже доказанным CanShow callback.
Статус PREFERRED_ROUTE_DEFINED, live mapping/pose ещё NOT_OBSERVED. Runtime-код,
установка/игра/production/VERSION не менялись. World/production BLOCKED;
реальное перекрытие Хильдой остаётся требованием, Screen только fallback.

**2026-10-29 — Open binding: NO_EVENTS, mapping/pose NOT_OBSERVED; probe отключён.**
[Результат](../research/interaction-prompts-owner/open-binding/README.md): native
SetShow hook зарегистрирован IDs10/11, WAITING14:28:55.863 → STOP reason=user
14:29:27.828, callbacks=0/samples=0 за31.965s. Ошибок probe нет, но MATCH/POSE нет;
getter/identity-проверки не исполнялись. Причина отсутствия событий неизвестна.
Лог сохранён; игра закрыта, снят только свой enabled.txt.23 прежних mod/loader
hashes совпали;87 остальных текущих файлов не изменились при отключении.
Этот event route не закрыл live mapping gate. Не повторять/расширять прогон
автоматически: сначала отдельный выбор проверяемого входа. World/production BLOCKED.

## История подготовки Open binding

**2026-10-29 — Open binding probe INSTALLED; runtime PENDING.**
По явному разрешению пользователя при закрытой игре установлен точный148e5c0
Lua SHA256a56d8fda1821f28a01e1d1f4e423a8b33e60d3f36d2c7312c5c2ff3327d3f56f.
Добавлены только Scripts/main.lua + enabled.txt в собственном OpenBindingProbe;
23 прежних mod/loader и64 config/save files не изменились по хэшам. Старые IIP
probes отключены. Вне loader сохранены rollback/снимки/манифесты в локальном
open-binding/install-20261029T112539Z. Игра не запускалась; следующий шаг —
[один пользовательский Open test](../research/interaction-prompts-owner/open-binding/README.md#user-experiment--installation-authorizedcompleted-run-still-pending).
Live mapping/pose ещё не подтверждены, World/production BLOCKED.

**2026-10-29 — natural Open binding: READY_SOURCE для одного read-only теста,
live mapping ещё NOT_TESTED.** [Отчёт и исходник](../research/interaction-prompts-owner/open-binding/README.md):
один естественный post SetShow даёт component context без сканирования мира;
проверяются назначенный TipHUD, GetOwner, взаимная actor.ExtendedWidget ссылка,
Open/Interact и transform компонента. SenderActor/NewUserWidget не объявлены
эквивалентом владельца без проверки. Лимиты60s/64 callbacks/6 snapshots, явный stop,
нет retargeting/игровых записей.83 offline tests проходят. Реальный вызов этого
отражённого метода для natural Open, live identities и pose ещё не получены.
Ничего не установлено/не запущено. Host runtime PASS не повторялся.
World rendering/occlusion и production BLOCKED.

**2026-10-29 — independent UserWidget host runtime PASS; probe отключён.**
[Лог и границы](../research/interaction-prompts-owner/userwidget-host/probe/README.md):
точный LoadAsset found/loaded=true → private tree → Construct Hidden → VISIBLE →
ручной LABEL_REMOVED/OWNERSHIP_RELEASED/CLEANED reason=user за22.218s.
Исходный HUD fingerprint неизменен; пользователь подтвердил весь сценарий.
Игра закрыта, лог сохранён, снят только собственный enabled.txt;87 остальных
текущих файлов сохранили хэши при отключении. Host-блокер закрыт для этого класса
и одного viewport lifecycle. Следующий отдельный шаг — exact natural Open
actor/component/pose. World rendering/occlusion и production всё ещё BLOCKED.

## История этапов (предыдущие статусы на момент записи)

**2026-10-29 — independent UserWidget probe установлен по разрешению пользователя;
runtime PENDING.** Точный source commit a23635b95b029ff8d73dec4f940e1aa54c213d37,
Lua SHA25666ffdce4fecdf954981a5364320bc78f3f67df717ee16175673558bac9543186.
Игра проверена закрытой до записи и включения; добавлены только main.lua и
enabled.txt в новом ImmersiveInteractionPromptsUserWidgetHostProbe.
22 прежних mod/loader files и63 config/save files сохранили хэши; старые IIP probes
отключены. Локальный rollback/manifest/log snapshot вне loader:
host-probe/install-20261029T081829Z. Игра не запускалась. Следующий шаг — один
Ctrl+Alt+F6 show → Ctrl+Alt+F6 cleanup тест по [процедуре](../research/interaction-prompts-owner/userwidget-host/probe/README.md).
Production/World gates остаются BLOCKED.

**2026-10-29 — independent UserWidget probe READY_SOURCE; runtime NOT_TESTED.**
[Исходник и процедура](../research/interaction-prompts-owner/userwidget-host/probe/README.md):
точная `_C` запись подтверждена в локальном AssetRegistry. Одна попытка
lookup/LoadAsset→Create, проверка свежего экземпляра/частного дерева, собственная
тестовая строка после Construct Hidden, Ctrl+Alt+F6 cleanup и однократный60s timeout.
Нет World/Aphes/TipHUD mutations.74 offline mock tests проходят; native Create,
Slate/rendering и освобождение UI-владения пока не проверены в игре.
Ничего не установлено/не запущено. Следующий шаг — отдельно разрешённый host-only
тест. Exact Open binding и production gate остаются BLOCKED.

**2026-10-29 — первый host-блокер SOURCE_RESOLVED: найден PostionItemUMG_BP_C.**
[Проверка host](../research/interaction-prompts-owner/userwidget-host/README.md):
прямая база UMG.UserWidget, concrete, без Genesis native-посредника; 14 exports,
4 собственные функции, no Tick/Paint/animations/bindings/nested UserWidgets.
Construct скрывает только self (Hidden); будущая видимость — после первого Slate
build. Нативный Create/Initialize инстанцирует собственное дерево и Slate cache.
Runtime загрузка/создание/очистка не проверены. Кандидат SOURCE_READY для отдельного
host-only lifecycle test, не World/runtime PASS. Полный World-прототип BLOCKED на
exact natural Open actor/component/pose и его собственных runtime gates.
На этапе поиска класса payload не создавался; follow-up исходник подготовлен выше.
Установка/запуск не выполнялись; никаких новых cooker/C++ зависимостей.


**2026-10-29 — World-space study завершён source/offline; executable payload
BLOCKED, production BLOCKED.** [Точный отчёт](../research/interaction-prompts-owner/world-space/README.md).
Предпочтительный дизайн — объектная подсказка с реальным перекрытием Хильдой;
X50%/Y78% остаётся проверенным fallback. Материалы stock Widget3DPassThrough
найдены и parent/depth defaults проверены: обычный World mesh с depth test возможен
без special mask. Но это не runtime PASS в Asterigos.

A (переключить оригинал) отклонён для первого опыта: SetWidgetSpace только пишет
Space; FWidgetRenderer создаётся в OnRegister для World. Из Screen renderer может
отсутствовать, и Tick не заменяет регистрацию/полный перенос screen-layer caches.
B (свой plain transient WidgetComponent) предпочтителен, но ещё не READY:
изначально не было подтверждённого host и exact Open binding. Host-класс теперь
найден source-only (выше); точная связь natural Open TipHUD→компонент/owner/pose
остаётся неизвестной. Live TipHUD нельзя делить между рендерерами,
а UserWidget base Abstract. Известные игровые native-базы не объявлены пустыми.
Следующий достаточный шаг — подтвердить один независимый конкретный UserWidget
через Create/Initialize и его lifecycle; затем exact Open binding/material/pose.
Lua/C++ payload не создан; игра/настройки/сохранения/другие моды не менялись.
Не исследовались CustomDepth/post-process/special mask, не повторялись font/UI runs.

**2026-10-29 — screen placement/render/manual cleanup PASS; пользователь выбрал
X50% / Y78% для продолжения. Arrow tuning NOT_PASSED. Probe отключён. Production BLOCKED.**
[Точный результат](../research/interaction-prompts-owner/viewport/README.md):
пять own children + один Canvas в Main_Panel, viewport2560×1440, исходный TipHUD
видим/нетронут.02:28:05 initial POSITION50,78;02:30:43 CLEANED reason=user,
оба brush refs/font released, все элементы и own Canvas удалены до180s timeout.
Стрелки двигали камеру по сообщению пользователя; в логе нет move/reset/commit.
Причина input routing не установлена, Home/F7 не приняты. Позиция выбрана словами
пользователя и кадром, без ложного успешного F7. Ремонт стрелок на этом этапе отложен.
Source242a5f0/helper/config/TTF/PNG/DLL и18 prior mod/loader files совпали.
Raw log/frame локально; при закрытой игре снят только свой enabled.txt.
Сохранить принятую геометрию при удалении debug indicator. Следующая осмысленная
граница — native state/show-hide для одного Open, ещё без production lifecycle.

**2026-10-29 — компактная композиция технически сработала в игре;
пользователь подтвердил видимый результат. Probe отключён. Production BLOCKED.**
[Точный результат](../research/interaction-prompts-owner/composition/README.md):
one local stock PNG import→TEXTURE_BOUND, Aphes/ornament/lower placement shown
in the user frame.00:33:27 LOWER_RESTORED→оба REMOVED→TEXTURE_UNBOUND/FONT_RELEASED→
CLEANED reason=target-state-changed за≈17.04с, до timeout; поздние user-key очистки
на нуле без повторного создания. Это не manual removal while attached/READ-тест.
Source996ee47, helper/config/TTF/PNG/DLL и15 старых mod/loader files совпали.
Лог/кадр сохранены локально; при закрытой игре снят только enabled.txt.
Оформление ещё не принято: особенно заметность тонкого орнамента и интервалы.
Следующий шаг — согласовать композиционные поправки, без повтора font/import
исследования и без автоматической установки новой версии.

**2026-10-28: Aphes OPEN→READ→manual cleanup технически прошёл runtime;
пользователь подтвердил визуальный успех. Probe отключён после выхода.
Композиция/разделитель/обводка/размеры открыты. Production BLOCKED.**

- [Runtime Aphes result](../research/interaction-prompts-owner/aphes-text/README.md):
  FONT_CONFIGURED→FONT_BOUND→DONOR_UNCHANGED, OPEN attached, READ same_element=true,
  оба REMOVED→FONT_RELEASED→CLEANED reason=user за ~27.2с, до timeout. Ошибок probe нет.
- Кадр2560×1440 показывает Aphes glyph shapes, original «Открыть»/F и divider;
  пользователь подтвердил визуальную процедуру. Исходник94770ed / hash9042d9da,
  config/TTF/DLL identities совпали. Архив log/frame локальный/ignored.
- Выход Alt+F4 записан явно: manual cleanup был раньше закрытия процесса, но
  normal-menu quit/GC/full lifecycle не принимаются этим тестом. 11 прежних mod
  files, loader settings и TTF неизменны; собственный enabled.txt снят при закрытой игре.
- Следующее направление — композиция на проверенном native-механизме, без повтора
  технического опыта. Финальные значения стиля и semantic Aphes translation не приняты.

## Историческая подготовка Aphes writer

- [Aphes-text](../research/interaction-prompts-owner/aphes-text/README.md): exact
  UE4SS nested setters и owning FString assignment проверены исходником и bounded
  static inspection установленной DLL. Копирование FString рассмотрено отдельно
  от успешного чтения/storage-теста; UObject nil setter не меняет shared FontFace.
- Новый probe создаёт одну собственную transient Template-копию с тем же package
  Outer, проверяет allocation-specific storage перед записями, меняет только её
  существующий FFontData и контролирует donor snapshot после попытки. Никакой
  перестройки native arrays/сырых offsets или записи в оригинальные UI/font нет.
- Ctrl+Alt+F6: OPEN → READ на том же own TextBlock → cleanup. Переиспользуются
  one-Open/30s, X38 и принятый resource-free divider. Удержание через собственный
  FontObject; очистка detach→typed SetFont(stock read) без раннего обнуления ссылки
  перед возможной ошибкой. Failed release сохраняет reference для явного retry.
- 10 новых mock groups проходят, включая partial setters, readback/bind failures,
  donor fault и cleanup retry. Реальная загрузка/глифы/GC не проверены. TTF/config/
  raw evidence ignored; production, VERSION и ранее существовавшие моды/настройки неизменны.
- Установлены exact source `94770eddf8ec9c74d75fa4ca145c4e81d1940fe4` / hash
  `9042d9da...`, private config и enabled.txt; сам TTF остаётся вне игры. Target ранее
  отсутствовал, guarded rollback/pretest log сохранены вне loader. 11 старых mod
  files, UE4SS settings и 57 current config/save files неизменны. Старые probes
  отключены; игра агентом не запускалась. Последующий runtime-результат приведён выше.

## Завершённый Template-copy creation/storage

**2026-10-28: UFont Template-copy runtime STORAGE_CHECK_PASS; probe отключён.
Одна отдельная transient копия и раздельный observed storage подтверждены логом.
Никаких FFontData/UI-записей или Aphes-загрузки. Production BLOCKED.**

- [Font-template probe](../research/interaction-prompts-owner/font-template/README.md):
  Ctrl+Alt+F7, один naturally loaded donor и одна transient копия; точный
  Template argument8, game-thread callback без hooks/timers/scans. NOT_LOADED
  завершает попытку. Num проверяется до index1, empty arrays не индексируются.
- Адреса native array header/buffer/entry/FontData сравниваются через проверенные
  pinned getters, не через identity Lua wrappers. Успех требует отличающегося
  storage, ожидаемой структуры/значений и повторной проверки донора. Shared
  FontFace ожидается; независимость FString backing/private state не объявляется.
- 10 новых offline test groups проходят: creation/type/shape/address/alias/API/
  dispatch failures, donor post-check и one-attempt policy. Это mocks, не native
  copy/GC/render. Предыдущие visual tests не повторялись. Все wrapper references
  callback-local, нет roots/manual GC; после выполненной попытки копия оставлена для
  обычного GC, немедленное освобождение не обещается.
- Установлен exact source `6c75063300c9aa84ec946f64ca108cc4d686e1e3`, hash
  `f7714817...`; target ранее отсутствовал, проверяемый откат/pretest log вне loader.
  Десять существующих mod files, настройки UE4SS и 61 config/save file неизменны.
  После пользовательского запуска source hash совпал, лог сохранён, probe отключён.
  Десять mod files и UE4SS settings всё ещё неизменны; для всех save bytes после
  обычной игры такого утверждения не делается. Игра агентом не запускалась.
- Runtime: 16:32:16 МСК, один CREATE_BEGIN/CREATED, STORAGE_DISTINCT,
  DONOR_UNCHANGED и DONE result=STORAGE_CHECK_PASS. Только наблюдённые storage/
  fields; не full deep-copy/setter/render/GC acceptance. Setter review и следующий
  отдельный source-прототип теперь находятся в Aphes-text выше; runtime writes открыты.

- [Dynamic font readiness](../research/interaction-prompts-owner/DYNAMIC_FONT_READINESS.md):
  17 известных font packages / 5 UFont / 12 FontFace; общий Umg_Font и Garamond
  имеют подтверждённых других потребителей. Для остальных отсутствие ссылок в
  ограниченных данных не доказывает независимость. Штатные ресурсы не менялись.
- UE4.27.2 source подтверждает filename-конструктор FSlateFontInfo, но его native
  shared pointer не отражён. C++ требует ещё подтверждённого engine linkage/ABI,
  pinned UE4SS/dependencies и совместимого компилятора; один SetFont этого не решает.
- Путь с Template-копией не требует этого конструктора: нативно скопировать
  небольшой Runtime UFont, проверить изоляцию, перенастроить только существующий
  FFontData копии и назначить её собственному TextBlock. Это source-supported
  гипотеза; optional Template, decode/render/cache и cleanup ещё не проверены.
  Для write/render этапа payload не создавался; нынешний probe только читает
  новую копию. Игра/моды/настройки не менялись.
- PNG-header ниже по-прежнему READY к своему отдельному тесту; это фиксированные
  глифы, не решение arbitrary dynamic text. Coherent — отдельный overlay route.

### Подготовленный PNG-header

- [PNG-header отчёт](../research/interaction-prompts-owner/png-header/README.md):
  точный UHT/UE4SS83330635 подтверждает ImportFileAsTexture2D, explicit CDO call,
  SetBrushFromTexture и удержание через Brush.ResourceObject. Один импорт за
  сессию, same one-Open/30s guards, независимая pair cleanup и очистка texture ref.
- Один PNG560×112 RGBA из exact Aphes.ttf, прозрачный, hash `6c6fdd18...`;
  OPEN — технические глифы, не перевод. PNG/TTF/private config ignored, в Git лишь
  оригинальные source/recipe. 30 offline tests проходят; native import/alpha/GPU/
  display/unbind не проверены. Нет установки, запуска игры или нового ПО.
- Для Nexus возможна локальная extraction→render схема без поставки glyph payload;
  targeted extractor/setup, зависимости, packaging и distribution review ещё
  не реализованы/не закрыты. Самостоятельный production release не готов.

### Завершённый divider baseline

- [Точный divider result](../research/interaction-prompts-owner/DIVIDER_READINESS.md):
  UImage default draw_as=3, ресурс отсутствует; explicit Box/readback успешен.
  Кадр показывает OPEN/линию/«Открыть»/F. Через ~5.5 с оба REMOVED, CLEANED
  reason=user own_children_remaining=0; не тайм-аут. Ошибок UIChild нет.
- Пользователь неуверенно вспомнил выключение; визуальное исчезновение пары
  отдельно не объявляется подтверждённым. Native detachment подтверждён логом и
  GetParent checks. Один случай, без GC/timeout/lifecycle/final-design acceptance.
- Исходник не менялся; disabled bytes/лог/кадр/откат сохранены локально, девять
  соседних mod files/settings неизменны. Повтор этого общего опыта не нужен.

### Подготовка разделителя (историческая)

- [Divider readiness](../research/interaction-prompts-owner/DIVIDER_READINESS.md):
  выбран UImage с native-initialized color-only Box brush, без текстур/ресурсов.
  Явные нулевые margins/белый цвет, 140×2 логических единицы, под OPEN. Defaults
  и readback проверяются, неожиданная ресурсная кисть отклоняется до attachment.
  Отрисовка линии не доказана существованием API и требует будущего наблюдения.
- Сохраняются one-Open/30s/identity/layout guards и отсутствие записи в оригинал.
  Очистка двух own children независима, partial failure не блокирует попытку
  убрать второго. 7+15 offline test groups проходят. Установлен source `180ffbf`,
  hash `94f7bd87...` совпал; девять других mod files/settings неизменны, откат и
  pretest log сохранены вне loader. Игра агентом не запускалась.

- [Успешный ui-child run](../research/interaction-prompts-owner/ui-child/README.md):
  source `6e55c18`, hash `b0e0f6c3...`, CREATED/SLOT_READY/ATTACHED и
  REMOVED/CLEANED reason=user, без FAILED. Native RemoveChild и проверка GetParent
  пройдены; отображение/исчезновение подтверждены пользователем. Один Open prompt,
  без Aphes/разделителя; immediate destruction/GC и полный lifecycle не проверены.
- Этот узкий label эксперимент завершён. Новый вопрос — видимость/толщина
  texture-free разделителя и очистка пары; прежний опыт не повторяется сам по себе.

### Предыдущие шаги и сохранённые ограничения

- Исправление ограничено доказанным Open baseline X=38; новый label берёт позицию
  из текущего оригинального слота, не записывая в него. Прочие guards сохранены.
  19 offline tests проходят. Кто устанавливает native X и поведение других
  целей/устройств пока неизвестны; создание/рендер/удаление ещё не достигнуты.

- [Разбор первого прогона](../research/interaction-prompts-owner/ui-child/README.md):
  клавиша/CanShow/выбор Open сработали; строгая проверка Position/Alignment не
  прошла. В первом логе значения отсутствовали; второй локализовал отличие X=38
  против 88. Создание/шрифт/рендер/GC и native RemoveChild не проверены.
- Предыдущая диагностическая ревизия добавляла вывод четырёх значений/типов перед
  той же проверкой. Источник `ea85872`, hash `837029dd...`, был установлен
  при закрытой игре; предыдущий отключённый payload/log/откат сохранены вне loader.
  Девять остальных mod files/settings неизменны по хэшам. Этот capture завершён,
  probe отключён; возвращаться к Aphes/native observer не нужно.

- [Новый ui-child прототип](../research/interaction-prompts-owner/ui-child/README.md):
  один новый TextBlock с OPEN в CanvasPanel_6 одного естественного «Открыть»;
  синхронная копия полного Font исходного TextBlock_89. Исходные Text/Font/Slot,
  родители, массивы, иконка/hold и управление не изменяются кодом.
- Один запуск/попытка за сессию, Ctrl+Alt+F9, окно 30 секунд; очистка своей
  дочерней ссылки при stop/timeout/изменении выбранного состояния/ошибке.
  Между вызовами только identity metadata, без UObject/Font/slot wrappers.
  Двенадцать новых mock-групп проходят; native создание/GC/рендер/возврат геометрии
  ещё требуют runtime-доказательства. Ошибка cleanup явно отмечается, не скрывается.
- Разделитель не добавлен: texture-free brush path не подтверждён. Aphes/cooker
  отложены по решению пользователя и не блокируют этот stock-font-only тест.
- Первый прогон использовал ui-child из `c9ecc0064eae59e8f6fc2a6557a1721b28d80534`,
  хэш `25ba56ca3de419fd187ee4ab29dfb88bc5ffa0c8a68cf19e2a9b7b72ac330f2d`.
  Новый отдельный folder/own enabled.txt; девять старых файлов модов и settings
  неизменны по хэшам, CanShow probe отключён. Откат к прежнему отсутствию UIChild
  и pretest log сохранены локально вне loader paths. Игра агентом не запускалась.

- [Visual readiness report](../research/interaction-prompts-owner/VISUAL_READINESS.md):
  семь reciprocal slot edges, штатный текст/иконки — отдельные дети CanvasPanel_6.
  Рекомендуется добавление соседних элементов, без reparent/изменения TextBlock_89
  и без вмешательства в input/hold/lock branch. Stock-font child/divider уже
  прошли ограниченный runtime-тест; Aphes render остаётся отдельным вопросом.
- Одного TTF/SourceFilename или записи reflected FontFilename недостаточно для
  доказательства корректной загрузки Aphes. Первоначальный cooked-план — новый
  локальный UE4.27 runtime composite UFont/FontFace только для верхней строки;
  [Локальная проверка toolchain](../research/interaction-prompts-owner/FONT_RESOURCE_READINESS.md)
  завершена: UE4.27 editor/cooker в проверенных местах не найден; существующий
  repak 0.2.3 только упаковывает файлы. Cooked font resource не создан. Текущий
  transient Aphes writer source теперь подготовлен отдельно, не установлен.
  OPEN остаётся временным техническим текстом, не переводом на Афес.
- Для возвращения к cooked Aphes-варианту потребуется совместимый UE4.27 editor/cook
  toolchain и локальный font resource. Автоматической установки не выполнялось.
  Measured-X38 source успешно прошёл первый attach/detach test и отключён;
  повторного capture координат не нужно.
  Full native observer/UEPseudo не возобновляются. Подробные ограничения native
  geometry, individual visibility и будущего узкого runtime-теста — в отчёте.

- Принята цель двух рядов с сохранением native localized action/input; выбран
  исследовательский additive layout path, размеры/приёмка и способ осмысленной
  внутримировой надписи остаются открытыми.
- VERSION = 0.1.0 — начальная метка, без кандидата/билда/релиза.
- [Статический отчёт](VERIFIED_RUNTIME.md) установил BaseGameEventObject_BP →
  ExtendedWidget → TipHUD; proxy → InteractTipToText/StringTable → native
  SetupTipMessage2. Последний доказанный consumer не равен доказанному final writer.
- BaseLoot2/сундук/документ имеют Take/Open/Check и RU «Взять/Открыть/Проверить».
  Ladder_BP идёт через отдельный native BaseClimbObject; общий prompt path и
  точное действие спуска не установлены.
- Aphes.ttf существует; 97 cmap entries, латинские буквы/цифры, кириллицы нет.
  Глифы просмотрены offline. UMG FontObject и перевод действий на язык Афеса
  не доказаны; транслитерация/декоративная стилизация не приняты автоматически.
- Предпочтительная исследовательская гипотеза — узкое расширение native TipHUD.
  Asset override — резерв; overlay пока требует больше недоказанных связей.
  Это сравнение механизмов, не разрешение на production implementation.
- Точные блокеры: native final writer/поздние перезаписи; live owner для четырёх
  семейств, особенно спуска; input/remapping/device→texture; show/hide/lifetime;
  пригодный Aphes font path в UMG и продуктовый смысл верхней строки.
- [Проверка готовности probe](../research/interaction-prompts-owner/README.md)
  ранее установила разрыв: не было отражённой native-сигнатуры SetupTipMessage2; выводить
  Lua ABI из Blueprint-вызова нельзя. По исходнику установленной версии UE4SS
  Blueprint callbacks доступны post-only, результат CanShow аргументом не приходит;
  маршалинг параметров происходит до Lua callback. Полный native probe не создан.
- [Проверка reflection API](../research/interaction-prompts-owner/METADATA_CAPTURE.md)
  подтвердила поиск UFunction, GetFunctionFlags, обход свойств, GetInner и
  однократную очередь ExecuteInGameThread по исходнику 83330635. Но FProperty и
  его Lua-базы не предоставляют чтение Parm/OutParm/ReferenceParm/ReturnParm.
  Полный Lua capture этим API недоступен; ограничение остаётся, но обходить его
  новым C++-модом для получения декларации больше не требуется.
- [UHT-результат](../research/interaction-prompts-owner/UHT_SIGNATURE.md):
  `void SetupTipMessage2(TArray<UTextBlock*>, TArray<UPanelWidget*>, ETipWidgetMode,
  TArray<FText>, TArray<UTexture2D*>)`; порядок и отсутствие const/ref/out/return
  подтверждены выводом и правилами генератора 83330635. Полная числовая маска
  UFunction/параметров и работоспособность hooks не проверены.
- Выполнен один разрешённый пользовательский запуск игры; лог содержит три
  последовательные завершённые UHT-генерации, анализируется последняя. Новых модов
  не установлено. Loader config восстановлен побайтово, старые моды/сохранения/
  игровые конфиги неизменны по хэшам. Сырая выгрузка и лог остаются локальными.
- [Проверка маршрута полного observer](../research/interaction-prompts-owner/OBSERVER_READINESS.md)
  установила borrowed-путь native frame → RemoteUnrealParam → TArray → элемент.
  Не подтверждено происхождение/время жизни callee Locals для Blueprint-вызова
  этого native consumer: необходимая зависимость UEPseudo на точном gitlink SHA
  недоступна через проверенные GitHub/Git/local routes. Это пробел доказательств,
  не установленный сбой UE4SS. Этот маршрут отложен; native hooks не регистрировались.
- Также подтверждено: индексный Get у TArray может расширить массив при выходе
  за границу; наличие обработчика типа/IsValid у массива не доказывает безопасное
  read-only чтение. Все будущие обращения должны быть строго ограничены размером
  и временем жизни исходной памяти; temporary parameter wrappers не сохраняются.
- Пользователем принят меньший эксперимент: только текущий текст и состояние
  TipHUD в zero-input Blueprint CanShow post, без native-массивов/отложенного
  UI-чтения. [Исходник и инструкция](../research/interaction-prompts-owner/can-show-state/README.md)
  подготовлены, семь групп Lua 5.4 mock-тестов проходят. Одна диагностическая
  клавиша запускает/останавливает наблюдение; лимиты 10 минут / 600 строк /
  8 identities, один снимок полей в секунду. UI writes и return overrides отсутствуют.
- UEPseudo и полный native observer отложены. По прямому разрешению пользователя
  CanShow payload из `4cda59f27f4719a728a88d671e04cca901e08ab8` установлен при
  закрытой игре; хэш совпал, прежние моды/config не изменены, лог сохранён локально.
  [Первый runtime-результат](VERIFIED_RUNTIME.md) подтвердил script hook и чтение
  TextBlock_89/state: `???` → «Взаимодействовать», «Открыть», «Взять» в трёх
  разных widgets; visibility 4(SelfHitTestInvisible) → 0(Visible), opacity=1,
  enabled=true. Это не доказательство скрытия и не видимый placeholder на экране.
  FAILED probe нет. Лог сохранён; enabled.txt вынесен из loader, probe отключён.
  Final writer, actor ownership, полный lifecycle, текстуры и спуск не входят
  в доказательства уменьшенного эксперимента.
- Веб-поиск уточнил prerequisite доступа: официальная документация UE4SS требует
  связки GitHub/Epic Games для UEPseudo. Подходящего публичного зеркала точного
  commit не найдено. Это исходная зависимость, не отдельный Nexus-мод; повторное
  скачивание готовой DLL не закрывает пробел. Состояние связки аккаунтов пользователя
  не проверялось.
- Текущий исследовательский шаг завершён. Простое чтение текущего TipHUD работает;
  расширять диагностику автоматически не требуется. Перед следующим изменением
  определить конкретный остаточный вопрос: layout/font и безопасное расширение
  native widget пока не доказаны. Final writer/owner не объявлены установленными.
- Production, другие моды и VERSION не изменены; hot reload не применялся.
  Нет runtime-приёмки будущего мода; получение SDK её не заменяет.
- Reusable статические факты переносятся в канонический Asterigos-Research;
  владельцем подробных первичных доказательств и gate остаётся этот модуль.
