# Notebook 导航

这些 notebook 都是历史复现或探索记录，不是下一阶段正式训练入口。正式管线将放在可测试的 Python 模块和脚本中。

## 分类

- `upstream/`：论文上游代码、结果可视化及 MATLAB 数据检查。
- `legacy/self_recorded/`：旧自采 3/4 分类、旧 20 分钟切段与域偏移对比实验。
- `tutorial/`：中文注释版本和阅读笔记。
- `lab_quick_test_legacy_model.ipynb`：输入单个 EDF 路径，严格按文件名识别 subject/真值，并复用 pooled frozen model 与适用的 lyc/zyf personal model 做现场快速 inference；zqd/未知 subject 跳过 personal，不训练、不 fit、不写入正式产物。

## 运行约定

从仓库根目录启动 Jupyter 或 VS Code，再运行 notebook；历史 notebook 的数据路径均相对仓库根目录。其输出统一写入 `artifacts/legacy/notebook_outputs/`，不得写回 `data/`。

旧 notebook 可能包含已经执行过的输出。随机窗口指标只用于历史流程核对，不代表跨 session 或跨被试泛化能力。

## 目录和文件说明

| 目录/文件 | 内容 |
|---|---|
| `lab_quick_test_legacy_model.ipynb` | 当前现场快速入口；输入 EDF 后复用共享函数比较 pooled/personal。 |
| `upstream/` | 原始上游训练、MAT 检查和结果可视化 notebook。 |
| `tutorial/` | 上游 notebook 的中文注释和阅读笔记。 |
| `legacy/self_recorded/` | 旧自采三/四分类、mixed EDF 和历史比较 notebook。 |

notebook 只适合作为交互式入口或阅读材料；需要可重复训练/评估时使用 `scripts/` 下的 Python 入口。
