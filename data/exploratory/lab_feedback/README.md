# 这个目录是什么

这里为今天看模型反馈、主动调整状态前后的录制建立归档规则。

## 它属于项目哪一步

Stage 8：LAB_FEEDBACK（现场反馈探索数据）。

前一步：Common6 通道对齐与 Mixed。
这一步：人看到模型反馈后主动调整状态，多个模型预测方向会不会一致变化？
后一步：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

人看到模型反馈后主动调整状态，多个模型预测方向会不会一致变化？

## 输入从哪里来

真实EDF/CSV/DSI回来后才登记；当前仅README，没有伪造信号或metadata。

## 谁生成这里的文件

采集者确认metadata；QuickTest调用subject_model_utils.py，不自动保存文件。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [2026-09-14/](2026-09-14/README.md) | 这里为今天看模型反馈、主动调整状态前后的录制建立归档规则。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

exploratory规则已建立；尚无今天录制或分析结果。

## 我什么时候需要看这个目录

今天带回录制文件后按数据协议第7节整理。

## 不要误解

feedback0未看本轮反馈，也不自动成为最终测试；本目录全部默认禁止训练和最终测试。

## 今日录制与metadata

目录：`data/exploratory/lab_feedback/2026-09-14/`。命名：`subject_status_timestamp_extra.edf`，如 `lyc_focus_202609141630_feedback0.edf`、`lyc_focus_202609141650_feedback1.edf`；EDF/CSV/DSI保持同一stem。

数据回来后逐EDF登记：subject_id、intended_label、timestamp（Asia/Shanghai）、feedback_round、feedback_seen_before_recording、task、notes、dataset_role=lab_feedback、eligible_for_training=false、eligible_for_final_test=false；补充pair_id、原文件名、EDF/CSV/DSI相对路径和SHA-256。feedback0为false，feedback1+为true；与实际过程不符时先核实。

原始文件 → 确认身份/预期标签/时间 → 确认反馈轮次 → 保留原件 → SHA-256 → metadata → QuickTest → 另存探索分析。当前只建README，不创建metadata.csv或信号文件。

不加入legacy_manifest.csv候选或正式session_manifest.csv；不按漂亮预测挑选训练数据。未来训练需另做明确数据晋升决定并保留provenance（来源与使用历史）；看过反馈的数据不能变成独立最终测试。

完整字段定义：[DATA_PROTOCOL.md](../../DATA_PROTOCOL.md)第7节。
