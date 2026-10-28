# План исследования — contextual prompts и письменность

## Текущий этап — одна штатная верхняя строка, READY для research runtime

Пользователь выделил независимый [stock-font child experiment](../research/interaction-prompts-owner/ui-child/README.md).
Исходник подготовлен и установлен по прямому разрешению при закрытой игре:
новый TextBlock в CanvasPanel_6 одного «Открыть», полный
typed Font copy, без изменения оригинала; один запуск, stop/timeout/own-child
cleanup. Разделитель исключён до подтверждения brush path. Следующий достаточный
шаг — первый пользовательский UI attach/detach test и анализ сохранённого лога; не нужно
решать Aphes/cooker или повторять старый CanShow-read probe. Native rendering/GC/
влияние на desired size остаются вопросами этого опыта. Production BLOCKED.

## Отложенный Aphes-вариант — font bridge BLOCKED

[Visual readiness](../research/interaction-prompts-owner/VISUAL_READINESS.md)
подтвердил slot ownership. Выбран узкий путь: добавить верхний label/разделитель
соседями TextBlock_89 в CanvasPanel_6, сохранив исходные localized text/input/
hold/lock и родителей. Полная замена TipHUD/overlay не оправданы.
Исполняемый prototype не создан: отсутствует проверенный Aphes UMG font object.
Проверка доступного toolchain [завершена](../research/interaction-prompts-owner/FONT_RESOURCE_READINESS.md):
UE4.27 editor/cooker в проверенных местах не найден. Следующий достаточный шаг —
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
