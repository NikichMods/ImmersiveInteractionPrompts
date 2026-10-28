# Статус Immersive Interaction Prompts

**2026-10-28 — компактная композиция: READY для отдельного ограниченного теста,
не установлена и не запущена. Production BLOCKED.**
[Источник и границы](../research/interaction-prompts-owner/composition/README.md):
штатный орнамент найден в Coherent как один PNG570×16; подготовлен его локальный
импорт в собственный UImage. Aphes32/outline1 над линией; линия на высоте центра F,
«Открыть» ниже через один обратимый render translation. Ось по тексту без клавиши.
Slot/Font/Text оригинала не меняются. При конфликте со штатной записью — остановка,
без повторного навязывания позиции. Восемь новых mock groups проходят;
alpha/render/масштаб/стабильность/точный возврат нижней строки требуют runtime.
Принятые Aphes OPEN→READ, UIChild и resource-free divider не повторялись.

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
