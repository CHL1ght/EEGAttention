# `artifacts/common6_compatibility/`

这里保存 common6 进入训练前的通道、reference 和 montage 兼容性审计。该目录是安全门禁产物，不是模型目录。

| 子目录 | 含义 |
|---|---|
| `2026-09-14/` | 当前 DSIStreamer EDF、CSV sidecar、作者 MAT、作者 notebook 和权威外部证据的兼容性核验；通道命名门禁已解除，author reference 仍为 `unknown`。 |

COMMON6 训练允许使用已确认的 T5/T6 ↔ P7/P8 nomenclature equivalence；但跨来源结果必须标注 reference compatibility uncertain。旧的 pooled frozen、personal、author-only-7ch 和 common7 阻塞产物不在此目录覆盖。历史阻塞材料保存在日期目录的 `HISTORICAL_*` 文件中。
