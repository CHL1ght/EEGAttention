# 脚本入口

正式可用的只读验收：

- `validate_locked_data.py`：核验锁定 EEG 的清单、标签、时长、采样率、配套文件和哈希。
- `validate_legacy_manifest.py`：核验 `legacy_dataset_v0` 清单，以及 39 个 EDF 的身份、采集时间、文件修改时间、混合片段边界、路径、标签映射、分组、文件头和 SHA-256。
- `validate_reproduction_models.py`：核验我们运行修改后上游流程所产生的 10 个历史深度模型权重；只检查完整性，不表示当前研究使用它们。
- `train_subject_models.py`：从 `data/legacy_manifest.csv` 的历史 `legacy_baseline_candidate` 中，仅按 subject 分别训练 `lyc` / `zyf` personal model；`zqd` 和 LOCKED_TEST 均拒绝进入训练。
- `evaluate_subject_models.py`：在同一批正式 `LOCKED_TEST` session 上，以 prediction-only 方式比较旧 pooled frozen model、lyc personal model 和 zyf personal model，并输出 subject × model 交叉表。

`legacy/` 中是旧深度学习训练和 ROC 绘图辅助脚本，仅供复现实验，不是新正式训练入口。

本阶段产物位于 `artifacts/subject_models/` 和 `artifacts/subject_model_comparison/2026-09-07/`。两个人模型复用 `legacy_baseline_v0.py` 与 `eeg_pipeline_utils.py` 的 EDF、预处理、窗口、Welch 特征和 Scaler/PCA/SVC 实现；没有 calibration、微调或新算法。
