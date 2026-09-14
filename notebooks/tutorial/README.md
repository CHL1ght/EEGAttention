# 这个目录是什么

这里是供逐步学习的中文注释笔记；正式实验不依赖第二套教学实现。

## 它属于项目哪一步

Stage 0：原作者方案与数据

前一步：从论文和上游材料开始。
这一步：最初复现的是什么，原方案能否运行？
后一步：能跑作者数据后，需要检查自己的设备和任务录制。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

最初复现的是什么，原方案能否运行？

## 输入从哪里来

data/reference/original_mat/ 的 34 个 MATLAB（MAT，保存数组的文件）与 notebooks/upstream/ 的原作者代码。

## 谁生成这里的文件

notebooks/upstream/；scripts/legacy/ 用于本仓库后续运行的历史复现。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [EEG_train_12_result_visualization_20250104_annotated_CN.ipynb](EEG_train_12_result_visualization_20250104_annotated_CN.ipynb) | 上游结果可视化的中文注释版。 | 代码手写/输出生成 | 可维护，保留来源与实验边界 |
| [EEG_train_22_20250226_annotated_CN.ipynb](EEG_train_22_20250226_annotated_CN.ipynb) | 上游训练 notebook 的中文注释版。 | 代码手写/输出生成 | 可维护，保留来源与实验边界 |
| [EEGAttention_notebook_reading_notes_CN.md](EEGAttention_notebook_reading_notes_CN.md) | 阅读上游 notebook 时的中文笔记和变量说明。 | 手写维护 | 可维护，保留来源与实验边界 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

historical：用于理解早期方案。

## 我什么时候需要看这个目录

需要回答“最初复现的是什么，原方案能否运行？”时查看本目录文件。

## 不要误解

确认方案与数据来源。历史随机窗口分数不能当作新录制泛化成绩。
