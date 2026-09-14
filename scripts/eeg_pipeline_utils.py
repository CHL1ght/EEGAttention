"""Small shared helpers for the Legacy baseline and locked inference paths."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterator, Mapping

import mne
import numpy as np
from scipy.signal import welch


def save_json(path: Path, value: Any) -> None:
    """Write stable, human-readable JSON."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def save_dataframe(path: Path, dataframe: Any) -> None:
    """Write a DataFrame to CSV, creating its parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)


def sha256_file(path: Path) -> str:
    """Return a file SHA-256 without loading the whole file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_locked_path(path: Path) -> bool:
    """Identify paths below the protected ``data/locked`` tree."""
    normalized = str(path.resolve()).replace("\\", "/").lower()
    return "/data/locked/" in normalized or normalized.endswith("/data/locked")


def assert_not_locked(path: Path, description: str) -> None:
    """Keep the training entry point from accidentally reading locked data."""
    if is_locked_path(path):
        raise RuntimeError(f"Refusing to access locked data ({description}): {path}")


def print_banner(title: str) -> None:
    """Print the compact heading shared by both formal entry points."""
    print("\n" + "=" * 60)
    print(f" EEGAttention — {title}")
    print("=" * 60)


def print_metric(name: str, value: Any) -> None:
    """Print one aligned summary value."""
    print(f"  {name:<20}: {value}")


def select_named_channels(
    data: np.ndarray,
    available_channels: list[str],
    requested_channels: tuple[str, ...],
    aliases: Mapping[str, tuple[str, ...]] | None = None,
) -> tuple[np.ndarray, list[str]]:
    """Select an explicitly mapped channel layout without spatial guessing.

    Matching is case-insensitive and whitespace-normalized.  ``aliases`` is
    intentionally explicit: a channel is accepted only when its exact name
    appears in the canonical name or in the caller-provided alias list.
    """
    if data.ndim != 2 or data.shape[0] != len(available_channels):
        raise ValueError("Channel data must have shape (channels, samples)")
    alias_map = aliases or {}
    normalized = {
        " ".join(str(name).strip().casefold().split()): index
        for index, name in enumerate(available_channels)
    }
    indices: list[int] = []
    missing: list[str] = []
    for canonical in requested_channels:
        candidates = (canonical, *alias_map.get(canonical, ()))
        index = next(
            (
                normalized[" ".join(str(candidate).strip().casefold().split())]
                for candidate in candidates
                if " ".join(str(candidate).strip().casefold().split()) in normalized
            ),
            None,
        )
        if index is None:
            missing.append(canonical)
        else:
            indices.append(index)
    if missing:
        raise ValueError(
            "Missing explicitly mapped channel(s): "
            f"{missing}; available channels={available_channels}"
        )
    return np.asarray(data[indices], dtype=np.float64), list(requested_channels)


def load_eeg_recording(
    edf_path: Path,
    *,
    target_fs: float = 128.0,
    allow_locked: bool = False,
    channel_names: tuple[str, ...] | None = None,
    channel_aliases: Mapping[str, tuple[str, ...]] | None = None,
) -> tuple[np.ndarray, float, list[str]]:
    """Load, select EEG channels, and resample one EDF consistently.

    ``allow_locked`` is only used by the separately validated inference
    entry point; the training baseline keeps the default protection enabled.
    """
    if not allow_locked:
        assert_not_locked(edf_path, "EDF")
    raw = mne.io.read_raw_edf(
        str(edf_path),
        preload=True,
        infer_types=True,
        verbose=False,
    )
    try:
        raw.pick_types(eeg=True, stim=False, misc=False, verbose=False)
    except TypeError:
        raw.pick_types(eeg=True, stim=False, misc=False)
    if len(raw.ch_names) == 0:
        raise ValueError(f"{edf_path} has no MNE-recognized EEG channels")

    selected_channels = list(raw.ch_names)
    if channel_names is not None:
        all_channels = list(raw.ch_names)
        all_data = raw.get_data()
        _selected_data, selected_channels = select_named_channels(
            all_data,
            all_channels,
            channel_names,
            channel_aliases,
        )
        normalized = {
            " ".join(str(name).strip().casefold().split()): index
            for index, name in enumerate(all_channels)
        }
        actual_names = []
        for canonical in channel_names:
            candidates = (canonical, *(channel_aliases or {}).get(canonical, ()))
            actual_names.append(
                all_channels[
                    next(
                        normalized[" ".join(str(candidate).strip().casefold().split())]
                        for candidate in candidates
                        if " ".join(str(candidate).strip().casefold().split()) in normalized
                    )
                ]
            )
        raw.pick(actual_names)

    source_fs = float(raw.info["sfreq"])
    if not np.isclose(source_fs, float(round(source_fs)), atol=1e-6):
        raise ValueError(f"Non-integral source sampling rate is unsupported: {source_fs}")
    if not np.isclose(source_fs, target_fs):
        raw.resample(target_fs, npad="auto", verbose=False)
    return raw.get_data(), float(raw.info["sfreq"]), selected_channels


def preprocess_eeg(
    segment_data: np.ndarray,
    sfreq: float,
    *,
    l_freq: float = 0.5,
    h_freq: float = 43.0,
) -> np.ndarray:
    """Apply the frozen MNE FIR bandpass to one logical segment."""
    return mne.filter.filter_data(
        segment_data,
        sfreq=sfreq,
        l_freq=l_freq,
        h_freq=h_freq,
        method="fir",
        fir_design="firwin",
        verbose=False,
    )


def make_windows(
    segment_data: np.ndarray,
    sfreq: float,
    *,
    window_sec: float = 4.0,
    step_sec: float = 2.0,
) -> Iterator[tuple[np.ndarray, float]]:
    """Yield fixed-size windows and offsets without crossing segment bounds."""
    window_size = int(round(window_sec * sfreq))
    step_size = int(round(step_sec * sfreq))
    if segment_data.shape[1] < window_size:
        raise ValueError("Segment is shorter than one frozen 4-second window")
    for start in range(0, segment_data.shape[1] - window_size + 1, step_size):
        yield segment_data[:, start : start + window_size], start / sfreq


def extract_bandpower_features(
    window_data: np.ndarray,
    sfreq: float,
    bands: dict[str, tuple[float, float]],
    *,
    welch_nperseg_sec: float = 2.0,
) -> np.ndarray:
    """Extract log absolute and relative Welch power for each channel/band."""
    features: list[float] = []
    for channel_data in window_data:
        freqs, psd = welch(
            channel_data,
            fs=sfreq,
            nperseg=min(len(channel_data), int(sfreq * welch_nperseg_sec)),
        )
        total_idx = (freqs >= 1.0) & (freqs <= 43.0)
        total_power = float(np.trapezoid(psd[total_idx], freqs[total_idx])) + 1e-12
        for low, high in bands.values():
            band_idx = (freqs >= low) & (freqs < high)
            power = float(np.trapezoid(psd[band_idx], freqs[band_idx])) + 1e-12
            features.extend((float(np.log(power)), float(power / total_power)))
    return np.asarray(features, dtype=np.float64)


def extract_segment_features(
    data: np.ndarray,
    sfreq: float,
    start_sec: float,
    end_sec: float,
    bands: dict[str, tuple[float, float]],
    *,
    window_sec: float = 4.0,
    step_sec: float = 2.0,
    l_freq: float = 0.5,
    h_freq: float = 43.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Filter a manifest interval, then turn it into band-power windows."""
    start = int(round(start_sec * sfreq))
    stop = int(round(end_sec * sfreq))
    if start < 0 or stop > data.shape[1] or stop <= start:
        raise ValueError(
            f"Manifest interval [{start_sec}, {end_sec}) is outside EDF "
            f"({data.shape[1] / sfreq:.3f} s)"
        )
    filtered = preprocess_eeg(
        data[:, start:stop],
        sfreq,
        l_freq=l_freq,
        h_freq=h_freq,
    )
    features: list[np.ndarray] = []
    starts: list[float] = []
    for window, offset_sec in make_windows(
        filtered,
        sfreq,
        window_sec=window_sec,
        step_sec=step_sec,
    ):
        features.append(extract_bandpower_features(window, sfreq, bands))
        starts.append(start_sec + offset_sec)
    return np.asarray(features), np.asarray(starts, dtype=np.float64)
