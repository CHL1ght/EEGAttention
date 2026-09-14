# `scripts/`

这里是仓库的可执行脚本层：把 manifest、EDF 和既有模型串成可复现的校验、训练、评估流程。脚本本身不存放原始 EEG；运行结果写入 `artifacts/`，命令默认从仓库根目录执行。

## 直接文件

| 文件 | 作用 | 是否属于当前正式入口 |
|---|---|---|
| `eeg_pipeline_utils.py` | 共享 EEG 工具库：EDF 读取、通道选择、预处理、窗口切分、Welch 特征、Scaler/PCA/SVC 辅助逻辑，以及 manifest 字段处理。个人模型与旧 pooled sklearn 流程共同复用。 | 是，共享库 |
| `legacy_baseline_v0.py` | 旧版 pooled sklearn baseline 的训练、验证和冻结；负责把历史候选数据变成 `pipeline.joblib` 及配套 manifest、split、指标和预测表。 | 是，旧模型重建/回归入口 |
| `evaluate_locked_test.py` | 加载已经冻结的 pooled pipeline，在 `data/locked/` 的 LOCKED_TEST session 上执行 prediction-only 评估；不重新 fit。 | 是，最终锁定测试入口 |
| `subject_model_utils.py` | personal model 的薄封装：subject 识别、按 EDF/session 分组、训练/预测时复用 baseline 的流水线组件。不是第二套预处理算法。 | 是，共享库 |
| `train_subject_models.py` | 从明确身份的历史训练候选中分别训练 `lyc`、`zyf` personal model；以 EDF/session 为最小划分单位，拒绝 `zqd`、未知身份和 LOCKED_TEST。 | 是 |
| `evaluate_subject_models.py` | 在同一批 LOCKED_TEST 数据上评估 pooled、lyc personal、zyf personal，并输出 subject × model 交叉结果、窗口/ session 汇总和预测文件。 | 是 |
| `cross_source_utils.py` | MAT 与 common6/common7 EDF 的薄输入 adapter、明确通道映射、author block manifest 和共享特征数据集入口；common6 显式将 `T5-Pz/T6-Pz` 映射为 `P7/P8`。 | 是，共享库 |
| `diagnose_subject_models.py` | 生成 personal model 的类别分布、预测偏置、session 诊断、历史 LOGO、PCA 和 common7 通道报告；LOCKED_TEST 不 fit。 | 是 |
| `train_cross_source_models.py` | 用共享流水线训练 author-only-7ch、author-common6、our-common6/common7 和 mixed-common6/common7；训练侧只使用历史数据，按 recording/session 分组。 | 是 |
| `evaluate_cross_source_models.py` | 生成 common6/common7 的 pooled/personal/author/mixed 统一比较表、逐窗口预测、逐 session 指标、混淆矩阵和 predicted class ratio；LOCKED_TEST 只 predict。 | 是 |
| `validate_legacy_manifest.py` | 验证历史 manifest、39 个 EDF 的身份/标签/时间/分组/边界/文件头/SHA-256 等完整性。 | 是，只读验收 |
| `validate_locked_data.py` | 验证锁定数据的 manifest、标签、时长、采样率、配套文件和哈希。 | 是，只读验收 |
| `validate_reproduction_models.py` | 验证上游深度学习复现实验的 10 个权重文件完整性；不表示这些模型用于当前 personal/locked 结论。 | 是，只读验收 |
| `README.md` | 本目录脚本索引和实验边界说明。 | 文档 |

## 子目录

| 目录 | 内容 |
|---|---|
| `annotated/` | 三个正式核心脚本的中文教学注释副本，只用于阅读，不能作为实验入口。 |
| `legacy/` | 上游深度模型 worker、批量调度器和 ROC 绘图辅助脚本；只服务于历史复现实验。 |

## 当前个人模型流程

`train_subject_models.py` 和 `evaluate_subject_models.py` 共同实现本阶段 subject-dependent 对比，但算法仍来自 `legacy_baseline_v0.py` 和 `eeg_pipeline_utils.py`：

```text
明确 subject 的历史 EDF
  → 按 EDF/session 分组划分
  → 共享 EDF 读取、预处理、窗口和 Welch 特征
  → 仅训练侧 fit StandardScaler / PCA / SVC
  → 保存 personal pipeline
  → LOCKED_TEST 只 transform / predict / 计分
```

本目录没有 calibration、快速微调、domain adaptation、未知身份猜测或超参数大搜索逻辑。

## 常用命令

```powershell
python scripts/validate_legacy_manifest.py
python scripts/validate_locked_data.py
python scripts/train_subject_models.py
python scripts/evaluate_subject_models.py
python scripts/diagnose_subject_models.py
python scripts/train_cross_source_models.py --model author-only
python scripts/verify_common6_compatibility.py
python scripts/train_cross_source_models.py --model author-common6
python scripts/train_cross_source_models.py --model our-common6
python scripts/train_cross_source_models.py --model mixed-common6
python scripts/evaluate_cross_source_models.py --channel-set common6
```

在当前 Windows 环境也可以显式使用 EEG conda 环境的 Python。详细产物说明见 [`docs/REPOSITORY_FILE_GUIDE.md`](../docs/REPOSITORY_FILE_GUIDE.md)。

## Common6 兼容性门禁

`verify_common6_compatibility.py` 只读取 EDF 头、DSIStreamer CSV sidecar、作者 MAT 结构、作者 notebook 和已登记的权威外部证据。当前已确认 `T5-Pz→P7-Pz`、`T6-Pz→P8-Pz`，Our EDF reference 为 Pz；author MAT reference 仍 unknown，故跨源结果必须标注 exploratory/channel-aligned/reference uncertain。该审计本身不训练模型，也不读取 LOCKED_TEST 信号。

```powershell
python scripts/verify_common6_compatibility.py
```
