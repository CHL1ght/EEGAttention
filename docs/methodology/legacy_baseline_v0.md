# legacy_baseline_v0 状态说明

## 当前结论

`legacy_baseline_v0 = FROZEN`（2026-09-13）。本轮只读取 `data/legacy_manifest.csv` 中的 `legacy_baseline_candidate`，未读取或测试 `data/locked/2026-09-07/`；LOCKED_TEST 仍未执行。

正式入口为 [`scripts/legacy_baseline_v0.py`](../../scripts/legacy_baseline_v0.py)，冻结产物位于 [`artifacts/legacy_baseline_v0/`](../../artifacts/legacy_baseline_v0/)。历史 Notebook 仍只作为实现依据和追溯记录。

## 数据身份与分组

- 数据版本：`legacy_dataset_v0`。
- candidate：43 个 manifest 行、34 个 `source_recording_id`、22 个 `session_group_id`；`focus` 22 行、`unfocus` 21 行。
- 标签只依据 manifest：`focus → focus`、`iu/ou → unfocus`；`rest/daze`、demo 和非 candidate 排除。
- 先在完整 `session_group_id` 上用固定 `RandomState(42)` 随机排列，取 `ceil(20% × 22) = 5` 个 group 做 validation，再读取 EDF、切逻辑 segment 和窗口。
- train：17 个 group、25 个 source；validation：5 个 group、9 个 source；两侧 `session_group_id` 与 `source_recording_id` 交集均为 0。
- validation groups：`legacy_lyc_mixed_01`、`legacy_lyc_mixed_03`、`legacy_lyc_run_01`、`legacy_lyc_run_02`、`legacy_lyc_run_09`。

## 冻结配置

配置完整记录在 [`config.json`](../../artifacts/legacy_baseline_v0/config.json)。实际采用：

- EDF：`mne.io.read_raw_edf(preload=True, infer_types=True)`；保留 MNE 识别的 24 个 EEG 通道，保持 EDF 中的通道顺序；非 128 Hz 时重采样至 128 Hz。
- 预处理：按 manifest segment 逐段做 MNE FIR `firwin` 带通，`0.5–43 Hz`。
- 窗口：4 s，step 2 s。
- 特征：逐通道 Welch，`nperseg = min(window_samples, 2 × sfreq)`；delta `(1,4)`、theta `(4,8)`、alpha `(8,13)`、beta `(13,30)`、gamma `(30,43)` Hz；每个频段保存 log 绝对功率和相对功率，共 240 维。
- 模型：`StandardScaler → PCA(n_components=0.95, random_state=42) → SVC(kernel='rbf', C=10, gamma='scale', class_weight='balanced', probability=True, random_state=42)`。
- 防泄漏：脚本中唯一的模型拟合为 `pipeline.fit(X_train, y_train)`；validation 只调用 `pipeline.predict(X_val)`。

## Legacy validation

- train windows：9,736；validation windows：3,282。
- accuracy：`0.699878`。
- confusion matrix（行/列顺序 `unfocus, focus`）：`[[1315, 475], [510, 982]]`。
- macro F1：`0.696756`；unfocus F1：`0.727524`；focus F1：`0.665988`。

各 validation group 的窗口数和 group accuracy 保存在 [`validation_group_metrics.csv`](../../artifacts/legacy_baseline_v0/validation_group_metrics.csv)，逐窗口真值/预测保存在 [`validation_predictions.csv`](../../artifacts/legacy_baseline_v0/validation_predictions.csv)。

## 冻结产物

`artifacts/legacy_baseline_v0/` 至少包含：

- `pipeline.joblib`：完整 Scaler、PCA、SVC。
- `config.json`：数据、标签、预处理、特征、PCA、SVC 和 split 配置。
- `split.csv`：manifest 行到 train/validation 的确定性分配。
- `validation_predictions.csv`、`validation_group_metrics.csv`、`validation_metrics.json`：Legacy validation 结果。
- `freeze_manifest.json`：git HEAD、manifest SHA-256、各冻结文件 SHA-256、版本和冻结时间。
- `run_summary.json`：本次运行汇总。

## 里程碑口径

- `00.1` Legacy 数据封存：已完成。
- `00.2` 预处理/特征/PCA/SVC 冻结：已完成。
- `00.3` 完整 recording/session 隔离：已完成并由脚本断言。
- LOCKED_TEST 数据封存：已完成。
- 首次独立盲测：未执行；只有用户明确开始下一阶段后才运行。
