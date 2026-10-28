# Статус Immersive Interaction Prompts

**2026-10-28: подготовлен минимальный CanShow observer, офлайн-проверки пройдены;
production evidence gate BLOCKED.**

- Принята цель двух рядов с сохранением native localized action/input; конкретный
  layout и способ осмысленной внутримировой надписи ещё не выбраны.
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
- UEPseudo и полный native observer отложены. Наличие callbacks/показ/текст
  ещё не проверены в игре. Следующий шаг — отдельно разрешённая установка
  точного CanShow payload при закрытой игре, затем короткое обычное наблюдение.
  Final writer, actor ownership, полный lifecycle, текстуры и спуск не входят
  в доказательства уменьшенного эксперимента.
- Веб-поиск уточнил prerequisite доступа: официальная документация UE4SS требует
  связки GitHub/Epic Games для UEPseudo. Подходящего публичного зеркала точного
  commit не найдено. Это исходная зависимость, не отдельный Nexus-мод; повторное
  скачивание готовой DLL не закрывает пробел. Состояние связки аккаунтов пользователя
  не проверялось.
- Production, другие моды и VERSION не изменены; hot reload не применялся.
  Нет runtime-приёмки будущего мода; получение SDK её не заменяет.
- Reusable статические факты переносятся в канонический Asterigos-Research;
  владельцем подробных первичных доказательств и gate остаётся этот модуль.
