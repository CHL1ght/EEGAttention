"""Validate the New Paradigm v1 session manifest without fitting a model."""

from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/current/new_paradigm_v1/session_manifest.csv"
DATA_ROOT = (ROOT / "data/current/new_paradigm_v1").resolve()
REQUIRED_COLUMNS = (
    "session_id", "subject_id", "recorded_date", "recorded_time", "timezone", "day_id",
    "canonical_label", "task", "paradigm_version", "dataset_role", "split_role",
    "edf_path", "csv_path", "dsi_path", "note_path", "recording_duration_s",
    "activity_start_s", "activity_end_s", "window_sec", "step_sec", "sfreq_hz",
    "n_signals", "sha256", "csv_sha256", "dsi_sha256", "note_sha256", "status", "notes",
)
DATASET_ROLES = {"train_candidate", "validation_candidate", "final_holdout", "reference", "excluded"}
SPLIT_ROLES = {"pending", "train", "validation", "final_test", "excluded"}
STATUSES = {"recorded_unverified", "ready", "frozen_before_prediction", "excluded"}


@dataclass(frozen=True)
class EdfHeader:
    duration_s: float
    n_signals: int
    eeg_sample_rates_hz: frozenset[float]


def edf_number(raw: bytes, field: str, cast):
    value = raw.decode("latin-1").strip()
    try:
        return cast(value)
    except ValueError as exc:
        raise ValueError(f"EDF field {field} is invalid: {value!r}") from exc


def read_edf_header(path: Path) -> EdfHeader:
    with path.open("rb") as handle:
        fixed = handle.read(256)
        if len(fixed) != 256:
            raise ValueError("file is shorter than the 256-byte EDF fixed header")
        header_bytes = edf_number(fixed[184:192], "header_bytes", int)
        n_records = edf_number(fixed[236:244], "n_records", int)
        record_duration = edf_number(fixed[244:252], "record_duration", float)
        n_signals = edf_number(fixed[252:256], "n_signals", int)
        signal_header = handle.read(header_bytes - 256)

    if len(signal_header) != n_signals * 256:
        raise ValueError("EDF signal header length is invalid")
    if n_records < 0 or record_duration <= 0:
        raise ValueError("EDF record count or duration is invalid")
    labels = tuple(
        signal_header[index * 16 : (index + 1) * 16].decode("latin-1").strip()
        for index in range(n_signals)
    )
    sample_offset = n_signals * (16 + 80 + 8 + 8 + 8 + 8 + 8 + 80)
    samples = tuple(
        edf_number(
            signal_header[sample_offset + index * 8 : sample_offset + (index + 1) * 8],
            "samples_per_record",
            int,
        )
        for index in range(n_signals)
    )
    return EdfHeader(
        duration_s=n_records * record_duration,
        n_signals=n_signals,
        eeg_sample_rates_hz=frozenset(
            samples[index] / record_duration
            for index, label in enumerate(labels)
            if label.startswith("EEG ")
        ),
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_repo_path(value: str, field: str, session_id: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(DATA_ROOT):
        raise AssertionError(f"{session_id}: {field} must stay under data/current/new_paradigm_v1")
    return path


def main() -> None:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise AssertionError("New Paradigm v1 manifest header does not match DATA_PROTOCOL_V2")
        rows = list(reader)

    seen: dict[str, str] = {}
    for row in rows:
        session_id = row["session_id"].strip()
        if not session_id:
            raise AssertionError("session_id is required")
        if session_id in seen:
            raise AssertionError(f"duplicate session_id: {session_id}")
        seen[session_id] = row["split_role"]
        if row["canonical_label"] not in {"focus", "unfocus", "observe"}:
            raise AssertionError(f"{session_id}: invalid canonical_label")
        if row["paradigm_version"] != "new_paradigm_v1":
            raise AssertionError(f"{session_id}: invalid paradigm_version")
        if row["dataset_role"] not in DATASET_ROLES or row["split_role"] not in SPLIT_ROLES:
            raise AssertionError(f"{session_id}: invalid dataset/split role")
        if row["status"] not in STATUSES:
            raise AssertionError(f"{session_id}: invalid status")
        if row["dataset_role"] == "final_holdout":
            if row["split_role"] != "final_test" or row["status"] != "frozen_before_prediction":
                raise AssertionError(f"{session_id}: final_holdout must be frozen before prediction")
        if row["canonical_label"] == "observe":
            if row["dataset_role"] != "reference" or row["split_role"] != "excluded":
                raise AssertionError(f"{session_id}: observe must be reference/excluded")
        if row["split_role"] == "train":
            if row["dataset_role"] != "train_candidate":
                raise AssertionError(f"{session_id}: train split must be train_candidate")
            if row["canonical_label"] not in {"focus", "unfocus"} or row["status"] != "ready":
                raise AssertionError(f"{session_id}: train rows must be ready focus/unfocus sessions")

        required_paths = ("edf_path", "csv_path", "dsi_path", "note_path")
        resolved_paths: dict[str, Path] = {}
        for field in required_paths:
            path = resolve_repo_path(row[field], field, session_id)
            resolved_paths[field] = path
            if row["status"] in {"ready", "frozen_before_prediction"} and not path.is_file():
                raise AssertionError(f"{session_id}: missing {field}: {row[field]}")

        hash_fields = {
            "edf_path": "sha256",
            "csv_path": "csv_sha256",
            "dsi_path": "dsi_sha256",
            "note_path": "note_sha256",
        }
        for path_field, hash_field in hash_fields.items():
            expected_hash = row[hash_field].strip().lower()
            path = resolved_paths[path_field]
            if row["status"] in {"ready", "frozen_before_prediction"} and not expected_hash:
                raise AssertionError(f"{session_id}: missing {hash_field}")
            if expected_hash and path.is_file() and sha256_file(path) != expected_hash:
                raise AssertionError(f"{session_id}: {hash_field} mismatch")

        edf_path = resolved_paths["edf_path"]
        if edf_path.is_file():
            header = read_edf_header(edf_path)
            duration = float(row["recording_duration_s"])
            start = float(row["activity_start_s"])
            end = float(row["activity_end_s"])
            window = float(row["window_sec"])
            step = float(row["step_sec"])
            sfreq = float(row["sfreq_hz"])
            n_signals = int(row["n_signals"])
            if not math.isclose(header.duration_s, duration, abs_tol=1e-6):
                raise AssertionError(f"{session_id}: EDF duration mismatch")
            if header.n_signals != n_signals:
                raise AssertionError(f"{session_id}: EDF n_signals mismatch")
            if header.eeg_sample_rates_hz != {sfreq}:
                raise AssertionError(f"{session_id}: EDF EEG sampling rate mismatch")
            if not (0 <= start < end <= duration):
                raise AssertionError(f"{session_id}: invalid activity interval")
            if not math.isclose(window, 4.0) or not math.isclose(step, 2.0):
                raise AssertionError(f"{session_id}: window/step must be 4/2 seconds")

    print(f"New Paradigm v1 manifest OK: {len(rows)} sessions; fit_calls=0")


if __name__ == "__main__":
    main()
