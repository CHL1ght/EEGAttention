# Personal model diagnostics

本报告只做诊断，不做调参，不重训正式 personal model，也不在 LOCKED_TEST 上 fit。

## 1. 数据分布

| dataset | subject | true label | sessions | EDFs | windows | window proportion |
|---|---|---|---:|---:|---:|---:|
| historical_training | lyc | unfocus | 7 | 10 | 2983 | 44.25% |
| historical_training | lyc | focus | 12 | 12 | 3758 | 55.75% |
| historical_training | zyf | unfocus | 6 | 8 | 2387 | 53.25% |
| historical_training | zyf | focus | 7 | 7 | 2096 | 46.75% |
| locked_test | lyc | unfocus | 1 | 1 | 424 | 37.56% |
| locked_test | lyc | focus | 2 | 2 | 705 | 62.44% |
| locked_test | zyf | unfocus | 1 | 1 | 418 | 33.17% |
| locked_test | zyf | focus | 2 | 2 | 842 | 66.83% |

## 2. 预测类别偏置

| model | test subject | accuracy | balanced accuracy | true focus | predicted focus | focus proportion delta |
|---|---|---:|---:|---:|---:|---:|
| lyc personal model | lyc | 46.68% | 47.67% | 62.44% | 45.44% | -17.01% |
| lyc personal model | zyf | 67.94% | 51.80% | 66.83% | 98.57% | +31.75% |
| Existing pooled frozen model | lyc | 65.54% | 64.28% | 62.44% | 58.64% | -3.81% |
| Existing pooled frozen model | zyf | 46.11% | 57.69% | 66.83% | 18.17% | -48.65% |
| zyf personal model | lyc | 45.79% | 56.45% | 62.44% | 8.77% | -53.68% |
| zyf personal model | zyf | 41.35% | 52.14% | 66.83% | 18.65% | -48.17% |

重点组合 `lyc personal → zyf`：
- accuracy = 67.94%；balanced accuracy = 51.80%。
- true focus proportion = 66.83%；predicted focus proportion = 98.57%。
- 诊断判断：支持明显类别预测偏置；67.94% 类似的 accuracy 不能解释为稳定跨受试者泛化。

## 3. Session 级结果

每个 EDF/session 的完整表见 `session_diagnostics.csv`；单一真实类别 session 的 balanced accuracy 标记为 N/A。

## 4. Historical subject-internal held-out

采用 Leave-One-Session-Group-Out。每个 fold 先按完整 session_group_id 分开，再只在 train fold fit Scaler/PCA/SVC。

| subject | folds | accuracy mean | accuracy std | balanced valid folds | balanced mean | balanced std |
|---|---:|---:|---:|---:|---:|---:|
| lyc | 12 | 71.67% | 29.00% | 7 | 75.39% | 13.62% |
| zyf | 7 | 74.58% | 12.80% | 6 | 75.71% | 13.71% |

## 5. PCA

| model | raw feature dimension | PCA dimension | cumulative explained variance |
|---|---:|---:|---:|
| Existing pooled frozen model | 240 | 67 | 95.05% |
| lyc personal model | 240 | 65 | 95.07% |
| zyf personal model | 240 | 74 | 95.06% |

## 6. MAT / EDF common-7 channel check

Required explicit order: `F7, F3, P7, O1, O2, P8, AF4`。不把 T5/T6 等空间近似名称猜成 P7/P8。

| EDF | sampling rate | common7 available | missing channels |
|---|---:|---|---|
| `lyc_focus1_20260907.edf` | 300 Hz | False | P7, P8, AF4 |
| `lyc_focus_202609072034_raw.edf` | 300 Hz | False | P7, P8, AF4 |
| `lyc_unfocus1_20260907.edf` | 300 Hz | False | P7, P8, AF4 |
| `zyf_focus1_20260907.edf` | 300 Hz | False | P7, P8, AF4 |
| `zyf_focus2_20260907.edf` | 300 Hz | False | P7, P8, AF4 |
| `zyf_unfocus1_20260907.edf` | 300 Hz | False | P7, P8, AF4 |

结论：无法公平进行 author → EDF、our-common7 或 mixed：正式 locked EDF 缺少 AF4, P7, P8；未使用 T5/T6 等空间近似替代。

## 7. 诊断结论

- Personal model 历史 held-out：lyc held-out 75.39%; zyf held-out 75.71%；历史 held-out 结果不完全接近随机，不能仅凭 LOCKED_TEST 结果断言任务本身不可分。
- LOCKED_TEST / historical 对比：历史 held-out 高于对应 LOCKED_TEST，结果支持 session/domain shift 是重要嫌疑，但不是唯一解释。
- 当前高 accuracy 组合：支持明显类别预测偏置；67.94% 类似的 accuracy 不能解释为稳定跨受试者泛化。
- 本次历史 held-out pipeline fit 次数：19；LOCKED_TEST fit 次数：0。

author-only 模型是否可以进一步测试 our EDF、以及 our-common7/mixed 模型，取决于上述明确通道对齐结果；如果缺少关键通道，本阶段不强行生成跨来源指标。
