# 上游 MATLAB 参考录制

本目录包含 `eeg_record1.mat` 至 `eeg_record34.mat`，共 34 个原始 MATLAB recording 文件。每个文件代表上游数据集中的一个记录，具体变量结构由文件自身和上游 notebook 决定；本仓库不把它们改写为新的 EDF。

| 文件范围 | 用途 |
|---|---|
| `eeg_record1.mat`–`eeg_record34.mat` | 上游结构检查、特征缓存和 GoogLeNet/ResNet18 历史复现的共同输入。 |

这些 `.mat` 不用于当前 subject-dependent 训练或 2026-09-07 LOCKED_TEST。原始文件只读；结构预览见 `artifacts/legacy/notebook_outputs/reference_inspection/`。
