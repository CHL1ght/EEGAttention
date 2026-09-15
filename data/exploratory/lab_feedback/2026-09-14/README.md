# 这个目录是什么

这里归档 2026-09-14 的 LAB_FEEDBACK 现场录制。它属于 Stage 8，现已冻结为 `historical pilot / transition dataset`，不是训练集、验证集、LOCKED_TEST 或 New Paradigm v1 final holdout。

完整故事：[实验阶段地图](../../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../../docs/MODEL_CATALOG.md)；字段定义：[DATA_PROTOCOL.md](../../../DATA_PROTOCOL.md)第7节。

## 当前归档状态

- 现场录制已完成，本目录实际找到 11 条 EDF。
- 11 条 EDF 均有配套 CSV 和 DSI；`metadata.csv` 已登记相对路径、原始文件名、文件大小、SHA-256、EDF 头部时长/采样率/通道数、CSV 时间轴和配套文件完整性。
- 标签事实来源按 `.md notes > 现场 metadata/明确人工记录 > EDF 文件名`；`.md` 存在时以其中的 `condition` 作为 `canonical_label`。`filename_label` 只保留为低优先级 provenance，未使用任何模型预测结果改标签。
- 全部记录固定为 `dataset_role=historical_pilot`、`experiment_version=pre_new_paradigm/lab_feedback_2026-09-14`、`eligible_for_training=false`、`eligible_for_validation=false`、`eligible_for_final_test=false`，不写入旧 `legacy_manifest.csv`、旧 `data/session_manifest.csv`、`data/locked/` 或 New Paradigm v1 manifest。

## 文件名与反馈轮次说明

本批实际文件名为 `subject_status_timestamp`（lyc 文件另有 `_raw`），没有协议要求的 `feedbackX` token；现场 `.md` 记录也没有反馈轮次或是否在录制前看过反馈的说明。因此所有记录的 `feedback_round` 和 `feedback_seen_before_recording` 均登记为 `unknown`，没有按时间顺序猜测。若后续核实出 `feedback0`，应改为 `false`；若核实出 `feedback1+`，应改为 `true`。

`zyf_unfocus_202609141641` 和 `zyf_unfocus_202609141707` 的现场 `.md` 写有 `condition: focus`，与 EDF 文件名的 `unfocus` 冲突。按 `.md` 优先级，metadata 将 `canonical_label` 和兼容字段 `intended_label` 登记为 `focus`，同时保留 `filename_label=unfocus`、`label_source=md_note`、`label_conflict=true` 及冲突说明；没有根据自报或模型预测改标签，也没有重命名原始文件。

### 标签登记规则

- `filename_label`：从原始 EDF 文件名的 status token 解析，仅作 provenance。
- `canonical_label`：按 `.md notes > 现场 metadata/明确人工记录 > filename_label` 确定；所有分析 accuracy 和 `target_class_proportion` 均使用它。
- `label_source`、`label_conflict`、`label_conflict_note`：显式登记标签来源和文件名/notes 冲突；`.md` 不删除，原始文件名和原始信号内容不修改。

## 本次实际录制

| EDF | subject | filename_label | canonical_label | timestamp（Asia/Shanghai） | feedback_round | feedback_seen_before_recording | CSV | DSI | 备注 |
|---|---|---|---|---|---:|---|---|---|---|
| `lyc_focus_202609141641_raw.edf` | lyc | focus | focus | 2026-09-14 16:41 | unknown | unknown | [CSV](lyc_focus_202609141641_raw.csv) | [DSI](lyc_focus_202609141641.dsi) | 王者排位；现场记录有专注状态说明 |
| `lyc_focus_202609141702_raw.edf` | lyc | focus | focus | 2026-09-14 17:02 | unknown | unknown | [CSV](lyc_focus_202609141702_raw.csv) | [DSI](lyc_focus_202609141702.dsi) | 王者排位；现场记录有专注状态说明 |
| `lyc_focus_202609141717_raw.edf` | lyc | focus | focus | 2026-09-14 17:17 | unknown | unknown | [CSV](lyc_focus_202609141717_raw.csv) | [DSI](lyc_focus_202609141717.dsi) | 王者排位；现场记录有专注状态说明 |
| `lyc_focus_202609141800_raw.edf` | lyc | focus | focus | 2026-09-14 18:00 | unknown | unknown | [CSV](lyc_focus_202609141800_raw.csv) | [DSI](lyc_focus_202609141800.dsi) | 王者排位；现场记录有专注状态说明 |
| `lyc_focus_202609141959_raw.edf` | lyc | focus | focus | 2026-09-14 19:59 | unknown | unknown | [CSV](lyc_focus_202609141959_raw.csv) | [DSI](lyc_focus_202609141959.dsi) | 王者排位；现场记录有专注状态说明 |
| `lyc_focus_202609142023_raw.edf` | lyc | focus | focus | 2026-09-14 20:23 | unknown | unknown | [CSV](lyc_focus_202609142023_raw.csv) | [DSI](lyc_focus_202609142023.dsi) | 王者排位；现场记录有专注状态说明 |
| `lyc_unfocus_202609141825_raw.edf` | lyc | unfocus | unfocus | 2026-09-14 18:25 | unknown | unknown | [CSV](lyc_unfocus_202609141825_raw.csv) | [DSI](lyc_unfocus_202609141825.dsi) | 王者排位；现场记录描述为放松、不紧张 |
| `zyf_focus_202609141752.edf` | zyf | focus | focus | 2026-09-14 17:52 | unknown | unknown | [CSV](zyf_focus_202609141752.csv) | [DSI](zyf_focus_202609141752.dsi) | 象棋棋力测评；self-report 已合并 |
| `zyf_focus_202609141810.edf` | zyf | focus | focus | 2026-09-14 18:10 | unknown | unknown | [CSV](zyf_focus_202609141810.csv) | [DSI](zyf_focus_202609141810.dsi) | 象棋棋力测评；与好友休闲局 |
| `zyf_unfocus_202609141641.edf` | zyf | unfocus | focus | 2026-09-14 16:41 | unknown | unknown | [CSV](zyf_unfocus_202609141641.csv) | [DSI](zyf_unfocus_202609141641.dsi) | `.md` 的 condition=focus 优先；与文件名冲突；外部干扰、惊吓和叫喊已登记 |
| `zyf_unfocus_202609141707.edf` | zyf | unfocus | focus | 2026-09-14 17:07 | unknown | unknown | [CSV](zyf_unfocus_202609141707.csv) | [DSI](zyf_unfocus_202609141707.dsi) | `.md` 的 condition=focus 优先；与文件名冲突；刷视频、被打扰、看QQ、问AI |

## 完整性与使用边界

只读 EDF 标准头检查显示 11/11 文件为 26 通道、300 Hz，EDF 头部记录数与实际文件大小精确匹配。CSV 均有 31 列、300 Hz 头信息和可读时间轴；CSV 时间轴与 EDF duration 的差异原值保留在 `metadata.csv`，不覆盖任何原始文件。DSI 仅做原文件存在、大小和 SHA-256 provenance 登记。

现场 `.md` 记录已合并主观状态、任务、模式和异常说明；未提供的反馈轮次、配对关系和佩戴异常信息写为 `unknown`，没有猜测。

本轮只做数据整理、metadata/标签登记、文档更新和 exploratory prediction-only 分析。三模型结果见 [artifacts/lab_feedback/2026-09-14/REPORT.md](../../../../artifacts/lab_feedback/2026-09-14/REPORT.md)；没有训练、微调、调参、calibration、阈值调整或写入任何正式评估清单。其后续研究入口是 [New Paradigm v1](../../../current/new_paradigm_v1/README.md)，本批原文件与历史预测产物继续原位保留。
