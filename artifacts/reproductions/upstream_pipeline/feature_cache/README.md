# 上游特征缓存

| 文件 | 含义 |
|---|---|
| `full.npz` | 上游流程的完整特征缓存。 |
| `anova.npz` | 经 ANOVA 特征筛选的上游缓存。 |
| `fi.npz` | 经 feature importance 特征筛选的上游缓存。 |
| `lcc.npz` | 经线性相关性筛选的上游缓存。 |
| `pca.npz` | 上游 PCA 特征缓存。 |

这些 `.npz` 来自原作者 MAT 数据的上游深度学习复现，不能直接当作当前 240 维 Welch 特征，也不用于 LOCKED_TEST。
