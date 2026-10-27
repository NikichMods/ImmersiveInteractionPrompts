# Verified Runtime — Interaction Prompts

**Нет принятой технической проверки цепочки contextual interaction prompts.** Имена widget, class, asset, локализационных полей, функции появления/скрытия, final writer и подходящего игрового шрифта пока неизвестны.

Повторно используемый [Asterigos Research](https://github.com/NikichMods/Asterigos-Research/blob/main/docs/RESEARCH_INDEX.md) фиксирует Steam 1.09/build 12996889, UE4.27, Windows x64 и принятый UE4SS/UEHelpers baseline. Соседние модули доказали частичную работу с UMG/Coherent UI и некоторыми шрифтами, но **не** применимость того же пути к взаимодействиям. Упоминание Aphes среди шрифтов в root LICENSING.md не доказывает правильное отображение букв, алфавит или возможность дистрибуции.

Исследовать: фактический owner и final writer; штатные localized text/input hints; hide/show, lifecycle и соседние UI surfaces; glyph asset/charset/смысл; fallback/rollback. Записывать сборку, точный путь, воспроизводимую проверку, источник и ограничения. Не помещать raw game assets, exports или logs в публичный Git.

Задача: [RESEARCH_PLAN.md](RESEARCH_PLAN.md).
