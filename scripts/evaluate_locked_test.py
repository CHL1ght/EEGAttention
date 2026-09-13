"""Evaluate a frozen baseline on LOCKED_TEST.

This script must never fit or modify the model.  It loads ``pipeline.joblib``,
uses the shared Legacy preprocessing/features, and performs inference only.
Reference ``rest`` sessions are kept separate from formal binary metrics.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix

from eeg_pipeline_utils import (
    extract_segment_features,
    load_eeg_recording,
    print_banner,
    print_metric,
    save_dataframe,
    save_json,
    sha256_file,
)
import legacy_baseline_v0 as baseline


SCRIPT_DIR = Path(__file__).resolve().parent
EVALUATION_VERSION = "locked_test_evaluation_v0"
LOCKED_DATE = "2026-09-07"
FORMAL_LABELS = ("unfocus", "focus")


def git_head(repo_root: Path) -> str:
    """Return the commit used as the test snapshot."""
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def load_and_validate_frozen_artifacts(
    baseline_dir: Path,
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    """Load the frozen model and reject hash/config/fitted-state mismatches."""
    pipeline_path = baseline_dir / "pipeline.joblib"
    config_path = baseline_dir / "config.json"
    freeze_path = baseline_dir / "freeze_manifest.json"
    for path in (pipeline_path, config_path, freeze_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing frozen artifact: {path}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    freeze_manifest = json.loads(freeze_path.read_text(encoding="utf-8"))
    for name, path in {"pipeline.joblib": pipeline_path, "config.json": config_path}.items():
        expected = freeze_manifest.get("artifact_sha256", {}).get(name)
        if not expected or sha256_file(path) != expected:
            raise AssertionError(f"Frozen artifact hash mismatch: {name}")
    if config.get("baseline_version") != baseline.BASELINE_VERSION:
        raise AssertionError("Frozen baseline version mismatch")
    if config.get("window_sec") != baseline.WINDOW_SEC or config.get("step_sec") != baseline.STEP_SEC:
        raise AssertionError("Frozen window configuration mismatch")
    if config.get("labels") != list(FORMAL_LABELS):
        raise AssertionError("Frozen label order is not [unfocus, focus]")

    pipeline = joblib.load(pipeline_path)
    if list(pipeline.named_steps) != ["scaler", "pca", "svc"]:
        raise AssertionError("Unexpected frozen pipeline steps")
    scaler, pca, svc = (pipeline.named_steps[name] for name in ("scaler", "pca", "svc"))
    if not hasattr(scaler, "mean_") or not hasattr(pca, "components_") or not hasattr(svc, "support_"):
        raise AssertionError("Frozen pipeline is not fitted")
    if pca.n_components != config["pca"]["n_components"]:
        raise AssertionError("Frozen PCA configuration mismatch")
    for parameter, expected in config["svc"].items():
        if svc.get_params()[parameter] != expected:
            raise AssertionError(f"Frozen SVC configuration mismatch: {parameter}")
    if int(scaler.n_features_in_) != 240:
        raise AssertionError(f"Unexpected frozen feature dimension: {scaler.n_features_in_}")
    return pipeline, config, freeze_manifest


def load_locked_manifest(repo_root: Path, manifest_path: Path) -> pd.DataFrame:
    """Load only the dated locked manifest and validate its roles/labels."""
    manifest_path = manifest_path.resolve()
    expected = (repo_root / "data" / "session_manifest.csv").resolve()
    if manifest_path != expected:
        raise RuntimeError("Locked evaluation accepts only data/session_manifest.csv")
    rows = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
    required = {
        "session_id", "subject_id", "recorded_date", "canonical_label", "dataset_role",
        "edf_path", "recording_duration_s", "activity_start_s", "activity_end_s",
        "window_sec", "step_sec", "sfreq_hz", "status",
    }
    missing = sorted(required - set(rows.columns))
    if missing:
        raise AssertionError(f"Locked manifest missing columns: {missing}")
    rows = rows.loc[rows["recorded_date"] == LOCKED_DATE].copy()
    if len(rows) != 7:
        raise AssertionError(f"Expected 7 sessions for {LOCKED_DATE}, got {len(rows)}")
    if set(rows["dataset_role"]) - {"locked_test", "locked_reference"}:
        raise AssertionError("Unsupported locked dataset role")
    formal = rows["dataset_role"].eq("locked_test")
    reference = rows["dataset_role"].eq("locked_reference")
    if set(rows.loc[formal, "canonical_label"]) != set(FORMAL_LABELS):
        raise AssertionError("Formal locked test must contain focus and unfocus")
    if not rows.loc[formal, "status"].eq("ready").all():
        raise AssertionError("Every formal locked session must be ready")
    if not rows.loc[reference, "canonical_label"].eq("rest").all():
        raise AssertionError("Reference session must be rest")
    for column in ("recording_duration_s", "activity_start_s", "activity_end_s", "window_sec", "step_sec", "sfreq_hz"):
        rows[column] = pd.to_numeric(rows[column], errors="raise")
    if not np.isclose(rows["window_sec"], baseline.WINDOW_SEC).all() or not np.isclose(rows["step_sec"], baseline.STEP_SEC).all():
        raise AssertionError("Locked manifest window parameters differ from frozen 4 s / 2 s")

    locked_root = (repo_root / "data" / "locked" / LOCKED_DATE).resolve()
    absolute_paths: list[Path] = []
    for value in rows["edf_path"]:
        path = (repo_root / value).resolve()
        if locked_root not in path.parents or path.suffix.lower() != ".edf":
            raise AssertionError(f"EDF is outside the expected locked directory: {path}")
        if not path.exists():
            raise FileNotFoundError(f"Locked EDF missing: {path}")
        absolute_paths.append(path)
    rows["edf_path_abs"] = absolute_paths
    return rows


def evaluate_one_session(pipeline: Any, row: pd.Series) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Extract frozen features and predict one independent locked session."""
    data, sfreq, _channels = load_eeg_recording(Path(row["edf_path_abs"]), allow_locked=True)
    X, starts = extract_segment_features(
        data,
        sfreq,
        float(row["activity_start_s"]),
        float(row["activity_end_s"]),
        baseline.BANDS,
        window_sec=baseline.WINDOW_SEC,
        step_sec=baseline.STEP_SEC,
        l_freq=baseline.FILTER_L_HZ,
        h_freq=baseline.FILTER_H_HZ,
    )
    expected_features = int(pipeline.named_steps["scaler"].n_features_in_)
    if X.shape[1] != expected_features:
        raise AssertionError(f"Feature dimension {X.shape[1]} != frozen dimension {expected_features}")
    predicted = pipeline.predict(X)
    predictions = pd.DataFrame(
        {
            "subject_id": str(row["subject_id"]),
            "session_id": str(row["session_id"]),
            "recording_id": str(row["session_id"]),
            "source_recording_id": "",
            "true_label": str(row["canonical_label"]),
            "predicted_label": predicted,
            "window_start_s": starts,
            "window_end_s": starts + baseline.WINDOW_SEC,
        }
    )
    true_label = str(row["canonical_label"])
    prediction_counts = predictions["predicted_label"].value_counts().reindex(FORMAL_LABELS, fill_value=0)
    summary = {
        "subject_id": str(row["subject_id"]),
        "session_id": str(row["session_id"]),
        "true_label": true_label,
        "windows": int(len(predictions)),
        "correct_windows": int((predictions["predicted_label"] == true_label).sum()),
        "session_accuracy": float(accuracy_score([true_label] * len(predictions), predictions["predicted_label"])),
        "predicted_focus_windows": int(prediction_counts["focus"]),
        "predicted_unfocus_windows": int(prediction_counts["unfocus"]),
        "focus_prediction_ratio": float(prediction_counts["focus"] / len(predictions)),
        "unfocus_prediction_ratio": float(prediction_counts["unfocus"] / len(predictions)),
    }
    return predictions, summary


def summarize_by_subject(session_metrics: pd.DataFrame) -> pd.DataFrame:
    """Aggregate formal session metrics by subject without changing predictions."""
    summaries: list[dict[str, Any]] = []
    for subject_id, subject in session_metrics.groupby("subject_id", sort=True):
        windows = int(subject["windows"].sum())
        summaries.append(
            {
                "subject_id": subject_id,
                "sessions": int(len(subject)),
                "windows": windows,
                "correct_windows": int(subject["correct_windows"].sum()),
                "subject_accuracy": float(subject["correct_windows"].sum() / windows),
                "focus_prediction_ratio": float(subject["predicted_focus_windows"].sum() / windows),
                "unfocus_prediction_ratio": float(subject["predicted_unfocus_windows"].sum() / windows),
            }
        )
    return pd.DataFrame(summaries)


def print_locked_summary(metrics: dict[str, Any]) -> None:
    """Print the compact locked-test summary used in the terminal."""
    print_metric("Formal sessions", metrics["formal_session_count"])
    print_metric("Reference sessions", metrics["reference_session_count_excluded"])
    print_metric("Windows", f"{metrics['total_windows']:,}")
    print_metric("Accuracy", f"{metrics['accuracy']:.2%}")
    print_metric("Balanced accuracy", f"{metrics['balanced_accuracy']:.2%}")
    cm = np.asarray(metrics["confusion_matrix"])
    print("\n  True \\ Pred       unfocus    focus")
    print(f"  unfocus          {cm[0, 0]:>8} {cm[0, 1]:>9}")
    print(f"  focus            {cm[1, 0]:>8} {cm[1, 1]:>9}")


def run_locked_evaluation(
    repo_root: Path,
    baseline_dir: Path,
    manifest_path: Path,
    output_dir: Path,
    expected_freeze_commit: str | None,
) -> dict[str, Any]:
    """Run the one-pass locked inference and save formal/reference outputs."""
    pipeline, config, _freeze_manifest = load_and_validate_frozen_artifacts(baseline_dir)
    current_commit = git_head(repo_root)
    if expected_freeze_commit is not None and current_commit != expected_freeze_commit:
        raise AssertionError(f"Current HEAD {current_commit} is not the requested freeze commit")
    rows = load_locked_manifest(repo_root, manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print_banner(f"LOCKED_TEST {LOCKED_DATE}")
    print("\nBaseline")
    print_metric("Version", config["baseline_version"])
    print_metric("Fit calls", 0)
    print("\nTest set")
    print_metric("Formal sessions", int((rows["dataset_role"] == "locked_test").sum()))
    print_metric("Reference", int((rows["dataset_role"] == "locked_reference").sum()))

    formal_predictions: list[pd.DataFrame] = []
    formal_summaries: list[dict[str, Any]] = []
    reference_predictions: list[pd.DataFrame] = []
    reference_summaries: list[dict[str, Any]] = []
    for _, row in rows.iterrows():
        print(f"  Predicting {row['session_id']}", flush=True)
        predictions, summary = evaluate_one_session(pipeline, row)
        if row["dataset_role"] == "locked_test":
            formal_predictions.append(predictions)
            formal_summaries.append(summary)
        else:
            reference_predictions.append(predictions)
            reference_summaries.append(summary)

    locked_predictions = pd.concat(formal_predictions, ignore_index=True)
    session_metrics = pd.DataFrame(formal_summaries).sort_values("session_id")
    subject_metrics = summarize_by_subject(session_metrics)
    reference_predictions_df = pd.concat(reference_predictions, ignore_index=True)
    reference_session_metrics = pd.DataFrame(reference_summaries).sort_values("session_id")
    true = locked_predictions["true_label"]
    predicted = locked_predictions["predicted_label"]
    cm = confusion_matrix(true, predicted, labels=list(FORMAL_LABELS))
    metrics = {
        "locked_date": LOCKED_DATE,
        "formal_dataset_role": "locked_test",
        "labels": list(FORMAL_LABELS),
        "confusion_matrix_label_order": ["unfocus", "focus"],
        "total_windows": int(len(locked_predictions)),
        "accuracy": float(accuracy_score(true, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(true, predicted)),
        "confusion_matrix": cm.astype(int).tolist(),
        "classification_report": classification_report(true, predicted, labels=list(FORMAL_LABELS), target_names=list(FORMAL_LABELS), output_dict=True, zero_division=0),
        "formal_session_count": int(len(session_metrics)),
        "reference_session_count_excluded": int(len(reference_session_metrics)),
        "reference_session_ids_excluded": reference_session_metrics["session_id"].tolist(),
        "training_performed": False,
    }

    print("\nOverall")
    print_locked_summary(metrics)
    save_dataframe(output_dir / "locked_predictions.csv", locked_predictions)
    save_dataframe(output_dir / "locked_session_metrics.csv", session_metrics)
    save_dataframe(output_dir / "locked_subject_metrics.csv", subject_metrics)
    save_json(output_dir / "locked_metrics.json", metrics)
    save_dataframe(output_dir / "reference_predictions.csv", reference_predictions_df)
    save_dataframe(output_dir / "reference_session_metrics.csv", reference_session_metrics)

    evaluation_script = Path(__file__).resolve()
    run_manifest = {
        "evaluation_version": EVALUATION_VERSION,
        "locked_date": LOCKED_DATE,
        "freeze_commit_sha": current_commit,
        "baseline_version": config["baseline_version"],
        "pipeline_sha256": sha256_file(baseline_dir / "pipeline.joblib"),
        "config_sha256": sha256_file(baseline_dir / "config.json"),
        "freeze_manifest_sha256": sha256_file(baseline_dir / "freeze_manifest.json"),
        "locked_manifest_path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "locked_manifest_sha256": sha256_file(manifest_path),
        "evaluation_script_path": str(evaluation_script.relative_to(repo_root)).replace("\\", "/"),
        "evaluation_script_sha256": sha256_file(evaluation_script),
        "training_performed": False,
        "fit_calls": 0,
        "predict_calls": int(len(rows)),
        "formal_session_ids": session_metrics["session_id"].tolist(),
        "excluded_reference_session_ids": reference_session_metrics["session_id"].tolist(),
        "output_sha256": {
            name: sha256_file(output_dir / name)
            for name in (
                "locked_predictions.csv", "locked_session_metrics.csv", "locked_subject_metrics.csv",
                "locked_metrics.json", "reference_predictions.csv", "reference_session_metrics.csv",
            )
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "run_manifest.json", run_manifest)
    result = {
        "freeze_commit_sha": current_commit,
        "output_dir": str(output_dir),
        "locked_metrics": metrics,
        "session_metrics": session_metrics.to_dict(orient="records"),
        "subject_metrics": subject_metrics.to_dict(orient="records"),
        "reference_session_metrics": reference_session_metrics.to_dict(orient="records"),
    }
    save_json(output_dir / "run_summary.json", result)
    print("\nSTATUS: FIRST LOCKED_TEST COMPLETE")
    return result


def check_existing_results(output_dir: Path) -> None:
    """Regression-check saved locked results without rereading locked EDFs."""
    metrics = json.loads((output_dir / "locked_metrics.json").read_text(encoding="utf-8"))
    predictions = pd.read_csv(output_dir / "locked_predictions.csv")
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["training_performed"] is False and manifest["fit_calls"] == 0
    assert len(predictions) == 2389
    assert abs(float(metrics["accuracy"]) - 0.552951) < 1e-6
    assert abs(float(metrics["balanced_accuracy"]) - 0.599068) < 1e-6
    assert metrics["confusion_matrix"] == [[636, 206], [862, 685]]
    print_banner(f"LOCKED_TEST {LOCKED_DATE} — regression check")
    print_metric("Formal sessions", metrics["formal_session_count"])
    print_metric("Reference sessions", metrics["reference_session_count_excluded"])
    print_metric("Windows", f"{len(predictions):,}")
    print_metric("Accuracy", f"{metrics['accuracy']:.2%}")
    print_metric("Balanced accuracy", f"{metrics['balanced_accuracy']:.2%}")
    cm = np.asarray(metrics["confusion_matrix"])
    print("\n  True \\ Pred       unfocus    focus")
    print(f"  unfocus          {cm[0, 0]:>8} {cm[0, 1]:>9}")
    print(f"  focus            {cm[1, 0]:>8} {cm[1, 1]:>9}")
    print("\nSTATUS: LOCKED_TEST REGRESSION CHECK PASSED")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse the explicit inference and no-write regression modes."""
    root = SCRIPT_DIR.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path, default=root / "artifacts" / "legacy_baseline_v0")
    parser.add_argument("--manifest", type=Path, default=root / "data" / "session_manifest.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "artifacts" / "locked_test" / LOCKED_DATE)
    parser.add_argument("--freeze-commit", default=None)
    parser.add_argument("--check-existing", action="store_true", help="Check saved results without reading EDFs.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    """Keep the top-level entry point to argument selection and business flow."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check_existing:
        check_existing_results(args.output_dir)
        return
    run_locked_evaluation(
        SCRIPT_DIR.parent,
        args.baseline_dir,
        args.manifest,
        args.output_dir,
        args.freeze_commit,
    )


if __name__ == "__main__":
    main()
