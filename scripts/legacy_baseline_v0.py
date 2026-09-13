"""Freeze the Legacy EEG traditional-ML baseline.

This is the only training entry point for ``legacy_baseline_v0``.  It is
intentionally limited to ``data/legacy_manifest.csv`` and refuses to read
anything under ``data/locked``.

The implementation follows the existing self-recorded 3/4-class notebooks:
MNE EDF loading, EEG-channel selection, 0.5--43 Hz FIR filtering, 4-second
windows with a 2-second step, Welch band-power features, and a
StandardScaler -> PCA -> RBF SVC pipeline.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import joblib
import mne
import numpy as np
import pandas as pd
from scipy.signal import welch
from sklearn.decomposition import PCA
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


BASELINE_VERSION = "legacy_baseline_v0"
DATASET_ROLE = "legacy_baseline_candidate"
LABELS = ("unfocus", "focus")
LABEL_MAPPING = {"focus": "focus", "iu": "unfocus", "ou": "unfocus"}
WINDOW_SEC = 4.0
STEP_SEC = 2.0
FILTER_L_HZ = 0.5
FILTER_H_HZ = 43.0
FILTER_METHOD = "fir"
FILTER_DESIGN = "firwin"
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
PCA_N_COMPONENTS: float = 0.95
SVC_PARAMS = {
    "kernel": "rbf",
    "C": 10.0,
    "gamma": "scale",
    "class_weight": "balanced",
    "probability": True,
    "random_state": RANDOM_SEED,
}


def _json_dump(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_locked_path(path: Path) -> bool:
    normalized = str(path.resolve()).replace("\\", "/").lower()
    return "/data/locked/" in normalized or normalized.endswith("/data/locked")


def assert_not_locked(path: Path, description: str) -> None:
    if is_locked_path(path):
        raise RuntimeError(f"Refusing to access locked data ({description}): {path}")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def read_legacy_manifest(manifest_path: Path, repo_root: Path) -> pd.DataFrame:
    manifest_path = manifest_path.resolve()
    assert_not_locked(manifest_path, "manifest")
    expected = (repo_root / "data" / "legacy_manifest.csv").resolve()
    if manifest_path != expected:
        raise RuntimeError(
            "legacy_baseline_v0 only accepts data/legacy_manifest.csv as its manifest"
        )

    rows = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
    required = {
        "dataset_version",
        "recording_id",
        "source_recording_id",
        "session_group_id",
        "canonical_label",
        "dataset_role",
        "split",
        "edf_path",
        "activity_start_s",
        "activity_end_s",
        "sfreq_hz",
        "window_sec",
        "step_sec",
    }
    missing = sorted(required - set(rows.columns))
    if missing:
        raise AssertionError(f"Manifest missing required columns: {missing}")

    rows = rows.loc[rows["dataset_role"] == DATASET_ROLE].copy()
    if rows.empty:
        raise AssertionError(f"Manifest has no {DATASET_ROLE!r} rows")
    if set(rows["canonical_label"]) - set(LABELS):
        raise AssertionError(
            "Candidate rows contain labels outside focus/unfocus: "
            f"{sorted(set(rows['canonical_label']) - set(LABELS))}"
        )
    if rows["split"].nunique() != 1 or rows["split"].iloc[0] != "unassigned":
        raise AssertionError("The input manifest must remain unassigned; split is generated here")
    if rows["dataset_version"].nunique() != 1:
        raise AssertionError("Candidate rows must have exactly one dataset_version")
    if rows[["recording_id", "source_recording_id", "session_group_id"]].isna().any().any():
        raise AssertionError("Identity/group fields must not be missing")

    # A source recording must have one path and one complete session group.
    source_summary = rows.groupby("source_recording_id").agg(
        n_paths=("edf_path", "nunique"),
        n_groups=("session_group_id", "nunique"),
    )
    if (source_summary != 1).any().any():
        raise AssertionError(
            "A source_recording_id maps to more than one EDF path or session_group_id"
        )

    rows["edf_path_abs"] = rows["edf_path"].map(
        lambda value: (repo_root / value).resolve()
    )
    if rows["edf_path_abs"].map(is_locked_path).any():
        raise AssertionError("Manifest candidate rows reference locked data")
    if not rows["edf_path_abs"].map(Path.exists).all():
        missing_paths = rows.loc[~rows["edf_path_abs"].map(Path.exists), "edf_path"].tolist()
        raise FileNotFoundError(f"Legacy EDF path(s) missing: {missing_paths}")

    for column in ("activity_start_s", "activity_end_s", "sfreq_hz", "window_sec", "step_sec"):
        rows[column] = pd.to_numeric(rows[column], errors="raise")
    if not np.isclose(rows["window_sec"], WINDOW_SEC).all() or not np.isclose(
        rows["step_sec"], STEP_SEC
    ).all():
        raise AssertionError("Manifest windows must be the frozen 4 s / 2 s rule")
    if (rows["activity_end_s"] <= rows["activity_start_s"]).any():
        raise AssertionError("Manifest activity intervals must have positive duration")

    return rows


def make_group_split(rows: pd.DataFrame) -> pd.DataFrame:
    """Assign whole session_group_id values before any EDF/window processing."""
    group_ids = rows["session_group_id"].drop_duplicates().tolist()
    if len(group_ids) < 2:
        raise AssertionError("At least two session groups are required")

    n_validation = max(1, int(math.ceil(len(group_ids) * VALIDATION_GROUP_FRACTION)))
    rng = np.random.RandomState(RANDOM_SEED)
    validation_groups = set(rng.permutation(group_ids)[:n_validation].tolist())
    rows = rows.copy()
    rows["split"] = np.where(
        rows["session_group_id"].isin(validation_groups), "validation", "train"
    )

    train_groups = set(rows.loc[rows["split"] == "train", "session_group_id"])
    val_groups = set(rows.loc[rows["split"] == "validation", "session_group_id"])
    assert train_groups.isdisjoint(val_groups), "session_group_id leakage"

    train_sources = set(rows.loc[rows["split"] == "train", "source_recording_id"])
    val_sources = set(rows.loc[rows["split"] == "validation", "source_recording_id"])
    assert train_sources.isdisjoint(val_sources), "source_recording_id leakage"
    assert set(rows["split"]) == {"train", "validation"}
    assert set(rows.loc[rows["split"] == "validation", "canonical_label"]) == set(LABELS), (
        "Validation must contain both focus and unfocus"
    )
    assert set(rows.loc[rows["split"] == "train", "canonical_label"]) == set(LABELS), (
        "Training must contain both focus and unfocus"
    )
    assert (rows["dataset_role"] == DATASET_ROLE).all()
    assert (~rows["edf_path_abs"].map(is_locked_path)).all()
    return rows


def bandpower_features(window_data: np.ndarray, sfreq: float) -> np.ndarray:
    """Match the existing self-recorded Notebook's per-channel features."""
    features: list[float] = []
    for channel_data in window_data:
        freqs, psd = welch(
            channel_data,
            fs=sfreq,
            nperseg=min(len(channel_data), int(sfreq * WELCH_NPERSEG_SEC)),
        )
        total_idx = (freqs >= 1.0) & (freqs <= 43.0)
        total_power = float(np.trapezoid(psd[total_idx], freqs[total_idx])) + 1e-12
        for low, high in BANDS.values():
            band_idx = (freqs >= low) & (freqs < high)
            power = float(np.trapezoid(psd[band_idx], freqs[band_idx])) + 1e-12
            features.extend((float(np.log(power)), float(power / total_power)))
    return np.asarray(features, dtype=np.float64)


def load_edf(edf_path: Path) -> tuple[np.ndarray, float, list[str]]:
    assert_not_locked(edf_path, "EDF")
    raw = mne.io.read_raw_edf(
        str(edf_path),
        preload=True,
        infer_types=True,
        verbose=False,
    )
    try:
        raw.pick_types(eeg=True, stim=False, misc=False, verbose=False)
    except TypeError:
        raw.pick_types(eeg=True, stim=False, misc=False)
    if len(raw.ch_names) == 0:
        raise ValueError(f"{edf_path} has no MNE-recognized EEG channels")

    if not np.isclose(float(raw.info["sfreq"]), float(round(float(raw.info["sfreq"]))), atol=1e-6):
        raise ValueError(f"Non-integral source sampling rate is unsupported: {raw.info['sfreq']}")
    source_fs = float(raw.info["sfreq"])
    target_fs = 128.0
    if not np.isclose(source_fs, target_fs):
        raw.resample(target_fs, npad="auto", verbose=False)
    data = raw.get_data()
    return data, float(raw.info["sfreq"]), list(raw.ch_names)


def filter_segment(segment_data: np.ndarray, sfreq: float) -> np.ndarray:
    """Apply the existing Notebook's MNE FIR bandpass to one manifest segment."""
    return mne.filter.filter_data(
        segment_data,
        sfreq=sfreq,
        l_freq=FILTER_L_HZ,
        h_freq=FILTER_H_HZ,
        method=FILTER_METHOD,
        fir_design=FILTER_DESIGN,
        verbose=False,
    )


def extract_segment_features(
    data: np.ndarray,
    sfreq: float,
    start_sec: float,
    end_sec: float,
) -> tuple[np.ndarray, np.ndarray]:
    start = int(round(start_sec * sfreq))
    stop = int(round(end_sec * sfreq))
    if start < 0 or stop > data.shape[1] or stop <= start:
        raise ValueError(
            f"Manifest interval [{start_sec}, {end_sec}) is outside EDF "
            f"({data.shape[1] / sfreq:.3f} s)"
        )
    segment = filter_segment(data[:, start:stop], sfreq)
    window_size = int(round(WINDOW_SEC * sfreq))
    step_size = int(round(STEP_SEC * sfreq))
    if segment.shape[1] < window_size:
        raise ValueError("Segment is shorter than one frozen 4-second window")

    features: list[np.ndarray] = []
    starts: list[float] = []
    for window_start in range(0, segment.shape[1] - window_size + 1, step_size):
        window = segment[:, window_start : window_start + window_size]
        features.append(bandpower_features(window, sfreq))
        starts.append(start_sec + window_start / sfreq)
    return np.asarray(features), np.asarray(starts, dtype=np.float64)


def build_features(rows: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Read each source EDF once, then cut only manifest-defined segments/windows."""
    source_to_rows: dict[str, list[int]] = defaultdict(list)
    for index, row in rows.iterrows():
        source_to_rows[str(row["source_recording_id"])].append(index)

    X_parts: list[np.ndarray] = []
    y_parts: list[str] = []
    metadata: list[dict[str, Any]] = []
    channel_signature: tuple[str, ...] | None = None

    for source_id, indices in source_to_rows.items():
        source_row = rows.loc[indices[0]]
        edf_path = Path(source_row["edf_path_abs"])
        print(f"Reading Legacy EDF: {source_id} ({edf_path.name})", flush=True)
        data, sfreq, channels = load_edf(edf_path)
        current_signature = tuple(channels)
        if channel_signature is None:
            channel_signature = current_signature
        elif current_signature != channel_signature:
            raise AssertionError(
                "All Legacy EDFs must have the same ordered EEG channels for one feature space; "
                f"expected {channel_signature}, got {current_signature} in {source_id}"
            )

        for index in indices:
            row = rows.loc[index]
            X_segment, window_starts = extract_segment_features(
                data,
                sfreq,
                float(row["activity_start_s"]),
                float(row["activity_end_s"]),
            )
            X_parts.append(X_segment)
            y_parts.extend([str(row["canonical_label"])] * len(X_segment))
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

    if not X_parts:
        raise AssertionError("No Legacy features were generated")
    X = np.concatenate(X_parts, axis=0)
    y = np.asarray(y_parts, dtype=object)
    metadata_df = pd.DataFrame(metadata)
    if len(X) != len(y) or len(X) != len(metadata_df):
        raise AssertionError("Feature/label/metadata lengths differ")
    if not np.isfinite(X).all():
        raise AssertionError("Feature matrix contains non-finite values")
    return X, y, metadata_df


def make_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=PCA_N_COMPONENTS, random_state=RANDOM_SEED)),
            ("svc", SVC(**SVC_PARAMS)),
        ]
    )


def group_metrics(predictions: pd.DataFrame) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    group_columns = ["session_group_id"]
    for group_id, group in predictions.groupby(group_columns, sort=True):
        group = group.copy()
        true_counts = group["true"].value_counts().reindex(LABELS, fill_value=0)
        pred_counts = group["pred"].value_counts().reindex(LABELS, fill_value=0)
        result.append(
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
    return result


def write_artifacts(
    output_dir: Path,
    repo_root: Path,
    manifest_path: Path,
    split_rows: pd.DataFrame,
    pipeline: Pipeline,
    predictions: pd.DataFrame,
    group_summary: list[dict[str, Any]],
    metrics: dict[str, Any],
    config: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    split_columns = [
        "dataset_version",
        "recording_id",
        "source_recording_id",
        "session_group_id",
        "subject_id",
        "canonical_label",
        "dataset_role",
        "split",
        "edf_path",
        "activity_start_s",
        "activity_end_s",
        "sfreq_hz",
        "window_sec",
        "step_sec",
    ]
    split_rows[split_columns].to_csv(output_dir / "split.csv", index=False)
    _json_dump(output_dir / "config.json", config)
    joblib.dump(pipeline, output_dir / "pipeline.joblib")
    predictions.to_csv(output_dir / "validation_predictions.csv", index=False)
    pd.DataFrame(group_summary).to_csv(output_dir / "validation_group_metrics.csv", index=False)
    _json_dump(output_dir / "validation_metrics.json", {**metrics, "groups": group_summary})

    artifact_paths = [
        output_dir / "pipeline.joblib",
        output_dir / "config.json",
        output_dir / "split.csv",
        output_dir / "validation_predictions.csv",
        output_dir / "validation_group_metrics.csv",
        output_dir / "validation_metrics.json",
    ]
    freeze_manifest = {
        "baseline_version": BASELINE_VERSION,
        "dataset_version": str(split_rows["dataset_version"].iloc[0]),
        "git_head": __import__("subprocess").check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip(),
        "git_branch": __import__("subprocess").check_output(
            ["git", "branch", "--show-current"], cwd=repo_root, text=True
        ).strip(),
        "legacy_manifest": {
            "path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
            "sha256": sha256_file(manifest_path),
        },
        "artifact_sha256": {
            path.name: sha256_file(path) for path in artifact_paths
        },
        "train_session_group_count": int(
            split_rows.loc[split_rows["split"] == "train", "session_group_id"].nunique()
        ),
        "validation_session_group_count": int(
            split_rows.loc[split_rows["split"] == "validation", "session_group_id"].nunique()
        ),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "locked_test_read": False,
    }
    _json_dump(output_dir / "freeze_manifest.json", freeze_manifest)


def run(repo_root: Path, manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    assert_not_locked(manifest_path, "manifest")
    rows = read_legacy_manifest(manifest_path, repo_root)
    split_rows = make_group_split(rows)
    split_rows = split_rows.sort_values(
        ["split", "session_group_id", "recording_id"]
    ).reset_index(drop=True)

    # The split is complete before this first EDF read.
    X, y, metadata = build_features(split_rows)
    train_mask = metadata["split"].eq("train").to_numpy()
    val_mask = metadata["split"].eq("validation").to_numpy()
    if not train_mask.any() or not val_mask.any():
        raise AssertionError("Both train and validation must have windows")

    pipeline = make_pipeline()
    # The only fit call in this script. Validation is strictly predict-only.
    pipeline.fit(X[train_mask], y[train_mask])
    y_pred = pipeline.predict(X[val_mask])

    validation_metadata = metadata.loc[val_mask].reset_index(drop=True)
    predictions = validation_metadata[
        [
            "recording_id",
            "source_recording_id",
            "session_group_id",
            "subject_id",
            "window_start_sec",
            "window_sec",
            "step_sec",
            "sfreq_hz",
        ]
    ].copy()
    predictions.insert(0, "true", validation_metadata["canonical_label"].to_numpy())
    predictions.insert(1, "pred", y_pred)

    cm = confusion_matrix(
        validation_metadata["canonical_label"], y_pred, labels=list(LABELS)
    )
    report = classification_report(
        validation_metadata["canonical_label"],
        y_pred,
        labels=list(LABELS),
        target_names=list(LABELS),
        output_dict=True,
        zero_division=0,
    )
    metrics = {
        "overall_accuracy": float(
            accuracy_score(validation_metadata["canonical_label"], y_pred)
        ),
        "labels": list(LABELS),
        "confusion_matrix": cm.astype(int).tolist(),
        "classification_report": report,
        "n_train_windows": int(train_mask.sum()),
        "n_validation_windows": int(val_mask.sum()),
        "n_features": int(X.shape[1]),
        "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
        "train_session_group_ids": sorted(
            split_rows.loc[split_rows["split"] == "train", "session_group_id"].unique()
        ),
        "validation_session_group_ids": sorted(
            split_rows.loc[split_rows["split"] == "validation", "session_group_id"].unique()
        ),
    }
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
            "filter": {
                "method": FILTER_METHOD,
                "fir_design": FILTER_DESIGN,
                "l_freq_hz": FILTER_L_HZ,
                "h_freq_hz": FILTER_H_HZ,
                "applied": "per manifest segment before windowing",
            },
        },
        "feature_extraction": {
            "method": "Welch band power per channel",
            "welch_nperseg_sec": WELCH_NPERSEG_SEC,
            "total_power_range_hz": [1.0, 43.0],
            "bands_hz": {name: list(bounds) for name, bounds in BANDS.items()},
            "features_per_band": ["log_absolute_power", "relative_power"],
            "feature_order": "channel, band insertion order, absolute then relative",
        },
        "pca": {
            "n_components": PCA_N_COMPONENTS,
            "random_state": RANDOM_SEED,
        },
        "svc": SVC_PARAMS,
        "random_seed": RANDOM_SEED,
        "split": {
            "unit": "session_group_id",
            "validation_fraction": VALIDATION_GROUP_FRACTION,
            "n_validation_groups": int(
                split_rows.loc[split_rows["split"] == "validation", "session_group_id"].nunique()
            ),
            "algorithm": "numpy RandomState(seed).permutation(groups), first ceil(fraction*n) groups",
            "seed": RANDOM_SEED,
        },
        "fit_policy": "pipeline.fit(X_train, y_train) only; validation uses pipeline.predict(X_val)",
    }
    group_summary = group_metrics(predictions)
    write_artifacts(
        output_dir,
        repo_root,
        manifest_path,
        split_rows,
        pipeline,
        predictions,
        group_summary,
        metrics,
        config,
    )

    train_groups = set(split_rows.loc[split_rows["split"] == "train", "session_group_id"])
    val_groups = set(split_rows.loc[split_rows["split"] == "validation", "session_group_id"])
    train_sources = set(split_rows.loc[split_rows["split"] == "train", "source_recording_id"])
    val_sources = set(split_rows.loc[split_rows["split"] == "validation", "source_recording_id"])
    result = {
        "output_dir": str(output_dir),
        "train_session_group_count": len(train_groups),
        "validation_session_group_count": len(val_groups),
        "train_source_recording_count": len(train_sources),
        "validation_source_recording_count": len(val_sources),
        "group_intersection_count": len(train_groups & val_groups),
        "source_intersection_count": len(train_sources & val_sources),
        "train_window_count": int(train_mask.sum()),
        "validation_window_count": int(val_mask.sum()),
        "metrics": metrics,
        "group_metrics": group_summary,
        "validation_groups": sorted(val_groups),
    }
    _json_dump(output_dir / "run_summary.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return result


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "data" / "legacy_manifest.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "artifacts" / BASELINE_VERSION,
    )
    return parser.parse_args(list(argv))


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    root = repo_root_from_script()
    run(root, args.manifest, args.output_dir)
