# Unified pooled / personal / cross-source comparison

本报告使用 `common6` 特征协议。正式 2026-09-07 LOCKED_TEST 仅执行 transform/predict/metric；fit calls = `0`。

## Unified table

| model | lyc accuracy | lyc balanced | zyf accuracy | zyf balanced | held-out balanced | status |
|---|---:|---:|---:|---:|---:|---|
| Existing pooled frozen model | 65.54% | 64.28% | 46.11% | 57.69% | N/A | available |
| lyc personal model | 46.68% | 47.67% | 67.94% | 51.80% | N/A | available |
| zyf personal model | 45.79% | 56.45% | 41.35% | 52.14% | N/A | available |
| author-common6 model | 37.56% | 50.00% | 33.17% | 50.00% | 64.69% | available |
| our-common6 model | 44.46% | 48.29% | 36.03% | 46.78% | 69.51% | available |
| mixed-common6 model | 47.48% | 52.68% | 51.03% | 55.77% | 67.31% | available |

## Channel and reference status

- Required channel order: `F7, F3, P7, O1, O2, P8`
- Common6 adapter: `F7-Pz→F7, F3-Pz→F3, T5-Pz→P7, O1-Pz→O1, O2-Pz→O2, T6-Pz→P8`; `AF4` is excluded.
- Our EDF / DSI-Streamer hardware reference: `Pz (confirmed)`.
- Author MAT reference: `unknown`; therefore reference compatibility is `uncertain`.
- LOCKED_TEST channel availability: `True`.
- Cross-source status: `exploratory / channel-aligned but reference compatibility uncertain`.
- Cross-source differences may reflect subject, session, device, task/paradigm, preprocessing representation, and unresolved author-reference differences.

## Author-only channel ablation

| author model | GroupKFold accuracy | GroupKFold balanced accuracy |
|---|---:|---:|
| author-only-7ch | 64.12% | 64.12% |
| author-common6 | 64.69% | 64.69% |

去掉 `AF4` 后仍沿用同一 recording-level GroupKFold；此表用于观察作者数据内部变化，不把它解释为跨设备效果。

## Output details

- `unified_model_comparison.csv`：按 model × test subject 的准确率、balanced accuracy、预测类别数量/比例和混淆矩阵。
- `locked_predictions.csv`：旧 pooled/personal 预测与本轮 common6 预测的逐窗口记录。
- `locked_session_metrics.csv`：逐 session accuracy、预测类别数量/比例；单一真实标签 session 的 balanced accuracy 记为 N/A。
- `locked_confusion_matrix.csv`：本轮 common6 模型按 subject 的混淆矩阵长表。
- `comparison_summary.json`：通道/reference 状态、fit policy、验证指标和新模型哈希。

Existing pooled frozen、lyc personal、zyf personal 结果直接读取上一阶段比较，不重新训练、不覆盖旧 artifact。
