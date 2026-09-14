# LOCKED_TEST 2026-09-07 结果

这是旧 pooled frozen model 的独立 prediction-only 结果。正式二分类包含 6 个 session、2,389 个窗口；`lyc_rest_01` 是 reference rest，不进入二分类 accuracy。

| 文件 | 含义 |
|---|---|
| `locked_predictions.csv` | 6 个正式 locked session 的逐窗口 true/pred、subject、session 和窗口起止时间。 |
| `locked_session_metrics.csv` | 每个正式 session 的窗口数、accuracy 和预测 focus/unfocus 数量/比例。 |
| `locked_subject_metrics.csv` | 将正式 session 按 lyc/zyf 聚合后的 subject 指标。 |
| `locked_metrics.json` | 总体 accuracy、balanced accuracy、混淆矩阵及计数。 |
| `reference_predictions.csv` | rest reference 的预测记录，仅供质量检查。 |
| `reference_session_metrics.csv` | rest reference 的汇总，不参与二分类指标。 |
| `run_manifest.json` | 旧 pipeline、清单、评估脚本和输出文件的哈希；记录 `fit_calls=0`。 |
| `run_summary.json` | 本次 locked evaluation 的机器可读摘要。 |
| `REPORT.md` | 人类可读的测试说明、结果和冻结边界。 |

使用 `python scripts/evaluate_locked_test.py --check-existing` 做无 EDF 读取的回归检查。
