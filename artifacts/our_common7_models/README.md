# 这个目录是什么

这里保留要求七个共同通道时未能训练的尝试。

## 它属于项目哪一步

Stage 7：common6出现前的历史通道门禁。

前一步：Author-only model。
这一步：记录为何旧七通道路径没有模型。
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

记录为何旧七通道路径没有模型。

## 输入从哪里来

历史EDF通道头；旧adapter不使用T5/T6别名且要求AF4。

## 谁生成这里的文件

scripts/train_cross_source_models.py --model our-common7。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [pooled_common7/](pooled_common7/README.md) | 这里记录我们自己的共同七通道方案为何被阻止训练；没有 pipeline.joblib 可用于预测。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

blocked / historical；无模型。

## 我什么时候需要看这个目录

阅读common6如何由旧尝试发展而来时查看。

## 不要误解

P7/P8命名现已获证实；旧门禁记录不代表当前common6仍阻塞。
