# `data/locked/`

这是受保护的正式测试/采集目录。`session_manifest.csv` 是唯一标签和活动区间入口；raw EDF/CSV/DSI 不得覆盖或就地编辑。

| 子目录 | 文件代表什么 | 当前用途 |
|---|---|---|
| `2026-09-07/` | lyc/zyf 正式 LOCKED_TEST 与 lyc rest reference 的 EDF 及 sidecar。 | 只做 transform/predict/最终指标。 |
| `2026-09-14/` | 下一轮现场采集计划文件。 | 计划，不是模型输入。 |

使用前运行 `python scripts/validate_locked_data.py`。任何训练脚本都不应读取本目录。
