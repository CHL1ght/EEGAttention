# 这个目录是什么

这里保存lyc与zyf各自的模型，用来检验只学一个人的历史记录是否更好。

## 它属于项目哪一步

Stage 4：lyc / zyf personal models

前一步：独立 LOCKED_TEST。
这一步：只用同一个人的历史数据训练，会不会更适合这个人？
后一步：不能只看一个准确率，需要检查预测偏向、类别比例和不同录制。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

我们怀疑通用模型受跨人差异影响，所以分别训练两个人模型；后来发现同人模型也未稳定适应新录制。

## 输入从哪里来

data/legacy_manifest.csv中的lyc/zyf历史候选；不含zqd、未知身份或测试数据。

## 谁生成这里的文件

scripts/train_subject_models.py（历史已运行）；本轮仅加载。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [lyc/](lyc/README.md) | 只用lyc历史数据训练的个人模型。 | 目录 | 按子目录规则 |
| [zyf/](zyf/README.md) | 只用zyf历史数据训练的个人模型。 | 目录 | 按子目录规则 |
| [excluded_candidate_rows.csv](excluded_candidate_rows.csv) | 被本阶段排除的 candidate 逻辑记录；当前为 zqd 的 6 条记录。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [training_summary.json](training_summary.json) | 两个模型的 EDF/session/window 数量、模型哈希、排除统计和 `locked_test_read=false`。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；两个人模型保留原哈希。

## 我什么时候需要看这个目录

现场文件属于lyc或zyf时，QuickTest自动选其本人模型；查training_scope_summary.csv可了解训练范围。

## 不要误解

personal只学本人的历史录制，不是现场校准，也不保证比通用模型准确。
