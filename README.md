# EEG Attention Reproduction

本仓库用于复现并改进 EEG 专注度识别系统。当前正式目标是区分 `focus`（专注）与 `unfocus`（不专注）；`rest`（静息态）保留作基线或质量检查，不并入不专注类别。

## 当前进度

- 最新简报：[`2026-09-14｜Personal diagnosis、author-only 与 common6 对比`](docs/progress/EEG项目推进简报_2026-09-14.md)
- 历史简报索引：[`docs/progress/`](docs/progress/README.md)

当前状态：`better_train` 分支已完成 `legacy_baseline_v0` 的 Legacy-only 冻结，并在冻结 pipeline 下完成 2026-09-07 的独立 `LOCKED_TEST FIRST RUN`。上一阶段新增 lyc/zyf subject-dependent personal model；本阶段完成 personal 诊断、author-only-7ch，并在权威 ACNS/Wearable Sensing 证据解除 T5/T6 命名阻塞后完成 author-common6、our-common6、mixed-common6。Personal 诊断显示 `lyc personal → zyf` 的高 accuracy 来自明显类别偏置，历史 held-out 高于 LOCKED_TEST，支持 session/domain shift 嫌疑。Author-only-7ch GroupKFold balanced accuracy 为 `64.12% ± 4.37%`，author-common6 为 `64.69% ± 4.29%`。Common6 结果见 [`artifacts/cross_source_comparison/2026-09-14/`](artifacts/cross_source_comparison/2026-09-14/)。

## 当前数据入口

- 正式清单：`data/session_manifest.csv`
- Legacy baseline 候选清单：`data/legacy_manifest.csv`
- 数据规范：`data/DATA_PROTOCOL.md`
- 新标准录制：`data/locked/YYYY-MM-DD/`
- 只读验收：`scripts/validate_locked_data.py`

新数据必须一段只对应一种状态，不依赖 marker。正式样本统一使用 4 秒窗口、2 秒步长，并在每段录制首尾默认各留 30 秒操作缓冲。训练/测试必须先按完整 session 或被试划分，再切窗口。

运行验收：

```powershell
python scripts/validate_locked_data.py
python scripts/validate_legacy_manifest.py
```

验收脚本只读取 EDF 文件头和哈希，不修改数据，也不依赖 MNE。

## 仓库文件总览

完整的递归文件说明见 [`docs/REPOSITORY_FILE_GUIDE.md`](docs/REPOSITORY_FILE_GUIDE.md)。每个主要内容目录均有自己的 README，负责说明本目录直接文件；不要把 `artifacts/` 中的历史缓存、上游结果或冻结模型误当作当前训练入口。

## 目录说明

| 目录 | 内容 |
|---|---|
| `data/locked/` | 不可用于训练或调参的锁定数据 |
| `data/legacy/` | 旧自采数据，仅用于历史追溯 |
| `data/reference/` | 上游论文 MATLAB 数据 |
| `artifacts/upstream_author/` | 原作者仓库早期版本中已有的结果表 |
| `artifacts/legacy/` | 我们早期探索 notebook 的历史产物 |
| `artifacts/reproductions/` | 我们运行/改造上游流程生成的数组、缓存、权重和结果 |
| `notebooks/` | 上游复现、历史实验和中文教程，分目录归档 |
| `scripts/` | 验收入口；旧训练辅助脚本位于 `scripts/legacy/` |
| `system/` | 系统原型代码 |
| `docs/` | 推进简报和说明图片 |

旧 notebook 中的随机窗口评估仅用于确认流程是否运行，不能作为跨 session 或跨被试的泛化结果。

## 上游参考

1. Wang, J.; Kim, S.-K. *Novel Machine Learning-Based Brain Attention Detection Systems*. Information 2025, 16, 25.
2. Aci, C.I.; Kaya, M.; Mishchenko, Y. *Distinguishing mental attention states of humans via an EEG-based passive BCI using machine learning methods*. Expert Systems with Applications 2019, 134, 153–166.

## Common6 当前状态

ACNS 与 Wearable Sensing 权威证据确认当前 DSI-24 数据的 nomenclature equivalence：`T5-Pz → P7-Pz`、`T6-Pz → P8-Pz`；Our EDF/DSI-Streamer reference 为 `Pz (confirmed)`，author MAT reference 仍为 `unknown`。因此 common6 已建立并完成三个模型，但跨来源结果统一标记为 exploratory / channel-aligned / reference compatibility uncertain。历史阻塞判断保留在 [`artifacts/common6_compatibility/2026-09-14/`](artifacts/common6_compatibility/2026-09-14/)。
