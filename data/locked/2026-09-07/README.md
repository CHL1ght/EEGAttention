# 这个目录是什么

这里是已有独立测试批次的原始信号，正式标签与有效区间由 session_manifest.csv 登记。

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
| [lyc_death1_20260907_raw.csv](lyc_death1_20260907_raw.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_death1_20260907_raw.edf](lyc_death1_20260907_raw.edf) | `20260907_lyc_rest_01`，早期命名 death，manifest canonical label 为 rest；reference，不计二分类。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_death1_20260907.dsi](lyc_death1_20260907.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_focus_202609072034_raw.csv](lyc_focus_202609072034_raw.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_focus_202609072034_raw.edf](lyc_focus_202609072034_raw.edf) | `20260907_lyc_focus_02`，lyc focus；CSV/DSI 为同名 sidecar。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_focus_202609072034.dsi](lyc_focus_202609072034.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_focus1_20260907.csv](lyc_focus1_20260907.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_focus1_20260907.dsi](lyc_focus1_20260907.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_focus1_20260907.edf](lyc_focus1_20260907.edf) | `20260907_lyc_focus_01`，lyc focus；CSV/DSI 为同名 sidecar。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_unfocus1_20260907.csv](lyc_unfocus1_20260907.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_unfocus1_20260907.dsi](lyc_unfocus1_20260907.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [lyc_unfocus1_20260907.edf](lyc_unfocus1_20260907.edf) | `20260907_lyc_unfocus_01`，lyc unfocus；CSV/DSI 为同名 sidecar。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [recording_notes.md](recording_notes.md) | 该批次现场记录备注。 | 手写维护 | 可维护，保留来源与实验边界 |
| [zyf_focus1_20260907.csv](zyf_focus1_20260907.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_focus1_20260907.dsi](zyf_focus1_20260907.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_focus1_20260907.edf](zyf_focus1_20260907.edf) | `20260907_zyf_focus_01`，zyf focus；CSV/DSI 为同名 sidecar。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_focus2_20260907.csv](zyf_focus2_20260907.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_focus2_20260907.dsi](zyf_focus2_20260907.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_focus2_20260907.edf](zyf_focus2_20260907.edf) | `20260907_zyf_focus_02`，zyf focus；CSV/DSI 为同名 sidecar。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_unfocus1_20260907.csv](zyf_unfocus1_20260907.csv) | 同名录制的设备时序导出；保留参考电极等元数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_unfocus1_20260907.dsi](zyf_unfocus1_20260907.dsi) | 同名录制的DSI采集软件配套文件，用于追溯。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [zyf_unfocus1_20260907.edf](zyf_unfocus1_20260907.edf) | `20260907_zyf_unfocus_01`，zyf unfocus；CSV/DSI 为同名 sidecar。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

原始数据只读；角色按清单/协议决定。

## 我什么时候需要看这个目录

需要回答“面对从未参与训练的新录制，旧模型表现如何？”时查看本目录文件。

## 不要误解

LOCKED_TEST（冻结测试数据，只能预测，不能参与任何 fit，即学习参数）首轮总 Accuracy 55.30%、Balanced Accuracy 59.91%，明显低于历史验证。按整个 EDF/session 隔离，防止同一次录制的窗口跨集合。
