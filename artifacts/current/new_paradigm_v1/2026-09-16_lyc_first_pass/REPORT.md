# 2026-09-16 lyc New Paradigm v1 first pass

## Scope

Only the six 2026-09-16 lyc New Paradigm v1 binary sessions were used: three focus and three unfocus. No historical, 2026-09-14, author, common6, locked-test, or other data were read. Evaluation used complete-session leave-one-session-out with six folds.

The preprocessing, feature extraction, and classifier parameters were copied unchanged from the existing baseline: 128 Hz resampling, 0.5–43 Hz FIR filtering, 4 s windows with 2 s step, Welch log/relative band power, StandardScaler, PCA retaining 95% variance, and balanced RBF SVC with C=10 and probability output.

## Fold results

| fold | held-out session | true | majority prediction | windows | window accuracy | mean focus probability | window confusion `[UU,UF;FU,FF]` |
|---:|---|---|---|---:|---:|---:|---|
| 1 | `20260916_lyc_focus_01` | focus | focus | 309 | 98.06% | 0.9683 | `[[0, 0], [6, 303]]` |
| 2 | `20260916_lyc_focus_02` | focus | focus | 266 | 99.25% | 0.9872 | `[[0, 0], [2, 264]]` |
| 3 | `20260916_lyc_focus_03` | focus | focus | 142 | 100.00% | 0.9898 | `[[0, 0], [0, 142]]` |
| 4 | `20260916_lyc_unfocus_01` | unfocus | unfocus | 316 | 98.10% | 0.0214 | `[[310, 6], [0, 0]]` |
| 5 | `20260916_lyc_unfocus_02` | unfocus | unfocus | 285 | 100.00% | 0.0017 | `[[285, 0], [0, 0]]` |
| 6 | `20260916_lyc_unfocus_03` | unfocus | unfocus | 338 | 94.67% | 0.1094 | `[[320, 18], [0, 0]]` |

## Overall held-out metrics

- Session-level accuracy: 100.00%
- Session-level balanced accuracy: 100.00%
- Window-level accuracy: 98.07%
- Window-level balanced accuracy: 98.16%
- Held-out windows: 1656

Session confusion matrix (rows=true, columns=predicted; label order unfocus, focus):

- unfocus: [3, 0]
- focus: [0, 3]

Window confusion matrix (rows=true, columns=predicted; label order unfocus, focus):

- unfocus: [915, 24]
- focus: [8, 709]

## Observe prediction-only control

The observe session was not used for fit, model selection, or any accuracy calculation. Its condition is: 认真观战王者、减少主动手部操作，用于运动/操作干扰对照。

- Session majority prediction: unfocus
- Windows: 280
- Predicted focus windows: 6 (2.14%)
- Mean focus probability: 0.0286
- Median focus probability: 0.0000
- Focus probability range: 0.0000–0.9196

## Interpretation boundary

**这是单日 6-session exploratory result，不代表跨日泛化。**

All three focus sessions were recorded before all three unfocus sessions on the same day. Label is therefore confounded with recording order, so temporal, device, electrode, fatigue, or other session drift may contribute to the high score.

No second-round tuning, feature changes, relabeling, threshold adjustment, or calibration was performed after seeing these results.
