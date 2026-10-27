# Статус Immersive Interaction Prompts

**2026-10-28: штатный UHT-генератор дал точную декларацию SetupTipMessage2;
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
  маршалинг параметров происходит до Lua callback. Исполняемый probe не создан.
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
- Следующий этап — подготовка одного observation-only observer с проверкой
  фактического loaded UFunction/FUNC_Native и поддержки wrappers; установка и
  игровой прогон отдельно. Final writer, live owner/lifecycle и спуск открыты.
- Production, другие моды и VERSION не изменены; hot reload не применялся.
  Нет runtime-приёмки будущего мода; получение SDK её не заменяет.
- Reusable статические факты переносятся в канонический Asterigos-Research;
  владельцем подробных первичных доказательств и gate остаётся этот модуль.
