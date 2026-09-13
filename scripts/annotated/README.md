# EEGAttention 教学注释版

这里的文件是当前三个正式脚本的中文教学副本，目标是帮助刚开始学习 Python 工程代码的读者顺着实验流程读懂代码。

## 重要边界

- 本目录不是 Python package，因此不要新建 `__init__.py`。
- annotated 文件不是正式训练入口，也不是正式 LOCKED_TEST 入口。
- 不要运行这些文件，不要让它们生成或覆盖任何 artifact、模型或指标。
- 正式实验只能运行 `scripts/legacy_baseline_v0.py` 和 `scripts/evaluate_locked_test.py`。
- 如果正式源文件以后发生变化，这些教学副本需要人工同步检查。

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
