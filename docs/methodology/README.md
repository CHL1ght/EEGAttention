# 这个目录是什么

这里解释正式基线与测试的数据划分方法，帮助读者理解为什么必须隔离录制。

## 它属于项目哪一步

Stage 2：Legacy pooled baseline

前一步：早期自采 EEG 探索。
这一步：怎样得到第一个可以保存、复查并重复预测的正式模型？
后一步：历史验证不错，不代表新的独立录制也能达到同样效果。

完整故事：[实验阶段地图](../EXPERIMENT_MAP.md)；名词和模型：[模型字典](../MODEL_CATALOG.md)。

## 为什么会有这个目录

怎样得到第一个可以保存、复查并重复预测的正式模型？

## 输入从哪里来

data/legacy_manifest.csv 批准的历史候选：按 session group（一次或一组关联录制）划分后，只有 train 侧进入拟合。旧 pooled 范围包含 zqd；后来的 personal/common6 才排除 zqd。

## 谁生成这里的文件

scripts/legacy_baseline_v0.py；scripts/eeg_pipeline_utils.py。复查只用 --check-existing，不运行训练入口。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [legacy_baseline_v0.md](legacy_baseline_v0.md) | 旧 pooled baseline 的数据范围、预处理、模型、session 划分、指标和冻结身份说明。 | 手写维护 | 可维护，保留来源与实验边界 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“怎样得到第一个可以保存、复查并重复预测的正式模型？”时查看本目录文件。

## 不要误解

历史验证 Accuracy 69.99%、Balanced Accuracy 69.64%。保存 StandardScaler（缩放特征）→ PCA（压缩特征）→ SVC（分类）全链，避免丢失训练时的处理状态。
