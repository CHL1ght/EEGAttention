# 这个目录是什么

这是 CURRENT 与 HISTORICAL 模型、预测和报告的总索引。

## 它属于项目哪一步

Stage 0–9：旧实验全部冻结为 historical evidence；New Paradigm v1 尚无模型产物。

前一步：Common6 通道对齐与 Mixed。
这一步：找到某个分数的原始记录，并判断它是历史探索、冻结模型还是正式测试结果。
后一步：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

完整故事：[实验阶段地图](../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

找到某个分数的原始记录，并判断它是历史探索、冻结模型还是正式测试结果。

## 输入从哪里来

data/reference/original_mat/、data/legacy_manifest.csv、data/session_manifest.csv及已保存模型。

## 谁生成这里的文件

各目录README列出的训练/评估脚本；本轮不执行任何训练。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [current/](current/README.md) | **CURRENT** 产物入口；New Paradigm v1 目前为空骨架。 | 目录 | 仅新实验版本可写 |
| [historical/](historical/README.md) | **HISTORICAL** 逻辑索引；指向原位保留的旧模型与报告。 | 目录 | 只维护索引和状态 |
| [lab_feedback/](lab_feedback/README.md) | 2026-09-14 historical pilot 的 prediction-only 结果。 | 目录 | 不覆盖历史结果 |
| [author_models/](author_models/README.md) | 这里保存两个只用原作者数据训练的模型：七通道基线与六通道对照。 | 目录 | 按子目录规则 |
| [common6_compatibility/](common6_compatibility/README.md) | 这里保存通道能否正确对应的检查证据；它是训练前的安全检查，不保存模型。 | 目录 | 按子目录规则 |
| [cross_source_comparison/](cross_source_comparison/README.md) | 这里保存作者、自采与混合模型在同一正式测试集上的对照成绩。 | 目录 | 按子目录规则 |
| [legacy/](legacy/README.md) | 这里保留早期自采实验导出的表格和中间数据，用于追溯当时为何得到那些分数。 | 目录 | 按子目录规则 |
| [legacy_baseline_v0/](legacy_baseline_v0/README.md) | 第一套保存完整处理步骤、供后续实验对照的多人通用模型。 | 目录 | 按子目录规则 |
| [locked_test/](locked_test/README.md) | 这里保存旧冻结通用模型对独立录制的测试结果，按测试批次归档。 | 目录 | 按子目录规则 |
| [mixed_models/](mixed_models/README.md) | 这里保存把作者与自采历史数据合并训练的尝试。 | 目录 | 按子目录规则 |
| [our_common6_models/](our_common6_models/README.md) | 这里保存只学我们历史数据、但只看六个共同通道的模型。 | 目录 | 按子目录规则 |
| [our_common7_models/](our_common7_models/README.md) | 这里保留要求七个共同通道时未能训练的尝试。 | 目录 | 按子目录规则 |
| [reproductions/](reproductions/README.md) | 这里存放我们运行原作者方法得到的历史复现结果，与作者自带的结果分开保存。 | 目录 | 按子目录规则 |
| [subject_model_comparison/](subject_model_comparison/README.md) | 这里保存三种模型对同一批新录制的成绩，用来公平比较个人模型与通用模型。 | 目录 | 按子目录规则 |
| [subject_model_diagnostics/](subject_model_diagnostics/README.md) | 这里保存查找个人模型失效原因的证据：预测偏向、历史留出表现和逐录制表现。 | 目录 | 按子目录规则 |
| [subject_models/](subject_models/README.md) | 这里保存lyc与zyf各自的模型，用来检验只学一个人的历史记录是否更好。 | 目录 | 按子目录规则 |
| [upstream_author/](upstream_author/README.md) | 这里保存原作者项目最初就附带的结果，用于区分作者成绩和我们后来复现的成绩。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

七个旧模型均为 `historical baseline`；2026-09-14 LAB_FEEDBACK 为 historical pilot。CURRENT 尚无训练模型或预测结果。

## 我什么时候需要看这个目录

当前工作先看 current/new_paradigm_v1/；追溯 mixed 则进入 cross_source_comparison/2026-09-14/。

## 不要误解

目录中有成绩不代表它是 CURRENT 或独立测试；不要覆盖旧模型和结果。
