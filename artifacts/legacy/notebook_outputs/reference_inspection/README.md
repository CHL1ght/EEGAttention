# 这个目录是什么

这里是帮助人查看作者 MAT 数组结构的表格预览，不是新的信号数据集。

## 它属于项目哪一步

Stage 0：理解原作者数据结构。

前一步：从已有实验或上游材料形成这个阶段的输入。
这一步：这里是帮助人查看作者 MAT 数组结构的表格预览，不是新的信号数据集。
后一步：按阶段地图查看其后续用途，历史材料不覆盖新结果。

完整故事：[实验阶段地图](../../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

最初复现的是什么，原方案能否运行？

## 输入从哪里来

data/reference/original_mat/ 的 34 个 MATLAB（MAT，保存数组的文件）与 notebooks/upstream/ 的原作者代码。

## 谁生成这里的文件

notebooks/upstream/；scripts/legacy/ 用于本仓库后续运行的历史复现。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [eeg_data_preview_5000.xlsx](eeg_data_preview_5000.xlsx) | 原始 MAT EEG 数值前 5,000 个样本的抽样导出。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [mat_structure_preview.xlsx](mat_structure_preview.xlsx) | 对 `data/reference/original_mat/*.mat` 结构的抽样预览。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

historical：用于理解早期方案。

## 我什么时候需要看这个目录

需要回答“最初复现的是什么，原方案能否运行？”时查看本目录文件。

## 不要误解

预览表不替代原始 MAT，也不能当作当前240维或60维特征缓存。
