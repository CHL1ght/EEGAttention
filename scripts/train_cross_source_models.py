"""Train author-only and channel-compatible cross-source models.

The author-only model is trained from the 23 recording files selected by the
checked-in author notebook.  The common-7 and common-6 variants use explicit
channel adapters and never read LOCKED_TEST for fit statistics.  Common-6 is
channel-aligned by the ACNS/DSI-24 nomenclature evidence, but cross-source
results remain exploratory because the author MAT reference is unknown.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import GroupKFold

import legacy_baseline_v0 as baseline
from cross_source_utils import (
    AUTHOR_RECORD_IDS,
    COMMON_6_CHANNELS,
    COMMON_7_CHANNELS,
    author_block_manifest,
    build_source_feature_dataset,
    inspect_author_mat_files,
    inspect_common6_edf_paths,
    inspect_common7_edf_paths,
)
from eeg_pipeline_utils import save_dataframe, save_json, sha256_file


MODEL_VERSION = "cross_source_models_v1"
AUTHOR_COMMON6_MODEL_DIR = "author_models/author_common6"
OUR_COMMON7_MODEL_DIR = "our_common7_models/pooled_common7"
OUR_COMMON6_MODEL_DIR = "our_common6_models/pooled_common6"
MIXED_MODEL_DIR = "mixed_models/our_author_mixed"
MIXED_COMMON6_MODEL_DIR = "mixed_models/our_author_mixed_common6"


def channel_config(channel_set: str) -> dict[str, Any]:
    if channel_set == "common6":
        return {
            "channels": COMMON_6_CHANNELS,
            "mapping": {
                "F7-Pz": "F7",
                "F3-Pz": "F3",
                "T5-Pz": "P7",
                "O1-Pz": "O1",
                "O2-Pz": "O2",
                "T6-Pz": "P8",
            },
            "reference_compatibility": "uncertain; author MAT reference unknown",
        }
    if channel_set == "common7":
        return {
            "channels": COMMON_7_CHANNELS,
            "mapping": "existing explicit common7 aliases; no T5/T6 substitution",
            "reference_compatibility": "not assessed for cross-source common7",
        }
    raise ValueError(f"Unsupported channel set: {channel_set}")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def _safe_balanced_accuracy(true: np.ndarray, predicted: np.ndarray) -> float | None:
    if len(np.unique(true)) < 2:
        return None
    return float(balanced_accuracy_score(true, predicted))


def group_kfold_validation(
    X: np.ndarray,
    y: np.ndarray,
    metadata: pd.DataFrame,
    *,
    n_splits: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fit only on train groups and return fold, summary, and predictions."""
    groups = metadata["session_group_id"].to_numpy()
    unique_groups = np.unique(groups)
    if len(unique_groups) < n_splits:
        raise ValueError(f"Need at least {n_splits} recording groups, got {len(unique_groups)}")
    fold_rows: list[dict[str, Any]] = []
    prediction_rows: list[pd.DataFrame] = []
    splitter = GroupKFold(n_splits=n_splits)
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, groups=groups), start=1):
        if set(y[train_idx]) != set(baseline.LABELS):
            raise AssertionError(f"GroupKFold fold {fold} train side lacks a class")
        pipeline = baseline.build_baseline_pipeline()
        pipeline.fit(X[train_idx], y[train_idx])
        predicted = np.asarray(pipeline.predict(X[test_idx]))
        true = y[test_idx]
        balanced = _safe_balanced_accuracy(true, predicted)
        fold_rows.append(
            {
                "fold": fold,
                "train_recordings": int(len(np.unique(groups[train_idx]))),
                "held_out_recordings": int(len(np.unique(groups[test_idx]))),
                "train_windows": int(len(train_idx)),
                "held_out_windows": int(len(test_idx)),
                "held_out_session_groups": ",".join(sorted(np.unique(groups[test_idx]))),
                "accuracy": float(accuracy_score(true, predicted)),
                "balanced_accuracy": balanced,
                "balanced_accuracy_applicable": balanced is not None,
                "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
            }
        )
        prediction_columns = [
            "recording_id", "source_recording_id", "session_group_id",
            "canonical_label", "window_start_sec", "sfreq_hz",
        ]
        prediction_columns.extend(
            column for column in ("source", "subject_id") if column in metadata.columns
        )
        fold_predictions = metadata.iloc[test_idx][prediction_columns].copy()
        fold_predictions.insert(0, "fold", fold)
        fold_predictions.insert(1, "true_label", true)
        fold_predictions.insert(2, "predicted_label", predicted)
        prediction_rows.append(fold_predictions)

    folds = pd.DataFrame(fold_rows)
    balanced_values = folds["balanced_accuracy"].dropna().astype(float)
    summary = pd.DataFrame([
        {
            "evaluation": "group_kfold",
            "folds": int(len(folds)),
            "accuracy_mean": float(folds["accuracy"].mean()),
            "accuracy_std": float(folds["accuracy"].std(ddof=1)) if len(folds) > 1 else 0.0,
            "balanced_accuracy_valid_folds": int(len(balanced_values)),
            "balanced_accuracy_mean": float(balanced_values.mean()) if len(balanced_values) else None,
            "balanced_accuracy_std": float(balanced_values.std(ddof=1)) if len(balanced_values) > 1 else (0.0 if len(balanced_values) else None),
            "balanced_accuracy_note": "N/A when a held-out group has one true class",
        }
    ])
    return folds, summary, pd.concat(prediction_rows, ignore_index=True)


def _model_config(
    *,
    repo_root: Path,
    model_type: str,
    rows: pd.DataFrame,
    X: np.ndarray,
    pipeline: Any,
    validation_summary: pd.DataFrame,
    validation_method: str,
    output_dir: Path,
    channel_set: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    channels = channel_config(channel_set)["channels"]
    return {
        "model_version": MODEL_VERSION,
        "model_type": model_type,
        "labels": list(baseline.LABELS),
        "source_scope": {
            "rows": int(len(rows)),
            "recordings": int(rows["source_recording_id"].nunique()),
            "session_groups": int(rows["session_group_id"].nunique()),
            "windows": int(len(X)),
            "blocks_by_label": rows.groupby("canonical_label")["recording_id"].nunique().to_dict(),
            "paths": [str(value) for value in rows["edf_path"].drop_duplicates().tolist()],
        },
        "feature_protocol": {
            "shared_module": "scripts/eeg_pipeline_utils.py",
            "channel_set": channel_set,
            "channels": list(channels),
            "channel_mapping": channel_config(channel_set)["mapping"],
            "raw_feature_dimension": int(X.shape[1]),
            "target_sampling_rate_hz": 128.0,
            "filter_hz": [baseline.FILTER_L_HZ, baseline.FILTER_H_HZ],
            "window_step_sec": [baseline.WINDOW_SEC, baseline.STEP_SEC],
            "welch_bands_hz": {name: list(bounds) for name, bounds in baseline.BANDS.items()},
        },
        "pca": {
            "requested": baseline.PCA_N_COMPONENTS,
            "fitted_components": int(pipeline.named_steps["pca"].n_components_),
            "explained_variance_ratio_sum": float(np.sum(pipeline.named_steps["pca"].explained_variance_ratio_)),
        },
        "svc": baseline.SVC_PARAMS,
        "final_fit_scope": "all listed non-LOCKED_TEST source rows",
        "validation": {
            "method": validation_method,
            **validation_summary.iloc[0].to_dict(),
        },
        "locked_test_read": False,
        "reference_compatibility": channel_config(channel_set)["reference_compatibility"],
        "output_dir": str(output_dir.relative_to(repo_root)).replace("\\", "/"),
        "git_head": _git_head(repo_root),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        **(extra or {}),
    }


def train_author_only(
    repo_root: Path,
    output_dir: Path,
    *,
    channel_set: str = "common7",
    model_type: str = "author_only",
) -> dict[str, Any]:
    """Train an author-only model with the shared recording-level pipeline."""
    channels = channel_config(channel_set)["channels"]
    rows = author_block_manifest(repo_root, split="train")
    X, y, metadata = build_source_feature_dataset(rows, channel_set=channel_set)
    if X.shape[1] != len(channels) * len(baseline.BANDS) * 2:
        raise AssertionError(f"Unexpected author {channel_set} feature shape: {X.shape}")
    folds, validation_summary, validation_predictions = group_kfold_validation(X, y, metadata, n_splits=5)

    # This is the final author-only artifact: fit on author data only, after
    # the recording-held-out diagnostic has been completed.
    pipeline = baseline.build_baseline_pipeline()
    pipeline.fit(X, y)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "pipeline.joblib"
    joblib.dump(pipeline, model_path)
    save_dataframe(output_dir / "train_manifest.csv", rows.drop(columns=["edf_path_abs"]))
    save_dataframe(output_dir / "mat_inspection.csv", inspect_author_mat_files(repo_root))
    save_dataframe(output_dir / "validation_fold_metrics.csv", folds)
    save_dataframe(output_dir / "validation_predictions.csv", validation_predictions)
    confusion = confusion_matrix(
        validation_predictions["true_label"],
        validation_predictions["predicted_label"],
        labels=list(baseline.LABELS),
    )
    save_dataframe(
        output_dir / "validation_confusion_matrix.csv",
        pd.DataFrame(confusion, index=baseline.LABELS, columns=baseline.LABELS)
        .rename_axis("true_label")
        .reset_index(),
    )
    save_json(output_dir / "validation_metrics.json", validation_summary.iloc[0].to_dict())
    config = _model_config(
        repo_root=repo_root,
        model_type=model_type,
        rows=rows,
        X=X,
        pipeline=pipeline,
        validation_summary=validation_summary,
        validation_method="GroupKFold(n_splits=5), group=session_group_id/author recording",
        output_dir=output_dir,
        channel_set=channel_set,
        extra={
            "channel_set": channel_set,
            "author_record_ids": list(AUTHOR_RECORD_IDS),
            "author_label_blocks": "each recording: [0,600)s focus and [600,1200)s unfocus",
            "mat_structure": {
                "top_level_struct": "o",
                "data_field": "o.data",
                "author_data_slice": "o.data[:20*128*60, 3:17]",
                "source_channel_count": 14,
                "source_channel_order": [
                    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2",
                    "P8", "T8", "FC6", "F4", "F8", "AF4",
                ],
                "sampling_rate_hz": 128.0,
            },
            "original_notebook_audit": {
                "label_construction": "first 10 minutes focus; next 10 minutes unfocus",
                "preprocessing": "BaselineRemoval.IModPoly then Butterworth 0.2–43 Hz",
                "features": "STFT nperseg=128, nfft=1024, noverlap=0; 36 frequency bins × 7 channels; 15-frame sliding average; 252 features (historical notebook)",
                "split": "train_test_split(X, y, test_size=0.2, random_state=42) after concatenating windows across recordings",
                "window_level_leakage": True,
                "scaler_pca_fit_scope": "train split only in the checked-in notebook",
            },
            "locked_test_read": False,
            "cross_source_scope": "exploratory; author MAT reference remains unknown",
            "pipeline_sha256": sha256_file(model_path),
        },
    )
    save_json(output_dir / "config.json", config)
    run_manifest = {
        "model_version": MODEL_VERSION,
        "model_type": model_type,
        "input_files": int(rows["edf_path"].nunique()),
        "locked_test_read": False,
        "fit_policy": "validation folds fit on train recordings; final artifact fit on author recordings only",
        "output_sha256": {
            name: sha256_file(output_dir / name)
            for name in (
                "pipeline.joblib", "train_manifest.csv", "validation_fold_metrics.csv",
                "validation_predictions.csv", "validation_confusion_matrix.csv",
                "validation_metrics.json", "config.json", "mat_inspection.csv",
            )
        },
        "git_head": _git_head(repo_root),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "run_manifest.json", run_manifest)
    _write_author_report(output_dir / "REPORT.md", config, rows, folds, validation_summary)
    return config


def _write_author_report(
    path: Path,
    config: dict[str, Any],
    rows: pd.DataFrame,
    folds: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    metric = summary.iloc[0]
    channels = config["feature_protocol"]["channels"]
    channel_set = config["feature_protocol"]["channel_set"]
    is_common6 = channel_set == "common6"
    def pct(value: Any) -> str:
        return "N/A" if value is None or pd.isna(value) else f"{float(value):.2%}"
    lines = [
        "# Author-common6 model" if is_common6 else "# Author-only model",
        "",
        "本模型只使用 `data/reference/original_mat/` 中由上游 notebook 选择的 23 个 author recording。每个 recording 的 `[0, 600)` 秒为 focus、`[600, 1200)` 秒为 unfocus；recording 是最小隔离单位。",
        "",
        f"- common channels: `{', '.join(channels)}`",
        "- common6 EDF adapter: `F7-Pz→F7, F3-Pz→F3, T5-Pz→P7, O1-Pz→O1, O2-Pz→O2, T6-Pz→P8`; `AF4` is intentionally excluded." if is_common6 else "",
        f"- recordings: {rows['source_recording_id'].nunique()}；blocks: {len(rows)}；windows: {int(folds['train_windows'].iloc[0] + folds['held_out_windows'].iloc[0]) if not folds.empty else 'see manifest'}",
        f"- raw feature dimension: {config['feature_protocol']['raw_feature_dimension']}；PCA: {config['pca']['fitted_components']} components",
        f"- GroupKFold accuracy: {pct(metric['accuracy_mean'])} ± {pct(metric['accuracy_std'])}",
        f"- GroupKFold balanced accuracy: {pct(metric['balanced_accuracy_mean'])} ± {pct(metric['balanced_accuracy_std'])} ({int(metric['balanced_accuracy_valid_folds'])} valid folds)",
        "- LOCKED_TEST 未参与任何 fit；跨来源结果仅作 exploratory/channel-aligned comparison，author MAT reference 仍未知。" if is_common6 else "- LOCKED_TEST 未参与任何 fit；该模型的跨 EDF 测试必须等 7 个共同通道完成明确对齐后再进行。",
        "",
        "## MAT structure and original notebook audit",
        "",
        "- 23 个 selected `.mat` 都是顶层 `o` struct，信号在 `o.data`；采样率为 128 Hz，原 notebook 使用 `o.data[:20*128*60, 3:17]` 的 14 列 EEG，并按明确通道名选择 common 7。逐文件结构见 `mat_inspection.csv`。",
        "- 原作者标签构造为每个 recording 前 10 分钟 focus、后 10 分钟 unfocus；当前模型把整个 recording 作为一个 session group。",
        "- 原 notebook 的 `train_test_split(X, y, test_size=0.2, random_state=42)` 是在所有 recording 的窗口拼接之后进行的，因此同一 recording 的窗口可能同时进入 train/test，存在 window-level leakage。",
        "- 原 notebook 的 StandardScaler/PCA/SVC 是对该随机窗口 split 的 train 侧 fit；本模型改用 recording-level GroupKFold，避免同 recording 跨集合。",
        "",
        "## Fold metrics",
        "",
        "| fold | held-out recordings | accuracy | balanced accuracy |",
        "|---:|---:|---:|---:|",
    ]
    for row in folds.itertuples():
        lines.append(f"| {row.fold} | {row.held_out_recordings} | {pct(row.accuracy)} | {pct(row.balanced_accuracy)} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_our_rows(repo_root: Path, manifest_path: Path) -> pd.DataFrame:
    rows = baseline.load_legacy_manifest(manifest_path, repo_root)
    rows = rows.loc[rows["subject_id"].str.casefold().isin(["lyc", "zyf"])].copy()
    rows["source"] = "our"
    rows["split"] = "unassigned"
    if rows.empty:
        raise AssertionError("No lyc/zyf historical candidate rows available")
    return rows


def _blocked_cross_source_model(
    repo_root: Path,
    output_dir: Path,
    model_type: str,
    alignment: pd.DataFrame,
    reason: str,
    channel_set: str,
) -> dict[str, Any]:
    channels = channel_config(channel_set)["channels"]
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dataframe(output_dir / "channel_alignment.csv", alignment)
    blocked = {
        "model_version": MODEL_VERSION,
        "model_type": model_type,
        "status": "blocked",
        "reason": reason,
        "channel_set": channel_set,
        "required_channels": list(channels),
        "locked_test_read_for_fit": False,
        "git_head": _git_head(repo_root),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "BLOCKED.json", blocked)
    (output_dir / "BLOCKED.md").write_text(
        "# Cross-source model blocked\n\n"
        f"{reason}\n\n"
        f"Required explicit channels: `{', '.join(channels)}`.\n"
        "No model was fit and no LOCKED_TEST statistics were used.\n",
        encoding="utf-8",
    )
    return blocked


def train_our_common7_or_mixed(
    repo_root: Path,
    manifest_path: Path,
    output_dir: Path,
    *,
    mixed: bool,
    channel_set: str = "common7",
) -> dict[str, Any]:
    """Train one explicit common-channel pooled or mixed model."""
    channels = channel_config(channel_set)["channels"]
    our_rows = _load_our_rows(repo_root, manifest_path)
    paths = [Path(value) for value in our_rows["edf_path_abs"].drop_duplicates()]
    if mixed:
        session_manifest = pd.read_csv(repo_root / "data" / "session_manifest.csv", dtype=str, keep_default_na=False)
        locked_paths = [
            (repo_root / value).resolve()
            for value in session_manifest.loc[
                (session_manifest["recorded_date"] == "2026-09-07")
                & (session_manifest["dataset_role"] == "locked_test"),
                "edf_path",
            ]
        ]
        paths.extend(locked_paths)
    inspect_alignment = inspect_common6_edf_paths if channel_set == "common6" else inspect_common7_edf_paths
    alignment = inspect_alignment(paths)
    availability_column = f"{channel_set}_available"
    missing_column = f"missing_{channel_set}_channels"
    if not bool(alignment[availability_column].all()):
        missing = sorted({item for value in alignment[missing_column] for item in str(value).split(", ") if item})
        blocked_model_type = (
            "our_author_mixed_common6" if mixed else "our_common6_pooled"
        ) if channel_set == "common6" else (
            "our_author_mixed" if mixed else "our_common7_pooled"
        )
        return _blocked_cross_source_model(
            repo_root,
            output_dir,
            blocked_model_type,
            alignment,
            f"Required {channel_set} channel(s) missing from current EDF layout: {', '.join(missing)}.",
            channel_set,
        )

    if mixed:
        author_rows = author_block_manifest(repo_root, split="train")
        rows = pd.concat([our_rows, author_rows], ignore_index=True)
        rows["split"] = "unassigned"
    else:
        rows = our_rows
    X, y, metadata = build_source_feature_dataset(rows, channel_set=channel_set)
    expected_features = len(channels) * len(baseline.BANDS) * 2
    if X.shape[1] != expected_features:
        raise AssertionError(f"Unexpected {channel_set} feature shape: {X.shape}")
    folds, validation_summary, validation_predictions = group_kfold_validation(X, y, metadata, n_splits=5)
    pipeline = baseline.build_baseline_pipeline()
    pipeline.fit(X, y)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "pipeline.joblib"
    joblib.dump(pipeline, model_path)
    save_dataframe(output_dir / "train_manifest.csv", rows.drop(columns=["edf_path_abs"]))
    save_dataframe(output_dir / "validation_fold_metrics.csv", folds)
    save_dataframe(output_dir / "validation_predictions.csv", validation_predictions)
    confusion = confusion_matrix(
        validation_predictions["true_label"],
        validation_predictions["predicted_label"],
        labels=list(baseline.LABELS),
    )
    save_dataframe(
        output_dir / "validation_confusion_matrix.csv",
        pd.DataFrame(confusion, index=baseline.LABELS, columns=baseline.LABELS)
        .rename_axis("true_label")
        .reset_index(),
    )
    save_json(output_dir / "validation_metrics.json", validation_summary.iloc[0].to_dict())
    config = _model_config(
        repo_root=repo_root,
        model_type=("our_author_mixed_common6" if mixed else "our_common6_pooled")
        if channel_set == "common6"
        else ("our_author_mixed" if mixed else "our_common7_pooled"),
        rows=rows,
        X=X,
        pipeline=pipeline,
        validation_summary=validation_summary,
        validation_method="GroupKFold(n_splits=5), group=session_group_id",
        output_dir=output_dir,
        channel_set=channel_set,
        extra={
            "sources": ["our", "author"] if mixed else ["our"],
            "cross_source_scope": "exploratory; channel-aligned but author MAT reference remains unknown",
            "pipeline_sha256": sha256_file(model_path),
        },
    )
    save_json(output_dir / "config.json", config)
    output_names = [
        "pipeline.joblib",
        "train_manifest.csv",
        "validation_fold_metrics.csv",
        "validation_predictions.csv",
        "validation_confusion_matrix.csv",
        "validation_metrics.json",
        "config.json",
    ]
    save_json(
        output_dir / "run_manifest.json",
        {
            "model_version": MODEL_VERSION,
            "model_type": config["model_type"],
            "channel_set": channel_set,
            "locked_test_read_for_fit": False,
            "fit_policy": "validation folds fit on train groups; final artifact fit on listed non-LOCKED_TEST source rows",
            "output_sha256": {name: sha256_file(output_dir / name) for name in output_names},
            "git_head": _git_head(repo_root),
            "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )
    return config


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=("author-only", "author-common6", "our-common7", "our-common6", "mixed", "mixed-common6"),
        required=True,
    )
    parser.add_argument("--manifest", type=Path, default=root / "data" / "legacy_manifest.csv")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = repo_root_from_script()
    if args.output_dir is not None:
        output_dir = args.output_dir
    elif args.model == "author-only":
        output_dir = root / "artifacts" / "author_models" / "author_only"
    elif args.model == "author-common6":
        output_dir = root / "artifacts" / AUTHOR_COMMON6_MODEL_DIR
    elif args.model == "our-common7":
        output_dir = root / "artifacts" / OUR_COMMON7_MODEL_DIR
    elif args.model == "our-common6":
        output_dir = root / "artifacts" / OUR_COMMON6_MODEL_DIR
    elif args.model == "mixed-common6":
        output_dir = root / "artifacts" / MIXED_COMMON6_MODEL_DIR
    else:
        output_dir = root / "artifacts" / MIXED_MODEL_DIR

    if args.model == "author-only":
        config = train_author_only(root, output_dir.resolve())
    elif args.model == "author-common6":
        config = train_author_only(
            root,
            output_dir.resolve(),
            channel_set="common6",
            model_type="author_common6",
        )
    else:
        config = train_our_common7_or_mixed(
            root,
            args.manifest,
            output_dir.resolve(),
            mixed=args.model in {"mixed", "mixed-common6"},
            channel_set="common6" if args.model in {"our-common6", "mixed-common6"} else "common7",
        )
    print(f"{args.model}: {config.get('status', 'trained')}")
    print(f"Output: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
