# legacy_baseline_v0 状态说明

## 当前结论

`legacy_baseline_v0` 尚未生成。仓库中已有旧实验代码、特征缓存、指标和部分深度模型权重，但没有保存可直接用于新数据的传统 `Scaler→PCA→SVC` Pipeline。

## 为什么旧 `.npy` 不等于已冻结模型

`artifacts/reproductions/upstream_pipeline/preprocessed_arrays/` 中的四个数组是修改后的上游 Notebook 用原作者 MAT 数据生成的训练/测试缓存。`X_train` 和 `X_test` 在保存前已经过 `StandardScaler`，但 Scaler 对象本身没有保存。

因此无法对 LOCKED_TEST 严格复用当时的均值、方差和后续 PCA/SVC 状态。这些数组只是历史复现缓存，不是正式 baseline。

## 计划的生成方式

1. 从 `data/legacy/multiclass_10min/` 选取单状态 EDF。
2. `focus → focus`，`iu + ou → unfocus`，`daze` 不进入二分类。
3. 先按完整 EDF/session 划分训练集和验证集，再切窗。
4. 只在训练集 `fit` Scaler、PCA 和 SVC。
5. 固定参数并保存完整 Pipeline、数据清单、配置和验证结果。
6. 完成上述冻结后，才允许对 `locked_test` 进行一次独立评估。

## 里程碑口径

- `00.1` Legacy 数据封存：已完成。
- `00.2` 预处理/特征/PCA/SVC 冻结：待规范主 Notebook 实现。
- `00.3` 完整 recording/session 隔离：规则已确立，待主 Notebook 强制执行。
- LOCKED_TEST 数据封存：已完成。
- 首次独立盲测：未执行。
