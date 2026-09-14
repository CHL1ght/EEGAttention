# `pooled_common7/`

本目录记录 `our-common7 pooled model` 的训练门禁结果。

| 文件 | 含义 |
|---|---|
| `channel_alignment.csv` | 我们历史 EDF 的 common7 明确映射检查。 |
| `BLOCKED.json` | 阻塞状态、缺失通道、所需通道和未使用 LOCKED_TEST fit 的机器可读记录。 |
| `BLOCKED.md` | 人类可读的阻塞原因。 |
| `README.md` | 本目录说明。 |

当前缺少 `P7/P8/AF4`，未创建 `pipeline.joblib`，未读取 LOCKED_TEST 做训练统计，也未使用 `T5/T6` 猜测替代。
