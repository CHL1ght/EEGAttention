# 这个目录是什么

这里保存确认 T5/T6 与 P7/P8 同名异写的证据，以及仍未解决的作者参考电极问题。

## 它属于项目哪一步

Stage 7：Common6 通道对齐与 Mixed

前一步：Author-only model。
这一步：在相同六通道输入下，加入作者训练数据能否改善新录制表现？
后一步：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

完整故事：[实验阶段地图](../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

在相同六通道输入下，加入作者训练数据能否改善新录制表现？

## 输入从哪里来

common6（我们的EDF与作者MAT都能可靠对应的六个EEG通道）：F7,F3,P7,O1,O2,P8。T5/T6依据设备和命名证据对应P7/P8；舍弃AF4。

## 谁生成这里的文件

scripts/verify_common6_compatibility.py；scripts/train_cross_source_models.py 的 author-common6 / our-common6 / mixed-common6；scripts/evaluate_cross_source_models.py --channel-set common6。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [author_mat_metadata.csv](author_mat_metadata.csv) | 34 个作者 MAT 的 `o` struct 字段、数据形状、采样率和是否存在 reference/montage 字段。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [BLOCKED.json](BLOCKED.json) | 机器可读门禁记录；common6审计中当前已解除阻塞，旧common7中仍为历史阻塞。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [BLOCKED.md](BLOCKED.md) | 解释门禁或状态迁移；不能只凭文件名判断当前是否可训练。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [edf_header_metadata.csv](edf_header_metadata.csv) | 已确认 lyc/zyf 历史 EDF 与当前 LOCKED_TEST/reference EDF 的 MNE/原始 EDF 通道头信息。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [evidence_audit.csv](evidence_audit.csv) | 每条兼容性证据及其是否支持映射/reference 的结构化记录。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [HISTORICAL_BLOCKED_REPORT.md](HISTORICAL_BLOCKED_REPORT.md) | 原始保守阻塞报告快照，不删除历史判断过程。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [HISTORICAL_BLOCKED.json](HISTORICAL_BLOCKED.json) | 原始阻塞 JSON 快照。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [HISTORICAL_EVIDENCE_AUDIT.csv](HISTORICAL_EVIDENCE_AUDIT.csv) | 原始证据审计表快照。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [notebook_audit.json](notebook_audit.json) | 作者 notebook 的通道选择、数据切片和显式 rereference 操作检查。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [REPORT.md](REPORT.md) | 当次实验的原始报告；当前阶段解释见本README，历史结论不改写。 | 手写维护 | 不就地覆盖；需另存版本并留痕 |
| [run_manifest.json](run_manifest.json) | 记录当次运行的来源、输出哈希和执行策略。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [sidecar_metadata.csv](sidecar_metadata.csv) | DSIStreamer CSV sidecar 的 `Reference location`、headset、logger、filter、单位和通道头。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

已完成；既有模型/结果只读。

## 我什么时候需要看这个目录

需要回答“在相同六通道输入下，加入作者训练数据能否改善新录制表现？”时查看本目录文件。

## 不要误解

当前 COMMON6 已解除通道命名阻塞；HISTORICAL_* 保留此前保守判断，不能拿旧状态覆盖当前结论。
