# 这个目录是什么

这里提供现场填路径看结果的页面，也保留过去实验的交互记录。

## 它属于项目哪一步

Stage 0–1历史Notebook；Stage 8当前QuickTest。

前一步：Common6 通道对齐与 Mixed。
这一步：让现场使用者录完即可比较已训练模型，历史Notebook用于理解早期方案。
后一步：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

完整故事：[实验阶段地图](../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

让现场使用者录完即可比较已训练模型，历史Notebook用于理解早期方案。

## 输入从哪里来

QuickTest读取用户指定EDF和三个代表模型；历史Notebook使用其原数据。

## 谁生成这里的文件

lab_quick_test_legacy_model.ipynb调用scripts/subject_model_utils.py；其余Notebook按各目录说明。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [legacy/](legacy/README.md) | 这里保留早期自采探索笔记，帮助追溯高分来自什么流程，不作为当前正式入口。 | 目录 | 按子目录规则 |
| [tutorial/](tutorial/README.md) | 这里是供逐步学习的中文注释笔记；正式实验不依赖第二套教学实现。 | 目录 | 按子目录规则 |
| [upstream/](upstream/README.md) | 这里保存阅读作者数据和复现原方案的笔记，不负责今天的现场三模型预测。 | 目录 | 按子目录规则 |
| [lab_quick_test_legacy_model.ipynb](lab_quick_test_legacy_model.ipynb) | 现场单文件及前后比较页面；只填写路径、调用共享helper和显示。 | 代码手写/输出生成 | 可维护，保留来源与实验边界 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

QuickTest可用；旧Notebook为historical。

## 我什么时候需要看这个目录

今天第一段录完运行单文件模式，第二段录完运行Before/After模式。

## 不要误解

QuickTest全文件计分不同于正式清单区间；它不会训练或覆盖模型。
