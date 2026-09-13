"""LOCKED_TEST 评估器的中文教学副本（仅供阅读）。

正式脚本是 ``scripts/evaluate_locked_test.py``。本文件保留正式脚本的
函数名、参数、主要控制流和数据格式，但在关键位置补充了面向初学者的
中文解释。它不是新的正式入口，也不应该被运行来生成、覆盖或更新实验
产物。

这份代码回答的是一个非常具体的问题：已经冻结的 baseline pipeline 在
一组预先锁定、没有参与训练的数据上表现如何？完整的数据流可以写成：

    pipeline.joblib + LOCKED_TEST EDF
        -> 相同的预处理与特征提取
        -> pipeline.predict(X)（只推理，不 fit）
        -> 窗口级 -> session 级 -> subject 级 -> overall 汇总

    这里的 ``locked_test`` 是正式二分类指标的数据集角色；同日期的
    ``locked_reference``（rest）会单独保存预测结果，但不会混入 focus/unfocus
    的正式 accuracy、balanced accuracy 或 confusion matrix。

    训练阶段遵守 ``fit-only-train``；本文件遵守更严格的
    ``predict-only-locked-test``，也就是 frozen pipeline 只接受 predict，
    不会因为读取测试数据而重新学习 scaler、PCA 或 SVC 参数。
"""

from __future__ import annotations

# argparse：把命令行字符串解析为 args 对象；json：读写冻结配置和运行清单；
# subprocess：读取当前 Git HEAD，用来证明评估时使用的是哪个代码快照；
# sys：取得命令行参数；datetime/timezone：写入 UTC 运行时间。
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# joblib 用来加载已经训练好的 sklearn Pipeline；它不是在这里训练模型。
# numpy/pandas 分别处理数值数组和表格；sklearn.metrics 只负责计算指标。
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix

# 教学副本使用同目录下的教学版工具。正式评估器使用的是
# ``from eeg_pipeline_utils import ...``；切换导入名不改变算法，只让读者
# 在 annotated 目录里能够对应看到带注释的实现。
from eeg_pipeline_utils_annotated import (
    extract_segment_features,
    load_eeg_recording,
    print_banner,
    print_metric,
    save_dataframe,
    save_json,
    sha256_file,
)
import legacy_baseline_v0_annotated as baseline


# ``__file__`` 是当前 Python 文件路径；resolve() 得到绝对路径；parent 是
# scripts/annotated。因此本文件的 SCRIPT_DIR 与正式脚本的值不同，但下面
# 的 root 会通过 parent 回到仓库根目录。
SCRIPT_DIR = Path(__file__).resolve().parent

# 这些字符串会写进输出的 run_manifest.json，帮助以后判断结果由哪一版
# 评估器产生。LOCKED_DATE 是当前正式 locked 测试批次的日期，不是随意的
# 输出目录名。
EVALUATION_VERSION = "locked_test_evaluation_v0"
LOCKED_DATE = "2026-09-07"

# 标签顺序是协议的一部分。混淆矩阵的行、列都按 [unfocus, focus] 排列，
# 不能只看矩阵里的数字而忘记这个顺序。
FORMAL_LABELS = ("unfocus", "focus")


def git_head(repo_root: Path) -> str:
    """返回本次测试使用的 Git 提交哈希。"""
    # subprocess.check_output 执行只读的 git 命令并返回 stdout。
    # cwd=repo_root 表示命令在仓库根目录执行；text=True 让结果直接是 str，
    # strip() 去掉命令行输出末尾的换行。
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def load_and_validate_frozen_artifacts(
    baseline_dir: Path,
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    """加载冻结模型，并拒绝哈希、配置或 fitted 状态不一致的产物。

    返回值是 ``(pipeline, config, freeze_manifest)``：

    * ``pipeline`` 是 joblib 反序列化出的 sklearn Pipeline；
    * ``config`` 是训练时记录的超参数和特征配置；
    * ``freeze_manifest`` 保存冻结时的文件 SHA-256。

    ``tuple[Any, dict[str, Any], ...]`` 是 Python 类型注解：它描述返回值
    的形状，运行时不会自动完成检查。``dict[str, Any]`` 表示键是字符串，
    值可以是多种 JSON 类型。
    """
    # 一个冻结 baseline 目录至少需要这三个输入：模型、模型配置、冻结清单。
    # Path / 运算符用于拼接路径，比手写反斜杠更稳定。
    pipeline_path = baseline_dir / "pipeline.joblib"
    config_path = baseline_dir / "config.json"
    freeze_path = baseline_dir / "freeze_manifest.json"
    for path in (pipeline_path, config_path, freeze_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing frozen artifact: {path}")

    # read_text 读取 UTF-8 文本；json.loads 将 JSON 字符串转换成 Python
    # 字典/列表/数字。这里的配置是验证对象，不是重新选择参数。
    config = json.loads(config_path.read_text(encoding="utf-8"))
    freeze_manifest = json.loads(freeze_path.read_text(encoding="utf-8"))

    # 冻结时写入了 pipeline.joblib 和 config.json 的 SHA-256。当前文件只要
    # 有一个字节不同，哈希就会不同，于是评估停止，避免无意中评估错模型。
    for name, path in {"pipeline.joblib": pipeline_path, "config.json": config_path}.items():
        expected = freeze_manifest.get("artifact_sha256", {}).get(name)
        if not expected or sha256_file(path) != expected:
            raise AssertionError(f"Frozen artifact hash mismatch: {name}")

    # 下面是“配置锁”的一部分：验证的 pipeline 必须确实属于这个
    # baseline 版本、4 s/2 s 窗口和固定的标签顺序。
    if config.get("baseline_version") != baseline.BASELINE_VERSION:
        raise AssertionError("Frozen baseline version mismatch")
    if config.get("window_sec") != baseline.WINDOW_SEC or config.get("step_sec") != baseline.STEP_SEC:
        raise AssertionError("Frozen window configuration mismatch")
    if config.get("labels") != list(FORMAL_LABELS):
        raise AssertionError("Frozen label order is not [unfocus, focus]")

    # joblib.load 只加载已经存在的 Pipeline。Pipeline 的 named_steps 是按
    # 名字访问步骤的有序映射；这里要求 scaler -> pca -> svc，防止模型结构
    # 被悄悄替换。
    pipeline = joblib.load(pipeline_path)
    if list(pipeline.named_steps) != ["scaler", "pca", "svc"]:
        raise AssertionError("Unexpected frozen pipeline steps")
    scaler, pca, svc = (pipeline.named_steps[name] for name in ("scaler", "pca", "svc"))

    # sklearn 拟合后会产生 mean_、components_、support_ 等属性。检查这些
    # 属性等价于确认加载的对象已经 fitted；但本函数没有调用 fit。
    if not hasattr(scaler, "mean_") or not hasattr(pca, "components_") or not hasattr(svc, "support_"):
        raise AssertionError("Frozen pipeline is not fitted")
    if pca.n_components != config["pca"]["n_components"]:
        raise AssertionError("Frozen PCA configuration mismatch")
    for parameter, expected in config["svc"].items():
        if svc.get_params()[parameter] != expected:
            raise AssertionError(f"Frozen SVC configuration mismatch: {parameter}")

    # baseline 每个窗口应产生 240 维特征；scaler 记录了训练时看到的维度。
    # locked-test 的 X 必须与这个维度完全一致，不能靠广播或截断“凑”过去。
    if int(scaler.n_features_in_) != 240:
        raise AssertionError(f"Unexpected frozen feature dimension: {scaler.n_features_in_}")
    return pipeline, config, freeze_manifest


def load_locked_manifest(repo_root: Path, manifest_path: Path) -> pd.DataFrame:
    """只加载指定日期的 locked manifest，并验证角色、标签和路径。"""
    # manifest 是实验元数据表，不是从 EDF 内容猜出来的临时表。正式协议
    # 只接受仓库中的 data/session_manifest.csv，避免用户传入另一份清单。
    manifest_path = manifest_path.resolve()
    expected = (repo_root / "data" / "session_manifest.csv").resolve()
    if manifest_path != expected:
        raise RuntimeError("Locked evaluation accepts only data/session_manifest.csv")

    # dtype=str 保留 session_id、日期等标识文本；keep_default_na=False 避免
    # 空字符串被 pandas 自动改成 NaN。后面再对确实应该是数值的列显式转换。
    rows = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
    required = {
        "session_id", "subject_id", "recorded_date", "canonical_label", "dataset_role",
        "edf_path", "recording_duration_s", "activity_start_s", "activity_end_s",
        "window_sec", "step_sec", "sfreq_hz", "status",
    }
    missing = sorted(required - set(rows.columns))
    if missing:
        raise AssertionError(f"Locked manifest missing columns: {missing}")

    # loc[布尔条件].copy() 只保留 LOCKED_DATE 这一批次，并创建独立副本。
    # 本次批次期望 7 个 session，其中正式二分类 session 与 rest reference
    # 的角色由 dataset_role 区分。
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

    # 从字符串转成数值。errors="raise" 很重要：元数据写错时应立刻报错，
    # 不应把错误值默默改成 NaN 再继续算窗口。
    for column in ("recording_duration_s", "activity_start_s", "activity_end_s", "window_sec", "step_sec", "sfreq_hz"):
        rows[column] = pd.to_numeric(rows[column], errors="raise")
    if not np.isclose(rows["window_sec"], baseline.WINDOW_SEC).all() or not np.isclose(rows["step_sec"], baseline.STEP_SEC).all():
        raise AssertionError("Locked manifest window parameters differ from frozen 4 s / 2 s")

    # 额外限制 EDF 必须位于 data/locked/2026-09-07 下。resolve() 会展开
    # 相对路径和 ..；locked_root not in path.parents 可以防止路径越界。
    locked_root = (repo_root / "data" / "locked" / LOCKED_DATE).resolve()
    absolute_paths: list[Path] = []
    for value in rows["edf_path"]:
        path = (repo_root / value).resolve()
        if locked_root not in path.parents or path.suffix.lower() != ".edf":
            raise AssertionError(f"EDF is outside the expected locked directory: {path}")
        if not path.exists():
            raise FileNotFoundError(f"Locked EDF missing: {path}")
        absolute_paths.append(path)
    # 新列只保存解析后的绝对路径，原始 edf_path 仍保留，方便输出和审计。
    rows["edf_path_abs"] = absolute_paths
    return rows


def evaluate_one_session(pipeline: Any, row: pd.Series) -> tuple[pd.DataFrame, dict[str, Any]]:
    """为一个独立 locked session 提取冻结特征并执行预测。"""
    # row 是 manifest 的一行。load_eeg_recording 会读取 EDF 并返回
    # data.shape=(channels, time_samples)、采样率和通道名。
    # allow_locked=True 是明确的只读评估许可；它不是训练开关。
    data, sfreq, _channels = load_eeg_recording(Path(row["edf_path_abs"]), allow_locked=True)

    # 这里必须与 baseline 训练阶段使用同一套处理：相同 activity 区间、
    # 频带、4 s 窗口、2 s 步长和 0.5--43 Hz FIR。extract_segment_features
    # 的返回值 X 是 (窗口数, 240)，starts 是每个窗口的起点秒数。
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

    # 这是 locked evaluator 中最关键的一行：predict 读取已经 fitted 的
    # scaler/PCA/SVC 状态，只产生预测标签；这里没有 pipeline.fit(X, y)，
    # 也没有任何会学习参数的调用。正式运行清单会把 fit_calls 写成 0。
    predicted = pipeline.predict(X)

    # 逐窗口结果保存 true/predicted label 和时间边界。一个 session 由多个
    # 4 秒窗口组成，所以这里的 DataFrame 行数就是该 session 的窗口数。
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

    # session 级摘要把窗口级预测压成一行。value_counts() 统计每个预测类
    # 的窗口数；reindex 保证即使某类没有被预测，也仍有 focus/unfocus 两列。
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
    """按 subject 汇总正式 session 指标，但不改动窗口预测。"""
    summaries: list[dict[str, Any]] = []

    # groupby 把同一个 subject 的多行 session 放到一组。这里先累加窗口数
    # 和正确窗口数，再计算 subject_accuracy，因此是按窗口加权，而不是
    # 简单平均各 session 的 accuracy。
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
    """打印终端中使用的紧凑 locked-test 汇总。"""
    # 这些打印函数只显示结果，不写文件，也不参与模型计算。
    print_metric("Formal sessions", metrics["formal_session_count"])
    print_metric("Reference sessions", metrics["reference_session_count_excluded"])
    print_metric("Windows", f"{metrics['total_windows']:,}")
    print_metric("Accuracy", f"{metrics['accuracy']:.2%}")
    print_metric("Balanced accuracy", f"{metrics['balanced_accuracy']:.2%}")

    # confusion_matrix 是 2x2 numpy 数组；astype(int).tolist() 后才适合
    # 写入 JSON。这里显示的行是真实标签，列是预测标签。
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
    """执行一次 locked inference，并保存正式与 reference 输出。

    参数中的 ``str | None`` 是 union type annotation，表示参数可以是
    字符串，也可以是 None；它表达“可选的期望 commit”。本函数的顺序很
    有意：先验证冻结模型，再验证代码快照和 manifest，最后才读取 EDF。
    """
    # 注意：load_and_validate_frozen_artifacts 内部只 load，不 fit。
    pipeline, config, _freeze_manifest = load_and_validate_frozen_artifacts(baseline_dir)
    current_commit = git_head(repo_root)
    if expected_freeze_commit is not None and current_commit != expected_freeze_commit:
        raise AssertionError(f"Current HEAD {current_commit} is not the requested freeze commit")
    rows = load_locked_manifest(repo_root, manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print_banner(f"LOCKED_TEST {LOCKED_DATE}")
    print("\nBaseline")
    print_metric("Version", config["baseline_version"])
    # 这是一个可审计的事实：locked evaluator 没有训练步骤，因此 fit_calls=0。
    print_metric("Fit calls", 0)
    print("\nTest set")
    print_metric("Formal sessions", int((rows["dataset_role"] == "locked_test").sum()))
    print_metric("Reference", int((rows["dataset_role"] == "locked_reference").sum()))

    # 两类列表分别收集正式 locked_test 和 rest reference。二者都经过同一
    # predict 流程，但后面只把 formal 列表放入正式指标。
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

    # pd.concat 把多个 session 的 DataFrame 纵向拼起来。此时：
    #   locked_predictions：窗口级正式预测；
    #   session_metrics：每个正式 session 一行；
    #   subject_metrics：每个 subject 一行。
    locked_predictions = pd.concat(formal_predictions, ignore_index=True)
    session_metrics = pd.DataFrame(formal_summaries).sort_values("session_id")
    subject_metrics = summarize_by_subject(session_metrics)
    reference_predictions_df = pd.concat(reference_predictions, ignore_index=True)
    reference_session_metrics = pd.DataFrame(reference_summaries).sort_values("session_id")

    # sklearn 指标接收一维真实标签和预测标签。accuracy 是全部窗口中预测
    # 正确的比例；balanced accuracy 是各类别 recall 的平均，类别不平衡时更
    # 有参考价值；classification_report 还会给出 precision/recall/F1。
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
        # 这个字段明确记录：本次 locked test 没有训练行为。
        "training_performed": False,
    }

    print("\nOverall")
    print_locked_summary(metrics)

    # 输出文件各自承担不同角色：CSV 适合逐行检查和 pandas 分析，JSON 适合
    # 保存指标/配置/清单，joblib 是冻结模型文件，Markdown 报告由外层流程
    # 维护。此评估器只写 output_dir 下的运行结果。
    save_dataframe(output_dir / "locked_predictions.csv", locked_predictions)
    save_dataframe(output_dir / "locked_session_metrics.csv", session_metrics)
    save_dataframe(output_dir / "locked_subject_metrics.csv", subject_metrics)
    save_json(output_dir / "locked_metrics.json", metrics)
    save_dataframe(output_dir / "reference_predictions.csv", reference_predictions_df)
    save_dataframe(output_dir / "reference_session_metrics.csv", reference_session_metrics)

    # run_manifest 是可复核的运行账本：记录冻结模型、manifest、评估脚本和
    # 输出的 SHA-256，以及 fit/predict 次数。SHA-256 不是模型指标，而是文件
    # 完整性指纹；同一个文件改一个字节，指纹就会改变。
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

    # run_summary 是更便于人或后续脚本读取的总结果；to_dict(orient="records")
    # 把 DataFrame 转成“每行一个字典”的 JSON 友好结构。
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
    """不重新读取 locked EDF，只回归检查已经保存的结果。"""
    # 这个模式适合检查已有 artifact 是否仍与已知首次结果一致；它不会
    # 调用 evaluate_one_session，也不会触碰模型或 EDF。
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
    """解析显式的推理模式和“不写入新结果”的回归检查模式。

    ``Iterable[str]`` 表示参数可以是任意可迭代字符串序列，例如
    ``["--check-existing"]``。argparse 最终返回 Namespace，可用
    ``args.output_dir`` 这样的属性读取解析结果。
    """
    # annotated 副本放在 scripts/annotated，所以 parent 是 scripts，
    # parent.parent 才是仓库根目录；正式脚本中的 SCRIPT_DIR.parent 等价于
    # 它自己的 scripts 目录上一级。
    root = SCRIPT_DIR.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path, default=root / "artifacts" / "legacy_baseline_v0")
    parser.add_argument("--manifest", type=Path, default=root / "data" / "session_manifest.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "artifacts" / "locked_test" / LOCKED_DATE)
    parser.add_argument("--freeze-commit", default=None)
    parser.add_argument("--check-existing", action="store_true", help="Check saved results without reading EDFs.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    """把命令行参数选择连接到两个业务分支。

    ``argv`` 默认是 None，表示使用真实命令行；传入列表则便于教学或测试。
    下面的 conditional expression（条件表达式）：

        sys.argv[1:] if argv is None else argv

    等价于更展开的写法：

        if argv is None:
            selected_args = sys.argv[1:]
        else:
            selected_args = argv

    ``sys.argv[0]`` 是脚本名，所以真正的选项从 ``[1:]`` 开始。解析后，
    ``--check-existing`` 只检查已有文件；否则才进入一次 locked 推理。
    """
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check_existing:
        check_existing_results(args.output_dir)
        return
    run_locked_evaluation(
        SCRIPT_DIR.parent.parent,
        args.baseline_dir,
        args.manifest,
        args.output_dir,
        args.freeze_commit,
    )


# ``if __name__ == "__main__":`` 是 Python 常见的入口保护：
#
# * 直接执行 ``python evaluate_locked_test.py`` 时，Python 把当前模块名设为
#   ``"__main__"``，因此会调用 main()；
# * 如果别的模块 import 本文件，``__name__`` 会是模块名，不满足条件，
#   于是只定义函数，不会在导入时自动读取 EDF 或写 artifact。
#
# 本教学副本仍保留这个语法是为了讲解正式脚本的结构；按照本任务约定，
# 不应执行 annotated 文件。
if __name__ == "__main__":
    main()
