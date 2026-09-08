# EEG Attention Reproduction

本仓库用于复现并改进 EEG 专注度识别系统。当前正式目标是区分 `focus`（专注）与 `unfocus`（不专注）；`rest`（静息态）保留作基线或质量检查，不并入不专注类别。

## 当前数据入口

- 正式清单：`data/session_manifest.csv`
- 数据规范：`data/DATA_PROTOCOL.md`
- 新标准录制：`data/locked/YYYY-MM-DD/`
- 只读验收：`scripts/validate_locked_data.py`

新数据必须一段只对应一种状态，不依赖 marker。正式样本统一使用 4 秒窗口、2 秒步长，并在每段录制首尾默认各留 30 秒操作缓冲。训练/测试必须先按完整 session 或被试划分，再切窗口。

运行验收：

```powershell
python scripts/validate_locked_data.py
```

验收脚本只读取 EDF 文件头和哈希，不修改数据，也不依赖 MNE。

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
