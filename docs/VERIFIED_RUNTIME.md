# Verified Runtime — Interaction Prompts

## Первый статический этап, 2026-10-27

**Статус: подтверждённые статические связи; runtime-путь и production gate BLOCKED.**
Исследование не меняло production, VERSION, установленные моды или игровые состояния;
игра не запускалась/не закрывалась, probe не устанавливался, hot reload не выполнялся.
Ниже «подтверждено» означает проверку конкретных данных/bytecode, а не наблюдение
видимой подсказки в игровом процессе. Имена сами по себе не использовались как
доказательство поведения.

**Вопрос и граница:** установить UI/data ownership, последний доступный consumer,
локализацию/input, различия четырёх семейств и доступные глифы. Это решает, можно ли
расширять native widget вместо воспроизведения взаимодействий в overlay. Достаточный
результат этапа — доказанная статическая цепочка либо точный разрыв и один безопасный
план наблюдения; не требуется угадывать C++ реализацию или менять UI ради проверки.

## Среда и восстановление

- Исследовательская основа: `origin/main`, commit
  `228c38e26bb2f3b07cbda73994d775cd8ec89079`; отдельный worktree,
  `research/interaction-prompts-owner`. Исходный checkout `feature/boss-aphes-name`
  на `c85b3525a351fe00fd992a975665b9dbd7c185cb` был чистым и не переключался.
  Другие worktrees, их ветки и незавершённая работа не изменялись; reset/stash/clean
  не применялись. Выполнены fetch и актуальная проверка remote heads.
- DevRules прочитаны с учётом актуального `origin/main`
  `8f75456` (включая automatic Research promotion); локальный main DevRules
  отставал на три коммита и не переписывался. Shared Research прочитан на
  `1c4cee6902a2a5c9730d569bfecd7e8713698d93`: R-001..005 не доказывают prompts.
- Baseline: Steam 1.09/build12996889, UE4.27 Windows x64. SHA256 exe:
  `DDEA6B5CA5D34836F01702993D20209C2595367287E6CD5A135A7ACE1958B1C0`;
  stock `pakchunk0-WindowsNoEditor.utoc`:
  `0E9D27F84B97F24651AE1CA0ED38FACAD171E620702CAB08198B14B56E52513E`.
  Они совпали с ранее принятой идентичностью. Не хешировался заново весь 10-GB ucas;
  это не побайтовый аудит всей установки. UE4SS не исполнялся этим исследованием.
- CUE4Parse 1.2.2, UE4.27, `ReadScriptData=true`, bytecode с `StatementIndex`;
  базовые ресурсы прочитаны из stock Paks отдельно от `~mods`. Локальный reader
  расширен только для inventory/raw/locres; NuGet использовал имеющийся cache.
  FontTools 4.67.0 + Pillow использованы для cmap/outline и локального contact sheet.
  Это инструменты статического чтения, не игровой исследовательский мод.

## 1. Подтверждённый UI owner и цепочка

База `/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP` наследует
`/Script/Genesis.BaseGameEventObject`. Её SCS явно содержит:

- `ExtendedWidget`, тип `/Script/Genesis.ExtendedWidgetComponent`,
  `IsActivated=true`, `WidgetClass=/Game/MainContent/Template/UMG/TipHUD.TipHUD_C`,
  `DrawSize=1000×1000`. Пространство world/screen и live размещение не установлены
  из этих сериализованных значений.
- `TipHUDArgument`, тип `/Script/Genesis.TipHUDArgumentComponent`,
  `msgTag=Interact`, `IconNameIndex=InteractButton`,
  `ActionName=EGenesisInputCommandType::Interact`, сетка `8×8`.

Положительная executable связь: `ReceiveBeginPlay` входит в
`ExecuteUbergraph_BaseGameEventObject_BP` на **92**; **102** вызывает
`ExtendedWidget.GetUserWidgetObject`, **144** cast к `TipHUD_C`, после проверки
успеха **219** записывает `TipHUD.CanHoldPress` из native `HoldPress` владельца.
Это доказывает связь компонента/виджета/режима удержания, но не всю C++ цепочку
выбора цели и установки аргументов.

`TipHUD_C` наследует `/Script/Genesis.ExtendedUserWidget`. Внутри widget:
`TextBlock_89`, `ImageInteractAllowed` под `RetainerBox_0`, `CanvasPanel_2` с
`ImageInteractNotAllowed`, общий `CanvasPanel_6`. Значения текстового placeholder
`???` и дизайнерской PS4-иконки — **не** реальные действие или выбранное устройство.

Отдельный `IndicateTip_UMG` содержит четыре элемента указаний с `Zone_Text` /
`Desc_Text`; у него не найден описанный выше call path действия/кнопки. Он не выбран
в качестве interaction owner. `HudUmg` из SoulsEnemyHUD относится к damage digits;
его похожее имя не связывает его с prompt.

## 2. Текст и последний установленный consumer

`TipHUD_C:SetupTipMessage_Proxy` имеет сериализованную сигнатуру:
`display_mode:ETipWidgetMode`, `msgTags:Name[]`, `base_texture:Texture2D[]`,
`img_ico_per_row:int[]`, `img_rows:int[]`, `ico_x:int[]`, `ico_y:int[]`,
`isLocked:bool`. Порядок и типы — из `ChildProperties`, не предположение о Lua ABI.
Событие копирует аргументы в persistent frame и входит в ubergraph на **819**.

Далее ubergraph:

1. **819–878:** выбирает visibility запретной накладки по `isLocked` (false → raw1,
   true → raw0); enum-имена не угадывались по числам.
2. **773 → 593:** очищает `ImagePanels`, добавляет `RetainerBox_0`.
3. **661:** собирает массив TextBlock ровно из `TextBlock_89`.
4. **681:** вызывает `ConvertMsgTagToTextArray(msgTags)`.
5. **713:** native `/Script/Genesis.ExtendedUserWidget:SetupTipMessage2`
   получает этот TextBlock-массив, ImagePanels, display mode, массив FText и
   native `base_texture`. **768** выходит к return **1206**.

`ConvertMsgTagToTextArray` итерирует входные имена, **253** читает row из
`/Game/MainContent/Tables/UMG/InteractTipToText`, при успешном lookup **332**
добавляет `TagToText.Text` в результат, **410** передаёт собранный массив наружу.
Row-not-found не доказывает ни vanilla fallback, ни сохранение прежней строки:
поведение consumer при пустом/коротком массиве остаётся неизвестным.

DataTable содержит FText-ссылки в StringTable
`/Game/MainContent/Tables/UMG/InteractTipToText_cs.InteractTipToText_cs`;
namespace StringTable — `NewStringTable`. Проверен фактический русский перевод в
`Genesis/Content/Localization/UI/ru/UI.locres`, а не китайское `LocalizedString`
из экспортера, запущенного без RU culture:

| Row | StringTable key | RU ресурс |
| --- | --- | --- |
| Take | Tip_12_Take | Взять |
| Open | Tip_04_Open | Открыть |
| Check | Tip_15_Check | Проверить |
| Climb | Tip_01_Climb | Вскарабкаться |

**Final writer не закрыт.** `SetupTipMessage2` — последний *доказанный вызванный
consumer* текста и textures в доступном Blueprint. Его native тело, фактический
`SetText`/Slate commit, построение glyph и возможные последующие писатели не
декомпилированы/не наблюдались. Нельзя объявлять `SetupTipMessage_Proxy` final writer,
считать post-hook автоматически достаточным или переписывать общий TextBlock setter.

## 3. Кнопка и lifecycle: доказанное и разрывы

- Родитель задаёт семантическую команду Interact и icon index, proxy принимает
  texture-массив, native consumer получает реальные textures. Где native код
  переводит command/device/remapping в texture и как инвалидирует её при смене
  устройства — **не установлено**.
- Stock `/Game/MainContent/Tables/DefaultInputMapping`: `K-Interact` → `F`,
  `PC-Joystick-Interact` и `X-Interact` → `Gamepad_FaceButton_Bottom`;
  `KeyBinding_KeyboardMouse` / `KeyBinding_XboxController` имеют изменяемые
  Interact rows (`CanNotModify=false`). Это defaults, не текущая настройка игрока.
  `base_texture` должен оставаться host-owned; фиксировать F/A/PS-иконку нельзя.
- `TipHUD_C:CanShow`: **0** parent `ExtendedUserWidget:CanShow`, **20**
  `GameGlobal:GetInputMode(true,false)`, **50** сравнение результата с byte1,
  **81/119** возврат логического AND parent result и `mode != 1`.
  Значение enum1 и native parent predicates в этом этапе не раскрыты.
- Tick входит в ubergraph на **972**. При валидном GameInstance читает
  `GetDebugParameter_Bool(DebugHideUMG)`: **1127/1147** пишет собственный
  RenderOpacity 0/1. Нельзя принять захваченную alpha за постоянную baseline
  или бороться с этим native писателем непрерывной записью.
- **407–534:** если widget enabled и `CanHoldPress`, получает effect material
  `RetainerBox_0`, native `GetToDoInteractActionPressTimer`, записывает scalar `t`.
  `RetainerBox_0.EffectMaterial=/Game/MainContent/Template/UMG/TipIconMat`,
  `TextureParameter=Icon`. Это цепочка прогресса удержания, её нельзя потерять.
- Construct → **1167** `IsHandheldMode`, при true → **10–361** копирует font
  info `TextBlock_89`, меняет Size на **56**, вызывает `SetFont`. Сериализованный
  desktop size — **22**, outline **2**, wrap **800**. FontObject в этом TextBlock
  явно не сериализован; активный font нельзя объявить Umg_Font по соседним widgets.
- **Не установлено:** кто создаёт/уничтожает live widget внутри компонента,
  native selection/range/priority, когда proxy повторяется, show/hide/fade на
  входе/выходе, смене цели, interaction completion, меню и respawn. Общий
  HUD_Panel из CombatHUD не доказан предком этого компонента. Blueprint-картина
  не заменяет реальный lifecycle.

## 4. Различия действий

| Семейство | Положительное статическое доказательство | Граница |
| --- | --- | --- |
| Подбор | `.../Act/Scene_BP/BaseScene_BP/BaseLoot2_BP` наследует `BaseGameEventObject_BP`; inherited TipHUDArgument override `msgTag=Take` | RU ресурс «Взять»; конкретный placed object может переопределить данные |
| Открытие | `.../Act/Scene_BP/BaseScene_BP/BaseLoot_BP` тот же родитель; override `msgTag=Open` | Подтверждена база сундуков, не все двери/рычаги и не каждый live сундук |
| Чтение | `.../Template/BaseBlueprint/BaseDocumentObject` → `BaseInteractiveItem_BP` → `BaseGameEventObject_BP`; override `msgTag=Check` | RU «Проверить», не «Прочитать». Наличие документа не доказывает буквальный текст «читать» |
| Спуск | `.../Act/Scene_BP/Ladder_BP` → `BaseClimbObject_BP` → native `/Script/Genesis.BaseClimbObject` | В этих экспортах нет доказанной связи к TipHUDArgument/TipHUD. `ForwardText/UpText/DownText=None` не означает, что native не создаёт UI. Descend отсутствует среди 18 rows InteractTipToText; нельзя подменить спуск Climb |

Первые три базы связаны с одним owner положительной цепочкой наследования,
component override и widget-class assignment. Это не подтверждение всех объектов
каждого вида в сессии. Лестница — отдельный открытый путь; требуемый охват четырёх
действий ещё не достигнут.

## 5. Настоящие шрифты и глифы

- Stock содержит `Genesis/Content/Fonts/Aphes.ttf`; внутренние имена
  `Aphes / Medium / Aphes Medium / Aphes-Medium`. `cmap` содержит **97 кодовых
  позиций**: U+0000, U+001D, U+0020..U+007E; **72 glyphs** всего.
  `a..z` указывают на те же глифы, что `A..Z`; A–Z и 0–9 имеют непустые outlines.
  Кириллицы/греческого Unicode/PUA в этом cmap нет. Наличие mapping у знака
  пунктуации само по себе не обещает непустой outline.
- Контактный лист реально отрисован Pillow из stock TTF и визуально просмотрен:
  декоративные знаки, в том числе игровые цифры, действительно присутствуют.
  Это **offline** font inspection, не Coherent/UMG рендер и не перевод языка.
- В stock inventory нет `Aphes.uasset`, `Aphes_Font.uasset` или отдельного
  Aphes FontFace. Есть сырой TTF; доступность корректного UMG `FontObject` для
  него не доказана. Работа URL TTF в браузере/соседнем Coherent addon не доказывает
  доступность UFont в `TipHUD`.
- `/Game/Fonts/Umg_Font`: runtime composite UFont; Default → EBGaramond-SemiBold,
  Desc → FiraSans-Regular; fallback → `_ZH-HANT_NotoSansCJKtc-Medium`, culture
  subfaces ja → NotoSansJP-Medium, zh-Hans → NotoSansSC-Medium. Эти реальные
  ресурсы не требуют глобальной замены шрифта и не доказывают, что prompt сейчас
  использует этот FontObject. FontFace и composite UFont — разные типы.
- Техническая латинская cmap-раскладка Aphes **не является словарём языка**.
  Таблица соответствия «действие → каноническое слово Афеса» не найдена в
  исследованных prompt/string/font ресурсах. Это ограниченный поиск, не утверждение
  об отсутствии языка во всей игре. RU транслитерация, английская подстановка или
  декоративная маркировка остаются продуктовым выбором, а не принятым решением.
  Общая смена font у русской строки не даст поддерживаемую Aphes надпись.

## 6. Пересечения и минимальные механизмы

Текущий inventory `~mods` перечитан CUE4Parse: среди исследованных prompt/base/input/
font paths override не найден. `z320_SubtitleSoftEdges` и `z330_SoulsEnemyHUD`
содержат `Genesis/Content/uiresources/Hud.html`; это общий файл этих двух модов,
а не доказанный ресурс TipHUD. Наличие их двух entries не доказывает порядок mount.
Известный SoulsEnemyHUD 0.3.0 HTML и Subtitle input остаются отдельными владельцами.
Исследование не меняло их payload. Lua CombatHUD управляет другими HUD-группами;
полная runtime-совместимость с компонентными prompts пока не проверена.

| Механизм | Что сохраняет / цена | Решение исследования |
| --- | --- | --- |
| Узкое расширение существующего TipHUD | Может унаследовать native text/button/hold и visibility от реального owner; нужен доказанный момент обновления, layout slot, native lifetime и подходящий FontObject | **Предпочтительная следующая гипотеза**, не готовая реализация и не принятый дизайн |
| Override ресурса TipHUD | Может выразить два ряда и линию в существующей структуре; понадобится воспроизводимое cooked-asset изменение, сохранение binding/parent behavior, проверка distribution/provenance | Резерв после проверки native seam; нельзя считать маленький asset override автоматически безопасным |
| Отдельный overlay | Оригинальный код можно отделить, но придётся синхронизировать target, text, input, position, show/hide и cleanup; для лестницы цепочка ещё неизвестна | Сейчас больше независимых предположений; не выбирать до доказательства недостаточности native варианта |

Data-only смена `msgTag`/StringTable не выражает два ряда/линию, меняет смысл native
строки и может затронуть другие consumers. Правка `Hud.html` не имеет доказанного
prompt consumer. Общий font override/TextBlock hook слишком широк. Эти варианты
не проходят host-native-first и per-change gate только на основании простоты.

## 7. Production evidence gate и один следующий probe

| Поле gate | Итог |
| --- | --- |
| Observable property | Два ряда вокруг неизменённого native localized action/input, layout ещё не принят |
| Canonical owner | Статически установлен для трёх баз; спуск и live instance correlation открыты |
| Final writer/consumer | Native SetupTipMessage2 установлен как consumer; фактические writers и поздняя перезапись открыты |
| Blast radius | Общие base widget/data/font paths выявлены; все native consumers и climb path не перечислены |
| Preserved invariants | Localization, remapping/device, hold/lock, selection, show/hide, соседние UI обязаны сохраниться; пока не доказано |
| Acceptance | Runtime и визуальная приёмка отсутствуют; offline font inspection их не заменяет |

**BLOCKED.** Без production-source mutation, билда, повышения VERSION или установки.

**Research-method checkpoint:** статические данные уже ответили на resource/Blueprint
вопросы; повторный полный экспорт их не улучшит. Один пользовательский просмотр
может доказать слова/вид, но не адреса owner, порядок native записи и смену lifetime.
Поэтому следующий минимальный эксперимент — **один observer-only probe**, пока
только спецификация, не написан и не установлен:

1. При будущей отдельно разрешённой подготовке проверить реальные reflection
   signatures и UE4SS callback shapes у точных `TipHUD_C:SetupTipMessage_Proxy`,
   `ExtendedUserWidget:SetupTipMessage2`, `TipHUD_C:CanShow`. Только доступные
   точные seams; при несовпадении прекратить этот observer, не угадывать ABI.
2. Наблюдать native вызовы pre/post, не вызывать их самостоятельно: identity
   actor → его ExtendedWidget → точный TipHUD → TextBlock_89/RetainerBox_0;
   msgTags/FText/textures/display mode/isLocked, actual TextBlock font/text,
   visibility/opacity/enabled. После post-call ограниченный read-only sample
   до следующего обновления выявляет позднюю перезапись, но не доказывает
   отсутствие transient writes между samples. Не перехватывать все TextBlocks.
3. Один проход доступных pickup/chest/document/ladder: подойти, отойти,
   перевести цель; переключить keyboard/pad, открыть/закрыть доступное меню.
   Для hold/locked — только естественно доступный случай. Визуально сопоставить
   widget с prompt и слова. Не создавать объекты, не писать game flags/keys,
   не выполнять взаимодействие автоматически. При недоступной лестнице не
   выдавать три семейства за покрытие четырёх.
4. Для лестницы установить фактический живой owner отдельно: read-only inspection
   точного взаимодействуемого actor/components/reflected references. Не создавать
   TipHUD и не навешивать предполагаемый class по имени. Если identity цепочка
   не доступна, сохранить узкий разрыв, не расширять probe до глобального сканера.
5. Логировать переходы/изменения с bounded lifetime и per-object error isolation,
   отбрасывать invalid/replaced widget; отсутствие событий не считать hide proof.
   Не нужны overlay, шрифтовая подмена, принудительная alpha или иной writer.
   Stop condition — четыре реальные связи либо точный недоступный seam, native
   update→readback, device смена и уход/смена цели с подтверждённым скрытием.

Подготовка/установка/запуск этого probe **не входят в выполненный этап**. Следующий
runtime шаг требует разрешённой установки при закрытой игре с backup/hash/rollback;
игру запускает пользователь. Визуальный font/layout эксперимент — отдельная гипотеза
после owner/final-writer результата, не добавка к read-only probe.

## 8. Локальные доказательства и воспроизведение

Raw inputs, exports, исходник reader и contact sheet остаются в ignored root
`.local/research/interaction-prompts/` исходного checkout (не внутри disposable
worktree). Machine paths/секреты в публичный Git не включены. Recovery — root
`.local/environment.json`, его `legacyArchive` и уже существующий внешний key file.

- `reader/reader.csproj`: CUE4Parse 1.2.2/net8.0; `dotnet build`.
- Запуск `reader.dll <stock-Paks> <external-key-file> <ignored-output> <filter>`;
  filters: `BaseGameEventObject_BP`, `BaseLoot`, `BaseDocumentObject`,
  `BaseInteractiveItem_BP`, `BaseClimbObject_BP`, `/Scene_BP/Ladder_BP`, `TipHUD`,
  `InteractTipToText`, `/Fonts/`, `DefaultInputMapping`, `KeyBinding_`.
- `--list` вместо filter сохраняет inventory; отдельно повторить для `~mods`.
- `--raw <virtual-path>` сохраняет только выбранный file; locres дополнительно
  декодируется `FTextLocalizationResource(FByteArchive)`. Проверялись UI/ru/UI.locres
  и Fonts/Aphes.ttf, а также конфиги; ключ читается из файла, не выводится.
- `summarize.py` сохраняет offsets при чтении AST; его краткий вывод проверен
  по полным nodes для SetArray **661**, SetupTipMessage2 **713** и lock **878**.
  Reader Program.cs SHA256:
  `00230d82dcd0362eebfad63aff4bf8b6339771fc2b4dd21e133e33f3ec99a47a`.
- Полный локальный manifest `evidence-hashes.json`, production snapshot
  `installed-before.json`; итоговое сравнение `installed-after-check.json`.

| Локальное доказательство | SHA256 |
| --- | --- |
| TipHUD.json | 8c9a885d2904956a4899d979b2c4b60f355f62ec05b7e53b45d95938dc1be16e |
| TipHUD--ExecuteUbergraph_TipHUD.bytecode.json | 980f62888f5db2a6f6e46a12ccfdce8703887842b6b43583988c0c8e70435dd0 |
| TipHUD--ConvertMsgTagToTextArray.bytecode.json | 2e64d0ae2dd1eddac715ec6109d65df288d8e53da264d6a7cedafbc1baf4e7f8 |
| TipHUD--CanShow.bytecode.json | 39cfc83d79b6e20b086aceb44dab96f9e5797ef6cbde980e0a5457bae9bbd605 |
| BaseGameEventObject_BP.json | ad8104d69647bc076f13c36fdb356939594ca28b5b62448854b95b122f7cb4df |
| BaseLoot_BP.json | d9cc5a683fab8c631606963b146380a28cd66121ffad009eb11db07b5276031e |
| BaseLoot2_BP.json | b9eafbeffdf2758cc5902e9caa9105b4e9a16ec3944ee6bf4b4fe9f205bc0a63 |
| BaseDocumentObject.json | c78674f58ff8a2fd1d997f2837b16b6617a4047466866ccf443999a1c8e8ce8e |
| Ladder_BP.json | 066c5202753a48b346f0ccb02b11e83e7ef66f29b2b5dd308a999c227e041a7b |
| InteractTipToText.json | 768d62913e90c1d3df2734bb2a8e76038421c0bbec1723d1d07dbb0337869b8a |
| InteractTipToText_cs.json | a1d000a46f1ede920aa38b0420e11ad899d37253420ffda658484dafadb0763d |
| UI/ru/UI.locres | e01484d7c78b77a48b9b2cd7d53800f6f4e5884769455e62e7aaedaec3a085d8 |
| Umg_Font.json | e99035e6fba5c0e3100e4114877be5219b0cdfbe4e95c5a3de11e40d32fcc5c5 |
| Aphes.ttf | 443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0 |

Полные извлечённые таблицы/шрифты/Blueprint exports не публикуются. В shared
Asterigos-Research переносится только статически подтверждённая reusable цепочка
и свойства ресурсов с указанной границей; gate/механизм/приёмка остаются здесь.
