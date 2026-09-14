# 这个目录是什么

只用lyc历史数据训练的个人模型。

## 它属于项目哪一步

Stage 4：lyc / zyf personal models

前一步：独立 LOCKED_TEST。
这一步：只用同一个人的历史数据训练，会不会更适合这个人？
后一步：不能只看一个准确率，需要检查预测偏向、类别比例和不同录制。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

检验消除跨人差异是否能改善新录制预测。

## 输入从哪里来

lyc：19个EDF、12个session group，6741个窗口。 没有使用：zyf、zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

## 谁生成这里的文件

scripts/train_subject_models.py（既有生成入口，本轮不训练）。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [config.json](config.json) | 模型使用的数据范围、通道/特征、固定参数等说明。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [pipeline.joblib](pipeline.joblib) | 保存已学好的缩放、降维、分类步骤；加载后可预测，不需要再训练。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [train_manifest.csv](train_manifest.csv) | 实际用于该模型训练的录制/片段清单，可追溯身份、标签和分组。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；LOCKED_TEST lyc Acc46.68% / Bal47.67%；zyf67.94% /51.80%，后者预测focus98.57%，存在明显偏向。

## 我什么时候需要看这个目录

lyc现场与旧pooled/mixed对照。

## 不要误解

输入为240维；文件名标签只用于计分，QuickTest不更新训练参数。
