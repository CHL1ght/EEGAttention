# `cross_source_comparison/`

这里保存 pooled、personal、author 和 cross-source 模型的统一比较表。已有 pooled/personal 结果直接读取上一阶段 locked comparison；common6/common7 新模型在通道可用时才会对 LOCKED_TEST 做 prediction-only 评估。

| 子目录 | 内容 |
|---|---|
| `2026-09-07/` | 当前正式 LOCKED_TEST 的统一比较；author-only 有 recording-level held-out 结果，但跨 EDF 结果因缺少 common7 通道为 N/A。 |
| `2026-09-14/` | common6 阶段最终比较：author-common6、our-common6、mixed-common6 与旧 pooled/personal 结果；含逐窗口、逐 session、混淆矩阵和 predicted class ratio。 |
| `README.md` | 本目录说明。 |
