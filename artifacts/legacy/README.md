# `artifacts/legacy/`：历史 notebook 产物

这里是早期自采 EEG notebook 的输出区。它们保留用于追溯旧实验和检查数据形状，不是 `legacy_baseline_v0` 的冻结输入，也不用于当前 LOCKED_TEST。

| 子目录 | 内容 |
|---|---|
| `notebook_outputs/` | 旧 notebook 生成的对比表、缓存、抽样 Excel 和数据检查表；继续按实验主题分目录保存。 |

不要把这里的随机窗口结果当作跨 session/跨 subject 泛化结果。需要生成正式结果时使用 `scripts/legacy_baseline_v0.py` 或 `scripts/evaluate_subject_models.py`。
