# 这个目录是什么

这里保存只学我们历史数据、但只看六个共同通道的模型。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

把通道数与mixed保持一致，作为检验加入作者数据效果的对照。

## 输入从哪里来

lyc/zyf的31个EDF、19个session group；不含作者、zqd、未知身份或LOCKED_TEST。

## 谁生成这里的文件

scripts/train_cross_source_models.py --model our-common6。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [pooled_common6/](pooled_common6/README.md) | 只用lyc与zyf历史数据、限制为六个共同通道的通用模型。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

已完成；60维特征模型。

## 我什么时候需要看这个目录

想检验混合数据是否有帮助时，先找到这个同通道对照。

## 不要误解

它是多人通用模型，不是lyc或zyf personal；它与旧24通道pooled也不是同一模型。
