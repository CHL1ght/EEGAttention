# Exploratory 数据（HISTORICAL）

本目录保留旧 exploratory 数据和当时的实验规则。2026-09-14 LAB_FEEDBACK 已完成并冻结为 `historical pilot / transition dataset`；当前正式采集入口已切换到 [New Paradigm v1](../current/new_paradigm_v1/README.md)。

## 目录

| 路径 | 状态与用途 |
|---|---|
| [lab_feedback/](lab_feedback/README.md) | Stage 8 历史现场反馈探索；只做过 prediction-only 分析。 |

## 边界

- 原始 EDF/CSV/DSI/notes 不改名、不覆盖。
- historical pilot 不进入 legacy manifest、旧 session manifest、LOCKED_TEST、New Paradigm v1 manifest 或 future final holdout。
- 模型预测不能改变 canonical label。
- 新采集和新训练资格由 [DATA_PROTOCOL_V2](../../docs/current/DATA_PROTOCOL_V2.md) 管理。
