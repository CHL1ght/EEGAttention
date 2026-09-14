# `scripts/annotated/`

这里保存三个正式核心脚本的中文教学注释副本，帮助读者顺着实验流程阅读代码。它们与正式脚本保持概念对应，但不是生产代码，也不应被当作独立实现。

## 直接文件

| 文件 | 对应正式文件 | 说明 |
|---|---|---|
| `eeg_pipeline_utils_annotated.py` | `../eeg_pipeline_utils.py` | 注释 EDF 读取、通道选择、预处理、窗口切分、Welch 特征以及 sklearn 前处理辅助函数。 |
| `legacy_baseline_v0_annotated.py` | `../legacy_baseline_v0.py` | 注释旧 pooled baseline 的 manifest 筛选、EDF/session 划分、Scaler/PCA/SVC 训练、验证和冻结过程。 |
| `evaluate_locked_test_annotated.py` | `../evaluate_locked_test.py` | 注释冻结 pooled pipeline 在 LOCKED_TEST 上的 prediction-only 评估，以及窗口、session、subject 汇总。 |
| `README.md` | — | 本目录的阅读顺序、使用边界和文件格式说明。 |

## 重要边界

- 本目录不是 Python package，因此不要新建 `__init__.py`。
- annotated 文件不是正式训练入口，也不是正式 LOCKED_TEST 入口。
- 不要运行这些文件，不要让它们生成或覆盖任何 artifact、模型或指标。
- 正式实验只能运行 `scripts/legacy_baseline_v0.py` 和 `scripts/evaluate_locked_test.py`。
- 如果正式源文件以后发生变化，这些教学副本需要人工同步检查。

本目录没有 personal model 的复制实现。`train_subject_models.py` 和 `evaluate_subject_models.py` 直接复用正式共享库及 baseline 逻辑；需要理解这部分时，应回到 `scripts/subject_model_utils.py` 和 `scripts/README.md`。

## 推荐阅读顺序

第一遍，先读 [`legacy_baseline_v0_annotated.py`](legacy_baseline_v0_annotated.py) 的 `main()`、`train_and_freeze()` 和 `prepare_split()`，了解实验业务流程：

```text
Legacy manifest
  → candidate 筛选
  → session_group_id 划分
  → EDF / preprocessing / windows / features
  → X_train、y_train、X_val、y_val
  → StandardScaler → PCA → SVC
  → validation → 保存冻结产物
```

第二遍，读 [`eeg_pipeline_utils_annotated.py`](eeg_pipeline_utils_annotated.py)，理解 EEG 信号如何变成一个可以交给 sklearn 的数字矩阵。

第三遍，再回到 baseline，重点看 `build_baseline_pipeline()`、`pipeline.fit()` 和 validation-only `pipeline.predict()`。
这对应一个必须守住的边界：`fit-only-train`，即只有训练集允许 fit；`predict-only-validation`，即 validation 只能 predict。

第四遍，读 [`evaluate_locked_test_annotated.py`](evaluate_locked_test_annotated.py)，理解 frozen model 如何在独立 locked session 上只做 inference，以及为什么 `rest/reference` 不进入二分类 accuracy。

## 三种文件格式各自做什么

```text
JSON     → 配置、哈希、指标等机器容易读取的结构化信息
CSV      → split、逐窗口预测、逐 session/subject 汇总表
JOBLIB   → sklearn Pipeline 对象，包括已经 fit 好的状态
Markdown → 给人阅读的报告和教学说明
```
