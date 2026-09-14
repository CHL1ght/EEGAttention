# 这个目录是什么

这里保存旧冻结通用模型在6个正式测试 session、2389个窗口上的成绩；rest 不计入二分类。

## 它属于项目哪一步

Stage 3：独立 LOCKED_TEST

前一步：Legacy pooled baseline。
这一步：面对从未参与训练的新录制，旧模型表现如何？
后一步：怀疑不同人的差异影响模型，于是检验个人模型。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

面对从未参与训练的新录制，旧模型表现如何？

## 输入从哪里来

data/locked/2026-09-07/：lyc/zyf 各3段二分类录制，共2389个正式窗口；另1段静息参考。

## 谁生成这里的文件

scripts/validate_locked_data.py；scripts/evaluate_locked_test.py。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [locked_metrics.json](locked_metrics.json) | 总体 accuracy、balanced accuracy、混淆矩阵及计数。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [locked_predictions.csv](locked_predictions.csv) | 正式测试逐窗口预测记录；不同于QuickTest全文件反馈。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [locked_session_metrics.csv](locked_session_metrics.csv) | 每次完整测试录制的预测比例和成绩。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [locked_subject_metrics.csv](locked_subject_metrics.csv) | 将正式 session 按 lyc/zyf 聚合后的 subject 指标。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [reference_predictions.csv](reference_predictions.csv) | rest reference 的预测记录，仅供质量检查。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [reference_session_metrics.csv](reference_session_metrics.csv) | rest reference 的汇总，不参与二分类指标。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [run_manifest.json](run_manifest.json) | 记录当次运行的来源、输出哈希和执行策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [run_summary.json](run_summary.json) | 本次 locked evaluation 的机器可读摘要。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“面对从未参与训练的新录制，旧模型表现如何？”时查看本目录文件。

## 不要误解

LOCKED_TEST（冻结测试数据，只能预测，不能参与任何 fit，即学习参数）首轮总 Accuracy 55.30%、Balanced Accuracy 59.91%，明显低于历史验证。按整个 EDF/session 隔离，防止同一次录制的窗口跨集合。
