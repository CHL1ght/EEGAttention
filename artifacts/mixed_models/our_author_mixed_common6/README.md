# 这个目录是什么

把我们的lyc/zyf历史数据与原作者23个录制合起来，只使用双方能可靠对应的六个通道训练的通用SVC模型。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

测试增加跨来源、跨录制的训练数据多样性，是否与新session泛化改善相关。

## 输入从哪里来

lyc历史候选 + zyf历史候选 + author23个MAT recording；共42组、24978窗口。 没有使用：zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

## 谁生成这里的文件

scripts/train_cross_source_models.py --model mixed-common6（既有生成入口，本轮不训练）。

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

已完成；GroupKFold Acc67.19% ±3.27%，Bal67.31% ±3.26%；LOCKED_TEST lyc47.48% /52.68%，zyf51.03% /55.77%。相对our-common6 Bal增加4.39/8.99个百分点。

## 我什么时候需要看这个目录

研究跨录制/跨来源泛化；现场QuickTest的第三个代表模型。

## 不要误解

mixed不是个人模型、校准模型、微调模型；Our reference=Pz、author reference未知，跨来源解释为exploratory。
