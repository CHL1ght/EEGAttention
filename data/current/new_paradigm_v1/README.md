# New Paradigm v1 数据

状态：`CURRENT`。

这里是今后正式采集的标准化 focus/unfocus 数据入口。`focus` / `unfocus` 暂时是实验操作标签；更高层研究构念是 task engagement，需要后续控制实验逐步验证。

## 目录

| 路径 | 用途 |
|---|---|
| [session_manifest.csv](session_manifest.csv) | New Paradigm v1 唯一 session 清单；当前含 2026-09-16 的 7 条 lyc session。 |
| [control_experiment_log_template.csv](control_experiment_log_template.csv) | 控制实验的空白辅助模板；只有 header，不代表任何真实 session。 |
| [raw/](raw/README.md) | 设备导出的原始 EDF/CSV/DSI；按 subject 归档。 |
| [notes/](notes/README.md) | 与 session 一一对应的现场 notes。 |
| [protocols/](protocols/README.md) | 指向当前正式协议和实验说明。 |

## 数据边界

- 一个 EDF 代表一个状态；窗口不是独立 session。
- 第一阶段只使用 `new_paradigm_v1` 数据。旧 legacy、author、common6、2026-09-14 LAB_FEEDBACK 均不进入默认训练。
- 同一 session 的窗口不得跨 train/validation/final holdout。
- final holdout 必须在预测前预先登记并冻结，不得按模型结果事后挑选。
- `session_manifest.csv` 仍是身份、canonical label、路径、角色和哈希的权威来源；控制实验表只通过 `session_id` 补充计划/实际条件与 confound metadata，避免重复维护原始数据事实。
- fatigue、sleepiness、mood、arousal 等主观量属于 confound metadata / auxiliary measures，不是模型标签真值。

完整设计见 [NEW_PARADIGM_V1](../../../docs/current/NEW_PARADIGM_V1.md)、[ENGAGEMENT_CONTROL_ROADMAP](../../../docs/current/ENGAGEMENT_CONTROL_ROADMAP.md) 和 [DATA_PROTOCOL_V2](../../../docs/current/DATA_PROTOCOL_V2.md)。
