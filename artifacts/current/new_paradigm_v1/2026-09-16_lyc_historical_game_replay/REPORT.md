# Frozen 2026-09-16 model — historical lyc gaming replay

## Boundary

This is a prediction-only replay. The frozen 2026-09-16 lyc New Paradigm v1 first-pass scaler, PCA, and SVC were loaded directly. Historical data were used only for the unchanged preprocessing/feature transform and prediction path. `fit_calls=0`; there was no calibration, parameter search, threshold adjustment, relabeling, or model update.

Frozen model SHA256: `2b7b97f9f2399bcd3595df63a406fd66adfb470edc7f9390d8d67d45431d8e24`.

**historical label is not guaranteed semantically equivalent to New Paradigm v1.** No strict cross-day generalization accuracy is reported.

## Included scope

Reliable historical sessions: **24**. Of these, 8 explicitly document 王者荣耀/玩王者; 16 older self-recordings explicitly document gaming but do not identify the game title.

## Historical metadata retained for comparison

| date | session / EDF | historical label | task | recording duration | analyzed interval | notes/context |
|---|---|---|---|---:|---:|---|
| 2026-09-14 | `lyc_focus_202609141641` / `lyc_focus_202609141641_raw.edf` | focus | 玩王者（排位） | 937.5 s | 0.0–937.5 s | 大部分时间专注；精神高度集中操作谨慎；角色死亡后可能分心30-59s直至复活 |
| 2026-09-14 | `lyc_focus_202609141702` / `lyc_focus_202609141702_raw.edf` | focus | 玩王者（排位） | 707.0 s | 0.0–707.0 s | 大部分时间专注；精神高度集中操作谨慎；角色死亡后可能分心30-59s直至复活 |
| 2026-09-14 | `lyc_focus_202609141717` / `lyc_focus_202609141717_raw.edf` | focus | 玩王者（排位） | 798.0 s | 0.0–798.0 s | 大部分时间专注；精神高度集中操作谨慎；角色死亡后可能分心30-59s直至复活 |
| 2026-09-14 | `lyc_focus_202609141800` / `lyc_focus_202609141800_raw.edf` | focus | 玩王者（排位） | 1271.0 s | 0.0–1271.0 s | 大部分时间专注；精神高度集中操作谨慎；角色死亡后可能分心30-59s直至复活 |
| 2026-09-14 | `lyc_focus_202609141959` / `lyc_focus_202609141959_raw.edf` | focus | 玩王者（排位） | 217.5 s | 0.0–217.5 s | 大部分时间专注；精神高度集中操作谨慎；角色死亡后可能分心30-59s直至复活 |
| 2026-09-14 | `lyc_focus_202609142023` / `lyc_focus_202609142023_raw.edf` | focus | 玩王者（排位） | 697.0 s | 0.0–697.0 s | 大部分时间专注；精神高度集中操作谨慎；角色死亡后可能分心30-59s直至复活 |
| 2026-09-14 | `lyc_unfocus_202609141825` / `lyc_unfocus_202609141825_raw.edf` | unfocus | 玩王者（排位） | 1139.5 s | 0.0–1139.5 s | 虽然叫做不专注状态，但是一直在玩游戏；玩的很放松精神不紧张 |
| 2026-09-07 | `20260907_lyc_focus_02` / `lyc_focus_202609072034_raw.edf` | focus | 王者荣耀 | 629.5 s | 30.0–599.5 s | 王者荣耀专注录制；首尾各保留 30 秒操作缓冲 |
| 2026-07-08 | `legacy_lyc_focus_07` / `focus7.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-08 | `legacy_lyc_focus_08` / `focus8.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-08 | `legacy_lyc_focus_09` / `focus9.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_focus_03` / `focus3.edf` | focus | 专注打游戏 | 905.5 s | 0.0–905.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_focus_04` / `focus4.edf` | focus | 专注打游戏 | 650.5 s | 0.0–650.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_focus_05` / `focus5.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_focus_06` / `focus6.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_iu_03` / `iu3.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_iu_04` / `iu4.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-07 | `legacy_lyc_ou_03` / `ou3.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-06 | `legacy_lyc_focus_01` / `focus1.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-06 | `legacy_lyc_focus_02` / `focus2.edf` | focus | 专注打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-06 | `legacy_lyc_iu_01` / `iu1.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-06 | `legacy_lyc_iu_02` / `iu2.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-06 | `legacy_lyc_ou_01` / `ou1.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |
| 2026-07-06 | `legacy_lyc_ou_02` / `ou2.edf` | unfocus | 分心打游戏 | 599.5 s | 0.0–599.5 s | subject confirmed by data owner; EDF header start cross-checked against file modification time; session group is a conservative filename-based grouping |

## Session predictions

| date | historical session | historical label → prediction | valid windows | focus windows | unfocus windows | mean focus prob | median | Q25–Q75 | min–max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-09-14 | `lyc_focus_202609141641` / `lyc_focus_202609141641_raw.edf` | focus → focus | 467 | 342 (73.23%) | 125 (26.77%) | 0.7141 | 0.8688 | 0.4883–0.9823 | 0.0000–1.0000 |
| 2026-09-14 | `lyc_focus_202609141702` / `lyc_focus_202609141702_raw.edf` | focus → focus | 352 | 306 (86.93%) | 46 (13.07%) | 0.8336 | 0.9462 | 0.7776–0.9912 | 0.0000–0.9999 |
| 2026-09-14 | `lyc_focus_202609141717` / `lyc_focus_202609141717_raw.edf` | focus → focus | 398 | 334 (83.92%) | 64 (16.08%) | 0.8151 | 0.9472 | 0.7445–0.9923 | 0.0213–0.9999 |
| 2026-09-14 | `lyc_focus_202609141800` / `lyc_focus_202609141800_raw.edf` | focus → focus | 634 | 559 (88.17%) | 75 (11.83%) | 0.8491 | 0.9570 | 0.8267–0.9922 | 0.0073–1.0000 |
| 2026-09-14 | `lyc_focus_202609141959` / `lyc_focus_202609141959_raw.edf` | focus → focus | 107 | 105 (98.13%) | 2 (1.87%) | 0.9580 | 0.9951 | 0.9730–0.9988 | 0.3503–1.0000 |
| 2026-09-14 | `lyc_focus_202609142023` / `lyc_focus_202609142023_raw.edf` | focus → focus | 347 | 283 (81.56%) | 64 (18.44%) | 0.7762 | 0.9005 | 0.6598–0.9776 | 0.0032–1.0000 |
| 2026-09-14 | `lyc_unfocus_202609141825` / `lyc_unfocus_202609141825_raw.edf` | unfocus → focus | 568 | 303 (53.35%) | 265 (46.65%) | 0.5364 | 0.5788 | 0.1725–0.9044 | 0.0000–0.9999 |
| 2026-09-07 | `20260907_lyc_focus_02` / `lyc_focus_202609072034_raw.edf` | focus → focus | 283 | 258 (91.17%) | 25 (8.83%) | 0.8541 | 0.9414 | 0.7871–0.9886 | 0.0906–0.9999 |
| 2026-07-08 | `legacy_lyc_focus_07` / `focus7.edf` | focus → unfocus | 298 | 2 (0.67%) | 296 (99.33%) | 0.3805 | 0.3675 | 0.3504–0.4008 | 0.3297–0.5483 |
| 2026-07-08 | `legacy_lyc_focus_08` / `focus8.edf` | focus → unfocus | 298 | 1 (0.34%) | 297 (99.66%) | 0.3550 | 0.3476 | 0.3367–0.3608 | 0.3242–0.5840 |
| 2026-07-08 | `legacy_lyc_focus_09` / `focus9.edf` | focus → unfocus | 298 | 0 (0.00%) | 298 (100.00%) | 0.3223 | 0.3246 | 0.3173–0.3289 | 0.2795–0.3486 |
| 2026-07-07 | `legacy_lyc_focus_03` / `focus3.edf` | focus → unfocus | 451 | 0 (0.00%) | 451 (100.00%) | 0.1079 | 0.1000 | 0.0585–0.1526 | 0.0074–0.2922 |
| 2026-07-07 | `legacy_lyc_focus_04` / `focus4.edf` | focus → unfocus | 324 | 6 (1.85%) | 318 (98.15%) | 0.1126 | 0.0596 | 0.0255–0.1386 | 0.0000–0.7782 |
| 2026-07-07 | `legacy_lyc_focus_05` / `focus5.edf` | focus → unfocus | 298 | 7 (2.35%) | 291 (97.65%) | 0.0595 | 0.0163 | 0.0082–0.0396 | 0.0000–0.9417 |
| 2026-07-07 | `legacy_lyc_focus_06` / `focus6.edf` | focus → unfocus | 298 | 24 (8.05%) | 274 (91.95%) | 0.1377 | 0.0474 | 0.0138–0.1348 | 0.0000–0.9734 |
| 2026-07-07 | `legacy_lyc_iu_03` / `iu3.edf` | unfocus → unfocus | 298 | 3 (1.01%) | 295 (98.99%) | 0.0499 | 0.0088 | 0.0027–0.0495 | 0.0000–0.6129 |
| 2026-07-07 | `legacy_lyc_iu_04` / `iu4.edf` | unfocus → unfocus | 298 | 18 (6.04%) | 280 (93.96%) | 0.1220 | 0.0281 | 0.0097–0.1386 | 0.0000–0.9666 |
| 2026-07-07 | `legacy_lyc_ou_03` / `ou3.edf` | unfocus → unfocus | 298 | 0 (0.00%) | 298 (100.00%) | 0.1005 | 0.0751 | 0.0409–0.1219 | 0.0042–0.3543 |
| 2026-07-06 | `legacy_lyc_focus_01` / `focus1.edf` | focus → unfocus | 298 | 3 (1.01%) | 295 (98.99%) | 0.0394 | 0.0124 | 0.0040–0.0328 | 0.0000–0.9473 |
| 2026-07-06 | `legacy_lyc_focus_02` / `focus2.edf` | focus → unfocus | 298 | 0 (0.00%) | 298 (100.00%) | 0.0158 | 0.0038 | 0.0000–0.0090 | 0.0000–0.4223 |
| 2026-07-06 | `legacy_lyc_iu_01` / `iu1.edf` | unfocus → unfocus | 298 | 13 (4.36%) | 285 (95.64%) | 0.0801 | 0.0107 | 0.0051–0.0408 | 0.0000–0.9016 |
| 2026-07-06 | `legacy_lyc_iu_02` / `iu2.edf` | unfocus → unfocus | 298 | 26 (8.72%) | 272 (91.28%) | 0.1308 | 0.0312 | 0.0085–0.1148 | 0.0000–0.9753 |
| 2026-07-06 | `legacy_lyc_ou_01` / `ou1.edf` | unfocus → unfocus | 298 | 4 (1.34%) | 294 (98.66%) | 0.0455 | 0.0079 | 0.0026–0.0340 | 0.0000–0.8678 |
| 2026-07-06 | `legacy_lyc_ou_02` / `ou2.edf` | unfocus → unfocus | 298 | 11 (3.69%) | 287 (96.31%) | 0.0916 | 0.0279 | 0.0124–0.0699 | 0.0000–0.9546 |

## Strict ‘认真打王者’ subset

This strict subset contains only sessions explicitly documented as 王者荣耀/玩王者 and historically described as focus/认真/高度集中. Original labels remain post-hoc context only.

| historical session | original context | focus % | mean focus prob | majority |
|---|---|---:|---:|---|
| `lyc_focus_202609141641` | 明确记录为玩王者/排位 | 73.23% | 0.7141 | focus |
| `lyc_focus_202609141702` | 明确记录为玩王者/排位 | 86.93% | 0.8336 | focus |
| `lyc_focus_202609141717` | 明确记录为玩王者/排位 | 83.92% | 0.8151 | focus |
| `lyc_focus_202609141800` | 明确记录为玩王者/排位 | 88.17% | 0.8491 | focus |
| `lyc_focus_202609141959` | 明确记录为玩王者/排位 | 98.13% | 0.9580 | focus |
| `lyc_focus_202609142023` | 明确记录为玩王者/排位 | 81.56% | 0.7762 | focus |
| `20260907_lyc_focus_02` | 明确记录为王者荣耀专注录制 | 91.17% | 0.8541 | focus |

Across these 7 sessions, the window-weighted focus proportion is 84.51%; session majorities are focus=7, unfocus=0. By this descriptive replay, they lean **focus**.

## Session-to-session variation

Across all included sessions, focus-window proportions range from 0.00% to 98.13%. This spread is reported descriptively and is not used to alter the model or labels.

## Exclusions

| candidate/group | reason |
|---|---|
| `20260907_lyc_focus_01` | 任务明确为课堂视频专注，不是游戏/王者 |
| `20260907_lyc_unfocus_01` | 任务明确为课堂视频不专注，不是游戏/王者 |
| `20260907_lyc_rest_01` | 静息态，不是游戏/王者 |
| `legacy_lyc_daze_01|legacy_lyc_daze_02` | legacy rest/daze，不是打游戏任务 |
| `legacy_lyc_mixed_demo_00` | 2.5 秒 setup/demo，短于一个 4 秒窗口，且任务未知 |
| `legacy_lyc_mixed_01|legacy_lyc_mixed_02|legacy_lyc_mixed_03` | 只能确认 focus/unfocus 分段顺序，无法从可靠 metadata/notes 确认是打游戏 |
| `2026-09-14 non-lyc sessions` | subject_id 不是 lyc |
| `zyf/zqd/author/common6 and other non-lyc data` | 超出只测 lyc 本人录制数据的范围 |
| `2026-09-16 current New Paradigm v1 sessions` | 属于冻结模型训练日数据，不是 historical replay 输入 |

## Required interpretation statement

**本分析是 frozen 2026-09-16 model 对 historical lyc gaming sessions 的 prediction-only replay，未参与任何 fit，不属于独立 final test。**
