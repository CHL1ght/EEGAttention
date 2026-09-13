# LOCKED_TEST 2026-09-07

This report indexes the existing first-run LOCKED_TEST artifacts. It does not replace the machine-readable JSON/CSV files.

## Baseline identity

- Baseline: `legacy_baseline_v0`.
- Freeze/test snapshot commit: `431f6c63c2e0f1461e67bf5f49b18a68b45b916d`.
- Pipeline SHA-256: `2c67ed005d3821f712771d3412bcad0a5b67a2638e89393d1d505460635488cc`.
- Config SHA-256: `274771877da2a88931edf28d9ab790c6d1ecae155558e728c6341ed89e0269e7`.
- `training_performed = false`; `fit_calls = 0`.
- Preprocessing/features are identical to Legacy: 128 Hz, 0.5–43 Hz FIR `firwin`, 4 s / 2 s windows, Welch five-band log+relative power.

## Test scope

Formal accuracy includes only the six `dataset_role=locked_test` sessions:

| Subject | Session | True label |
|---|---|---|
| lyc | 20260907_lyc_focus_01 | focus |
| lyc | 20260907_lyc_focus_02 | focus |
| lyc | 20260907_lyc_unfocus_01 | unfocus |
| zyf | 20260907_zyf_focus_01 | focus |
| zyf | 20260907_zyf_focus_02 | focus |
| zyf | 20260907_zyf_unfocus_01 | unfocus |

Excluded reference session: `20260907_lyc_rest_01` (`rest`, 31 windows), retained only for QC.

## Overall result

- Formal windows: **2,389**.
- Accuracy: **0.552951**.
- Balanced accuracy: **0.599068**.

Confusion matrix, labels `[unfocus, focus]`:

```text
[[636, 206],
 [862, 685]]
```

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| unfocus | 0.424566 | 0.755344 | 0.543590 | 842 |
| focus | 0.768799 | 0.442793 | 0.561936 | 1547 |
| macro avg | 0.596683 | 0.599068 | 0.552763 | 2389 |

## Per-session result

| Subject | Session | True | Windows | Accuracy | Focus ratio | Unfocus ratio |
|---|---|---|---:|---:|---:|---:|
| lyc | 20260907_lyc_focus_01 | focus | 422 | 0.521327 | 0.521327 | 0.478673 |
| lyc | 20260907_lyc_focus_02 | focus | 283 | 0.950530 | 0.950530 | 0.049470 |
| lyc | 20260907_lyc_unfocus_01 | unfocus | 424 | 0.591981 | 0.408019 | 0.591981 |
| zyf | 20260907_zyf_focus_01 | focus | 424 | 0.068396 | 0.068396 | 0.931604 |
| zyf | 20260907_zyf_focus_02 | focus | 418 | 0.399522 | 0.399522 | 0.600478 |
| zyf | 20260907_zyf_unfocus_01 | unfocus | 418 | 0.921053 | 0.078947 | 0.921053 |

## Per-subject result

| Subject | Sessions | Windows | Accuracy | Focus ratio | Unfocus ratio |
|---|---:|---:|---:|---:|---:|
| lyc | 3 | 1129 | 0.655447 | 0.586360 | 0.413640 |
| zyf | 3 | 1260 | 0.461111 | 0.181746 | 0.818254 |

## Reference QC

`20260907_lyc_rest_01`: 31 windows; predicted focus 29 (0.935484), predicted unfocus 2 (0.064516). It is excluded from formal accuracy and confusion matrix.

## Legacy comparison

- Legacy validation accuracy: `0.699878`.
- LOCKED_TEST accuracy: `0.552951`.
- Generalization gap: **−0.146927** (−14.69 percentage points).
- Balanced accuracy decreased from `0.696407` to `0.599068` (about −9.73 percentage points).

## Artifacts

- `locked_predictions.csv`: formal window-level predictions.
- `locked_session_metrics.csv`: formal per-session metrics.
- `locked_subject_metrics.csv`: formal per-subject metrics.
- `locked_metrics.json`: formal overall metrics and classification report.
- `reference_predictions.csv`: rest QC predictions.
- `reference_session_metrics.csv`: rest QC summary.
- `run_manifest.json`: freeze commit, pipeline/config/manifest hashes, evaluation script hash, and `fit_calls=0`.
- `run_summary.json`: complete run summary.

