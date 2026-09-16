"""Prediction-only replay of historical lyc gaming EEG sessions.

This script loads the frozen 2026-09-16 New Paradigm v1 first-pass model and
applies it to historical sessions whose task is reliably documented as lyc
playing Honor of Kings or another game.  It never fits, calibrates, tunes, or
updates any model component.
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import mne
import numpy as np
import pandas as pd
import scipy
import sklearn

import legacy_baseline_v0 as baseline
from eeg_pipeline_utils import (
    extract_segment_features,
    load_eeg_recording,
    save_dataframe,
    save_json,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
FROZEN_DIR = ROOT / "artifacts/current/new_paradigm_v1/2026-09-16_lyc_first_pass"
MODEL_PATH = FROZEN_DIR / "binary_model.joblib"
CONFIG_PATH = FROZEN_DIR / "config.json"
FREEZE_MANIFEST_PATH = FROZEN_DIR / "baseline_freeze_manifest.json"
FIRST_PASS_RUN_MANIFEST_PATH = FROZEN_DIR / "run_manifest.json"
OUTPUT_DIR = ROOT / "artifacts/current/new_paradigm_v1/2026-09-16_lyc_historical_game_replay"

LAB_FEEDBACK_MANIFEST = ROOT / "data/exploratory/lab_feedback/2026-09-14/metadata.csv"
LOCKED_MANIFEST = ROOT / "data/session_manifest.csv"
LEGACY_MANIFEST = ROOT / "data/legacy_manifest.csv"
LEGACY_EVIDENCE_NOTEBOOK = (
    ROOT / "notebooks/legacy/self_recorded/eeg_three_class_self_record_merged_iu_ou.ipynb"
)

RUN_ID = "2026-09-16_lyc_historical_game_replay"
EXPECTED_MODEL_SHA256 = "2b7b97f9f2399bcd3595df63a406fd66adfb470edc7f9390d8d67d45431d8e24"
EXPECTED_CONFIG_SHA256 = "a88db15b292574ad4f283f3255834214c60d4dcb1ceab5ef1dfa3d9126b91e24"
SEMANTIC_WARNING = "historical label is not guaranteed semantically equivalent to New Paradigm v1"
LABELS = baseline.LABELS


def repo_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise AssertionError(f"Input path escaped repository: {value}")
    return path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_frozen_baseline() -> tuple[Any, dict[str, Any], dict[str, str]]:
    """Verify every frozen artifact hash before loading the model."""
    freeze = load_json(FREEZE_MANIFEST_PATH)
    run_manifest = load_json(FIRST_PASS_RUN_MANIFEST_PATH)
    expected = run_manifest["artifact_sha256"]
    for name, expected_hash in expected.items():
        path = FROZEN_DIR / name
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise AssertionError(f"Frozen first-pass artifact missing or changed: {name}")
    if sha256_file(MODEL_PATH) != EXPECTED_MODEL_SHA256:
        raise AssertionError("Frozen model hash differs from the approved first-pass model")
    if sha256_file(CONFIG_PATH) != EXPECTED_CONFIG_SHA256:
        raise AssertionError("Frozen config hash differs from the approved first-pass config")
    if freeze["artifact_sha256"][MODEL_PATH.name] != EXPECTED_MODEL_SHA256:
        raise AssertionError("Freeze manifest does not identify the approved model")

    config = load_json(CONFIG_PATH)
    feature_config = config["preprocessing_and_features"]
    expected_bands = {name: list(bounds) for name, bounds in baseline.BANDS.items()}
    if feature_config["bands_hz"] != dict(sorted(expected_bands.items())):
        raise AssertionError("Frozen band definitions differ from baseline constants")
    if not (
        float(feature_config["target_sampling_rate_hz"]) == 128.0
        and float(feature_config["filter_l_hz"]) == baseline.FILTER_L_HZ
        and float(feature_config["filter_h_hz"]) == baseline.FILTER_H_HZ
        and float(feature_config["window_sec"]) == baseline.WINDOW_SEC
        and float(feature_config["step_sec"]) == baseline.STEP_SEC
        and int(feature_config["n_features"]) == 240
    ):
        raise AssertionError("Frozen preprocessing configuration is unexpected")

    pipeline = joblib.load(MODEL_PATH)
    if list(pipeline.named_steps) != ["scaler", "pca", "svc"]:
        raise AssertionError("Frozen pipeline steps are not scaler/PCA/SVC")
    if int(pipeline.named_steps["scaler"].n_features_in_) != 240:
        raise AssertionError("Frozen scaler does not expect 240 features")
    if set(map(str, pipeline.named_steps["svc"].classes_)) != set(LABELS):
        raise AssertionError("Frozen classifier classes are not focus/unfocus")
    frozen_hashes = {
        "binary_model.joblib": sha256_file(MODEL_PATH),
        "config.json": sha256_file(CONFIG_PATH),
        "baseline_freeze_manifest.json": sha256_file(FREEZE_MANIFEST_PATH),
        "run_manifest.json": sha256_file(FIRST_PASS_RUN_MANIFEST_PATH),
    }
    return pipeline, config, frozen_hashes


def build_included_sessions() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    lab = pd.read_csv(LAB_FEEDBACK_MANIFEST, dtype=str, keep_default_na=False)
    lab_selected = lab.loc[
        lab["subject_id"].eq("lyc")
        & lab["task"].str.contains("王者", regex=False)
    ].copy()
    if len(lab_selected) != 7:
        raise AssertionError(f"Expected seven documented 2026-09-14 lyc 王者 sessions, got {len(lab_selected)}")
    for _, row in lab_selected.iterrows():
        label = str(row["canonical_label"])
        rows.append(
            {
                "historical_date": row["recorded_date"],
                "session_id": row["session_id"],
                "filename": row["original_filename"],
                "edf_path": row["edf_path"],
                "expected_edf_sha256": row["edf_sha256"],
                "historical_label": label,
                "task": f"{row['task']}（{row['mode']}）",
                "notes": row["subjective_state"],
                "original_context": "明确记录为玩王者/排位",
                "evidence_source": LAB_FEEDBACK_MANIFEST.relative_to(ROOT).as_posix(),
                "evidence_tier": "confirmed_honor_of_kings",
                "serious_honor_of_kings": label == "focus",
                "recording_duration_s": float(row["recording_duration_s"]),
                "activity_start_s": 0.0,
                "activity_end_s": float(row["recording_duration_s"]),
            }
        )

    locked = pd.read_csv(LOCKED_MANIFEST, dtype=str, keep_default_na=False)
    locked_selected = locked.loc[
        locked["subject_id"].eq("lyc")
        & locked["notes"].str.contains("王者荣耀", regex=False)
    ].copy()
    if len(locked_selected) != 1 or locked_selected.iloc[0]["session_id"] != "20260907_lyc_focus_02":
        raise AssertionError("Expected exactly one documented 2026-09-07 lyc 王者 session")
    for _, row in locked_selected.iterrows():
        rows.append(
            {
                "historical_date": row["recorded_date"],
                "session_id": row["session_id"],
                "filename": Path(row["edf_path"]).name,
                "edf_path": row["edf_path"],
                "expected_edf_sha256": row["sha256"],
                "historical_label": row["canonical_label"],
                "task": "王者荣耀",
                "notes": row["notes"],
                "original_context": "明确记录为王者荣耀专注录制",
                "evidence_source": LOCKED_MANIFEST.relative_to(ROOT).as_posix(),
                "evidence_tier": "confirmed_honor_of_kings",
                "serious_honor_of_kings": True,
                "recording_duration_s": float(row["recording_duration_s"]),
                "activity_start_s": float(row["activity_start_s"]),
                "activity_end_s": float(row["activity_end_s"]),
            }
        )

    legacy = pd.read_csv(LEGACY_MANIFEST, dtype=str, keep_default_na=False)
    legacy_selected = legacy.loc[
        legacy["subject_id"].eq("lyc")
        & legacy["edf_path"].str.startswith("data/legacy/multiclass_10min/")
        & legacy["canonical_label"].isin(LABELS)
    ].copy()
    if len(legacy_selected) != 16:
        raise AssertionError(f"Expected 16 documented legacy lyc gaming sessions, got {len(legacy_selected)}")
    notebook_text = LEGACY_EVIDENCE_NOTEBOOK.read_text(encoding="utf-8")
    if "专注打游戏" not in notebook_text or "分心打游戏" not in notebook_text:
        raise AssertionError("Legacy notebook no longer contains the gaming-task evidence")
    for _, row in legacy_selected.iterrows():
        label = str(row["canonical_label"])
        if label == "focus":
            task = "专注打游戏"
            context = "lyc 早期自录专注 gaming；具体游戏名称未记录"
        else:
            task = "分心打游戏"
            context = "lyc 早期自录分心 gaming（iu/ou 合并）；具体游戏名称未记录"
        rows.append(
            {
                "historical_date": row["recorded_date"],
                "session_id": row["recording_id"],
                "filename": Path(row["edf_path"]).name,
                "edf_path": row["edf_path"],
                "expected_edf_sha256": row["sha256"],
                "historical_label": label,
                "task": task,
                "notes": row["notes"],
                "original_context": context,
                "evidence_source": LEGACY_EVIDENCE_NOTEBOOK.relative_to(ROOT).as_posix(),
                "evidence_tier": "confirmed_gaming_title_unspecified",
                "serious_honor_of_kings": False,
                "recording_duration_s": float(row["recording_duration_s"]),
                "activity_start_s": float(row["activity_start_s"]),
                "activity_end_s": float(row["activity_end_s"]),
            }
        )

    result = pd.DataFrame(rows).sort_values(["historical_date", "session_id"], ascending=[False, True])
    if len(result) != 24 or result["session_id"].duplicated().any():
        raise AssertionError("Reliable historical gaming selection must contain 24 unique sessions")
    return result.reset_index(drop=True)


def build_candidate_audit(included: pd.DataFrame) -> pd.DataFrame:
    audit_rows = [
        {
            "candidate": row["session_id"],
            "decision": "included",
            "reason": row["original_context"],
            "source": row["evidence_source"],
        }
        for _, row in included.iterrows()
    ]
    audit_rows.extend(
        [
            {
                "candidate": "20260907_lyc_focus_01",
                "decision": "excluded",
                "reason": "任务明确为课堂视频专注，不是游戏/王者",
                "source": "data/session_manifest.csv",
            },
            {
                "candidate": "20260907_lyc_unfocus_01",
                "decision": "excluded",
                "reason": "任务明确为课堂视频不专注，不是游戏/王者",
                "source": "data/session_manifest.csv",
            },
            {
                "candidate": "20260907_lyc_rest_01",
                "decision": "excluded",
                "reason": "静息态，不是游戏/王者",
                "source": "data/session_manifest.csv",
            },
            {
                "candidate": "legacy_lyc_daze_01|legacy_lyc_daze_02",
                "decision": "excluded",
                "reason": "legacy rest/daze，不是打游戏任务",
                "source": "data/legacy_manifest.csv",
            },
            {
                "candidate": "legacy_lyc_mixed_demo_00",
                "decision": "excluded",
                "reason": "2.5 秒 setup/demo，短于一个 4 秒窗口，且任务未知",
                "source": "data/legacy_manifest.csv",
            },
            {
                "candidate": "legacy_lyc_mixed_01|legacy_lyc_mixed_02|legacy_lyc_mixed_03",
                "decision": "excluded",
                "reason": "只能确认 focus/unfocus 分段顺序，无法从可靠 metadata/notes 确认是打游戏",
                "source": "data/legacy_manifest.csv; legacy notebooks",
            },
            {
                "candidate": "2026-09-14 non-lyc sessions",
                "decision": "excluded",
                "reason": "subject_id 不是 lyc",
                "source": "data/exploratory/lab_feedback/2026-09-14/metadata.csv",
            },
            {
                "candidate": "zyf/zqd/author/common6 and other non-lyc data",
                "decision": "excluded",
                "reason": "超出只测 lyc 本人录制数据的范围",
                "source": "repository manifests",
            },
            {
                "candidate": "2026-09-16 current New Paradigm v1 sessions",
                "decision": "excluded",
                "reason": "属于冻结模型训练日数据，不是 historical replay 输入",
                "source": "data/current/new_paradigm_v1/session_manifest.csv",
            },
        ]
    )
    return pd.DataFrame(audit_rows)


def focus_probability(pipeline: Any, features: np.ndarray) -> np.ndarray:
    classes = list(map(str, pipeline.named_steps["svc"].classes_))
    return pipeline.predict_proba(features)[:, classes.index("focus")]


def majority_vote(predictions: np.ndarray, probabilities: np.ndarray) -> tuple[str, str]:
    focus_count = int(np.sum(predictions == "focus"))
    unfocus_count = int(np.sum(predictions == "unfocus"))
    if focus_count != unfocus_count:
        return ("focus" if focus_count > unfocus_count else "unfocus"), "majority_vote"
    label = "focus" if float(np.mean(probabilities)) >= 0.5 else "unfocus"
    return label, "tie_broken_by_mean_focus_probability"


def probability_summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean_focus_probability": float(np.mean(values)),
        "median_focus_probability": float(np.median(values)),
        "q25_focus_probability": float(np.quantile(values, 0.25)),
        "q75_focus_probability": float(np.quantile(values, 0.75)),
        "min_focus_probability": float(np.min(values)),
        "max_focus_probability": float(np.max(values)),
    }


def predict_sessions(
    pipeline: Any,
    config: dict[str, Any],
    sessions: pd.DataFrame,
    output_dir: Path,
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    channel_order = tuple(config["preprocessing_and_features"]["channel_order"])
    summary_rows: list[dict[str, Any]] = []
    window_dir = output_dir / "windows"
    window_dir.mkdir(parents=True, exist_ok=True)

    for _, row in sessions.iterrows():
        path = repo_path(str(row["edf_path"]))
        if not path.is_file():
            raise FileNotFoundError(path)
        actual_hash = sha256_file(path)
        if actual_hash != str(row["expected_edf_sha256"]).lower():
            raise AssertionError(f"EDF SHA256 mismatch: {row['session_id']}")

        data, sfreq, channels = load_eeg_recording(
            path,
            target_fs=128.0,
            allow_locked=True,
            channel_names=channel_order,
        )
        if tuple(channels) != channel_order:
            raise AssertionError(f"Channel order mismatch: {row['session_id']}")
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
        if features.ndim != 2 or features.shape[1] != 240 or not np.isfinite(features).all():
            raise AssertionError(f"Invalid feature matrix for {row['session_id']}: {features.shape}")
        predictions = pipeline.predict(features).astype(str)
        probabilities = focus_probability(pipeline, features)
        majority, vote_method = majority_vote(predictions, probabilities)
        focus_count = int(np.sum(predictions == "focus"))
        unfocus_count = int(np.sum(predictions == "unfocus"))
        n_windows = int(len(predictions))

        window_frame = pd.DataFrame(
            {
                "window_index": np.arange(n_windows, dtype=int),
                "start_s": starts,
                "end_s": starts + baseline.WINDOW_SEC,
                "predicted_label": predictions,
                "focus_probability": probabilities,
            }
        )
        save_dataframe(window_dir / f"{row['session_id']}.csv", window_frame)

        summary_rows.append(
            {
                **row.to_dict(),
                "edf_sha256": actual_hash,
                "model_input_sfreq_hz": sfreq,
                "n_effective_windows": n_windows,
                "focus_windows": focus_count,
                "focus_proportion": focus_count / n_windows,
                "unfocus_windows": unfocus_count,
                "unfocus_proportion": unfocus_count / n_windows,
                "majority_prediction": majority,
                "vote_method": vote_method,
                "historical_label_to_prediction": f"{row['historical_label']} → {majority}",
                "semantic_warning": SEMANTIC_WARNING,
                **probability_summary(probabilities),
                "window_predictions_path": (
                    Path("windows") / f"{row['session_id']}.csv"
                ).as_posix(),
            }
        )
        print(
            f"{row['session_id']}: windows={n_windows}, focus={focus_count / n_windows:.2%}, "
            f"mean_p={float(np.mean(probabilities)):.4f}, majority={majority}"
        )
    return pd.DataFrame(summary_rows), channel_order


def build_report(summary: pd.DataFrame, audit: pd.DataFrame, model_hash: str) -> str:
    strict = summary.loc[summary["serious_honor_of_kings"].astype(bool)].copy()
    explicit_hok = summary.loc[summary["evidence_tier"].eq("confirmed_honor_of_kings")].copy()
    legacy_gaming = summary.loc[summary["evidence_tier"].eq("confirmed_gaming_title_unspecified")].copy()
    strict_focus_weighted = float(strict["focus_windows"].sum() / strict["n_effective_windows"].sum())
    strict_majorities = strict["majority_prediction"].value_counts().to_dict()
    session_range = (float(summary["focus_proportion"].min()), float(summary["focus_proportion"].max()))

    lines = [
        "# Frozen 2026-09-16 model — historical lyc gaming replay",
        "",
        "## Boundary",
        "",
        "This is a prediction-only replay. The frozen 2026-09-16 lyc New Paradigm v1 first-pass scaler, PCA, and SVC were loaded directly. Historical data were used only for the unchanged preprocessing/feature transform and prediction path. `fit_calls=0`; there was no calibration, parameter search, threshold adjustment, relabeling, or model update.",
        "",
        f"Frozen model SHA256: `{model_hash}`.",
        "",
        f"**{SEMANTIC_WARNING}.** No strict cross-day generalization accuracy is reported.",
        "",
        "## Included scope",
        "",
        f"Reliable historical sessions: **{len(summary)}**. Of these, {len(explicit_hok)} explicitly document 王者荣耀/玩王者; {len(legacy_gaming)} older self-recordings explicitly document gaming but do not identify the game title.",
        "",
        "## Historical metadata retained for comparison",
        "",
        "| date | session / EDF | historical label | task | recording duration | analyzed interval | notes/context |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['historical_date']} | `{row['session_id']}` / `{row['filename']}` | "
            f"{row['historical_label']} | {row['task']} | {float(row['recording_duration_s']):.1f} s | "
            f"{float(row['activity_start_s']):.1f}–{float(row['activity_end_s']):.1f} s | "
            f"{row['notes']} |"
        )
    lines.extend(
        [
        "",
        "## Session predictions",
        "",
        "| date | historical session | historical label → prediction | valid windows | focus windows | unfocus windows | mean focus prob | median | Q25–Q75 | min–max |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['historical_date']} | `{row['session_id']}` / `{row['filename']}` | "
            f"{row['historical_label_to_prediction']} | {int(row['n_effective_windows'])} | "
            f"{int(row['focus_windows'])} ({float(row['focus_proportion']):.2%}) | "
            f"{int(row['unfocus_windows'])} ({float(row['unfocus_proportion']):.2%}) | "
            f"{float(row['mean_focus_probability']):.4f} | {float(row['median_focus_probability']):.4f} | "
            f"{float(row['q25_focus_probability']):.4f}–{float(row['q75_focus_probability']):.4f} | "
            f"{float(row['min_focus_probability']):.4f}–{float(row['max_focus_probability']):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Strict ‘认真打王者’ subset",
            "",
            "This strict subset contains only sessions explicitly documented as 王者荣耀/玩王者 and historically described as focus/认真/高度集中. Original labels remain post-hoc context only.",
            "",
            "| historical session | original context | focus % | mean focus prob | majority |",
            "|---|---|---:|---:|---|",
        ]
    )
    for _, row in strict.iterrows():
        lines.append(
            f"| `{row['session_id']}` | {row['original_context']} | "
            f"{float(row['focus_proportion']):.2%} | {float(row['mean_focus_probability']):.4f} | "
            f"{row['majority_prediction']} |"
        )
    dominant = "focus" if strict_focus_weighted >= 0.5 else "unfocus"
    lines.extend(
        [
            "",
            f"Across these {len(strict)} sessions, the window-weighted focus proportion is {strict_focus_weighted:.2%}; session majorities are focus={strict_majorities.get('focus', 0)}, unfocus={strict_majorities.get('unfocus', 0)}. By this descriptive replay, they lean **{dominant}**.",
            "",
            "## Session-to-session variation",
            "",
            f"Across all included sessions, focus-window proportions range from {session_range[0]:.2%} to {session_range[1]:.2%}. This spread is reported descriptively and is not used to alter the model or labels.",
            "",
            "## Exclusions",
            "",
            "| candidate/group | reason |",
            "|---|---|",
        ]
    )
    for _, row in audit.loc[audit["decision"].eq("excluded")].iterrows():
        lines.append(f"| `{row['candidate']}` | {row['reason']} |")
    lines.extend(
        [
            "",
            "## Required interpretation statement",
            "",
            "**本分析是 frozen 2026-09-16 model 对 historical lyc gaming sessions 的 prediction-only replay，未参与任何 fit，不属于独立 final test。**",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise RuntimeError(f"Refusing to overwrite existing replay artifacts: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pipeline, config, frozen_hashes_before = verify_frozen_baseline()
    sessions = build_included_sessions()
    audit = build_candidate_audit(sessions)
    summary, channel_order = predict_sessions(pipeline, config, sessions, OUTPUT_DIR)
    save_dataframe(OUTPUT_DIR / "session_predictions.csv", summary)
    save_dataframe(OUTPUT_DIR / "candidate_audit.csv", audit)

    report_path = OUTPUT_DIR / "REPORT.md"
    report_path.write_text(
        build_report(summary, audit, frozen_hashes_before["binary_model.joblib"]),
        encoding="utf-8",
    )

    frozen_hashes_after = {
        "binary_model.joblib": sha256_file(MODEL_PATH),
        "config.json": sha256_file(CONFIG_PATH),
        "baseline_freeze_manifest.json": sha256_file(FREEZE_MANIFEST_PATH),
        "run_manifest.json": sha256_file(FIRST_PASS_RUN_MANIFEST_PATH),
    }
    if frozen_hashes_after != frozen_hashes_before:
        raise AssertionError("Frozen first-pass artifacts changed during prediction-only replay")

    input_hashes = {
        row["edf_path"]: row["edf_sha256"]
        for _, row in summary.sort_values("edf_path").iterrows()
    }
    output_files = [
        OUTPUT_DIR / "REPORT.md",
        OUTPUT_DIR / "session_predictions.csv",
        OUTPUT_DIR / "candidate_audit.csv",
        *(OUTPUT_DIR / "windows").glob("*.csv"),
    ]
    run_manifest = {
        "run_id": RUN_ID,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "prediction-only",
        "prediction_only": True,
        "fit_calls": 0,
        "calibration_calls": 0,
        "parameter_search_calls": 0,
        "threshold_tuning_calls": 0,
        "historical_data_used_for_fit": False,
        "historical_labels_used_for_prediction": False,
        "strict_accuracy_calculated": False,
        "semantic_warning": SEMANTIC_WARNING,
        "frozen_baseline": {
            "directory": FROZEN_DIR.relative_to(ROOT).as_posix(),
            "model_path": MODEL_PATH.relative_to(ROOT).as_posix(),
            "model_sha256": frozen_hashes_before["binary_model.joblib"],
            "config_path": CONFIG_PATH.relative_to(ROOT).as_posix(),
            "config_sha256": frozen_hashes_before["config.json"],
            "baseline_freeze_manifest_path": FREEZE_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "baseline_freeze_manifest_sha256": frozen_hashes_before["baseline_freeze_manifest.json"],
            "first_pass_run_manifest_path": FIRST_PASS_RUN_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "first_pass_run_manifest_sha256": frozen_hashes_before["run_manifest.json"],
            "artifacts_unchanged_after_replay": True,
        },
        "preprocessing": {
            "implementation": "scripts/eeg_pipeline_utils.py",
            "feature_order_source": "scripts/legacy_baseline_v0.py:BANDS",
            "target_sampling_rate_hz": 128.0,
            "filter_hz": [baseline.FILTER_L_HZ, baseline.FILTER_H_HZ],
            "window_sec": baseline.WINDOW_SEC,
            "step_sec": baseline.STEP_SEC,
            "welch_nperseg_sec": baseline.WELCH_NPERSEG_SEC,
            "channel_order": list(channel_order),
            "n_features": 240,
        },
        "selection": {
            "subject_id": "lyc",
            "n_included_sessions": int(len(summary)),
            "n_explicit_honor_of_kings": int(summary["evidence_tier"].eq("confirmed_honor_of_kings").sum()),
            "n_gaming_title_unspecified": int(summary["evidence_tier"].eq("confirmed_gaming_title_unspecified").sum()),
            "candidate_audit_path": "candidate_audit.csv",
        },
        "input_edf_sha256": input_hashes,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "mne": mne.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
        "git": {
            "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        },
        "artifact_sha256": {
            path.relative_to(OUTPUT_DIR).as_posix(): sha256_file(path)
            for path in sorted(output_files)
        },
        "interpretation_boundary": "not an independent final test",
    }
    save_json(OUTPUT_DIR / "prediction_run_manifest.json", run_manifest)

    print(f"Replay complete: {OUTPUT_DIR}")
    print(f"sessions={len(summary)}; fit_calls=0; prediction_only=true")


if __name__ == "__main__":
    main()
