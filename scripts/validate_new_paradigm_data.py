"""Validate the New Paradigm v1 session manifest without fitting a model."""

from __future__ import annotations

import csv
import hashlib
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
        if row["canonical_label"] not in {"focus", "unfocus"}:
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
        if row["split_role"] == "train" and row["dataset_role"] != "train_candidate":
            raise AssertionError(f"{session_id}: train split must be train_candidate")

        required_paths = ("edf_path", "csv_path", "dsi_path", "note_path")
        for field in required_paths:
            path = resolve_repo_path(row[field], field, session_id)
            if row["status"] in {"ready", "frozen_before_prediction"} and not path.is_file():
                raise AssertionError(f"{session_id}: missing {field}: {row[field]}")
        edf_path = resolve_repo_path(row["edf_path"], "edf_path", session_id)
        if row["sha256"] and edf_path.is_file() and sha256_file(edf_path) != row["sha256"].lower():
            raise AssertionError(f"{session_id}: EDF SHA-256 mismatch")
        if row["activity_start_s"] and row["activity_end_s"]:
            if float(row["activity_start_s"]) < 0 or float(row["activity_end_s"]) <= float(row["activity_start_s"]):
                raise AssertionError(f"{session_id}: invalid activity interval")

    print(f"New Paradigm v1 manifest OK: {len(rows)} sessions; fit_calls=0")


if __name__ == "__main__":
    main()
