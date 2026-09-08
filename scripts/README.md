# 脚本入口

正式可用的只读验收：

- `validate_locked_data.py`：核验锁定 EEG 的清单、标签、时长、采样率、配套文件和哈希。
- `validate_legacy_manifest.py`：核验 `legacy_dataset_v0` 清单，以及 39 个 EDF 的身份、采集时间、文件修改时间、混合片段边界、路径、标签映射、分组、文件头和 SHA-256。
- `validate_reproduction_models.py`：核验我们运行修改后上游流程所产生的 10 个历史深度模型权重；只检查完整性，不表示当前研究使用它们。

`legacy/` 中是旧深度学习训练和 ROC 绘图辅助脚本，仅供复现实验，不是新正式训练入口。
