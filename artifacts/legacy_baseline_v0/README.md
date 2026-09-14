# `legacy_baseline_v0/`：冻结 pooled baseline

这是旧 pooled 模型的完整冻结包。它使用 `data/legacy_manifest.csv` 中全部 `legacy_baseline_candidate`，按完整 `session_group_id` 做 train/validation 划分；不读取 `data/locked/`。

| 文件 | 含义 |
|---|---|
| `pipeline.joblib` | 已 fit 的 `StandardScaler → PCA(95%) → RBF SVC`，输入 240 维 Welch 特征；推理时只允许 `predict/transform`。 |
| `config.json` | 标签映射、240 维特征顺序、滤波/窗口/Welch 参数、PCA/SVC 参数及 session 划分规则。 |
| `split.csv` | 43 条候选逻辑记录的 train/validation session-group 分配；同一 EDF/源录制不跨侧。 |
| `validation_predictions.csv` | validation 窗口级 true/pred 和窗口/session 元数据。 |
| `validation_group_metrics.csv` | 按 session group 汇总的窗口数、预测分布和准确率。 |
| `validation_metrics.json` | 总体 accuracy、混淆矩阵、classification report 和 group 指标。 |
| `freeze_manifest.json` | pipeline、配置、split、结果文件哈希及冻结 commit，供回归检查。 |
| `run_summary.json` | 冻结运行的摘要信息。 |
| `REPORT.md` | 人类可读的 baseline 方法、数据范围和验证结果。 |

运行 `python scripts/legacy_baseline_v0.py --check-existing` 只检查这些文件，不重训。
