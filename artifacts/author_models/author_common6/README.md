# `author_common6/`

这是只使用上游作者 MATLAB 数据的 `author-common6` 模型。训练范围沿用 checked-in author notebook 选出的 23 个 recording：`3–7, 10–14, 17–21, 24–27, 31–34`；每个 recording 的前 600 秒标为 `focus`，后 600 秒标为 `unfocus`。

common6 直接保留作者 MAT 中的 `F7,F3,P7,O1,O2,P8`，主动舍弃 `AF4`。它与 DSI-24 的通道名通过 `scripts/cross_source_utils.py` 的 `T5-Pz→P7`、`T6-Pz→P8` adapter 对齐；author MAT reference 仍为 unknown，因此跨来源结果仅为 exploratory。

| 文件 | 含义 |
|---|---|
| `pipeline.joblib` | 用作者 common6 特征 fit 的 `StandardScaler → PCA → RBF SVC` pipeline。 |
| `train_manifest.csv` | 46 个 author label blocks（23 recording × focus/unfocus）及其 session group。 |
| `mat_inspection.csv` | 选定 MAT 的字段、数据形状、采样率和 common channel inspection。 |
| `validation_fold_metrics.csv` | recording-level 5-fold GroupKFold 每折结果。 |
| `validation_predictions.csv` | validation window 的真实/预测标签及 recording 信息。 |
| `validation_confusion_matrix.csv` | validation 总混淆矩阵。 |
| `validation_metrics.json` | GroupKFold accuracy / balanced accuracy 均值和标准差。 |
| `config.json` | common6 映射、60 维特征、PCA/SVC 配置、author recording 范围与审计边界。 |
| `run_manifest.json` | 输出哈希与训练策略声明；`locked_test_read=false`。 |
| `REPORT.md` | 人类可读的 author common6 训练和验证报告。 |
| `README.md` | 本目录文件说明。 |

该模型不改变既有 `author_models/author_only/` 的 author-only-7ch 结果；两者可在统一比较报告中进行 AF4 去除前后的内部 ablation 对照。
