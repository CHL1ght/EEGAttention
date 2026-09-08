"""Validate legacy_dataset_v0 without modifying EEG data."""

from __future__ import annotations

import csv
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from validate_locked_data import REPO, file_hash, read_edf_header, repo_path


MANIFEST = REPO / "data" / "legacy_manifest.csv"
SINGLE_DIR = REPO / "data" / "legacy" / "multiclass_10min"
MIXED_DIR = REPO / "data" / "legacy" / "mixed_20min"
NAME_PATTERN = re.compile(r"(?:(zyf)_)?(daze|focus|iu|ou)(\d+)\.edf", re.IGNORECASE)
MIXED_NAME_PATTERN = re.compile(r"data_(?:(zqd|zyf)_)?(\d+)_raw\.edf", re.IGNORECASE)
LABEL_MAP = {"focus": "focus", "iu": "unfocus", "ou": "unfocus", "daze": "rest"}


def expected_single(filename: str) -> dict[str, str]:
    match = NAME_PATTERN.fullmatch(filename)
    if match is None:
        raise ValueError(f"无法解析 Legacy 文件名: {filename}")
    subject = (match.group(1) or "lyc").lower()
    source_label = match.group(2).lower()
    number = int(match.group(3))
    suffix = f"{number:02d}"
    return {
        "recording_id": f"legacy_{subject}_{source_label}_{suffix}",
        "source_recording_id": f"legacy_{subject}_{source_label}_{suffix}",
        "subject_id": subject,
        "session_number": str(number),
        "session_group_id": f"legacy_{subject}_run_{suffix}",
        "segment_order": "single_state_full_recording",
        "source_label": source_label,
        "canonical_label": LABEL_MAP[source_label],
    }


def expected_mixed(filename: str, canonical_label: str) -> dict[str, str]:
    match = MIXED_NAME_PATTERN.fullmatch(filename)
    if match is None:
        raise ValueError(f"无法解析混合 Legacy 文件名: {filename}")
    prefix = (match.group(1) or "").lower()
    number = int(match.group(2))
    is_demo = not prefix and number == 1
    subject = prefix or "lyc"
    session = 0 if is_demo else (number - 1 if not prefix else number)
    suffix = f"{session:02d}"
    source_id = "legacy_lyc_mixed_demo_00" if is_demo else f"legacy_{subject}_mixed_{suffix}"
    subject_evidence = "subject_confirmed_by_owner" if subject == "lyc" else "subject_from_filename"
    if is_demo:
        if canonical_label != "unknown":
            raise ValueError(f"{filename} 只能登记为 unknown demo")
        return {
            "recording_id": source_id,
            "source_recording_id": source_id,
            "subject_id": subject,
            "session_number": str(session),
            "session_group_id": source_id,
            "segment_order": "not_applicable_short_demo",
            "source_label": "unknown",
            "canonical_label": "unknown",
            "label_source": "none",
            "dataset_role": "legacy_demo_reference",
            "split": "excluded_too_short",
            "status": "excluded_too_short",
            "metadata_confidence": f"{subject_evidence};recorded_at_from_edf_header;label_unknown",
            "activity_start_s": "0",
        }
    if canonical_label not in {"focus", "unfocus"}:
        raise ValueError(f"{filename} 的混合片段标签无效: {canonical_label}")
    start, end = ("0", "600") if canonical_label == "unfocus" else ("600", "1200")
    return {
        "recording_id": f"{source_id}_{canonical_label}",
        "source_recording_id": source_id,
        "subject_id": subject,
        "session_number": str(session),
        "session_group_id": source_id,
        "segment_order": "unfocus_first_then_focus",
        "source_label": canonical_label,
        "canonical_label": canonical_label,
        "label_source": "later_executed_specific_legacy_notebook",
        "dataset_role": "legacy_baseline_candidate",
        "split": "unassigned",
        "status": "candidate_inferred_segment",
        "metadata_confidence": (
            f"{subject_evidence};recorded_at_from_edf_header;"
            "segment_order_supported_by_later_executed_specific_notebook"
        ),
        "activity_start_s": start,
        "activity_end_s": end,
    }


def recorded_times(edf: Path) -> tuple[str, str, float]:
    with edf.open("rb") as handle:
        handle.seek(168)
        date_text = handle.read(8).decode("ascii").strip()
        time_text = handle.read(8).decode("ascii").strip()
    day, month, short_year = (int(value) for value in date_text.split("."))
    hour, minute, second = (int(value) for value in time_text.split("."))
    modified = datetime.fromtimestamp(edf.stat().st_mtime)
    year = modified.year - modified.year % 100 + short_year
    if year - modified.year > 50:
        year -= 100
    elif modified.year - year > 50:
        year += 100
    recorded = datetime(year, month, day, hour, minute, second)
    return (
        recorded.strftime("%Y-%m-%d %H:%M:%S"),
        modified.strftime("%Y-%m-%d %H:%M:%S"),
        (modified - recorded).total_seconds(),
    )


def main() -> int:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    listed: set[Path] = set()
    ids: set[str] = set()
    counts: Counter[tuple[str, str]] = Counter()
    mixed_segments: dict[Path, set[str]] = {}

    for row in rows:
        name = Path(row.get("edf_path", "")).name
        prefix = row.get("recording_id", name)
        is_mixed = row.get("edf_path", "").startswith("data/legacy/mixed_20min/")
        try:
            values = expected_mixed(name, row.get("canonical_label", "")) if is_mixed else expected_single(name)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if row.get("dataset_version") != "legacy_dataset_v0":
            errors.append(f"[{prefix}] dataset_version 错误")
        for field, value in values.items():
            if row.get(field) != value:
                errors.append(f"[{prefix}] {field} 应为 {value!r}")
        expected_label_source = values.get("label_source", "filename_and_legacy_notebook")
        if row.get("label_source") != expected_label_source:
            errors.append(f"[{prefix}] label_source 应为 {expected_label_source}")
        expected_confidence = values.get("metadata_confidence") or (
            "subject_confirmed_by_owner;recorded_at_from_edf_header;session_inferred_from_filename"
            if values["subject_id"] == "lyc"
            else "subject_from_filename;recorded_at_from_edf_header;session_inferred_from_filename"
        )
        if row.get("metadata_confidence") != expected_confidence:
            errors.append(f"[{prefix}] metadata_confidence 错误")

        is_binary = values["canonical_label"] in {"focus", "unfocus"}
        role = values.get("dataset_role", "legacy_baseline_candidate" if is_binary else "legacy_reference")
        split = values.get("split", "unassigned" if is_binary else "excluded_binary")
        status = values.get("status", "candidate" if is_binary else "reference_rest")
        for field, value in {"dataset_role": role, "split": split, "status": status}.items():
            if row.get(field) != value:
                errors.append(f"[{prefix}] {field} 应为 {value}")

        try:
            edf = repo_path(row["edf_path"])
        except (KeyError, ValueError) as exc:
            errors.append(f"[{prefix}] EDF 路径错误: {exc}")
            continue
        listed.add(edf)
        if not edf.is_file():
            errors.append(f"[{prefix}] EDF 不存在")
            continue
        try:
            recorded_at, modified_at, save_delay_s = recorded_times(edf)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"[{prefix}] 采集时间解析失败: {exc}")
            continue
        if row.get("recorded_date") != recorded_at[:10]:
            errors.append(f"[{prefix}] recorded_date 与 EDF 文件头不一致")
        if row.get("recorded_at_local") != recorded_at:
            errors.append(f"[{prefix}] recorded_at_local 与 EDF 文件头不一致")
        if row.get("recorded_at_source") != "edf_header":
            errors.append(f"[{prefix}] recorded_at_source 应为 edf_header")
        if row.get("file_modified_at_local") != modified_at:
            errors.append(f"[{prefix}] file_modified_at_local 与文件系统不一致")
        if is_mixed:
            mixed_segments.setdefault(edf, set()).add(values["canonical_label"])
        for field in ("csv_path", "dsi_path"):
            value = row.get(field, "").strip()
            if value and not repo_path(value).is_file():
                errors.append(f"[{prefix}] {field} 文件不存在")
        if edf.with_suffix(".dsi").is_file() != bool(row.get("dsi_path", "").strip()):
            errors.append(f"[{prefix}] dsi_path 登记不一致")

        try:
            header = read_edf_header(edf)
            duration = float(row["recording_duration_s"])
            start = float(row["activity_start_s"])
            end = float(row["activity_end_s"])
            sfreq = float(row["sfreq_hz"])
            n_signals = int(row["n_signals"])
            window = float(row["window_sec"])
            step = float(row["step_sec"])
        except (KeyError, ValueError) as exc:
            errors.append(f"[{prefix}] 数值或 EDF 头解析失败: {exc}")
            continue

        if not math.isclose(duration, header.duration_s, abs_tol=1e-6):
            errors.append(f"[{prefix}] 时长与 EDF 不一致")
        # Windows 修改时间会受保存收尾、复制和整理影响，不能作为采集时间真值。
        # 它只应晚于 EDF 文件头记录的开始时间；真实采集时间仍以文件头为准。
        if save_delay_s < 0:
            errors.append(f"[{prefix}] 文件修改时间早于 EDF 文件头的采集开始时间")
        expected_start = float(values.get("activity_start_s", "0"))
        expected_end_text = values.get("activity_end_s", "full_duration")
        expected_end = header.duration_s if expected_end_text == "full_duration" else float(expected_end_text)
        if not (math.isclose(start, expected_start) and math.isclose(end, expected_end, abs_tol=1e-6)):
            errors.append(f"[{prefix}] 有效区间应为 {expected_start:g}-{expected_end:g} 秒")
        if end > header.duration_s:
            errors.append(f"[{prefix}] 有效区间超过 EDF 时长")
        eeg_rates = {rate for rate, label in zip(header.sample_rates_hz, header.labels) if label.startswith("EEG ")}
        if eeg_rates != {sfreq} or not math.isclose(sfreq, 300.0):
            errors.append(f"[{prefix}] EEG 采样率异常")
        if header.n_signals != n_signals or n_signals != 26:
            errors.append(f"[{prefix}] 信号数异常")
        if not (math.isclose(window, 4.0) and math.isclose(step, 2.0)):
            errors.append(f"[{prefix}] 窗口必须为 4 秒/2 秒")
        if file_hash(edf).lower() != row.get("sha256", "").lower():
            errors.append(f"[{prefix}] SHA-256 不匹配")
        if prefix in ids:
            errors.append(f"[{prefix}] recording_id 重复")
        ids.add(prefix)
        counts[(role, values["canonical_label"])] += 1

    found = {path.resolve() for directory in (SINGLE_DIR, MIXED_DIR) for path in directory.glob("*.edf")}
    for path in sorted(found - listed):
        errors.append(f"未登记 EDF: {path.relative_to(REPO)}")
    for path in sorted(listed - found):
        errors.append(f"非 Legacy 数据目录 EDF: {path.relative_to(REPO)}")

    for edf in sorted(MIXED_DIR.glob("*.edf")):
        labels = mixed_segments.get(edf.resolve(), set())
        expected_labels = {"unknown"} if edf.name == "data_0001_raw.edf" else {"focus", "unfocus"}
        if labels != expected_labels:
            errors.append(f"[{edf.name}] 片段登记应为 {sorted(expected_labels)}，实际为 {sorted(labels)}")

    expected_counts = {
        ("legacy_baseline_candidate", "focus"): 22,
        ("legacy_baseline_candidate", "unfocus"): 21,
        ("legacy_reference", "rest"): 4,
        ("legacy_demo_reference", "unknown"): 1,
    }
    if dict(counts) != expected_counts:
        errors.append(f"标签/角色数量异常: {dict(counts)}")

    candidates = counts[("legacy_baseline_candidate", "focus")] + counts[("legacy_baseline_candidate", "unfocus")]
    print(
        f"Legacy 清单: rows={len(rows)}, source_edf={len(listed)}, candidates={candidates}, "
        f"focus={counts[('legacy_baseline_candidate', 'focus')]}, "
        f"unfocus={counts[('legacy_baseline_candidate', 'unfocus')]}, "
        f"rest_reference={counts[('legacy_reference', 'rest')]}, errors={len(errors)}"
    )
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print("legacy_dataset_v0 清单验收通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
