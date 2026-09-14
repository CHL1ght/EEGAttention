# Unified cross-source comparison — `2026-09-07`

本目录不重新训练已有 pooled/personal 模型；直接复用上一阶段同一批 LOCKED_TEST 比较，并登记 author/common7/mixed 的可比性状态。

| 文件 | 含义 |
|---|---|
| `unified_model_comparison.csv` | 按 model × test subject 的 accuracy、balanced accuracy、author/cross-source held-out balanced accuracy 和状态。 |
| `common7_channel_alignment.csv` | 6 个正式 locked EDF 的通道映射和缺失通道。 |
| `comparison_summary.json` | 统一比较版本、通道门禁、模型哈希和 LOCKED_TEST fit policy。 |
| `REPORT.md` | 最终统一表和跨来源比较阻塞说明。 |
| `README.md` | 本日期比较目录说明。 |
