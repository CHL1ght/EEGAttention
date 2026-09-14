# 这个目录是什么

这里记录共同七通道 mixed 方案为什么没有生成模型；不是可加载的模型目录。

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
| [BLOCKED.json](BLOCKED.json) | 机器可读门禁记录；common6审计中当前已解除阻塞，旧common7中仍为历史阻塞。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [BLOCKED.md](BLOCKED.md) | 解释门禁或状态迁移；不能只凭文件名判断当前是否可训练。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [channel_alignment.csv](channel_alignment.csv) | our historical EDF 和 LOCKED_TEST EDF 的 common7 明确映射检查。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

blocked / historical；旧七通道记录保持原样。

## 我什么时候需要看这个目录

需要回答“在相同六通道输入下，加入作者训练数据能否改善新录制表现？”时查看本目录文件。

## 不要误解

旧七通道阻塞不代表当前六通道仍不可用。
