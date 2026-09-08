"""Read-only validation for locked EEG sessions; requires only Python stdlib."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO / "data" / "session_manifest.csv"
ALLOWED_LABELS = {"focus", "unfocus", "rest"}
ALLOWED_ROLES = {"locked_test", "locked_reference"}
ALLOWED_STATUSES = {"ready", "excluded_short", "reference_rest"}


@dataclass(frozen=True)
class EdfHeader:
    duration_s: float
    n_signals: int
    sample_rates_hz: tuple[float, ...]
    labels: tuple[str, ...]


def number(raw: bytes, field: str, cast):
    value = raw.decode("latin-1").strip()
    try:
        return cast(value)
    except ValueError as exc:
        raise ValueError(f"EDF 字段 {field} 无法解析: {value!r}") from exc


def read_edf_header(path: Path) -> EdfHeader:
    with path.open("rb") as handle:
        fixed = handle.read(256)
        if len(fixed) != 256:
            raise ValueError("文件短于 EDF 固定头 256 字节")
        header_bytes = number(fixed[184:192], "header_bytes", int)
        n_records = number(fixed[236:244], "n_records", int)
        record_duration = number(fixed[244:252], "record_duration", float)
        n_signals = number(fixed[252:256], "n_signals", int)
        signal_header = handle.read(header_bytes - 256)

    if len(signal_header) != n_signals * 256:
        raise ValueError("EDF 信号头长度异常")
    if n_records < 0 or record_duration <= 0:
        raise ValueError("EDF 记录数或记录时长异常")

    labels = tuple(
        signal_header[i * 16 : (i + 1) * 16].decode("latin-1").strip()
        for i in range(n_signals)
    )
    offset = n_signals * (16 + 80 + 8 + 8 + 8 + 8 + 8 + 80)
    samples = tuple(
        number(signal_header[offset + i * 8 : offset + (i + 1) * 8], "samples", int)
        for i in range(n_signals)
    )
    return EdfHeader(
        duration_s=n_records * record_duration,
        n_signals=n_signals,
        sample_rates_hz=tuple(value / record_duration for value in samples),
        labels=labels,
    )


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_path(value: str) -> Path:
    path = (REPO / value).resolve()
    try:
        path.relative_to(REPO)
    except ValueError as exc:
        raise ValueError(f"路径越出仓库: {value}") from exc
    return path


def validate(row: dict[str, str]) -> tuple[list[str], int]:
    errors: list[str] = []
    session = row.get("session_id", "<missing>")
    label = row.get("canonical_label")
    role = row.get("dataset_role")
    status = row.get("status")
    if label not in ALLOWED_LABELS:
        errors.append("标签必须是 focus、unfocus 或 rest")
    if role not in ALLOWED_ROLES:
        errors.append("数据角色不合法")
    if status not in ALLOWED_STATUSES:
        errors.append("状态不合法")
    if label == "rest" and (role != "locked_reference" or status != "reference_rest"):
        errors.append("rest 必须是 locked_reference/reference_rest")
    if label in {"focus", "unfocus"} and role != "locked_test":
        errors.append("二分类数据必须是 locked_test")

    try:
        edf = repo_path(row["edf_path"])
    except (KeyError, ValueError) as exc:
        return [f"[{session}] {exc}"], 0
    if not edf.is_file():
        return [f"[{session}] EDF 不存在: {row.get('edf_path', '')}"], 0

    for field in ("csv_path", "dsi_path"):
        value = row.get(field, "").strip()
        if value and not repo_path(value).is_file():
            errors.append(f"配套文件不存在: {value}")

    try:
        header = read_edf_header(edf)
        expected_duration = float(row["recording_duration_s"])
        start = float(row["activity_start_s"])
        end = float(row["activity_end_s"])
        window = float(row["window_sec"])
        step = float(row["step_sec"])
        expected_rate = float(row["sfreq_hz"])
        expected_signals = int(row["n_signals"])
    except (KeyError, ValueError) as exc:
        return [f"[{session}] 数值或 EDF 头解析失败: {exc}"], 0

    if not math.isclose(header.duration_s, expected_duration, abs_tol=1e-6):
        errors.append(f"时长变化: 清单 {expected_duration}, EDF {header.duration_s}")
    if header.n_signals != expected_signals:
        errors.append(f"信号数变化: 清单 {expected_signals}, EDF {header.n_signals}")
    eeg_rates = {
        rate for rate, name in zip(header.sample_rates_hz, header.labels)
        if name.startswith("EEG ")
    }
    if eeg_rates != {expected_rate}:
        errors.append(f"EEG 采样率异常: {sorted(eeg_rates)}")
    if not (0 <= start < end <= header.duration_s):
        errors.append("活动起止时间超出录制范围")
    if window <= 0 or step <= 0:
        errors.append("窗口和步长必须大于 0")

    usable = max(0.0, end - start)
    windows = math.floor((usable - window) / step) + 1 if usable >= window else 0
    if status == "ready" and usable < 300:
        errors.append("ready 数据有效时长不足 300 秒")
    if file_hash(edf).lower() != row.get("sha256", "").lower():
        errors.append("SHA-256 不匹配，锁定 EDF 内容可能已改变")
    return [f"[{session}] {item}" for item in errors], windows


def main() -> int:
    parser = argparse.ArgumentParser(description="验收锁定 EEG 数据")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    with args.manifest.resolve().open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    listed: set[Path] = set()
    ready_sessions = 0
    ready_windows = 0
    for row in rows:
        row_errors, windows = validate(row)
        errors.extend(row_errors)
        listed.add(repo_path(row["edf_path"]))
        if row.get("status") == "ready":
            ready_sessions += 1
            ready_windows += windows
        outcome = "FAIL" if row_errors else "OK"
        print(f"{row['session_id']}: status={row['status']}, windows={windows}, validation={outcome}")

    found = {path.resolve() for path in (REPO / "data" / "locked").rglob("*.edf")}
    for path in sorted(found - listed):
        errors.append(f"未登记 EDF: {path.relative_to(REPO)}")
    for path in sorted(listed - found):
        errors.append(f"清单 EDF 不在 locked 目录: {path.relative_to(REPO)}")

    print(
        f"\n汇总: sessions={len(rows)}, ready_sessions={ready_sessions}, "
        f"ready_windows={ready_windows}, errors={len(errors)}"
    )
    if errors:
        print("验收失败:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("锁定数据验收通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

