"""Run the frozen 2026-09-16 lyc New Paradigm v1 exploratory first pass.

This entry point deliberately accepts exactly three focus and three unfocus
sessions from the current New Paradigm manifest. Evaluation is leave-one-
session-out. The observe control is loaded only after the binary baseline and
full-data model have been saved and frozen, and is prediction-only.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix

import legacy_baseline_v0 as baseline
from eeg_pipeline_utils import (
    extract_segment_features,
    load_eeg_recording,
    save_dataframe,
    save_json,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/current/new_paradigm_v1/session_manifest.csv"
DATA_ROOT = (ROOT / "data/current/new_paradigm_v1").resolve()
OUTPUT_DIR = ROOT / "artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass"
RUN_ID = "2026-09-16_lyc_first_pass"
EXPECTED_BINARY_IDS = (
    "20260916_lyc_focus_01",
    "20260916_lyc_focus_02",
    "20260916_lyc_focus_03",
    "20260916_lyc_unfocus_01",
    "20260916_lyc_unfocus_02",
    "20260916_lyc_unfocus_03",
)
EXPECTED_OBSERVE_ID = "20260916_lyc_observe_01"
LABELS = baseline.LABELS


def _repo_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(DATA_ROOT):
        raise AssertionError(f"New Paradigm path escaped its data root: {value}")
    return path


def load_and_guard_manifest() -> tuple[pd.DataFrame, pd.Series]:
    rows = pd.read_csv(MANIFEST, dtype=str, keep_default_na=False)
    current = rows.loc[
        rows["paradigm_version"].eq("new_paradigm_v1")
        & rows["subject_id"].eq("lyc")
        & rows["recorded_date"].eq("2026-09-16")
    ].copy()
    binary = current.loc[
        current["canonical_label"].isin(LABELS)
        & current["dataset_role"].eq("train_candidate")
        & current["split_role"].eq("train")
        & current["status"].eq("ready")
    ].copy()
    if set(binary["session_id"]) != set(EXPECTED_BINARY_IDS) or len(binary) != 6:
        raise AssertionError("First pass requires exactly the six frozen binary session IDs")
    label_counts = binary["canonical_label"].value_counts().to_dict()
    if label_counts != {"focus": 3, "unfocus": 3}:
        raise AssertionError(f"Expected three sessions per binary label, got {label_counts}")

    observe_rows = current.loc[current["session_id"].eq(EXPECTED_OBSERVE_ID)]
    if len(observe_rows) != 1:
        raise AssertionError("First pass requires exactly one observe control")
    observe = observe_rows.iloc[0].copy()
    if not (
        observe["canonical_label"] == "observe"
        and observe["dataset_role"] == "reference"
        and observe["split_role"] == "excluded"
        and observe["status"] == "ready"
    ):
        raise AssertionError("Observe control must remain observe/reference/excluded/ready")

    for _, row in pd.concat([binary, observe_rows]).iterrows():
        edf = _repo_path(row["edf_path"])
        if not edf.is_file() or sha256_file(edf) != row["sha256"].lower():
            raise AssertionError(f"EDF missing or hash mismatch: {row['session_id']}")
        normalized = edf.as_posix().lower()
        forbidden = ("/historical/", "/legacy/", "/locked/", "/reference/", "/exploratory/")
        if any(token in normalized for token in forbidden):
            raise AssertionError(f"Forbidden non-current data source: {edf}")

    numeric = ("activity_start_s", "activity_end_s", "window_sec", "step_sec", "sfreq_hz")
    for column in numeric:
        binary[column] = pd.to_numeric(binary[column], errors="raise")
    if not np.isclose(binary["window_sec"], baseline.WINDOW_SEC).all():
        raise AssertionError("Binary sessions must use the frozen 4-second windows")
    if not np.isclose(binary["step_sec"], baseline.STEP_SEC).all():
        raise AssertionError("Binary sessions must use the frozen 2-second step")
    binary["edf_path_abs"] = binary["edf_path"].map(_repo_path)
    binary = binary.sort_values(["recorded_time", "session_id"]).reset_index(drop=True)
    return binary, observe


def extract_one_session(row: pd.Series) -> tuple[np.ndarray, pd.DataFrame, tuple[str, ...]]:
    path = _repo_path(str(row["edf_path"]))
    data, sfreq, channels = load_eeg_recording(path)
    features, starts = extract_segment_features(
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
    if features.ndim != 2 or features.shape[1] != 240 or len(features) == 0:
        raise AssertionError(f"Unexpected feature shape for {row['session_id']}: {features.shape}")
    metadata = pd.DataFrame(
        {
            "session_id": str(row["session_id"]),
            "canonical_label": str(row["canonical_label"]),
            "window_start_sec": starts,
            "window_sec": baseline.WINDOW_SEC,
            "step_sec": baseline.STEP_SEC,
            "model_sfreq_hz": sfreq,
        }
    )
    return features, metadata, tuple(channels)


def build_binary_features(binary: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame, tuple[str, ...]]:
    feature_parts: list[np.ndarray] = []
    metadata_parts: list[pd.DataFrame] = []
    channel_signature: tuple[str, ...] | None = None
    for _, row in binary.iterrows():
        features, metadata, channels = extract_one_session(row)
        if channel_signature is None:
            channel_signature = channels
        elif channels != channel_signature:
            raise AssertionError("Binary EDF sessions do not share one ordered EEG channel layout")
        feature_parts.append(features)
        metadata_parts.append(metadata)
    X = np.concatenate(feature_parts, axis=0)
    metadata = pd.concat(metadata_parts, ignore_index=True)
    y = metadata["canonical_label"].to_numpy(dtype=object)
    if not np.isfinite(X).all() or len(X) != len(y):
        raise AssertionError("Feature matrix is invalid")
    return X, y, metadata, channel_signature or ()


def focus_probability(pipeline, X: np.ndarray) -> np.ndarray:
    classes = list(map(str, pipeline.named_steps["svc"].classes_))
    if "focus" not in classes:
        raise AssertionError(f"Fitted SVC lacks focus class: {classes}")
    return pipeline.predict_proba(X)[:, classes.index("focus")]


def score_summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(np.min(values)),
        "q25": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "q75": float(np.quantile(values, 0.75)),
        "max": float(np.max(values)),
    }


def majority_vote(predictions: np.ndarray, probabilities: np.ndarray) -> tuple[str, str]:
    counts = {label: int(np.sum(predictions == label)) for label in LABELS}
    if counts["focus"] != counts["unfocus"]:
        return max(LABELS, key=lambda label: counts[label]), "majority_vote"
    label = "focus" if float(np.mean(probabilities)) >= 0.5 else "unfocus"
    return label, "majority_vote_tie_broken_by_mean_focus_probability"


def run_loso(
    X: np.ndarray,
    y: np.ndarray,
    metadata: pd.DataFrame,
    ordered_session_ids: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, int]:
    window_parts: list[pd.DataFrame] = []
    folds: list[dict[str, object]] = []
    fold_cm_rows: list[dict[str, object]] = []
    fit_calls = 0
    for fold_index, heldout_id in enumerate(ordered_session_ids, start=1):
        test_mask = metadata["session_id"].eq(heldout_id).to_numpy()
        train_mask = ~test_mask
        train_sessions = sorted(metadata.loc[train_mask, "session_id"].unique())
        if heldout_id in train_sessions or set(y[train_mask]) != set(LABELS):
            raise AssertionError(f"Session leakage or missing training class in fold {fold_index}")
        pipeline = baseline.build_baseline_pipeline()
        pipeline.fit(X[train_mask], y[train_mask])
        fit_calls += 1
        predictions = pipeline.predict(X[test_mask]).astype(str)
        probabilities = focus_probability(pipeline, X[test_mask])
        truth = y[test_mask].astype(str)
        true_label = str(np.unique(truth).item())
        session_prediction, vote_method = majority_vote(predictions, probabilities)
        cm = confusion_matrix(truth, predictions, labels=list(LABELS))
        pred_counts = {label: int(np.sum(predictions == label)) for label in LABELS}
        stats = score_summary(probabilities)
        folds.append(
            {
                "fold": fold_index,
                "heldout_session_id": heldout_id,
                "true_label": true_label,
                "predicted_label": session_prediction,
                "session_correct": bool(session_prediction == true_label),
                "vote_method": vote_method,
                "n_train_sessions": len(train_sessions),
                "train_session_ids": "|".join(train_sessions),
                "n_train_windows": int(train_mask.sum()),
                "n_test_windows": int(test_mask.sum()),
                "window_accuracy": float(accuracy_score(truth, predictions)),
                "pred_unfocus_windows": pred_counts["unfocus"],
                "pred_focus_windows": pred_counts["focus"],
                "mean_focus_probability": stats["mean"],
                "median_focus_probability": stats["median"],
                "min_focus_probability": stats["min"],
                "max_focus_probability": stats["max"],
                "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
            }
        )
        for true_index, true_name in enumerate(LABELS):
            for pred_index, pred_name in enumerate(LABELS):
                fold_cm_rows.append(
                    {
                        "fold": fold_index,
                        "heldout_session_id": heldout_id,
                        "true_label_axis": true_name,
                        "predicted_label_axis": pred_name,
                        "count": int(cm[true_index, pred_index]),
                    }
                )
        fold_windows = metadata.loc[test_mask].reset_index(drop=True).copy()
        fold_windows.insert(0, "fold", fold_index)
        fold_windows["true_label"] = truth
        fold_windows["predicted_label"] = predictions
        fold_windows["focus_probability"] = probabilities
        window_parts.append(fold_windows)

    windows = pd.concat(window_parts, ignore_index=True)
    if windows["session_id"].nunique() != 6 or len(windows) != len(metadata):
        raise AssertionError("Every binary window must be held out exactly once")
    return pd.DataFrame(folds), windows, pd.DataFrame(fold_cm_rows), fit_calls


def matrix_frame(values: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame(values.astype(int), index=LABELS, columns=LABELS).rename_axis(
        index="true_label", columns="predicted_label"
    ).reset_index()


def build_report(
    folds: pd.DataFrame,
    overall: dict[str, object],
    observe: dict[str, object],
) -> str:
    lines = [
        "# 2026-09-16 lyc New Paradigm v1 first pass",
        "",
        "## Scope",
        "",
        "Only the six 2026-09-16 lyc New Paradigm v1 binary sessions were used: three focus and three unfocus. No historical, 2026-09-14, author, common6, locked-test, or other data were read. Evaluation used complete-session leave-one-session-out with six folds.",
        "",
        "The preprocessing, feature extraction, and classifier parameters were copied unchanged from the existing baseline: 128 Hz resampling, 0.5–43 Hz FIR filtering, 4 s windows with 2 s step, Welch log/relative band power, StandardScaler, PCA retaining 95% variance, and balanced RBF SVC with C=10 and probability output.",
        "",
        "## Fold results",
        "",
        "| fold | held-out session | true | majority prediction | windows | window accuracy | mean focus probability | window confusion `[UU,UF;FU,FF]` |",
        "|---:|---|---|---|---:|---:|---:|---|",
    ]
    for _, row in folds.iterrows():
        if row["true_label"] == "unfocus":
            fold_matrix = [
                [int(row["pred_unfocus_windows"]), int(row["pred_focus_windows"])],
                [0, 0],
            ]
        else:
            fold_matrix = [
                [0, 0],
                [int(row["pred_unfocus_windows"]), int(row["pred_focus_windows"])],
            ]
        lines.append(
            f"| {int(row['fold'])} | `{row['heldout_session_id']}` | {row['true_label']} | "
            f"{row['predicted_label']} | {int(row['n_test_windows'])} | "
            f"{float(row['window_accuracy']):.2%} | {float(row['mean_focus_probability']):.4f} | "
            f"`{fold_matrix}` |"
        )
    lines.extend(
        [
            "",
            "## Overall held-out metrics",
            "",
            f"- Session-level accuracy: {float(overall['session_level_accuracy']):.2%}",
            f"- Session-level balanced accuracy: {float(overall['session_level_balanced_accuracy']):.2%}",
            f"- Window-level accuracy: {float(overall['window_level_accuracy']):.2%}",
            f"- Window-level balanced accuracy: {float(overall['window_level_balanced_accuracy']):.2%}",
            f"- Held-out windows: {int(overall['n_heldout_windows'])}",
            "",
            "Session confusion matrix (rows=true, columns=predicted; label order unfocus, focus):",
            "",
            f"- unfocus: {overall['session_confusion_matrix'][0]}",
            f"- focus: {overall['session_confusion_matrix'][1]}",
            "",
            "Window confusion matrix (rows=true, columns=predicted; label order unfocus, focus):",
            "",
            f"- unfocus: {overall['window_confusion_matrix'][0]}",
            f"- focus: {overall['window_confusion_matrix'][1]}",
            "",
            "## Observe prediction-only control",
            "",
            "The observe session was not used for fit, model selection, or any accuracy calculation. Its condition is: 认真观战王者、减少主动手部操作，用于运动/操作干扰对照。",
            "",
            f"- Session majority prediction: {observe['predicted_label']}",
            f"- Windows: {observe['n_windows']}",
            f"- Predicted focus windows: {observe['pred_focus_windows']} ({float(observe['pred_focus_proportion']):.2%})",
            f"- Mean focus probability: {float(observe['focus_probability']['mean']):.4f}",
            f"- Median focus probability: {float(observe['focus_probability']['median']):.4f}",
            f"- Focus probability range: {float(observe['focus_probability']['min']):.4f}–{float(observe['focus_probability']['max']):.4f}",
            "",
            "## Interpretation boundary",
            "",
            "**这是单日 6-session exploratory result，不代表跨日泛化。**",
            "",
            "All three focus sessions were recorded before all three unfocus sessions on the same day. Label is therefore confounded with recording order, so temporal, device, electrode, fatigue, or other session drift may contribute to the high score.",
            "",
            "No second-round tuning, feature changes, relabeling, threshold adjustment, or calibration was performed after seeing these results.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise RuntimeError(f"Refusing to overwrite non-empty first-pass output: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    binary, observe_row = load_and_guard_manifest()
    X, y, metadata, channels = build_binary_features(binary)
    ordered_ids = binary["session_id"].tolist()
    folds, windows, fold_confusions, fit_calls = run_loso(X, y, metadata, ordered_ids)

    session_cm = confusion_matrix(folds["true_label"], folds["predicted_label"], labels=list(LABELS))
    window_cm = confusion_matrix(windows["true_label"], windows["predicted_label"], labels=list(LABELS))
    overall = {
        "run_id": RUN_ID,
        "labels": list(LABELS),
        "n_sessions": 6,
        "n_folds": 6,
        "n_heldout_windows": int(len(windows)),
        "session_level_accuracy": float(accuracy_score(folds["true_label"], folds["predicted_label"])),
        "session_level_balanced_accuracy": float(
            balanced_accuracy_score(folds["true_label"], folds["predicted_label"])
        ),
        "window_level_accuracy": float(accuracy_score(windows["true_label"], windows["predicted_label"])),
        "window_level_balanced_accuracy": float(
            balanced_accuracy_score(windows["true_label"], windows["predicted_label"])
        ),
        "session_confusion_matrix": session_cm.astype(int).tolist(),
        "window_confusion_matrix": window_cm.astype(int).tolist(),
    }

    final_pipeline = baseline.build_baseline_pipeline()
    final_pipeline.fit(X, y)
    fit_calls += 1

    config = {
        "run_id": RUN_ID,
        "purpose": "single-day exploratory leave-one-session-out first pass",
        "data_scope": {
            "paradigm_version": "new_paradigm_v1",
            "subject_id": "lyc",
            "recorded_date": "2026-09-16",
            "binary_session_ids": ordered_ids,
            "observe_session_id": EXPECTED_OBSERVE_ID,
            "forbidden_sources": ["historical", "2026-09-14", "author", "common6", "locked-test"],
        },
        "evaluation": {
            "unit": "complete session/EDF",
            "method": "leave-one-session-out",
            "folds": 6,
            "same_edf_cross_split": False,
        },
        "preprocessing_and_features": {
            "implementation": "scripts/eeg_pipeline_utils.py",
            "target_sampling_rate_hz": 128.0,
            "filter_l_hz": baseline.FILTER_L_HZ,
            "filter_h_hz": baseline.FILTER_H_HZ,
            "window_sec": baseline.WINDOW_SEC,
            "step_sec": baseline.STEP_SEC,
            "bands_hz": {name: list(bounds) for name, bounds in baseline.BANDS.items()},
            "welch_nperseg_sec": baseline.WELCH_NPERSEG_SEC,
            "features": ["log_absolute_power", "relative_power"],
            "channel_order": list(channels),
            "n_features": int(X.shape[1]),
        },
        "model": {
            "implementation": "scripts/legacy_baseline_v0.py:build_baseline_pipeline",
            "steps": ["StandardScaler", "PCA", "SVC"],
            "pca_n_components": baseline.PCA_N_COMPONENTS,
            "svc": baseline.SVC_PARAMS,
            "parameter_search": False,
            "threshold_tuning": False,
            "calibration_added": False,
        },
        "observe_policy": "prediction-only after binary baseline freeze; excluded from fit and accuracy",
    }

    input_columns = [
        "session_id", "subject_id", "recorded_date", "recorded_time", "canonical_label",
        "task", "dataset_role", "split_role", "edf_path", "recording_duration_s",
        "activity_start_s", "activity_end_s", "window_sec", "step_sec", "sha256", "status",
    ]
    save_dataframe(OUTPUT_DIR / "input_sessions.csv", binary[input_columns])
    save_dataframe(OUTPUT_DIR / "fold_metrics.csv", folds)
    save_dataframe(OUTPUT_DIR / "fold_confusion_matrices.csv", fold_confusions)
    save_dataframe(OUTPUT_DIR / "window_predictions.csv", windows)
    save_dataframe(OUTPUT_DIR / "session_confusion_matrix.csv", matrix_frame(session_cm))
    save_dataframe(OUTPUT_DIR / "window_confusion_matrix.csv", matrix_frame(window_cm))
    save_json(OUTPUT_DIR / "overall_metrics.json", overall)
    save_json(OUTPUT_DIR / "config.json", config)
    model_path = OUTPUT_DIR / "binary_model.joblib"
    joblib.dump(final_pipeline, model_path)

    baseline_artifacts = [
        OUTPUT_DIR / "input_sessions.csv",
        OUTPUT_DIR / "fold_metrics.csv",
        OUTPUT_DIR / "fold_confusion_matrices.csv",
        OUTPUT_DIR / "window_predictions.csv",
        OUTPUT_DIR / "session_confusion_matrix.csv",
        OUTPUT_DIR / "window_confusion_matrix.csv",
        OUTPUT_DIR / "overall_metrics.json",
        OUTPUT_DIR / "config.json",
        model_path,
    ]
    freeze = {
        "run_id": RUN_ID,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_path": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha256_file(MANIFEST),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "artifact_sha256": {path.name: sha256_file(path) for path in baseline_artifacts},
        "fit_calls": fit_calls,
        "loso_fit_calls": 6,
        "full_binary_model_fit_calls": 1,
        "observe_fit_calls": 0,
        "observe_signal_loaded_before_freeze": False,
        "observe_bytes_read_for_sha256_during_manifest_guard": True,
        "non_current_data_read": False,
    }
    freeze_path = OUTPUT_DIR / "baseline_freeze_manifest.json"
    save_json(freeze_path, freeze)

    frozen_pipeline = joblib.load(model_path)
    observe_features, observe_meta, observe_channels = extract_one_session(observe_row)
    if observe_channels != channels:
        raise AssertionError("Observe control channel layout differs from binary sessions")
    observe_predictions = frozen_pipeline.predict(observe_features).astype(str)
    observe_probabilities = focus_probability(frozen_pipeline, observe_features)
    observe_label, observe_vote_method = majority_vote(observe_predictions, observe_probabilities)
    observe_counts = {label: int(np.sum(observe_predictions == label)) for label in LABELS}
    observe_output = observe_meta.drop(columns=["canonical_label"]).copy()
    observe_output["predicted_label"] = observe_predictions
    observe_output["focus_probability"] = observe_probabilities
    save_dataframe(OUTPUT_DIR / "observe_predictions.csv", observe_output)
    observe_summary = {
        "session_id": EXPECTED_OBSERVE_ID,
        "condition": "observe",
        "task": "认真观战王者、减少主动手部操作，用于运动/操作干扰对照",
        "ground_truth_binary_label": None,
        "included_in_fit": False,
        "included_in_model_selection": False,
        "included_in_accuracy": False,
        "prediction_only": True,
        "model_sha256": sha256_file(model_path),
        "predicted_label": observe_label,
        "vote_method": observe_vote_method,
        "n_windows": int(len(observe_predictions)),
        "pred_unfocus_windows": observe_counts["unfocus"],
        "pred_focus_windows": observe_counts["focus"],
        "pred_unfocus_proportion": float(observe_counts["unfocus"] / len(observe_predictions)),
        "pred_focus_proportion": float(observe_counts["focus"] / len(observe_predictions)),
        "focus_probability": score_summary(observe_probabilities),
    }
    save_json(OUTPUT_DIR / "observe_summary.json", observe_summary)
    report_path = OUTPUT_DIR / "REPORT.md"
    report_path.write_text(build_report(folds, overall, observe_summary), encoding="utf-8")

    final_artifacts = [
        *baseline_artifacts,
        freeze_path,
        OUTPUT_DIR / "observe_predictions.csv",
        OUTPUT_DIR / "observe_summary.json",
        report_path,
    ]
    run_manifest = {
        "run_id": RUN_ID,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_frozen_before_observe": True,
        "observe_prediction_only": True,
        "total_fit_calls": fit_calls,
        "fit_calls_after_observe_loaded": 0,
        "artifact_sha256": {path.name: sha256_file(path) for path in final_artifacts},
        "interpretation_boundary": "这是单日 6-session exploratory result，不代表跨日泛化。",
    }
    save_json(OUTPUT_DIR / "run_manifest.json", run_manifest)

    print(f"New Paradigm first pass complete: {OUTPUT_DIR}")
    print(json.dumps(overall, ensure_ascii=False, indent=2))
    print(json.dumps(observe_summary, ensure_ascii=False, indent=2))
    print(f"fit_calls={fit_calls}; observe_fit_calls=0; tuning_calls=0")


if __name__ == "__main__":
    main()
