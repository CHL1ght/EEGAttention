# 仓库文件路径查询手册

- 不知道项目为什么发展到这里 → [EXPERIMENT_MAP.md](EXPERIMENT_MAP.md)。
- 不知道某个模型是什么 → [MODEL_CATALOG.md](MODEL_CATALOG.md)。
- 不知道某个文件路径干什么 → 查本文件及对应目录README。

本页按目录查路径，项目故事由实验地图负责。每个目录README都包含阶段、输入、生成者、文件字典、状态和使用场景；术语第一次阅读可查模型字典。

## 2. 根目录

| 文件 | 作用 |
|---|---|
| `.gitignore` | 忽略本地环境、Python 缓存和不应提交的临时文件。 |
| `README.md` | 面向使用者的项目入口、当前状态、目录导航和常用命令。 |
| `docs/REPOSITORY_FILE_GUIDE.md` | 本文档；递归解释仓库文件和目录之间的关系。 |

## 3. `data/`

| 文件/目录 | 作用 |
|---|---|
| `README.md` | 数据入口、清单优先级、原始文件保护规则。 |
| `DATA_PROTOCOL.md` | 正式数据协议：标签、活动区间、窗口、session 划分和 LOCKED_TEST 规则。 |
| `legacy_manifest.csv` | `legacy_dataset_v0` 的唯一旧数据清单；包括 subject、逻辑片段、标签、session group、用途、路径和 SHA-256。 |
| `legacy_manifest_dictionary.md` | `legacy_manifest.csv` 每一列的允许值和含义。 |
| `session_manifest.csv` | 正式 session 清单；当前记录 2026-09-07 的 locked/reference 数据。 |
| `recording_notes_template_simplified.md` | 新采集 session 的现场记录模板，不改变 manifest schema。 |
| `legacy/` | 旧自采 EDF、CSV、DSI 原始文件；只按 legacy manifest 使用。 |
| `locked/` | 受保护的新标准录制；当前正式测试集和后续采集计划。 |
| `reference/original_mat/` | 上游论文/原始项目的MATLAB参考数据；同时是author-only/common6与mixed的作者训练来源。 |

### `data/legacy/`

- `mixed_20min/`：固定顺序的约 20 分钟 EDF。标签边界不从文件名猜，而从 `legacy_manifest.csv` 的 `activity_start_s`、`activity_end_s`、`canonical_label` 读取；同一 EDF 的片段共享一个 session group。
- `multiclass_10min/`：旧单状态记录。无 subject 前缀的文件由数据负责人确认属于 lyc；`focus` 保留为 focus，`iu/ou` 合并为 unfocus，`daze` 不进入二分类。
- 每个 `.csv` 是设备导出的配套时序表，每个 `.dsi` 是采集软件配套文件；当前正式 MNE 管线以 EDF 为信号入口，CSV/DSI 用于追溯和质量核验。

### `data/locked/`

- `2026-09-07/`：3 个 lyc 正式二分类 session、3 个 zyf 正式二分类 session，以及 1 个 lyc rest reference；每个 EDF 配有 CSV/DSI（若存在）。
- `2026-09-14/recording_plan.md`：下一轮采集计划，不是 EEG 数据，也不进入模型。

## 4. `scripts/`

| 文件 | 作用 |
|---|---|
| `eeg_pipeline_utils.py` | 唯一共享信号处理实现：EDF 读取、EEG 通道选择、重采样、FIR、窗口、Welch 频带特征、JSON/CSV/哈希工具。 |
| `legacy_baseline_v0.py` | 训练并冻结旧 pooled baseline；只接受 legacy candidate，按完整 `session_group_id` 划分 train/validation。 |
| `evaluate_locked_test.py` | 加载旧冻结 pooled pipeline，在 LOCKED_TEST 上只预测，不 fit。 |
| `train_subject_models.py` | 从历史 legacy candidate 分别训练 lyc/zyf personal pipeline；zqd 和 locked 数据被排除。 |
| `evaluate_subject_models.py` | 在同一 LOCKED_TEST 上评估 pooled、lyc personal、zyf personal，并输出交叉矩阵。 |
| `cross_source_utils.py` | MAT/EDF 输入 adapter、common6/common7 明确通道映射、author block manifest 和共享特征数据集入口。 |
| `diagnose_subject_models.py` | Personal model 类别分布、预测偏置、session 级结果、历史 LOGO、PCA 和通道诊断。 |
| `train_cross_source_models.py` | author-only-7ch、author-common6、our-common6/common7、mixed-common6/common7 训练入口；所有训练以 recording/session 为组。 |
| `evaluate_cross_source_models.py` | common6/common7 统一 pooled/personal/author/mixed 比较入口，输出逐窗口和逐 session 结果。 |
| `subject_model_utils.py` | 严格解析文件名；单EDF和前后比较的共享推理helper，按240/60维分别提取特征。 |
| `validate_legacy_manifest.py` | 验证 legacy manifest、EDF 头、路径、片段、身份和哈希。 |
| `validate_locked_data.py` | 验证 locked manifest、EDF 头、时长、窗口数、配套文件和哈希。 |
| `validate_reproduction_models.py` | 仅检查上游复现深度模型权重的完整性。 |
| `README.md` | 脚本入口和当前正式/历史脚本边界。 |
| `annotated/` | 带中文注释的阅读版脚本，不是独立实现入口。 |
| `legacy/` | 旧深度学习 worker 和 ROC 辅助，仅用于复现历史实验。 |

## 5. `notebooks/`

| 目录/文件 | 作用 |
|---|---|
| `README.md` | notebook 分类和运行约定。 |
| `lab_quick_test_legacy_model.ipynb` | 现场单EDF及Before/After入口；pooled/personal用240维、mixed-common6用60维；不fit或写artifacts。 |
| `upstream/` | 上游原始 notebook：MAT 检查、训练和结果可视化。 |
| `tutorial/` | 上游 notebook 的中文注释/阅读材料。 |
| `legacy/self_recorded/` | 旧自采三分类、四分类、mixed EDF 和历史对比 notebook。 |

## 6. `artifacts/`

artifacts 是实验产物，不是新的原始数据入口。

| 目录 | 作用 |
|---|---|
| `legacy_baseline_v0/` | 旧 pooled baseline 的冻结 pipeline、配置、split、validation 预测和冻结证明。不得覆盖。 |
| `locked_test/2026-09-07/` | 已完成的旧 pooled LOCKED_TEST 结果；用作回归基线。 |
| `subject_models/` | 本阶段 lyc/zyf personal pipeline、训练范围和排除清单。 |
| `subject_model_comparison/2026-09-07/` | 三个模型在同一 locked session 上的窗口/subject/session 结果。 |
| `subject_model_diagnostics/2026-09-07/` | personal model 的类别偏置、历史 session-held-out、PCA 和 common7 检查。 |
| `author_models/author_only/` | 23 个 author MAT recording 的既有 author-only-7ch pipeline、GroupKFold 验证和 MAT 审计。 |
| `author_models/author_common6/` | 同一 23 个 author recording 的 common6 pipeline；`AF4` 不进入特征。 |
| `our_common7_models/pooled_common7/` | our-common7 训练门禁；当前因缺少 P7/P8/AF4 而 blocked。 |
| `our_common6_models/pooled_common6/` | 只使用 lyc/zyf historical candidate 的 common6 pipeline、训练清单和 GroupKFold 验证。 |
| `mixed_models/our_author_mixed/` | our+author mixed 训练门禁；当前 blocked。 |
| `mixed_models/our_author_mixed_common6/` | author historical 与 lyc/zyf historical 的 common6 mixed pipeline 和验证产物。 |
| `cross_source_comparison/2026-09-07/` | 最终统一模型比较表和跨来源阻塞状态。 |
| `cross_source_comparison/2026-09-14/` | common6 最终比较，包括旧 pooled/personal、author-common6、our-common6、mixed-common6、逐 session、逐窗口和 predicted class ratio。 |
| `legacy/notebook_outputs/` | 旧 notebook 的探索性输出、缓存和检查表，不代表正式泛化指标。 |
| `reproductions/upstream_pipeline/` | 运行/改造上游深度学习流程产生的数组、特征缓存、权重、ROC 数据和训练表。 |
| `upstream_author/` | 原作者仓库原有的结果表，只用于来源追溯。 |
| `README.md` | artifacts 来源和可信边界说明。 |

## 7. `docs/`

| 目录/文件 | 作用 |
|---|---|
| `README.md` | 文档目录导航。 |
| `REPOSITORY_FILE_GUIDE.md` | 本仓库递归文件总览。 |
| `methodology/legacy_baseline_v0.md` | 旧 baseline 的方法、冻结和指标解释。 |
| `progress/` | 按日期的推进简报、模板和历史决策记录。 |
| `assets/upstream_architecture.png` | 上游网络/流程架构图，仅供文档引用。 |

## 8. `system/`

| 文件/目录 | 作用 |
|---|---|
| `README.md` | 说明当前系统原型尚未接入 EEG 管线。 |
| `backend/main.py` | 最小 FastAPI 健康检查路由；当前不读取 EDF、不加载模型。 |

## 9. 修改边界

- 原始 EDF/CSV/DSI/MAT 不就地编辑。
- `artifacts/legacy_baseline_v0/` 和既有 `artifacts/locked_test/` 是冻结/回归产物，不因新实验重写。
- 需要新增实验时，新建有版本或日期的 artifacts 目录，并在相应 README 中登记来源、输入、输出和是否可用于正式结论。

## 10. Common6 兼容性审计

`scripts/verify_common6_compatibility.py` 是 common6 的前置审计。它检查当前 DSIStreamer/EDF 的 `T5-Pz`、`T6-Pz`、Pz sidecar metadata、MNE header 状态，以及作者 MAT/notebook 的 reference/montage provenance，并登记 ACNS/Wearable Sensing 权威证据；当前状态为 `unblocked_for_common6_training`。历史阻塞快照保存在 `HISTORICAL_*` 文件中；审计本身不执行模型 fit 或 LOCKED_TEST 信号预测。


## 11. 现场 LAB_FEEDBACK（Stage 8）

| 路径 | 用途 |
|---|---|
| `data/exploratory/README.md` | 探索数据入口；不是默认训练或最终测试。 |
| `data/exploratory/lab_feedback/README.md` | 反馈实验的命名、metadata、归档与数据晋升规则。 |
| `data/exploratory/lab_feedback/2026-09-14/README.md` | 今天的执行说明；尚无新EDF或metadata。 |
| `data/DATA_PROTOCOL.md` 第7节 | subject、预期标签、时间、feedback轮次、看反馈标志、task、notes、角色和资格的字段字典。 |
| `scripts/subject_model_utils.py` | `run_quick_test()` 和 `compare_quick_tests()`；旧模型不fit，240/60维特征分开。 |
| `scripts/validate_quick_test.py` | 真实EDF dry run、A/B标签差异、未知身份、维数及fit拦截验收；不生成实验分数文件。 |
| `notebooks/lab_quick_test_legacy_model.ipynb` | 填路径、调用helper、显示模型说明和前后指标。 |
| `docs/MODEL_CATALOG.md` | 七种既有模型及输入/用途解释。 |
| `docs/EXPERIMENT_MAP.md` | Stage 0–8的实验发展顺序。 |

`data/locked/2026-09-14/recording_plan.md`仅保留旧计划；今天的feedback数据不照旧计划加入LOCKED_TEST。未来探索结果可另存到独立的lab_feedback结果目录，但本轮不预造数据或结果。
