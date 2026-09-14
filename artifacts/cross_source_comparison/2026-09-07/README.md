# 这个目录是什么

这里保存共同七通道方案尚未打通时的历史对照表，不是后来 COMMON6 的完整成绩表。

## 它属于项目哪一步

Stage 6 → 7：作者模型之后、COMMON6 解阻之前的 common7 历史尝试。

前一步：从已有实验或上游材料形成这个阶段的输入。
这一步：这里保存共同七通道方案尚未打通时的历史对照表，不是后来 COMMON6 的完整成绩表。
后一步：按阶段地图查看其后续用途，历史材料不覆盖新结果。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

在相同六通道输入下，加入作者训练数据能否改善新录制表现？

## 输入从哪里来

上一阶段 pooled/personal 的2026-09-07 LOCKED_TEST结果、author-only-7ch历史CV与当时的common7通道检查。

## 谁生成这里的文件

scripts/evaluate_cross_source_models.py 的旧 common7 比较路径；本轮不重跑或覆盖本目录结果。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [common7_channel_alignment.csv](common7_channel_alignment.csv) | 6 个正式 locked EDF 的通道映射和缺失通道。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [comparison_summary.json](comparison_summary.json) | 比较使用的模型哈希、通道协议和测试策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [unified_model_comparison.csv](unified_model_comparison.csv) | 按 model × test subject 的 accuracy、balanced accuracy、author/cross-source held-out balanced accuracy 和状态。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

historical / common7 blocked；本目录原始报告保留，当前六通道结果见 ../2026-09-14/。

## 我什么时候需要看这个目录

追溯为何最初 author→EDF 结果是N/A、以及后来为什么改为六通道时查看。

## 不要误解

当时按显式名称缺少 P7/P8/AF4，因而报告 N/A。后来确认 T5/T6 等价命名解决 P7/P8，但 AF4 仍缺失；不要改写旧 REPORT，也不要把后来的 mixed-common6 分数当作本目录计算结果。
