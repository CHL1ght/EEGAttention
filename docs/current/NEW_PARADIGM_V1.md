# New Paradigm v1

状态：`CURRENT`。已登记 2026-09-16 lyc focus ×3、unfocus ×3、observe control ×1，并完成单日 6-session leave-one-session-out first pass。该结果仅为探索性单日结果，不代表跨日泛化。

## 研究目标

新范式不继续沿用 2026-09-14 LAB_FEEDBACK 对 focus 的现场定义。目标是重新采集标准化、平衡、跨 session、跨 recording day 的 focus/unfocus 数据，再建立同范式模型并检验泛化。

2026-09-14 pilot 显示旧模型对新任务状态定义存在明显失配和 session variation。这个结果只说明需要重新标准化采集；不证明某个心理状态、反馈或 calibration 导致了变化。

## 第一阶段采集原则

- 同一任务条件、同一设备、尽量相同姿势和环境。
- 一个 EDF 只对应一个目标状态。
- 除目标精神状态或任务投入程度外，尽量不改变其他条件。
- 窗口只能作为同一 session 内的样本，不能计作独立 session。

第一轮 pilot 最低目标：

| subject | focus sessions | unfocus sessions |
|---|---:|---:|
| lyc | ≥4 | ≥4 |
| zyf | ≥4 | ≥4 |

正式版本目标：每人 focus ≥6、unfocus ≥6，覆盖至少 2–3 个 recording day。

## 未来模型计划

按以下顺序建立新模型：

1. `lyc-new personal`
2. `zyf-new personal`
3. `new-paradigm pooled`

第一轮训练只允许使用 `data/current/new_paradigm_v1/session_manifest.csv` 中符合资格的 New Paradigm v1 session。不得混入 legacy old data、author data、2026-09-14 LAB_FEEDBACK pilot 或 common6 historical training。

若 new-only 结果成立，再把 `new + old`、`new + author` 作为独立 ablation；不得静默改变主模型训练范围。

## 划分与评估

- 从第一天开始执行 session-level isolation；一个 EDF 的窗口不能跨 split。
- 有多个 recording day 后，优先增加 leave-one-day-out 分析。
- final holdout 必须在任何预测、模型选择、阈值调整之前预先登记并冻结。
- final holdout 从不参与 fit、模型选择、阈值调整或 calibration。

## 入口

- 数据目录：[data/current/new_paradigm_v1](../../data/current/new_paradigm_v1/README.md)
- 数据协议：[DATA_PROTOCOL_V2](DATA_PROTOCOL_V2.md)
- 当前校验：`scripts/validate_new_paradigm_data.py`
- 未来训练/评估入口预留为 `scripts/train_new_paradigm.py` 和 `scripts/evaluate_new_paradigm.py`；本轮不创建训练实现，继续复用 `eeg_pipeline_utils.py`，不复制预处理/特征管线。
