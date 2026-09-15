# LAB_FEEDBACK 2026-09-14 prediction-only analysis

归档状态：`HISTORICAL / historical pilot / transition dataset`。本报告和 CSV 保留当次输出，不是 New Paradigm v1 的 CURRENT 结果。

本报告只描述已有 frozen pipeline 对现场 EDF 的 `predict()` 输出。没有训练、微调、calibration、阈值调整或重新保存模型。所有 accuracy 和 `target_class_proportion` 均使用 metadata 中的 `canonical_label`，不使用 filename label，也不使用模型输出修改标签。

输入为每个 EDF 的全时长，复用既有 4 秒窗口、2 秒步长特征入口。pooled/personal 使用 240 维正式特征，mixed-common6 使用独立的 60 维 common6 特征。

## 11 条 EDF 三模型结果

| subject | timestamp | EDF | filename → canonical | label source | pooled target% | personal target% | mixed target% |
|---|---|---|---|---|---|---|---|
| lyc | 2026-09-14T16:41:00+08:00 | lyc_focus_202609141641_raw.edf | focus → focus | md_note_shared | 67.88% | 44.97% | 57.82% |
| lyc | 2026-09-14T17:02:00+08:00 | lyc_focus_202609141702_raw.edf | focus → focus | md_note_shared | 67.05% | 32.39% | 55.11% |
| lyc | 2026-09-14T17:17:00+08:00 | lyc_focus_202609141717_raw.edf | focus → focus | md_note_shared | 58.79% | 29.15% | 53.02% |
| lyc | 2026-09-14T18:00:00+08:00 | lyc_focus_202609141800_raw.edf | focus → focus | md_note_shared | 72.08% | 54.42% | 47.16% |
| lyc | 2026-09-14T18:25:00+08:00 | lyc_unfocus_202609141825_raw.edf | unfocus → unfocus | md_note_shared | 69.01% | 76.23% | 66.20% |
| lyc | 2026-09-14T19:59:00+08:00 | lyc_focus_202609141959_raw.edf | focus → focus | md_note_shared | 53.27% | 27.10% | 31.78% |
| lyc | 2026-09-14T20:23:00+08:00 | lyc_focus_202609142023_raw.edf | focus → focus | md_note_shared | 20.46% | 4.03% | 6.63% |
| zyf | 2026-09-14T16:41:00+08:00 | zyf_unfocus_202609141641.edf | unfocus → focus | md_note | 10.63% | 4.56% | 8.03% |
| zyf | 2026-09-14T17:07:00+08:00 | zyf_unfocus_202609141707.edf | unfocus → focus | md_note | 12.58% | 7.95% | 33.44% |
| zyf | 2026-09-14T17:52:00+08:00 | zyf_focus_202609141752.edf | focus → focus | md_note | 3.63% | 2.23% | 19.27% |
| zyf | 2026-09-14T18:10:00+08:00 | zyf_focus_202609141810.edf | focus → focus | md_note | 2.15% | 2.86% | 31.98% |

`target%` 与本批单一 canonical label 下的 window accuracy 数值相同，但含义仍以 canonical label 为准。

## A. 同一被试跨 session 波动

以下为同一 subject、同一 canonical label 内的描述性 session 波动；单 session 的组不作波动解释。

### lyc
- canonical `focus`，n=6：
  - mixed-common6：range 51.19%，population SD 17.92%，chronological mean absolute step 10.24%.
  - personal：range 50.38%，population SD 15.73%，chronological mean absolute step 18.29%.
  - pooled：range 51.62%，population SD 17.31%，chronological mean absolute step 14.80%.
- canonical `unfocus`，n=1：
  - mixed-common6：range 0.00%，population SD 0.00%，chronological mean absolute step unknown.
  - personal：range 0.00%，population SD 0.00%，chronological mean absolute step unknown.
  - pooled：range 0.00%，population SD 0.00%，chronological mean absolute step unknown.

### zyf
- canonical `focus`，n=4：
  - mixed-common6：range 25.42%，population SD 10.34%，chronological mean absolute step 17.43%.
  - personal：range 5.71%，population SD 2.22%，chronological mean absolute step 3.24%.
  - pooled：range 10.43%，population SD 4.44%，chronological mean absolute step 4.13%.

## B. 三模型一致性

按 `target proportion > 0.5` 支持 intended state 的规则，三模型都不支持 canonical label 的 session：
- `lyc_focus_202609142023_raw.edf`（lyc 2026-09-14T20:23:00+08:00，canonical=focus）：pooled 20.46%，personal 4.03%，mixed-common6 6.63%.
- `zyf_unfocus_202609141641.edf`（zyf 2026-09-14T16:41:00+08:00，canonical=focus）：pooled 10.63%，personal 4.56%，mixed-common6 8.03%.
- `zyf_unfocus_202609141707.edf`（zyf 2026-09-14T17:07:00+08:00，canonical=focus）：pooled 12.58%，personal 7.95%，mixed-common6 33.44%.
- `zyf_focus_202609141752.edf`（zyf 2026-09-14T17:52:00+08:00，canonical=focus）：pooled 3.63%，personal 2.23%，mixed-common6 19.27%.
- `zyf_focus_202609141810.edf`（zyf 2026-09-14T18:10:00+08:00，canonical=focus）：pooled 2.15%，personal 2.86%，mixed-common6 31.98%.

personal 独自异常（pooled 与 mixed-common6 同侧，personal 另一侧）：
- `lyc_focus_202609141641_raw.edf`（lyc 2026-09-14T16:41:00+08:00）。
- `lyc_focus_202609141702_raw.edf`（lyc 2026-09-14T17:02:00+08:00）。
- `lyc_focus_202609141717_raw.edf`（lyc 2026-09-14T17:17:00+08:00）。

## C. 时间序列

## chronological session sequence

| subject | timestamp | EDF | canonical | pooled | personal | mixed-common6 |
|---|---|---|---|---|---|---|
| lyc | 2026-09-14T16:41:00+08:00 | lyc_focus_202609141641_raw.edf | focus | 67.88% | 44.97% | 57.82% |
| lyc | 2026-09-14T17:02:00+08:00 | lyc_focus_202609141702_raw.edf | focus | 67.05% | 32.39% | 55.11% |
| lyc | 2026-09-14T17:17:00+08:00 | lyc_focus_202609141717_raw.edf | focus | 58.79% | 29.15% | 53.02% |
| lyc | 2026-09-14T18:00:00+08:00 | lyc_focus_202609141800_raw.edf | focus | 72.08% | 54.42% | 47.16% |
| lyc | 2026-09-14T18:25:00+08:00 | lyc_unfocus_202609141825_raw.edf | unfocus | 69.01% | 76.23% | 66.20% |
| lyc | 2026-09-14T19:59:00+08:00 | lyc_focus_202609141959_raw.edf | focus | 53.27% | 27.10% | 31.78% |
| lyc | 2026-09-14T20:23:00+08:00 | lyc_focus_202609142023_raw.edf | focus | 20.46% | 4.03% | 6.63% |
| zyf | 2026-09-14T16:41:00+08:00 | zyf_unfocus_202609141641.edf | focus | 10.63% | 4.56% | 8.03% |
| zyf | 2026-09-14T17:07:00+08:00 | zyf_unfocus_202609141707.edf | focus | 12.58% | 7.95% | 33.44% |
| zyf | 2026-09-14T17:52:00+08:00 | zyf_focus_202609141752.edf | focus | 3.63% | 2.23% | 19.27% |
| zyf | 2026-09-14T18:10:00+08:00 | zyf_focus_202609141810.edf | focus | 2.15% | 2.86% | 31.98% |

时间只按真实 timestamp 排序；本表不将时间顺序解释为 feedback round，也不表示 feedback improvement 或 calibration 前后变化。

## zyf focus 17:52 与 18:10

| timestamp | pooled focus% | zyf personal focus% | mixed-common6 focus% |
|---|---|---|---|
| 2026-09-14T17:52:00+08:00 | 3.63% | 2.23% | 19.27% |
| 2026-09-14T18:10:00+08:00 | 2.15% | 2.86% | 31.98% |

这里仅比较两条 canonical focus recording 的描述性输出，不能据此下 calibration、attention state 因果或 feedback 效果结论。

## 稳定性与 shift 边界

在可比较组（同一 subject、同一 canonical label 且 n≥2）中，各模型 population SD 的组间平均为：personal 8.97%, pooled 10.88%, mixed-common6 14.13%。
按这个小样本描述性指标，离散度最低的是 `personal`；这不是模型优越性或泛化结论。
本批只有 2026-09-14 一天，不能识别 day shift。若把 session 间 target proportion 的差异称为 session shift，只能报告上述 range/SD；feedback round 全部 unknown，因此不能把它解释为 feedback-driven change。

## 资格与运行保护

- 11 条数据现归档为 `dataset_role=historical_pilot`、`experiment_version=pre_new_paradigm/lab_feedback_2026-09-14`，且 training/validation/final-test eligibility 均为 `false`。
- 没有写入 `legacy_manifest.csv`、`LOCKED_TEST`、New Paradigm v1 manifest 或 future final holdout。
- 本次每个 recording × 3 model 均只调用 `predict()`；运行时 `fit_calls=0`，且禁止模型 artifact 写出。
- 详细逐模型字段见 [session_model_summary.csv](session_model_summary.csv)，session 分类见 [session_consistency.csv](session_consistency.csv)，波动统计见 [session_stability.csv](session_stability.csv)。
