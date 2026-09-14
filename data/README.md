# 这个目录是什么

这里保存原始脑电、允许训练的数据清单和禁止训练的测试/探索数据规则。

## 它属于项目哪一步

Stage 0–8：作者数据 → 自采历史 → 冻结测试 → 现场探索。

前一步：Common6 通道对齐与 Mixed。
这一步：防止来源不明、标签不明或看过反馈的数据混进正式训练或最终测试。
后一步：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

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
| [legacy/](legacy/README.md) | 这里封存早期自采原始信号；训练能用哪些片段由 legacy_manifest.csv 决定。 | 目录 | 按子目录规则 |
| [locked/](locked/README.md) | 这里封存预先指定的独立测试信号，训练程序不能使用；今天的反馈录制另有目录。 | 目录 | 按子目录规则 |
| [reference/](reference/README.md) | 这里保存原作者提供的MAT数据：最初用于复现，后来也为作者模型和mixed模型提供训练录制。 | 目录 | 按子目录规则 |
| [DATA_PROTOCOL.md](DATA_PROTOCOL.md) | 数据角色、标签、窗口、禁止泄漏规则；第7节定义现场反馈metadata。 | 手写维护 | 可维护，保留来源与实验边界 |
| [legacy_manifest_dictionary.md](legacy_manifest_dictionary.md) | legacy manifest 30 列的数据字典。 | 手写维护 | 可维护，保留来源与实验边界 |
| [legacy_manifest.csv](legacy_manifest.csv) | 唯一历史候选入口；记录身份、标签、片段、分组、路径与哈希。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [recording_notes_template_simplified.md](recording_notes_template_simplified.md) | 现场采集后填写的 session 记录模板。 | 手写维护 | 可维护，保留来源与实验边界 |
| [session_manifest.csv](session_manifest.csv) | 正式locked/reference录制的唯一登记；不收LAB_FEEDBACK数据。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [exploratory/](exploratory/README.md) | 这里为今天看模型反馈、主动调整状态前后的录制建立归档规则。 | 目录 | 按子目录规则 |

## 当前状态

历史与测试已登记；今天lab_feedback只有规则，无新增信号。

## 我什么时候需要看这个目录

今天带回文件时先看exploratory/lab_feedback/README.md。

## 不要误解

并非所有新录制都放locked；feedback0同样是探索数据。
