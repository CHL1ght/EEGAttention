# Author-only model

本模型只使用 `data/reference/original_mat/` 中由上游 notebook 选择的 23 个 author recording。每个 recording 的 `[0, 600)` 秒为 focus、`[600, 1200)` 秒为 unfocus；recording 是最小隔离单位。

- common channels: `F7, F3, P7, O1, O2, P8, AF4`
- recordings: 23；blocks: 46；windows: 13754
- raw feature dimension: 70；PCA: 23 components
- GroupKFold accuracy: 64.12% ± 4.37%
- GroupKFold balanced accuracy: 64.12% ± 4.37% (5 valid folds)
- LOCKED_TEST 未参与任何 fit；该模型的跨 EDF 测试必须等 7 个共同通道完成明确对齐后再进行。

## MAT structure and original notebook audit

- 23 个 selected `.mat` 都是顶层 `o` struct，信号在 `o.data`；采样率为 128 Hz，原 notebook 使用 `o.data[:20*128*60, 3:17]` 的 14 列 EEG，并按明确通道名选择 common 7。逐文件结构见 `mat_inspection.csv`。
- 原作者标签构造为每个 recording 前 10 分钟 focus、后 10 分钟 unfocus；当前模型把整个 recording 作为一个 session group。
- 原 notebook 的 `train_test_split(X, y, test_size=0.2, random_state=42)` 是在所有 recording 的窗口拼接之后进行的，因此同一 recording 的窗口可能同时进入 train/test，存在 window-level leakage。
- 原 notebook 的 StandardScaler/PCA/SVC 是对该随机窗口 split 的 train 侧 fit；本模型改用 recording-level GroupKFold，避免同 recording 跨集合。

## Fold metrics

| fold | held-out recordings | accuracy | balanced accuracy |
|---:|---:|---:|---:|
| 1 | 5 | 69.93% | 69.93% |
| 2 | 5 | 60.47% | 60.47% |
| 3 | 5 | 65.42% | 65.42% |
| 4 | 4 | 59.11% | 59.11% |
| 5 | 4 | 65.68% | 65.68% |
