# 这个目录是什么

这里检查个人模型为何历史验证尚可、换录制却退化，保存按录制留出的诊断和预测偏置统计。

## 它属于项目哪一步

Stage 5：Personal diagnosis

前一步：lyc / zyf personal models。
这一步：个人模型为什么在历史留出录制约75%，新录制却接近50%？
后一步：增加不同录制来源可能有帮助，因此检查作者数据是否可分并能否共同训练。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

个人模型为什么在历史留出录制约75%，新录制却接近50%？

## 输入从哪里来

原历史候选与已保存的 personal/LOCKED_TEST 预测文件。

## 谁生成这里的文件

scripts/diagnose_subject_models.py（历史诊断会训练各折，本轮不执行）；测试侧只统计已有预测。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [class_distribution.csv](class_distribution.csv) | lyc/zyf historical training 与 LOCKED_TEST 的按真实类别 session、EDF、window 数和比例。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [common7_channel_alignment.csv](common7_channel_alignment.csv) | 正式 locked EDF 的实际通道名、明确映射结果和缺失 common7 通道。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [diagnostic_summary.json](diagnostic_summary.json) | 诊断结论、偏置证据、session shift 判断和 fit policy。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [historical_heldout_folds.csv](historical_heldout_folds.csv) | 每个 subject 的 Leave-One-Session-Group-Out fold 结果；Scaler/PCA/SVC 只在该 fold train group fit。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [historical_heldout_summary.csv](historical_heldout_summary.csv) | lyc/zyf fold accuracy、balanced accuracy 均值、标准差和有效 balanced fold 数。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [pca_diagnostics.csv](pca_diagnostics.csv) | pooled、lyc personal、zyf personal 的原始 feature dimension、PCA 维度和累计解释方差。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [prediction_bias.csv](prediction_bias.csv) | pooled、lyc personal、zyf personal 在 lyc/zyf LOCKED_TEST 上的真实/预测类别数量、比例、accuracy 和 balanced accuracy。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [run_manifest.json](run_manifest.json) | 记录当次运行的来源、输出哈希和执行策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [session_diagnostics.csv](session_diagnostics.csv) | 每个 model × subject × EDF/session 的真实标签、窗口数、预测类别数/比例、accuracy、balanced accuracy（单类 session 为 N/A）和 majority prediction。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“个人模型为什么在历史留出录制约75%，新录制却接近50%？”时查看本目录文件。

## 不要误解

lyc personal→zyf 把98.57%的窗口预测为 focus，说明较高 Accuracy 主要来自类别偏向。历史按组留一的 Balanced Accuracy 约75%只汇总含两类的有效折；不是所有折都可计算。结果支持 session/domain shift（新录制条件/数据分布变化）的嫌疑，尚不能证明单一原因。
