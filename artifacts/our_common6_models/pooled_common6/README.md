# 这个目录是什么

只用lyc与zyf历史数据、限制为六个共同通道的通用模型。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

给mixed提供相同输入通道数的对照，避免混淆增加数据与更换通道。

## 输入从哪里来

lyc+zyf历史候选：31个EDF、19组、11224窗口。 没有使用：作者数据、zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

## 谁生成这里的文件

scripts/train_cross_source_models.py --model our-common6（既有生成入口，本轮不训练）。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [config.json](config.json) | 模型使用的数据范围、通道/特征、固定参数等说明。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [pipeline.joblib](pipeline.joblib) | 保存已学好的缩放、降维、分类步骤；加载后可预测，不需要再训练。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [run_manifest.json](run_manifest.json) | 记录当次运行的来源、输出哈希和执行策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_manifest.csv](train_manifest.csv) | 实际用于该模型训练的录制/片段清单，可追溯身份、标签和分组。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_confusion_matrix.csv](validation_confusion_matrix.csv) | 分别统计两类预测正确和互相混淆的数量。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_fold_metrics.csv](validation_fold_metrics.csv) | 逐折列出哪些完整录制被留出以及该折成绩。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_metrics.json](validation_metrics.json) | 历史留出数据上的汇总成绩；不是今天新录制的结果。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_predictions.csv](validation_predictions.csv) | 每个历史验证窗口的真实/预测类别，可复算指标。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；GroupKFold Acc69.83% ±6.98%，Bal69.51% ±7.21%；LOCKED_TEST lyc44.46% /48.29%，zyf36.03% /46.78%。

## 我什么时候需要看这个目录

研究用同通道对照，不作为默认现场展示。

## 不要误解

输入为60维；文件名标签只用于计分，QuickTest不更新训练参数。
