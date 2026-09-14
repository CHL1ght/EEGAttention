# 这个目录是什么

这里保存通道能否正确对应的检查证据；它是训练前的安全检查，不保存模型。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

在相同六通道输入下，加入作者训练数据能否改善新录制表现？

## 输入从哪里来

common6（我们的EDF与作者MAT都能可靠对应的六个EEG通道）：F7,F3,P7,O1,O2,P8。T5/T6依据设备和命名证据对应P7/P8；舍弃AF4。

## 谁生成这里的文件

scripts/verify_common6_compatibility.py；scripts/train_cross_source_models.py 的 author-common6 / our-common6 / mixed-common6；scripts/evaluate_cross_source_models.py --channel-set common6。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [2026-09-14/](2026-09-14/README.md) | 这里保存确认 T5/T6 与 P7/P8 同名异写的证据，以及仍未解决的作者参考电极问题。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“在相同六通道输入下，加入作者训练数据能否改善新录制表现？”时查看本目录文件。

## 不要误解

不要把审计通过理解为两个数据源完全一致：作者的电压参考电极仍未知。
