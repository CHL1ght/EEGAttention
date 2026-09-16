# 这个目录是什么

这里把读数据、做预测、核对结果变成可重复执行的步骤。

## 它属于项目哪一步

Stage 2–9：旧训练/评估入口保留用于复现；CURRENT 只新增 New Paradigm v1 数据验证入口。

前一步：Common6 通道对齐与 Mixed。
这一步：Notebook只填路径，信号处理由同一份函数负责，避免不同入口算出不同特征。
后一步：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

完整故事：[实验阶段地图](../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

Notebook只填路径，信号处理由同一份函数负责，避免不同入口算出不同特征。

## 输入从哪里来

manifest、原始EDF/MAT和artifacts中的已保存模型。

## 谁生成这里的文件

脚本由开发者维护；历史训练已生成既有产物。当前没有运行训练，也没有为 New Paradigm v1 建立训练入口。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [validate_new_paradigm_data.py](validate_new_paradigm_data.py) | 只读检查 New Paradigm v1 manifest schema、角色、observe reference 保护、路径、全部文件哈希及 EDF 时长/采样率/信号数，输出 `fit_calls=0`。 | 手写维护 | 随 v2 schema 同步维护 |
| [run_new_paradigm_first_pass.py](run_new_paradigm_first_pass.py) | 固定运行 2026-09-16 lyc 的 6-session LOSO first pass；冻结二分类 baseline 后再对 observe 做 prediction-only。 | 手写维护 | 不调参；只读 CURRENT manifest 指定数据 |
| [validate_historical_integrity.py](validate_historical_integrity.py) | 只读检查 9/14 的 11 条 metadata/sidecar/hash/标签冲突/资格、未进入旧/新 manifest，以及七个冻结模型哈希和 `fit_calls=0`。 | 手写维护 | 与冻结哈希和 pilot schema 同步维护 |
| [validate_markdown_links.py](validate_markdown_links.py) | 只读检查仓库 Markdown 的相对文件/目录链接。 | 手写维护 | 可维护 |
| [annotated/](annotated/README.md) | 这里是三个核心脚本的中文教学注释副本，只用于阅读，不是第二套正式算法。 | 目录 | 按子目录规则 |
| [legacy/](legacy/README.md) | 这里保留旧上游深度学习和ROC曲线的辅助脚本，不是当前三模型推理入口。 | 目录 | 按子目录规则 |
| [cross_source_utils.py](cross_source_utils.py) | MAT 与 common6/common7 EDF 的薄输入 adapter、明确通道映射、author block manifest 和共享特征数据集入口；common6 显式将 `T5-Pz/T6-Pz` 映射为 `P7/P8`。 | 手写维护 | 可维护，保留来源与实验边界 |
| [diagnose_subject_models.py](diagnose_subject_models.py) | 生成 personal model 的类别分布、预测偏置、session 诊断、历史 LOGO、PCA 和 common7 通道报告；LOCKED_TEST 不 fit。 | 手写维护 | 可维护，保留来源与实验边界 |
| [eeg_pipeline_utils.py](eeg_pipeline_utils.py) | 共享 EEG 工具库：EDF 读取、通道选择、预处理、窗口切分、Welch 特征、Scaler/PCA/SVC 辅助逻辑，以及 manifest 字段处理。个人模型与旧 pooled sklearn 流程共同复用。 | 手写维护 | 可维护，保留来源与实验边界 |
| [evaluate_cross_source_models.py](evaluate_cross_source_models.py) | 生成 common6/common7 的 pooled/personal/author/mixed 统一比较表、逐窗口预测、逐 session 指标、混淆矩阵和 predicted class ratio；LOCKED_TEST 只 predict。 | 手写维护 | 可维护，保留来源与实验边界 |
| [evaluate_locked_test.py](evaluate_locked_test.py) | 加载已经冻结的 pooled pipeline，在 `data/locked/` 的 LOCKED_TEST session 上执行 prediction-only 评估；不重新 fit。 | 手写维护 | 可维护，保留来源与实验边界 |
| [evaluate_subject_models.py](evaluate_subject_models.py) | 在同一批 LOCKED_TEST 数据上评估 pooled、lyc personal、zyf personal，并输出 subject × model 交叉结果、窗口/ session 汇总和预测文件。 | 手写维护 | 可维护，保留来源与实验边界 |
| [legacy_baseline_v0.py](legacy_baseline_v0.py) | 旧版 pooled sklearn baseline 的训练、验证和冻结；负责把历史候选数据变成 `pipeline.joblib` 及配套 manifest、split、指标和预测表。 | 手写维护 | 可维护，保留来源与实验边界 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [subject_model_utils.py](subject_model_utils.py) | 严格解析文件名；pooled/personal用240维、mixed用60维；单文件和前后比较只做预测。 | 手写维护 | 可维护，保留来源与实验边界 |
| [train_cross_source_models.py](train_cross_source_models.py) | 用共享流水线训练 author-only-7ch、author-common6、our-common6/common7 和 mixed-common6/common7；训练侧只使用历史数据，按 recording/session 分组。 | 手写维护 | 可维护，保留来源与实验边界 |
| [train_subject_models.py](train_subject_models.py) | 从明确身份的历史训练候选中分别训练 `lyc`、`zyf` personal model；以 EDF/session 为最小划分单位，拒绝 `zqd`、未知身份和 LOCKED_TEST。 | 手写维护 | 可维护，保留来源与实验边界 |
| [validate_legacy_manifest.py](validate_legacy_manifest.py) | 验证历史 manifest、39 个 EDF 的身份/标签/时间/分组/边界/文件头/SHA-256 等完整性。 | 手写维护 | 可维护，保留来源与实验边界 |
| [validate_locked_data.py](validate_locked_data.py) | 验证锁定数据的 manifest、标签、时长、采样率、配套文件和哈希。 | 手写维护 | 可维护，保留来源与实验边界 |
| [validate_reproduction_models.py](validate_reproduction_models.py) | 验证上游深度学习复现实验的 10 个权重文件完整性；不表示这些模型用于当前 personal/locked 结论。 | 手写维护 | 可维护，保留来源与实验边界 |
| [verify_common6_compatibility.py](verify_common6_compatibility.py) | 本阶段的配套记录；用途结合生成脚本和原报告核查。 | 手写维护 | 可维护，保留来源与实验边界 |
| [validate_quick_test.py](validate_quick_test.py) | 阻断fit/fit_transform后，以真实EDF和合成边界案例验证两套特征、A/B与身份规则。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

旧入口已冻结为 historical。CURRENT 只有数据 validator；尚无新范式训练/评估脚本和产物。

## 我什么时候需要看这个目录

新数据登记后先运行 validate_new_paradigm_data.py；追溯旧现场推理才看 subject_model_utils.py。

## 不要误解

现有 train_* 脚本都是历史训练入口，不得用于首轮 New Paradigm v1。只读验收不是训练。

## 本轮只读验收

```powershell
python scripts/validate_new_paradigm_data.py
python scripts/validate_historical_integrity.py
python scripts/validate_markdown_links.py
python scripts/validate_legacy_manifest.py
python scripts/validate_locked_data.py
python scripts/validate_reproduction_models.py
python scripts/validate_quick_test.py
```

历史train_*入口仅供追溯，本轮不运行。所有信号预处理与特征实现仍在eeg_pipeline_utils.py，COMMON6映射复用cross_source_utils.py。
