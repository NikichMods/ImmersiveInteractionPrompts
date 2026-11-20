# Native World-space TipHUD до первой регистрации — 2026-11-20

**Итог испытания: YES для Квинтуса.** [Кандидат](../native-world-quintus/README.md#runtime-result--2026-11-20)
выбрал компонент по владельцу, назначенному штатным SpawnObject до SCS.
Ранний World сохранился. Тот же оригинальный TipHUD получил RenderTarget
и показал штатное `F Поговорить` с перекрытием моделью Квинтуса.
Ниже сохранён исходный source-only вердикт до двух игровых наблюдений.

**Позднее в тот же день:** [read-only прогон у торговца](../native-world-observer/README.md#runtime-result--2026-11-20)
подтвердил доставку `NotifyOnNewObject` до присваивания SCS CreationMethod
и штатной регистрации. Связь установлена до первого `CanShow(Talk)` для
того же компонента. Сохранность записи `World` и точный фильтр торговца
к моменту записи остаются открытыми.

**Вердикт: UNKNOWN для одного торговца, source-only.** В UE4.27 штатная
регистрация умеет создать World-рендерер, если к этому моменту компонент уже
в World. Найден наследуемый шаблон и проверено окно `NotifyOnNewObject` в UE4SS
`83330635`. Для данного экземпляра ещё не установлено, что callback приходит
в нужный момент, что в нём можно однозначно распознать торговца и что запись
переживёт оставшуюся инициализацию. Кандидат с записью свойства не подготовлен.

## Владелец, шаблон и порядок

- В cooked-экспортах Steam 1.09/build 12996889 наследование идёт от
  `NPCInteract_Bp_C` через `BaseNPCInteract_BP_C` к `BaseGameEventObject_BP_C`.
  В последнем `SimpleConstructionScript_0.SCS_Node_7` под `WidgetLocator`
  связывает переменную `ExtendedWidget` с архетипом
  `/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C:ExtendedWidget_GEN_VARIABLE`.
  Это `/Script/Genesis.ExtendedWidgetComponent` с `WidgetClass=TipHUD_C`,
  `DrawSize=1000×1000`, `IsActivated=true`. Поле `Space` не представлено
  в экспортированных данных архетипа. Сохранённый UHT-дамп отражает
  `Space=Screen` у native default, а архивная игра подтверждает Screen
  на готовых экземплярах. UHT-заглушки не раскрывают реализации методов.
- `InheritableComponentHandler` у `BaseNPCInteract_BP_C` содержит записи
  `Title` и `WidgetLocator`, у `NPCInteract_Bp_C` записей в экспорте нет.
  Переопределение `ExtendedWidget` в этой цепочке не найдено. Подходящего
  actor CDO subobject тоже нет в этих экспортах. Запись в общий SCS-шаблон
  затронет будущие инстансы, которые используют этот архетип и читают
  изменяемое поле из него. Запись в CDO самого класса Genesis имеет ещё
  более широкий охват и также не гарантирует наследование значения.
- Для создаваемого актёра `AActor::ExecuteConstruction` запускает SCS.
  `USCS_Node::ExecuteNodeOnActor` выбирает шаблон или cooked instancing data,
  создаёт компонент, вызывает `OnComponentCreated`, прикрепляет scene component
  и регистрирует его через `RegisterInstancedComponent`. Регистрация вызывает
  виртуальный `OnRegister` **до** присваивания `actor.ExtendedWidget` в этом узле.
  User Construction Script и BeginPlay идут позже. У актора, загруженного
  с уровня, данные экземпляра проходят загрузку до регистрации. Архивный
  журнал устанавливает экземпляр торговца после регистрации, но не
  фиксирует вызывающего его создание или ветку instancing.
- Cooked `ReceiveBeginPlay` NPC вызывает родительскую цепочку, а
  `BaseGameEventObject_BP_C` читает уже имеющийся `ExtendedWidget` через
  `GetUserWidgetObject` и приводит его к `TipHUD_C`. В штатном UE
  `UWidgetComponent::BeginPlay` вызывает `InitWidget` для `WidgetClass`.
  Архивный S1 observer связал именно этот NPC и его компонент с тем же
  TipHUD в `BeginPlayPost` и первом `CanShow` с `Talk`. Тогда ранний тег
  ещё был `Interact`. Сгенерированный суффикс имени NPC известен за один
  сеанс и непригоден как постоянный идентификатор торговца.

Источники порядка: [UE4.27 SCS_Node.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/SCS_Node.cpp#L82),
[ActorConstruction.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/ActorConstruction.cpp#L747),
[ActorComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Components/ActorComponent.cpp#L1519),
[Actor Lifecycle UE4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-lifecycle?application_version=4.27),
[архив S1](../../native-tiphud-s1/README.md#merchant-early-owner-and-layout--local-evidence-2026-11-19).

## Проверенный ранний API и предел доказательства

`NotifyOnNewObject("/Script/Genesis.ExtendedWidgetComponent", ...)` вызывает
Lua после `StaticConstructObject_Internal` прямо на игровом потоке. Для
остальных потоков версия `83330635` ставит callback в очередь, поэтому
доставка тогда не гарантирует раннего окна. Даже синхронный вызов
предшествует завершению SCS-инстанцирования. В обычной ветке
`CreateComponentFromTemplate` внутри `StaticDuplicateObjectEx` за созданием
объекта следуют запись данных исходного объекта и чтение их в копию.
В fast path после `NewObject` идёт `Serialize` с кэшированным списком
свойств, затем `PostDuplicate` и `ConditionalPostLoad`. Ранняя запись
`Space` может быть перекрыта, если его загружает этот путь. Отсутствие
`Space` в JSON архетипа не доказывает его отсутствие в потоке дублирования.
Для ветки быстрой загрузки правка самого шаблона также не переписывает
уже построенный буфер. Проверка `GetWidgetSpace` сразу после setter
установила бы только результат в момент callback.

Blueprint `RegisterHook` в этой версии доставляет script hook в post,
и даже вход в User Construction Script уже следует за регистрацией SCS.
`RegisterBeginPlayPreHook` также поздний. Прямого Lua API для pre
виртуального `OnRegister` в проверенном `LuaMod.cpp` нет, а объявление
`OnRegister` в UE4.27 не является `UFUNCTION`. Простого поддержанного
интервала «после переноса данных, до регистрации» для этого компонента
пока не найдено.

В изученных cooked-графах трёх классов нет вызова `SetWidgetSpace`.
Из Genesis подтверждены исходное значение Screen и отдельная цепочка
показа через native `SetShow`. Сохранённые сведения об этой цепочке не
устанавливают, что после переноса шаблона или при первом показе отсутствует
native-запись в `Space`. Связывать возможный сброс с Genesis без наблюдения
нельзя: штатное копирование UE уже даёт самостоятельный источник перезаписи.

Источники: [UE4SS 83330635 LuaMod.cpp, static construct callback](https://github.com/UE4SS-RE/RE-UE4SS/blob/8333063595fa3c49ad307f3b0f732accbb760d25/UE4SS/src/Mod/LuaMod.cpp#L6657),
[ActorConstruction.cpp, обе ветки](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/ActorConstruction.cpp#L970),
[UObjectGlobals.cpp, дублирование](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/UObject/UObjectGlobals.cpp#L2014),
[ноябрьское исследование и native show](TARGET_AUTHORITY_STUDY.md).

## Что даст штатная регистрация

При World в первом `UWidgetComponent::OnRegister` игровой клиент с RHI
создаёт `FWidgetRenderer`. Дальше штатный World-путь требует валидный Slate
content для scene proxy, ненулевой допустимый draw size и draw для появления
render target. `UpdateWidget` поднимает виртуальное окно, дальнейший World
draw использует свои render target и материал. Это подтверждает возможность
выделения рендерера силами UE, а фактический кадр у торговца остаётся
открытым. `1000×1000` даёт допустимую область, но размер в мире, pivot,
ориентация, видимость с нужной стороны и возможная коллизия требуют проверки.
Родной locator рассчитан на экранную проекцию; его существующая привязка
сохранит точку крепления, но сама по себе не гарантирует читаемое положение
плоскости в 3D.

`WidgetClass` и создание TipHUD остаются в штатном компоненте по источникам.
Поведение Genesis show/hide, layout, материала и глубины в World для этой
цепочки ещё не наблюдалось. Отдельный World-компонент ранее доказал 3D
перекрытие, а [коммит 00ca2d2](https://github.com/NikichMods/ImmersiveInteractionPrompts/commit/00ca2d2fcdfc365d221aac9876a57259bcf4e317)
доказал совместный записанный кадр Aphes, разделителя и штатного действия
с кнопкой для Screen. Оба результата относятся к своим режимам.
Production BLOCKED. [UE4.27 WidgetComponent.cpp](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/UMG/Private/Components/WidgetComponent.cpp).

## Одно ближайшее наблюдение

После отдельного разрешения провести **один read-only запуск** с отдельным
наблюдателем. До загрузки того же сохранения подписаться на
`NotifyOnNewObject` компонента. Для точного имени компонента `ExtendedWidget`
и класса NPC в том же sublevel записать ограниченный набор ранних отметок
с путём outer, `CreationMethod`, `WidgetClass` и `Space`. Связать запись
того же компонента с `BeginPlayPost` по идентичности и подтвердить торговца
по первому штатному `CanShow(Talk)` через исходный `GetUserWidgetObject`.
Пользователь один раз загружает сохранение, подходит к тому же торговцу,
закрывает игру обычным способом и оставляет свежий UE4SS.log для анализа.
Установку отдельного наблюдателя нужно согласовать до запуска.

Искомый результат — **есть ли у именно этого компонента callback до
присваивания `CreationMethod=SimpleConstructionScript` и какие данные уже
видны в нём**. Соответствующая ранняя запись подтвердит доставку внутри
SCS до регистрации для этого создания и покажет, возможен ли выбор
экземпляра по имеющимся данным. Совпадение только после регистрации или
отсутствие ранней записи при подтверждённом BeginPlay отсекает этот путь
на наблюдавшейся загрузке. Даже ранняя доставка оставит сохранность
изменённого `Space` отдельным вопросом. В этом отчёте ни один запуск
или запись в свойства игры не выполнялись.

## Размещённый Open — граница окна (2026-11-20)

**BLOCKED для узкого кандидата.** Изучен существующий cooked-экспорт
`0-1_plot_outerRimA_interact1`, SHA-256
`c8fca3bfee13de734a0f8189a07c284cee584ec46f7729719d72c4a4b9a17b97`,
без повторного извлечения. Актор `0-1_lootbox_01_mat_ST001` класса
`item_lootbox02_C` находится в `PersistentLevel`. Его поле
`ExtendedWidget` указывает на экспорт 130. У компонента
`/Script/Genesis.ExtendedWidgetComponent` Outer — этот актор,
`RF_WasLoaded`, `CreationMethod=SimpleConstructionScript`, шаблон
`BaseGameEventObject_BP_C:ExtendedWidget_GEN_VARIABLE`, AttachParent —
собственный `WidgetLocator`. `CurrentDrawSize=1000×1000`; явного
`Space` в экспортированных свойствах экземпляра нет. Архивный
[Open join](../../../../docs/VERIFIED_RUNTIME.md#natural-open-join-and-component-world-pose--bounded-pass-2026-10-29)
подтверждает ту же цепочку до живого TipHUD при показе. В просмотренных
журналах раннего World-кандидата нет `PLACED_OBJECT_NOTIFY` или
`PLACED_OBJECT_BEGIN` для этого сундука. Участие подуровня в тех
сеансах не установлено, поэтому отсутствие строк ничего не доказывает
о доставке при его загрузке.

### Загрузка и первое потребление Space

На свежем загруженном экземпляре исходный путь UE4.27 создаёт
экспорт с Outer и флагами загрузки. В linker path за созданием
следует `FLinkerLoad::Preload` с десериализацией, а в асинхронной
ветке загрузка экспортов и `ConditionalPostLoad` предшествуют
доставке готового пакета. Для конкретной холодной загрузки сундука
точный загрузочный поток и выбранную ветку ранее не измеряли.
В игровом streaming path `UWorld::AddToWorld` вызывает
`ULevel::IncrementalUpdateComponents`, затем
`AActor::PreRegisterAllComponents` и `IncrementalRegisterComponents`.
Последний регистрирует родителя перед ребёнком и вызывает
`RegisterComponentWithWorld` для исходного компонента. Его
`ExecuteRegisterEvents` вызывает виртуальный `OnRegister`.
`UWidgetComponent::OnRegister` потребляет `Space` для создания
рендерера World. Это порядок из закреплённого исходника, а не
непосредственная запись первой регистрации сундука.
[LinkerLoad](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/UObject/LinkerLoad.cpp#L4779),
[AsyncLoading](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/CoreUObject/Private/Serialization/AsyncLoading.cpp#L6371),
[World](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/World.cpp#L2570),
[Level](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/Level.cpp#L1093).

В нормальной ветке `ULevelStreaming::AsyncLevelLoadComplete`
`SetLoadedLevel` предшествует синхронному `OnLevelLoaded.Broadcast()`.
Видимость добавляет подуровень в мир позднее через `AddToWorld`.
Поэтому для свежего экземпляра `OnLevelLoaded` — подходящий штатный
сигнал **после десериализации**, с доступным `GetLoadedLevel()`.
Путь уже загруженного пакета также может выдать `OnLevelLoaded`;
само событие не доказывает, что конкретный экземпляр ещё ни разу
не регистрировался. В нужном свежем level identity можно проверять по
точному пути актора, классу, имени компонента, Outer и обратному
`actor.ExtendedWidget`, без числовых адресов между сессиями.
[SetLoadedLevel](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/LevelStreaming.cpp#L795),
[ветка async](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/LevelStreaming.cpp#L1139),
[добавление в мир](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Engine/Private/LevelStreaming.cpp#L573).

### Почему пока нет кандидата

- `NotifyOnNewObject` на игровом потоке срабатывает при создании
  экспорта до чтения его свойств, на другом потоке может быть
  отложен. Outer и имя могут быть уже доступны, тогда как поле
  актора, flags и данные компонента ещё не дают годной точки
  записи. Для одного linker path `RF_NeedLoad` очищается ещё
  **до** `Serialize`. Отсутствие `Space` в JSON и немедленный
  readback не исключают копирование default/template или
  последующую native-запись. Сохранность до `OnRegister` не доказана.
- `OnLevelLoaded` отражён как multicast, а `GetLoadedLevel` и
  `GetStreamingLevel` присутствуют в сохранённом UHT. У UE4SS
  `83330635` метод `Add` принимает UObject и имя UFunction и
  создаёт `FScriptDelegate` через `BindUFunction`. Приёма Lua
  closure нет. `RegisterCustomEvent` регистрирует наблюдателя по
  имени, а не создаёт вызываемую UFunction. В сохранённых графах
  не найден подходящий штатный обработчик этого делегата.
  Не подтверждены безопасный receiver и момент подключения к
  точному `ULevelStreaming` до сигнала. Произвольный вызов
  чужой функции как переходника не имеет доказательства безопасности.
  [UE4SS multicast Add](https://github.com/UE4SS-RE/RE-UE4SS/blob/8333063595fa3c49ad307f3b0f732accbb760d25/UE4SS/src/LuaType/LuaXDelegateProperty.cpp#L154),
  [RegisterCustomEvent](https://github.com/UE4SS-RE/RE-UE4SS/blob/8333063595fa3c49ad307f3b0f732accbb760d25/UE4SS/src/Mod/LuaMod.cpp#L2369).
- `PreRegisterAllComponents`, `OnRegister` и `PostLoad` —
  native virtual, вне обычного `RegisterHook` по UFunction.
  `LoadMapPre` относится к загрузке карты, до появления
  целевого экспорта, а `LoadMapPost` не даёт этой границы для
  отдельно загружаемого подуровня. `BeginPlayPre/Post`,
  `OnLevelShown` и `CanShow` приходят после регистрации;
  поздний `SetWidgetSpace` не создаёт отсутствующий рендерер.
  Штатный instance override `Space` в cooked-экспорте мог бы
  сделать запись частью десериализации, но безопасный узкий
  путь поставки такого изменения и его сохранность не установлены.
  Общие CDO/SCS и перерегистрация остаются вне задачи.

**Один следующий шаг.** Подтвердить на одном холодном входе
read-only доставку `OnLevelLoaded` через штатный, совместимый
receiver, привязанный к точному подуровню до запроса загрузки.
Достаточное наблюдение — на игровом потоке уже доступна
взаимно подтверждённая пара actor/ExtendedWidget с завершённой
загрузкой и компонент входит в свою первую регистрацию только
после этой отметки. Пока receiver не подтверждён, не готовить
пробу с подменой. Положительный результат откроет отдельно
согласованную проверку одного World/NoCollision без второго
компонента, с проверкой сохранности `Space` на штатном рендерере.

**Динамический Talk вне Квинтуса.** Подтверждённый общий
`CharacterSetCanInteract → SpawnObject` остаётся применимым
направлением, если доказан конкретный owner с тем же порядком.
В сохранённом Quintus sublevel ближайший именованный сосед
`1-1_QB_Decimus_creator` с `CharacterName=m003` не имеет
явного `InitialCanInteract=true` и наблюдения reciprocal
owner → новый компонент → `Talk`. Расширять фильтр по
одному классу `NPCInteract_Bp_C` оснований нет. Другой
доказанный Talk в этой узкой сверке не найден.

Source-only кандидат для Open не создан. Игровой сеанс,
установка и запись в игровые ресурсы не выполнялись.

### Проверка штатного обработчика OnLevelLoaded — 2026-11-20

**Проба BLOCKED до установки.** В сохранённом cooked-экспорте
целевого подуровня нет собственного LevelScriptActor или
LevelStreaming receiver. Поиск по сохранённым Blueprint bytecode,
включая MainGameMode и GameInstance, не нашёл привязки
`OnLevelLoaded` или вызова проверяемого обработчика. Это предел
просмотренных экспортов. Возможность привязки из другого пакета
или native-кода остаётся открытой.

В сохранённом UHT `FLevelStreamingLoadedStatus` — динамический
multicast без параметров. У Genesis есть отражённый
`EventLoadStreamLevelComplete(FName subLevelName)`, но его
сигнатура не совпадает, а вызов именно между `SetLoadedLevel`
и первой регистрацией для этого пакета не доказан. Безаргументные
`EventStartUpdateSubLevelProcess` и
`EventCompleteUpdateSubLevelProcess` в cooked MainGameMode
включают и выключают индикатор загрузки (`ShowLoadingIcon`,
узлы 703 и 724). Использование их как новых получателей вызвало
бы игровую логику. Пассивное наблюдение этих двух событий само
по себе не установит доставку `OnLevelLoaded` точного подуровня.

В UE4.27 multicast обходит список привязок и вызывает
`ProcessEvent` на найденной функции получателя. Hook функции
сигнатуры делегата не даёт события рассылки. Поэтому для
пассивной пробы через закреплённый UE4SS нужен именно проверенный
получатель, которого движок естественно вызывает для нужного
streaming-объекта до регистрации сундука. Ни один такой получатель
в доступных данных не подтверждён.
[Рассылка и вызов получателя в UE4.27](https://github.com/AlexMercer-MA/UnrealEngine-4.27/blob/306a7e9f7fb53f14c2cb3bfd3854ad906710a17e/Engine/Source/Runtime/Core/Public/UObject/ScriptDelegates.h#L215).

На момент проверки игра работала. Пробу не подготовили и не
установили, игровая сессия и `Space` не менялись. Закрытие игры
само по себе не снимает блокировку. Пересмотреть вывод можно по
положительной привязке конкретного `UObject/UFunction` к
`OnLevelLoaded` этого подуровня или по доказанной штатной
цепочке, доставляющей тот же момент без вызова побочной логики.

### Минимальная ранняя проба для одного Open — source-only (2026-11-20)

**RESEARCH ONLY, NOT INSTALLED, production BLOCKED.** После выбора
пользователя исследование гипотетического receiver для
`OnLevelLoaded` не продолжается. В уже используемый
`NotifyOnNewObject("/Script/Genesis.ExtendedWidgetComponent")`
добавлена одна allowlisted ветка для
`0-1_lootbox_01_mat_ST001.ExtendedWidget` точного подуровня
`0-1_plot_outerRimA_interact1` и класса `item_lootbox02_C`.
Для `Take/Check` сохраняется только журнал, путь Квинтуса не изменён.

В callback ветка требует `CreationMethod == 0`,
`Space == Screen (1)`, отсутствие валидного `WidgetClass`,
проверенные Outer/actor path/class. При успехе она ставит
`NoCollision` и `Space=World (0)`, проверяет readback и
запоминает идентичность. При позднем/несовместимом состоянии
пишет `PLACED_OPEN_SKIP`, ничего не меняет.
Неудачная запись локально отклоняется с попыткой восстановления
прежней коллизии и Screen. Никаких новых компонентов, хука
загрузки, Tick, scan, собственных виджетов или автоповторов нет.

**Важно:** ранние признаки не доказывают, что объект
десериализован и ещё не проходил `OnRegister`.
Последующая запись свойств может вернуть `Space=Screen`.
Поэтому `PLACED_OPEN_SET_WORLD` — лишь свидетельство
моментального setter. `PLACED_OPEN_BEGIN` сверяет
`early_write`, `same_instance`, `space`, `collision`,
`widget`, `rt` и `added_to_screen`; F5 или
NumPad5 в действующем F5-редакторе дают
`PLACED_OPEN_SAMPLE` после появления подсказки.
Для положительного World-пути нужен RT оригинального
компонента, отсутствие добавления на Screen и реальная
пользовательская визуальная проверка.

Первая проба намеренно **не добавляет Aphes/разделитель,
не изменяет масштаб, высоту или RGB сундука**.
Это проверка штатного World-рендерера, а не дизайна.
Ранее принятая база Квинтуса не меняется.

Следующий шаг только после отдельного разрешения на
закрытоигровую установку и откат: холодно загрузить
сохранение с точным сундуком, подойти, вызвать F5
для `PLACED_OPEN_SAMPLE`, закрыть игру нормально,
сопоставить свежий журнал и наблюдаемый вид.
При `PLACED_OPEN_SKIP` не форсировать поздний World.
Source-only mocks не устанавливают поведение в реальной игре.

### Установка точной пробы Open (2026-11-20)

**INSTALLED**, source `52c6035793cf4a3d24d4cf615ec28cfbe32f70b8`.
Пользователь отдельно разрешил установить этот точный коммит вместе
с унаследованной правкой начального RGB Квинтуса из `6730cc6`.
Итоговые значения его визуальной базы прежние. Проверка нового порядка
записи RGB в игре ещё предстоит. Для самого сундука кандидат проверяет
исходный World-рендерер без добавления оформления.

Перед заменой действующий World `a688dde` и Screen S1 `8f1231d`
совпали с прежним отчётом. Preflight подтвердил Steam build 12996889,
UE4SS 83330635, хэши хоста, загрузчика, UEHelpers и локальных ресурсов.
В единственном активном World-каталоге изменились два Lua-файла.
SHA-256 семифайлового манифеста
`9cbffce77233b4d1025ca2b8812ee7c4c27ab4c5ab220b2dbc99aff8654aeb98`.

| Установленный файл | SHA-256 |
| --- | --- |
| `Scripts/main.lua` | `cc072851b4e9c679978e7b7549c80e92113f3a7604d87e59e666a180d992d965` |
| `Scripts/IIPQuintusProbe.lua` | `f32a663aa36a3490825d590a1d7a1c9da4d110e97e16a7e1fda636b4aa1f19af` |
| `Scripts/IIPQuintusResources.lua` | `c1a870f6ad21f724e72188914675d9743e84431050fb5a22a4e0f8f38567b814` |
| `Scripts/IIPQuintusKeyboardBindings.lua` | `552895a3b7ed1091231f93f8f93e1f5d1ae5cc5b3e7518b53f72777977dbe8ef` |
| `Assets/aphes_divider_256x32.png` | `b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969` |
| `Scripts/IIPLiveConfig.lua` | `894f191e0d8d1beaaafd21c9e4265e2a623cd7b6028b979a2e67811d270d9978` |
| `enabled.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Хэши всех пяти файлов Screen S1 и соседних файлов до и после совпали.
Сверены 12 545 остальных файлов под ue4ss, 26 файлов корня Win64,
11 pak-модов, 16 сохранений и 46 файлов настроек. Повторная сверка
после установки подтвердила World (7), Screen S1 (5) и резервную
копию прежнего World (7). Резервная копия — исходный каталог
`a688dde`, перенесённый целиком во внешний архив. Его полный
локальный путь хранится в `deployment/installed.json` эксперимента
`52c6035793cf`. Откат выполняет
`.local/install-native-world-open-52c6035.py --rollback` при закрытой
игре. Восстановление полного активного пакета отрепетировано на копии.

Шесть локальных тестов Open, локальные проверки Quintus и компиляция
Lua при подготовке прошли. [Полный CI PASS](https://github.com/NikichMods/ImmersiveInteractionPrompts/actions/runs/44762199739).

Готово к пользовательскому тесту. Холодно загрузить сохранение
с точным сундуком, подойти до штатной подсказки и нажать F5 для
`PLACED_OPEN_SAMPLE`, затем штатно выйти. Сопоставить
`PLACED_OPEN_SET_WORLD` или `PLACED_OPEN_SKIP`, `PLACED_OPEN_BEGIN`
и ручной sample. Для положительного результата нужны идентичность
исходного компонента, сохранившийся World, оригинальный RT,
визуальная подсказка и штатное взаимодействие. Установочный прогон
игру не запускал. Runtime PENDING, production BLOCKED.
