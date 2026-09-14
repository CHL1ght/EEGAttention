"""Helpers shared by subject-dependent evaluation and the quick-test notebook.

This module deliberately delegates EDF loading, preprocessing, windowing, and
feature extraction to :mod:`eeg_pipeline_utils`.  It only adds strict identity
parsing and inference-time model bookkeeping around the existing pipeline.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from eeg_pipeline_utils import extract_segment_features, load_eeg_recording
import legacy_baseline_v0 as baseline
import evaluate_locked_test as locked_eval


PERSONAL_SUBJECTS = ("lyc", "zyf")
KNOWN_SUBJECTS = frozenset((*PERSONAL_SUBJECTS, "zqd"))
_STATUS_RE = re.compile(r"^(focus|unfocus|iu|ou|daze|rest|death)\d*$", re.IGNORECASE)

RAW_STATUS_TO_MODEL_LABEL: dict[str, str | None] = {
    **baseline.LABEL_MAPPING,
    "unfocus": "unfocus",
    "daze": None,
    "rest": None,
    "death": None,
}


def parse_edf_identity(edf_path: Path) -> dict[str, Any]:
    """Parse only an explicit ``subject_status_timestamp`` filename pattern.

    A numeric suffix on a status (for example ``focus1``) is accepted because
    it is part of the repository's locked-file naming convention.  No content
    or signal values are used to infer a subject.
    """

    stem = edf_path.stem
    fields = stem.split("_")
    subject_token = fields[0].casefold() if fields and fields[0] else ""
    raw_status_token = fields[1].casefold() if len(fields) >= 2 else ""
    timestamp = fields[2] if len(fields) >= 3 else ""
    subject = subject_token if subject_token in KNOWN_SUBJECTS else "unknown"
    warnings: list[str] = []

    if subject_token not in KNOWN_SUBJECTS:
        warnings.append("无法从文件名可靠确认 subject；不启用 personal model")

    status_match = _STATUS_RE.fullmatch(raw_status_token)
    if status_match is None:
        warnings.append("status 不在允许集合中；无法得到可靠 true label")
        raw_status = raw_status_token
    else:
        raw_status = status_match.group(1).casefold()

    if len(fields) < 3 or not timestamp or not timestamp.isdigit():
        warnings.append("文件名不符合 subject_status_timestamp 结构；无法得到可靠 true label")

    true_label: str | None = None
    if not warnings or (status_match is not None and timestamp.isdigit()):
        true_label = RAW_STATUS_TO_MODEL_LABEL.get(raw_status)
        if raw_status in {"daze", "rest", "death"}:
            warnings.append("该状态不是当前 focus/unfocus 二分类真值")

    if warnings:
        true_label = None if any("true label" in warning or "status" in warning for warning in warnings) else true_label

    return {
        "filename": edf_path.name,
        "subject": subject,
        "subject_token": subject_token,
        "subject_recognized": subject_token in KNOWN_SUBJECTS,
        "raw_status": raw_status,
        "timestamp": timestamp,
        "true_label": true_label,
        "personal_model_allowed": subject in PERSONAL_SUBJECTS,
        "warnings": warnings,
    }


def validate_fitted_pipeline(pipeline: Any, *, expected_features: int = 240) -> None:
    """Reject an artifact that is not the fitted shared Scaler/PCA/SVC chain."""

    if list(pipeline.named_steps) != ["scaler", "pca", "svc"]:
        raise AssertionError(f"Unexpected pipeline steps: {list(pipeline.named_steps)}")
    scaler, pca, svc = (pipeline.named_steps[name] for name in ("scaler", "pca", "svc"))
    if not hasattr(scaler, "mean_") or not hasattr(pca, "components_") or not hasattr(svc, "support_"):
        raise AssertionError("Pipeline is not fitted")
    if int(scaler.n_features_in_) != expected_features:
        raise AssertionError(f"Unexpected feature dimension: {scaler.n_features_in_}")
    if set(map(str, svc.classes_)) != set(baseline.LABELS):
        raise AssertionError(f"Unexpected model classes: {svc.classes_}")


def load_personal_pipeline(path: Path) -> Any:
    """Load and validate a personal model without calling ``fit``."""

    if not path.is_file():
        raise FileNotFoundError(f"Missing personal model: {path}")
    pipeline = joblib.load(path)
    validate_fitted_pipeline(pipeline)
    return pipeline


def _prediction_distribution(predicted: np.ndarray) -> pd.DataFrame:
    counts = pd.Series(predicted).value_counts().reindex(baseline.LABELS, fill_value=0)
    return pd.DataFrame(
        {
            "predicted_windows": counts.astype(int),
            "proportion": (counts / len(predicted)).astype(float),
        }
    )


def _summarize_predictions(
    model_label: str,
    predicted: np.ndarray,
    true_label: str | None,
) -> dict[str, Any]:
    distribution = _prediction_distribution(predicted)
    summary: dict[str, Any] = {
        "model": model_label,
        "window_total": int(len(predicted)),
        "true_label": true_label,
        "accuracy": None,
        "predicted_unfocus_windows": int(distribution.loc["unfocus", "predicted_windows"]),
        "predicted_unfocus_proportion": float(distribution.loc["unfocus", "proportion"]),
        "predicted_focus_windows": int(distribution.loc["focus", "predicted_windows"]),
        "predicted_focus_proportion": float(distribution.loc["focus", "proportion"]),
    }
    if true_label in baseline.LABELS:
        summary["accuracy"] = float(np.mean(predicted == true_label))
    return summary


def run_quick_comparison(
    edf_path: str | Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Run pooled plus the applicable personal model(s) on one EDF.

    This function is inference-only.  The pooled model is loaded through the
    existing frozen-artifact validator; personal artifacts are also checked
    for fitted Scaler/PCA/SVC state.  Feature extraction is performed once and
    shared by all models.
    """

    path = Path(edf_path).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"EDF 不存在: {path}")
    if path.suffix.casefold() != ".edf":
        raise ValueError(f"输入必须是 .edf 文件: {path}")

    identity = parse_edf_identity(path)
    pooled_dir = repo_root / "artifacts" / baseline.BASELINE_VERSION
    pooled_pipeline, _pooled_config, _freeze = locked_eval.load_and_validate_frozen_artifacts(pooled_dir)
    models: dict[str, Any] = {"pooled": pooled_pipeline}
    model_labels = {"pooled": "Existing pooled frozen model"}

    subject = identity["subject"]
    if subject in PERSONAL_SUBJECTS:
        personal_path = repo_root / "artifacts" / "subject_models" / subject / "pipeline.joblib"
        models["personal"] = load_personal_pipeline(personal_path)
        model_labels["personal"] = f"{subject} personal model"
    else:
        if subject == "zqd":
            print("⚠️ subject=zqd：按本阶段范围跳过 personal model，不参与个人模型评估。")
        else:
            print("⚠️ subject 无法可靠确认：按本阶段范围跳过 personal model，不猜测身份。")

    data, sfreq, channels = load_eeg_recording(path, allow_locked=True)
    duration_sec = data.shape[1] / sfreq
    X, window_starts = extract_segment_features(
        data,
        sfreq,
        0.0,
        duration_sec,
        baseline.BANDS,
        window_sec=baseline.WINDOW_SEC,
        step_sec=baseline.STEP_SEC,
        l_freq=baseline.FILTER_L_HZ,
        h_freq=baseline.FILTER_H_HZ,
    )
    if X.ndim != 2 or X.shape[1] != 240:
        raise AssertionError(f"Feature shape {X.shape} is not the shared 240-feature protocol")

    predictions: dict[str, pd.DataFrame] = {}
    distributions: dict[str, pd.DataFrame] = {}
    summaries: list[dict[str, Any]] = []
    for model_id, pipeline in models.items():
        predicted = np.asarray(pipeline.predict(X))
        model_predictions = pd.DataFrame(
            {
                "window_start_s": window_starts,
                "window_end_s": window_starts + baseline.WINDOW_SEC,
                "predicted_label": predicted,
            }
        )
        predictions[model_id] = model_predictions
        distributions[model_id] = _prediction_distribution(predicted)
        summaries.append(_summarize_predictions(model_labels[model_id], predicted, identity["true_label"]))

    model_summary = pd.DataFrame(summaries)
    print(f"\nEDF: {path.name}")
    print(f"subject={identity['subject']}; true_label={identity['true_label'] or 'unknown'}")
    print(f"EEG channels: {len(channels)}; shape: {data.shape}; sampling rate: {sfreq:g} Hz")
    print(f"duration: {duration_sec:.2f} s; feature matrix: {X.shape}")
    print("\nPooled vs personal summary:")
    print(model_summary.to_string(index=False))
    for warning in identity["warnings"]:
        print(f"⚠️ {warning}")

    return {
        "path": str(path),
        "filename_info": identity,
        "channels": channels,
        "sampling_rate_hz": float(sfreq),
        "features": X,
        "predictions": predictions,
        "distributions": distributions,
        "model_summary": model_summary,
        "metrics": {
            row["model"]: {key: value for key, value in row.items() if key != "model"}
            for row in summaries
        },
    }
