# HISTORICAL 数据索引

`HISTORICAL` 表示旧实验、旧模型对应数据、已结束测试或已被新范式替代的 pilot。它们必须保留并可复现，但不是 New Paradigm v1 的默认训练入口。

为避免破坏大量硬编码路径，本轮建立逻辑索引，不移动原始数据：

| 历史类别 | 当前物理位置 | 状态 |
|---|---|---|
| legacy self-recorded | [data/legacy](../legacy/README.md) | historical training source；仅供旧模型复现 |
| locked_test_v1 | [data/locked](../locked/README.md) | historical locked/reference set；不可重新定义为新 final holdout |
| 2026-09-14 LAB_FEEDBACK | [historical pilots index](pilots/README.md) | historical pilot / transition dataset；不可训练、不可 final-test |

CURRENT 数据见 [data/current](../current/README.md)。外部作者数据属于 [REFERENCE](../reference/README.md)，不属于本目录。
