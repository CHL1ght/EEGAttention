# CURRENT 数据入口

`data/current/` 只保存当前正式继续采集、建模和验证的数据。当前研究版本为 [new_paradigm_v1](new_paradigm_v1/README.md)。

旧自采数据、旧 LOCKED_TEST 和 2026-09-14 LAB_FEEDBACK 不从这里读取；它们由 [HISTORICAL 索引](../historical/README.md)说明。作者 MAT 等外部数据继续位于 [REFERENCE](../reference/README.md)。

当前目录尚无新 EEG session。新增记录必须先遵守 [DATA_PROTOCOL_V2](../../docs/current/DATA_PROTOCOL_V2.md)，再写入版本自己的 manifest。
