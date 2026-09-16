# EEGEngagement migration inventory

状态：`DRAFT / UNCOMMITTED`。本清单只盘点现有文件；本轮没有创建 `EEGEngagement`、没有复制数据、没有训练或预测，也没有 push。

- source repository: `EEGAttention`
- branch: `better_train`
- final legacy transition commit: `165501aebcf5ed7ae7ac81356d7824ac91dd4458`
- frozen model source commit: `6a8117b39a882e380d3bcb2b3a2503f34efaacc1`
- frozen model SHA256: `2b7b97f9f2399bcd3595df63a406fd66adfb470edc7f9390d8d67d45431d8e24`

迁移总原则：新库只接收 2026-09-16 以后 Task Engagement 主线继续运行所需的最小集合。原始 EEG 文件在新库仍必须被 Git ignore。9/14 与 9/7 候选只用于 prediction/reference，不默认参与 fit。

## A. MUST MIGRATE

### A1. 2026-09-16 current sessions

以下 7 条 EDF 是新项目的核心起点。所有活动区间、标签、任务、EDF/CSV/DSI/note 哈希已由 `data/current/new_paradigm_v1/session_manifest.csv` 登记；本轮重新计算的 21 个 raw/sidecar 哈希全部与 manifest 相符。

| source path | type | date | subject | purpose / task | activity interval | SHA256 | bytes | destination suggestion | reason |
|---|---|---|---|---|---|---|---:|---|---|
| `data/current/new_paradigm_v1/raw/lyc/lyc_focus_202609161100_raw.edf` | EDF | 2026-09-16 | lyc | focus / 王者荣耀高投入专注 | 0–621.5 s | `b9d30de36284db7a34df4b01a6e65a1e1be51f87dee2ebcd20222b068a4316a4` | 9,702,312 | `data/current/2026-09-16/raw/lyc_focus_202609161100_raw.edf` | bootstrap training session 1/6 |
| `data/current/new_paradigm_v1/raw/lyc/lyc_focus_202609161115_raw.edf` | EDF | 2026-09-16 | lyc | focus / 王者荣耀高投入专注 | 0–535.5 s | `fb0cf4cbbf4f515c4861430c7cc850948e970c8d00968bbae50766981a572967` | 8,360,712 | `data/current/2026-09-16/raw/lyc_focus_202609161115_raw.edf` | bootstrap training session 2/6 |
| `data/current/new_paradigm_v1/raw/lyc/lyc_focus_202609161134_raw.edf` | EDF | 2026-09-16 | lyc | focus / 王者荣耀高投入专注 | 0–286.5 s | `930e432afbedcf5fbd7e1e518bb2d8975fc8d9a3668540e2446addfa423ef8c5` | 4,476,312 | `data/current/2026-09-16/raw/lyc_focus_202609161134_raw.edf` | bootstrap training session 3/6 |
| `data/current/new_paradigm_v1/raw/lyc/lyc_observe_202509161235_raw.edf` | EDF | 2026-09-16 | lyc | observe / 认真观战王者，motor reference | 0–563.0 s | `118a5ae9561a2a02f738844d1317bf75ce87ce52486226c2a67b4a24fb8fb233` | 8,789,712 | `data/current/2026-09-16/raw/lyc_observe_202509161235_raw.edf` | prediction-only active/passive and motor reference |
| `data/current/new_paradigm_v1/raw/lyc/lyc_unfocus_202509161254_raw.edf` | EDF | 2026-09-16 | lyc | unfocus / 王者荣耀低投入不专注 | 0–635.0 s | `872c0746c234bf3be2bdc30bbd5250a0816840bae8672ce14a3e94f9d7d21bdd` | 9,912,912 | `data/current/2026-09-16/raw/lyc_unfocus_202509161254_raw.edf` | bootstrap training session 4/6 |
| `data/current/new_paradigm_v1/raw/lyc/lyc_unfocus_202509161306_raw.edf` | EDF | 2026-09-16 | lyc | unfocus / 王者荣耀低投入不专注 | 0–573.0 s | `22db4a55d8abde4343eebf5e7b3a4f7fe53f8f4091d44d23db0f2a487ebcae89` | 8,945,712 | `data/current/2026-09-16/raw/lyc_unfocus_202509161306_raw.edf` | bootstrap training session 5/6 |
| `data/current/new_paradigm_v1/raw/lyc/lyc_unfocus_202509161316_raw.edf` | EDF | 2026-09-16 | lyc | unfocus / 王者荣耀低投入不专注 | 0–678.0 s | `e27a69728a2cd3e98215eb9d86c1c2812e5abd17da90de06977d157310df7cea` | 10,583,712 | `data/current/2026-09-16/raw/lyc_unfocus_202509161316_raw.edf` | bootstrap training session 6/6 |

文件名中的 `20250916` 是保留的原始命名；EDF/CSV header、保存日期、manifest 与 notes 均确认实际日期为 2026-09-16。迁移时不得静默重命名原始文件，应在 manifest 中保留这一 provenance。

### A2. Manifest, notes, and control metadata

| source path | type | date | subject | purpose | current SHA256 | destination suggestion | reason |
|---|---|---|---|---|---|---|---|
| `data/current/new_paradigm_v1/session_manifest.csv` | CSV manifest | 2026-09-16 | lyc | 7-session authoritative metadata | `5a9ec25cfb3d7d3c6804ac0c506d07f9e3b03840397e46bd334dae33496efa03` | `data/manifest.csv` | labels, roles, paths, intervals and hashes are authoritative |
| `data/current/new_paradigm_v1/notes/20260916_lyc_focus_01.md` | session note | 2026-09-16 | lyc | focus provenance | `89d57b2fa0cea34f2972eb02dd167e7c65faa36048805cd76ba075415b3d5f7f` | `data/current/2026-09-16/notes/20260916_lyc_focus_01.md` | label/task provenance |
| `data/current/new_paradigm_v1/notes/20260916_lyc_focus_02.md` | session note | 2026-09-16 | lyc | focus provenance | `be17325164c4db0d5ea3bd1cdaf9506fc60d14703166626c340f504eeb22a1fc` | `data/current/2026-09-16/notes/20260916_lyc_focus_02.md` | label/task provenance |
| `data/current/new_paradigm_v1/notes/20260916_lyc_focus_03.md` | session note | 2026-09-16 | lyc | focus provenance | `0d53201e3b28bb11df50f49a963164b3f5275609ce5c8f9a52a56691e8de63d3` | `data/current/2026-09-16/notes/20260916_lyc_focus_03.md` | label/task provenance |
| `data/current/new_paradigm_v1/notes/20260916_lyc_observe_01.md` | session note | 2026-09-16 | lyc | observe/control provenance | `2ec90cbd87fe1d531695bbbddb43da6e771eec137ba2c5dd17e23bb5e29d50ce` | `data/current/2026-09-16/notes/20260916_lyc_observe_01.md` | reference role and filename-date discrepancy |
| `data/current/new_paradigm_v1/notes/20260916_lyc_unfocus_01.md` | session note | 2026-09-16 | lyc | unfocus provenance | `3176107f074cd50d8036f433bacdf1aa8f74038a600952bf0defdb65af4cae93` | `data/current/2026-09-16/notes/20260916_lyc_unfocus_01.md` | label/task provenance |
| `data/current/new_paradigm_v1/notes/20260916_lyc_unfocus_02.md` | session note | 2026-09-16 | lyc | unfocus provenance | `20fcb8f2786aa33fa909e0a99b723a3a14de79fafe8b8d49820899ecfe566230` | `data/current/2026-09-16/notes/20260916_lyc_unfocus_02.md` | label/task provenance |
| `data/current/new_paradigm_v1/notes/20260916_lyc_unfocus_03.md` | session note | 2026-09-16 | lyc | unfocus provenance | `74de67045984bc2e977f99c622dfea87af22771b6c6f1e8228ad5727aad45c00` | `data/current/2026-09-16/notes/20260916_lyc_unfocus_03.md` | label/task provenance |
| `data/current/new_paradigm_v1/control_experiment_log_template.csv` | metadata template | current | N/A | control experiment schema | `4d94185fea8bc1402ccc7209422918da254e711831502865d6a41df34c816e33` | `data/control_experiment_log_template.csv` | preserves planned/actual condition and confound metadata fields |

### A3. Bootstrap/reference baseline artifacts

Only the compact provenance and aggregate evaluation set should migrate. `window_predictions.csv`, `observe_predictions.csv`, the complete historical replay window tree and old artifact trees remain in EEGAttention.

| source path | type | purpose | current SHA256 | bytes | destination suggestion | reason |
|---|---|---|---|---:|---|---|
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/binary_model.joblib` | model | bootstrap/reference inference | `2b7b97f9f2399bcd3595df63a406fd66adfb470edc7f9390d8d67d45431d8e24` | 247,853 | `artifacts/bootstrap_baseline/binary_model.joblib` | only model approved for continued use |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/config.json` | config | preprocessing, channel and estimator specification | `a88db15b292574ad4f283f3255834214c60d4dcb1ceab5ef1dfa3d9126b91e24` | 2,497 | `artifacts/bootstrap_baseline/config.json` | required feature order and pipeline contract |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/baseline_freeze_manifest.json` | manifest | freeze provenance | `42b5f46fecf5f2f9713d3124af37ccc047a6e3005704f73c7fd5e7e722ec1fd2` | 1,523 | `artifacts/bootstrap_baseline/baseline_freeze_manifest.json` | model/source commit and artifact integrity |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/run_manifest.json` | manifest | complete first-pass run provenance | `5dd1ba2bebbb887a0bb0d56bcb94c591d1a1218b6eed068130507d1c5944b292` | 1,650 | `artifacts/bootstrap_baseline/run_manifest.json` | records freeze-before-observe and artifact hashes |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/input_sessions.csv` | provenance table | six fit sessions | `4781c20609dbdca7f5cb115d720a946ad2fa564c5b39ebbad7efe811b423f28e` | 1,779 | `artifacts/bootstrap_baseline/input_sessions.csv` | explicit training scope |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/fold_metrics.csv` | metrics | LOSO session metrics | `182ccba618f4eb2913e0e8e49019bcb4f2b9892dfaf8b348566f6cf83ebce72d` | 2,047 | `artifacts/bootstrap_baseline/fold_metrics.csv` | compact evaluation evidence |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/fold_confusion_matrices.csv` | metrics | per-fold confusion matrices | `eecf0f47c1ccdc038acd6fdc1f28576aa5e79ba8fd421eee02f2e328206fdcac` | 1,089 | `artifacts/bootstrap_baseline/fold_confusion_matrices.csv` | compact evaluation evidence |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/overall_metrics.json` | metrics | aggregate LOSO result | `618767ab754011173ab896cb91cbbfaaf98374ca73e963f2b5950cedcb6de5e8` | 561 | `artifacts/bootstrap_baseline/overall_metrics.json` | single-day exploratory baseline summary |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/session_confusion_matrix.csv` | metrics | session confusion matrix | `03df4d64b8a853bbd48d29de9553773b3f4e6da4ebcd4ae5a20835f5ebfbf2c0` | 50 | `artifacts/bootstrap_baseline/session_confusion_matrix.csv` | session-level evidence |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/window_confusion_matrix.csv` | metrics | window confusion matrix | `b93560cd7ba1946ecd942db4d888be21d43c5798354bd4f5b50defe988d6d016` | 55 | `artifacts/bootstrap_baseline/window_confusion_matrix.csv` | reproducible aggregate, without all window rows |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/observe_summary.json` | prediction summary | observe prediction-only outcome | `d5d2ab4c85fdce7e35bca772bd0be3f99deda2a0a9fa1cbce0bd97c596a2c45d` | 947 | `artifacts/bootstrap_baseline/observe_summary.json` | motor/active-passive reference summary |

### A4. Documents to migrate or rewrite

| source path | type | destination suggestion | action |
|---|---|---|---|
| `docs/current/ENGAGEMENT_CONTROL_ROADMAP.md` | research roadmap | `docs/control-experiments.md` | migrate and rename; remains the control ladder source |
| `docs/current/NEW_PARADIGM_V1.md` | research positioning | `docs/research-roadmap.md` | rewrite around EEGEngagement; remove legacy navigation |
| `docs/current/DATA_PROTOCOL_V2.md` | collection protocol | `docs/data-protocol.md` | migrate applicable collection, split and holdout rules |
| `docs/progress/EEG项目推进简报_2026-09-16.md` | historical snapshot | `docs/history-and-provenance.md` | summarize/link; do not copy the whole progress tree |

## B. REFERENCE MIGRATION CANDIDATES

All entries below are `prediction/reference only; not default training`.

### B1. 2026-09-14 lyc Honor of Kings

The filenames, `metadata.csv`, shared lyc notes and historical replay report agree that all seven sessions are lyc playing 王者荣耀/排位. Six focus rows share the explicit high-concentration note; the unfocus row is explicitly described as still playing but relaxed/not tense. This is enough for task-domain reference, but not for semantic equivalence to New Paradigm v1.

| source EDF | label | task evidence | SHA256 | bytes | destination suggestion | use |
|---|---|---|---|---:|---|---|
| `data/exploratory/lab_feedback/2026-09-14/lyc_focus_202609141641_raw.edf` | focus | 玩王者 / 排位 | `0729a05a942aca6f091afa15af91d5a1d5a29dd5f66419fdd759940c57dfeb52` | 14,631,912 | `data/reference/2026-09-14/lyc_focus_202609141641_raw.edf` | historical replay / domain-session drift |
| `data/exploratory/lab_feedback/2026-09-14/lyc_focus_202609141702_raw.edf` | focus | 玩王者 / 排位 | `e15db6359124ca7ca69fdba483bf862c80aa7185ca3870ba0f587bf0fb4acd04` | 11,036,112 | `data/reference/2026-09-14/lyc_focus_202609141702_raw.edf` | historical replay / domain-session drift |
| `data/exploratory/lab_feedback/2026-09-14/lyc_focus_202609141717_raw.edf` | focus | 玩王者 / 排位 | `5efe932729caf83e6a28997e7524fdcf7047417a1f5993ce4a0a18b9fe56e244` | 12,455,712 | `data/reference/2026-09-14/lyc_focus_202609141717_raw.edf` | historical replay / domain-session drift |
| `data/exploratory/lab_feedback/2026-09-14/lyc_focus_202609141800_raw.edf` | focus | 玩王者 / 排位 | `1cab948410c450dc31ee1bf69fb3d9f237d9c73f6581dccdc5792562bd6b68fb` | 19,834,512 | `data/reference/2026-09-14/lyc_focus_202609141800_raw.edf` | historical replay / domain-session drift |
| `data/exploratory/lab_feedback/2026-09-14/lyc_unfocus_202609141825_raw.edf` | unfocus | 玩王者 / 排位；放松、不紧张 | `232a676394896075ea748bcf061661ebf486a926f025ee9e53342df6c052e903` | 17,783,112 | `data/reference/2026-09-14/lyc_unfocus_202609141825_raw.edf` | task consistency and domain drift; not in strict high-engagement subset |
| `data/exploratory/lab_feedback/2026-09-14/lyc_focus_202609141959_raw.edf` | focus | 玩王者 / 排位 | `c56eecad75fd050d6b9099ff2e0f20601684729c2e54cbe9c75ea8eabff15cf4` | 3,399,912 | `data/reference/2026-09-14/lyc_focus_202609141959_raw.edf` | historical replay / domain-session drift |
| `data/exploratory/lab_feedback/2026-09-14/lyc_focus_202609142023_raw.edf` | focus | 玩王者 / 排位 | `20a5b6d253c6948bad798924cf574bb94fb1658455f3bb975f2de9fa7e697db0` | 10,880,112 | `data/reference/2026-09-14/lyc_focus_202609142023_raw.edf` | historical replay / domain-session drift |

Supporting provenance stays available at `data/exploratory/lab_feedback/2026-09-14/metadata.csv`, `data/exploratory/lab_feedback/2026-09-14/lyc_foucs_20260914.md`, `data/exploratory/lab_feedback/2026-09-14/lyc_unfoucs_20260914.md`, and `artifacts/current/new_paradigm_v1/2026-09-16_lyc_historical_game_replay/REPORT.md`. When migration is approved, create a seven-row reference subset in the new manifest instead of copying the entire 11-row historical-pilot metadata file.

### B2. 2026-09-07 lyc Honor of Kings

| source EDF | label | task evidence | activity interval | SHA256 | bytes | destination suggestion | use |
|---|---|---|---|---|---:|---|---|
| `data/locked/2026-09-07/lyc_focus_202609072034_raw.edf` | focus | `data/session_manifest.csv` says 王者荣耀专注录制 | 30.0–599.5 s | `6ebb9ebd1350d5b54521a776a60dec86d76fe4958b9d87b4d4684735e7635111` | 9,827,112 | `data/reference/2026-09-07/lyc_focus_202609072034_raw.edf` | historical replay / cross-day reference |

The other 9/7 lyc focus/unfocus sessions are classroom-video tasks and the rest session is not a gaming task; they stay in EEGAttention.

## C. CODE DEPENDENCIES

### Dependency trace

`run_new_paradigm_first_pass.py` imports `legacy_baseline_v0.py` for constants, band order and `build_baseline_pipeline`, and imports `eeg_pipeline_utils.py` for EDF loading, preprocessing/feature extraction, hashing and output helpers.

`replay_lyc_historical_gaming.py` loads the frozen model/config/manifests, reuses the same two modules, and additionally reads three legacy manifests and hard-coded historical paths. It is therefore evidence for the old run, not a clean new-project inference entry point.

| source | imported by | direct dependencies | migration classification | destination / extraction plan |
|---|---|---|---|---|
| `scripts/eeg_pipeline_utils.py` | first-pass, replay, legacy baseline and other old pipelines | `mne`, `numpy`, `scipy.signal.welch` | `MIGRATE_CORE` | split `load_eeg_recording` into `io/edf.py`; `preprocess_eeg`/`make_windows` into `preprocessing/`; bandpower functions into `features/`; keep hash helpers in manifest/provenance utilities |
| `scripts/legacy_baseline_v0.py` | first-pass and replay | `eeg_pipeline_utils`, `numpy`, `pandas`, `joblib`, `scikit-learn` | `MIGRATE_AFTER_REFACTOR` | extract only BANDS/order, window/filter constants and Scaler→PCA→SVC construction into `models/bootstrap.py`; do not copy legacy training CLI |
| `scripts/validate_new_paradigm_data.py` | standalone validator | stdlib CSV/hash/EDF-header parsing | `MIGRATE_AFTER_REFACTOR` | parameterize root/schema and move to `scripts/validate_data.py` or package validator |
| `scripts/run_new_paradigm_first_pass.py` | standalone historical experiment | the two modules above, `joblib`, `numpy`, `pandas`, sklearn metrics | `REFERENCE_ONLY` | keep as frozen experiment evidence; future runners must not hard-code six IDs or old artifact paths |
| `scripts/replay_lyc_historical_gaming.py` | standalone historical replay | frozen artifacts, old manifests, the two modules above, `joblib`, `mne`, `numpy`, `pandas`, `scipy`, `sklearn` | `REFERENCE_ONLY` | use as behavioral specification for a new generic prediction-only utility; do not copy its legacy path coupling |

No old notebook, compatibility script or complete `scripts/` tree is a required import of the new core.

### Frozen model portability

The joblib begins with `sklearn.pipeline.Pipeline`; embedded globals found in the artifact are limited to sklearn (`Pipeline`, `StandardScaler`, `PCA`, `SVC`) and NumPy. No `eeg_pipeline_utils`, `legacy_baseline_v0`, `EEGAttention`, or `__main__` class path is embedded. Therefore the model is structurally independent of the old repository's Python module paths.

It is not dependency-free. The recorded successful replay runtime was Python 3.12.13, joblib 1.5.3, NumPy 2.5.1, pandas 3.0.5, SciPy 1.18.0, MNE 1.12.1 and scikit-learn 1.9.0. The currently available clean Codex runtimes do not contain joblib/sklearn, so this round could not perform a second clean-environment `joblib.load`. A load + one-session prediction smoke test in a pinned environment is a mandatory acceptance gate for the future migration.

## D. KEEP IN EEGAttention

| existing source path / class | classification | reason |
|---|---|---|
| `data/legacy/` | `KEEP_IN_LEGACY` | July legacy recordings, multiclass and mixed datasets are historical and show major source/date drift |
| `data/reference/` | `KEEP_IN_LEGACY` | author/reference source data are not part of the current personal engagement line |
| `data/locked/2026-09-07/` except the one candidate in B2 | `KEEP_IN_LEGACY` | classroom video, rest and unrelated subjects/tasks |
| `data/exploratory/lab_feedback/2026-09-14/` except the seven candidate EDFs and their subset provenance | `KEEP_IN_LEGACY` | other subjects/tasks and the complete old feedback archive |
| `data/current/new_paradigm_v1/raw/lyc/lyc_focus_202609161010.dsi` | `KEEP_IN_LEGACY` | orphan 15.64 MiB DSI sidecar; no matching EDF/CSV or manifest session, and no current pipeline use |
| `artifacts/legacy/`, `artifacts/legacy_baseline_v0/`, `artifacts/locked_test/` | `KEEP_IN_LEGACY` | old pooled and locked-test history |
| `artifacts/subject_models/`, `artifacts/subject_model_comparison/`, `artifacts/subject_model_diagnostics/` | `KEEP_IN_LEGACY` | old personal models and diagnostics |
| `artifacts/common6_compatibility/`, `artifacts/our_common6_models/`, `artifacts/our_common7_models/`, `artifacts/mixed_models/` | `KEEP_IN_LEGACY` | old compatibility/common-channel experiments |
| `artifacts/upstream_author/`, `artifacts/author_models/`, `artifacts/reproductions/` | `KEEP_IN_LEGACY` | upstream reproduction and author models |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass/window_predictions.csv` and `observe_predictions.csv` | `KEEP_IN_LEGACY` | aggregate metrics and observe summary are sufficient for bootstrap provenance |
| `artifacts/current/new_paradigm_v1/2026-09-16_lyc_historical_game_replay/` | `KEEP_IN_LEGACY` | complete replay remains historical evidence; new repo only needs selected reference EDFs and a provenance summary |
| `notebooks/` | `KEEP_IN_LEGACY` | old four-class, reproduction, tutorial and quick-test notebooks are not production dependencies |
| `scripts/legacy/`, `scripts/annotated/` and old compatibility/evaluation scripts | `KEEP_IN_LEGACY` | no direct import from the proposed engagement core |
| `docs/EXPERIMENT_MAP.md`, `docs/MODEL_CATALOG.md`, `docs/LAB_FEEDBACK_HANDOFF.md`, most of `docs/progress/` | `KEEP_IN_LEGACY` | preserve complete history here; new repo should link through one concise provenance document |

## E. OPEN QUESTIONS / RISKS

1. **CSV is not required by the current model path.** The active pipeline calls MNE on EDF; it does not read raw CSV for features or inference. The seven 9/16 CSVs add 190.57 MiB, the seven 9/14 candidates add 278.11 MiB and the 9/7 candidate adds 30.68 MiB. Default: retain in EEGAttention/external raw archive, preserve their hashes in provenance, and migrate only if new QA requires device time-series columns absent from EDF.
2. **DSI is not required by the current model path.** It is a vendor sidecar for acquisition provenance. The corresponding sizes are 71.38 MiB, 105.70 MiB and 11.54 MiB. Default: retain in EEGAttention/external raw archive; migrate only for acquisition-forensics or vendor re-export requirements.
3. **Model load depends on compatible third-party packages.** It does not depend on old project modules, but scikit-learn/joblib pickle compatibility is not a long-term serialization guarantee. Pin the recorded environment first, then run `joblib.load`, check `n_features_in_=240`, classes and a known-session prediction.
4. **Feature ordering is split across sources.** Channel order and feature contract are in `config.json`; band insertion order and estimator construction currently live in `legacy_baseline_v0.py`. The new package must consolidate these into one versioned model spec and test exact 240-feature ordering.
5. **Current scripts contain legacy path coupling.** The first-pass script hard-codes the seven 9/16 IDs and output path; replay reads old manifests and legacy notebooks. They must not become the new generic experiment API unchanged.
6. **Manifest schema for absent sidecars must be decided.** If CSV/DSI are not copied, the new manifest should use explicit optional/external-source fields rather than stale local paths.
7. **9/14 semantics are historical.** The shared notes verify task and state description, but feedback round, device/wear notes and semantic equivalence to New Paradigm v1 remain unknown.
8. **Raw data must stay ignored.** New repository `.gitignore` must exclude EDF/CSV/DSI before any transfer; metadata, notes and hashes may be tracked.
9. **One orphan DSI exists.** `lyc_focus_202609161010.dsi` has SHA256 `ea403ff651baaa13c2a433ab7a22aa45c069a5b004342b98cd84c2abe402ec77`, but no matching EDF/CSV or manifest row. It is explicitly excluded from migration unless later provenance evidence establishes a valid session.

## Recommended initial repository structure

```text
EEGEngagement/
├── README.md
├── pyproject.toml
├── docs/
│   ├── research-roadmap.md
│   ├── control-experiments.md
│   ├── data-protocol.md
│   ├── history-and-provenance.md
│   └── progress/
├── data/
│   ├── current/2026-09-16/
│   │   ├── raw/
│   │   └── notes/
│   ├── reference/
│   │   ├── 2026-09-14/
│   │   └── 2026-09-07/
│   ├── manifest.csv
│   ├── control_experiment_log_template.csv
│   └── README.md
├── src/eeg_engagement/
│   ├── io/
│   ├── preprocessing/
│   ├── features/
│   ├── models/
│   ├── inference/
│   └── validation/
├── experiments/
│   ├── cross_day/
│   ├── motor_control/
│   ├── active_passive/
│   ├── cross_task/
│   └── internal_state/
├── dashboard/
├── artifacts/bootstrap_baseline/
├── scripts/
└── tests/
```

## Size estimate

| scope | size |
|---|---:|
| 9/16 seven EDFs | 57.96 MiB |
| 9/16 EDFs + manifest + seven notes + selected compact artifacts | 58.22 MiB |
| seven 9/14 candidate EDFs | 85.85 MiB |
| one 9/7 candidate EDF | 9.37 MiB |
| recommended data/artifact set, including all candidate EDFs | 153.44 MiB |
| same scope with every matching raw CSV and DSI sidecar | 841.43 MiB |

Code and selected documents add well under 0.2 MiB, so a practical estimate for the recommended minimal migration is approximately **154 MiB**, versus approximately **842 MiB** if all CSV/DSI sidecars are also copied.

## Approval gate for the next round

Do not commit this inventory yet. After scope confirmation, the next operation should be: create EEGEngagement, establish `.gitignore` and dependency pins, copy the approved minimum set, validate every hash, perform an independent model load/prediction smoke test, then begin Dashboard work.
