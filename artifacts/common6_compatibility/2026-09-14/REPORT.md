# Common-6 compatibility audit

> **UNBLOCKED_FOR_COMMON6_TRAINING** — authoritative nomenclature/device evidence confirms the T5/T6 to P7/P8 name equivalence for the current DSI-24 data. The author MAT reference remains unknown, so all cross-source results are exploratory and channel-aligned but reference-compatibility-uncertain.

## Decision

| item | result |
|---|---|
| `T5-Pz → P7-Pz` | **confirmed nomenclature equivalence** for current DSI-24 data by ACNS old/new 10–20 naming and Wearable Sensing `P7/T5` device specification. |
| `T6-Pz → P8-Pz` | **confirmed nomenclature equivalence** for current DSI-24 data by ACNS old/new 10–20 naming and Wearable Sensing `P8/T6` device specification. |
| `COMMON_6_CHANNELS` | **established** as `F7, F3, P7, O1, O2, P8`; the adapter is implemented in `scripts/cross_source_utils.py`. `AF4` is intentionally dropped. |
| Our EDF reference | **Pz confirmed** by Wearable Sensing technical documentation, DSIStreamer sidecars, and `*-Pz` labels. |
| Author MAT reference | **unknown**; 34 MAT files expose no reference/montage/electrode metadata sufficient to resolve it. |
| Reference compatibility | **uncertain**; common6 may be used for exploratory channel-aligned comparisons, but the two sources must not be claimed to have identical references. |

## Authoritative external evidence

- [ACNS Guideline 2](https://www.acns.org/UserFiles/file/EEGGuideline2Electrodenomenclature_final_v1.pdf): modified 10–10 nomenclature replaces old 10–20 `T5/T6` with `P7/P8`.
- [Wearable Sensing DSI-24 specification](https://wearablesensing.com/dsi-24/): lists the corresponding device locations as `P7/T5` and `P8/T6`.
- [Wearable Sensing technical documentation](https://support.wearablesensing.com/examples/mne/python/core/channels.html): states DSI-24 hardware reference is `Pz` and DSI-Streamer data uses this reference.

## Evidence inspected

- EDF audit: 43 unique EDF files from confirmed `lyc`/`zyf` historical rows plus current LOCKED_TEST/reference rows. Layout details are in `edf_header_metadata.csv`.
- EDF channel evidence: `T5-Pz` in 43/43 files; `T6-Pz` in 43/43; literal `P7` in 0/43; literal `P8` in 0/43.
- DSI sidecars: 36 unique CSV files; `Reference location: Pz` in 36/36. Details are in `sidecar_metadata.csv`.
- EDF raw headers contain `EEG T5-Pz` and `EEG T6-Pz`; the adapter applies only the documented nomenclature equivalence, not a spatial interpolation or signal transformation.
- Author MAT audit: 34 files inspected; 0 contain a field whose name explicitly mentions reference/montage/electrode/channel/sensor/headset. Details are in `author_mat_metadata.csv`.
- The author notebooks explicitly select `F7,F3,P7,O1,O2,P8,AF4` from `o.data[:, 3:17]`, but provide no acquisition reference declaration or rereference call.

## Scope and fit policy

- The channel-name gate is cleared; `author-common6`, `our-common6`, and `mixed-common6` may now be trained by the dedicated training script.
- `LOCKED_TEST` remains prediction-only: it may be used for `transform`, `predict`, and final metrics, never for scaler/PCA/SVC/feature-selector fit, threshold tuning, or model selection.
- Only confirmed `lyc`/`zyf` historical data are eligible for our-source training. `zqd` and unknown-identity files remain excluded.
- Cross-source conclusions must be labeled `exploratory / channel-aligned but reference compatibility uncertain` and must account for subject, session, device, task/paradigm, preprocessing representation, and unresolved author-reference differences.

## Historical blocked state

The previous conservative gate is preserved in `HISTORICAL_BLOCKED_REPORT.md`, `HISTORICAL_BLOCKED.json`, and `HISTORICAL_EVIDENCE_AUDIT.csv`. It recorded T5/T6 mapping as unconfirmed and stopped before common6 model fitting; those historical judgments are not deleted or rewritten.

Audit outputs are in `C:/CHLight/0-Plan/EEGreproduction/EEGAttention/artifacts/common6_compatibility/2026-09-14/`. Generated from repository HEAD `12e70b819938dde0b9ca48d0423337c9c3550917`; this audit itself performed no model fitting and did not read LOCKED_TEST signal values.
