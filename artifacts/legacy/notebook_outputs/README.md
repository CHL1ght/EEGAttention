# `artifacts/legacy/notebook_outputs/`

这里收集旧 self-recorded notebook 的导出文件。它们用于查看旧流程的中间结果、数据形状和历史对比，不是当前正式训练/测试产物；不要用这里的随机窗口指标声明跨 session 或跨 subject 泛化。

| 子目录 | 内容 |
|---|---|
| `comparisons/` | 原作者/自采通道信息及历史比较 CSV/XLSX。 |
| `mixed_20min/` | mixed EDF 导出的小样本 Excel 检查。 |
| `multiclass_10min/` | 三/四分类特征缓存、逐 EDF 留出和 progressive test 结果。 |
| `reference_inspection/` | 原始 MAT 结构和 EEG 数据抽样预览。 |
