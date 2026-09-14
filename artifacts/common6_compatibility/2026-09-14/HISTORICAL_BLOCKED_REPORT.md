# Common-6 compatibility audit

> **BLOCKED** — common6 训练与 LOCKED_TEST prediction-only 对比未启动，因为仓库证据不足以可靠确认 `T5/T6 → P7/P8`，且作者 MAT 的 reference 未知。

## Decision

| item | result |
|---|---|
| `T5-Pz → P7` | **unconfirmed**；当前 EDF 有 T5-Pz，但没有设备 montage/electrode mapping 证明它在本数据语境中等于作者 P7。 |
| `T6-Pz → P8` | **unconfirmed**；理由同上。 |
| Proposed `COMMON_6_CHANNELS` | **not established**；没有写入 `cross_source_utils.py`，也没有启动 common6 训练。 |
| Our EDF reference | **Pz indicated**：CSV sidecar 明确写 `Reference location: Pz`，EDF signal label 也带 `-Pz`；但 EDF 没有完整 rereference 历史或逐通道数值方程。 |
| Author MAT reference | **unknown**；34 个 MAT 的 `o` struct 没有 reference/montage/electrode 字段，检查的作者 notebook 也没有显式 rereference 操作。 |
| Reference compatibility | **uncertain**；不能把作者 MAT 与我们的 Pz-referenced EDF 宣称为完全兼容。 |

## Evidence inspected

- EDF audit: 43 unique EDF files from confirmed `lyc`/`zyf` historical rows plus current LOCKED_TEST/reference rows。所有已审计 EDF 的采样率和通道布局见 `edf_header_metadata.csv`。
- EDF channel evidence: `T5-Pz` in 43/43 files；`T6-Pz` in 43/43；literal `P7` in 0/43；literal `P8` in 0/43。
- DSI sidecars: 36 unique CSV files；`Reference location: Pz` in 36/36。Headset/logger/filter metadata and channel headers见 `sidecar_metadata.csv`。
- `data/DATA_PROTOCOL.md` records the fixed collection target as `DSIStreamer`, 300 Hz, 24 EEG channels, Pz reference; this confirms the project-level reference declaration, but it does not provide a T5/T6-to-P7/P8 mapping table.
- EDF raw headers contain labels such as `EEG T5-Pz` and `EEG T6-Pz`; they contain no literal `P7` or `P8` in the audited layout. MNE metadata has no montage object or explicit rereference history.
- Author MAT audit: 34 files inspected; 0 contain a field whose name explicitly mentions reference/montage/electrode/channel/sensor/headset。逐文件见 `author_mat_metadata.csv`。
- The author notebooks explicitly select `F7,F3,P7,O1,O2,P8,AF4` from `o.data[:, 3:17]`, but provide no acquisition montage/reference declaration and no rereference call.
- The repository contains no checked-in device montage/electrode mapping that establishes `T5-Pz ↔ P7-Pz` and `T6-Pz ↔ P8-Pz`; the existing adapter intentionally refuses this spatial-name substitution.

## Why the stage stops

The conventional old/new 10–20 naming relationship may be a hypothesis, but it is not sufficient under this project's rule requiring evidence from the current device/data context. Substituting T5/T6 would change the semantic channel definition while pretending the author and EDF features are identical. That would make `author-common6`, `our-common6`, and `mixed-common6` an unfair comparison.

Reference uncertainty is also a potential domain-shift source. Even if the spatial mapping is later confirmed, the cross-source conclusion must still be qualified by device, reference, session, and paradigm differences.

## Not run

| model | lyc LOCKED_TEST | zyf LOCKED_TEST | status |
|---|---:|---:|---|
| `author-common6` | N/A | N/A | BLOCKED before fit |
| `our-common6` | N/A | N/A | BLOCKED before fit |
| `mixed-common6` | N/A | N/A | BLOCKED before fit |

- `author-common6`: not trained; no model artifact.
- `our-common6`: not trained; no historical feature/model fit was run.
- `mixed-common6`: not trained; no source mixing was run.
- Common6 LOCKED_TEST comparison: not run because there is no common6 pipeline to transform/predict. Existing pooled/personal LOCKED_TEST artifacts were not read or rewritten by this audit.
- No scaler, PCA, SVC, feature selector, threshold, calibration, fine-tuning, oversampling, or hyperparameter search was performed.

## Evidence required to unblock

1. A device/manufacturer acquisition configuration or montage for the actual DSI headset/channel setup that explicitly identifies the physical/electrical meaning of T5 and T6 relative to P7 and P8.
2. Author-side acquisition documentation or MAT metadata that states the reference and any rereferencing/derivation operation.
3. A reproducible conversion rule showing that the two sources can use the same six channel semantics and reference, or an explicitly justified rereference procedure outside LOCKED_TEST.

Audit outputs are in `C:/CHLight/0-Plan/EEGreproduction/EEGAttention/artifacts/common6_compatibility/2026-09-14/`. Generated from repository HEAD `12e70b819938dde0b9ca48d0423337c9c3550917`; no model fitting occurred.
