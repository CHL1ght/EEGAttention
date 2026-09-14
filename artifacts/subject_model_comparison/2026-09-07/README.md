# pooled × subject-dependent 对比：2026-09-07

本目录比较三个已 fit 模型在同一批 6 个正式 LOCKED_TEST session 上的表现：旧 pooled frozen、lyc personal、zyf personal。评估入口 `scripts/evaluate_subject_models.py` 的 `fit_calls=0`；rest reference 被排除。

| 文件 | 含义 |
|---|---|
| `predictions.csv` | 三个模型对每个 locked 窗口的逐窗口 prediction；包含 model、test subject、session、true/pred 和窗口时间。 |
| `session_metrics.csv` | model × session 的窗口数量、accuracy、预测类别数量和比例。 |
| `subject_model_comparison.csv` | model × test subject 的交叉评估主表，含 accuracy、balanced accuracy、类别比例和混淆矩阵。 |
| `test_sessions.csv` | 实际参与比较的 6 个 formal locked session 及其标签/活动区间。 |
| `comparison_metrics.json` | 主表的 JSON 版本、模型哈希、测试 session、reference 排除和 fit policy。 |
| `run_manifest.json` | 清单和输出文件哈希；确认本次评估未训练。 |
| `REPORT.md` | 人类可读的结果矩阵和测试 session 列表。 |
