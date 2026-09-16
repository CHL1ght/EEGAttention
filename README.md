# EEGAttention

## CURRENT：New Paradigm v1

当前核心研究构念是 **task engagement / cognitive engagement（任务认知投入状态）**：未来面向工作/学习场景，按时间轴估计用户是否持续、主动地投入当前任务。`focus` / `unfocus` 目前仍是 New Paradigm v1 的实验操作标签，不等于已经验证的普适 engagement 真值；当前 `focus` 也不得直接解释为 flow。行为正确率、反应时间和完成量可作为未来 external validation，但不是唯一标签定义。

当前状态：`data/current/new_paradigm_v1/session_manifest.csv` 已登记 2026-09-16 的 lyc focus ×3、unfocus ×3 和 observe control ×1。首次单日 6-session LOSO 达到 session 6/6、window accuracy 98.07%，但录制顺序为 `F-F-F → U-U-U`，标签与时间/顺序完全混杂；这是很强的**单日 exploratory** 结果，不能解释为跨日 attention 或 engagement 泛化。下一阶段首要任务不是调参或继续刷准确率，而是系统控制混杂因素、使用 frozen model 做跨日 prediction-only，并开展 task engagement 构念验证。

- 当前数据入口：[data/current/new_paradigm_v1/](data/current/new_paradigm_v1/README.md)
- 当前协议：[DATA_PROTOCOL_V2.md](docs/current/DATA_PROTOCOL_V2.md)
- 当前研究计划：[NEW_PARADIGM_V1.md](docs/current/NEW_PARADIGM_V1.md)
- 控制实验路线：[ENGAGEMENT_CONTROL_ROADMAP.md](docs/current/ENGAGEMENT_CONTROL_ROADMAP.md)
- 当前产物入口：[artifacts/current/new_paradigm_v1/](artifacts/current/new_paradigm_v1/README.md)

## HISTORICAL：已冻结实验

旧 pooled、personal、author、common6 和 2026-09-14 LAB_FEEDBACK 均为可追溯历史证据，不是 New Paradigm v1 的默认训练输入。为避免破坏脚本、报告与哈希链，旧数据和产物保留原物理路径，由 [data/historical/](data/historical/README.md) 与 [artifacts/historical/](artifacts/historical/README.md) 提供逻辑索引。

| 阶段 | 状态 | 主要位置 |
|---|---|---|
| Stage 0–1：作者参考与早期自采探索 | historical / reference | `data/reference/`、`data/legacy/` |
| Stage 2：Existing pooled frozen | historical baseline | `artifacts/legacy_baseline_v0/` |
| Stage 3：LOCKED_TEST v1 | historical locked evaluation | `data/locked/`、`artifacts/locked_test/` |
| Stage 4–5：lyc/zyf personal 与诊断 | historical baseline | `artifacts/subject_models/`、`artifacts/subject_model_diagnostics/` |
| Stage 6–7：author/common6/mixed | historical baseline | `artifacts/author_models/`、`artifacts/our_common6_models/`、`artifacts/mixed_models/` |
| Stage 8：2026-09-14 LAB_FEEDBACK | historical pilot / transition dataset | `data/exploratory/lab_feedback/2026-09-14/`、`artifacts/lab_feedback/2026-09-14/` |
| Stage 9：New Paradigm v1 | **CURRENT** | `data/current/new_paradigm_v1/`、`docs/current/` |

Stage 8 已完成 11 条 EDF 的归档和 prediction-only 三模型分析。它揭示了明显的 session 波动与标签来源问题，但反馈轮次无法可靠确认，因此不能解释为 feedback improvement，也不能晋升为训练、验证或最终测试数据。所有 11 条固定为 `dataset_role=historical_pilot`，训练/验证/final eligibility 均为 `false`。

## 研究边界

- New Paradigm v1 首轮训练只允许使用其 manifest 中明确登记且符合协议的 `new_paradigm_v1` session。
- legacy、author、2026-09-14 LAB_FEEDBACK、旧 LOCKED_TEST 和 common6 数据不得默认混入新模型；未来若做迁移/合并，必须作为单独 ablation 并留下新版本记录。
- 划分单位是完整 session；推荐 leave-one-day-out，最终留出在预测前冻结。
- 不做全部混杂变量的全因子组合；按 control ladder 一次优先检验一个最大混杂，其余条件尽量固定。
- 原始 EDF/CSV/DSI/notes 不就地修改或重命名；标签来源和冲突必须显式登记。
- 历史模型与历史报告保留用于比较，不代表当前最佳模型或最终结论。
- 下一系统开发方向是 **Attention Dashboard**，用于未来展示 engagement 状态时间轴；它不改变当前证据边界。

## 导航

- 实验为什么一步步发展到这里：[EXPERIMENT_MAP.md](docs/EXPERIMENT_MAP.md)
- 七个历史模型和三个未来模型：[MODEL_CATALOG.md](docs/MODEL_CATALOG.md)
- 仓库路径用途：[REPOSITORY_FILE_GUIDE.md](docs/REPOSITORY_FILE_GUIDE.md)
- 2026-09-14 pilot 清单：[LAB_FEEDBACK README](data/exploratory/lab_feedback/2026-09-14/README.md)
- 历史进度记录：[docs/progress/](docs/progress/README.md)
- 2026-09-16 阶段简报：[EEG项目推进简报_2026-09-16.md](docs/progress/EEG项目推进简报_2026-09-16.md)

## 只读验收

```powershell
python scripts/validate_new_paradigm_data.py
python scripts/validate_historical_integrity.py
python scripts/validate_markdown_links.py
python scripts/validate_legacy_manifest.py
python scripts/validate_locked_data.py
python scripts/validate_reproduction_models.py
python scripts/validate_quick_test.py
git diff --check
```

`train_*` 与其他会调用 fit 的历史入口只用于来源追溯，不属于当前验收。当前本机 EEG 环境可使用 `C:\CHLight\1-Workconfig\Miniconda\envs\EEG\python.exe`。

## 上游参考

Wang, J.; Kim, S.-K. *Novel Machine Learning-Based Brain Attention Detection Systems*. Information 2025, 16, 25。

Aci, C.I.; Kaya, M.; Mishchenko, Y. *Distinguishing mental attention states of humans via an EEG-based passive BCI using machine learning methods*. Expert Systems with Applications 2019, 134, 153–166。
