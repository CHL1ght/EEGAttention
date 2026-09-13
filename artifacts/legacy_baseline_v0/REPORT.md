# legacy_baseline_v0

This report is a human-readable index of the existing machine-readable freeze artifacts. It does not replace the JSON/CSV files and does not rerun training.

## Data scope and split

- Dataset: `legacy_dataset_v0`, from `data/legacy_manifest.csv`.
- Included rows: 43 `legacy_baseline_candidate` rows, 34 source recordings, 22 complete `session_group_id` values.
- Labels: `focus → focus`; `iu/ou → unfocus`. `rest/daze`, demo, and non-candidate rows are excluded.
- Split: deterministic `numpy RandomState(42)`, first `ceil(20% × 22) = 5` complete groups for validation.
- Train: 17 groups, 25 source recordings, 9,736 windows.
- Validation: 5 groups, 9 source recordings, 3,282 windows.
- `session_group_id` intersection: 0. `source_recording_id` intersection: 0.

Validation groups:

`legacy_lyc_mixed_01`, `legacy_lyc_mixed_03`, `legacy_lyc_run_01`, `legacy_lyc_run_02`, `legacy_lyc_run_09`.

## Frozen preprocessing and features

- EDF loading: MNE, preload enabled, inferred types; all MNE EEG channels in EDF order.
- Sampling rate: resample to 128 Hz when needed.
- Filter: per manifest segment, FIR `firwin`, 0.5–43 Hz.
- Window/step: 4 s / 2 s.
- Features: Welch power per channel with 2 s `nperseg`; delta, theta, alpha, beta, and gamma bands; log absolute power plus relative power; 240 features.
- Model: `StandardScaler → PCA(n_components=0.95, random_state=42) → SVC(kernel='rbf', C=10, gamma='scale', class_weight='balanced', probability=True, random_state=42)`.
- Leakage rule: the pipeline is fitted on train windows only; validation is prediction-only.

## Legacy validation

Accuracy: **0.699878**  
Balanced accuracy: **0.696407**  
PCA components: 67

Confusion matrix, labels `[unfocus, focus]`:

```text
[[1315, 475],
 [ 510, 982]]
```

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| unfocus | 0.720548 | 0.734637 | 0.727524 | 1790 |
| focus | 0.673988 | 0.658177 | 0.665988 | 1492 |
| macro avg | 0.697268 | 0.696407 | 0.696756 | 3282 |

### Validation group metrics

| Group | True unfocus/focus | Pred unfocus/focus | Windows | Accuracy |
|---|---:|---:|---:|---:|
| legacy_lyc_mixed_01 | 299 / 299 | 509 / 89 | 598 | 0.638796 |
| legacy_lyc_mixed_03 | 299 / 299 | 287 / 311 | 598 | 0.939799 |
| legacy_lyc_run_01 | 596 / 298 | 529 / 365 | 894 | 0.678971 |
| legacy_lyc_run_02 | 596 / 298 | 393 / 501 | 894 | 0.620805 |
| legacy_lyc_run_09 | 0 / 298 | 107 / 191 | 298 | 0.640940 |

## Freeze identity and artifacts

- Baseline version: `legacy_baseline_v0`.
- Pre-LOCKED_TEST snapshot commit: `431f6c63c2e0f1461e67bf5f49b18a68b45b916d`.
- `freeze_manifest.json` records the artifact hashes and the original artifact-generation HEAD; it was intentionally not rewritten after the snapshot commit.
- `pipeline.joblib`: complete fitted Scaler/PCA/SVC.
- `config.json`: frozen data, split, preprocessing, features, PCA, and SVC configuration.
- `split.csv`: manifest rows and deterministic split assignment.
- `validation_predictions.csv`: window-level validation predictions.
- `validation_group_metrics.csv`: group-level validation summaries.
- `validation_metrics.json`: machine-readable validation metrics.
- `freeze_manifest.json`: version, git/hash provenance, and freeze timestamp.
- `run_summary.json`: run summary.

