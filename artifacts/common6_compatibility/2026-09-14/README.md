# Common6 兼容性核验｜2026-09-14

本目录是 inspection-only 兼容性审计结果。ACNS 与 Wearable Sensing 权威证据确认当前 DSI-24 数据的 `T5/T6` 分别可按 nomenclature equivalence 映射为 `P7/P8`，因此 common6 训练门禁已解除。Our EDF reference 为 `Pz (confirmed)`，但 author MAT reference 仍为 `unknown`；跨源结论必须保持 exploratory / channel-aligned but reference compatibility uncertain。

| 文件 | 含义 |
|---|---|
| `REPORT.md` | 人类可读的当前兼容性结论、外部证据链接、reference 说明和 fit policy。 |
| `BLOCKED.json` | 兼容性门禁的机器可读状态；当前 `status=unblocked_for_common6_training`。 |
| `BLOCKED.md` | 说明保留 `BLOCKED` 文件名的原因和状态迁移。 |
| `HISTORICAL_BLOCKED_REPORT.md` | 原始保守阻塞报告快照，不删除历史判断过程。 |
| `HISTORICAL_BLOCKED.json` | 原始阻塞 JSON 快照。 |
| `HISTORICAL_EVIDENCE_AUDIT.csv` | 原始证据审计表快照。 |
| `edf_header_metadata.csv` | 已确认 lyc/zyf 历史 EDF 与当前 LOCKED_TEST/reference EDF 的 MNE/原始 EDF 通道头信息。 |
| `sidecar_metadata.csv` | DSIStreamer CSV sidecar 的 `Reference location`、headset、logger、filter、单位和通道头。 |
| `author_mat_metadata.csv` | 34 个作者 MAT 的 `o` struct 字段、数据形状、采样率和是否存在 reference/montage 字段。 |
| `notebook_audit.json` | 作者 notebook 的通道选择、数据切片和显式 rereference 操作检查。 |
| `evidence_audit.csv` | 每条兼容性证据及其是否支持映射/reference 的结构化记录。 |
| `run_manifest.json` | 审计版本、输出哈希和“未进行模型 fit / 未读 LOCKED_TEST 信号”的声明。 |

重跑兼容性审计：

```powershell
python scripts/verify_common6_compatibility.py
```
