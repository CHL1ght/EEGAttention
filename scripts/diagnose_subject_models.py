"""Diagnose lyc/zyf personal-model behavior without tuning or locked fitting.

This report combines historical class/session counts, existing locked-test
predictions, per-session prediction behavior, leave-one-session-group-out
validation, fitted-pipeline PCA diagnostics, and an explicit common-channel
check for the author-data phase.  LOCKED_TEST is read only for transform/
prediction-derived summaries; no scaler/PCA/SVC is fit on it.
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
from sklearn.metrics import accuracy_score, balanced_accuracy_score

import evaluate_locked_test as locked_eval
import legacy_baseline_v0 as baseline
from cross_source_utils import COMMON_7_CHANNELS, inspect_common7_edf_paths
from eeg_pipeline_utils import save_dataframe, save_json, sha256_file
from subject_model_utils import PERSONAL_SUBJECTS


DIAGNOSTIC_VERSION = "subject_model_diagnostics_v1"
MODEL_ORDER = ("pooled", "lyc_personal", "zyf_personal")
MODEL_LABELS = {
    "pooled": "Existing pooled frozen model",
    "lyc_personal": "lyc personal model",
    "zyf_personal": "zyf personal model",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def _safe_balanced_accuracy(true: Iterable[Any], predicted: Iterable[Any]) -> float | None:
    true_values = np.asarray(list(true), dtype=object)
    if len(np.unique(true_values)) < 2:
        return None
    return float(balanced_accuracy_score(true_values, np.asarray(list(predicted), dtype=object)))


def _distribution_row(
    *,
    dataset: str,
    subject: str,
    true_label: str,
    session_count: int,
    edf_count: int,
    window_count: int,
    total_windows: int,
) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "subject": subject,
        "true_label": true_label,
        "sessions": int(session_count),
        "edfs": int(edf_count),
        "windows": int(window_count),
        "window_proportion": float(window_count / total_windows) if total_windows else None,
        "total_windows": int(total_windows),
    }


def historical_distributions(
    repo_root: Path,
    manifest_path: Path,
) -> tuple[pd.DataFrame, dict[str, tuple[np.ndarray, np.ndarray, pd.DataFrame]]]:
    """Count historical subject data and build features for group-held-out folds."""
    rows = baseline.load_legacy_manifest(manifest_path, repo_root)
    outputs: list[dict[str, Any]] = []
    feature_sets: dict[str, tuple[np.ndarray, np.ndarray, pd.DataFrame]] = {}
    for subject in PERSONAL_SUBJECTS:
        subject_rows = rows.loc[rows["subject_id"].str.casefold().eq(subject)].copy()
        X, y, metadata = baseline.build_feature_dataset(subject_rows)
        feature_sets[subject] = (X, y, metadata)
        total_windows = len(y)
        for label in baseline.LABELS:
            label_rows = subject_rows.loc[subject_rows["canonical_label"].eq(label)]
            outputs.append(
                _distribution_row(
                    dataset="historical_training",
                    subject=subject,
                    true_label=label,
                    session_count=label_rows["session_group_id"].nunique(),
                    edf_count=label_rows["edf_path"].nunique(),
                    window_count=int(np.sum(y == label)),
                    total_windows=total_windows,
                )
            )
    return pd.DataFrame(outputs), feature_sets


def locked_distributions(predictions: pd.DataFrame) -> pd.DataFrame:
    """Count the true label distribution once per locked session/window."""
    required = {"test_subject", "session_id", "true_label", "model_id", "edf_path"}
    missing = sorted(required - set(predictions.columns))
    if missing:
        raise AssertionError(f"Comparison predictions missing columns: {missing}")
    truth = predictions.loc[predictions["model_id"].eq("pooled"), [
        "test_subject", "session_id", "edf_path", "true_label",
    ]].copy()
    if truth.empty:
        raise AssertionError("Existing comparison has no pooled locked predictions")
    outputs: list[dict[str, Any]] = []
    for subject in PERSONAL_SUBJECTS:
        subject_truth = truth.loc[truth["test_subject"].eq(subject)]
        total_windows = len(subject_truth)
        for label in baseline.LABELS:
            label_truth = subject_truth.loc[subject_truth["true_label"].eq(label)]
            outputs.append(
                _distribution_row(
                    dataset="locked_test",
                    subject=subject,
                    true_label=label,
                    session_count=label_truth["session_id"].nunique(),
                    edf_count=label_truth["edf_path"].nunique(),
                    window_count=len(label_truth),
                    total_windows=total_windows,
                )
            )
    return pd.DataFrame(outputs)


def prediction_bias(predictions: pd.DataFrame) -> pd.DataFrame:
    """Summarize true and predicted class proportions for every model/subject."""
    rows: list[dict[str, Any]] = []
    for (model_id, subject), group in predictions.groupby(["model_id", "test_subject"], sort=True):
        true_counts = group["true_label"].value_counts().reindex(baseline.LABELS, fill_value=0)
        predicted_counts = group["predicted_label"].value_counts().reindex(baseline.LABELS, fill_value=0)
        total = len(group)
        true_focus = float(true_counts["focus"] / total)
        predicted_focus = float(predicted_counts["focus"] / total)
        rows.append(
            {
                "model_id": model_id,
                "model": MODEL_LABELS.get(model_id, model_id),
                "test_subject": subject,
                "windows": int(total),
                "true_focus_windows": int(true_counts["focus"]),
                "true_focus_proportion": true_focus,
                "true_unfocus_windows": int(true_counts["unfocus"]),
                "true_unfocus_proportion": float(true_counts["unfocus"] / total),
                "predicted_focus_windows": int(predicted_counts["focus"]),
                "predicted_focus_proportion": predicted_focus,
                "predicted_unfocus_windows": int(predicted_counts["unfocus"]),
                "predicted_unfocus_proportion": float(predicted_counts["unfocus"] / total),
                "focus_proportion_delta": predicted_focus - true_focus,
                "accuracy": float(accuracy_score(group["true_label"], group["predicted_label"])),
                "balanced_accuracy": _safe_balanced_accuracy(group["true_label"], group["predicted_label"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["model_id", "test_subject"]).reset_index(drop=True)


def session_diagnostics(predictions: pd.DataFrame) -> pd.DataFrame:
    """Create one row per model × subject × locked EDF/session."""
    rows: list[dict[str, Any]] = []
    for (model_id, subject, session_id), group in predictions.groupby(
        ["model_id", "test_subject", "session_id"], sort=True
    ):
        true_counts = group["true_label"].value_counts().reindex(baseline.LABELS, fill_value=0)
        predicted_counts = group["predicted_label"].value_counts().reindex(baseline.LABELS, fill_value=0)
        majority = predicted_counts.sort_values(ascending=False, kind="stable").index[0]
        rows.append(
            {
                "model_id": model_id,
                "model": MODEL_LABELS.get(model_id, model_id),
                "subject": subject,
                "session_id": session_id,
                "filename": Path(str(group["edf_path"].iloc[0])).name,
                "true_label": str(group["true_label"].iloc[0]),
                "true_label_count": int(group["true_label"].nunique()),
                "windows": int(len(group)),
                "true_focus_windows": int(true_counts["focus"]),
                "true_unfocus_windows": int(true_counts["unfocus"]),
                "predicted_focus_windows": int(predicted_counts["focus"]),
                "predicted_unfocus_windows": int(predicted_counts["unfocus"]),
                "predicted_focus_proportion": float(predicted_counts["focus"] / len(group)),
                "predicted_unfocus_proportion": float(predicted_counts["unfocus"] / len(group)),
                "accuracy": float(accuracy_score(group["true_label"], group["predicted_label"])),
                "balanced_accuracy": _safe_balanced_accuracy(group["true_label"], group["predicted_label"]),
                "majority_prediction": str(majority),
            }
        )
    return pd.DataFrame(rows)


def historical_group_holdout(
    feature_sets: dict[str, tuple[np.ndarray, np.ndarray, pd.DataFrame]],
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Run Leave-One-Session-Group-Out using a fresh pipeline per fold."""
    fold_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    fit_calls = 0
    for subject in PERSONAL_SUBJECTS:
        X, y, metadata = feature_sets[subject]
        groups = sorted(metadata["session_group_id"].unique())
        subject_results: list[dict[str, Any]] = []
        for held_out_group in groups:
            test_mask = metadata["session_group_id"].eq(held_out_group).to_numpy()
            train_mask = ~test_mask
            if set(y[train_mask]) != set(baseline.LABELS):
                raise AssertionError(f"{subject} fold {held_out_group} train side lacks a class")
            pipeline = baseline.build_baseline_pipeline()
            pipeline.fit(X[train_mask], y[train_mask])
            fit_calls += 1
            predicted = pipeline.predict(X[test_mask])
            true = y[test_mask]
            balanced = _safe_balanced_accuracy(true, predicted)
            result = {
                "subject": subject,
                "held_out_session_group": held_out_group,
                "held_out_windows": int(test_mask.sum()),
                "held_out_labels": ",".join(sorted(set(true))),
                "train_session_groups": int(metadata.loc[train_mask, "session_group_id"].nunique()),
                "train_windows": int(train_mask.sum()),
                "accuracy": float(accuracy_score(true, predicted)),
                "balanced_accuracy": balanced,
                "balanced_accuracy_applicable": balanced is not None,
                "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
            }
            fold_rows.append(result)
            subject_results.append(result)
        acc = np.asarray([row["accuracy"] for row in subject_results], dtype=float)
        balanced_values = np.asarray(
            [row["balanced_accuracy"] for row in subject_results if row["balanced_accuracy"] is not None],
            dtype=float,
        )
        summary_rows.append(
            {
                "subject": subject,
                "evaluation": "leave_one_session_group_out",
                "folds": int(len(subject_results)),
                "accuracy_mean": float(acc.mean()),
                "accuracy_std": float(acc.std(ddof=1)) if len(acc) > 1 else 0.0,
                "balanced_accuracy_valid_folds": int(len(balanced_values)),
                "balanced_accuracy_mean": float(balanced_values.mean()) if len(balanced_values) else None,
                "balanced_accuracy_std": float(balanced_values.std(ddof=1)) if len(balanced_values) > 1 else (0.0 if len(balanced_values) else None),
                "balanced_accuracy_note": "N/A for held-out groups containing one true class",
            }
        )
    return pd.DataFrame(fold_rows), pd.DataFrame(summary_rows), fit_calls


def pca_diagnostics(repo_root: Path, model_dir: Path) -> pd.DataFrame:
    """Read PCA state from fitted artifacts without fitting or changing them."""
    paths = {
        "pooled": repo_root / "artifacts" / baseline.BASELINE_VERSION / "pipeline.joblib",
        "lyc_personal": model_dir / "lyc" / "pipeline.joblib",
        "zyf_personal": model_dir / "zyf" / "pipeline.joblib",
    }
    rows: list[dict[str, Any]] = []
    for model_id, path in paths.items():
        pipeline = joblib.load(path)
        scaler = pipeline.named_steps["scaler"]
        pca = pipeline.named_steps["pca"]
        rows.append(
            {
                "model_id": model_id,
                "model": MODEL_LABELS[model_id],
                "pipeline_path": str(path.relative_to(repo_root)).replace("\\", "/"),
                "raw_feature_dimension": int(scaler.n_features_in_),
                "pca_components": int(pca.n_components_),
                "explained_variance_ratio_sum": float(np.sum(pca.explained_variance_ratio_)),
                "pipeline_sha256": sha256_file(path),
            }
        )
    return pd.DataFrame(rows)


def _pct(value: Any) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{float(value):.2%}"


def _write_report(
    path: Path,
    *,
    summary: dict[str, Any],
    class_distribution: pd.DataFrame,
    bias: pd.DataFrame,
    session: pd.DataFrame,
    holdout_summary: pd.DataFrame,
    pca: pd.DataFrame,
    channel_alignment: pd.DataFrame,
) -> None:
    lines = [
        "# Personal model diagnostics",
        "",
        "本报告只做诊断，不做调参，不重训正式 personal model，也不在 LOCKED_TEST 上 fit。",
        "",
        "## 1. 数据分布",
        "",
        "| dataset | subject | true label | sessions | EDFs | windows | window proportion |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in class_distribution.itertuples():
        lines.append(
            f"| {row.dataset} | {row.subject} | {row.true_label} | {row.sessions} | {row.edfs} | {row.windows} | {_pct(row.window_proportion)} |"
        )
    lines.extend([
        "",
        "## 2. 预测类别偏置",
        "",
        "| model | test subject | accuracy | balanced accuracy | true focus | predicted focus | focus proportion delta |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in bias.itertuples():
        lines.append(
            f"| {row.model} | {row.test_subject} | {_pct(row.accuracy)} | {_pct(row.balanced_accuracy)} | {_pct(row.true_focus_proportion)} | {_pct(row.predicted_focus_proportion)} | {row.focus_proportion_delta:+.2%} |"
        )
    lines.extend([
        "",
        "重点组合 `lyc personal → zyf`：",
        f"- accuracy = {_pct(summary['lyc_personal_to_zyf_accuracy'])}；balanced accuracy = {_pct(summary['lyc_personal_to_zyf_balanced_accuracy'])}。",
        f"- true focus proportion = {_pct(summary['lyc_personal_to_zyf_true_focus_proportion'])}；predicted focus proportion = {_pct(summary['lyc_personal_to_zyf_predicted_focus_proportion'])}。",
        f"- 诊断判断：{summary['lyc_personal_to_zyf_bias_conclusion']}",
        "",
        "## 3. Session 级结果",
        "",
        "每个 EDF/session 的完整表见 `session_diagnostics.csv`；单一真实类别 session 的 balanced accuracy 标记为 N/A。",
        "",
        "## 4. Historical subject-internal held-out",
        "",
        "采用 Leave-One-Session-Group-Out。每个 fold 先按完整 session_group_id 分开，再只在 train fold fit Scaler/PCA/SVC。",
        "",
        "| subject | folds | accuracy mean | accuracy std | balanced valid folds | balanced mean | balanced std |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in holdout_summary.itertuples():
        lines.append(
            f"| {row.subject} | {row.folds} | {_pct(row.accuracy_mean)} | {_pct(row.accuracy_std)} | {row.balanced_accuracy_valid_folds} | {_pct(row.balanced_accuracy_mean)} | {_pct(row.balanced_accuracy_std)} |"
        )
    lines.extend([
        "",
        "## 5. PCA",
        "",
        "| model | raw feature dimension | PCA dimension | cumulative explained variance |",
        "|---|---:|---:|---:|",
    ])
    for row in pca.itertuples():
        lines.append(f"| {row.model} | {row.raw_feature_dimension} | {row.pca_components} | {_pct(row.explained_variance_ratio_sum)} |")
    lines.extend([
        "",
        "## 6. MAT / EDF common-7 channel check",
        "",
        f"Required explicit order: `{', '.join(COMMON_7_CHANNELS)}`。不把 T5/T6 等空间近似名称猜成 P7/P8。",
        "",
        "| EDF | sampling rate | common7 available | missing channels |",
        "|---|---:|---|---|",
    ])
    for row in channel_alignment.itertuples():
        lines.append(f"| `{Path(row.edf_path).name}` | {row.sampling_rate_hz:g} Hz | {row.common7_available} | {row.missing_common7_channels or '—'} |")
    lines.extend([
        "",
        f"结论：{summary['channel_conclusion']}",
        "",
        "## 7. 诊断结论",
        "",
        f"- Personal model 历史 held-out：{summary['historical_conclusion']}",
        f"- LOCKED_TEST / historical 对比：{summary['shift_conclusion']}",
        f"- 当前高 accuracy 组合：{summary['bias_conclusion']}",
        f"- 本次历史 held-out pipeline fit 次数：{summary['historical_fit_calls']}；LOCKED_TEST fit 次数：0。",
        "",
        "author-only 模型是否可以进一步测试 our EDF、以及 our-common7/mixed 模型，取决于上述明确通道对齐结果；如果缺少关键通道，本阶段不强行生成跨来源指标。",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_diagnostics(
    repo_root: Path,
    manifest_path: Path,
    comparison_dir: Path,
    model_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    comparison_dir = comparison_dir.resolve()
    model_dir = model_dir.resolve()
    output_dir = output_dir.resolve()
    predictions_path = comparison_dir / "predictions.csv"
    if not predictions_path.is_file():
        raise FileNotFoundError(f"Missing existing comparison predictions: {predictions_path}")

    historical_distribution, feature_sets = historical_distributions(repo_root, manifest_path)
    predictions = pd.read_csv(predictions_path)
    locked_distribution = locked_distributions(predictions)
    class_distribution = pd.concat([historical_distribution, locked_distribution], ignore_index=True)
    bias = prediction_bias(predictions)
    session = session_diagnostics(predictions)
    holdout_folds, holdout_summary, historical_fit_calls = historical_group_holdout(feature_sets)
    pca = pca_diagnostics(repo_root, model_dir)

    formal_manifest = locked_eval.load_locked_manifest(repo_root, repo_root / "data" / "session_manifest.csv")
    formal_paths = [Path(value) for value in formal_manifest.loc[formal_manifest["dataset_role"].eq("locked_test"), "edf_path_abs"]]
    channel_alignment = inspect_common7_edf_paths(formal_paths)

    focus_combo = bias.loc[(bias["model_id"] == "lyc_personal") & (bias["test_subject"] == "zyf")].iloc[0]
    bias_evidence = (
        float(abs(focus_combo["focus_proportion_delta"])) >= 0.20
        or float(focus_combo["accuracy"] - (focus_combo["balanced_accuracy"] or 0.0)) >= 0.10
        or float(max(focus_combo["predicted_focus_proportion"], 1.0 - focus_combo["predicted_focus_proportion"])) >= 0.85
    )
    if bias_evidence:
        bias_conclusion = "支持明显类别预测偏置；67.94% 类似的 accuracy 不能解释为稳定跨受试者泛化。"
    else:
        bias_conclusion = "未见足以单独判定为一边倒预测的证据，仍需结合 session 级结果解释。"

    historical_conclusion = []
    for row in holdout_summary.itertuples():
        metric = row.balanced_accuracy_mean if row.balanced_accuracy_mean is not None and not pd.isna(row.balanced_accuracy_mean) else row.accuracy_mean
        historical_conclusion.append(f"{row.subject} held-out {_pct(metric)}")
    if any(
        row.balanced_accuracy_mean is not None and not pd.isna(row.balanced_accuracy_mean) and row.balanced_accuracy_mean < 0.60
        for row in holdout_summary.itertuples()
    ):
        historical_text = "至少一个 subject 的历史 session-held-out 仍接近随机水平，更支持数据/任务可分性有限或数据量不足。"
    else:
        historical_text = "历史 held-out 结果不完全接近随机，不能仅凭 LOCKED_TEST 结果断言任务本身不可分。"
    historical_conclusion = "; ".join(historical_conclusion) + "；" + historical_text

    own_locked = bias.loc[bias["model_id"].isin(["lyc_personal", "zyf_personal"])].copy()
    shift_conclusion = "需要结合历史 held-out 与 locked 结果；本报告不把一次 locked 结果单独归因为某一原因。"
    for subject in PERSONAL_SUBJECTS:
        internal = holdout_summary.loc[holdout_summary["subject"].eq(subject), "balanced_accuracy_mean"]
        locked_row = bias.loc[(bias["model_id"] == f"{subject}_personal") & (bias["test_subject"] == subject)]
        if not internal.empty and not locked_row.empty and pd.notna(internal.iloc[0]) and pd.notna(locked_row.iloc[0]["balanced_accuracy"]):
            if float(internal.iloc[0]) - float(locked_row.iloc[0]["balanced_accuracy"]) >= 0.15:
                shift_conclusion = "历史 held-out 高于对应 LOCKED_TEST，结果支持 session/domain shift 是重要嫌疑，但不是唯一解释。"
                break

    if bool(channel_alignment["common7_available"].all()):
        channel_conclusion = "所有正式 locked EDF 均具备明确映射的 7 个共同通道，可以继续 author → EDF、our-common7 和 mixed。"
    else:
        missing = sorted({item for value in channel_alignment["missing_common7_channels"] for item in str(value).split(", ") if item})
        channel_conclusion = f"无法公平进行 author → EDF、our-common7 或 mixed：正式 locked EDF 缺少 {', '.join(missing)}；未使用 T5/T6 等空间近似替代。"

    output_dir.mkdir(parents=True, exist_ok=True)
    save_dataframe(output_dir / "class_distribution.csv", class_distribution)
    save_dataframe(output_dir / "prediction_bias.csv", bias)
    save_dataframe(output_dir / "session_diagnostics.csv", session)
    save_dataframe(output_dir / "historical_heldout_folds.csv", holdout_folds)
    save_dataframe(output_dir / "historical_heldout_summary.csv", holdout_summary)
    save_dataframe(output_dir / "pca_diagnostics.csv", pca)
    save_dataframe(output_dir / "common7_channel_alignment.csv", channel_alignment)

    summary = {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "historical_manifest": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "comparison_predictions": str(predictions_path.relative_to(repo_root)).replace("\\", "/"),
        "subjects": list(PERSONAL_SUBJECTS),
        "labels": list(baseline.LABELS),
        "historical_fit_calls": historical_fit_calls,
        "locked_test_fit_calls": 0,
        "locked_test_policy": "existing predictions only; no scaler/PCA/SVC fit on LOCKED_TEST",
        "lyc_personal_to_zyf_accuracy": float(focus_combo["accuracy"]),
        "lyc_personal_to_zyf_balanced_accuracy": None if pd.isna(focus_combo["balanced_accuracy"]) else float(focus_combo["balanced_accuracy"]),
        "lyc_personal_to_zyf_true_focus_proportion": float(focus_combo["true_focus_proportion"]),
        "lyc_personal_to_zyf_predicted_focus_proportion": float(focus_combo["predicted_focus_proportion"]),
        "lyc_personal_to_zyf_bias_conclusion": bias_conclusion,
        "historical_conclusion": historical_conclusion,
        "shift_conclusion": shift_conclusion,
        "bias_conclusion": bias_conclusion,
        "channel_conclusion": channel_conclusion,
        "common7_channels": list(COMMON_7_CHANNELS),
        "common7_available_for_formal_locked": bool(channel_alignment["common7_available"].all()),
        "git_head": _git_head(repo_root),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "diagnostic_summary.json", summary)
    run_manifest = {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "fit_policy": "historical LOGO folds fit only on train groups; locked predictions read from existing comparison artifact",
        "locked_test_fit_calls": 0,
        "input_sha256": {
            "legacy_manifest.csv": sha256_file(manifest_path),
            "comparison_predictions.csv": sha256_file(predictions_path),
        },
        "output_sha256": {
            name: sha256_file(output_dir / name)
            for name in (
                "class_distribution.csv", "prediction_bias.csv", "session_diagnostics.csv",
                "historical_heldout_folds.csv", "historical_heldout_summary.csv",
                "pca_diagnostics.csv", "common7_channel_alignment.csv", "diagnostic_summary.json",
            )
        },
        "git_head": _git_head(repo_root),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "run_manifest.json", run_manifest)
    _write_report(
        output_dir / "REPORT.md",
        summary=summary,
        class_distribution=class_distribution,
        bias=bias,
        session=session,
        holdout_summary=holdout_summary,
        pca=pca,
        channel_alignment=channel_alignment,
    )
    return summary


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "data" / "legacy_manifest.csv")
    parser.add_argument(
        "--comparison-dir",
        type=Path,
        default=root / "artifacts" / "subject_model_comparison" / locked_eval.LOCKED_DATE,
    )
    parser.add_argument("--model-dir", type=Path, default=root / "artifacts" / "subject_models")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "artifacts" / "subject_model_diagnostics" / locked_eval.LOCKED_DATE,
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    summary = run_diagnostics(
        repo_root_from_script(),
        args.manifest,
        args.comparison_dir,
        args.model_dir,
        args.output_dir,
    )
    print("Personal-model diagnostics complete")
    print(f"  historical LOGO fit calls: {summary['historical_fit_calls']}")
    print(f"  locked-test fit calls: {summary['locked_test_fit_calls']}")
    print(f"  common-7 available: {summary['common7_available_for_formal_locked']}")
    print(f"  report: {args.output_dir.resolve() / 'REPORT.md'}")


if __name__ == "__main__":
    main()
