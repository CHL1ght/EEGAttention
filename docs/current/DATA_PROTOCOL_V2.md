# New Paradigm v1 数据协议

适用范围：`data/current/new_paradigm_v1/`。旧 `data/legacy_manifest.csv`、旧 `data/session_manifest.csv` 和 2026-09-14 pilot 不受本协议驱动，也不是新范式训练入口。

## 1. Session 定义

- 一个真实 EDF 是一个 session，并且只登记一个 canonical label。
- 4 秒窗口或其他切窗只是 session 内样本，不能增加 session 数量。
- 同一 session 的所有窗口必须落在同一个 split。
- `day_id` 按 subject 与真实 recording date 稳定登记，例如 `lyc_20260920`；不能根据模型结果重分 day。

## 2. 采集控制

同一批 focus/unfocus 应保持任务、设备、姿势和环境尽可能一致，只改变目标精神状态或任务投入状态。现场 notes 至少记录任务、目标标签、开始/结束时间、姿势、环境、佩戴情况、异常和中断；没有信息写 `unknown`。

原始 EDF/CSV/DSI 不就地编辑。标签纠正通过 manifest 和 notes 保留 provenance，不通过重命名原始文件完成。

## 3. 标签事实来源

优先级：同 stem notes > 明确现场人工 metadata > filename label。若来源冲突，应在 notes 中记录原始值、canonical 值、来源和原因；模型预测永远不能成为改标签依据。

## 4. Manifest schema

权威清单：[session_manifest.csv](../../data/current/new_paradigm_v1/session_manifest.csv)。当前登记 2026-09-16 的 7 条 lyc session，其中 6 条二分类 session 可进入当前 first-pass，1 条 observe 为 reference/control。

| 字段 | 规则 |
|---|---|
| `session_id` | 稳定且唯一；一个 EDF 一个 session。 |
| `subject_id` | 明确受试者标识。 |
| `recorded_date`, `recorded_time`, `timezone` | 真实现场时间。 |
| `day_id` | subject × recording day 稳定分组。 |
| `canonical_label` | 主任务仅 `focus` 或 `unfocus`；明确的非二分类控制条件可用 `observe`，但必须是 `reference/excluded`。 |
| `task` | 标准化任务名称。 |
| `paradigm_version` | 固定为 `new_paradigm_v1`。 |
| `dataset_role` | `train_candidate`、`validation_candidate`、`final_holdout`、`reference` 或 `excluded`。 |
| `split_role` | `pending`、`train`、`validation`、`final_test` 或 `excluded`。 |
| `edf_path`, `csv_path`, `dsi_path`, `note_path` | 仓库相对路径；原始文件和现场记录。 |
| `recording_duration_s` | EDF 实际时长。 |
| `activity_start_s`, `activity_end_s` | 预先定义的有效任务区间。 |
| `window_sec`, `step_sec` | 当前计划默认 4 秒、2 秒；变更必须版本化。 |
| `sfreq_hz`, `n_signals` | 原始 EDF 采样率和信号数。 |
| `sha256` | EDF SHA-256；其他 sidecar 哈希分别写入对应字段。 |
| `status` | `recorded_unverified`、`ready`、`frozen_before_prediction` 或 `excluded`。 |
| `notes` | 任务、佩戴、环境、异常、标签冲突和其他 provenance。 |

## 5. 数据角色和晋升

- `train_candidate`：可在 protocol 检查通过后进入新范式训练；不得自动跨版本复用。
- `validation_candidate`：只用于新范式模型选择或开发期评估，不进入对应 fit。
- `final_holdout`：预测前预先指定，`split_role=final_test` 且 `status=frozen_before_prediction`。
- `reference`：用于说明或诊断，不进入主训练。
- `excluded`：保留原始记录和排除原因。

`observe` 是控制条件，不得重标为 focus/unfocus；必须使用 `dataset_role=reference`、`split_role=excluded`，只允许 prediction-only 描述，不计入训练、模型选择或 accuracy。

任何角色变化都必须在预测前完成，并保留 Git 历史。不能依据模型结果把 session 从 validation/final 改成 training，也不能从已看过结果的数据中挑 final holdout。

## 6. 当前可训练范围

当前 manifest 无 session，因此 New Paradigm v1 暂无可训练数据。未来只有同时满足以下条件的记录才允许进入主训练：

- `paradigm_version=new_paradigm_v1`
- `dataset_role=train_candidate`
- `split_role=train`
- `status=ready`
- 路径、时长、活动区间和哈希验证通过

历史数据和 REFERENCE 数据只能在后续明确命名的 ablation 中使用。
