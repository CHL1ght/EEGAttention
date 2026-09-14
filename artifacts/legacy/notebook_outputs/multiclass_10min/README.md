# 这个目录是什么

这里保存早期约10分钟单状态录制做多分类探索时的中间结果。

## 它属于项目哪一步

Stage 1：早期自采 EEG 探索

前一步：原作者方案与数据。
这一步：模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？
后一步：需要按完整录制隔离、并能保存全套处理步骤的正式基线。

完整故事：[实验阶段地图](../../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？

## 输入从哪里来

data/legacy/multiclass_10min/ 和 data/legacy/mixed_20min/：39 个 EDF（脑电信号文件）。CSV/DSI 是设备配套导出。

## 谁生成这里的文件

notebooks/legacy/self_recorded/；scripts/validate_legacy_manifest.py 核对后续建立的清单。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [four_class_features_cache.npz](four_class_features_cache.npz) | 旧四分类 notebook 的特征缓存；保留作历史复现。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [leave_one_edf_file_out_28train_1test_results.csv](leave_one_edf_file_out_28train_1test_results.csv) | 旧逐 EDF 留出实验结果；与当前 LOCKED_TEST 协议不同。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [progressive_next_file_test_results.csv](progressive_next_file_test_results.csv) | 旧按文件顺序逐步测试结果；仅作探索记录。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [three_class_features_cache.npz](three_class_features_cache.npz) | 旧三分类 notebook 的特征缓存；不是当前 240 维正式 baseline 输入。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

historical：用于理解早期方案。

## 我什么时候需要看这个目录

需要回答“模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？”时查看本目录文件。

## 不要误解

同一录制切成的相邻窗口很相似，随机分配窗口可能让模型在测试中见到熟悉的录制条件，分数虚高。旧单状态 iu/ou 归为 unfocus，daze 只作静息参考；旧 mixed 前10分钟 unfocus、后10分钟 focus。
