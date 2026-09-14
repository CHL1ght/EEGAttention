# Personal model diagnostics — `2026-09-07`

本目录使用历史 `legacy_baseline_candidate` 重新做 session-held-out 诊断，并读取既有 subject comparison predictions 统计 LOCKED_TEST；LOCKED_TEST fit 次数为 0。

| 文件 | 含义 |
|---|---|
| `class_distribution.csv` | lyc/zyf historical training 与 LOCKED_TEST 的按真实类别 session、EDF、window 数和比例。 |
| `prediction_bias.csv` | pooled、lyc personal、zyf personal 在 lyc/zyf LOCKED_TEST 上的真实/预测类别数量、比例、accuracy 和 balanced accuracy。 |
| `session_diagnostics.csv` | 每个 model × subject × EDF/session 的真实标签、窗口数、预测类别数/比例、accuracy、balanced accuracy（单类 session 为 N/A）和 majority prediction。 |
| `historical_heldout_folds.csv` | 每个 subject 的 Leave-One-Session-Group-Out fold 结果；Scaler/PCA/SVC 只在该 fold train group fit。 |
| `historical_heldout_summary.csv` | lyc/zyf fold accuracy、balanced accuracy 均值、标准差和有效 balanced fold 数。 |
| `pca_diagnostics.csv` | pooled、lyc personal、zyf personal 的原始 feature dimension、PCA 维度和累计解释方差。 |
| `common7_channel_alignment.csv` | 正式 locked EDF 的实际通道名、明确映射结果和缺失 common7 通道。 |
| `diagnostic_summary.json` | 诊断结论、偏置证据、session shift 判断和 fit policy。 |
| `run_manifest.json` | 输入/输出哈希与本次诊断运行边界。 |
| `REPORT.md` | 人类可读的完整 personal diagnosis。 |
| `README.md` | 本日期诊断目录说明。 |
