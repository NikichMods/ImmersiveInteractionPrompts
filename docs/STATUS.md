# Статус Immersive Interaction Prompts

**2026-10-28: офлайн-проверка готовности observer завершена с техническим блокером;
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
  установила разрыв: нет отражённой native-сигнатуры SetupTipMessage2; выводить
  Lua ABI из Blueprint-вызова нельзя. По исходнику установленной версии UE4SS
  Blueprint callbacks доступны post-only, результат CanShow аргументом не приходит;
  маршалинг параметров происходит до Lua callback. Исполняемый probe не создан.
- Следующий достаточный шаг — узкий reflection-only захват метаданных ровно трёх
  UFunctions без hooks и вызова этих функций, после отдельной подготовки и
  разрешённой установки при закрытой игре; либо доступная точная native-декларация.
  Затем подготовка одного observer. Визуальный font/layout тест остаётся отдельно.
- Production, sibling mods, установленные файлы и VERSION не изменены; игра не
  запускалась/не закрывалась, hot reload не применялся. Нет runtime-приёмки.
- Reusable статические факты переносятся в канонический Asterigos-Research;
  владельцем подробных первичных доказательств и gate остаётся этот модуль.
