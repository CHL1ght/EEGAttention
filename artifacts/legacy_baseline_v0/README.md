# 这个目录是什么

第一套保存完整处理步骤、供后续实验对照的多人通用模型。

状态：`historical baseline`。保留模型、配置、划分、预测和哈希用于追溯；不是 New Paradigm v1 的当前模型，不得覆盖。

## 它属于项目哪一步

Stage 2：Legacy pooled baseline

前一步：早期自采 EEG 探索。
这一步：怎样得到第一个可以保存、复查并重复预测的正式模型？
后一步：历史验证不错，不代表新的独立录制也能达到同样效果。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

需要一个能重复预测新EDF的正式起点。

## 输入从哪里来

legacy_manifest.csv中候选数据按完整组划分后的训练侧，包含lyc、zyf、zqd；不是把全部候选都拟合进去。 没有使用：历史validation侧、LOCKED_TEST、LAB_FEEDBACK。

## 谁生成这里的文件

scripts/legacy_baseline_v0.py（既有生成入口，本轮不训练）。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [config.json](config.json) | 模型使用的数据范围、通道/特征、固定参数等说明。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [freeze_manifest.json](freeze_manifest.json) | 记录冻结时的文件哈希，用于确认模型没有被改写。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [pipeline.joblib](pipeline.joblib) | 保存已学好的缩放、降维、分类步骤；加载后可预测，不需要再训练。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [run_summary.json](run_summary.json) | 冻结运行的摘要信息。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [split.csv](split.csv) | 43 条候选逻辑记录的 train/validation session-group 分配；同一 EDF/源录制不跨侧。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_group_metrics.csv](validation_group_metrics.csv) | 按 session group 汇总的窗口数、预测分布和准确率。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_metrics.json](validation_metrics.json) | 历史留出数据上的汇总成绩；不是今天新录制的结果。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_predictions.csv](validation_predictions.csv) | 每个历史验证窗口的真实/预测类别，可复算指标。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；历史validation Acc69.99% / Bal69.64%；LOCKED_TEST lyc65.54% /64.28%，zyf46.11% /57.69%。

## 我什么时候需要看这个目录

现场与研究的固定参考。

## 不要误解

输入为240维；文件名标签只用于计分，QuickTest不更新训练参数。
