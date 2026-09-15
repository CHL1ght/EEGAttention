"""Read-only integrity checks for frozen models and the 2026-09-14 pilot."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = ROOT / "data/exploratory/lab_feedback/2026-09-14"
METADATA = PILOT_DIR / "metadata.csv"
EXPECTED_MODEL_HASHES = {
    "artifacts/author_models/author_common6/pipeline.joblib": "85987c2ec5cd13d72279696a166b4fc9da84460909264b1679b96f37799f5974",
    "artifacts/author_models/author_only/pipeline.joblib": "80f7cb46aa1cd98bf04f4e20f8b9f54199cd0c623b9ea7b82afa480590b9f244",
    "artifacts/legacy_baseline_v0/pipeline.joblib": "2c67ed005d3821f712771d3412bcad0a5b67a2638e89393d1d505460635488cc",
    "artifacts/mixed_models/our_author_mixed_common6/pipeline.joblib": "5f171c20e61b7ad827d08494f283fa6612d3eabbddb012b8389699a392881db8",
    "artifacts/our_common6_models/pooled_common6/pipeline.joblib": "bf8e20d43ab7927cdf28bba6501b835e212fcf37fb7e7c1bdbc5cb2dd761dbb6",
    "artifacts/subject_models/lyc/pipeline.joblib": "7270a2dbf0f04f490b48dc52db4eb694df698d2b1636234abd65534505a9c0fa",
    "artifacts/subject_models/zyf/pipeline.joblib": "5343939b19d0bfde7aa2ff8915c43bf8be8169d020b48932f586bcb93d690ff4",
}
EXPECTED_PILOT_SCRIPT_SNAPSHOT_HASH = "002a1dd0670804d14f5bdb252924afd6b5a4eaf42dd25734f4622188e5e79144"
REQUIRED_METADATA_FIELDS = {
    "session_id", "subject_id", "recorded_date", "recorded_time", "original_filename",
    "filename_label", "canonical_label", "label_source", "label_conflict",
    "label_conflict_note", "dataset_role", "experiment_version", "edf_path", "csv_path",
    "dsi_path", "md_note_path", "recording_duration_s", "sfreq_hz", "n_signals",
    "edf_sha256", "csv_sha256", "dsi_sha256", "task", "notes",
    "eligible_for_training", "eligible_for_validation", "eligible_for_final_test", "status",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_file(value: str, field: str, session_id: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(PILOT_DIR.resolve()):
        raise AssertionError(f"{session_id}: {field} leaves the pilot directory")
    if not path.is_file():
        raise AssertionError(f"{session_id}: missing {field}: {value}")
    return path


def validate_pilot() -> list[dict[str, str]]:
    with METADATA.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        missing = REQUIRED_METADATA_FIELDS - fields
        if missing:
            raise AssertionError(f"pilot metadata missing fields: {sorted(missing)}")
        rows = list(reader)

    if len(rows) != 11:
        raise AssertionError(f"pilot metadata must contain 11 EDF rows, found {len(rows)}")
    if len({row["session_id"] for row in rows}) != 11:
        raise AssertionError("pilot session_id values must be unique")

    metadata_edfs: set[str] = set()
    for row in rows:
        session_id = row["session_id"]
        if row["dataset_role"] != "historical_pilot":
            raise AssertionError(f"{session_id}: invalid dataset_role")
        if row["experiment_version"] != "pre_new_paradigm/lab_feedback_2026-09-14":
            raise AssertionError(f"{session_id}: invalid experiment_version")
        for field in ("eligible_for_training", "eligible_for_validation", "eligible_for_final_test"):
            if row[field] != "false":
                raise AssertionError(f"{session_id}: {field} must be false")
        if row["status"] != "archived_verified":
            raise AssertionError(f"{session_id}: status must be archived_verified")
        if row["model_prediction_used_for_label"] != "false":
            raise AssertionError(f"{session_id}: prediction cannot be a label source")
        if row["feedback_round"] != "unknown" or row["feedback_seen_before_recording"] != "unknown":
            raise AssertionError(f"{session_id}: feedback facts must remain unknown")
        if row["paired_files_complete"] != "true":
            raise AssertionError(f"{session_id}: paired files must be complete")

        metadata_edfs.add(row["original_filename"])
        for kind in ("edf", "csv", "dsi"):
            path = repo_file(row[f"{kind}_path"], f"{kind}_path", session_id)
            if sha256_file(path) != row[f"{kind}_sha256"].lower():
                raise AssertionError(f"{session_id}: {kind.upper()} SHA-256 mismatch")
            size_field = f"{kind}_size_bytes"
            if size_field in row and row[size_field] and path.stat().st_size != int(row[size_field]):
                raise AssertionError(f"{session_id}: {kind.upper()} size mismatch")
        repo_file(row["md_note_path"], "md_note_path", session_id)

    disk_edfs = {path.name for path in PILOT_DIR.glob("*.edf")}
    if metadata_edfs != disk_edfs:
        raise AssertionError("pilot EDF inventory and metadata rows differ")
    if len(list(PILOT_DIR.glob("*.csv"))) != 12:  # 11 sidecars plus metadata.csv
        raise AssertionError("pilot must contain 11 sidecar CSV files plus metadata.csv")
    if len(list(PILOT_DIR.glob("*.dsi"))) != 11:
        raise AssertionError("pilot must contain 11 DSI files")

    conflicts = {row["original_filename"]: row for row in rows if row["label_conflict"] == "true"}
    expected_conflicts = {
        "zyf_unfocus_202609141641.edf",
        "zyf_unfocus_202609141707.edf",
    }
    if set(conflicts) != expected_conflicts:
        raise AssertionError(f"unexpected pilot label conflicts: {sorted(conflicts)}")
    for filename, row in conflicts.items():
        if (row["filename_label"], row["canonical_label"], row["label_source"]) != ("unfocus", "focus", "md_note"):
            raise AssertionError(f"{filename}: conflict provenance is invalid")
        if not row["label_conflict_note"].strip() or row["label_conflict_note"] == "none":
            raise AssertionError(f"{filename}: conflict note is required")

    pilot_tokens = {row["session_id"] for row in rows} | metadata_edfs
    for manifest in (ROOT / "data/session_manifest.csv", ROOT / "data/legacy_manifest.csv"):
        text = manifest.read_text(encoding="utf-8-sig")
        if any(token in text for token in pilot_tokens):
            raise AssertionError(f"pilot data leaked into {manifest.relative_to(ROOT)}")
    with (ROOT / "data/current/new_paradigm_v1/session_manifest.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        if list(csv.DictReader(handle)):
            raise AssertionError("New Paradigm v1 manifest must remain schema-only in this transition")
    return rows


def validate_models() -> None:
    for relative, expected in EXPECTED_MODEL_HASHES.items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise AssertionError(f"frozen model hash mismatch: {relative}")


def validate_prediction_manifest() -> None:
    path = ROOT / "artifacts/lab_feedback/2026-09-14/run_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("prediction_only") is not True:
        raise AssertionError("pilot run_manifest prediction_only must be true")
    if payload.get("training_performed") is not False or payload.get("fit_calls") != 0:
        raise AssertionError("pilot run_manifest must record fit_calls=0 and no training")
    if payload.get("script_sha256") != EXPECTED_PILOT_SCRIPT_SNAPSHOT_HASH:
        raise AssertionError("pilot execution-time script snapshot hash changed")


def main() -> None:
    rows = validate_pilot()
    validate_models()
    validate_prediction_manifest()
    print(
        "Historical integrity OK: "
        f"{len(rows)} pilot EDF/CSV/DSI rows; {len(EXPECTED_MODEL_HASHES)} frozen model hashes; "
        "training/validation/final eligibility=false; fit_calls=0"
    )


if __name__ == "__main__":
    main()
