# `author_only/`

这是本阶段唯一完成训练的跨来源模型：只使用 `data/reference/original_mat/` 中 23 个有效 recording。每个 recording 的前 10 分钟作为 focus、后 10 分钟作为 unfocus；完整 recording 是最小 GroupKFold 隔离单位。

| 文件 | 含义 |
|---|---|
| `pipeline.joblib` | 最终 author-only 已 fit 的共享 `StandardScaler → PCA → RBF SVC` pipeline；共 70 个原始 Welch 特征。 |
| `config.json` | 数据范围、MAT 结构、共同通道、特征协议、PCA/SVC 参数、验证摘要和 fit policy。 |
| `train_manifest.csv` | 46 条 author label block 记录：23 个 recording × focus/unfocus 两个 block。 |
| `mat_inspection.csv` | 23 个 `.mat` 的 `o.data` shape、采样率、`nS`、时长、字段切片和通道顺序检查。 |
| `validation_fold_metrics.csv` | 5 个 recording-level GroupKFold 的 train/held-out recording 数、窗口数、accuracy 和 balanced accuracy。 |
| `validation_predictions.csv` | 每个 held-out author 窗口的 fold、真实标签和预测标签。 |
| `validation_metrics.json` | GroupKFold accuracy/balanced accuracy 均值、标准差和有效 fold 数。 |
| `run_manifest.json` | 输入/输出哈希、训练边界、Git HEAD 和 LOCKED_TEST 未参与 fit 的证明。 |
| `REPORT.md` | author 数据结构、原 notebook window-level leakage 审计和模型验证结果。 |
| `README.md` | 本模型目录说明。 |

当前 EDF 缺少明确映射的 `P7/P8/AF4`，所以该 pipeline 暂不对 our LOCKED_TEST 做 transform/predict；不能用 `T5/T6` 空间替代。
