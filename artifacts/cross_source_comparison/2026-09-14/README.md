# Common6 cross-source comparison｜2026-09-14

本目录是本轮 common6 的最终比较产物。它读取上一阶段已冻结的 pooled/personal LOCKED_TEST 结果，并对新建的 `author-common6`、`our-common6`、`mixed-common6` pipeline 做 prediction-only 评估。

| 文件 | 含义 |
|---|---|
| `unified_model_comparison.csv` | 6 个模型 × 2 个测试 subject 的 Accuracy、Balanced Accuracy、窗口数、预测类别数量/比例、混淆矩阵和 GroupKFold held-out 指标。 |
| `locked_predictions.csv` | 旧 pooled/personal 与本轮 common6 模型的逐窗口预测。 |
| `locked_session_metrics.csv` | 逐 session accuracy、窗口数、预测类别数量/比例；单标签 session 的 balanced accuracy 留空是定义上的限制。 |
| `locked_confusion_matrix.csv` | 本轮 common6 模型按 subject 展开的混淆矩阵长表。 |
| `common6_channel_alignment.csv` | 6 个 formal LOCKED_TEST EDF 的通道匹配结果；确认 T5/T6 adapter 可用。 |
| `comparison_summary.json` | 需要的通道、reference 状态、fit policy、训练/评估模型哈希及 author-only-7ch 对照指标。 |
| `REPORT.md` | 人类可读的统一表、author 7ch→common6 内部 ablation、reference uncertainty 和结论边界。 |
| `README.md` | 本比较日期目录的文件字典。 |

Cross-source 结果统一标记为 `exploratory / channel-aligned but author MAT reference compatibility uncertain`。LOCKED_TEST 的 `fit_calls=0`；没有 calibration、微调、domain adaptation 或超参数搜索。
