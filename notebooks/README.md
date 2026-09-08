# Notebook 导航

这些 notebook 都是历史复现或探索记录，不是下一阶段正式训练入口。正式管线将放在可测试的 Python 模块和脚本中。

## 分类

- `upstream/`：论文上游代码、结果可视化及 MATLAB 数据检查。
- `legacy/self_recorded/`：旧自采 3/4 分类、旧 20 分钟切段与域偏移对比实验。
- `tutorial/`：中文注释版本和阅读笔记。

## 运行约定

从仓库根目录启动 Jupyter 或 VS Code，再运行 notebook；历史 notebook 的数据路径均相对仓库根目录。其输出统一写入 `artifacts/legacy/notebook_outputs/`，不得写回 `data/`。

旧 notebook 可能包含已经执行过的输出。随机窗口指标只用于历史流程核对，不代表跨 session 或跨被试泛化能力。

