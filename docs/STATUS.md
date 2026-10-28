# Статус Immersive Interaction Prompts

**2026-10-28: диагностический прогон измерил живой slot: Position=(38,0),
Alignment=(0,0.5), оба getter возвращают table. OPEN не создавался из-за ожидания
designer X=88. Исправленный source установлен по прямому разрешению при закрытой
игре; первый creation test ожидается. Предыдущий payload сохранён для отката.
Production evidence gate BLOCKED.**

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
  и без вмешательства в input/hold/lock branch. Это выбранный исследовательский
  путь, не проверенная runtime-реализация.
- Одного TTF/SourceFilename или записи reflected FontFilename недостаточно для
  доказательства корректной загрузки Aphes. Предпочтительное продолжение — новый
  локальный UE4.27 runtime composite UFont/FontFace только для верхней строки;
  [Локальная проверка toolchain](../research/interaction-prompts-owner/FONT_RESOURCE_READINESS.md)
  завершена: UE4.27 editor/cooker в проверенных местах не найден; существующий
  repak 0.2.3 только упаковывает файлы. Font resource и визуальный payload не созданы.
  OPEN остаётся временным техническим текстом, не переводом на Афес.
- Для будущего Aphes-варианта потребуется совместимый UE4.27 editor/cook
  toolchain и локальный font resource. Автоматической установки не выполнялось.
  Ближайший шаг UI-эксперимента — отдельно разрешённое обновление на исправленный
  source выполнено; дальше первый реальный attach/detach test. Повторного capture
  координат не нужно.
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
