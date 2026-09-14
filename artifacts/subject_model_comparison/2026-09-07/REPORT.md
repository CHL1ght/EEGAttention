# Subject-dependent model comparison

- Test set: `LOCKED_TEST 2026-09-07`; reference rest sessions excluded.
- Training: personal models fit only on their own historical `legacy_baseline_candidate` rows.
- Leakage policy: this evaluator made `0` fit calls; locked data are prediction-only.
- Labels: `unfocus`, `focus`; confusion matrices use that order.

## Cross-evaluation matrix

| Model | lyc test | zyf test |
|---|---:|---:|
| Existing pooled frozen model | 65.54% | 46.11% |
| lyc personal model | 46.68% | 67.94% |
| zyf personal model | 45.79% | 41.35% |

## Sessions used

- `20260907_lyc_focus_01` — subject `lyc`, label `focus`, `data/locked/2026-09-07/lyc_focus1_20260907.edf`
- `20260907_lyc_focus_02` — subject `lyc`, label `focus`, `data/locked/2026-09-07/lyc_focus_202609072034_raw.edf`
- `20260907_lyc_unfocus_01` — subject `lyc`, label `unfocus`, `data/locked/2026-09-07/lyc_unfocus1_20260907.edf`
- `20260907_zyf_focus_01` — subject `zyf`, label `focus`, `data/locked/2026-09-07/zyf_focus1_20260907.edf`
- `20260907_zyf_focus_02` — subject `zyf`, label `focus`, `data/locked/2026-09-07/zyf_focus2_20260907.edf`
- `20260907_zyf_unfocus_01` — subject `zyf`, label `unfocus`, `data/locked/2026-09-07/zyf_unfocus1_20260907.edf`

The table is a window-level accuracy comparison on the same independent locked sessions. The personal models are not calibrated or fine-tuned in this phase.
