# 这个目录是什么

这是 CURRENT 研究协议与 HISTORICAL 项目故事、模型解释、路径查询的阅读入口。

## 它属于项目哪一步

Stage 0–9：串起历史实验、transition pilot 与当前 New Paradigm v1。

前一步：Common6 通道对齐与 Mixed。
这一步：让第一次接触项目的人先理解问题，再查代码和产物。
后一步：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

完整故事：[实验阶段地图](EXPERIMENT_MAP.md)；名词和模型：[模型字典](MODEL_CATALOG.md)。

## 为什么会有这个目录

让第一次接触项目的人先理解问题，再查代码和产物。

## 输入从哪里来

已保存的manifest、模型配置、REPORT与项目进度记录。

## 谁生成这里的文件

人工维护；README和解释文档不作为模型输入。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [current/](current/README.md) | **CURRENT**：New Paradigm v1 计划与 Data Protocol v2。 | 目录 | 随当前协议版本维护 |
| [assets/](assets/README.md) | 这里保存帮助理解原作者方案的示意图，不保存模型或预测结果。 | 目录 | 按子目录规则 |
| [methodology/](methodology/README.md) | 这里解释正式基线与测试的数据划分方法，帮助读者理解为什么必须隔离录制。 | 目录 | 按子目录规则 |
| [progress/](progress/README.md) | 这里按日期保留项目推进简报，让读者看到当时做了什么决定。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPOSITORY_FILE_GUIDE.md](REPOSITORY_FILE_GUIDE.md) | 按路径查询文件用途；不承担项目故事。 | 手写维护 | 可维护，保留来源与实验边界 |
| [MODEL_CATALOG.md](MODEL_CATALOG.md) | 逐个解释七种已保存模型的训练数据、特征、用途和既有分数。 | 手写维护 | 可维护，保留来源与实验边界 |
| [EXPERIMENT_MAP.md](EXPERIMENT_MAP.md) | 按实验发展顺序解释问题、数据、脚本、产物、结论和下一步。 | 手写维护 | 可维护，保留来源与实验边界 |
| [LAB_FEEDBACK_HANDOFF.md](LAB_FEEDBACK_HANDOFF.md) | HISTORICAL：旧 QuickTest/LAB_FEEDBACK 交付、执行时哈希与完整修改清单。 | 手写维护 | 历史交付记录，后续变更另留痕 |

## 当前状态

CURRENT 文档已建立；历史地图、模型说明和每日简报继续保留。

## 我什么时候需要看这个目录

要执行新采集先看 current/；不知道旧模型是什么看 MODEL_CATALOG；不知道为什么转向看 EXPERIMENT_MAP。

## 不要误解

文档中的训练命令用于追溯，不要求读者重新训练。
