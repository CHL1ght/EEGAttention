# zyf personal model

| 文件 | 含义 |
|---|---|
| `pipeline.joblib` | 只用 zyf historical candidate 训练得到的已 fit `StandardScaler → PCA → RBF SVC`。 |
| `config.json` | zyf 的训练 EDF/session 范围、类别窗口计数、特征和模型参数、训练 commit。 |
| `train_manifest.csv` | zyf 进入训练的 15 条逻辑记录；12 个唯一 EDF、7 个 session group，全部标记 `train`。 |
| `README.md` | 本模型目录说明。 |

该模型不包含任何 `data/locked/` 文件。测试时由 `evaluate_subject_models.py` 只对 locked session 调用 `predict`。
