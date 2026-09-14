"""Compare the frozen pooled model with lyc/zyf personal models.

The only evaluation data are formal ``LOCKED_TEST`` sessions from the existing
dated session manifest.  This script never calls ``fit`` and does not modify
the existing locked-test outputs or the frozen pooled artifact.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix

from eeg_pipeline_utils import extract_segment_features, load_eeg_recording, save_dataframe, save_json, sha256_file
import evaluate_locked_test as locked_eval
import legacy_baseline_v0 as baseline
from subject_model_utils import PERSONAL_SUBJECTS, load_personal_pipeline, validate_fitted_pipeline


COMPARISON_VERSION = "subject_model_comparison_v1"
MODEL_ORDER = ("pooled", "lyc_personal", "zyf_personal")
MODEL_LABELS = {
    "pooled": "Existing pooled frozen model",
    "lyc_personal": "lyc personal model",
    "zyf_personal": "zyf personal model",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_models(repo_root: Path, model_dir: Path) -> dict[str, Any]:
    """Load all three fitted artifacts, without any fitting operation."""

    pooled_dir = repo_root / "artifacts" / baseline.BASELINE_VERSION
    pooled, _config, _freeze = locked_eval.load_and_validate_frozen_artifacts(pooled_dir)
    validate_fitted_pipeline(pooled)
    models: dict[str, Any] = {"pooled": pooled}
    for subject in PERSONAL_SUBJECTS:
        path = model_dir / subject / "pipeline.joblib"
        models[f"{subject}_personal"] = load_personal_pipeline(path)
        config_path = model_dir / subject / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if config.get("subject") != subject or config.get("locked_test_read") is not False:
            raise AssertionError(f"Invalid personal model config: {config_path}")
    return models


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def _session_prediction_rows(
    model_id: str,
    row: pd.Series,
    starts: np.ndarray,
    predicted: np.ndarray,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "model_id": model_id,
            "model": MODEL_LABELS[model_id],
            "test_subject": str(row["subject_id"]),
            "session_id": str(row["session_id"]),
            "edf_path": str(row["edf_path"]),
            "true_label": str(row["canonical_label"]),
            "predicted_label": predicted,
            "window_start_s": starts,
            "window_end_s": starts + baseline.WINDOW_SEC,
        }
    )


def _summarize(predictions: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for group_values, group in predictions.groupby(group_columns, sort=True):
        if not isinstance(group_values, tuple):
            group_values = (group_values,)
        values = dict(zip(group_columns, group_values))
        true = group["true_label"]
        predicted = group["predicted_label"]
        counts = predicted.value_counts().reindex(baseline.LABELS, fill_value=0)
        rows.append(
            {
                **values,
                "sessions": int(group["session_id"].nunique()),
                "windows": int(len(group)),
                "accuracy": float(accuracy_score(true, predicted)),
                "balanced_accuracy": float(balanced_accuracy_score(true, predicted)),
                "predicted_unfocus_windows": int(counts["unfocus"]),
                "predicted_unfocus_proportion": float(counts["unfocus"] / len(group)),
                "predicted_focus_windows": int(counts["focus"]),
                "predicted_focus_proportion": float(counts["focus"] / len(group)),
                "confusion_matrix": confusion_matrix(true, predicted, labels=list(baseline.LABELS)).astype(int).tolist(),
            }
        )
    return pd.DataFrame(rows)


def evaluate_locked_comparison(
    repo_root: Path,
    model_dir: Path,
    manifest_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Evaluate pooled and both personal models on the same locked sessions."""

    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    model_dir = model_dir.resolve()
    output_dir = output_dir.resolve()
    models = load_models(repo_root, model_dir)
    rows = locked_eval.load_locked_manifest(repo_root, manifest_path)
    formal = rows.loc[rows["dataset_role"].eq("locked_test")].copy()
    if set(formal["subject_id"]) != set(PERSONAL_SUBJECTS):
        raise AssertionError("LOCKED_TEST comparison must contain only lyc and zyf")
    if formal["subject_id"].isin(["zqd"]).any():
        raise AssertionError("zqd is not allowed in this phase's cross evaluation")

    prediction_parts: list[pd.DataFrame] = []
    session_rows: list[dict[str, Any]] = []
    for _, row in formal.sort_values("session_id").iterrows():
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
        if X.shape[1] != 240:
            raise AssertionError(f"Feature dimension mismatch for {row['session_id']}: {X.shape}")
        for model_id in MODEL_ORDER:
            predicted = np.asarray(models[model_id].predict(X))
            predictions = _session_prediction_rows(model_id, row, starts, predicted)
            prediction_parts.append(predictions)
            counts = pd.Series(predicted).value_counts().reindex(baseline.LABELS, fill_value=0)
            session_rows.append(
                {
                    "model_id": model_id,
                    "model": MODEL_LABELS[model_id],
                    "test_subject": str(row["subject_id"]),
                    "session_id": str(row["session_id"]),
                    "true_label": str(row["canonical_label"]),
                    "windows": int(len(predicted)),
                    "accuracy": float(np.mean(predicted == str(row["canonical_label"]))),
                    "predicted_unfocus_windows": int(counts["unfocus"]),
                    "predicted_unfocus_proportion": float(counts["unfocus"] / len(predicted)),
                    "predicted_focus_windows": int(counts["focus"]),
                    "predicted_focus_proportion": float(counts["focus"] / len(predicted)),
                }
            )

    predictions_df = pd.concat(prediction_parts, ignore_index=True)
    subject_metrics = _summarize(predictions_df, ["model_id", "model", "test_subject"])
    session_metrics = pd.DataFrame(session_rows).sort_values(["model_id", "test_subject", "session_id"])
    test_sessions = formal[
        ["session_id", "subject_id", "canonical_label", "dataset_role", "edf_path", "activity_start_s", "activity_end_s"]
    ].sort_values("session_id")

    output_dir.mkdir(parents=True, exist_ok=True)
    save_dataframe(output_dir / "predictions.csv", predictions_df)
    save_dataframe(output_dir / "session_metrics.csv", session_metrics)
    save_dataframe(output_dir / "subject_model_comparison.csv", subject_metrics)
    save_dataframe(output_dir / "test_sessions.csv", test_sessions)

    comparison_rows = subject_metrics.to_dict(orient="records")
    summary = {
        "comparison_version": COMPARISON_VERSION,
        "locked_date": locked_eval.LOCKED_DATE,
        "labels": list(baseline.LABELS),
        "models": MODEL_LABELS,
        "test_subjects": list(PERSONAL_SUBJECTS),
        "formal_locked_sessions": test_sessions["session_id"].tolist(),
        "reference_sessions_excluded": rows.loc[rows["dataset_role"].eq("locked_reference"), "session_id"].tolist(),
        "fit_calls": 0,
        "training_performed": False,
        "locked_test_policy": "LOCKED_TEST used only for transform/predict/final metrics",
        "results": comparison_rows,
        "model_sha256": {
            "pooled": sha256_file(repo_root / "artifacts" / baseline.BASELINE_VERSION / "pipeline.joblib"),
            "lyc_personal": sha256_file(model_dir / "lyc" / "pipeline.joblib"),
            "zyf_personal": sha256_file(model_dir / "zyf" / "pipeline.joblib"),
        },
        "git_head": _git_head(repo_root),
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "comparison_metrics.json", summary)
    run_manifest = {
        "comparison_version": COMPARISON_VERSION,
        "locked_manifest_path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "locked_manifest_sha256": sha256_file(manifest_path),
        "training_performed": False,
        "fit_calls": 0,
        "reference_sessions_not_evaluated": summary["reference_sessions_excluded"],
        "output_sha256": {
            name: sha256_file(output_dir / name)
            for name in ("predictions.csv", "session_metrics.csv", "subject_model_comparison.csv", "test_sessions.csv", "comparison_metrics.json")
        },
        "git_head": _git_head(repo_root),
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "run_manifest.json", run_manifest)
    _write_report(output_dir / "REPORT.md", summary, subject_metrics, test_sessions)
    return summary


def _write_report(path: Path, summary: dict[str, Any], metrics: pd.DataFrame, test_sessions: pd.DataFrame) -> None:
    lines = [
        "# Subject-dependent model comparison",
        "",
        f"- Test set: `LOCKED_TEST {summary['locked_date']}`; reference rest sessions excluded.",
        "- Training: personal models fit only on their own historical `legacy_baseline_candidate` rows.",
        "- Leakage policy: this evaluator made `0` fit calls; locked data are prediction-only.",
        "- Labels: `unfocus`, `focus`; confusion matrices use that order.",
        "",
        "## Cross-evaluation matrix",
        "",
        "| Model | lyc test | zyf test |",
        "|---|---:|---:|",
    ]
    for model_id in MODEL_ORDER:
        values = []
        for subject in PERSONAL_SUBJECTS:
            match = metrics.loc[(metrics["model_id"] == model_id) & (metrics["test_subject"] == subject)]
            values.append(f"{float(match.iloc[0]['accuracy']):.2%}" if not match.empty else "n/a")
        lines.append(f"| {MODEL_LABELS[model_id]} | {values[0]} | {values[1]} |")
    lines.extend(
        [
            "",
            "## Sessions used",
            "",
            *[f"- `{row.session_id}` — subject `{row.subject_id}`, label `{row.canonical_label}`, `{row.edf_path}`" for row in test_sessions.itertuples()],
            "",
            "The table is a window-level accuracy comparison on the same independent locked sessions."
            " The personal models are not calibrated or fine-tuned in this phase.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "data" / "session_manifest.csv")
    parser.add_argument("--model-dir", type=Path, default=root / "artifacts" / "subject_models")
    parser.add_argument("--output-dir", type=Path, default=root / "artifacts" / "subject_model_comparison" / locked_eval.LOCKED_DATE)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = evaluate_locked_comparison(repo_root_from_script(), args.model_dir, args.manifest, args.output_dir)
    print("\nCross-evaluation matrix (accuracy)")
    metrics = pd.DataFrame(result["results"])
    for model_id in MODEL_ORDER:
        values = []
        for subject in PERSONAL_SUBJECTS:
            match = metrics.loc[(metrics["model_id"] == model_id) & (metrics["test_subject"] == subject)]
            values.append(f"{float(match.iloc[0]['accuracy']):.2%}")
        print(f"  {MODEL_LABELS[model_id]:<30} lyc={values[0]}  zyf={values[1]}")
    print(f"Saved comparison artifacts under {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
