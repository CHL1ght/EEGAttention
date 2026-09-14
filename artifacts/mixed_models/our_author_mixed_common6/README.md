# `our_author_mixed_common6/`

这是 `mixed-common6` pipeline：训练数据为 author historical recordings 加上明确身份的 lyc/zyf historical candidate。`zqd`、unknown identity、LOCKED_TEST 和 locked reference 均不进入 fit。

| 文件 | 含义 |
|---|---|
| `pipeline.joblib` | mixed historical 数据上 fit 的共享 StandardScaler/PCA/RBF SVC pipeline。 |
| `train_manifest.csv` | author 与 our 两个 source 的实际训练片段；保留 `source`、`subject_id`、`session_group_id`、label。 |
| `validation_fold_metrics.csv` | 跨 source 训练数据的 recording-level GroupKFold 每折结果。 |
| `validation_predictions.csv` | validation 窗口预测及来源/session 信息。 |
| `validation_confusion_matrix.csv` | validation 总混淆矩阵。 |
| `validation_metrics.json` | GroupKFold 汇总 accuracy / balanced accuracy。 |
| `config.json` | source 范围、common6 映射、特征/PCA/SVC 配置、reference compatibility uncertainty。 |
| `run_manifest.json` | 输出 SHA-256、Git HEAD 和 LOCKED_TEST fit policy。 |
| `README.md` | 本目录的输入、输出和禁止用途说明。 |

LOCKED_TEST 只在 `scripts/evaluate_cross_source_models.py --channel-set common6` 中进行 transform/predict/metric。加入 author 数据后的泛化变化只能表述为当前实际数据表示下与 LOCKED_TEST 泛化相关，不可单独归因于 subject、device 或 task/paradigm。
