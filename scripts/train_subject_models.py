"""Train the lyc/zyf subject-dependent Scaler -> PCA -> RBF SVC models.

Only ``legacy_manifest.csv`` rows marked ``legacy_baseline_candidate`` are
eligible.  The two personal models are fit on their subject's complete
historical candidate recordings; the dated ``LOCKED_TEST`` manifest is never
read by this training entry point.
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

import legacy_baseline_v0 as baseline
from eeg_pipeline_utils import assert_not_locked, save_dataframe, save_json, sha256_file
from subject_model_utils import PERSONAL_SUBJECTS


MODEL_VERSION = "subject_dependent_v1"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_training_scope(manifest_path: Path, repo_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return lyc/zyf rows and an explicit exclusion table for other subjects."""

    manifest_path = manifest_path.resolve()
    rows = baseline.load_legacy_manifest(manifest_path, repo_root)
    rows["subject_id"] = rows["subject_id"].astype(str).str.casefold()
    excluded = rows.loc[~rows["subject_id"].isin(PERSONAL_SUBJECTS)].copy()
    excluded["exclusion_reason"] = np.where(
        excluded["subject_id"].eq("zqd"),
        "zqd_excluded_by_phase_scope",
        "subject_identity_not_allowed_for_phase",
    )
    selected = rows.loc[rows["subject_id"].isin(PERSONAL_SUBJECTS)].copy()
    selected["split"] = "train"
    if selected.empty or set(selected["subject_id"]) != set(PERSONAL_SUBJECTS):
        raise AssertionError("Both lyc and zyf must have historical training rows")
    if selected["edf_path_abs"].map(lambda path: path.as_posix().lower().find("/data/locked/") >= 0).any():
        raise AssertionError("Personal training scope contains a LOCKED_TEST path")
    for path in selected["edf_path_abs"]:
        assert_not_locked(Path(path), "personal training EDF")
    return selected, excluded


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def train_subject_models(
    repo_root: Path,
    manifest_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Fit and save both personal models while sharing the existing feature path."""

    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    output_dir = output_dir.resolve()
    selected, excluded = load_training_scope(manifest_path, repo_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    excluded_columns = [
        "recording_id", "source_recording_id", "session_group_id", "subject_id",
        "canonical_label", "dataset_role", "edf_path", "split", "exclusion_reason",
    ]
    save_dataframe(output_dir / "excluded_candidate_rows.csv", excluded[excluded_columns])

    model_summaries: list[dict[str, Any]] = []
    for subject in PERSONAL_SUBJECTS:
        subject_rows = (
            selected.loc[selected["subject_id"].eq(subject)]
            .sort_values(["session_group_id", "recording_id"])
            .reset_index(drop=True)
        )
        if set(subject_rows["canonical_label"]) != set(baseline.LABELS):
            raise AssertionError(f"{subject} training rows do not contain both binary labels")

        X, y, metadata = baseline.build_feature_dataset(subject_rows)
        if set(metadata["subject_id"]) != {subject} or set(metadata["split"]) != {"train"}:
            raise AssertionError(f"{subject} feature metadata escaped the personal training scope")
        if not np.isfinite(X).all():
            raise AssertionError(f"{subject} features contain non-finite values")

        pipeline = baseline.build_baseline_pipeline()
        pipeline.fit(X, y)

        subject_dir = output_dir / subject
        subject_dir.mkdir(parents=True, exist_ok=True)
        model_path = subject_dir / "pipeline.joblib"
        config_path = subject_dir / "config.json"
        train_manifest_path = subject_dir / "train_manifest.csv"
        joblib.dump(pipeline, model_path)
        manifest_columns = [
            "dataset_version", "recording_id", "source_recording_id", "session_group_id",
            "subject_id", "canonical_label", "dataset_role", "split", "edf_path",
            "activity_start_s", "activity_end_s", "sfreq_hz", "window_sec", "step_sec",
        ]
        save_dataframe(train_manifest_path, subject_rows[manifest_columns])
        config = {
            "model_version": MODEL_VERSION,
            "model_type": "subject_dependent",
            "subject": subject,
            "dataset_version": str(subject_rows["dataset_version"].iloc[0]),
            "dataset_role": baseline.DATASET_ROLE,
            "labels": list(baseline.LABELS),
            "training_scope": {
                "unit": "complete EDF/source_recording_id and session_group_id",
                "n_edf": int(subject_rows["edf_path"].nunique()),
                "n_source_recordings": int(subject_rows["source_recording_id"].nunique()),
                "n_session_groups": int(subject_rows["session_group_id"].nunique()),
                "edf_paths": [str(value) for value in subject_rows["edf_path"].drop_duplicates().tolist()],
            },
            "n_train_windows": int(len(y)),
            "class_window_counts": {label: int(np.sum(y == label)) for label in baseline.LABELS},
            "n_features": int(X.shape[1]),
            "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
            "preprocessing": {
                "shared_with": "scripts/eeg_pipeline_utils.py",
                "target_sampling_rate_hz": 128.0,
                "filter_hz": [baseline.FILTER_L_HZ, baseline.FILTER_H_HZ],
                "window_step_sec": [baseline.WINDOW_SEC, baseline.STEP_SEC],
            },
            "pca": {"n_components": baseline.PCA_N_COMPONENTS, "random_state": baseline.RANDOM_SEED},
            "svc": baseline.SVC_PARAMS,
            "fit_policy": "pipeline.fit(X_subject_historical, y_subject_historical) only; LOCKED_TEST is prediction-only",
            "locked_test_read": False,
            "git_head": _git_head(repo_root),
            "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        save_json(config_path, config)
        model_summaries.append(
            {
                "subject": subject,
                "model_path": str(model_path.relative_to(repo_root)).replace("\\", "/"),
                "config_path": str(config_path.relative_to(repo_root)).replace("\\", "/"),
                "train_manifest_path": str(train_manifest_path.relative_to(repo_root)).replace("\\", "/"),
                "n_edf": int(subject_rows["edf_path"].nunique()),
                "n_source_recordings": int(subject_rows["source_recording_id"].nunique()),
                "n_session_groups": int(subject_rows["session_group_id"].nunique()),
                "n_train_windows": int(len(y)),
                "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
                "pipeline_sha256": sha256_file(model_path),
            }
        )
        print(f"{subject}: {len(y):,} windows from {subject_rows['edf_path'].nunique()} EDFs; "
              f"{subject_rows['session_group_id'].nunique()} session groups; "
              f"PCA={pipeline.named_steps['pca'].n_components_}")

    scope = {
        "model_version": MODEL_VERSION,
        "subjects": list(PERSONAL_SUBJECTS),
        "manifest_path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "manifest_sha256": sha256_file(manifest_path),
        "excluded_subjects": {"zqd": int(len(excluded.loc[excluded["subject_id"].eq("zqd")]))},
        "unknown_subject_rows_in_manifest": int(len(excluded.loc[~excluded["subject_id"].eq("zqd")])),
        "locked_test_read": False,
        "fit_calls": 2,
        "models": model_summaries,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "training_summary.json", scope)
    return scope


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "data" / "legacy_manifest.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "artifacts" / "subject_models")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = train_subject_models(repo_root_from_script(), args.manifest, args.output_dir)
    print(f"Saved subject models under {args.output_dir.resolve()}")
    print(f"Excluded candidate rows: {result['excluded_subjects']}")


if __name__ == "__main__":
    main()
