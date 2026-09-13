"""
【教学注释版】

对应正式文件：
    scripts/legacy_baseline_v0.py

用途：
    帮助项目所有者沿着 Legacy baseline 的完整数据流学习代码。

重要：
    1. 本文件是教学副本，不是正式训练入口。
    2. 正式实验请运行 scripts/legacy_baseline_v0.py。
    3. 本文件不参与训练、冻结、LOCKED_TEST 或任何正式实验。
    4. 不要运行本文件，也不要让它生成或覆盖 artifacts。
    5. 正式源文件以后变化时，本副本可能需要人工同步。
"""

from __future__ import annotations

# argparse：把命令行参数变成 Python 对象。
# json / subprocess：读写配置以及查询 Git 版本。
# defaultdict：按 source_recording_id 收集多条 manifest segment。
import argparse
import json
import math
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# joblib 可以保存 sklearn Pipeline 对象及其 fit 后的内部状态。
# numpy / pandas 分别负责数值数组和表格型 manifest/metadata。
import joblib
import numpy as np
import pandas as pd

# 这三个 sklearn 组件组成当前冻结模型：
# 原始 feature vector → StandardScaler → PCA → SVC → focus/unfocus。
from sklearn.decomposition import PCA
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 教学副本使用“对应的教学工具模块”来展示调用关系。
# 正式脚本使用 scripts/eeg_pipeline_utils.py。
from eeg_pipeline_utils_annotated import (
    assert_not_locked,
    extract_segment_features,
    load_eeg_recording,
    print_metric,
    save_dataframe,
    save_json,
    sha256_file,
)


# =========================
# 1. 冻结配置
# =========================
# 这些常量不是“随手写的默认值”，而是本项目 baseline 的实验协议。
# 如果改变其中任意一项，就不再是同一个 frozen baseline。
BASELINE_VERSION = "legacy_baseline_v0"
DATASET_ROLE = "legacy_baseline_candidate"

# 标签顺序在很多地方都很重要：混淆矩阵的行/列也使用这个顺序。
LABELS = ("unfocus", "focus")
LABEL_MAPPING = {
    "focus": "focus",
    "iu": "unfocus",
    "ou": "unfocus",
}

WINDOW_SEC = 4.0
STEP_SEC = 2.0
FILTER_L_HZ = 0.5
FILTER_H_HZ = 43.0
BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 43.0),
}
WELCH_NPERSEG_SEC = 2.0

RANDOM_SEED = 42
VALIDATION_GROUP_FRACTION = 0.20
PCA_N_COMPONENTS = 0.95
SVC_PARAMS = {
    "kernel": "rbf",
    "C": 10.0,
    "gamma": "scale",
    "class_weight": "balanced",
    "probability": True,
    "random_state": RANDOM_SEED,
}


def repo_root_from_script() -> Path:
    """返回仓库根目录，而不是依赖用户当前在哪个目录运行命令。"""
    # __file__ 是当前脚本文件路径。
    # 正式文件位于 scripts/，所以正式文件的 parents[1] 是仓库根目录。
    # 教学副本多了一层 scripts/annotated，因此这里使用 parents[2]，让
    # 副本中的默认路径仍能指向同一个仓库；这只是文件位置带来的调整，
    # 不改变正式脚本的路径逻辑。
    return Path(__file__).resolve().parents[2]


def load_legacy_manifest(manifest_path: Path, repo_root: Path) -> pd.DataFrame:
    """
    读取 Legacy 唯一清单，并筛选允许进入二分类 baseline 的行。

    这里的 manifest 是“数据身份和标签的事实来源”。
    不能通过 focus1.edf、iu1.edf 这样的文件名重新猜标签。

    关键字段
    --------
    recording_id:
        一条逻辑记录的身份。单状态 EDF 通常一行对应一个 recording。
    source_recording_id:
        底层原始录音的身份。一个 mixed EDF 被切成 focus/unfocus 两行时，
        这两行会共享一个 source_recording_id。
    session_group_id:
        用于 train/validation 隔离的完整 session 组。多个 source recording
        可以属于同一个组，所以它的数量可能少于 source_recording_id。
    canonical_label:
        项目统一后的标签，本轮只接受 focus 和 unfocus。
    dataset_role:
        该行的研究角色；只有 legacy_baseline_candidate 进入训练/validation。
    split:
        清单原本应为 unassigned，由本脚本在完整 group 上生成 train/validation。
    """
    manifest_path = manifest_path.resolve()

    # baseline 是 Legacy-only 训练入口，路径保护防止它误读最终测试集。
    assert_not_locked(manifest_path, "manifest")
    expected = (repo_root / "data" / "legacy_manifest.csv").resolve()
    if manifest_path != expected:
        raise RuntimeError("This baseline accepts only data/legacy_manifest.csv")

    # dtype=str 保留 manifest 中的 ID 原样，避免 01 被当成数字 1。
    # keep_default_na=False 让空字符串保持为空，而不是自动变成 NaN。
    rows = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
    required = {
        "dataset_version",
        "recording_id",
        "source_recording_id",
        "session_group_id",
        "canonical_label",
        "dataset_role",
        "split",
        "edf_path",
        "activity_start_s",
        "activity_end_s",
        "sfreq_hz",
        "window_sec",
        "step_sec",
    }
    missing = sorted(required - set(rows.columns))
    if missing:
        raise AssertionError(f"Manifest missing required columns: {missing}")

    # 先按 dataset_role 筛选，再做任何特征工作。
    # 因此 rest/daze、demo 和其他角色不会意外混入二分类 baseline。
    rows = rows.loc[rows["dataset_role"] == DATASET_ROLE].copy()
    if rows.empty:
        raise AssertionError(f"Manifest has no {DATASET_ROLE!r} rows")
    if set(rows["canonical_label"]) - set(LABELS):
        raise AssertionError("Candidate rows contain labels outside focus/unfocus")
    if rows["split"].nunique() != 1 or rows["split"].iloc[0] != "unassigned":
        raise AssertionError("The input manifest must remain unassigned")
    if rows["dataset_version"].nunique() != 1:
        raise AssertionError("Candidate rows must have exactly one dataset_version")

    # 这是一个很重要的身份检查：
    # 同一 source recording 不能一半指向一个 group、另一半指向另一个 group。
    source_summary = rows.groupby("source_recording_id").agg(
        n_paths=("edf_path", "nunique"),
        n_groups=("session_group_id", "nunique"),
    )
    if (source_summary != 1).any().any():
        raise AssertionError("A source recording maps to multiple paths or groups")

    # 相对路径 data/legacy/... 变成绝对 Path，后续读取不再依赖 cwd。
    rows["edf_path_abs"] = rows["edf_path"].map(
        lambda value: (repo_root / value).resolve()
    )
    if rows["edf_path_abs"].map(lambda path: path.exists()).eq(False).any():
        missing_paths = rows.loc[
            ~rows["edf_path_abs"].map(lambda path: path.exists()),
            "edf_path",
        ].tolist()
        raise FileNotFoundError(f"Legacy EDF path(s) missing: {missing_paths}")
    if rows["edf_path_abs"].map(
        lambda path: not path.is_relative_to(repo_root)
    ).any():
        raise AssertionError("Manifest EDF path escaped the repository")
    if rows["edf_path_abs"].map(
        lambda path: not path.is_relative_to(repo_root / "data" / "legacy")
    ).any():
        raise AssertionError("Candidate EDF path is outside data/legacy")
    if rows["edf_path_abs"].map(
        lambda path: "/data/locked/" in path.as_posix().lower()
    ).any():
        raise AssertionError("Manifest candidate rows reference locked data")

    # 只有这几个时间/频率列需要变成数字，ID 和标签继续保持字符串。
    for column in (
        "activity_start_s",
        "activity_end_s",
        "sfreq_hz",
        "window_sec",
        "step_sec",
    ):
        rows[column] = pd.to_numeric(rows[column], errors="raise")
    if not np.isclose(rows["window_sec"], WINDOW_SEC).all() or not np.isclose(
        rows["step_sec"], STEP_SEC
    ).all():
        raise AssertionError("Manifest windows must be the frozen 4 s / 2 s rule")
    if (rows["activity_end_s"] <= rows["activity_start_s"]).any():
        raise AssertionError("Manifest activity intervals must be positive")
    return rows


def prepare_split(rows: pd.DataFrame) -> pd.DataFrame:
    """
    在完整 session_group_id 层面生成确定性 train/validation split。

    不能先切 window 再随机划分：4 秒窗口以 2 秒移动，邻近窗口高度
    重叠。如果同一录音的相邻窗口同时出现在 train 和 validation，模型
    看到的不是“新 session”，validation accuracy 会严重虚高。
    """
    # drop_duplicates 保留 manifest 中 group 的第一次出现顺序。
    group_ids = rows["session_group_id"].drop_duplicates().tolist()
    if len(group_ids) < 2:
        raise AssertionError("At least two session groups are required")

    # ceil(20% × 22)=5。这里的 20% 是 group 数，不是 window 数。
    n_validation = max(
        1,
        int(math.ceil(len(group_ids) * VALIDATION_GROUP_FRACTION)),
    )
    rng = np.random.RandomState(RANDOM_SEED)
    validation_groups = set(rng.permutation(group_ids)[:n_validation].tolist())

    rows = rows.copy()
    rows["split"] = np.where(
        rows["session_group_id"].isin(validation_groups),
        "validation",
        "train",
    )

    train_groups = set(rows.loc[rows["split"] == "train", "session_group_id"])
    val_groups = set(rows.loc[rows["split"] == "validation", "session_group_id"])
    train_sources = set(rows.loc[rows["split"] == "train", "source_recording_id"])
    val_sources = set(rows.loc[rows["split"] == "validation", "source_recording_id"])

    # 任意断言失败都应该让训练停止，而不是继续产生可疑 artifact。
    assert train_groups.isdisjoint(val_groups), "session_group_id leakage"
    assert train_sources.isdisjoint(val_sources), "source_recording_id leakage"
    assert set(rows.loc[rows["split"] == "validation", "canonical_label"]) == set(LABELS)
    assert set(rows.loc[rows["split"] == "train", "canonical_label"]) == set(LABELS)
    assert (rows["dataset_role"] == DATASET_ROLE).all()
    assert (~rows["edf_path_abs"].map(
        lambda path: "/data/locked/" in path.as_posix().lower()
    )).all()
    return rows


def build_feature_dataset(
    rows: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    读取 source EDF，并把 manifest segment 转成 X、y 和窗口元数据。

    输出
    ----
    X:
        shape=(总窗口数, 特征数)，例如 (299, 240) 这类二维矩阵。
        实际总数取决于传入的是 train、validation 还是全体 rows。
    y:
        shape=(总窗口数,)，每个元素是 focus 或 unfocus。
    metadata:
        每一行对应 X 的一个窗口，记录 session、group、时间和 split。
    """
    # 一个 mixed EDF 的两个逻辑 segment 共享 source_recording_id。
    # 先按 source 分组，可以让同一个物理 EDF 只读取一次。
    source_to_rows: dict[str, list[int]] = defaultdict(list)
    for index, row in rows.iterrows():
        source_to_rows[str(row["source_recording_id"])].append(index)

    feature_parts: list[np.ndarray] = []
    labels: list[str] = []
    metadata: list[dict[str, Any]] = []
    channel_signature: tuple[str, ...] | None = None

    for source_id, indices in source_to_rows.items():
        source_row = rows.loc[indices[0]]

        # load_eeg_recording 返回：
        # data.shape=(channels,time_samples)，例如 (24, 76800)；
        # sfreq=128；channels 是每行数据对应的通道名。
        data, sfreq, channels = load_eeg_recording(
            Path(source_row["edf_path_abs"])
        )
        current_signature = tuple(channels)
        if channel_signature is None:
            channel_signature = current_signature
        elif current_signature != channel_signature:
            raise AssertionError(
                "Legacy EDFs do not share one ordered EEG channel layout"
            )

        for index in indices:
            row = rows.loc[index]

            # 这里的 start/end 来自 manifest，而不是文件名或模型猜测。
            # 函数内部依次执行：segment → filter → windows → Welch features。
            features, window_starts = extract_segment_features(
                data,
                sfreq,
                float(row["activity_start_s"]),
                float(row["activity_end_s"]),
                BANDS,
                window_sec=WINDOW_SEC,
                step_sec=STEP_SEC,
                l_freq=FILTER_L_HZ,
                h_freq=FILTER_H_HZ,
            )
            # features.shape=(本 segment 的窗口数, 240)。
            feature_parts.append(features)
            labels.extend([str(row["canonical_label"])] * len(features))

            # metadata 是“每个 X 行的身份证”。
            # X[i]、y[i]、metadata.iloc[i] 必须描述同一个窗口。
            for window_start in window_starts:
                metadata.append(
                    {
                        "recording_id": str(row["recording_id"]),
                        "source_recording_id": source_id,
                        "session_group_id": str(row["session_group_id"]),
                        "subject_id": str(row["subject_id"]),
                        "canonical_label": str(row["canonical_label"]),
                        "split": str(row["split"]),
                        "window_start_sec": float(window_start),
                        "window_sec": WINDOW_SEC,
                        "step_sec": STEP_SEC,
                        "sfreq_hz": sfreq,
                    }
                )

    # concatenate(axis=0) 沿样本方向叠加不同 EDF/segment 的 feature 矩阵。
    # 最终 X 是一个二维矩阵；y 是一维标签数组。
    X = np.concatenate(feature_parts, axis=0)
    y = np.asarray(labels, dtype=object)
    metadata_df = pd.DataFrame(metadata)
    if len(X) != len(y) or len(X) != len(metadata_df):
        raise AssertionError("Feature, label, and metadata arrays are inconsistent")
    if not np.isfinite(X).all():
        raise AssertionError("Feature matrix contains non-finite values")
    return X, y, metadata_df


def build_baseline_pipeline() -> Pipeline:
    """
    建立冻结的 sklearn Pipeline，但此函数本身还没有训练模型。

    Pipeline 数据流：

    ```text
    一个 window 的 240 维 feature vector
          ↓
    StandardScaler：学习训练集均值/标准差并标准化
          ↓
    PCA(95%)：只保留训练集学习出的 95% 方差方向
          ↓
    RBF SVC：根据训练标签学习 focus/unfocus 决策边界
    ```

    StandardScaler 和 PCA 也会从数据中“学习”。因此它们和 SVC 一样，
    只能通过后面的唯一 pipeline.fit(X_train, y_train) 接收训练数据。
    """
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=PCA_N_COMPONENTS, random_state=RANDOM_SEED)),
            ("svc", SVC(**SVC_PARAMS)),
        ]
    )


def evaluate_predictions(
    pipeline: Pipeline,
    X_validation: np.ndarray,
    validation_metadata: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    只对 validation 做预测，并形成保存用的 metrics 字典。

    confusion matrix 的约定：
        行 = 真实标签，列 = 预测标签；顺序固定为 [unfocus, focus]。

    accuracy：所有预测正确的窗口 / 窗口总数。
    balanced accuracy：先分别计算两个类别的 recall，再取平均，
    避免某一类别样本较多时掩盖另一类别表现。
    precision：被预测成某类的窗口中，真正属于该类的比例。
    recall：真实属于某类的窗口中，被正确找回的比例。
    F1：precision 和 recall 的综合指标。
    """
    # validation 只能走 predict，不能对 validation 再 fit/refit。
    y_pred = pipeline.predict(X_validation)
    y_true = validation_metadata["canonical_label"]
    cm = confusion_matrix(y_true, y_pred, labels=list(LABELS))
    metrics = {
        "overall_accuracy": float(accuracy_score(y_true, y_pred)),
        "labels": list(LABELS),
        "confusion_matrix": cm.astype(int).tolist(),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=list(LABELS),
            target_names=list(LABELS),
            output_dict=True,
            zero_division=0,
        ),
        # 这些字段由 train_and_freeze 在知道 train_mask 后补齐。
        "n_train_windows": None,
        "n_validation_windows": int(len(y_true)),
        "n_features": int(X_validation.shape[1]),
        "pca_components_fitted": int(pipeline.named_steps["pca"].n_components_),
        "train_session_group_ids": [],
        "validation_session_group_ids": sorted(
            validation_metadata["session_group_id"].unique()
        ),
    }
    return y_pred, metrics


def summarize_by_session(
    predictions: pd.DataFrame,
) -> list[dict[str, Any]]:
    """按 validation session_group 汇总真值、预测比例和 accuracy。"""
    summaries: list[dict[str, Any]] = []
    for group_id, group in predictions.groupby(["session_group_id"], sort=True):
        # reindex 保证即使某个组没有预测出某类，输出仍有两个类别的键。
        true_counts = group["true"].value_counts().reindex(LABELS, fill_value=0)
        pred_counts = group["pred"].value_counts().reindex(LABELS, fill_value=0)
        summaries.append(
            {
                "session_group_id": group_id[0],
                "true_label_counts": {
                    label: int(true_counts[label]) for label in LABELS
                },
                "pred_label_counts": {
                    label: int(pred_counts[label]) for label in LABELS
                },
                "n_windows": int(len(group)),
                "group_accuracy": float(
                    accuracy_score(group["true"], group["pred"])
                ),
                "predicted_label_proportion": {
                    label: float(pred_counts[label] / len(group))
                    for label in LABELS
                },
            }
        )
    return summaries


def save_baseline_outputs(
    output_dir: Path,
    repo_root: Path,
    manifest_path: Path,
    split_rows: pd.DataFrame,
    pipeline: Pipeline,
    predictions: pd.DataFrame,
    group_summaries: list[dict[str, Any]],
    metrics: dict[str, Any],
    config: dict[str, Any],
) -> None:
    """
    保存机器可读的冻结证据。

    JSON 适合配置/指标，CSV 适合逐行表格结果，JOBLIB 保存 sklearn
    对象及其内部状态。它们共同组成“以后能复核的实验快照”。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    split_columns = [
        "dataset_version",
        "recording_id",
        "source_recording_id",
        "session_group_id",
        "subject_id",
        "canonical_label",
        "dataset_role",
        "split",
        "edf_path",
        "activity_start_s",
        "activity_end_s",
        "sfreq_hz",
        "window_sec",
        "step_sec",
    ]

    # split.csv 让读者可以审计每条 manifest 逻辑记录去哪一侧。
    save_dataframe(output_dir / "split.csv", split_rows[split_columns])
    # config.json 保存当时的采样、滤波、特征、PCA、SVC 和 split 协议。
    save_json(output_dir / "config.json", config)
    # pipeline.joblib 保存 fit 后的 scaler.mean_、PCA components_、SVC 状态等。
    joblib.dump(pipeline, output_dir / "pipeline.joblib")
    save_dataframe(output_dir / "validation_predictions.csv", predictions)
    save_dataframe(
        output_dir / "validation_group_metrics.csv",
        pd.DataFrame(group_summaries),
    )
    save_json(
        output_dir / "validation_metrics.json",
        {**metrics, "groups": group_summaries},
    )

    # freeze_manifest 是“这些文件当时是什么”的记录。
    # SHA-256 可视为文件内容的数字指纹：内容变化时通常会变化。
    artifact_paths = [
        output_dir / "pipeline.joblib",
        output_dir / "config.json",
        output_dir / "split.csv",
        output_dir / "validation_predictions.csv",
        output_dir / "validation_group_metrics.csv",
        output_dir / "validation_metrics.json",
    ]
    freeze_manifest = {
        "baseline_version": BASELINE_VERSION,
        "dataset_version": str(split_rows["dataset_version"].iloc[0]),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip(),
        "git_branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=repo_root, text=True
        ).strip(),
        "legacy_manifest": {
            "path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
            "sha256": sha256_file(manifest_path),
        },
        "artifact_sha256": {
            path.name: sha256_file(path) for path in artifact_paths
        },
        "train_session_group_count": int(
            split_rows.loc[
                split_rows["split"] == "train", "session_group_id"
            ].nunique()
        ),
        "validation_session_group_count": int(
            split_rows.loc[
                split_rows["split"] == "validation", "session_group_id"
            ].nunique()
        ),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "locked_test_read": False,
    }
    save_json(output_dir / "freeze_manifest.json", freeze_manifest)


def print_validation_summary(
    metrics: dict[str, Any],
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> None:
    """打印人类可读的验证摘要；详细结果仍保留在 JSON/CSV 中。"""
    balanced = balanced_accuracy_score(y_true, y_pred)
    print_metric("Accuracy", f"{metrics['overall_accuracy']:.2%}")
    print_metric("Balanced accuracy", f"{balanced:.2%}")

    # 行是真实标签，列是预测标签；顺序 [unfocus, focus]。
    print("\n  True \\ Pred       unfocus    focus")
    cm = np.asarray(metrics["confusion_matrix"])
    print(f"  unfocus          {cm[0, 0]:>8} {cm[0, 1]:>9}")
    print(f"  focus            {cm[1, 0]:>8} {cm[1, 1]:>9}")


def train_and_freeze(
    repo_root: Path,
    manifest_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """
    Legacy baseline 的主业务流程。

    注意：真正的模型逻辑不是“一个神秘的大函数”，而是下面这些
    明确阶段的串联：manifest → split → features → fit train → predict val
    → metrics → freeze artifacts。
    """
    print("\n" + "=" * 60)
    print(" EEGAttention — Legacy Baseline v0")
    print("=" * 60)

    print("\n[1/5] Loading Legacy dataset")
    rows = load_legacy_manifest(manifest_path, repo_root)
    split_rows = prepare_split(rows).sort_values(
        ["split", "session_group_id", "recording_id"]
    ).reset_index(drop=True)
    print_metric(
        "Train groups",
        int(
            split_rows.loc[
                split_rows["split"] == "train", "session_group_id"
            ].nunique()
        ),
    )
    print_metric(
        "Validation groups",
        int(
            split_rows.loc[
                split_rows["split"] == "validation", "session_group_id"
            ].nunique()
        ),
    )

    print("\n[2/5] Extracting EEG features")
    print_metric("Sampling rate", "128 Hz")
    print_metric("Filter", "0.5–43 Hz")
    print_metric("Window / step", "4 s / 2 s")
    X, y, metadata = build_feature_dataset(split_rows)
    train_mask = metadata["split"].eq("train").to_numpy()
    val_mask = metadata["split"].eq("validation").to_numpy()
    print_metric("Train windows", f"{int(train_mask.sum()):,}")
    print_metric("Val windows", f"{int(val_mask.sum()):,}")

    print("\n[3/5] Training model")
    print("  StandardScaler\n    → PCA (95%)\n    → RBF SVC (C=10, balanced)")
    pipeline = build_baseline_pipeline()

    # 这是正式 baseline 唯一的 fit 调用。
    # pipeline 会依次在 X_train 上 fit scaler、PCA 和 SVC。
    # X_val 完全没有进入 fit，因此 validation 不会泄漏到模型状态。
    pipeline.fit(X[train_mask], y[train_mask])

    print("\n[4/5] Validation")
    validation_metadata = metadata.loc[val_mask].reset_index(drop=True)
    y_pred, metrics = evaluate_predictions(
        pipeline,
        X[val_mask],
        validation_metadata,
    )
    metrics["n_train_windows"] = int(train_mask.sum())
    metrics["train_session_group_ids"] = sorted(
        split_rows.loc[
            split_rows["split"] == "train", "session_group_id"
        ].unique()
    )
    print_validation_summary(
        metrics,
        validation_metadata["canonical_label"],
        y_pred,
    )

    # 预测表的每一行对应 validation 的一个 window。
    predictions = validation_metadata[
        [
            "recording_id",
            "source_recording_id",
            "session_group_id",
            "subject_id",
            "window_start_sec",
            "window_sec",
            "step_sec",
            "sfreq_hz",
        ]
    ].copy()
    predictions.insert(
        0,
        "true",
        validation_metadata["canonical_label"].to_numpy(),
    )
    predictions.insert(1, "pred", y_pred)
    group_summaries = summarize_by_session(predictions)

    # config 是参数快照，不是临时变量的随意 dump。
    # 后续如果结果变化，可以检查这些实验条件是否真的一致。
    config = {
        "baseline_version": BASELINE_VERSION,
        "dataset_version": str(split_rows["dataset_version"].iloc[0]),
        "dataset_role": DATASET_ROLE,
        "label_mapping": LABEL_MAPPING,
        "labels": list(LABELS),
        "window_sec": WINDOW_SEC,
        "step_sec": STEP_SEC,
        "preprocessing": {
            "edf_reader": "mne.io.read_raw_edf(preload=True, infer_types=True)",
            "channel_policy": "all channels identified as EEG by MNE, ordered as in EDF",
            "target_sampling_rate_hz": 128.0,
            "resample": "MNE Raw.resample(target_fs, npad='auto') when source is not 128 Hz",
            "filter": {
                "method": "fir",
                "fir_design": "firwin",
                "l_freq_hz": FILTER_L_HZ,
                "h_freq_hz": FILTER_H_HZ,
                "applied": "per manifest segment before windowing",
            },
        },
        "feature_extraction": {
            "method": "Welch band power per channel",
            "welch_nperseg_sec": WELCH_NPERSEG_SEC,
            "total_power_range_hz": [1.0, 43.0],
            "bands_hz": {name: list(bounds) for name, bounds in BANDS.items()},
            "features_per_band": ["log_absolute_power", "relative_power"],
            "feature_order": "channel, band insertion order, absolute then relative",
        },
        "pca": {
            "n_components": PCA_N_COMPONENTS,
            "random_state": RANDOM_SEED,
        },
        "svc": SVC_PARAMS,
        "random_seed": RANDOM_SEED,
        "split": {
            "unit": "session_group_id",
            "validation_fraction": VALIDATION_GROUP_FRACTION,
            "n_validation_groups": int(
                split_rows.loc[
                    split_rows["split"] == "validation", "session_group_id"
                ].nunique()
            ),
            "algorithm": "numpy RandomState(seed).permutation(groups), first ceil(fraction*n) groups",
            "seed": RANDOM_SEED,
        },
        "fit_policy": "pipeline.fit(X_train, y_train) only; validation uses pipeline.predict(X_val)",
    }

    print("\n[5/5] Frozen artifacts")
    save_baseline_outputs(
        output_dir,
        repo_root,
        manifest_path,
        split_rows,
        pipeline,
        predictions,
        group_summaries,
        metrics,
        config,
    )
    for name in (
        "pipeline.joblib",
        "config.json",
        "split.csv",
        "validation_predictions.csv",
        "validation_metrics.json",
        "freeze_manifest.json",
    ):
        print(f"  ✓ {output_dir / name}")
    print("\nSTATUS: LEGACY_BASELINE_V0 FROZEN")
    return metrics


def check_existing_artifacts(output_dir: Path) -> None:
    """
    只读检查已有冻结结果，不训练、不读 EDF、不生成新 artifact。

    这是教学用的 regression check。它验证的是“已有证据没有被重构改写”，
    而不是重新执行训练流程。
    """
    metrics = json.loads(
        (output_dir / "validation_metrics.json").read_text(encoding="utf-8")
    )
    split = pd.read_csv(output_dir / "split.csv")
    predictions = pd.read_csv(output_dir / "validation_predictions.csv")

    assert len(predictions) == 3282
    assert abs(float(metrics["overall_accuracy"]) - 0.699878) < 1e-6
    assert metrics["confusion_matrix"] == [[1315, 475], [510, 982]]

    train_groups = split.loc[
        split["split"] == "train", "session_group_id"
    ].nunique()
    validation_groups = split.loc[
        split["split"] == "validation", "session_group_id"
    ].nunique()
    print("\n" + "=" * 60)
    print(" EEGAttention — Legacy Baseline v0 — regression check")
    print("=" * 60)
    print_metric("Train groups", train_groups)
    print_metric("Validation groups", validation_groups)
    print_metric("Validation windows", f"{len(predictions):,}")
    print_validation_summary(metrics, predictions["true"], predictions["pred"])
    print("\nSTATUS: LEGACY_BASELINE_V0 REGRESSION CHECK PASSED")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """
    解析命令行参数。

    `Iterable[str]` 表示 argv 是一个可以逐个遍历字符串的对象，
    例如 `['--check-existing']`。`argparse.Namespace` 是 argparse
    返回的属性对象，例如 args.output_dir。
    """
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "data" / "legacy_manifest.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "artifacts" / BASELINE_VERSION,
    )
    parser.add_argument(
        "--check-existing",
        action="store_true",
        help="Check saved results without training or reading EDFs.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    """
    程序入口。

    `argv: Iterable[str] | None = None` 展开理解：

    - `argv` 是函数参数，可以传入 `['--check-existing']`；
    - `Iterable[str]` 表示其中的元素是字符串，并且可以被遍历；
    - `| None` 表示也可以不传这个参数；
    - `= None` 表示不传时默认值是 None；
    - `-> None` 表示这个函数主要执行流程，不返回业务结果。

    下面这行使用 Python 条件表达式：

    ```python
    sys.argv[1:] if argv is None else argv
    ```

    它等价于：

    ```python
    if argv is None:
        actual_argv = sys.argv[1:]
    else:
        actual_argv = argv
    args = parse_args(actual_argv)
    ```
    """
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check_existing:
        check_existing_artifacts(args.output_dir)
        return
    train_and_freeze(repo_root_from_script(), args.manifest, args.output_dir)


# 当用户直接执行：
#
#     python scripts/legacy_baseline_v0.py
#
# Python 会把当前文件的 __name__ 设置为 "__main__"，所以这里调用 main()。
#
# 如果另一个 Python 文件只是：
#
#     import legacy_baseline_v0
#
# 那么 __name__ 会是模块名，而不是 "__main__"，main() 不会自动执行。
# 这让同一个文件既能提供可复用函数，又能作为命令行程序直接运行。
if __name__ == "__main__":
    main()
