# 实验产物总览

这里保存由脚本或 notebook 生成的可复现实验文件。原始 EDF/CSV/DSI/MAT 在 `data/`，代码在 `scripts/`；本目录中的文件通常可以删除后重新生成，但冻结目录和锁定测试结果必须先核对哈希，不能随意覆盖。

| 子目录 | 直接内容与用途 | 当前可信边界 |
|---|---|---|
| `legacy_baseline_v0/` | 旧 pooled baseline 的完整冻结 pipeline、配置、划分、验证预测和冻结清单。 | 已冻结；不因新实验重训或覆盖。 |
| `locked_test/2026-09-07/` | 旧 pooled model 在正式 LOCKED_TEST 上的 prediction-only 结果。 | 回归基线；只读。 |
| `subject_models/` | lyc/zyf personal model 及各自历史训练范围、zqd 排除清单。 | 本阶段新模型；不包含 locked 数据。 |
| `subject_model_comparison/2026-09-07/` | pooled 与两个 personal model 在相同 locked session 上的交叉评估。 | 本阶段正式比较结果。 |
| `subject_model_diagnostics/2026-09-07/` | personal model 的类别偏置、session 级、历史 held-out 和 PCA 诊断。 | 诊断结果，不是新冻结模型。 |
| `author_models/author_only/` | 只使用 23 个 author MAT recording 的既有 7 通道 author-only pipeline 和 GroupKFold 验证。 | 保留的内部基线；不覆盖。 |
| `author_models/author_common6/` | 只使用同一 23 个 author recording 的 common6 pipeline；主动舍弃 AF4。 | 可用于探索性跨来源比较；author reference unknown。 |
| `our_common7_models/pooled_common7/` | our-common7 pooled 的通道门禁结果。 | 当前 blocked，无模型。 |
| `our_common6_models/pooled_common6/` | lyc/zyf historical candidate 的 common6 pooled pipeline 和 recording-level 验证。 | 已训练；不含 zqd/unknown/LOCKED_TEST。 |
| `mixed_models/our_author_mixed/` | our+author mixed 的通道门禁结果。 | 当前 blocked，无模型。 |
| `mixed_models/our_author_mixed_common6/` | author historical + lyc/zyf historical 的 common6 mixed pipeline 和验证产物。 | 已训练；跨源解释 exploratory。 |
| `cross_source_comparison/2026-09-07/` | pooled/personal/author/common7/mixed 的统一比较表。 | 跨来源结果按通道可比性标记。 |
| `cross_source_comparison/2026-09-14/` | common6 最终统一比较、逐窗口/逐 session 指标、预测比例和混淆矩阵。 | LOCKED_TEST fit_calls=0；reference compatibility uncertain。 |
| `legacy/` | 旧自采 notebook 输出、缓存和人工检查表。 | 历史探索，不作为正式泛化结论。 |
| `reproductions/` | 运行/改造上游流程得到的 `.npy`、`.npz`、`.pth`、ROC 和训练表。 | 上游复现证据，不用于当前 LOCKED_TEST。 |
| `upstream_author/` | 原作者版本中已有的训练结果表。 | 来源对照，不是本项目新生成结果。 |
| `README.md` | 本目录的来源分类和保护规则。 | 文档。 |

各子目录的直接文件说明见对应 README；跨目录完整索引见 [`docs/REPOSITORY_FILE_GUIDE.md`](../docs/REPOSITORY_FILE_GUIDE.md)。

## Common6 兼容性门禁

`common6_compatibility/2026-09-14/` 保存本轮的设备通道、EDF/MAT reference、montage 证据和历史门禁迁移。ACNS/Wearable Sensing 证据已解除 T5/T6→P7/P8 命名阻塞；Our reference=Pz confirmed，author MAT reference unknown。原始阻塞状态保存在 `HISTORICAL_*` 文件中。
