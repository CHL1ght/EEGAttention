# 上游流程的本地复现产物

本目录中的文件不是原作者直接提供的成果。它们是在本项目中修改、运行上游 Notebook 及辅助脚本后产生的历史产物，输入数据为原作者的 `data/reference/original_mat/`。

## 目录内容

| 目录 | 内容 | 来源判定 |
|---|---|---|
| `preprocessed_arrays/` | `X_train/X_test/y_train/y_test.npy` | 由修改后的 `EEG_train_22_20250226.ipynb` 导出 |
| `feature_cache/` | 完整特征及 ANOVA/FI/LCC/PCA 缓存 | 由同一 Notebook 为深度训练生成 |
| `models/` | 5 个 GoogLeNet 和 5 个 ResNet18 权重 | 由本项目后加的深度训练辅助流程生成/保存 |
| `results/` | 本地复现的训练表、ROC 数据、图和进度日志 | 与上述复现流程同批生成 |

Git 追溯证据：上述数组、缓存和权重在提交 `68a25c0` (`better train process`) 中加入；四个 `.npy` 的导出语句也位于该版本的 Notebook 中。

## 重要限制

- `.npy` 是随机窗口划分后的历史缓存，且 `X_train/X_test` 已经缩放。
- 当时的 `StandardScaler` 对象没有保存，因此无法对新数据做严格一致的 `transform`。
- 仓库没有保存传统 DT/RF/KNN/LR/SVC 模型对象，也没有保存完整的 Scaler→PCA→SVC Pipeline。
- GoogLeNet/ResNet18 文件不是当前研究的正式模型，不用于 LOCKED_TEST。

## 与新 baseline 的关系

这些文件只作历史复现证据。新的 `legacy_baseline_v0` 需要由规范主 Notebook 从明确的 Legacy 训练数据重新生成，并把数据范围、预处理、特征、Scaler、PCA 和 SVC 一起冻结。
