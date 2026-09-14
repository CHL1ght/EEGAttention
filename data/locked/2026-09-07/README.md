# LOCKED_TEST 2026-09-07 原始数据

这些 raw 文件只允许被读取用于冻结模型的 transform/predict 和最终指标。正式测试的活动区间、标签、窗口数和 SHA-256 均登记在 `data/session_manifest.csv`。

| 文件 | session/用途 |
|---|---|
| `lyc_focus1_20260907.edf` | `20260907_lyc_focus_01`，lyc focus；CSV/DSI 为同名 sidecar。 |
| `lyc_focus_202609072034_raw.edf` | `20260907_lyc_focus_02`，lyc focus；CSV/DSI 为同名 sidecar。 |
| `lyc_unfocus1_20260907.edf` | `20260907_lyc_unfocus_01`，lyc unfocus；CSV/DSI 为同名 sidecar。 |
| `lyc_death1_20260907_raw.edf` | `20260907_lyc_rest_01`，早期命名 death，manifest canonical label 为 rest；reference，不计二分类。 |
| `zyf_focus1_20260907.edf` | `20260907_zyf_focus_01`，zyf focus；CSV/DSI 为同名 sidecar。 |
| `zyf_focus2_20260907.edf` | `20260907_zyf_focus_02`，zyf focus；CSV/DSI 为同名 sidecar。 |
| `zyf_unfocus1_20260907.edf` | `20260907_zyf_unfocus_01`，zyf unfocus；CSV/DSI 为同名 sidecar。 |
| `*.csv` | DSIStreamer 导出的配套时序数据；不作为当前 sklearn 特征入口。 |
| `*.dsi` | 采集软件配套记录；用于追溯/现场核验。 |
| `recording_notes.md` | 该批次现场记录备注。 |

文件哈希、活动起止和预期窗口数由 `validate_locked_data.py` 检查。不要在这里生成模型或缓存。
