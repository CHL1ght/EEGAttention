# 这个目录是什么

这里区分 CURRENT、HISTORICAL 与 REFERENCE 数据，并保存原始脑电、manifest 和数据资格规则。

## 它属于项目哪一步

Stage 0–9：作者数据 → 自采历史 → 冻结测试 → 现场探索 → New Paradigm v1。

前一步：2026-09-14 LAB_FEEDBACK historical pilot。
这一步：按 New Paradigm v1 协议采集和登记新 session，同时冻结旧证据边界。
后一步：达到预定 session 数量后，按完整 session 和 leave-one-day-out 设计训练/验证，并在预测前冻结最终留出。

完整故事：[实验阶段地图](../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

防止来源不明、标签不明或看过反馈的数据混进正式训练或最终测试。

## 输入从哪里来

作者原始MAT、DSI设备导出的EDF/CSV/DSI、采集者确认的身份与任务记录。

## 谁生成这里的文件

原始文件由设备/作者提供；清单人工登记；validate_legacy_manifest.py与validate_locked_data.py只读验收。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [current/](current/README.md) | **CURRENT** 数据入口；New Paradigm v1 的 schema、raw/notes/protocols 骨架。 | 目录 | 按 v2 协议新增，不覆盖原始文件 |
| [historical/](historical/README.md) | **HISTORICAL** 逻辑索引；旧物理路径原位保留以维持引用与复现。 | 目录 | 只维护索引和状态 |
| [legacy/](legacy/README.md) | 这里封存早期自采原始信号；训练能用哪些片段由 legacy_manifest.csv 决定。 | 目录 | 按子目录规则 |
| [locked/](locked/README.md) | 这里封存预先指定的独立测试信号，训练程序不能使用；今天的反馈录制另有目录。 | 目录 | 按子目录规则 |
| [reference/](reference/README.md) | 这里保存原作者提供的MAT数据：最初用于复现，后来也为作者模型和mixed模型提供训练录制。 | 目录 | 按子目录规则 |
| [DATA_PROTOCOL.md](DATA_PROTOCOL.md) | HISTORICAL v1 协议；保留旧 legacy/locked/LAB_FEEDBACK 规则。 | 手写维护 | 可维护，保留来源与实验边界 |
| [legacy_manifest_dictionary.md](legacy_manifest_dictionary.md) | legacy manifest 30 列的数据字典。 | 手写维护 | 可维护，保留来源与实验边界 |
| [legacy_manifest.csv](legacy_manifest.csv) | 唯一历史候选入口；记录身份、标签、片段、分组、路径与哈希。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [recording_notes_template_simplified.md](recording_notes_template_simplified.md) | 现场采集后填写的 session 记录模板。 | 手写维护 | 可维护，保留来源与实验边界 |
| [session_manifest.csv](session_manifest.csv) | 正式locked/reference录制的唯一登记；不收LAB_FEEDBACK数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [exploratory/](exploratory/README.md) | HISTORICAL exploratory 数据；含 2026-09-14 pilot。 | 目录 | 原始文件不改名、不覆盖 |

## 当前状态

CURRENT 的 New Paradigm v1 manifest 只有表头、0 条 session；HISTORICAL 与 REFERENCE 数据保持原位。2026-09-14 pilot 已归档 11 条 EDF，但所有 eligibility 均为 false。

## 我什么时候需要看这个目录

新采集先看 [New Paradigm v1 数据入口](current/new_paradigm_v1/README.md) 和 [v2 协议](../docs/current/DATA_PROTOCOL_V2.md)。

## 不要误解

旧 manifest 不会自动升级为 CURRENT；任何新录制都必须按 v2 schema 登记，final holdout 也必须在预测前冻结。
