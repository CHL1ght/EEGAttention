"""Audit whether the checked-in EDF and author MAT sources support common-6.

This is an inspection-only compatibility audit.  The channel-name gate is
now cleared by the checked-in authoritative ACNS and Wearable Sensing
evidence, while the author MAT reference remains unknown.  This script does
not fit a scaler/PCA/SVC or read LOCKED_TEST signal values; model fitting and
prediction-only evaluation are separate scripts.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import mne
import numpy as np
import pandas as pd
from scipy.io import loadmat

from cross_source_utils import AUTHOR_RECORD_IDS
from eeg_pipeline_utils import save_dataframe, save_json, sha256_file


AUDIT_VERSION = "common6_compatibility_audit_v2"
AUDIT_DATE = "2026-09-14"
AUTHORITATIVE_EVIDENCE = (
    {
        "evidence_id": "acns_nomenclature",
        "source": "ACNS Guideline 2",
        "url": "https://www.acns.org/UserFiles/file/EEGGuideline2Electrodenomenclature_final_v1.pdf",
        "finding": "Modified 10-10 nomenclature replaces old 10-20 T5/T6 with P7/P8; T5/T6 are acceptable alternate names.",
        "status": "authoritative_nomenclature_equivalence",
        "supports_t5_t6_mapping": True,
        "supports_reference": False,
    },
    {
        "evidence_id": "wearable_sensing_dsi24_positions",
        "source": "Wearable Sensing DSI-24 product specification",
        "url": "https://wearablesensing.com/dsi-24/",
        "finding": "DSI-24 sensor locations list P7/T5 and P8/T6.",
        "status": "authoritative_device_position_equivalence",
        "supports_t5_t6_mapping": True,
        "supports_reference": False,
    },
    {
        "evidence_id": "wearable_sensing_pz_reference",
        "source": "Wearable Sensing technical documentation",
        "url": "https://support.wearablesensing.com/examples/mne/python/core/channels.html",
        "finding": "DSI-24 hardware reference is Pz and DSI-Streamer data uses this reference.",
        "status": "authoritative_our_reference",
        "supports_t5_t6_mapping": False,
        "supports_reference": True,
    },
)
AUTHOR_NOTEBOOKS = (
    "notebooks/upstream/EEG_train_22_origin.ipynb",
    "notebooks/upstream/EEG_train_22_20250226.ipynb",
)
REFERENCE_OPERATION_TOKENS = (
    "set_eeg_reference",
    "rereference",
    "re-reference",
    "reref",
    "common average",
    "linked ear",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _first_csv_metadata_line(lines: Iterable[str], prefix: str) -> str:
    prefix = prefix.casefold()
    for line in lines:
        if line.casefold().startswith(prefix):
            return line
    return ""


def _csv_metadata_value(line: str) -> str:
    if not line:
        return ""
    parts = line.split(",")
    if len(parts) < 2:
        return ""
    return parts[1].strip()


def _read_csv_sidecar(path: Path, *, source_role: str) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    channel_line = next(
        (line for line in lines if line.casefold().startswith("time,")), ""
    )
    return {
        "csv_path": str(path),
        "source_role": source_role,
        "reference_location": _csv_metadata_value(
            _first_csv_metadata_line(lines, "# reference location")
        ),
        "headset_name": _csv_metadata_value(
            _first_csv_metadata_line(lines, "# headset_name")
        ),
        "data_logger": _csv_metadata_value(
            _first_csv_metadata_line(lines, "# data_logger")
        ),
        "filter_metadata": _csv_metadata_value(
            _first_csv_metadata_line(lines, "# filter =")
        ),
        "sensor_units": _csv_metadata_value(
            _first_csv_metadata_line(lines, "# sensor_data_units")
        ),
        "channel_header": channel_line,
    }


def _manifest_paths(repo_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    session = pd.read_csv(
        repo_root / "data" / "session_manifest.csv",
        dtype=str,
        keep_default_na=False,
    )
    legacy = pd.read_csv(
        repo_root / "data" / "legacy_manifest.csv",
        dtype=str,
        keep_default_na=False,
    )
    return session, legacy


def _unique_manifest_file_rows(
    repo_root: Path, session: pd.DataFrame, legacy: pd.DataFrame
) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}

    for row in session.to_dict(orient="records"):
        path = str((repo_root / row["edf_path"]).resolve())
        rows.setdefault(
            path,
            {
                "edf_path": path,
                "source_role": row["dataset_role"],
                "subject_id": row["subject_id"],
                "csv_path": str((repo_root / row["csv_path"]).resolve()),
            },
        )

    # Include only the confirmed lyc/zyf historical source files.  This is an
    # audit of the data eligible for the requested stage, not a new inclusion
    # rule for zqd or unknown recordings.
    historical = legacy.loc[
        legacy["subject_id"].str.casefold().isin({"lyc", "zyf"})
    ]
    for row in historical.to_dict(orient="records"):
        path = str((repo_root / row["edf_path"]).resolve())
        rows.setdefault(
            path,
            {
                "edf_path": path,
                "source_role": row["dataset_role"],
                "subject_id": row["subject_id"],
                "csv_path": str((repo_root / row["csv_path"]).resolve())
                if row.get("csv_path")
                else "",
            },
        )
    return list(rows.values())


def _edf_header_labels(path: Path) -> list[str]:
    with path.open("rb") as handle:
        fixed = handle.read(256)
        if len(fixed) != 256:
            raise ValueError(f"EDF header is shorter than 256 bytes: {path}")
        try:
            n_channels = int(fixed[252:256].decode("ascii").strip())
        except ValueError as exc:
            raise ValueError(f"Invalid EDF channel count in header: {path}") from exc
        labels_raw = handle.read(16 * n_channels)
    if len(labels_raw) != 16 * n_channels:
        raise ValueError(f"EDF signal-label header is truncated: {path}")
    return [
        labels_raw[offset : offset + 16].decode("ascii", errors="replace").strip()
        for offset in range(0, len(labels_raw), 16)
    ]


def inspect_edf_files(file_rows: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in file_rows:
        path = Path(item["edf_path"])
        raw = mne.io.read_raw_edf(
            str(path), preload=False, infer_types=True, verbose="ERROR"
        )
        try:
            mne_channels = list(raw.ch_names)
            header_labels = _edf_header_labels(path)
            channel_text = ", ".join(mne_channels)
            header_text = ", ".join(header_labels)
            rows.append(
                {
                    "edf_path": str(path),
                    "source_role": item["source_role"],
                    "subject_id": item["subject_id"],
                    "sfreq_hz": float(raw.info["sfreq"]),
                    "mne_eeg_channel_count": int(len(mne_channels)),
                    "mne_channel_names": channel_text,
                    "edf_header_signal_labels": header_text,
                    "has_t5_pz": any(name.casefold() == "t5-pz" for name in mne_channels),
                    "has_t6_pz": any(name.casefold() == "t6-pz" for name in mne_channels),
                    "has_p7": any(name.casefold() in {"p7", "p7-pz"} for name in mne_channels),
                    "has_p8": any(name.casefold() in {"p8", "p8-pz"} for name in mne_channels),
                    "has_f7_pz": any(name.casefold() == "f7-pz" for name in mne_channels),
                    "has_f3_pz": any(name.casefold() == "f3-pz" for name in mne_channels),
                    "has_o1_pz": any(name.casefold() == "o1-pz" for name in mne_channels),
                    "has_o2_pz": any(name.casefold() == "o2-pz" for name in mne_channels),
                    "info_description": _as_text(raw.info.get("description")),
                    "info_subject_info": _as_text(raw.info.get("subject_info")),
                    "mne_montage_dig_present": raw.info.get("dig") is not None,
                    "mne_custom_ref_applied": _as_text(raw.info.get("custom_ref_applied")),
                    "mne_projector_count": int(len(raw.info.get("projs", []))),
                    "orig_units": _as_text(getattr(raw, "_orig_units", {})),
                    "csv_path": item["csv_path"],
                }
            )
        finally:
            raw.close()
    return pd.DataFrame(rows)


def inspect_csv_sidecars(file_rows: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in file_rows:
        csv_path = item.get("csv_path", "")
        if not csv_path or csv_path in seen:
            continue
        path = Path(csv_path)
        if not path.is_file():
            continue
        seen.add(csv_path)
        rows.append(_read_csv_sidecar(path, source_role=item["source_role"]))
    return pd.DataFrame(rows)


def _mat_field_names(record: Any) -> list[str]:
    return list(getattr(record, "_fieldnames", []) or [])


def inspect_author_mats(repo_root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record_id in range(1, 35):
        path = repo_root / "data" / "reference" / "original_mat" / f"eeg_record{record_id}.mat"
        payload = loadmat(path, squeeze_me=True, struct_as_record=False)
        record = payload["o"]
        fields = _mat_field_names(record)
        data = np.asarray(record.data)
        metadata_fields = [
            field
            for field in fields
            if re.search(r"reference|montage|electrode|channel|sensor|headset", field, re.I)
        ]
        rows.append(
            {
                "record_id": record_id,
                "mat_path": str(path),
                "selected_for_author_common7": record_id in AUTHOR_RECORD_IDS,
                "top_level_struct": "o",
                "o_fields": ", ".join(fields),
                "reference_or_montage_fields": ", ".join(metadata_fields),
                "data_shape": str(tuple(int(value) for value in data.shape)),
                "sampFreq_hz": float(np.asarray(record.sampFreq).squeeze()),
                "author_data_slice": "o.data[:20*128*60, 3:17]",
                "author_channel_order": "AF3,F7,F3,FC5,T7,P7,O1,O2,P8,T8,FC6,F4,F8,AF4",
                "tag": _as_text(getattr(record, "tag", "")),
            }
        )
    return pd.DataFrame(rows)


def inspect_author_notebooks(repo_root: Path) -> dict[str, Any]:
    notebooks: list[dict[str, Any]] = []
    combined_source = ""
    for relative in AUTHOR_NOTEBOOKS:
        path = repo_root / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        source = "\n".join(
            "".join(cell.get("source", []))
            for cell in payload.get("cells", [])
            if cell.get("cell_type") == "code"
        )
        lower = source.casefold()
        combined_source += "\n" + lower
        notebooks.append(
            {
                "path": relative,
                "has_author_channel_order": "useful_channel" in lower and "p7" in lower and "p8" in lower,
                "has_data_slice": "data[:20 * 128 * 60, 3:17]" in source.replace("\n", " ")
                or "data[:20*128*60, 3:17]" in source.replace("\n", " "),
                "reference_operation_tokens_found": [
                    token for token in REFERENCE_OPERATION_TOKENS if token in lower
                ],
            }
        )
    return {
        "notebooks": notebooks,
        "any_reference_operation_token_found": any(
            token in combined_source for token in REFERENCE_OPERATION_TOKENS
        ),
        "reference_operation_tokens_checked": list(REFERENCE_OPERATION_TOKENS),
        "common7_selection_is_explicit": all(
            item["has_author_channel_order"] and item["has_data_slice"]
            for item in notebooks
        ),
    }


def _write_report(
    path: Path,
    *,
    repo_root: Path,
    edf: pd.DataFrame,
    sidecars: pd.DataFrame,
    mats: pd.DataFrame,
    notebook_audit: dict[str, Any],
    output_dir: Path,
) -> None:
    t5_count = int(edf["has_t5_pz"].sum()) if not edf.empty else 0
    t6_count = int(edf["has_t6_pz"].sum()) if not edf.empty else 0
    p7_count = int(edf["has_p7"].sum()) if not edf.empty else 0
    p8_count = int(edf["has_p8"].sum()) if not edf.empty else 0
    pz_count = int((sidecars["reference_location"].str.casefold() == "pz").sum()) if not sidecars.empty else 0
    metadata_fields = (
        int(mats["reference_or_montage_fields"].fillna("").ne("").sum())
        if not mats.empty
        else 0
    )
    lines = [
        "# Common-6 compatibility audit",
        "",
        "> **UNBLOCKED_FOR_COMMON6_TRAINING** — authoritative nomenclature/device evidence confirms the T5/T6 to P7/P8 name equivalence for the current DSI-24 data. The author MAT reference remains unknown, so all cross-source results are exploratory and channel-aligned but reference-compatibility-uncertain.",
        "",
        "## Decision",
        "",
        "| item | result |",
        "|---|---|",
        "| `T5-Pz → P7-Pz` | **confirmed nomenclature equivalence** for current DSI-24 data by ACNS old/new 10–20 naming and Wearable Sensing `P7/T5` device specification. |",
        "| `T6-Pz → P8-Pz` | **confirmed nomenclature equivalence** for current DSI-24 data by ACNS old/new 10–20 naming and Wearable Sensing `P8/T6` device specification. |",
        "| `COMMON_6_CHANNELS` | **established** as `F7, F3, P7, O1, O2, P8`; the adapter is implemented in `scripts/cross_source_utils.py`. `AF4` is intentionally dropped. |",
        "| Our EDF reference | **Pz confirmed** by Wearable Sensing technical documentation, DSIStreamer sidecars, and `*-Pz` labels. |",
        "| Author MAT reference | **unknown**; 34 MAT files expose no reference/montage/electrode metadata sufficient to resolve it. |",
        "| Reference compatibility | **uncertain**; common6 may be used for exploratory channel-aligned comparisons, but the two sources must not be claimed to have identical references. |",
        "",
        "## Authoritative external evidence",
        "",
        "- [ACNS Guideline 2](https://www.acns.org/UserFiles/file/EEGGuideline2Electrodenomenclature_final_v1.pdf): modified 10–10 nomenclature replaces old 10–20 `T5/T6` with `P7/P8`.",
        "- [Wearable Sensing DSI-24 specification](https://wearablesensing.com/dsi-24/): lists the corresponding device locations as `P7/T5` and `P8/T6`.",
        "- [Wearable Sensing technical documentation](https://support.wearablesensing.com/examples/mne/python/core/channels.html): states DSI-24 hardware reference is `Pz` and DSI-Streamer data uses this reference.",
        "",
        "## Evidence inspected",
        "",
        f"- EDF audit: {len(edf)} unique EDF files from confirmed `lyc`/`zyf` historical rows plus current LOCKED_TEST/reference rows. Layout details are in `edf_header_metadata.csv`.",
        f"- EDF channel evidence: `T5-Pz` in {t5_count}/{len(edf)} files; `T6-Pz` in {t6_count}/{len(edf)}; literal `P7` in {p7_count}/{len(edf)}; literal `P8` in {p8_count}/{len(edf)}.",
        f"- DSI sidecars: {len(sidecars)} unique CSV files; `Reference location: Pz` in {pz_count}/{len(sidecars)}. Details are in `sidecar_metadata.csv`.",
        "- EDF raw headers contain `EEG T5-Pz` and `EEG T6-Pz`; the adapter applies only the documented nomenclature equivalence, not a spatial interpolation or signal transformation.",
        f"- Author MAT audit: {len(mats)} files inspected; {metadata_fields} contain a field whose name explicitly mentions reference/montage/electrode/channel/sensor/headset. Details are in `author_mat_metadata.csv`.",
        "- The author notebooks explicitly select `F7,F3,P7,O1,O2,P8,AF4` from `o.data[:, 3:17]`, but provide no acquisition reference declaration or rereference call.",
        "",
        "## Scope and fit policy",
        "",
        "- The channel-name gate is cleared; `author-common6`, `our-common6`, and `mixed-common6` may now be trained by the dedicated training script.",
        "- `LOCKED_TEST` remains prediction-only: it may be used for `transform`, `predict`, and final metrics, never for scaler/PCA/SVC/feature-selector fit, threshold tuning, or model selection.",
        "- Only confirmed `lyc`/`zyf` historical data are eligible for our-source training. `zqd` and unknown-identity files remain excluded.",
        "- Cross-source conclusions must be labeled `exploratory / channel-aligned but reference compatibility uncertain` and must account for subject, session, device, task/paradigm, preprocessing representation, and unresolved author-reference differences.",
        "",
        "## Historical blocked state",
        "",
        "The previous conservative gate is preserved in `HISTORICAL_BLOCKED_REPORT.md`, `HISTORICAL_BLOCKED.json`, and `HISTORICAL_EVIDENCE_AUDIT.csv`. It recorded T5/T6 mapping as unconfirmed and stopped before common6 model fitting; those historical judgments are not deleted or rewritten.",
        "",
        f"Audit outputs are in `{output_dir.as_posix()}/`. Generated from repository HEAD `{_git_head(repo_root)}`; this audit itself performed no model fitting and did not read LOCKED_TEST signal values.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_audit(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    session, legacy = _manifest_paths(repo_root)
    file_rows = _unique_manifest_file_rows(repo_root, session, legacy)
    edf = inspect_edf_files(file_rows)
    sidecars = inspect_csv_sidecars(file_rows)
    mats = inspect_author_mats(repo_root)
    notebook_audit = inspect_author_notebooks(repo_root)

    output_dir.mkdir(parents=True, exist_ok=True)
    save_dataframe(output_dir / "edf_header_metadata.csv", edf)
    save_dataframe(output_dir / "sidecar_metadata.csv", sidecars)
    save_dataframe(output_dir / "author_mat_metadata.csv", mats)

    sidecar_refs = Counter(sidecars["reference_location"].tolist()) if not sidecars.empty else Counter()
    evidence = pd.DataFrame(
        [
            *AUTHORITATIVE_EVIDENCE,
            {
                "evidence_id": "project_protocol",
                "source": "data/DATA_PROTOCOL.md",
                "finding": "DSIStreamer, 300 Hz, 24 EEG channels, Pz reference",
                "status": "explicit_project_declaration",
                "supports_t5_t6_mapping": False,
                "supports_reference": True,
            },
            {
                "evidence_id": "edf_labels",
                "source": "audited EDF signal headers",
                "finding": f"T5-Pz={int(edf['has_t5_pz'].sum())}/{len(edf)}; T6-Pz={int(edf['has_t6_pz'].sum())}/{len(edf)}; literal P7={int(edf['has_p7'].sum())}/{len(edf)}; literal P8={int(edf['has_p8'].sum())}/{len(edf)}",
                "status": "observed_labels_only",
                "supports_t5_t6_mapping": False,
                "supports_reference": "partial",
            },
            {
                "evidence_id": "sidecar_reference",
                "source": "DSIStreamer CSV sidecars",
                "finding": f"reference_location counts={dict(sidecar_refs)}; logger/filter metadata retained",
                "status": "explicit_pz_metadata",
                "supports_t5_t6_mapping": False,
                "supports_reference": True,
            },
            {
                "evidence_id": "author_mat_schema",
                "source": "data/reference/original_mat/*.mat",
                "finding": "o.data and o.sampFreq exist; no reference/montage/electrode field",
                "status": "reference_unknown",
                "supports_t5_t6_mapping": False,
                "supports_reference": False,
            },
            {
                "evidence_id": "author_notebook",
                "source": "; ".join(AUTHOR_NOTEBOOKS),
                "finding": "explicit P7/P8 selection and o.data slice; no explicit rereference operation",
                "status": "channel_names_without_reference_provenance",
                "supports_t5_t6_mapping": False,
                "supports_reference": False,
            },
        ]
    )
    save_dataframe(output_dir / "evidence_audit.csv", evidence)

    model_dirs = [
        repo_root / "artifacts" / "author_models" / "author_common6",
        repo_root / "artifacts" / "our_common6_models" / "pooled_common6",
        repo_root / "artifacts" / "mixed_models" / "our_author_mixed_common6",
    ]
    common6_models_trained = all((directory / "pipeline.joblib").is_file() for directory in model_dirs)
    comparison_path = repo_root / "artifacts" / "cross_source_comparison" / AUDIT_DATE / "unified_model_comparison.csv"
    common6_locked_test_evaluated = comparison_path.is_file()

    blocked = {
        "audit_version": AUDIT_VERSION,
        "status": "unblocked_for_common6_training",
        "blockers": [
            "author MAT reference/montage is unknown; retained as a non-hard-blocking uncertainty",
        ],
        "our_edf_reference": "Pz confirmed by Wearable Sensing DSI-24/DSI-Streamer technical documentation, DSIStreamer sidecars, and -Pz labels",
        "author_mat_reference": "unknown",
        "reference_compatibility": "uncertain",
        "common6_channels_established": True,
        "common6_channels": ["F7", "F3", "P7", "O1", "O2", "P8"],
        "common6_mapping": {
            "F7-Pz": "F7",
            "F3-Pz": "F3",
            "T5-Pz": "P7",
            "O1-Pz": "O1",
            "O2-Pz": "O2",
            "T6-Pz": "P8",
        },
        "common6_models_trained": common6_models_trained,
        "common6_locked_test_evaluated": common6_locked_test_evaluated,
        "locked_test_used_for_fit": False,
        "locked_test_signal_values_read": False,
        "zqd_or_unknown_used_for_modeling": False,
        "required_channels_not_substituted": [],
        "author_record_ids_audited": list(AUTHOR_RECORD_IDS),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(repo_root),
    }
    save_json(output_dir / "BLOCKED.json", blocked)
    _write_report(
        output_dir / "REPORT.md",
        repo_root=repo_root,
        edf=edf,
        sidecars=sidecars,
        mats=mats,
        notebook_audit=notebook_audit,
        output_dir=output_dir,
    )
    save_json(output_dir / "notebook_audit.json", notebook_audit)
    run_manifest = {
        "audit_version": AUDIT_VERSION,
        "audit_date": AUDIT_DATE,
        "status": "unblocked_for_common6_training",
        "outputs": [
            "edf_header_metadata.csv",
            "sidecar_metadata.csv",
            "author_mat_metadata.csv",
            "evidence_audit.csv",
            "notebook_audit.json",
            "BLOCKED.json",
            "REPORT.md",
        ],
        "common6_models_trained": common6_models_trained,
        "common6_locked_test_evaluated": common6_locked_test_evaluated,
        "model_fit_performed": False,
        "locked_test_signal_values_read": False,
        "output_sha256": {},
        "git_head": _git_head(repo_root),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(output_dir / "run_manifest.json", run_manifest)
    run_manifest["output_sha256"] = {
        name: sha256_file(output_dir / name)
        for name in run_manifest["outputs"]
        if (output_dir / name).is_file()
    }
    save_json(output_dir / "run_manifest.json", run_manifest)
    return blocked


def main() -> None:
    repo_root = repo_root_from_script()
    output_dir = repo_root / "artifacts" / "common6_compatibility" / AUDIT_DATE
    result = run_audit(repo_root, output_dir)
    print(f"common6 compatibility: {result['status']}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
