# 新人文档、现场 QuickTest 与 LAB_FEEDBACK 交付记录

> 状态：`HISTORICAL handoff`。本文保留当时的交付事实和执行时哈希；当前研究入口见 [New Paradigm v1](current/NEW_PARADIGM_V1.md)。2026-09-14 数据现归档为 historical pilot，CURRENT 结构整理前快照由 Git tag `pre-new-paradigm-v1` 指向提交 `f12359d`。

本轮只整理文档、扩展固定模型推理和定义反馈数据规则。没有训练、调参、修改正式实验分数或伪造新录制。

## 1. 开始时的 Git 状态

- 分支：better_train。
- 开始时 git status --short 为空。
- 本地 HEAD、origin/better_train 和实时 git ls-remote origin refs/heads/better_train 均为 `6a0c93ce12e7c070ffe40886a875b6167ca3e70d`。
- 没有 reset、pull、提交或推送。本次修改保留在工作区。

## 2. 新人阅读入口

根 [README](../README.md) 从“30秒看懂”开始，按为什么做、数据、结论、脚本和产物串起路线。
[实验阶段地图](EXPERIMENT_MAP.md) 讲故事；[模型字典](MODEL_CATALOG.md) 解释模型；
[路径指南](REPOSITORY_FILE_GUIDE.md) 查具体文件。Stage 8 是现场探索，未来新 final holdout 才是预先规定、不看反馈的独立最终评估。

## 3. README 模板落地

原有66份README全部更新，新建3份探索目录README，共69份；根README按用户要求采用入口布局，
其余68份使用“是什么／哪一步／为什么／输入／生成者／文件表／状态／使用场景／不要误解”的统一结构。
文件表解释本目录直接文件与子目录入口；历史缓存、教学副本、来源结果与正式模型区分说明。
旧common7阻塞和历史审计原文不改写，README指出后续COMMON6状态。

## 4. 七个模型，用普通话解释

| 模型 | 一句话 | 当前输入特征 |
|---|---|---|
| Existing pooled frozen | 最早冻结的多人通用基线；原历史训练范围含zqd，不能把后来的排除规则倒写进历史。 | 24通道×10=240维 |
| lyc personal | 只学习lyc历史录制的个人模型。 | 240维 |
| zyf personal | 只学习zyf历史录制的个人模型。 | 240维 |
| author-only-7ch | 只学习作者23个MAT录制，保留作者原来的7个通道。 | 70维 |
| author-common6 | 仍只学习作者数据，但去掉AF4，以便与我们使用相同6通道。 | 60维 |
| our-common6 | 只学习lyc/zyf历史数据的6通道通用模型，是mixed的直接对照。 | 60维 |
| mixed-common6 | 把lyc/zyf历史录制和作者23个录制合起来学习，不是校准或个人微调。 | 60维 |

上述模型均已存在，本轮没有重新训练。共同六通道顺序为F7,F3,P7,O1,O2,P8；
DSI输入的T5-Pz/T6-Pz按已确认的命名等价关系对应P7/P8。

## 5. QuickTest 修改与使用

修改原 [notebook](../notebooks/lab_quick_test_legacy_model.ipynb) 和共享
[subject_model_utils.py](../scripts/subject_model_utils.py)；新增只读
[validate_quick_test.py](../scripts/validate_quick_test.py)。

Notebook只填路径、调用和显示。完整通道走既有eeg_pipeline_utils，COMMON6通过既有cross_source_utils适配，
两路复用同一个预处理与特征函数；窗口必须一一对齐。mixed加载时核对模型hash、模型类型、通道顺序和60维协议，
不把240维矩阵送入mixed。默认不加载author-common6或our-common6。

- 单EDF：`run_quick_test(EDF_PATH)`。显示文件名、subject、预期标签、时长、窗口数和六列表格；逐窗口预测与类别数量仍在返回对象中。
- 前后比较：`compare_quick_tests(EDF_PATH_BEFORE, EDF_PATH_AFTER)`。同一已知受试者、同一二分类标签且不是同一个路径时显示差值，以百分点表达。
- 标签不同、身份不同/未知、重复文件不算改善Δ；时长不同明确提示不是逐窗口配对。
- zqd或未知身份：只跑pooled与mixed，personal明确skipped，不猜测受试者。
- 文件名标签只在预测后用于计分。单标签Accuracy与目标类别比例是同一个数，不能当两项独立证据。
- 当前按全EDF计算，未套用正式测试manifest的首尾缓冲；因此dry run分数不覆盖正式指标。
- mixed输出始终标记 exploratory / channel-aligned but reference compatibility uncertain；Our reference=Pz，author reference未知。

## 6. 实际验收与 inference-only

以下四个真实已有EDF完成了只读推理，既有文件未复制、重命名或伪装成今天的新数据：

- [lyc focus第一段](../data/locked/2026-09-07/lyc_focus1_20260907.edf)
- [lyc focus第二段](../data/locked/2026-09-07/lyc_focus_202609072034_raw.edf)
- [lyc unfocus](../data/locked/2026-09-07/lyc_unfocus1_20260907.edf)
- [zyf focus](../data/locked/2026-09-07/zyf_focus1_20260907.edf)

单EDF、相同标签A/B、不同标签/受试者/重复文件保护、feedback0/1/2解析均通过。
zqd/未知身份检查复用真实特征与保存模型，覆盖文件名身份解析而不生成虚假EDF。
Notebook默认空路径单元格可以安全执行。

验证用运行时拦截器禁止Pipeline、StandardScaler、PCA、SVC的fit/fit_transform/partial_fit，
调用计数全部为0；同时禁止joblib.dump。模型和测试原始数据hash保持一致。
没有calibration、阈值优化、模型选择或任何新模型写出；QuickTest结果只保存在内存。

实际运行环境出现scikit-learn版本提示：模型保存版本1.9.1，当前环境1.9.0。
本环境下验收通过，但不保证跨版本数值完全一致；本轮没有安装包、重训或重新保存模型。

## 7. LAB_FEEDBACK 归档与 metadata

目录：[data/exploratory/lab_feedback/2026-09-14/](../data/exploratory/lab_feedback/2026-09-14/README.md)。
目前只有README，没有伪造EDF/CSV/DSI或metadata记录。

命名示例：

- `lyc_focus_202609141630_feedback0.edf`
- `lyc_focus_202609141650_feedback1.edf`
- 后续轮次使用feedback2等；同次EDF/CSV/DSI保持同一stem，保留原始信号与命名来源。

必填metadata：subject_id、intended_label、timestamp、feedback_round、
feedback_seen_before_recording、task、notes、dataset_role=lab_feedback、
eligible_for_training=false、eligible_for_final_test=false。
另建议pair_id、原始文件名、各文件路径和SHA-256，具体以
[DATA_PROTOCOL](../data/DATA_PROTOCOL.md)为准。

feedback0在本轮反馈前，feedback_seen_before_recording=false；feedback1+为true。
实际历史不符时必须如实登记，不能只靠后缀反推事实。
包括feedback0在内，整轮数据均为exploratory，不默认加入legacy训练清单，不加入LOCKED_TEST或final holdout。
以后如需用于训练，必须另有明确晋升决定与provenance；看过反馈的数据不能变成“从未见过”的最终测试。

旧[2026-09-14 recording_plan](../data/locked/2026-09-14/recording_plan.md)仅在顶部追加当前归档指引，原计划保留。
这是文档修改，不是修改已锁定的信号、标签、清单或测试区间。

## 8. 验证与保护结果

- validate_legacy_manifest.py：通过，48行、39个唯一EDF、43个candidate片段，0错误。
- validate_locked_data.py：通过，7个session、6个正式ready测试、2389个窗口，0错误。
- validate_reproduction_models.py：10份历史深度权重检查通过，0错误。
- validate_quick_test.py：上述实际推理、特征隔离、A/B和零fit检查通过。
- Markdown相对链接与README阶段入口检查通过；Git diff --check通过。
- Git出现LF→CRLF提示是现有换行配置提示，不是diff-check空白错误。
- 开始时记录的233个artifacts/与data/locked/非README文件中，232个hash完全不变；
  唯一变化是上面明确说明的recording_plan.md文档指引。所有模型、旧正式报告/结果与已有locked信号不变。
- legacy_manifest.csv、session_manifest.csv及原始数据没有修改；没有删除或移动文件。

### 模型 SHA-256：与开始时一致

| 模型文件 | SHA-256 |
|---|---|
| [artifacts/author_models/author_common6/pipeline.joblib](../artifacts/author_models/author_common6/pipeline.joblib) | `85987c2ec5cd13d72279696a166b4fc9da84460909264b1679b96f37799f5974` |
| [artifacts/author_models/author_only/pipeline.joblib](../artifacts/author_models/author_only/pipeline.joblib) | `80f7cb46aa1cd98bf04f4e20f8b9f54199cd0c623b9ea7b82afa480590b9f244` |
| [artifacts/legacy_baseline_v0/pipeline.joblib](../artifacts/legacy_baseline_v0/pipeline.joblib) | `2c67ed005d3821f712771d3412bcad0a5b67a2638e89393d1d505460635488cc` |
| [artifacts/mixed_models/our_author_mixed_common6/pipeline.joblib](../artifacts/mixed_models/our_author_mixed_common6/pipeline.joblib) | `5f171c20e61b7ad827d08494f283fa6612d3eabbddb012b8389699a392881db8` |
| [artifacts/our_common6_models/pooled_common6/pipeline.joblib](../artifacts/our_common6_models/pooled_common6/pipeline.joblib) | `bf8e20d43ab7927cdf28bba6501b835e212fcf37fb7e7c1bdbc5cb2dd761dbb6` |
| [artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_anova.pth](../artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_anova.pth) | `d69826df92831c67dd11af1e58a1d8a8ff625662877078e31f854051773a4397` |
| [artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_fi.pth](../artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_fi.pth) | `b4f6c31ca537bf7fb41e6e9dc5a14ebb2f9a6095dac25cb529af24fcf7bbf88d` |
| [artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_lcc.pth](../artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_lcc.pth) | `808bef8e57ed1a5b0afd867eabd052c5eaac8a7c4cf71a8f8e9a3666b847b50d` |
| [artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_pca.pth](../artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win_pca.pth) | `bee3646f07baa4ccb007147cacaefc114f729cf438f6b8557de7388c38302289` |
| [artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win.pth](../artifacts/reproductions/upstream_pipeline/models/googlenet_model_part_detrend_plr_stft_bin_win.pth) | `7fa0a39651cc1226bfb74e0f02eb13cd3b58337eafefc214aaaecbab311f6cc2` |
| [artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_anova.pth](../artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_anova.pth) | `59c6ddb4a18065b5d5b833bde647c5f3714cc42be8e57fa6c8abd91e7085cc61` |
| [artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_fi.pth](../artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_fi.pth) | `a089788b3370bf355ed3c57c09025590b9153e362d98ba413b2ad99bf9a07dcf` |
| [artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_lcc.pth](../artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_lcc.pth) | `9531e16c28af5517b7af9b1f44ca1da39b259d79b706d7a9b4c7b8ee9c4e4636` |
| [artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_pca.pth](../artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win_pca.pth) | `5ac0a8b1635ae9f089e86ff08931a93db6beac60761adc24e7e2084e75d35b97` |
| [artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win.pth](../artifacts/reproductions/upstream_pipeline/models/resnet18_model_part_detrend_plr_stft_bin_win.pth) | `6ed6f7ab85f41a6d30c8d2a7bbd658594d87e3d43beb9369a71158607c1365c6` |
| [artifacts/subject_models/lyc/pipeline.joblib](../artifacts/subject_models/lyc/pipeline.joblib) | `7270a2dbf0f04f490b48dc52db4eb694df698d2b1636234abd65534505a9c0fa` |
| [artifacts/subject_models/zyf/pipeline.joblib](../artifacts/subject_models/zyf/pipeline.joblib) | `5343939b19d0bfde7aa2ff8915c43bf8be8169d020b48932f586bcb93d690ff4` |

## 9. 最终修改文件清单

共78个文件：71个已跟踪文件修改、7个新文件。此表覆盖本轮所有文件，不含Python自动忽略的缓存。
全部属于用户要求的文档、QuickTest或数据规则范围；无旧模型、信号或正式指标文件变更。

| 状态 | 文件 |
|---|---|
| 修改 | [README.md](../README.md) |
| 修改 | [artifacts/README.md](../artifacts/README.md) |
| 修改 | [artifacts/author_models/README.md](../artifacts/author_models/README.md) |
| 修改 | [artifacts/author_models/author_common6/README.md](../artifacts/author_models/author_common6/README.md) |
| 修改 | [artifacts/author_models/author_only/README.md](../artifacts/author_models/author_only/README.md) |
| 修改 | [artifacts/common6_compatibility/2026-09-14/README.md](../artifacts/common6_compatibility/2026-09-14/README.md) |
| 修改 | [artifacts/common6_compatibility/README.md](../artifacts/common6_compatibility/README.md) |
| 修改 | [artifacts/cross_source_comparison/2026-09-07/README.md](../artifacts/cross_source_comparison/2026-09-07/README.md) |
| 修改 | [artifacts/cross_source_comparison/2026-09-14/README.md](../artifacts/cross_source_comparison/2026-09-14/README.md) |
| 修改 | [artifacts/cross_source_comparison/README.md](../artifacts/cross_source_comparison/README.md) |
| 修改 | [artifacts/legacy/README.md](../artifacts/legacy/README.md) |
| 修改 | [artifacts/legacy/notebook_outputs/README.md](../artifacts/legacy/notebook_outputs/README.md) |
| 修改 | [artifacts/legacy/notebook_outputs/comparisons/README.md](../artifacts/legacy/notebook_outputs/comparisons/README.md) |
| 修改 | [artifacts/legacy/notebook_outputs/mixed_20min/README.md](../artifacts/legacy/notebook_outputs/mixed_20min/README.md) |
| 修改 | [artifacts/legacy/notebook_outputs/multiclass_10min/README.md](../artifacts/legacy/notebook_outputs/multiclass_10min/README.md) |
| 修改 | [artifacts/legacy/notebook_outputs/reference_inspection/README.md](../artifacts/legacy/notebook_outputs/reference_inspection/README.md) |
| 修改 | [artifacts/legacy_baseline_v0/README.md](../artifacts/legacy_baseline_v0/README.md) |
| 修改 | [artifacts/locked_test/2026-09-07/README.md](../artifacts/locked_test/2026-09-07/README.md) |
| 修改 | [artifacts/locked_test/README.md](../artifacts/locked_test/README.md) |
| 修改 | [artifacts/mixed_models/README.md](../artifacts/mixed_models/README.md) |
| 修改 | [artifacts/mixed_models/our_author_mixed/README.md](../artifacts/mixed_models/our_author_mixed/README.md) |
| 修改 | [artifacts/mixed_models/our_author_mixed_common6/README.md](../artifacts/mixed_models/our_author_mixed_common6/README.md) |
| 修改 | [artifacts/our_common6_models/README.md](../artifacts/our_common6_models/README.md) |
| 修改 | [artifacts/our_common6_models/pooled_common6/README.md](../artifacts/our_common6_models/pooled_common6/README.md) |
| 修改 | [artifacts/our_common7_models/README.md](../artifacts/our_common7_models/README.md) |
| 修改 | [artifacts/our_common7_models/pooled_common7/README.md](../artifacts/our_common7_models/pooled_common7/README.md) |
| 修改 | [artifacts/reproductions/README.md](../artifacts/reproductions/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/README.md](../artifacts/reproductions/upstream_pipeline/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/feature_cache/README.md](../artifacts/reproductions/upstream_pipeline/feature_cache/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/models/README.md](../artifacts/reproductions/upstream_pipeline/models/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/preprocessed_arrays/README.md](../artifacts/reproductions/upstream_pipeline/preprocessed_arrays/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/results/README.md](../artifacts/reproductions/upstream_pipeline/results/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/results/progress/README.md](../artifacts/reproductions/upstream_pipeline/results/progress/README.md) |
| 修改 | [artifacts/reproductions/upstream_pipeline/results/roc_artifacts/README.md](../artifacts/reproductions/upstream_pipeline/results/roc_artifacts/README.md) |
| 修改 | [artifacts/subject_model_comparison/2026-09-07/README.md](../artifacts/subject_model_comparison/2026-09-07/README.md) |
| 修改 | [artifacts/subject_model_comparison/README.md](../artifacts/subject_model_comparison/README.md) |
| 修改 | [artifacts/subject_model_diagnostics/2026-09-07/README.md](../artifacts/subject_model_diagnostics/2026-09-07/README.md) |
| 修改 | [artifacts/subject_model_diagnostics/README.md](../artifacts/subject_model_diagnostics/README.md) |
| 修改 | [artifacts/subject_models/README.md](../artifacts/subject_models/README.md) |
| 修改 | [artifacts/subject_models/lyc/README.md](../artifacts/subject_models/lyc/README.md) |
| 修改 | [artifacts/subject_models/zyf/README.md](../artifacts/subject_models/zyf/README.md) |
| 修改 | [artifacts/upstream_author/README.md](../artifacts/upstream_author/README.md) |
| 修改 | [artifacts/upstream_author/results/README.md](../artifacts/upstream_author/results/README.md) |
| 修改 | [data/DATA_PROTOCOL.md](../data/DATA_PROTOCOL.md) |
| 修改 | [data/README.md](../data/README.md) |
| 新增 | [data/exploratory/README.md](../data/exploratory/README.md) |
| 新增 | [data/exploratory/lab_feedback/2026-09-14/README.md](../data/exploratory/lab_feedback/2026-09-14/README.md) |
| 新增 | [data/exploratory/lab_feedback/README.md](../data/exploratory/lab_feedback/README.md) |
| 修改 | [data/legacy/README.md](../data/legacy/README.md) |
| 修改 | [data/legacy/mixed_20min/README.md](../data/legacy/mixed_20min/README.md) |
| 修改 | [data/legacy/multiclass_10min/README.md](../data/legacy/multiclass_10min/README.md) |
| 修改 | [data/locked/2026-09-07/README.md](../data/locked/2026-09-07/README.md) |
| 修改 | [data/locked/2026-09-14/README.md](../data/locked/2026-09-14/README.md) |
| 修改 | [data/locked/2026-09-14/recording_plan.md](../data/locked/2026-09-14/recording_plan.md) |
| 修改 | [data/locked/README.md](../data/locked/README.md) |
| 修改 | [data/reference/README.md](../data/reference/README.md) |
| 修改 | [data/reference/original_mat/README.md](../data/reference/original_mat/README.md) |
| 新增 | [docs/EXPERIMENT_MAP.md](EXPERIMENT_MAP.md) |
| 新增 | [docs/LAB_FEEDBACK_HANDOFF.md](LAB_FEEDBACK_HANDOFF.md) |
| 新增 | [docs/MODEL_CATALOG.md](MODEL_CATALOG.md) |
| 修改 | [docs/README.md](README.md) |
| 修改 | [docs/REPOSITORY_FILE_GUIDE.md](REPOSITORY_FILE_GUIDE.md) |
| 修改 | [docs/assets/README.md](assets/README.md) |
| 修改 | [docs/methodology/README.md](methodology/README.md) |
| 修改 | [docs/progress/README.md](progress/README.md) |
| 修改 | [notebooks/README.md](../notebooks/README.md) |
| 修改 | [notebooks/lab_quick_test_legacy_model.ipynb](../notebooks/lab_quick_test_legacy_model.ipynb) |
| 修改 | [notebooks/legacy/README.md](../notebooks/legacy/README.md) |
| 修改 | [notebooks/legacy/self_recorded/README.md](../notebooks/legacy/self_recorded/README.md) |
| 修改 | [notebooks/tutorial/README.md](../notebooks/tutorial/README.md) |
| 修改 | [notebooks/upstream/README.md](../notebooks/upstream/README.md) |
| 修改 | [scripts/README.md](../scripts/README.md) |
| 修改 | [scripts/annotated/README.md](../scripts/annotated/README.md) |
| 修改 | [scripts/legacy/README.md](../scripts/legacy/README.md) |
| 修改 | [scripts/subject_model_utils.py](../scripts/subject_model_utils.py) |
| 新增 | [scripts/validate_quick_test.py](../scripts/validate_quick_test.py) |
| 修改 | [system/README.md](../system/README.md) |
| 修改 | [system/backend/README.md](../system/backend/README.md) |
