# 这个目录是什么

只使用原作者23个MAT录制、保留七通道的模型。

## 它属于项目哪一步

Stage 6：作者数据内部可分性。

前一步：Personal diagnosis。
这一步：确认作者数据在按完整录制隔离后仍能分类。
后一步：作者与自采通道不同，必须先选可可靠对应的共同通道。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

检查作者数据在完整录制隔离后是否仍能区分两类。

## 输入从哪里来

作者recordings 3–7、10–14、17–21、24–27、31–34；共13754窗口。 没有使用：任何自采训练数据、LOCKED_TEST、LAB_FEEDBACK；未选中的11个MAT。

## 谁生成这里的文件

scripts/train_cross_source_models.py --model author-only（既有生成入口，本轮不训练）。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [config.json](config.json) | 模型使用的数据范围、通道/特征、固定参数等说明。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [mat_inspection.csv](mat_inspection.csv) | 23 个 `.mat` 的 `o.data` shape、采样率、`nS`、时长、字段切片和通道顺序检查。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [pipeline.joblib](pipeline.joblib) | 保存已学好的缩放、降维、分类步骤；加载后可预测，不需要再训练。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [run_manifest.json](run_manifest.json) | 记录当次运行的来源、输出哈希和执行策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_manifest.csv](train_manifest.csv) | 实际用于该模型训练的录制/片段清单，可追溯身份、标签和分组。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_fold_metrics.csv](validation_fold_metrics.csv) | 逐折列出哪些完整录制被留出以及该折成绩。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_metrics.json](validation_metrics.json) | 历史留出数据上的汇总成绩；不是今天新录制的结果。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [validation_predictions.csv](validation_predictions.csv) | 每个历史验证窗口的真实/预测类别，可复算指标。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；5-fold GroupKFold Acc/Bal均64.12% ±4.37%；未进行正式七通道跨EDF比较。

## 我什么时候需要看这个目录

保留作者数据内部基线；不作默认现场模型。

## 不要误解

输入为70维；文件名标签只用于计分，QuickTest不更新训练参数。
