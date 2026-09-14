# `scripts/legacy/`

这里是上游深度学习/ROC 的历史辅助脚本，不是当前正式 sklearn pipeline 入口。

| 文件 | 含义 |
|---|---|
| `eeg_deep_worker.py` | 单个上游深度模型/特征变体的 worker。 |
| `run_deep_workers.py` | 批量调度上游深度 worker。 |
| `save_roc_figures.py` | 读取上游 ROC 缓存并保存图片。 |

它们产生或使用 `artifacts/reproductions/upstream_pipeline/` 的历史产物，不参与 lyc/zyf personal model 和 LOCKED_TEST。
