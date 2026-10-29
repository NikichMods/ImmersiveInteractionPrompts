# План исследования — contextual prompts и письменность

## Текущий шаг — independent host найден; World-прототип ещё BLOCKED

[Ограниченная проверка host](../research/interaction-prompts-owner/userwidget-host/README.md)
нашла concrete PostionItemUMG_BP_C на прямой базе UMG.UserWidget, с проверенными
self-only callback/tree/Slate creation контрактами. Поиск остановлен на одном
подходящем классе, без общего реестра UI или нового authoring toolchain.
Первый архитектурный host-блокер source-resolved. Следующий достаточный шаг —
отдельный host-only тест residency/Create/private tree/first build/cleanup;
не выдавать это за World occlusion. Construct Hidden обязательно учесть.

Независимый следующий блокер — точная привязка natural Open actor/component/pose;
в текущем этапе она не исследовалась. World renderer/material/registration review
сохранён в [World report](../research/interaction-prompts-owner/world-space/README.md).
Новый исполняемый payload не создан, установка и игра не выполнялись.
Предпочтительный объектный дизайн и fallback X50%/Y78% неизменны; font/divider/
viewport исследования не повторялись. Production lifecycle остаётся BLOCKED.

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
