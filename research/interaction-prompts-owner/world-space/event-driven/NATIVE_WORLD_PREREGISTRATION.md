# Native World-space TipHUD до первой регистрации — 2026-11-20

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
