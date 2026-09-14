"""Build pooled/personal and cross-source common-channel comparisons.

The existing pooled and personal metrics are read from the prior frozen
LOCKED_TEST comparison. New author-common6, our-common6, and mixed-common6
pipelines use the shared EDF adapter and are evaluated with prediction-only
calls. Their cross-source interpretation is exploratory because the author
MAT reference is unknown.
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
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix

import evaluate_locked_test as locked_eval
import legacy_baseline_v0 as baseline
from cross_source_utils import (
    COMMON_6_CHANNELS,
    COMMON_7_CHANNELS,
    inspect_common6_edf_paths,
    inspect_common7_edf_paths,
    load_common6_edf_recording,
    load_common7_edf_recording,
)
from eeg_pipeline_utils import extract_segment_features, save_dataframe, save_json, sha256_file


MODEL_ORDER_BY_CHANNEL = {
    "common7": (
        "existing_pooled_frozen", "lyc_personal", "zyf_personal",
        "our_common7_pooled", "author_only", "our_author_mixed",
    ),
    "common6": (
        "existing_pooled_frozen", "lyc_personal", "zyf_personal",
        "author_common6", "our_common6_pooled", "our_author_mixed_common6",
    ),
}
MODEL_LABELS = {
    "existing_pooled_frozen": "Existing pooled frozen model",
    "lyc_personal": "lyc personal model",
    "zyf_personal": "zyf personal model",
    "our_common7_pooled": "our-common7 pooled model",
    "author_only": "author-only-7ch model",
    "our_author_mixed": "our+author mixed-common7 model",
    "author_common6": "author-common6 model",
    "our_common6_pooled": "our-common6 model",
    "our_author_mixed_common6": "mixed-common6 model",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def _safe_balanced(true: list[str], predicted: np.ndarray) -> float | None:
    if len(set(true)) < 2:
        return None
    return float(balanced_accuracy_score(true, predicted))


def _class_summary(predicted: Iterable[str]) -> tuple[dict[str, int], dict[str, float]]:
    values = pd.Series(list(predicted), dtype="string")
    counts = values.value_counts().reindex(baseline.LABELS, fill_value=0).astype(int)
    total = max(int(counts.sum()), 1)
    ratios = (counts / total).astype(float)
    return counts.to_dict(), ratios.to_dict()


def evaluate_channel_pipeline(
    pipeline: Any,
    repo_root: Path,
    *,
    channel_set: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate one new pipeline on formal LOCKED_TEST without calling fit."""
    rows = locked_eval.load_locked_manifest(repo_root, repo_root / "data" / "session_manifest.csv")
    rows = rows.loc[rows["dataset_role"].eq("locked_test")].copy()
    loader = load_common6_edf_recording if channel_set == "common6" else load_common7_edf_recording
    expected_channels = COMMON_6_CHANNELS if channel_set == "common6" else COMMON_7_CHANNELS
    outputs: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    session_rows: list[dict[str, Any]] = []

    for subject in ("lyc", "zyf"):
        subject_rows = rows.loc[rows["subject_id"].eq(subject)]
        true_all: list[str] = []
        predicted_all: list[str] = []
        for _, row in subject_rows.iterrows():
            data, sfreq, channels = loader(Path(row["edf_path_abs"]), allow_locked=True)
            if tuple(channels) != tuple(expected_channels):
                raise AssertionError(f"Unexpected {channel_set} channel order: {channels}")
            X, starts = extract_segment_features(
                data, sfreq, float(row["activity_start_s"]), float(row["activity_end_s"]),
                baseline.BANDS, window_sec=baseline.WINDOW_SEC, step_sec=baseline.STEP_SEC,
                l_freq=baseline.FILTER_L_HZ, h_freq=baseline.FILTER_H_HZ,
            )
            expected_features = int(pipeline.named_steps["scaler"].n_features_in_)
            if X.shape[1] != expected_features:
                raise AssertionError(f"{channel_set} feature dimension {X.shape[1]} != model dimension {expected_features}")
            predicted = np.asarray(pipeline.predict(X), dtype=object)
            true_label = str(row["canonical_label"])
            true = [true_label] * len(predicted)
            true_all.extend(true)
            predicted_all.extend(predicted.astype(str).tolist())
            counts, ratios = _class_summary(predicted.astype(str).tolist())
            session_rows.append({
                "model_id": "pending", "model": "pending", "test_subject": subject,
                "session_id": str(row["session_id"]), "true_label": true_label,
                "windows": int(len(predicted)), "accuracy": float(accuracy_score(true, predicted)),
                "balanced_accuracy": None,
                "predicted_class_counts": json.dumps(counts, ensure_ascii=False, sort_keys=True),
                "predicted_class_ratio": json.dumps(ratios, ensure_ascii=False, sort_keys=True),
            })
            prediction_frames.append(pd.DataFrame({
                "model_id": "pending", "model": "pending", "test_subject": subject,
                "session_id": str(row["session_id"]), "edf_path": str(row["edf_path"]),
                "true_label": true_label, "predicted_label": predicted.astype(str),
                "window_start_s": starts, "window_end_s": starts + baseline.WINDOW_SEC,
            }))
        predicted_array = np.asarray(predicted_all, dtype=object)
        counts, ratios = _class_summary(predicted_all)
        outputs.append({
            "test_subject": subject,
            "accuracy": float(accuracy_score(true_all, predicted_array)),
            "balanced_accuracy": _safe_balanced(true_all, predicted_array),
            "windows": int(len(true_all)),
            "predicted_class_counts": json.dumps(counts, ensure_ascii=False, sort_keys=True),
            "predicted_class_ratio": json.dumps(ratios, ensure_ascii=False, sort_keys=True),
            "confusion_matrix": json.dumps(confusion_matrix(true_all, predicted_array, labels=list(baseline.LABELS)).tolist()),
        })
    return pd.DataFrame(outputs), pd.concat(prediction_frames, ignore_index=True), pd.DataFrame(session_rows)


def _metric_from_existing(metrics: pd.DataFrame, model_id: str, subject: str) -> dict[str, Any]:
    row = metrics.loc[(metrics["model_id"] == model_id) & (metrics["test_subject"] == subject)]
    if row.empty:
        return {"accuracy": None, "balanced_accuracy": None, "windows": None,
                "predicted_class_counts": "", "predicted_class_ratio": "", "confusion_matrix": ""}
    value = row.iloc[0]
    counts = {"focus": int(value["predicted_focus_windows"]), "unfocus": int(value["predicted_unfocus_windows"])}
    ratios = {"focus": float(value["predicted_focus_proportion"]), "unfocus": float(value["predicted_unfocus_proportion"])}
    return {
        "accuracy": float(value["accuracy"]),
        "balanced_accuracy": None if pd.isna(value["balanced_accuracy"]) else float(value["balanced_accuracy"]),
        "windows": int(value["windows"]),
        "predicted_class_counts": json.dumps(counts, sort_keys=True),
        "predicted_class_ratio": json.dumps(ratios, sort_keys=True),
        "confusion_matrix": str(value["confusion_matrix"]),
    }


def _add_old_session_metrics(subject_comparison_dir: Path) -> pd.DataFrame:
    path = subject_comparison_dir / "session_metrics.csv"
    if not path.is_file():
        return pd.DataFrame()
    old = pd.read_csv(path)
    old["model_id"] = old["model_id"].replace({"pooled": "existing_pooled_frozen"})
    old["model"] = old["model_id"].map(MODEL_LABELS).fillna(old["model"])
    old["balanced_accuracy"] = None
    old["predicted_class_counts"] = old.apply(lambda row: json.dumps({
        "focus": int(row["predicted_focus_windows"]), "unfocus": int(row["predicted_unfocus_windows"])
    }, sort_keys=True), axis=1)
    old["predicted_class_ratio"] = old.apply(lambda row: json.dumps({
        "focus": float(row["predicted_focus_proportion"]), "unfocus": float(row["predicted_unfocus_proportion"])
    }, sort_keys=True), axis=1)
    return old[["model_id", "model", "test_subject", "session_id", "true_label", "windows",
                "accuracy", "balanced_accuracy", "predicted_class_counts", "predicted_class_ratio"]]


def build_unified_comparison(
    repo_root: Path,
    subject_comparison_dir: Path,
    author_dir: Path,
    common_dir: Path,
    mixed_dir: Path,
    output_dir: Path,
    *,
    channel_set: str = "common7",
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    subject_comparison_dir = subject_comparison_dir.resolve()
    author_dir, common_dir, mixed_dir, output_dir = [p.resolve() for p in (author_dir, common_dir, mixed_dir, output_dir)]
    if channel_set not in MODEL_ORDER_BY_CHANNEL:
        raise ValueError(f"Unsupported channel set: {channel_set}")
    model_order = MODEL_ORDER_BY_CHANNEL[channel_set]
    channels = COMMON_6_CHANNELS if channel_set == "common6" else COMMON_7_CHANNELS
    inspect_alignment = inspect_common6_edf_paths if channel_set == "common6" else inspect_common7_edf_paths
    alignment_name = f"{channel_set}_channel_alignment.csv"
    availability_column = f"{channel_set}_available"
    missing_column = f"missing_{channel_set}_channels"
    existing = pd.read_csv(subject_comparison_dir / "subject_model_comparison.csv")
    author_metrics_path, author_config_path = author_dir / "validation_metrics.json", author_dir / "config.json"
    author_metrics = json.loads(author_metrics_path.read_text(encoding="utf-8")) if author_metrics_path.is_file() else {}
    author_config = json.loads(author_config_path.read_text(encoding="utf-8")) if author_config_path.is_file() else {}

    locked_rows = locked_eval.load_locked_manifest(repo_root, repo_root / "data" / "session_manifest.csv")
    formal_paths = [Path(value) for value in locked_rows.loc[locked_rows["dataset_role"].eq("locked_test"), "edf_path_abs"]]
    alignment = inspect_alignment(formal_paths)
    available = bool(alignment[availability_column].all())
    missing = sorted({item for value in alignment[missing_column] for item in str(value).split(", ") if item})
    blocked_reason = f"missing explicit {channel_set} channel(s): {', '.join(missing)}" if missing else ""

    model_dirs = {
        ("author_common6" if channel_set == "common6" else "author_only"): author_dir,
        ("our_common6_pooled" if channel_set == "common6" else "our_common7_pooled"): common_dir,
        ("our_author_mixed_common6" if channel_set == "common6" else "our_author_mixed"): mixed_dir,
    }
    pipelines = {model_id: directory / "pipeline.joblib" for model_id, directory in model_dirs.items()
                 if (directory / "pipeline.joblib").is_file()}
    locked_results: dict[str, pd.DataFrame] = {}
    new_prediction_frames: list[pd.DataFrame] = []
    new_session_frames: list[pd.DataFrame] = []
    if available:
        for model_id, path in pipelines.items():
            aggregate, predictions, sessions = evaluate_channel_pipeline(joblib.load(path), repo_root, channel_set=channel_set)
            aggregate.insert(0, "model_id", model_id)
            aggregate.insert(1, "model", MODEL_LABELS[model_id])
            predictions["model_id"], predictions["model"] = model_id, MODEL_LABELS[model_id]
            sessions["model_id"], sessions["model"] = model_id, MODEL_LABELS[model_id]
            locked_results[model_id] = aggregate
            new_prediction_frames.append(predictions)
            new_session_frames.append(sessions)

    rows: list[dict[str, Any]] = []
    for model_id in model_order:
        for subject in ("lyc", "zyf"):
            status, note, heldout = "available", "", None
            if model_id == "existing_pooled_frozen":
                metric = _metric_from_existing(existing, "pooled", subject)
            elif model_id in {"lyc_personal", "zyf_personal"}:
                metric = _metric_from_existing(existing, model_id, subject)
            else:
                validation_path = model_dirs.get(model_id, author_dir) / "validation_metrics.json"
                validation = json.loads(validation_path.read_text(encoding="utf-8")) if validation_path.is_file() else {}
                heldout = validation.get("balanced_accuracy_mean")
                empty = {"accuracy": None, "balanced_accuracy": None, "windows": None,
                         "predicted_class_counts": "", "predicted_class_ratio": "", "confusion_matrix": ""}
                if not available:
                    metric, status, note = empty, "blocked", blocked_reason
                elif model_id in locked_results:
                    hit = locked_results[model_id].loc[locked_results[model_id]["test_subject"].eq(subject)].iloc[0]
                    metric = {key: hit[key] for key in ("accuracy", "balanced_accuracy", "windows", "predicted_class_counts", "predicted_class_ratio", "confusion_matrix")}
                else:
                    metric, status, note = empty, "missing_artifact", "model pipeline.joblib not found"
            rows.append({
                "model_id": model_id, "model": MODEL_LABELS[model_id], "test_subject": subject,
                "status": status, "accuracy": metric["accuracy"], "balanced_accuracy": metric["balanced_accuracy"],
                "windows": metric["windows"], "predicted_class_counts": metric["predicted_class_counts"],
                "predicted_class_ratio": metric["predicted_class_ratio"], "confusion_matrix": metric["confusion_matrix"],
                "author_or_cross_source_heldout_balanced_accuracy": heldout, "note": note,
            })

    table = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dataframe(output_dir / "unified_model_comparison.csv", table)
    save_dataframe(output_dir / alignment_name, alignment)
    old_predictions_path = subject_comparison_dir / "predictions.csv"
    old_predictions = pd.read_csv(old_predictions_path) if old_predictions_path.is_file() else pd.DataFrame()
    if not old_predictions.empty:
        old_predictions["model_id"] = old_predictions["model_id"].replace({"pooled": "existing_pooled_frozen"})
        old_predictions["model"] = old_predictions["model_id"].map(MODEL_LABELS).fillna(old_predictions["model"])
    new_predictions = pd.concat(new_prediction_frames, ignore_index=True) if new_prediction_frames else pd.DataFrame()
    save_dataframe(output_dir / "locked_predictions.csv", pd.concat([old_predictions, new_predictions], ignore_index=True))
    old_sessions = _add_old_session_metrics(subject_comparison_dir)
    new_sessions = pd.concat(new_session_frames, ignore_index=True) if new_session_frames else pd.DataFrame()
    save_dataframe(output_dir / "locked_session_metrics.csv", pd.concat([old_sessions, new_sessions], ignore_index=True))
    confusion_rows: list[dict[str, Any]] = []
    for model_id, aggregate in locked_results.items():
        for row in aggregate.to_dict(orient="records"):
            matrix = json.loads(row["confusion_matrix"])
            for i, true_label in enumerate(baseline.LABELS):
                for j, predicted_label in enumerate(baseline.LABELS):
                    confusion_rows.append({"model_id": model_id, "model": MODEL_LABELS[model_id],
                                           "test_subject": row["test_subject"], "true_label": true_label,
                                           "predicted_label": predicted_label, "count": int(matrix[i][j])})
    save_dataframe(output_dir / "locked_confusion_matrix.csv", pd.DataFrame(confusion_rows))

    author_7ch_metrics_path = repo_root / "artifacts" / "author_models" / "author_only" / "validation_metrics.json"
    author_7ch_metrics = json.loads(author_7ch_metrics_path.read_text(encoding="utf-8")) if author_7ch_metrics_path.is_file() else {}
    summary = {
        "comparison_version": "unified_cross_source_comparison_v2", "channel_set": channel_set,
        "models": {key: MODEL_LABELS[key] for key in model_order}, "required_channels": list(channels),
        "common6_mapping": {"F7-Pz": "F7", "F3-Pz": "F3", "T5-Pz": "P7", "O1-Pz": "O1", "O2-Pz": "O2", "T6-Pz": "P8"} if channel_set == "common6" else None,
        "common6_available_for_locked": available if channel_set == "common6" else None,
        "channel_available_for_locked": available, "blocked_reason": blocked_reason,
        "locked_test_fit_calls": 0,
        "locked_test_policy": "transform/predict/metric only; no fit, threshold tuning, or model selection",
        "cross_source_scope": "exploratory / channel-aligned but author MAT reference compatibility uncertain" if channel_set == "common6" else "not established for common7 cross-source EDF comparison",
        "our_edf_reference": "Pz confirmed", "author_mat_reference": "unknown", "reference_compatibility": "uncertain",
        "author_source_records": author_config.get("author_record_ids", []),
        "author_only_7ch_validation": {"accuracy_mean": author_7ch_metrics.get("accuracy_mean"), "balanced_accuracy_mean": author_7ch_metrics.get("balanced_accuracy_mean")},
        "author_common6_validation": {"accuracy_mean": author_metrics.get("accuracy_mean"), "balanced_accuracy_mean": author_metrics.get("balanced_accuracy_mean")} if channel_set == "common6" else None,
        "artifact_sha256": {model_id: sha256_file(path) for model_id, path in pipelines.items()},
        "old_frozen_comparison": str((subject_comparison_dir / "comparison_metrics.json").relative_to(repo_root)).replace("\\", "/"),
        "git_head": _git_head(repo_root), "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "comparison_summary.json", summary)
    _write_report(output_dir / "REPORT.md", table, summary, author_metrics, author_7ch_metrics)
    return summary


def _pct(value: Any) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{float(value):.2%}"


def _write_report(path: Path, table: pd.DataFrame, summary: dict[str, Any], author_metrics: dict[str, Any], author_7ch_metrics: dict[str, Any]) -> None:
    lines = [
        "# Unified pooled / personal / cross-source comparison", "",
        f"本报告使用 `{summary['channel_set']}` 特征协议。正式 2026-09-07 LOCKED_TEST 仅执行 transform/predict/metric；fit calls = `{summary['locked_test_fit_calls']}`。", "",
        "## Unified table", "",
        "| model | lyc accuracy | lyc balanced | zyf accuracy | zyf balanced | held-out balanced | status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for model_id in summary["models"]:
        model_rows = table.loc[table["model_id"].eq(model_id)]
        lyc = model_rows.loc[model_rows["test_subject"].eq("lyc")].iloc[0]
        zyf = model_rows.loc[model_rows["test_subject"].eq("zyf")].iloc[0]
        lines.append(f"| {lyc['model']} | {_pct(lyc['accuracy'])} | {_pct(lyc['balanced_accuracy'])} | {_pct(zyf['accuracy'])} | {_pct(zyf['balanced_accuracy'])} | {_pct(lyc['author_or_cross_source_heldout_balanced_accuracy'])} | {lyc['status']} |")
    lines.extend([
        "", "## Channel and reference status", "",
        f"- Required channel order: `{', '.join(summary['required_channels'])}`",
        "- Common6 adapter: `F7-Pz→F7, F3-Pz→F3, T5-Pz→P7, O1-Pz→O1, O2-Pz→O2, T6-Pz→P8`; `AF4` is excluded.",
        "- Our EDF / DSI-Streamer hardware reference: `Pz (confirmed)`.",
        "- Author MAT reference: `unknown`; therefore reference compatibility is `uncertain`.",
        f"- LOCKED_TEST channel availability: `{summary['channel_available_for_locked']}`{(' (' + summary['blocked_reason'] + ')') if summary['blocked_reason'] else ''}.",
        "- Cross-source status: `exploratory / channel-aligned but reference compatibility uncertain`.",
        "- Cross-source differences may reflect subject, session, device, task/paradigm, preprocessing representation, and unresolved author-reference differences.",
        "", "## Author-only channel ablation", "",
        "| author model | GroupKFold accuracy | GroupKFold balanced accuracy |", "|---|---:|---:|",
        f"| author-only-7ch | {_pct(author_7ch_metrics.get('accuracy_mean'))} | {_pct(author_7ch_metrics.get('balanced_accuracy_mean'))} |",
        f"| author-common6 | {_pct(author_metrics.get('accuracy_mean'))} | {_pct(author_metrics.get('balanced_accuracy_mean'))} |",
        "", "去掉 `AF4` 后仍沿用同一 recording-level GroupKFold；此表用于观察作者数据内部变化，不把它解释为跨设备效果。",
        "", "## Output details", "",
        "- `unified_model_comparison.csv`：按 model × test subject 的准确率、balanced accuracy、预测类别数量/比例和混淆矩阵。",
        "- `locked_predictions.csv`：旧 pooled/personal 预测与本轮 common6 预测的逐窗口记录。",
        "- `locked_session_metrics.csv`：逐 session accuracy、预测类别数量/比例；单一真实标签 session 的 balanced accuracy 记为 N/A。",
        "- `locked_confusion_matrix.csv`：本轮 common6 模型按 subject 的混淆矩阵长表。",
        "- `comparison_summary.json`：通道/reference 状态、fit policy、验证指标和新模型哈希。",
        "", "Existing pooled frozen、lyc personal、zyf personal 结果直接读取上一阶段比较，不重新训练、不覆盖旧 artifact。",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel-set", choices=("common7", "common6"), default="common7")
    parser.add_argument("--subject-comparison-dir", type=Path, default=root / "artifacts" / "subject_model_comparison" / locked_eval.LOCKED_DATE)
    parser.add_argument("--author-dir", type=Path, default=None)
    parser.add_argument("--common-dir", type=Path, default=None)
    parser.add_argument("--common7-dir", type=Path, default=None, help="Backward-compatible alias for --common-dir")
    parser.add_argument("--mixed-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = repo_root_from_script()
    if args.channel_set == "common6":
        defaults = (
            root / "artifacts" / "author_models" / "author_common6",
            root / "artifacts" / "our_common6_models" / "pooled_common6",
            root / "artifacts" / "mixed_models" / "our_author_mixed_common6",
            root / "artifacts" / "cross_source_comparison" / "2026-09-14",
        )
    else:
        defaults = (
            root / "artifacts" / "author_models" / "author_only",
            root / "artifacts" / "our_common7_models" / "pooled_common7",
            root / "artifacts" / "mixed_models" / "our_author_mixed",
            root / "artifacts" / "cross_source_comparison" / locked_eval.LOCKED_DATE,
        )
    author_dir = args.author_dir or defaults[0]
    common_dir = args.common_dir or args.common7_dir or defaults[1]
    mixed_dir = args.mixed_dir or defaults[2]
    output_dir = args.output_dir or defaults[3]
    summary = build_unified_comparison(root, args.subject_comparison_dir, author_dir, common_dir, mixed_dir, output_dir, channel_set=args.channel_set)
    print(f"{args.channel_set} available: {summary['channel_available_for_locked']}")
    print(f"report: {output_dir.resolve() / 'REPORT.md'}")


if __name__ == "__main__":
    main()
