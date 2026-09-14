# Unified pooled / personal / author comparison

Accuracy 和 balanced accuracy 均按正式 2026-09-07 LOCKED_TEST 记录；author held-out 列来自 recording-level GroupKFold。LOCKED_TEST 只做 transform/predict/metric。

## Unified table

| model | lyc accuracy | lyc balanced | zyf accuracy | zyf balanced | author/cross-source held-out balanced | status |
|---|---:|---:|---:|---:|---:|---|
| Existing pooled frozen model | 65.54% | 64.28% | 46.11% | 57.69% | N/A | available |
| lyc personal model | 46.68% | 47.67% | 67.94% | 51.80% | N/A | available |
| zyf personal model | 45.79% | 56.45% | 41.35% | 52.14% | N/A | available |
| our-common7 pooled model | N/A | N/A | N/A | N/A | N/A | blocked |
| author-only model | N/A | N/A | N/A | N/A | 64.12% | not_comparable |
| our+author mixed model | N/A | N/A | N/A | N/A | N/A | blocked |

## Data and blocker

- Required explicit channel order: `F7, F3, P7, O1, O2, P8, AF4`
- Current formal LOCKED_TEST common7 available: `False`
- Cross-source status: missing explicit common-7 channel(s): AF4, P7, P8
- Author GroupKFold balanced accuracy: 64.12% ± 4.37%
- T5/T6 等空间近似名称没有替代 P7/P8；缺少关键通道时 author-only → EDF、our-common7 和 mixed 结果保持 N/A。

Existing pooled 和 lyc/zyf personal 结果直接读取上一阶段同一 LOCKED_TEST 比较，不覆盖旧 frozen artifact。
