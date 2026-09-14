# `subject_models/`：subject-dependent personal models

本目录保存本阶段的两个个人模型。训练入口是 `scripts/train_subject_models.py`，输入只来自 `data/legacy_manifest.csv` 中各 subject 的历史 `legacy_baseline_candidate`；`zqd` 不进入训练，`data/locked/` 不被训练入口读取。

| 文件/目录 | 含义 |
|---|---|
| `lyc/` | lyc personal model、配置和训练清单。 |
| `zyf/` | zyf personal model、配置和训练清单。 |
| `excluded_candidate_rows.csv` | 被本阶段排除的 candidate 逻辑记录；当前为 zqd 的 6 条记录。 |
| `training_summary.json` | 两个模型的 EDF/session/window 数量、模型哈希、排除统计和 `locked_test_read=false`。 |
| `README.md` | 本目录的训练范围和文件说明。 |

个人模型与旧 pooled 模型使用同一套 EDF、预处理、240 维 Welch 特征和 sklearn pipeline 实现；没有 calibration、微调或 domain adaptation。
