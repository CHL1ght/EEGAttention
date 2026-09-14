# 这个目录是什么

这里把六个已保存模型在同一批独立录制上的成绩并排展示，重点看加入作者数据是否有帮助。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

在相同六通道输入下，加入作者训练数据能否改善新录制表现？

## 输入从哪里来

common6（我们的EDF与作者MAT都能可靠对应的六个EEG通道）：F7,F3,P7,O1,O2,P8。T5/T6依据设备和命名证据对应P7/P8；舍弃AF4。

## 谁生成这里的文件

scripts/verify_common6_compatibility.py；scripts/train_cross_source_models.py 的 author-common6 / our-common6 / mixed-common6；scripts/evaluate_cross_source_models.py --channel-set common6。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [common6_channel_alignment.csv](common6_channel_alignment.csv) | 6 个 formal LOCKED_TEST EDF 的通道匹配结果；确认 T5/T6 adapter 可用。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [comparison_summary.json](comparison_summary.json) | 比较使用的模型哈希、通道协议和测试策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [locked_confusion_matrix.csv](locked_confusion_matrix.csv) | 本轮 common6 模型按 subject 展开的混淆矩阵长表。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [locked_predictions.csv](locked_predictions.csv) | 正式测试逐窗口预测记录；不同于QuickTest全文件反馈。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [locked_session_metrics.csv](locked_session_metrics.csv) | 每次完整测试录制的预测比例和成绩。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [unified_model_comparison.csv](unified_model_comparison.csv) | 6 个模型 × 2 个测试 subject 的 Accuracy、Balanced Accuracy、窗口数、预测类别数量/比例、混淆矩阵和 GroupKFold held-out 指标。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“在相同六通道输入下，加入作者训练数据能否改善新录制表现？”时查看本目录文件。

## 不要误解

mixed 相比 our 在lyc/zyf LOCKED_TEST Balanced Accuracy增加4.39/8.99个百分点，分别为52.68%/55.77%；仍未超过旧pooled的64.28%/57.69%。Our reference（电压参考电极）=Pz已确认，作者reference未知，跨来源结论保持 exploratory / channel-aligned but reference compatibility uncertain。
