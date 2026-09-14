# 这个目录是什么

这里是三个核心脚本的中文教学注释副本，只用于阅读，不是第二套正式算法。

## 它属于项目哪一步

Stage 2–3：理解基线如何训练、冻结后如何只预测。

前一步：从已有实验或上游材料形成这个阶段的输入。
这一步：这里是三个核心脚本的中文教学注释副本，只用于阅读，不是第二套正式算法。
后一步：按阶段地图查看其后续用途，历史材料不覆盖新结果。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

怎样得到第一个可以保存、复查并重复预测的正式模型？

## 输入从哪里来

scripts/eeg_pipeline_utils.py、scripts/legacy_baseline_v0.py、scripts/evaluate_locked_test.py 的代码及其业务流程，不直接读取信号做实验。

## 谁生成这里的文件

人工补充中文教学注释；不是正式脚本运行生成。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [eeg_pipeline_utils_annotated.py](eeg_pipeline_utils_annotated.py) | 讲解EDF读取、预处理、窗口和Welch频带特征；对应正式 eeg_pipeline_utils.py。 | 手写教学注释 | 仅维护注释，不作为实验入口 |
| [evaluate_locked_test_annotated.py](evaluate_locked_test_annotated.py) | 讲解冻结模型只预测及窗口/session/受试者汇总；对应正式 evaluate_locked_test.py。 | 手写教学注释 | 仅维护注释，不作为实验入口 |
| [legacy_baseline_v0_annotated.py](legacy_baseline_v0_annotated.py) | 讲解清单筛选、session划分、训练与冻结；对应正式 legacy_baseline_v0.py。 | 手写教学注释 | 仅维护注释，不作为实验入口 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

教学参考 / 不运行、不生成产物。

## 我什么时候需要看这个目录

需要回答“怎样得到第一个可以保存、复查并重复预测的正式模型？”时查看本目录文件。

## 不要误解

不要运行这些注释副本，不新建 __init__.py，不生成或覆盖模型/结果。正式实现有变化时需人工同步教学说明；personal直接复用共享库，没有复制实现。
