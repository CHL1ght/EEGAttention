# `data/legacy/mixed_20min/`

这里保存旧的约 20 分钟固定顺序 EDF。文件本身不携带可依赖的二分类边界；正式读取必须使用 `data/legacy_manifest.csv` 中登记的片段区间：`0–600s=unfocus`、`600–1200s=focus`。同一 EDF 的两个逻辑片段共享 source/session group，不能拆到不同数据侧。

| 文件 | 身份/用途 |
|---|---|
| `data_0001_raw.edf` | lyc 早期 2.5 秒设置/demo，短于 4 秒窗口；排除。 |
| `data_0002_raw.edf` | lyc mixed session 01；manifest 登记 unfocus/focus 两个片段。 |
| `data_0003_raw.edf` | lyc mixed session 02；manifest 登记 unfocus/focus 两个片段。 |
| `data_0004_raw.edf` | lyc mixed session 03；manifest 登记 unfocus/focus 两个片段。 |
| `data_zqd_1_raw.edf` | zqd mixed session 01；本阶段 personal model 排除。 |
| `data_zqd_2_raw.edf` | zqd mixed session 02；本阶段 personal model 排除。 |
| `data_zqd_3_raw.edf` | zqd mixed session 03；本阶段 personal model 排除。 |
| `data_zyf_1_raw.edf` | zyf mixed session 01；manifest 登记 unfocus/focus 两个片段。 |
| `data_zyf_2_raw.edf` | zyf mixed session 02；manifest 登记 unfocus/focus 两个片段。 |
| `data_zyf_3_raw.edf` | zyf mixed session 03；manifest 登记 unfocus/focus 两个片段。 |

这些 EDF 是只读原始数据，没有配套 CSV/DSI；标签、时间边界和哈希都在 manifest。验收命令：`python scripts/validate_legacy_manifest.py`。
