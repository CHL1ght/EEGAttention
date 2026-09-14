# `data/reference/`

这里保存上游论文/原始项目的参考数据。它们用于复现上游 notebook，不进入当前 legacy pooled 或 lyc/zyf personal model 的训练。

| 子目录 | 内容 |
|---|---|
| `original_mat/` | 34 个 `eeg_recordN.mat` MATLAB EEG recording 文件。 |

MAT 文件保持原始格式和名称；需要查看结构时使用 `notebooks/upstream/inspect_original_mat.ipynb`，相关抽样 Excel 在 `artifacts/legacy/notebook_outputs/reference_inspection/`。
