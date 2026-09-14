# 这个目录是什么

这里保存原作者提供的MAT数据：最初用于复现，后来也为作者模型和mixed模型提供训练录制。

## 它属于项目哪一步

Stage 0 → 6 → 7：原作者数据 → 作者内部验证 → 跨来源共同六通道实验。

前一步：从已有实验或上游材料形成这个阶段的输入。
这一步：这里保存原作者提供的MAT数据：最初用于复现，后来也为作者模型和mixed模型提供训练录制。
后一步：按阶段地图查看其后续用途，历史材料不覆盖新结果。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

最初复现的是什么，原方案能否运行？

## 输入从哪里来

data/reference/original_mat/ 的 34 个 MATLAB（MAT，保存数组的文件）与 notebooks/upstream/ 的原作者代码。

## 谁生成这里的文件

原作者采集并提供MAT；本仓库只读保存。notebooks/upstream/inspect_original_mat.ipynb用于查看结构，scripts/train_cross_source_models.py按固定清单读取23个recording训练。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [original_mat/](original_mat/README.md) | 这里保存原作者的34个原始MAT录制文件；后续作者模型按固定清单选择其中23个，不改写原始文件。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

原始数据只读；角色按清单/协议决定。

## 我什么时候需要看这个目录

需要回答“最初复现的是什么，原方案能否运行？”时查看本目录文件。

## 不要误解

不进入旧pooled或lyc/zyf personal训练；author-only/author-common6/mixed按清单选23个recording。作者reference未知，不声称与我们的Pz参考完全一致。
