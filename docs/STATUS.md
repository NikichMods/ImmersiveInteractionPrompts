# Статус Immersive Interaction Prompts

**2026-10-30 — native World hint mirror INSTALLED, runtime PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точный7c2aa07
в новый ImmersiveInteractionPromptsWorldHintProbe: три Lua и enabled.txt.
[Хэши, откат и один сценарий](../research/interaction-prompts-owner/world-space/hint-mirror/README.md). Lua не менялся; source/installed hashes совпали.
Только новая IIP-проба включена,14 старых отключены.29 исторических mod/loader
hashes совпали;35 текущих mod/loader и55 существующих tracked config/save файлов
сохранены по хэшам. UE4SS DLL совпал; backup/manifest/guarded rollback вне loader,
syntax PASS. Игра не запускалась/не закрывалась агентом, hot reload не применялся.
Далее keyboard→controller→keyboard→F7 без F8 на controller. Runtime pixel/device/
current remapping ещё не принят; полная композиция/production BLOCKED.


**2026-10-30 — native input-hint World mirror READY_SOURCE, NOT_INSTALLED.**
[Три Lua, точные контракты/хэши и один тест](../research/interaction-prompts-owner/world-space/hint-mirror/README.md). Перед own allocation проверяется
selected Retainer: при bRetainRender/global1/phase0-count1 и готовом UI MID/Icon RT
свой Image ссылается на существующий MID; при выключенном bRetainRender допускается
только одиночный untransformed Texture2D Image Brush. Global0/missing/change и
неподдерживаемые источники отвергаются. Второго Retainer/записи параметров нет.
Каждый кадр проверяются ресурс/device/identity; own stale reference скрывается/
снимается до bounded settling/rebind. Максимум8 поколений, прежний World/Yaw/F7/
timeout сохранён; никаких Aphes/текста/PNG.232 tests/16 suites PASS,25 новых.
Фактическая активность/пиксели/alpha-gamma/device/remapping ещё не проверены в игре.
Следующий отдельный тест: keyboard→controller→keyboard (без F8 на controller),
F7 до30s. Полная композиция/production BLOCKED. Ничего не устанавливалось.


**2026-10-30 — World Aphes composition integration BLOCKED: live input hint.**
[Source-only review / partial pure plan](../research/interaction-prompts-owner/world-space/composition/README.md). Текст действия можно читать из
оригинального GetText и обновлять собственный TextBlock текущим локализованным
значением; pinned FText setter не сохраняет полную string-table history. Прежний
скопированный F brush был только снимком. RetainerBox_0/TipIconMat добавляет слой
Icon render-target и hold-параметр t; второй Retainer с оригинальным MID сам писал
бы в shared Icon — такой путь отвергнут. Own Image с read-only final MID — кандидат,
его alpha/gamma/актуальность при смене устройства и remapping ещё не доказаны.
Исполняемый композиционный payload не создан, заглушки F нет. Подготовлен только
pure slot-envelope512x128 и8 тестов;207 tests/15 suites PASS. Aphes/PNG локальны,
renderer/anchor/material/Yaw/cleanup и прежние исходники не менялись. Следующий
достаточный тест после отдельной подготовки/разрешения — узкий hint-only mirror
keyboard→controller→keyboard, затем F7. Финальный дизайн/full lifecycle/production
BLOCKED; ничего не устанавливалось и игра не запускалась.


**2026-10-30 — vertical frame-Yaw / manual F7 bounded runtime PASS; probe DISABLED.**
[Точная запись](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Пользователь подтвердил почти идеальную работу и F7.
Один loop handle3,1068 frames/1068 writes за~17.796s, no degeneracy/errors;
STATE Pitch/Roll0, world position/scale неизменны, RT512x128/stock depth material.
F7: LOOP_CANCELLED→STOP user/hooks_remaining0→native destroy/CLEANED user.
Снято только own enabled.txt при уже закрытой игре;33 прежних mod/loader hashes
совпали,88 текущих файлов сохранены. Sourcef1eb635 неизменён. Закрыт узкий gate
вертикального покадрового Yaw и ручной очистки. Точный FPS/latency не измерены,
финальная композиция/full lifecycle/production BLOCKED; нового payload/теста нет.


**2026-10-30 — vertical world-Z yaw INSTALLED, runtime PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точныйf1eb635
в новый ImmersiveInteractionPromptsWorldYawProbe: два Lua и enabled.txt.
[Хэши, откат и один сценарий](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Source/installed SHA256 совпали, Lua неизменён.
Только новая IIP-проба включена;13 прежних отключены.29 исторических mod/loader
hashes совпали;33 текущих mod/loader и56 существующих tracked config/save файлов
сохранили hashes. UE4SS83330635/DLL совпал, backup/manifest/guarded rollback вне
loader, syntax PASS. Игра не запускалась/не закрывалась, hot reload не применялся.
Следующий шаг — один пользовательский vertical-yaw/F7 тест; runtime/production
acceptance остаётся BLOCKED, установка не является его прохождением.


**2026-10-30 — vertical world-Z yaw READY_SOURCE, NOT_INSTALLED.**
[Отдельная ревизия, контракты, хэши и один будущий тест](../research/interaction-prompts-owner/world-space/vertical-yaw/README.md). Решение пользователя
зафиксировано в REQUIREMENTS: каждый EngineTick только горизонтальный Yaw,
Pitch/Roll0, без1° threshold/интерполяции; fixed initial vertical — минимальный резерв.
Pinned LoopInGameThreadAfterFrames(1) подтверждён вместе с ownership/cancel/unref.
Один own loop после регистрации, нативный lifetime каждый кадр, полная topology/
anchor проверка каждые12 callbacks;12000 updates/45s, прежние пределы сохранены.
8 точечных lookups/13 UE calls в обычном follow-кадре — не замер производительности.
199 tests/14 suites PASS,22 новых. Не установлен, игра и прежний payload не менялись.
Следующий отдельный runtime gate: вертикальность/покадровый Yaw и F7 до30s в одном
коротком прогоне. Cadence/camera phase/performance и manual cleanup ещё не приняты;
production BLOCKED. Старые результаты rendering/occlusion/setter не повторять.


**2026-10-30 — bounded World rotation / target-loss cleanup PASS; probe DISABLED.**
[Технический результат и границы](../research/interaction-prompts-owner/world-space/orientation/README.md). Fixed:103 polls/0 writes/error27.383°;
F6 включил follow, первый native setter вернулся, ошибки setter/readback нет.
Через42.629s после создания stop по потере видимости Screen Open (CONTRACT_ERROR),
затем hooks_remaining0, native destruction и CLEANED. Конкретный visibility
predicate/причина неизвестны; F7 в логе отсутствует и не принят. Итогового follow
sample/числа поворотов нет. Пользователь сообщил общую успешность; дизайн,
предпочтение режимов и плавность не оцениваются. Логи архивированы; при закрытой
игре снят только own enabled.txt,31 прежний mod/loader hash совпал,87 текущих
файлов сохранены при отключении. Production BLOCKED, нового payload нет.


**2026-10-30 — World orientation comparison INSTALLED, runtime PENDING.**
По прямому разрешению пользователя при закрытой игре установлен точный6d44daa
в новый ImmersiveInteractionPromptsWorldOrientationProbe: два Lua и enabled.txt.
[Идентичность, откат и сценарий](../research/interaction-prompts-owner/world-space/orientation/README.md). Source/installed hashes совпали;
только новая IIP-проба включена,12 прежних отключены.29 исторических и31 текущий
mod/loader hash сохранены,59 config/save hash неизменны. DLL83330635 совпал;
backup/manifest/guarded rollback вне loader, syntax PASS. Игра не запускалась,
hot reload не применялся. Далее один пользовательский fixed/follow/F7 тест;
плавность, native rotation/marshalling и ручной cleanup ещё не приняты.


**2026-10-30 — World orientation comparison READY_SOURCE, NOT_INSTALLED.**
[Исходники, контракты, хэши и будущий тест](../research/interaction-prompts-owner/world-space/orientation/README.md).
Отдельная ограниченная ревизия сохраняет принятый V3 renderer/anchor/material и
начальную фиксированную ориентацию. F6 переключает fixed/follow: не чаще10Hz,
поворот при ошибке>=1°, только собственный компонент через K2_SetWorldRotation
на EngineTick, с readback и свежей проверкой цели/UI. Максимум450 проверок/45s;
при потере/смене известной цели, уходе за экспериментальные bounds или F7 — stop
и own cleanup. Нет сканирования мира, изменения размера/положения/оригинального UI.
177 tests/13 suites PASS,19 новых; setter/marshaling/плавность ещё runtime PENDING.
Динамический billboard не принят как production-дизайн. Следующий достаточный
шаг после отдельного разрешения установки — один fixed/follow camera comparison
и ручной F7 до timeout. Принятый rendering/occlusion опыт не повторять. Игра и
установленный payload не менялись; production BLOCKED.

**2026-10-30 — bounded World rendering / Hilda occlusion / timeout cleanup PASS.**
[Полный результат](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Точный6ad93fc V3 загрузил host одним LoadAsset после reload, создал собственный
World-компонент; пользователь подтвердил видимость, частичное перекрытие букв
Хильдой и возвращение букв при смещении. Два STATE: одинаковые world position/
rotation, RT512×128, штатный masked/depth материал. Через45s world_timeout:
hooks_remaining0, native COMPONENT_DESTROYED и CLEANED, ошибок probe нет.
F7 до timeout не выполнен — ручной World cleanup-key не принят. Первые22s не
покрыты снимками; ощущение начального поворота не диагностировано. В коде только
начальная ориентация, динамический billboard пока не реализован/не проверен.
Логи сохранены, при закрытой игре снят только own enabled.txt;29 прежних mod/loader
hashes совпали,91 текущий файл не изменился при отключении. Проба DISABLED.
Механизм реального перекрытия в одном Open доказан; причина первого зависания
неизвестна. Не повторять этот этап. Следующий отдельный вопрос — поведение при
движении камеры/дистанции; финальная композиция и production lifecycle BLOCKED.

## История установки V3

**2026-10-30 — Deferred World V3 INSTALLED, runtime PENDING.**
По разрешению пользователя при закрытой игре установлен точный6ad93fc source
в новый ImmersiveInteractionPromptsWorldRefreshProbe: два Lua и enabled.txt.
[Хэши/откат/процедура](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Другие IIP probes сохранены/отключены;29 старых mod/loader и59 текущих config/save
файлов сохранили хэши, UE4SS DLL совпал. Backup/manifest/guarded rollback вне
loader в local post-reload-refresh/install-20261029T220606Z. Lua не менялся.
Игра не запускалась/не закрывалась, hot reload не выполнялся. Следующий шаг — один
пользовательский F8→reload→Open→F7 тест новой загрузки и, если пройдена, renderer.
Причина первого зависания неизвестна; World/production acceptance BLOCKED.

## Подготовка V3

**2026-10-30 — Deferred World V3 post-reload refresh READY_SOURCE, NOT_INSTALLED.**
[Текущие исходники/хэши/проверки](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
F8 проверяет только API, без преждевременной загрузки. После MATCH отложенная
EngineTick-задача различает nil/null-wrapper/Lua-invalid/native-invalid/identity
mismatch и разрешает максимум один точный LoadAsset каждого HOST/MASK за сессию.
После загрузки заново проверяются actor/component/TipHUD/UI/Open/native validity
и текущий anchor; только затем прежний путь создания. Отмена/срок/reentry/cleanup
сохранены, геометрия и материал неизменны.158 tests/12 suites PASS; deferred34.
Установленная V2 и старый World probe отключены и не изменены. Игра не запускалась,
новая ревизия не устанавливалась. Следующий шаг — отдельно разрешённая установка
новой пары и один ограниченный фазовый тест. Загрузка класса не доказывает World
renderer; причина первого зависания неизвестна, production/World acceptance BLOCKED.

## Предыдущий результат Deferred V2

**2026-10-30 — deferred World run: NOT_LOADED после reload, probe DISABLED.**
[Точный результат](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Host load/PREPARED прошли до own hooks; после reload MATCH→CREATE_QUEUED→
CREATE_DISPATCHED(EngineTick) и anchor/camera/math-фазы завершились. Затем gate
resident_assets отказал: живой точный PostionItemUMG_BP_C не подтверждён.
STOP result=NOT_LOADED/hooks_remaining0; component_construct не начат, World
renderer не создавался. GC/unload как причина и исправление первого зависания
не доказаны. Логи сохранены; при закрытой игре снят только own enabled.txt.
27 старых mod/loader и88 текущих файлов сохранили хэши при проверке/отключении.
Текущий lookup-only вариант BLOCKED; минимальная следующая правка — одно точное
обновление ресурсов через EngineTick после reload, затем свежая проверка цели/UI.
Новая ревизия не установлена; World/production acceptance BLOCKED.

## История deferred-установки

**2026-10-30 — deferred World revision INSTALLED, runtime PENDING.**
По разрешению пользователя при закрытой игре установлен точный2941123 source
в новый ImmersiveInteractionPromptsWorldDeferredProbe: два Lua и enabled.txt.
[Хэши, откат и сценарий](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Старая зависшая ревизия сохранена и отключена; включён только новый IIP probe.
UE4SS DLL совпал;27 прежних mod/loader и59 текущих config/save файлов сохранили
хэши. Backup/manifest/guarded rollback вне loader в local deferred/
install-20261029T214003Z. Игру не запускали/не закрывали, hot reload не применяли.
Следующий шаг — один пользовательский F8→reload→Open→F7 тест с фазовыми логами.
Причина прежнего зависания ещё не доказана; runtime/production acceptance BLOCKED.

## Подготовка отложенной ревизии

**2026-10-30 — deferred World diagnostic revision READY_SOURCE, NOT_INSTALLED.**
[Разбор и отдельные исходники](../research/interaction-prompts-owner/world-space/probe/deferred/README.md).
Причина первого зависания не доказана. Точный UE4SS source подтверждает: script
callback удерживает общий recursive mutex, а простая EngineTick action выполняется
после освобождения очереди/lock. Синхронный LoadAsset на miss вызывает LoadObject.
Новая ревизия разрешает класс/материал до регистрации своих hooks, создаёт только
через EngineTick после свежей проверки identity/UI/native validity, не загружает
ресурсы при создании/после reload; cleanup тоже отложен. BEGIN/END-фазы отделяют
load/construct/Create/first Slate/register/cleanup. Anchor/визуальные параметры и
материал прежние.139 offline tests/12 suites PASS;15 новых policy cases.
Зависшая ревизия/установленные Lua не изменены и отключены. Новой установки,
игрового прогона или runtime PASS нет; World/production acceptance BLOCKED.
Следующий достаточный шаг — отдельное разрешение на установку новой пары файлов
и один ограниченный пользовательский фазовый тест.

## Предыдущий отрицательный игровой результат

**2026-10-30 — первый World-прогон: пользователь сообщил зависание; probe DISABLED.**
[Логи, границы и следующий шаг](../research/interaction-prompts-owner/world-space/probe/README.md).
Точное Open MATCH получено00:15:12.150; это последняя строка UE4SS.log.
CREATED/STATE/FAILED/CLEANED/STOP отсутствуют; Genesis.log заканчивается через8ms
на FlushAsyncLoading. Конкретный зависший вызов и причина не доказаны. World
отрисовка/перекрытие/очистка не приняты. Процесс уже отсутствовал при проверке;
агент его не завершал. Оба лога и exact source сохранены локально. При закрытой
игре снят только собственный enabled.txt;25 прежних mod/loader hashes совпали,
86 текущих файлов не изменились при отключении. Исходники/другие моды сохранены.
Эта ревизия BLOCKED для повторного теста; следующий шаг — узкая проверка контекста
создания/загрузки и фазовая диагностика, без автоматической установки исправления.

## История установки

**2026-10-30 — World TEST prototype INSTALLED, runtime PENDING.**
По разрешению пользователя при закрытой игре установлен точный d4a1ac6 source:
два Lua-файла и enabled.txt в новом ImmersiveInteractionPromptsWorldProbe.
[Хэши, откат и инструкция](../research/interaction-prompts-owner/world-space/probe/README.md).
UE4SS83330635/DLL совпали;25 старых mod/loader и58 текущих config/save files
сохранили хэши. CombatHUD/SoulsEnemyHUD сохранены; остальные IIP probes отключены.
Backup/manifest/guarded rollback вне loader: local world-space/probe/
install-20261029T211023Z. Исходники не менялись, игру не запускали/не закрывали.
Следующий шаг — один пользовательский reload/Open/partial-occlusion/F7 test.
World rendering/очистка в игре и production BLOCKED до результата.

## Подготовка исходников

**2026-10-29 — отдельный World-component прототип READY_SOURCE, не установлен.**
[Исходники, точные хэши и процедура](../research/interaction-prompts-owner/world-space/probe/README.md).
Проверенные OpenJoin и независимый host переиспользованы. Один собственный
RF_Transient UMG.WidgetComponent: World0 до FinishAddComponent(manual=true),
stock masked depth-tested material, WORLD TEST, фиксированная плоскость512×128
со scale.25 и live anchor+32Z, без collision/overlaps/input/focus. Оригинальный
TipHUD и его компонент остаются Screen и не изменяются.45s после создания,
общие120s, явный F7 cleanup с native PendingKill-aware проверкой и retry отказа.
16 новых policy tests PASS; весь suite124 tests PASS. Source/UHT audit и mocks
не доказывают реальную отрисовку/перекрытие/teardown. Следующий шаг — отдельно
разрешённая установка и один визуальный тест частично закрытых Хильдой букв.
Установки/запуска игры не было; World runtime acceptance и production BLOCKED.

## История binding-проверки

**2026-10-29 — один natural Open actor/component/TipHUD join и world pose PASS;
probe отключён.** [Полные identity/координаты](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md):
603ab6b сохранил3 пары после ACQUISITION_CLOSED init128; CanShow после reload
выбрал0-1_lootbox_01_mat_ST001 класса item_lootbox02_C и его exact ExtendedWidget/
TipHUD.2 конечных world-pose снимка, затем user STOP result=MATCHED за46.394s,
show415/unmatched0/match1/poses2/hooks_remaining0. Ошибок probe нет.
Прямая live связь и один anchor доказаны; обе script routes пригодны в этом reload.
Лог сохранён; игра закрыта, снят только собственный enabled.txt.24 прочих baseline
mod/loader hashes совпали,88 текущих файлов сохранили хэши при отключении.
Следующий отдельный шаг — подготовить собственный World-component тест на этом
anchor, не менять оригинал. World rendering/occlusion и production BLOCKED.

**2026-10-29 — исправленная OpenJoin ревизия INSTALLED, runtime PENDING.**
Source603ab6be645bbc2b552f3e88e0d2448c981485b1, installed SHA256
932901d8766bfb3640ddd48f1d7811e8ccadbf83df2b63bc597dfece225ea664.
При закрытой игре заменён только own main.lua и добавлен enabled.txt;24 остальных
mod/loader и62 текущих config/save files сохранили хэши. Старый995a581f payload
и disabled-state сохранены для отката вне loader в локальном
beginplay-probe/budget-fix/install-20261029T165639Z. Только OpenJoin включён.
Игра/reload не запускались; [один пользовательский тест](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
проверяет продолжение CanShow после ACQUISITION_CLOSED и MATCH/POSE.
Это research handoff, не production release; VERSION/World gate не менялись.

**2026-10-29 — acquisition-budget correction READY_SOURCE, installation authorized.**
[Ревизия](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md)
закрывает только BeginPlay acquisition при128, сохраняя проверенные пары и CanShow.
Общие120s/4096 callbacks/4 poses и≤8 кандидатов прежние; лишние init contexts не
читаются даже при отложенном снятии hook.108 offline tests PASS, включая replay
3-пар/128-callback сценария с последующим MATCH. Lua SHA256
932901d8766bfb3640ddd48f1d7811e8ccadbf83df2b63bc597dfece225ea664.
Runtime новой ревизии не проверен; production/VERSION/World не меняются.

**2026-10-29 — OpenJoin: acquisition PASS, selection cut off by init budget;
probe отключён.** [Точный результат](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md):
после ручного reload получены3 реальные Open actor/component/TipHUD пары с
проверенными взаимными ссылками. Затем STOP init_budget за20.789s: init=128,
open/ready=3, show/matches/poses=0; ошибок probe нет.128 — callbacks, не число actor.
Подтверждён BeginPlay dispatch после reload; CanShow survival/visible join и pose
ещё не установлены. Лог сохранён, игра закрыта, снят только собственный enabled.txt;
24 старых mod/loader hashes совпали,87 остальных текущих файлов не изменились при
отключении. Код не менялся. Предложение следующего этапа — закрывать только
acquisition при128, сохраняя3 пары и прежние общие лимиты; не реализовано/не установлено.
World rendering и production BLOCKED.

## История подготовки и установки

**2026-10-29 — BeginPlay + CanShow OpenJoin probe INSTALLED, runtime PENDING на момент установки.**
По разрешению пользователя при закрытой игре установлен точный3497ab5 исходник,
Lua SHA256995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3.
Добавлены только main.lua/enabled.txt в новом ImmersiveInteractionPromptsOpenJoinProbe.
24 старых mod/loader и61 текущий config/save files сохранили хэши. Другие моды и
CombatHUD сохранены, старые IIP probes отключены. Вне loader сохранён rollback,
снимки и манифесты в локальном beginplay-probe/install-20261029T163735Z.
Игра/reload не запускались; следующий шаг — [один пользовательский reload/test](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md).
Live mapping/pose, World rendering и production остаются BLOCKED.

**2026-10-29 — BeginPlay + CanShow join probe READY_SOURCE, runtime NOT_TESTED.**
[Исходник/процедура](../research/interaction-prompts-owner/open-binding/beginplay-probe/README.md):
два точных single-callback script hooks,≤8 Open attempts,≤128 init/4096 CanShow,
120s wall-clock,≤4 pose snapshots только после взаимного identity join.
Проверены partial registration rollback, nil-return всех callbacks, source lifetime
script registry через LoadMap и cleanup при отсутствующей metadata.105 offline
tests/10 suites PASS. Lua SHA256995a581f2b05aa5acc2578c293792f90817655ba652027167c2fbdf1177c16e3.
Установки, запуска игры/reload/hot reload не было; production/VERSION не менялись.
Реальная сохранность двух hooks через ручной reload и live actor/component/pose
остаются непроверенными. Следующий шаг — отдельно разрешённая closed-game установка
этих байтов и один пользовательский reload/test. World/production BLOCKED.

**2026-10-29 — после NO_EVENTS выбран source-only маршрут: parent Blueprint
BeginPlay → точный join с CanShow. Новый payload не создан.**
[Переоценка архитектуры и контракт](../research/interaction-prompts-owner/open-binding/ROUTE_REVIEW.md):
BaseLoot/Open ReceiveBeginPlay входит в ubergraph2152 и явно вызывает родительский
BaseGameEventObject_BP.ReceiveBeginPlay; родитель получает own ExtendedWidget's
widget на102. Это более сильное callsite-доказательство, чем декларации native
Setup/SetArrayData. Для них natural timing/dispatch всё ещё неизвестны.
Предпочтительный следующий тест — ограниченный захват≤8 Open-пар на естественном
BeginPlay после ручного reload и сопоставление с уже доказанным CanShow callback.
Статус PREFERRED_ROUTE_DEFINED, live mapping/pose ещё NOT_OBSERVED. Runtime-код,
установка/игра/production/VERSION не менялись. World/production BLOCKED;
реальное перекрытие Хильдой остаётся требованием, Screen только fallback.

**2026-10-29 — Open binding: NO_EVENTS, mapping/pose NOT_OBSERVED; probe отключён.**
[Результат](../research/interaction-prompts-owner/open-binding/README.md): native
SetShow hook зарегистрирован IDs10/11, WAITING14:28:55.863 → STOP reason=user
14:29:27.828, callbacks=0/samples=0 за31.965s. Ошибок probe нет, но MATCH/POSE нет;
getter/identity-проверки не исполнялись. Причина отсутствия событий неизвестна.
Лог сохранён; игра закрыта, снят только свой enabled.txt.23 прежних mod/loader
hashes совпали;87 остальных текущих файлов не изменились при отключении.
Этот event route не закрыл live mapping gate. Не повторять/расширять прогон
автоматически: сначала отдельный выбор проверяемого входа. World/production BLOCKED.

## История подготовки Open binding

**2026-10-29 — Open binding probe INSTALLED; runtime PENDING.**
По явному разрешению пользователя при закрытой игре установлен точный148e5c0
Lua SHA256a56d8fda1821f28a01e1d1f4e423a8b33e60d3f36d2c7312c5c2ff3327d3f56f.
Добавлены только Scripts/main.lua + enabled.txt в собственном OpenBindingProbe;
23 прежних mod/loader и64 config/save files не изменились по хэшам. Старые IIP
probes отключены. Вне loader сохранены rollback/снимки/манифесты в локальном
open-binding/install-20261029T112539Z. Игра не запускалась; следующий шаг —
[один пользовательский Open test](../research/interaction-prompts-owner/open-binding/README.md#user-experiment--installation-authorizedcompleted-run-still-pending).
Live mapping/pose ещё не подтверждены, World/production BLOCKED.

**2026-10-29 — natural Open binding: READY_SOURCE для одного read-only теста,
live mapping ещё NOT_TESTED.** [Отчёт и исходник](../research/interaction-prompts-owner/open-binding/README.md):
один естественный post SetShow даёт component context без сканирования мира;
проверяются назначенный TipHUD, GetOwner, взаимная actor.ExtendedWidget ссылка,
Open/Interact и transform компонента. SenderActor/NewUserWidget не объявлены
эквивалентом владельца без проверки. Лимиты60s/64 callbacks/6 snapshots, явный stop,
нет retargeting/игровых записей.83 offline tests проходят. Реальный вызов этого
отражённого метода для natural Open, live identities и pose ещё не получены.
Ничего не установлено/не запущено. Host runtime PASS не повторялся.
World rendering/occlusion и production BLOCKED.

**2026-10-29 — independent UserWidget host runtime PASS; probe отключён.**
[Лог и границы](../research/interaction-prompts-owner/userwidget-host/probe/README.md):
точный LoadAsset found/loaded=true → private tree → Construct Hidden → VISIBLE →
ручной LABEL_REMOVED/OWNERSHIP_RELEASED/CLEANED reason=user за22.218s.
Исходный HUD fingerprint неизменен; пользователь подтвердил весь сценарий.
Игра закрыта, лог сохранён, снят только собственный enabled.txt;87 остальных
текущих файлов сохранили хэши при отключении. Host-блокер закрыт для этого класса
и одного viewport lifecycle. Следующий отдельный шаг — exact natural Open
actor/component/pose. World rendering/occlusion и production всё ещё BLOCKED.

## История этапов (предыдущие статусы на момент записи)

**2026-10-29 — independent UserWidget probe установлен по разрешению пользователя;
runtime PENDING.** Точный source commit a23635b95b029ff8d73dec4f940e1aa54c213d37,
Lua SHA25666ffdce4fecdf954981a5364320bc78f3f67df717ee16175673558bac9543186.
Игра проверена закрытой до записи и включения; добавлены только main.lua и
enabled.txt в новом ImmersiveInteractionPromptsUserWidgetHostProbe.
22 прежних mod/loader files и63 config/save files сохранили хэши; старые IIP probes
отключены. Локальный rollback/manifest/log snapshot вне loader:
host-probe/install-20261029T081829Z. Игра не запускалась. Следующий шаг — один
Ctrl+Alt+F6 show → Ctrl+Alt+F6 cleanup тест по [процедуре](../research/interaction-prompts-owner/userwidget-host/probe/README.md).
Production/World gates остаются BLOCKED.

**2026-10-29 — independent UserWidget probe READY_SOURCE; runtime NOT_TESTED.**
[Исходник и процедура](../research/interaction-prompts-owner/userwidget-host/probe/README.md):
точная `_C` запись подтверждена в локальном AssetRegistry. Одна попытка
lookup/LoadAsset→Create, проверка свежего экземпляра/частного дерева, собственная
тестовая строка после Construct Hidden, Ctrl+Alt+F6 cleanup и однократный60s timeout.
Нет World/Aphes/TipHUD mutations.74 offline mock tests проходят; native Create,
Slate/rendering и освобождение UI-владения пока не проверены в игре.
Ничего не установлено/не запущено. Следующий шаг — отдельно разрешённый host-only
тест. Exact Open binding и production gate остаются BLOCKED.

**2026-10-29 — первый host-блокер SOURCE_RESOLVED: найден PostionItemUMG_BP_C.**
[Проверка host](../research/interaction-prompts-owner/userwidget-host/README.md):
прямая база UMG.UserWidget, concrete, без Genesis native-посредника; 14 exports,
4 собственные функции, no Tick/Paint/animations/bindings/nested UserWidgets.
Construct скрывает только self (Hidden); будущая видимость — после первого Slate
build. Нативный Create/Initialize инстанцирует собственное дерево и Slate cache.
Runtime загрузка/создание/очистка не проверены. Кандидат SOURCE_READY для отдельного
host-only lifecycle test, не World/runtime PASS. Полный World-прототип BLOCKED на
exact natural Open actor/component/pose и его собственных runtime gates.
На этапе поиска класса payload не создавался; follow-up исходник подготовлен выше.
Установка/запуск не выполнялись; никаких новых cooker/C++ зависимостей.


**2026-10-29 — World-space study завершён source/offline; executable payload
BLOCKED, production BLOCKED.** [Точный отчёт](../research/interaction-prompts-owner/world-space/README.md).
Предпочтительный дизайн — объектная подсказка с реальным перекрытием Хильдой;
X50%/Y78% остаётся проверенным fallback. Материалы stock Widget3DPassThrough
найдены и parent/depth defaults проверены: обычный World mesh с depth test возможен
без special mask. Но это не runtime PASS в Asterigos.

A (переключить оригинал) отклонён для первого опыта: SetWidgetSpace только пишет
Space; FWidgetRenderer создаётся в OnRegister для World. Из Screen renderer может
отсутствовать, и Tick не заменяет регистрацию/полный перенос screen-layer caches.
B (свой plain transient WidgetComponent) предпочтителен, но ещё не READY:
изначально не было подтверждённого host и exact Open binding. Host-класс теперь
найден source-only (выше); точная связь natural Open TipHUD→компонент/owner/pose
остаётся неизвестной. Live TipHUD нельзя делить между рендерерами,
а UserWidget base Abstract. Известные игровые native-базы не объявлены пустыми.
Следующий достаточный шаг — подтвердить один независимый конкретный UserWidget
через Create/Initialize и его lifecycle; затем exact Open binding/material/pose.
Lua/C++ payload не создан; игра/настройки/сохранения/другие моды не менялись.
Не исследовались CustomDepth/post-process/special mask, не повторялись font/UI runs.

**2026-10-29 — screen placement/render/manual cleanup PASS; пользователь выбрал
X50% / Y78% для продолжения. Arrow tuning NOT_PASSED. Probe отключён. Production BLOCKED.**
[Точный результат](../research/interaction-prompts-owner/viewport/README.md):
пять own children + один Canvas в Main_Panel, viewport2560×1440, исходный TipHUD
видим/нетронут.02:28:05 initial POSITION50,78;02:30:43 CLEANED reason=user,
оба brush refs/font released, все элементы и own Canvas удалены до180s timeout.
Стрелки двигали камеру по сообщению пользователя; в логе нет move/reset/commit.
Причина input routing не установлена, Home/F7 не приняты. Позиция выбрана словами
пользователя и кадром, без ложного успешного F7. Ремонт стрелок на этом этапе отложен.
Source242a5f0/helper/config/TTF/PNG/DLL и18 prior mod/loader files совпали.
Raw log/frame локально; при закрытой игре снят только свой enabled.txt.
Сохранить принятую геометрию при удалении debug indicator. Следующая осмысленная
граница — native state/show-hide для одного Open, ещё без production lifecycle.

**2026-10-29 — компактная композиция технически сработала в игре;
пользователь подтвердил видимый результат. Probe отключён. Production BLOCKED.**
[Точный результат](../research/interaction-prompts-owner/composition/README.md):
one local stock PNG import→TEXTURE_BOUND, Aphes/ornament/lower placement shown
in the user frame.00:33:27 LOWER_RESTORED→оба REMOVED→TEXTURE_UNBOUND/FONT_RELEASED→
CLEANED reason=target-state-changed за≈17.04с, до timeout; поздние user-key очистки
на нуле без повторного создания. Это не manual removal while attached/READ-тест.
Source996ee47, helper/config/TTF/PNG/DLL и15 старых mod/loader files совпали.
Лог/кадр сохранены локально; при закрытой игре снят только enabled.txt.
Оформление ещё не принято: особенно заметность тонкого орнамента и интервалы.
Следующий шаг — согласовать композиционные поправки, без повтора font/import
исследования и без автоматической установки новой версии.

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
