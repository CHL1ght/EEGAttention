"""Thin MAT/EDF adapters around the shared EEG feature pipeline.

The author-data and common-7-channel experiments use the same window,
preprocessing, Welch feature, Scaler, PCA, and SVC implementation as the
existing Legacy baseline.  This module only supplies explicit input layouts
and recording/block metadata.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

import mne
import numpy as np
import pandas as pd
from scipy.io import loadmat

import legacy_baseline_v0 as baseline
from eeg_pipeline_utils import (
    load_eeg_recording,
    select_named_channels,
)


COMMON_7_CHANNELS = ("F7", "F3", "P7", "O1", "O2", "P8", "AF4")

# These are exact accepted spellings for the existing common-7 gate.  T5/T6
# are intentionally not silently treated as P7/P8 in this older experiment.
COMMON_7_EDF_ALIASES: dict[str, tuple[str, ...]] = {
    "F7": ("F7", "F7-Pz", "EEG F7", "EEG F7-Pz"),
    "F3": ("F3", "F3-Pz", "EEG F3", "EEG F3-Pz"),
    "P7": ("P7", "P7-Pz", "EEG P7", "EEG P7-Pz"),
    "O1": ("O1", "O1-Pz", "EEG O1", "EEG O1-Pz"),
    "O2": ("O2", "O2-Pz", "EEG O2", "EEG O2-Pz"),
    "P8": ("P8", "P8-Pz", "EEG P8", "EEG P8-Pz"),
    "AF4": ("AF4", "AF4-Pz", "EEG AF4", "EEG AF4-Pz"),
}

# Common-6 is a separate, explicitly evidenced adapter.  ACNS defines the
# old 10-20 T5/T6 names as the P7/P8 names used in the modified 10-10
# nomenclature, and the DSI-24 specification lists the physical positions as
# P7/T5 and P8/T6.  The reference suffix remains part of the EDF evidence.
COMMON_6_CHANNELS = ("F7", "F3", "P7", "O1", "O2", "P8")
COMMON_6_EDF_ALIASES: dict[str, tuple[str, ...]] = {
    "F7": ("F7-Pz", "EEG F7-Pz"),
    "F3": ("F3-Pz", "EEG F3-Pz"),
    "P7": ("T5-Pz", "EEG T5-Pz", "P7-Pz", "EEG P7-Pz"),
    "O1": ("O1-Pz", "EEG O1-Pz"),
    "O2": ("O2-Pz", "EEG O2-Pz"),
    "P8": ("T6-Pz", "EEG T6-Pz", "P8-Pz", "EEG P8-Pz"),
}

AUTHOR_MAT_CHANNELS = (
    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2",
    "P8", "T8", "FC6", "F4", "F8", "AF4",
)

# This is the exact valid-record selection in the checked-in author notebook:
# five records for persons 1–3, four records for persons 4–5.
AUTHOR_RECORD_IDS = (
    3, 4, 5, 6, 7,
    10, 11, 12, 13, 14,
    17, 18, 19, 20, 21,
    24, 25, 26, 27,
    31, 32, 33, 34,
)
AUTHOR_BLOCKS = (
    ("focus", 0.0, 600.0),
    ("unfocus", 600.0, 1200.0),
)


def load_common7_edf_recording(
    edf_path: Path,
    *,
    allow_locked: bool = False,
) -> tuple[np.ndarray, float, list[str]]:
    """Load an EDF using the explicit common-7 channel mapping."""
    return load_eeg_recording(
        edf_path,
        allow_locked=allow_locked,
        channel_names=COMMON_7_CHANNELS,
        channel_aliases=COMMON_7_EDF_ALIASES,
    )


def load_common6_edf_recording(
    edf_path: Path,
    *,
    allow_locked: bool = False,
) -> tuple[np.ndarray, float, list[str]]:
    """Load DSI-24 EDF data using the explicit common-6 nomenclature map."""
    return load_eeg_recording(
        edf_path,
        allow_locked=allow_locked,
        channel_names=COMMON_6_CHANNELS,
        channel_aliases=COMMON_6_EDF_ALIASES,
    )


def _mat_scalar(value: Any, name: str) -> Any:
    array = np.asarray(value).squeeze()
    if array.size != 1:
        raise ValueError(f"MAT field {name!r} is not scalar: shape={array.shape}")
    return array.item()


def load_author_mat_recording(
    mat_path: Path,
    *,
    requested_channels: tuple[str, ...] = COMMON_7_CHANNELS,
) -> tuple[np.ndarray, float, list[str]]:
    """Load the author's 14-column EEG layout and return requested channels.

    The checked-in author notebook uses ``o.data[:, 3:17]`` and this exact
    channel order.  The adapter keeps the first 20 minutes because the author
    labels define two explicit 10-minute blocks within that interval.
    """
    mat_path = mat_path.resolve()
    payload = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    if "o" not in payload:
        raise ValueError(f"Author MAT has no top-level 'o' struct: {mat_path}")
    record = payload["o"]
    for field in ("data", "sampFreq"):
        if not hasattr(record, field):
            raise ValueError(f"Author MAT is missing o.{field}: {mat_path}")

    data = np.asarray(record.data, dtype=np.float64)
    if data.ndim != 2 or data.shape[1] < 17:
        raise ValueError(f"Unexpected author o.data shape {data.shape}: {mat_path}")
    sfreq = float(_mat_scalar(record.sampFreq, "sampFreq"))
    if not np.isclose(sfreq, 128.0):
        raise ValueError(f"Author sampling rate is not 128 Hz: {sfreq} ({mat_path})")
    required_samples = int(round(1200.0 * sfreq))
    if data.shape[0] < required_samples:
        raise ValueError(
            f"Author recording is shorter than two 10-minute blocks: "
            f"{data.shape[0] / sfreq:.3f}s ({mat_path})"
        )

    eeg14 = data[:required_samples, 3:17].T
    selected, channels = select_named_channels(
        eeg14,
        list(AUTHOR_MAT_CHANNELS),
        requested_channels,
    )
    if not np.isfinite(selected).all():
        raise ValueError(f"Author MAT contains non-finite EEG values: {mat_path}")
    return selected, sfreq, channels


def author_block_manifest(repo_root: Path, *, split: str = "unassigned") -> pd.DataFrame:
    """Build one row per explicit focus/unfocus block in each valid MAT."""
    repo_root = repo_root.resolve()
    rows: list[dict[str, Any]] = []
    for record_id in AUTHOR_RECORD_IDS:
        mat_path = repo_root / "data" / "reference" / "original_mat" / f"eeg_record{record_id}.mat"
        if not mat_path.is_file():
            raise FileNotFoundError(f"Missing author MAT: {mat_path}")
        source_id = f"author_eeg_record{record_id}"
        for label, start_sec, end_sec in AUTHOR_BLOCKS:
            rows.append(
                {
                    "dataset_version": "author_mat_v1",
                    "recording_id": f"{source_id}_{label}",
                    "source_recording_id": source_id,
                    "session_group_id": source_id,
                    "source": "author",
                    "subject_id": "author",
                    "canonical_label": label,
                    "dataset_role": "author_candidate",
                    "split": split,
                    "edf_path": str(mat_path.relative_to(repo_root)).replace("\\", "/"),
                    "edf_path_abs": mat_path,
                    "activity_start_s": start_sec,
                    "activity_end_s": end_sec,
                    "sfreq_hz": 128.0,
                    "window_sec": baseline.WINDOW_SEC,
                    "step_sec": baseline.STEP_SEC,
                }
            )
    return pd.DataFrame(rows)


def inspect_author_mat_files(repo_root: Path) -> pd.DataFrame:
    """Record the real MAT container/schema for every selected recording."""
    repo_root = repo_root.resolve()
    rows: list[dict[str, Any]] = []
    for record_id in AUTHOR_RECORD_IDS:
        mat_path = repo_root / "data" / "reference" / "original_mat" / f"eeg_record{record_id}.mat"
        payload = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
        record = payload["o"]
        data = np.asarray(record.data)
        marker = np.asarray(getattr(record, "marker", np.asarray([])))
        trials = np.asarray(getattr(record, "trials", np.asarray([])))
        rows.append(
            {
                "record_id": f"eeg_record{record_id}",
                "mat_filename": mat_path.name,
                "o_id": str(getattr(record, "id", "")),
                "top_level_data_field": "o.data",
                "data_rows_samples": int(data.shape[0]) if data.ndim >= 1 else None,
                "data_columns": int(data.shape[1]) if data.ndim >= 2 else None,
                "sampFreq_hz": float(_mat_scalar(record.sampFreq, "sampFreq")),
                "nS": int(_mat_scalar(record.nS, "nS")) if hasattr(record, "nS") else None,
                "duration_s": float(data.shape[0] / float(_mat_scalar(record.sampFreq, "sampFreq"))) if data.ndim >= 1 else None,
                "marker_shape": str(marker.shape),
                "trials_shape": str(trials.shape),
                "author_slice": "o.data[:20*128*60, 3:17]",
                "author_channel_order": ", ".join(AUTHOR_MAT_CHANNELS),
                "common7_channel_order": ", ".join(COMMON_7_CHANNELS),
                "common6_channel_order": ", ".join(COMMON_6_CHANNELS),
            }
        )
    return pd.DataFrame(rows)


def load_source_recording(
    path: Path,
    *,
    channel_set: str = "common7",
) -> tuple[np.ndarray, float, list[str]]:
    """Dispatch a source path to a shared MAT/EDF channel adapter."""
    if channel_set not in {"common6", "common7"}:
        raise ValueError(f"Unsupported channel set: {channel_set}")
    if path.suffix.casefold() == ".mat":
        requested = COMMON_6_CHANNELS if channel_set == "common6" else COMMON_7_CHANNELS
        return load_author_mat_recording(path, requested_channels=requested)
    if path.suffix.casefold() == ".edf":
        if channel_set == "common6":
            return load_common6_edf_recording(path)
        return load_common7_edf_recording(path)
    raise ValueError(f"Unsupported source recording suffix: {path}")


def build_source_feature_dataset(
    rows: pd.DataFrame,
    *,
    channel_set: str = "common7",
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Reuse the baseline dataset builder with a source-format loader."""
    return baseline.build_feature_dataset(
        rows,
        load_recording_fn=lambda path: load_source_recording(path, channel_set=channel_set),
    )


def inspect_common7_edf_paths(paths: Iterable[Path]) -> pd.DataFrame:
    """Inspect EDF headers and report explicit common-7 coverage only."""
    return _inspect_edf_paths(paths, COMMON_7_CHANNELS, COMMON_7_EDF_ALIASES, "common7")


def inspect_common6_edf_paths(paths: Iterable[Path]) -> pd.DataFrame:
    """Inspect EDF headers using the evidenced common-6 T5/T6 adapter."""
    return _inspect_edf_paths(paths, COMMON_6_CHANNELS, COMMON_6_EDF_ALIASES, "common6")


def _inspect_edf_paths(
    paths: Iterable[Path],
    required_channels: tuple[str, ...],
    aliases: dict[str, tuple[str, ...]],
    channel_set: str,
) -> pd.DataFrame:
    """Inspect EDF headers for one explicit channel adapter."""
    rows: list[dict[str, Any]] = []
    for path in paths:
        path = Path(path).resolve()
        raw = mne.io.read_raw_edf(str(path), preload=False, infer_types=True, verbose=False)
        available = list(raw.ch_names)
        normalized = {
            " ".join(str(name).strip().casefold().split()): name
            for name in available
        }
        matched: dict[str, str | None] = {}
        missing: list[str] = []
        for canonical in required_channels:
            channel_aliases = aliases[canonical]
            actual = next(
                (
                    normalized[" ".join(alias.strip().casefold().split())]
                    for alias in channel_aliases
                    if " ".join(alias.strip().casefold().split()) in normalized
                ),
                None,
            )
            matched[canonical] = actual
            if actual is None:
                missing.append(canonical)
        rows.append(
            {
                "edf_path": str(path),
                "sampling_rate_hz": float(raw.info["sfreq"]),
                "available_channels": ", ".join(available),
                "matched_channels": "; ".join(f"{key}={value}" for key, value in matched.items()),
                f"missing_{channel_set}_channels": ", ".join(missing),
                f"{channel_set}_available": not missing,
            }
        )
    return pd.DataFrame(rows)
