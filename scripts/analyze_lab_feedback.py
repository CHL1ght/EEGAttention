"""Run prediction-only analysis for the 2026-09-14 LAB_FEEDBACK EDFs.

This script deliberately consumes the existing frozen pipelines and writes
only exploratory analysis outputs. Canonical labels come from metadata, not
from the filename label and never from model predictions.
"""

from __future__ import annotations

import csv
import json
import sys
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import pandas as pd

from subject_model_utils import run_quick_comparison
from eeg_pipeline_utils import sha256_file


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data/exploratory/lab_feedback/2026-09-14"
OUTPUT_DIR = REPO_ROOT / "artifacts/lab_feedback/2026-09-14"
MODELS = ("pooled", "personal", "mixed_common6")
DISPLAY_MODELS = {
    "pooled": "pooled",
    "personal": "personal",
    "mixed_common6": "mixed-common6",
}
MODEL_ARTIFACTS = {
    "pooled": REPO_ROOT / "artifacts/legacy_baseline_v0/pipeline.joblib",
    "lyc personal": REPO_ROOT / "artifacts/subject_models/lyc/pipeline.joblib",
    "zyf personal": REPO_ROOT / "artifacts/subject_models/zyf/pipeline.joblib",
    "mixed-common6": REPO_ROOT / "artifacts/mixed_models/our_author_mixed_common6/pipeline.joblib",
}


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    frame = pd.DataFrame(rows)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def _pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    return f"{float(value):.2%}"


def _num(value: float | int | None, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    return f"{float(value):.{digits}f}"


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def _forbid_fit(*args: Any, **kwargs: Any) -> None:
    raise AssertionError("LAB_FEEDBACK 分析禁止 fit/fit_transform/partial_fit")


def _no_model_write(*args: Any, **kwargs: Any) -> None:
    raise AssertionError("LAB_FEEDBACK 分析禁止写出模型 artifact")


def _fit_guard(stack: ExitStack) -> None:
    """Block common estimator fitting and joblib writes during this run."""
    from sklearn.decomposition import PCA
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    for cls in (Pipeline, StandardScaler, PCA, SVC):
        for method in ("fit", "fit_transform", "partial_fit"):
            if hasattr(cls, method):
                stack.enter_context(patch.object(cls, method, _forbid_fit))
    import joblib

    stack.enter_context(patch.object(joblib, "dump", _no_model_write))


def _load_metadata() -> pd.DataFrame:
    metadata_path = DATA_DIR / "metadata.csv"
    metadata = pd.read_csv(metadata_path, dtype=str, keep_default_na=False)
    required = {
        "source_stem",
        "subject_id",
        "filename_label",
        "canonical_label",
        "label_source",
        "label_conflict",
        "label_conflict_note",
        "timestamp",
        "feedback_round",
        "feedback_seen_before_recording",
        "dataset_role",
        "experiment_version",
        "eligible_for_training",
        "eligible_for_validation",
        "eligible_for_final_test",
        "edf_path",
        "edf_sha256",
        "paired_files_complete",
    }
    missing = required.difference(metadata.columns)
    if missing:
        raise AssertionError(f"metadata 缺少字段: {sorted(missing)}")
    if len(metadata) != 11:
        raise AssertionError(f"metadata 应有11条，实际 {len(metadata)}")
    if set(metadata["canonical_label"]) - {"focus", "unfocus"}:
        raise AssertionError("canonical_label 含未知二分类标签")
    if not (metadata["eligible_for_training"] == "false").all():
        raise AssertionError("LAB_FEEDBACK 发现 training=true")
    if not (metadata["eligible_for_validation"] == "false").all():
        raise AssertionError("historical pilot 发现 validation=true")
    if not (metadata["eligible_for_final_test"] == "false").all():
        raise AssertionError("LAB_FEEDBACK 发现 final_test=true")
    if not (metadata["dataset_role"] == "historical_pilot").all():
        raise AssertionError("LAB_FEEDBACK dataset_role 不一致")
    if not (metadata["experiment_version"] == "pre_new_paradigm/lab_feedback_2026-09-14").all():
        raise AssertionError("LAB_FEEDBACK experiment_version 不一致")
    if not (metadata["feedback_round"] == "unknown").all():
        raise AssertionError("本批 feedback_round 不应由分析脚本推断")
    if not (metadata["feedback_seen_before_recording"] == "unknown").all():
        raise AssertionError("本批 feedback_seen_before_recording 不应由分析脚本推断")
    return metadata


def _prediction_row(meta: dict[str, str], model_id: str, result: dict[str, Any]) -> dict[str, Any]:
    predictions = result["predictions"][model_id]
    labels = predictions["predicted_label"].astype(str)
    total = int(len(labels))
    focus_count = int((labels == "focus").sum())
    unfocus_count = int((labels == "unfocus").sum())
    focus_prop = focus_count / total
    unfocus_prop = unfocus_count / total
    canonical = meta["canonical_label"]
    target_prop = focus_prop if canonical == "focus" else unfocus_prop
    accuracy = target_prop
    return {
        "subject": meta["subject_id"],
        "timestamp": meta["timestamp"],
        "filename": Path(meta["edf_path"]).name,
        "filename_label": meta["filename_label"],
        "canonical_label": canonical,
        "label_source": meta["label_source"],
        "label_conflict": meta["label_conflict"],
        "label_conflict_note": meta["label_conflict_note"],
        "feedback_round": meta["feedback_round"],
        "feedback_seen_before_recording": meta["feedback_seen_before_recording"],
        "model_id": DISPLAY_MODELS[model_id],
        "feature_dimension": int(result["feature_dimensions"][model_id]),
        "window_count": total,
        "accuracy": accuracy,
        "predicted_focus_count": focus_count,
        "predicted_focus_proportion": focus_prop,
        "predicted_unfocus_count": unfocus_count,
        "predicted_unfocus_proportion": unfocus_prop,
        "target_class_proportion": target_prop,
        "duration_s": float(result["duration_sec"]),
        "sampling_rate_hz": float(meta["sfreq_hz"]),
        "processing_sampling_rate_hz": float(result["sampling_rate_hz"]),
        "paired_files_complete": meta["paired_files_complete"],
    }


def _stability_rows(summary: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    grouped = summary.sort_values(["subject", "canonical_label", "timestamp"]).groupby(
        ["subject", "canonical_label", "model_id"], sort=True
    )
    for (subject, canonical, model_id), group in grouped:
        values = group["target_class_proportion"].astype(float).to_numpy()
        deltas = np.diff(values)
        rows.append(
            {
                "subject": subject,
                "canonical_label": canonical,
                "model_id": model_id,
                "session_count": int(len(values)),
                "mean_target_class_proportion": float(values.mean()),
                "min_target_class_proportion": float(values.min()),
                "max_target_class_proportion": float(values.max()),
                "range_target_class_proportion": float(values.max() - values.min()),
                "population_sd_target_class_proportion": float(values.std(ddof=0)),
                "mean_abs_chronological_step": float(np.abs(deltas).mean()) if len(deltas) else None,
            }
        )
    return rows


def _consistency_rows(summary: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (subject, timestamp, filename), group in summary.groupby(
        ["subject", "timestamp", "filename"], sort=False
    ):
        group = group.set_index("model_id")
        support = {model: bool(float(group.loc[model, "target_class_proportion"]) > 0.5) for model in DISPLAY_MODELS.values()}
        all_support = all(support.values())
        all_not_support = not any(support.values())
        disagreement = not (all_support or all_not_support)
        personal_only = (
            support["pooled"] == support["mixed-common6"]
            and support["personal"] != support["pooled"]
        )
        pooled_prop = float(group.loc["pooled", "target_class_proportion"])
        personal_prop = float(group.loc["personal", "target_class_proportion"])
        mixed_prop = float(group.loc["mixed-common6", "target_class_proportion"])
        rows.append(
            {
                "subject": subject,
                "timestamp": timestamp,
                "filename": filename,
                "canonical_label": group.iloc[0]["canonical_label"],
                "pooled_target_proportion": pooled_prop,
                "personal_target_proportion": personal_prop,
                "mixed_common6_target_proportion": mixed_prop,
                "pooled_supports_target": support["pooled"],
                "personal_supports_target": support["personal"],
                "mixed_common6_supports_target": support["mixed-common6"],
                "consistency_class": (
                    "all_three_support_target"
                    if all_support
                    else "all_three_not_supporting_target"
                    if all_not_support
                    else "model_disagreement"
                ),
                "personal_only_anomaly": personal_only,
                "mixed_minus_mean_of_pooled_personal": mixed_prop - float(np.mean([pooled_prop, personal_prop])),
            }
        )
    return rows


def _report(summary: pd.DataFrame, consistency: pd.DataFrame, stability: pd.DataFrame) -> str:
    summary = summary.sort_values(["subject", "timestamp", "filename", "model_id"])
    consistency = consistency.sort_values(["subject", "timestamp", "filename"])
    lines = [
        "# LAB_FEEDBACK 2026-09-14 prediction-only analysis",
        "",
        "本报告只描述已有 frozen pipeline 对现场 EDF 的 `predict()` 输出。没有训练、微调、calibration、阈值调整或重新保存模型。所有 accuracy 和 `target_class_proportion` 均使用 metadata 中的 `canonical_label`，不使用 filename label，也不使用模型输出修改标签。",
        "",
        "输入为每个 EDF 的全时长，复用既有 4 秒窗口、2 秒步长特征入口。pooled/personal 使用 240 维正式特征，mixed-common6 使用独立的 60 维 common6 特征。",
        "",
        "## 11 条 EDF 三模型结果",
        "",
    ]
    table_rows: list[list[str]] = []
    for (subject, timestamp, filename), group in summary.groupby(["subject", "timestamp", "filename"], sort=False):
        first = group.iloc[0]
        values = {row["model_id"]: row for _, row in group.iterrows()}
        table_rows.append(
            [
                subject,
                timestamp,
                filename,
                f"{first['filename_label']} → {first['canonical_label']}",
                first["label_source"],
                _pct(values["pooled"]["target_class_proportion"]),
                _pct(values["personal"]["target_class_proportion"]),
                _pct(values["mixed-common6"]["target_class_proportion"]),
            ]
        )
    lines.append(
        _md_table(
            ["subject", "timestamp", "EDF", "filename → canonical", "label source", "pooled target%", "personal target%", "mixed target%"],
            table_rows,
        )
    )
    lines.extend(["", "`target%` 与本批单一 canonical label 下的 window accuracy 数值相同，但含义仍以 canonical label 为准。", ""])

    lines.extend(["## A. 同一被试跨 session 波动", ""])
    lines.append("以下为同一 subject、同一 canonical label 内的描述性 session 波动；单 session 的组不作波动解释。")
    lines.append("")
    for subject in ("lyc", "zyf"):
        lines.append(f"### {subject}")
        subject_stability = stability[stability["subject"] == subject]
        if subject_stability.empty:
            lines.append("无结果。")
            lines.append("")
            continue
        for canonical in sorted(subject_stability["canonical_label"].unique()):
            group = subject_stability[subject_stability["canonical_label"] == canonical]
            n = int(group["session_count"].iloc[0])
            lines.append(f"- canonical `{canonical}`，n={n}：")
            for _, row in group.sort_values("model_id").iterrows():
                lines.append(
                    f"  - {row['model_id']}：range {_pct(row['range_target_class_proportion'])}，"
                    f"population SD {_pct(row['population_sd_target_class_proportion'])}，"
                    f"chronological mean absolute step {_pct(row['mean_abs_chronological_step'])}."
                )
        lines.append("")

    lines.extend(["## B. 三模型一致性", ""])
    all_wrong = consistency[consistency["consistency_class"] == "all_three_not_supporting_target"]
    personal_only = consistency[consistency["personal_only_anomaly"]]
    if all_wrong.empty:
        lines.append("按 `target proportion > 0.5` 支持 intended state 的规则，没有三模型都不支持 canonical label 的 session。")
    else:
        lines.append("按 `target proportion > 0.5` 支持 intended state 的规则，三模型都不支持 canonical label 的 session：")
        for _, row in all_wrong.iterrows():
            lines.append(
                f"- `{row['filename']}`（{row['subject']} {row['timestamp']}，canonical={row['canonical_label']}）："
                f"pooled {_pct(row['pooled_target_proportion'])}，personal {_pct(row['personal_target_proportion'])}，"
                f"mixed-common6 {_pct(row['mixed_common6_target_proportion'])}."
            )
    lines.append("")
    if personal_only.empty:
        lines.append("没有发现 personal 独自改变支持/不支持分类而 pooled 与 mixed-common6 同侧的 session。")
    else:
        lines.append("personal 独自异常（pooled 与 mixed-common6 同侧，personal 另一侧）：")
        for _, row in personal_only.iterrows():
            lines.append(f"- `{row['filename']}`（{row['subject']} {row['timestamp']}）。")
    lines.append("")

    lines.extend(["## C. 时间序列", "", "## chronological session sequence", ""])
    chronological_rows = []
    for _, row in consistency.sort_values(["subject", "timestamp", "filename"]).iterrows():
        chronological_rows.append(
            [
                row["subject"],
                row["timestamp"],
                row["filename"],
                row["canonical_label"],
                _pct(row["pooled_target_proportion"]),
                _pct(row["personal_target_proportion"]),
                _pct(row["mixed_common6_target_proportion"]),
            ]
        )
    lines.append(_md_table(["subject", "timestamp", "EDF", "canonical", "pooled", "personal", "mixed-common6"], chronological_rows))
    lines.extend(["", "时间只按真实 timestamp 排序；本表不将时间顺序解释为 feedback round，也不表示 feedback improvement 或 calibration 前后变化。", ""])

    lines.extend(["## zyf focus 17:52 与 18:10", ""])
    zyf_focus = summary[(summary["subject"] == "zyf") & (summary["canonical_label"] == "focus")]
    selected = zyf_focus[zyf_focus["timestamp"].str.contains("17:52|18:10", regex=True)]
    if len(selected) == 6:
        rows = []
        for timestamp, group in selected.groupby("timestamp", sort=True):
            values = {row["model_id"]: row for _, row in group.iterrows()}
            rows.append([timestamp, _pct(values["pooled"]["target_class_proportion"]), _pct(values["personal"]["target_class_proportion"]), _pct(values["mixed-common6"]["target_class_proportion"])])
        lines.append(_md_table(["timestamp", "pooled focus%", "zyf personal focus%", "mixed-common6 focus%"], rows))
        lines.append("")
        lines.append("这里仅比较两条 canonical focus recording 的描述性输出，不能据此下 calibration、attention state 因果或 feedback 效果结论。")
    else:
        lines.append("未找到恰好两条 zyf focus recording 的 17:52/18:10 三模型结果。")
    lines.append("")

    lines.extend(["## 稳定性与 shift 边界", ""])
    eligible = stability[stability["session_count"] >= 2]
    if eligible.empty:
        lines.append("没有至少两个相同 canonical label session 的组，不能比较 session 稳定性。")
    else:
        avg_sd = eligible.groupby("model_id")["population_sd_target_class_proportion"].mean().sort_values()
        ranking = ", ".join(f"{idx} {_pct(value)}" for idx, value in avg_sd.items())
        lines.append(f"在可比较组（同一 subject、同一 canonical label 且 n≥2）中，各模型 population SD 的组间平均为：{ranking}。")
        best = avg_sd.index[0]
        lines.append(f"按这个小样本描述性指标，离散度最低的是 `{best}`；这不是模型优越性或泛化结论。")
    lines.append("本批只有 2026-09-14 一天，不能识别 day shift。若把 session 间 target proportion 的差异称为 session shift，只能报告上述 range/SD；feedback round 全部 unknown，因此不能把它解释为 feedback-driven change。")
    lines.append("")
    lines.extend(["## 资格与运行保护", "", "- 11 条数据继续为 `dataset_role=historical_pilot`、`experiment_version=pre_new_paradigm/lab_feedback_2026-09-14`，且 training/validation/final-test eligibility 均为 `false`。", "- 没有写入 `legacy_manifest.csv`、`LOCKED_TEST`、New Paradigm v1 manifest 或 future final holdout。", "- 本次每个 recording × 3 model 均只调用 `predict()`；运行时 `fit_calls=0`，且禁止模型 artifact 写出。", "- 详细逐模型字段见 [session_model_summary.csv](session_model_summary.csv)，session 分类见 [session_consistency.csv](session_consistency.csv)，波动统计见 [session_stability.csv](session_stability.csv)。"])
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = _load_metadata()
    edfs = sorted(DATA_DIR.glob("*.edf"))
    if len(edfs) != 11:
        raise AssertionError(f"目录中应有11条EDF，实际 {len(edfs)}")
    by_filename = {Path(str(row["edf_path"])).name: row.to_dict() for _, row in metadata.iterrows()}
    if set(by_filename) != {path.name for path in edfs}:
        raise AssertionError("metadata 与实际 EDF 文件集合不一致")

    summary_rows: list[dict[str, Any]] = []
    run_records: list[dict[str, Any]] = []
    with ExitStack() as stack:
        _fit_guard(stack)
        for edf_path in edfs:
            meta = by_filename[edf_path.name]
            result = run_quick_comparison(edf_path, REPO_ROOT, verbose=False)
            if int(result.get("fit_calls", -1)) != 0:
                raise AssertionError(f"{edf_path.name}: inference entry reported fit_calls != 0")
            if result["feature_dimensions"] != {"pooled": 240, "personal": 240, "mixed_common6": 60}:
                raise AssertionError(f"{edf_path.name}: feature dimensions {result['feature_dimensions']}")
            if len(result["predictions"]) != 3:
                raise AssertionError(f"{edf_path.name}: expected three model predictions")
            for model_id in MODELS:
                summary_rows.append(_prediction_row(meta, model_id, result))
            run_records.append(
                {
                    "filename": edf_path.name,
                    "edf_sha256": sha256_file(edf_path),
                    "window_count": int(result["window_count"]),
                    "duration_s": float(result["duration_sec"]),
                    "raw_sampling_rate_hz": float(meta["sfreq_hz"]),
                    "processing_sampling_rate_hz": float(result["sampling_rate_hz"]),
                    "feature_dimensions": result["feature_dimensions"],
                    "fit_calls": int(result["fit_calls"]),
                    "models": [DISPLAY_MODELS[model] for model in MODELS],
                }
            )

    summary = pd.DataFrame(summary_rows)
    summary = summary.sort_values(["subject", "timestamp", "filename", "model_id"]).reset_index(drop=True)
    consistency = pd.DataFrame(_consistency_rows(summary)).sort_values(["subject", "timestamp", "filename"])
    stability = pd.DataFrame(_stability_rows(summary)).sort_values(["subject", "canonical_label", "model_id"])
    _write_csv(OUTPUT_DIR / "session_model_summary.csv", summary.to_dict(orient="records"))
    _write_csv(OUTPUT_DIR / "session_consistency.csv", consistency.to_dict(orient="records"))
    _write_csv(OUTPUT_DIR / "session_stability.csv", stability.to_dict(orient="records"))

    chronological = consistency.sort_values(["subject", "timestamp", "filename"]).copy()
    chronological.insert(0, "sequence_title", "chronological session sequence")
    chronological.to_csv(OUTPUT_DIR / "chronological_session_sequence.csv", index=False, encoding="utf-8-sig")
    (OUTPUT_DIR / "REPORT.md").write_text(_report(summary, consistency, stability), encoding="utf-8")

    model_hashes = {name: sha256_file(path) for name, path in MODEL_ARTIFACTS.items() if path.is_file()}
    manifest = {
        "analysis": "LAB_FEEDBACK 2026-09-14 exploratory prediction-only",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": str(Path(__file__).relative_to(REPO_ROOT)).replace("\\", "/"),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "input_edf_count": len(edfs),
        "input_records": run_records,
        "model_artifact_sha256": model_hashes,
        "training_performed": False,
        "prediction_only": True,
        "fit_calls": 0,
        "calibration_performed": False,
        "threshold_tuning_performed": False,
        "canonical_label_source": "metadata.csv: .md note > field/manual record > filename label",
        "feedback_round_policy": "unknown unless reliable explicit record; no chronological inference",
        "output_files": [
            "session_model_summary.csv",
            "session_consistency.csv",
            "session_stability.csv",
            "chronological_session_sequence.csv",
            "REPORT.md",
        ],
    }
    (OUTPUT_DIR / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"LAB_FEEDBACK prediction-only complete: {len(edfs)} EDF × 3 models")
    print(f"output={OUTPUT_DIR}")
    print("fit_calls=0")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
