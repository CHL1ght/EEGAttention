# `pooled_common6/`

这是 `our-common6` 模型的独立产物目录。它只使用 `lyc`/`zyf` 的历史训练候选，不使用 `zqd`、未知身份数据或任何 LOCKED_TEST 信号值，也不覆盖既有 pooled frozen model。

| 文件 | 含义 |
|---|---|
| `pipeline.joblib` | 已 fit 的共享 `StandardScaler → PCA → RBF SVC` pipeline；输入为 60 维 common6 Welch 特征。 |
| `train_manifest.csv` | 实际进入训练的 historical 逻辑片段；`session_group_id` 是 recording-level 隔离键。 |
| `validation_fold_metrics.csv` | 5-fold recording-level GroupKFold 的每折 accuracy、balanced accuracy、窗口数和 held-out groups。 |
| `validation_predictions.csv` | 每个 validation window 的真实/预测标签及 recording/session 信息。 |
| `validation_confusion_matrix.csv` | validation 总混淆矩阵，标签顺序为 `unfocus, focus`。 |
| `validation_metrics.json` | GroupKFold 汇总指标。 |
| `config.json` | 通道顺序、T5/T6 adapter、预处理/特征/PCA/SVC 参数、训练范围和 reference uncertainty。 |
| `run_manifest.json` | 输出文件 SHA-256、训练时间、Git HEAD 和 `locked_test_read_for_fit=false` 声明。 |
| `README.md` | 本模型目录的文件字典和使用边界。 |

LOCKED_TEST 评估不在这里写入；请使用 `scripts/evaluate_cross_source_models.py --channel-set common6`，它只调用 `predict` 并将结果写入 `artifacts/cross_source_comparison/2026-09-14/`。
