# 这个目录是什么

这里是约20分钟的固定顺序录制：前10分钟unfocus、后10分钟focus，边界以正式清单为准。

## 它属于项目哪一步

Stage 1：早期自采 EEG 探索

前一步：原作者方案与数据。
这一步：模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？
后一步：需要按完整录制隔离、并能保存全套处理步骤的正式基线。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？

## 输入从哪里来

data/legacy/multiclass_10min/ 和 data/legacy/mixed_20min/：39 个 EDF（脑电信号文件）。CSV/DSI 是设备配套导出。

## 谁生成这里的文件

notebooks/legacy/self_recorded/；scripts/validate_legacy_manifest.py 核对后续建立的清单。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [data_0001_raw.edf](data_0001_raw.edf) | lyc 早期 2.5 秒设置/demo，短于 4 秒窗口；排除。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_0002_raw.edf](data_0002_raw.edf) | lyc mixed session 01；manifest 登记 unfocus/focus 两个片段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_0003_raw.edf](data_0003_raw.edf) | lyc mixed session 02；manifest 登记 unfocus/focus 两个片段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_0004_raw.edf](data_0004_raw.edf) | lyc mixed session 03；manifest 登记 unfocus/focus 两个片段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_zqd_1_raw.edf](data_zqd_1_raw.edf) | zqd mixed session 01；本阶段 personal model 排除。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_zqd_2_raw.edf](data_zqd_2_raw.edf) | zqd mixed session 02；本阶段 personal model 排除。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_zqd_3_raw.edf](data_zqd_3_raw.edf) | zqd mixed session 03；本阶段 personal model 排除。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_zyf_1_raw.edf](data_zyf_1_raw.edf) | zyf mixed session 01；manifest 登记 unfocus/focus 两个片段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_zyf_2_raw.edf](data_zyf_2_raw.edf) | zyf mixed session 02；manifest 登记 unfocus/focus 两个片段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [data_zyf_3_raw.edf](data_zyf_3_raw.edf) | zyf mixed session 03；manifest 登记 unfocus/focus 两个片段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

原始数据只读；角色按清单/协议决定。

## 我什么时候需要看这个目录

需要回答“模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？”时查看本目录文件。

## 不要误解

同一录制切成的相邻窗口很相似，随机分配窗口可能让模型在测试中见到熟悉的录制条件，分数虚高。旧单状态 iu/ou 归为 unfocus，daze 只作静息参考；旧 mixed 前10分钟 unfocus、后10分钟 focus。

## 历史标签与身份依据

单状态focus保留，iu/ou合并unfocus，daze仅参考。旧mixed前600秒unfocus、后600秒focus，早期相反说法作为历史来源冲突保留。无姓名前缀的旧lyc文件由数据负责人确认并登记；现场parser不会据此猜新文件身份。完整时间/片段/哈希见data/legacy_manifest.csv及其数据字典。
