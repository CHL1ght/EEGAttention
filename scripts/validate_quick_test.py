"""Read-only QuickTest acceptance: real EDFs, routing and no-fit guards.

Run from the repository: python scripts/validate_quick_test.py
No new recordings, model files or experiment results are written.
"""
from __future__ import annotations

import json
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC

import subject_model_utils as quick

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    locked = ROOT / "data/locked/2026-09-07"
    lyc_before = locked / "lyc_focus1_20260907.edf"
    lyc_after = locked / "lyc_focus_202609072034_raw.edf"
    unfocus = locked / "lyc_unfocus1_20260907.edf"
    zyf = locked / "zyf_focus1_20260907.edf"
    hashes_before = {
        str(path): quick.sha256_file(path)
        for path in [*ROOT.glob("artifacts/**/pipeline.joblib"), *locked.glob("*")]
        if path.is_file()
    }
    guards = []
    with ExitStack() as stack:
        for cls in (Pipeline, StandardScaler, PCA, SVC):
            for name in ("fit", "fit_transform", "partial_fit"):
                if hasattr(cls, name):
                    guards.append(stack.enter_context(patch.object(
                        cls, name, side_effect=AssertionError(f"Forbidden: {cls.__name__}.{name}")
                    )))
        stack.enter_context(patch.object(joblib, "dump", side_effect=AssertionError("No model writes")))
        real_runs = {
            str(path): quick.run_quick_test(path, verbose=False)
            for path in (lyc_before, lyc_after, unfocus, zyf)
        }
        first = real_runs[str(lyc_before)]
        for path, result in real_runs.items():
            assert result["feature_dimensions"] == {"pooled": 240, "personal": 240, "mixed_common6": 60}
            assert result["features"].shape[0] == result["common6_features"].shape[0]
            assert result["common6_channels"] == list(quick.COMMON_6_CHANNELS)
            assert result["fit_calls"] == 0
            assert result["display_table"]["Model"].tolist()[-1] == "mixed-common6"
        # Use the real predictions already computed to test the A/B wrapper;
        # this avoids re-reading the same recordings for display-only checks.
        def cached(path, repo_root=None, *, verbose=True):
            return real_runs[str(path)]

        with patch.object(quick, "run_quick_test", side_effect=cached):
            same = quick.compare_quick_tests(lyc_before, lyc_after, verbose=False)
            different = quick.compare_quick_tests(lyc_before, unfocus, verbose=False)
            other_subject = quick.compare_quick_tests(lyc_before, zyf, verbose=False)
            duplicate = quick.compare_quick_tests(lyc_before, lyc_before, verbose=False)
        assert same["improvement_comparable"]
        assert same["comparison"]["Δ Accuracy"].notna().all()
        np.testing.assert_allclose(same["comparison"]["Δ Accuracy"],
                                   same["comparison"]["After Accuracy"] - same["comparison"]["Before Accuracy"])
        for result in (different, other_subject, duplicate):
            assert not result["improvement_comparable"]
            assert result["comparison"]["Δ Accuracy"].isna().all()

        # Synthetic filename identities only; no counterfeit EDF is created.
        # Real EDF and saved model inference are reused with identity override.
        for name, subject in (
            ("zqd_focus_202609141630_feedback0.edf", "zqd"),
            ("newperson_focus_202609141630_feedback0.edf", "unknown"),
            ("lyc_focus_no_timestamp.edf", "unknown"),
        ):
            identity = quick.parse_edf_identity(Path(name))
            assert identity["subject"] == subject and not identity["personal_model_allowed"]
            with patch.object(quick, "parse_edf_identity", return_value=identity), patch.object(
                quick, "load_personal_pipeline", side_effect=AssertionError("Personal must be skipped")
            ), patch.object(quick, "_quick_features") as feature_loader:
                feature_loader.side_effect = lambda path, common6: (
                    first["common6_features"] if common6 else first["features"],
                    first["predictions"]["pooled"]["window_start_s"].to_numpy(),
                    first["duration_sec"],
                    first["common6_channels"] if common6 else first["channels"],
                    first["sampling_rate_hz"],
                )
                result = quick.run_quick_comparison(lyc_before, ROOT, verbose=False)
                assert result["feature_dimensions"] == {"pooled": 240, "mixed_common6": 60}
                assert any("skipped" in notice for notice in result["notices"])
        for state in ("focus", "unfocus"):
            for round_no in (0, 1, 2):
                parsed = quick.parse_edf_identity(Path(f"lyc_{state}_202609141630_feedback{round_no}.edf"))
                assert parsed["true_label"] == state and parsed["subject"] == "lyc"
        assert quick.parse_edf_identity(Path("lyc_rest_202609141630_feedback0.edf"))["true_label"] is None

        # The notebook's default blank inputs must execute without model work.
        notebook = json.loads((ROOT / "notebooks/lab_quick_test_legacy_model.ipynb").read_text(encoding="utf-8"))
        scope = {}
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                exec(compile("".join(cell["source"]), "<quicktest-notebook>", "exec"), scope)
        assert all(guard.call_count == 0 for guard in guards)
    for path, expected in hashes_before.items():
        assert quick.sha256_file(Path(path)) == expected, f"Protected file changed: {path}"
    print("PASS: real lyc/zyf EDF inference; 240/240/60 feature routing; same-label A/B; mismatch/identity guards.")
    print("PASS: fit/fit_transform/partial_fit calls=0; model dump blocked; model and locked-file hashes unchanged.")
    print("Existing EDFs are interface dry-run inputs, not new LAB_FEEDBACK recordings or new final-test results.")


if __name__ == "__main__":
    main()
