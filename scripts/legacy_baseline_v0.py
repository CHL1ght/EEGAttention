"""Train and freeze ``legacy_baseline_v0``.

Data:
    Legacy self-recorded EEG candidates only.

Important:
    Train/validation are separated by complete ``session_group_id`` values.
    Scaler/PCA/SVC are fitted only on training windows.  LOCKED_TEST data is
    refused by the loader and is never accessed from this entry point.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from eeg_pipeline_utils import (
    assert_not_locked,
    extract_segment_features,
    load_eeg_recording,
    save_dataframe,
    save_json,
    sha256_file,
    print_banner,
    print_metric,
)


BASELINE_VERSION = "legacy_baseline_v0"
DATASET_ROLE = "legacy_baseline_candidate"
LABELS = ("unfocus", "focus")
LABEL_MAPPING = {"focus": "focus", "iu": "unfocus", "ou": "unfocus"}
WINDOW_SEC = 4.0
STEP_SEC = 2.0
FILTER_L_HZ = 0.5
FILTER_H_HZ = 43.0
BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 43.0),
}
WELCH_NPERSEG_SEC = 2.0
RANDOM_SEED = 42
VALIDATION_GROUP_FRACTION = 0.20
PCA_N_COMPONENTS = 0.95
SVC_PARAMS = {
    "kernel": "rbf",
    "C": 10.0,
    "gamma": "scale",
    "class_weight": "balanced",
    "probability": True,
    "random_state": RANDOM_SEED,
}


def repo_root_from_script() -> Path:
    """Return the repository root without depending on the working directory."""
    return Path(__file__).resolve().parents[1]


def load_legacy_manifest(manifest_path: Path, repo_root: Path) -> pd.DataFrame:
    """Load only manifest rows approved for the Legacy binary baseline."""
    manifest_path = manifest_path.resolve()
    assert_not_locked(manifest_path, "manifest")
    expected = (repo_root / "data" / "legacy_manifest.csv").resolve()
    if manifest_path != expected:
        raise RuntimeError("This baseline accepts only data/legacy_manifest.csv")

    rows = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
    required = {
        "dataset_version", "recording_id", "source_recording_id", "session_group_id",
        "canonical_label", "dataset_role", "split", "edf_path", "activity_start_s",
        "activity_end_s", "sfreq_hz", "window_sec", "step_sec",
    }
    missing = sorted(required - set(rows.columns))
    if missing:
        raise AssertionError(f"Manifest missing required columns: {missing}")

    rows = rows.loc[rows["dataset_role"] == DATASET_ROLE].copy()
    if rows.empty:
        raise AssertionError(f"Manifest has no {DATASET_ROLE!r} rows")
    if set(rows["canonical_label"]) - set(LABELS):
        raise AssertionError("Candidate rows contain labels outside focus/unfocus")
    if rows["split"].nunique() != 1 or rows["split"].iloc[0] != "unassigned":
        raise AssertionError("The input manifest must remain unassigned")
    if rows["dataset_version"].nunique() != 1:
        raise AssertionError("Candidate rows must have exactly one dataset_version")

    source_summary = rows.groupby("source_recording_id").agg(
        n_paths=("edf_path", "nunique"),
        n_groups=("session_group_id", "nunique"),
    )
    if (source_summary != 1).any().any():
        raise AssertionError("A source recording maps to multiple paths or groups")

    rows["edf_path_abs"] = rows["edf_path"].map(lambda value: (repo_root / value).resolve())
    if rows["edf_path_abs"].map(lambda path: path.exists()).eq(False).any():
        missing_paths = rows.loc[~rows["edf_path_abs"].map(lambda path: path.exists()), "edf_path"].tolist()
        raise FileNotFoundError(f"Legacy EDF path(s) missing: {missing_paths}")
    if rows["edf_path_abs"].map(lambda path: not path.is_relative_to(repo_root)).any():
        raise AssertionError("Manifest EDF path escaped the repository")
    if rows["edf_path_abs"].map(lambda path: not path.is_relative_to(repo_root / "data" / "legacy")).any():
        raise AssertionError("Candidate EDF path is outside data/legacy")
    if rows["edf_path_abs"].map(lambda path: path.as_posix().lower().find("/data/locked/") >= 0).any():
        raise AssertionError("Manifest candidate rows reference locked data")

    for column in ("activity_start_s", "activity_end_s", "sfreq_hz", "window_sec", "step_sec"):
        rows[column] = pd.to_numeric(rows[column], errors="raise")
    if not np.isclose(rows["window_sec"], WINDOW_SEC).all() or not np.isclose(rows["step_sec"], STEP_SEC).all():
        raise AssertionError("Manifest windows must be the frozen 4 s / 2 s rule")
    if (rows["activity_end_s"] <= rows["activity_start_s"]).any():
        raise AssertionError("Manifest activity intervals must be positive")
    return rows


def prepare_split(rows: pd.DataFrame) -> pd.DataFrame:
    """Assign whole groups before any EDF is read or any window is created."""
    group_ids = rows["session_group_id"].drop_duplicates().tolist()
    if len(group_ids) < 2:
        raise AssertionError("At least two session groups are required")
    n_validation = max(1, int(math.ceil(len(group_ids) * VALIDATION_GROUP_FRACTION)))
    rng = np.random.RandomState(RANDOM_SEED)
    validation_groups = set(rng.permutation(group_ids)[:n_validation].tolist())

    rows = rows.copy()
    rows["split"] = np.where(rows["session_group_id"].isin(validation_groups), "validation", "train")
    train_groups = set(rows.loc[rows["split"] == "train", "session_group_id"])
    val_groups = set(rows.loc[rows["split"] == "validation", "session_group_id"])
    train_sources = set(rows.loc[rows["split"] == "train", "source_recording_id"])
    val_sources = set(rows.loc[rows["split"] == "validation", "source_recording_id"])
    assert train_groups.isdisjoint(val_groups), "session_group_id leakage"
    assert train_sources.isdisjoint(val_sources), "source_recording_id leakage"
    assert set(rows.loc[rows["split"] == "validation", "canonical_label"]) == set(LABELS)
    assert set(rows.loc[rows["split"] == "train", "canonical_label"]) == set(LABELS)
    assert (rows["dataset_role"] == DATASET_ROLE).all()
    assert (~rows["edf_path_abs"].map(lambda path: path.as_posix().lower().find("/data/locked/") >= 0)).all()
    return rows


def build_feature_dataset(rows: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Read each source once, then extract only its manifest-defined segments."""
    source_to_rows: dict[str, list[int]] = defaultdict(list)
    for index, row in rows.iterrows():
        source_to_rows[str(row["source_recording_id"])].append(index)

    feature_parts: list[np.ndarray] = []
    labels: list[str] = []
    metadata: list[dict[str, Any]] = []
    channel_signature: tuple[str, ...] | None = None
    for source_id, indices in source_to_rows.items():
        source_row = rows.loc[indices[0]]
        data, sfreq, channels = load_eeg_recording(Path(source_row["edf_path_abs"]))
        current_signature = tuple(channels)
        if channel_signature is None:
            channel_signature = current_signature
        elif current_signature != channel_signature:
            raise AssertionError("Legacy EDFs do not share one ordered EEG channel layout")

        for index in indices:
            row = rows.loc[index]
            features, window_starts = extract_segment_features(
                data,
                sfreq,
                float(row["activity_start_s"]),
                float(row["activity_end_s"]),
                BANDS,
                window_sec=WINDOW_SEC,
                step_sec=STEP_SEC,
                l_freq=FILTER_L_HZ,
                h_freq=FILTER_H_HZ,
            )
            feature_parts.append(features)
            labels.extend([str(row["canonical_label"])] * len(features))
            for window_start in window_starts:
                metadata.append(
                    {
                        "recording_id": str(row["recording_id"]),
                        "source_recording_id": source_id,
                        "session_group_id": str(row["session_group_id"]),
                        "subject_id": str(row["subject_id"]),
                        "canonical_label": str(row["canonical_label"]),
                        "split": str(row["split"]),
                        "window_start_sec": float(window_start),
                        "window_sec": WINDOW_SEC,
                        "step_sec": STEP_SEC,
                        "sfreq_hz": sfreq,
                    }
                )

    X = np.concatenate(feature_parts, axis=0)
    y = np.asarray(labels, dtype=object)
    metadata_df = pd.DataFrame(metadata)
    if len(X) != len(y) or len(X) != len(metadata_df) or not np.isfinite(X).all():
        raise AssertionError("Feature, label, and metadata arrays are inconsistent")
    return X, y, metadata_df


def build_baseline_pipeline() -> Pipeline:
    """Build the frozen Scaler -> PCA -> RBF SVC pipeline."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=PCA_N_COMPONENTS, random_state=RANDOM_SEED)),
            ("svc", SVC(**SVC_PARAMS)),
        ]
    )


def evaluate_predictions(
    pipeline: Pipeline,
    X_validation: np.ndarray,
    validation_metadata: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Predict validation windows and format the frozen metrics schema."""
    y_pred = pipeline.predict(X_validation)
    y_true = validation_metadata["canonical_label"]
    cm = confusion_matrix(y_true, y_pred, labels=list(LABELS))
    metrics = {
        "overall_accuracy": float(accuracy_score(y_true, y_pred)),
        "labels": list(LABELS),
        "confusion_matrix": cm.astype(int).tolist(),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=list(LABELS),
            target_names=list(LABELS),
            output_dict=True,
            zero_division=0,
        ),
        "n_train_windows": None,
        "n_validation_windows": int(len(y_true)),
        "n_features": int(X_validation.shape[1]),
        "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
        "train_session_group_ids": [],
        "validation_session_group_ids": sorted(validation_metadata["session_group_id"].unique()),
    }
    return y_pred, metrics


def summarize_by_session(predictions: pd.DataFrame) -> list[dict[str, Any]]:
    """Summarize window truth/predictions for every Legacy validation group."""
    summaries: list[dict[str, Any]] = []
    for group_id, group in predictions.groupby(["session_group_id"], sort=True):
        true_counts = group["true"].value_counts().reindex(LABELS, fill_value=0)
        pred_counts = group["pred"].value_counts().reindex(LABELS, fill_value=0)
        summaries.append(
            {
                "session_group_id": group_id[0],
                "true_label_counts": {label: int(true_counts[label]) for label in LABELS},
                "pred_label_counts": {label: int(pred_counts[label]) for label in LABELS},
                "n_windows": int(len(group)),
                "group_accuracy": float(accuracy_score(group["true"], group["pred"])),
                "predicted_label_proportion": {
                    label: float(pred_counts[label] / len(group)) for label in LABELS
                },
            }
        )
    return summaries


def save_baseline_outputs(
    output_dir: Path,
    repo_root: Path,
    manifest_path: Path,
    split_rows: pd.DataFrame,
    pipeline: Pipeline,
    predictions: pd.DataFrame,
    group_summaries: list[dict[str, Any]],
    metrics: dict[str, Any],
    config: dict[str, Any],
) -> None:
    """Persist the same machine-readable freeze artifacts as the original run."""
    output_dir.mkdir(parents=True, exist_ok=True)
    split_columns = [
        "dataset_version", "recording_id", "source_recording_id", "session_group_id",
        "subject_id", "canonical_label", "dataset_role", "split", "edf_path",
        "activity_start_s", "activity_end_s", "sfreq_hz", "window_sec", "step_sec",
    ]
    save_dataframe(output_dir / "split.csv", split_rows[split_columns])
    save_json(output_dir / "config.json", config)
    joblib.dump(pipeline, output_dir / "pipeline.joblib")
    save_dataframe(output_dir / "validation_predictions.csv", predictions)
    save_dataframe(output_dir / "validation_group_metrics.csv", pd.DataFrame(group_summaries))
    save_json(output_dir / "validation_metrics.json", {**metrics, "groups": group_summaries})

    artifact_paths = [
        output_dir / "pipeline.joblib", output_dir / "config.json", output_dir / "split.csv",
        output_dir / "validation_predictions.csv", output_dir / "validation_group_metrics.csv",
        output_dir / "validation_metrics.json",
    ]
    freeze_manifest = {
        "baseline_version": BASELINE_VERSION,
        "dataset_version": str(split_rows["dataset_version"].iloc[0]),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip(),
        "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo_root, text=True).strip(),
        "legacy_manifest": {
            "path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
            "sha256": sha256_file(manifest_path),
        },
        "artifact_sha256": {path.name: sha256_file(path) for path in artifact_paths},
        "train_session_group_count": int(split_rows.loc[split_rows["split"] == "train", "session_group_id"].nunique()),
        "validation_session_group_count": int(split_rows.loc[split_rows["split"] == "validation", "session_group_id"].nunique()),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "locked_test_read": False,
    }
    save_json(output_dir / "freeze_manifest.json", freeze_manifest)


def print_validation_summary(metrics: dict[str, Any], y_true: pd.Series, y_pred: np.ndarray) -> None:
    """Print a compact validation summary without dumping arrays or DataFrames."""
    balanced = balanced_accuracy_score(y_true, y_pred)
    print_metric("Accuracy", f"{metrics['overall_accuracy']:.2%}")
    print_metric("Balanced accuracy", f"{balanced:.2%}")
    print("\n  True \\ Pred       unfocus    focus")
    cm = np.asarray(metrics["confusion_matrix"])
    print(f"  unfocus          {cm[0, 0]:>8} {cm[0, 1]:>9}")
    print(f"  focus            {cm[1, 0]:>8} {cm[1, 1]:>9}")


def train_and_freeze(repo_root: Path, manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    """Run the complete Legacy training/validation/freeze business flow."""
    print_banner("Legacy Baseline v0")
    print("\n[1/5] Loading Legacy dataset")
    rows = load_legacy_manifest(manifest_path, repo_root)
    split_rows = prepare_split(rows).sort_values(["split", "session_group_id", "recording_id"]).reset_index(drop=True)
    print_metric("Train groups", int(split_rows.loc[split_rows["split"] == "train", "session_group_id"].nunique()))
    print_metric("Validation groups", int(split_rows.loc[split_rows["split"] == "validation", "session_group_id"].nunique()))

    print("\n[2/5] Extracting EEG features")
    print_metric("Sampling rate", "128 Hz")
    print_metric("Filter", "0.5–43 Hz")
    print_metric("Window / step", "4 s / 2 s")
    X, y, metadata = build_feature_dataset(split_rows)
    train_mask = metadata["split"].eq("train").to_numpy()
    val_mask = metadata["split"].eq("validation").to_numpy()
    print_metric("Train windows", f"{int(train_mask.sum()):,}")
    print_metric("Val windows", f"{int(val_mask.sum()):,}")

    print("\n[3/5] Training model")
    print("  StandardScaler\n    → PCA (95%)\n    → RBF SVC (C=10, balanced)")
    pipeline = build_baseline_pipeline()
    # The only model fit: validation data never reaches this call.
    pipeline.fit(X[train_mask], y[train_mask])

    print("\n[4/5] Validation")
    validation_metadata = metadata.loc[val_mask].reset_index(drop=True)
    y_pred, metrics = evaluate_predictions(pipeline, X[val_mask], validation_metadata)
    metrics["n_train_windows"] = int(train_mask.sum())
    metrics["train_session_group_ids"] = sorted(split_rows.loc[split_rows["split"] == "train", "session_group_id"].unique())
    print_validation_summary(metrics, validation_metadata["canonical_label"], y_pred)

    predictions = validation_metadata[[
        "recording_id", "source_recording_id", "session_group_id", "subject_id",
        "window_start_sec", "window_sec", "step_sec", "sfreq_hz",
    ]].copy()
    predictions.insert(0, "true", validation_metadata["canonical_label"].to_numpy())
    predictions.insert(1, "pred", y_pred)
    group_summaries = summarize_by_session(predictions)
    config = {
        "baseline_version": BASELINE_VERSION,
        "dataset_version": str(split_rows["dataset_version"].iloc[0]),
        "dataset_role": DATASET_ROLE,
        "label_mapping": LABEL_MAPPING,
        "labels": list(LABELS),
        "window_sec": WINDOW_SEC,
        "step_sec": STEP_SEC,
        "preprocessing": {
            "edf_reader": "mne.io.read_raw_edf(preload=True, infer_types=True)",
            "channel_policy": "all channels identified as EEG by MNE, ordered as in EDF",
            "target_sampling_rate_hz": 128.0,
            "resample": "MNE Raw.resample(target_fs, npad='auto') when source is not 128 Hz",
            "filter": {"method": "fir", "fir_design": "firwin", "l_freq_hz": FILTER_L_HZ, "h_freq_hz": FILTER_H_HZ, "applied": "per manifest segment before windowing"},
        },
        "feature_extraction": {
            "method": "Welch band power per channel",
            "welch_nperseg_sec": WELCH_NPERSEG_SEC,
            "total_power_range_hz": [1.0, 43.0],
            "bands_hz": {name: list(bounds) for name, bounds in BANDS.items()},
            "features_per_band": ["log_absolute_power", "relative_power"],
            "feature_order": "channel, band insertion order, absolute then relative",
        },
        "pca": {"n_components": PCA_N_COMPONENTS, "random_state": RANDOM_SEED},
        "svc": SVC_PARAMS,
        "random_seed": RANDOM_SEED,
        "split": {
            "unit": "session_group_id",
            "validation_fraction": VALIDATION_GROUP_FRACTION,
            "n_validation_groups": int(split_rows.loc[split_rows["split"] == "validation", "session_group_id"].nunique()),
            "algorithm": "numpy RandomState(seed).permutation(groups), first ceil(fraction*n) groups",
            "seed": RANDOM_SEED,
        },
        "fit_policy": "pipeline.fit(X_train, y_train) only; validation uses pipeline.predict(X_val)",
    }
    print("\n[5/5] Frozen artifacts")
    save_baseline_outputs(output_dir, repo_root, manifest_path, split_rows, pipeline, predictions, group_summaries, metrics, config)
    for name in ("pipeline.joblib", "config.json", "split.csv", "validation_predictions.csv", "validation_metrics.json", "freeze_manifest.json"):
        print(f"  ✓ {output_dir / name}")
    print("\nSTATUS: LEGACY_BASELINE_V0 FROZEN")
    return metrics


def check_existing_artifacts(output_dir: Path) -> None:
    """Regression-check frozen Legacy numbers without retraining or rereading EDFs."""
    metrics = json.loads((output_dir / "validation_metrics.json").read_text(encoding="utf-8"))
    split = pd.read_csv(output_dir / "split.csv")
    predictions = pd.read_csv(output_dir / "validation_predictions.csv")
    assert len(predictions) == 3282
    assert abs(float(metrics["overall_accuracy"]) - 0.699878) < 1e-6
    assert metrics["confusion_matrix"] == [[1315, 475], [510, 982]]
    train_groups = split.loc[split["split"] == "train", "session_group_id"].nunique()
    val_groups = split.loc[split["split"] == "validation", "session_group_id"].nunique()
    balanced = (1315 / (1315 + 475) + 982 / (982 + 510)) / 2
    print_banner("Legacy Baseline v0 — regression check")
    print_metric("Train groups", train_groups)
    print_metric("Validation groups", val_groups)
    print_metric("Validation windows", f"{len(predictions):,}")
    print_validation_summary(metrics, predictions["true"], predictions["pred"])
    print("\nSTATUS: LEGACY_BASELINE_V0 REGRESSION CHECK PASSED")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "data" / "legacy_manifest.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "artifacts" / BASELINE_VERSION)
    parser.add_argument("--check-existing", action="store_true", help="Check saved results without training or reading EDFs.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    """Select the explicit training flow or a no-write regression check."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check_existing:
        check_existing_artifacts(args.output_dir)
        return
    train_and_freeze(repo_root_from_script(), args.manifest, args.output_dir)


if __name__ == "__main__":
    main()
