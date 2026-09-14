# 这个目录是什么

这里用同一批6个独立测试录制比较旧通用模型、lyc个人模型和zyf个人模型。

## 它属于项目哪一步

Stage 4：lyc / zyf personal models

前一步：独立 LOCKED_TEST。
这一步：只用同一个人的历史数据训练，会不会更适合这个人？
后一步：不能只看一个准确率，需要检查预测偏向、类别比例和不同录制。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

只用同一个人的历史数据训练，会不会更适合这个人？

## 输入从哪里来

lyc 的19个历史EDF/12组、zyf 的12个历史EDF/7组；各自只用自己的历史候选。

## 谁生成这里的文件

scripts/train_subject_models.py 生成已保存模型；scripts/evaluate_subject_models.py 比较三个已训练模型。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [comparison_metrics.json](comparison_metrics.json) | 主表的 JSON 版本、模型哈希、测试 session、reference 排除和 fit policy。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [predictions.csv](predictions.csv) | 三个模型对每个 locked 窗口的逐窗口 prediction；包含 model、test subject、session、true/pred 和窗口时间。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [run_manifest.json](run_manifest.json) | 记录当次运行的来源、输出哈希和执行策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [session_metrics.csv](session_metrics.csv) | model × session 的窗口数量、accuracy、预测类别数量和比例。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [subject_model_comparison.csv](subject_model_comparison.csv) | model × test subject 的交叉评估主表，含 accuracy、balanced accuracy、类别比例和混淆矩阵。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [test_sessions.csv](test_sessions.csv) | 实际参与比较的 6 个 formal locked session 及其标签/活动区间。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“只用同一个人的历史数据训练，会不会更适合这个人？”时查看本目录文件。

## 不要误解

个人模型未稳定优于 pooled：lyc personal→lyc Balanced Accuracy 47.67%，zyf personal→zyf 52.14%。lyc personal→zyf Accuracy 67.94% 看似高，但 Balanced Accuracy 仅51.80%。
