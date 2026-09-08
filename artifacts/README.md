# 实验产物来源说明

本目录按“谁生成、用什么数据生成、能否代表当前研究”分类。上游数据、原作者结果和我们运行上游流程后生成的产物必须分开。

## `upstream_author/`：原作者仓库结果

- `results/`：在项目最早的上游版本中已经存在的 15 份训练结果表。
- 这里不再放我们后来生成的数组、缓存或模型权重。

这些文件仅用于追溯上游工作，不作为我们的实验结论。

## `legacy/`：我们的历史探索产物

- `notebook_outputs/`：旧自采 notebook 生成的缓存、数据检查表和对比结果。

它们同样不属于下一阶段正式训练管线，但来源与原作者文件分开保存。

## `reproductions/`：我们运行或改造上游流程的产物

`reproductions/upstream_pipeline/` 保存 2026 年修改并运行上游 Notebook/辅助脚本后加入仓库的数组、特征缓存、深度模型权重和结果。它们使用原作者 MAT 数据，但不是原作者直接提供的产物。

这些产物也不是当前要构建的 `legacy_baseline_v0`，不得直接用于 LOCKED_TEST。详见 `reproductions/upstream_pipeline/README.md`。
