# 这个目录是什么

这里保存把作者与自采历史数据合并训练的尝试。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

检验更多来源、更多录制的训练数据是否与新session表现改善相关。

## 输入从哪里来

作者23个MAT与lyc/zyf历史候选，按完整录制组隔离。

## 谁生成这里的文件

scripts/train_cross_source_models.py；common6已完成，common7尝试保留。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [our_author_mixed/](our_author_mixed/README.md) | 这里记录共同七通道 mixed 方案为什么没有生成模型；不是可加载的模型目录。 | 目录 | 按子目录规则 |
| [our_author_mixed_common6/](our_author_mixed_common6/README.md) | 把我们的lyc/zyf历史数据与原作者23个录制合起来，只使用双方能可靠对应的六个通道训练的通用SVC模型。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

our_author_mixed_common6已完成；our_author_mixed是历史blocked记录。

## 我什么时候需要看这个目录

今天QuickTest的第三个模型来自our_author_mixed_common6/。

## 不要误解

mixed不是personal、校准或作者模型微调；两种来源直接合并训练，author参考电极未知。
