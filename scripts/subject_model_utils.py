"""Helpers shared by subject-dependent evaluation and the quick-test notebook.

This module deliberately delegates EDF loading, preprocessing, windowing, and
feature extraction to :mod:`eeg_pipeline_utils`.  It only adds strict identity
parsing and inference-time model bookkeeping around the existing pipeline.
"""

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from eeg_pipeline_utils import extract_segment_features, load_eeg_recording, sha256_file
from cross_source_utils import COMMON_6_CHANNELS, load_common6_edf_recording
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
    valid_structure = len(fields) >= 3 and timestamp.isdigit()
    subject = subject_token if subject_token in KNOWN_SUBJECTS and valid_structure else "unknown"
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
        "subject_recognized": subject in KNOWN_SUBJECTS,
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


def load_mixed_common6_pipeline(repo_root: Path) -> Any:
    """Verify the saved mixed artifact and its ordered 60-feature contract."""
    directory = repo_root / "artifacts/mixed_models/our_author_mixed_common6"
    path = directory / "pipeline.joblib"
    config = json.loads((directory / "config.json").read_text(encoding="utf-8"))
    expected_hash = config.get("pipeline_sha256")
    if not expected_hash or sha256_file(path) != expected_hash:
        raise AssertionError("mixed-common6 模型 SHA-256 不匹配")
    protocol = config["feature_protocol"]
    if config["model_type"] != "our_author_mixed_common6":
        raise AssertionError("不是已登记的 mixed-common6 模型")
    if protocol["channels"] != list(COMMON_6_CHANNELS) or protocol["raw_feature_dimension"] != 60:
        raise AssertionError("mixed-common6 通道顺序或特征维数不匹配")
    pipeline = joblib.load(path)
    validate_fitted_pipeline(pipeline, expected_features=60)
    return pipeline


def _quick_features(path: Path, *, common6: bool) -> tuple[np.ndarray, np.ndarray, float, list[str], float]:
    """Select one channel space, then delegate all signal processing."""
    loader = load_common6_edf_recording if common6 else load_eeg_recording
    data, sfreq, channels = loader(path, allow_locked=True)
    duration = data.shape[1] / sfreq
    X, starts = extract_segment_features(
        data, sfreq, 0.0, duration, baseline.BANDS,
        window_sec=baseline.WINDOW_SEC, step_sec=baseline.STEP_SEC,
        l_freq=baseline.FILTER_L_HZ, h_freq=baseline.FILTER_H_HZ,
    )
    expected = 60 if common6 else 240
    if X.ndim != 2 or X.shape[1] != expected or len(X) == 0:
        raise AssertionError(f"特征矩阵 {X.shape} 不符合 {expected} 维协议")
    return X, starts, duration, channels, sfreq


def run_quick_comparison(
    edf_path: str | Path,
    repo_root: Path,
    *,
    verbose: bool = True,
) -> dict[str, Any]:
    """Predict pooled/personal on 240 features and mixed on 60 features.

    Whole-file lab feedback only; unlike formal manifest evaluation this uses
    [0, duration), without the formal 30-second buffers. Nothing is saved.
    The filename label is used only after predictions to compute metrics.
    """
    repo_root = Path(repo_root).resolve()
    path = Path(edf_path).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"EDF 不存在: {path}")
    if path.suffix.casefold() != ".edf":
        raise ValueError(f"输入必须是 .edf 文件: {path}")

    identity = parse_edf_identity(path)
    pooled, _, _ = locked_eval.load_and_validate_frozen_artifacts(
        repo_root / "artifacts" / baseline.BASELINE_VERSION
    )
    models = {"pooled": pooled}
    labels = {"pooled": "Existing pooled frozen"}
    descriptions = {"pooled": "历史多受试者通用基线（已冻结）"}
    notices = list(identity["warnings"])
    subject = identity["subject"]
    if subject in PERSONAL_SUBJECTS:
        models["personal"] = load_personal_pipeline(
            repo_root / "artifacts/subject_models" / subject / "pipeline.joblib"
        )
        labels["personal"] = f"{subject} personal"
        descriptions["personal"] = f"只用 {subject} 历史数据训练"
    else:
        notices.append(f"subject={subject}：personal = skipped；仍运行 pooled 和 mixed-common6。")
    models["mixed_common6"] = load_mixed_common6_pipeline(repo_root)
    labels["mixed_common6"] = "mixed-common6"
    descriptions["mixed_common6"] = "lyc+zyf 历史数据 + 作者23个 recording，共同6通道"

    full, starts, duration, channels, sfreq = _quick_features(path, common6=False)
    common, common_starts, common_duration, common_channels, common_fs = _quick_features(path, common6=True)
    if not np.array_equal(starts, common_starts) or duration != common_duration or sfreq != common_fs:
        raise AssertionError("两套通道特征没有使用相同时间窗口")
    if common_channels != list(COMMON_6_CHANNELS):
        raise AssertionError("COMMON6 通道顺序错误")
    features_by_model = {key: common if key == "mixed_common6" else full for key in models}
    predictions, distributions, summaries = {}, {}, []
    for model_id, pipeline in models.items():
        X = features_by_model[model_id]
        validate_fitted_pipeline(pipeline, expected_features=X.shape[1])
        predicted = np.asarray(pipeline.predict(X))
        predictions[model_id] = pd.DataFrame({
            "window_start_s": starts, "window_end_s": starts + baseline.WINDOW_SEC,
            "predicted_label": predicted,
        })
        distributions[model_id] = _prediction_distribution(predicted)
        summary = _summarize_predictions(labels[model_id], predicted, identity["true_label"])
        summary.update(model_id=model_id, description=descriptions[model_id], feature_dimension=X.shape[1])
        summaries.append(summary)

    table = pd.DataFrame(summaries)
    display_table = table[[
        "model", "description", "true_label", "accuracy",
        "predicted_focus_proportion", "predicted_unfocus_proportion",
    ]].rename(columns={
        "model": "Model", "description": "这个模型是什么", "true_label": "True label",
        "accuracy": "Accuracy", "predicted_focus_proportion": "Focus比例",
        "predicted_unfocus_proportion": "Unfocus比例",
    })
    notices.append("现场指标按全 EDF 计算；文件名标签是 intended label（预期状态），不是独立测量出的心理真值。")
    notices.append("mixed-common6：exploratory / channel-aligned but reference compatibility uncertain；Our reference=Pz，author reference=unknown。")
    if verbose:
        print(f"EDF: {path.name}\nsubject={subject}; true label={identity['true_label'] or 'unknown'}")
        print(f"duration={duration:.2f}s; windows={len(starts)}; pooled/personal=240维; mixed-common6=60维")
        printable = display_table.copy()
        for column in ("Accuracy", "Focus比例", "Unfocus比例"):
            printable[column] = printable[column].map(lambda x: "N/A" if pd.isna(x) else f"{x:.2%}")
        print(printable.to_string(index=False))
        for notice in notices:
            print(notice)
    return {
        "path": str(path), "filename_info": identity, "channels": channels,
        "common6_channels": common_channels, "sampling_rate_hz": float(sfreq),
        "duration_sec": duration, "window_count": len(starts),
        "features": full, "common6_features": common,
        "feature_dimensions": {key: X.shape[1] for key, X in features_by_model.items()},
        "predictions": predictions, "distributions": distributions,
        "model_summary": table, "display_table": display_table, "notices": notices,
        "fit_calls": 0,
        "metrics": {row["model"]: {key: value for key, value in row.items() if key != "model"} for row in summaries},
    }


def run_quick_test(edf_path: str | Path, repo_root: Path | None = None, *, verbose: bool = True) -> dict[str, Any]:
    """Single-EDF notebook/API entry; root defaults to this repository."""
    return run_quick_comparison(edf_path, repo_root or Path(__file__).resolve().parents[1], verbose=verbose)


def compare_quick_tests(
    edf_path_before: str | Path,
    edf_path_after: str | Path,
    repo_root: Path | None = None,
    *,
    verbose: bool = True,
) -> dict[str, Any]:
    """Compare two recordings with fixed models; never tune on feedback.

    Only the same known subject and binary label permit an improvement delta.
    File labels and identity do not alter predictions or select a threshold.
    """
    before = run_quick_test(edf_path_before, repo_root, verbose=False)
    after = run_quick_test(edf_path_after, repo_root, verbose=False)
    first, second = before["filename_info"], after["filename_info"]
    notices = list(dict.fromkeys([*before["notices"], *after["notices"]]))
    same_label = first["true_label"] in baseline.LABELS and first["true_label"] == second["true_label"]
    same_subject = first["subject"] in KNOWN_SUBJECTS and first["subject"] == second["subject"]
    distinct = before["path"] != after["path"]
    if not same_label:
        notices.append("两段标签不同或真值未知：不是同一状态的前后对照，不计算改善 Δ。")
    if not same_subject:
        notices.append("两段受试者不同或身份未确认：不计算个人前后改善 Δ。")
    if not distinct:
        notices.append("两次输入是同一个 EDF：只能核对重复推理，不计算改善 Δ。")
    comparable = same_label and same_subject and distinct
    if before["window_count"] != after["window_count"]:
        notices.append("两段窗口数不同；按各自完整录制的比例比较，不按窗口一一配对。")
    notices.append("前后差值是现场描述性反馈；不能据此证明因果改善或最终泛化。")

    left = before["model_summary"].set_index("model")
    right = after["model_summary"].set_index("model")
    records = []
    for model in dict.fromkeys([*left.index, *right.index]):
        a = left.loc[model] if model in left.index else None
        b = right.loc[model] if model in right.index else None
        a_acc = None if a is None else a["accuracy"]
        b_acc = None if b is None else b["accuracy"]
        target = first["true_label"] if same_label else None
        records.append({
            "Model": model, "Before Accuracy": a_acc, "After Accuracy": b_acc,
            "Δ Accuracy": float(b_acc - a_acc) if comparable and a is not None and b is not None else None,
            "Before target比例": a[f"predicted_{target}_proportion"] if target and a is not None else None,
            "After target比例": b[f"predicted_{target}_proportion"] if target and b is not None else None,
            "target": target,
        })
    comparison = pd.DataFrame(records)
    if verbose:
        for name, result in (("Before", before), ("After", after)):
            info = result["filename_info"]
            print(f"{name}: {Path(result['path']).name}; subject={info['subject']}; "
                  f"true label={info['true_label'] or 'unknown'}; "
                  f"duration={result['duration_sec']:.2f}s; windows={result['window_count']}")
        formatted = comparison.copy()
        for column in ("Before Accuracy", "After Accuracy", "Before target比例", "After target比例"):
            formatted[column] = formatted[column].map(lambda x: "N/A" if pd.isna(x) else f"{x:.2%}")
        formatted["Δ Accuracy"] = formatted["Δ Accuracy"].map(lambda x: "N/A" if pd.isna(x) else f"{x * 100:+.2f} 个百分点")
        print(formatted.to_string(index=False))
        for notice in notices:
            print(notice)
    return {"before": before, "after": after, "comparison": comparison,
            "improvement_comparable": comparable, "notices": notices, "fit_calls": 0}
