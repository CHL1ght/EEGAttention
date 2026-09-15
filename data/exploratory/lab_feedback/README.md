# LAB_FEEDBACK（HISTORICAL）

本目录保存 Stage 8 现场反馈探索。它现已冻结为 `historical pilot / transition dataset / lab_feedback`，不是 CURRENT 训练、验证或最终测试入口。

## 已归档批次

| 批次 | 内容 | 状态 |
|---|---|---|
| [2026-09-14/](2026-09-14/README.md) | 11 条 EDF，均有 CSV/DSI；metadata、哈希、notes 与 11×3 prediction-only 分析已归档。 | `archived_verified` |

标签事实来源固定为：同 stem `.md notes` > 明确现场 metadata/人工记录 > 文件名。冲突通过 `filename_label`、`canonical_label`、`label_source`、`label_conflict` 和 `label_conflict_note` 保存，不重命名原始文件，也不根据模型结果改标签。

本批 feedback round 缺少可靠记录，因此保持 `unknown`；时间先后不能用于推断是否看过反馈。所有记录统一为 `dataset_role=historical_pilot`、`experiment_version=pre_new_paradigm/lab_feedback_2026-09-14`，training/validation/final-test eligibility 均为 `false`。

CURRENT 采集规则见 [DATA_PROTOCOL_V2](../../../docs/current/DATA_PROTOCOL_V2.md)，当前数据入口见 [New Paradigm v1](../../current/new_paradigm_v1/README.md)。
