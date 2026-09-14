# 这个目录是什么

这里保存两个只用原作者数据训练的模型：七通道基线与六通道对照。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

先确认作者数据按完整录制隔离后仍可分，再检查去掉AF4的影响。

## 输入从哪里来

data/reference/original_mat/中选定23个recording；前600秒focus，后600秒unfocus。

## 谁生成这里的文件

scripts/train_cross_source_models.py；本轮仅查已保存结果。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [author_common6/](author_common6/README.md) | 只用作者23个录制、去掉AF4后训练的六通道模型。 | 目录 | 按子目录规则 |
| [author_only/](author_only/README.md) | 只使用原作者23个MAT录制、保留七通道的模型。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |

## 当前状态

author_only与author_common6均已完成；原模型只读。

## 我什么时候需要看这个目录

要比较作者内部7ch与6ch成绩时进入两个子目录。

## 不要误解

author-only是仅作者数据训练；不是将自采个人模型微调到作者数据。
