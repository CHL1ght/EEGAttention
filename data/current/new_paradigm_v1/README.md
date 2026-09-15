# New Paradigm v1 数据

状态：`CURRENT`。

这里是今后正式采集的标准化 focus/unfocus 数据入口。当前只建立 schema、目录和协议，不包含任何虚构 session，也不触发训练。

## 目录

| 路径 | 用途 |
|---|---|
| [session_manifest.csv](session_manifest.csv) | New Paradigm v1 唯一 session 清单；当前只有表头。 |
| [raw/](raw/README.md) | 设备导出的原始 EDF/CSV/DSI；按 subject 归档。 |
| [notes/](notes/README.md) | 与 session 一一对应的现场 notes。 |
| [protocols/](protocols/README.md) | 指向当前正式协议和实验说明。 |

## 数据边界

- 一个 EDF 代表一个状态；窗口不是独立 session。
- 第一阶段只使用 `new_paradigm_v1` 数据。旧 legacy、author、common6、2026-09-14 LAB_FEEDBACK 均不进入默认训练。
- 同一 session 的窗口不得跨 train/validation/final holdout。
- final holdout 必须在预测前预先登记并冻结，不得按模型结果事后挑选。

完整设计见 [NEW_PARADIGM_V1](../../../docs/current/NEW_PARADIGM_V1.md) 和 [DATA_PROTOCOL_V2](../../../docs/current/DATA_PROTOCOL_V2.md)。
