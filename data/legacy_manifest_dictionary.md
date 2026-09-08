# `legacy_manifest.csv` 中文数据字典

`legacy_manifest.csv` 是 `legacy_dataset_v0` 的统一入口。它不复制或修改原始数据，只记录每一条可读取数据的身份、标签、有效时间范围、文件位置和审计信息。

## 先理解“一行”代表什么

- 对单状态 EDF，一行通常对应一整个 EDF。
- 对 20 分钟混合 EDF，一份物理 EDF 对应两行逻辑片段：`0–600 s` 为 `unfocus`，`600–1200 s` 为 `focus`。
- 因此，清单行数不等于 EDF 文件数。当前是 48 行，覆盖 39 个 EDF。
- 训练/验证划分必须按 `session_group_id` 整体进行，不能直接随机打散清单行或窗口。

mixed 的分段信息就在清单本身，不需要再去别处找。例如同一份 `data_zqd_1_raw.edf` 会出现两行：

| `edf_path` | `canonical_label` | `activity_start_s` | `activity_end_s` |
|---|---:|---:|---:|
| `data/legacy/mixed_20min/data_zqd_1_raw.edf` | `unfocus` | 0 | 600 |
| `data/legacy/mixed_20min/data_zqd_1_raw.edf` | `focus` | 600 | 1200 |

这两行不是重复登记：它们共同说明“同一物理文件中的哪一段是什么状态”。同一路径出现多次时，读取代码不得擅自去重。

## 1. 版本、身份与分组

| 英文字段 | 中文含义 | 当前写法 / 使用方法 |
|---|---|---|
| `dataset_version` | 数据集版本 | 当前固定为 `legacy_dataset_v0`，用于说明这行属于哪一版冻结清单。 |
| `recording_id` | 逻辑记录唯一编号 | 每行唯一。混合 EDF 的两个片段会分别以 `_unfocus`、`_focus` 结尾。代码和结果表建议用它标识一行。 |
| `source_recording_id` | 原始录制编号 | 标识物理上的同一份 EDF。混合 EDF 的两行具有相同值；单状态 EDF 通常与 `recording_id` 相同。 |
| `subject_id` | 被试编号 | 当前有 `lyc`、`zqd`、`zyf`。无姓名前缀的旧数据已由数据负责人确认为 `lyc`。 |
| `session_number` | 该类录制的序号 | 从原文件名中的编号整理而来，例如 `1`、`2`、`3`；不是训练轮数。 |
| `session_group_id` | 数据划分组编号 | 防止数据泄漏的关键字段。相同值的所有行必须一起进入训练集或验证集；后续切窗后也必须继承这个值。 |
| `segment_order` | 一份录制内部的状态顺序 | `single_state_full_recording` 表示整条单状态；`unfocus_first_then_focus` 表示先不专注后专注；`not_applicable_short_demo` 表示过短演示文件不适用。 |

`recording_id`、`source_recording_id`、`session_group_id` 的区别，可以用一份混合 EDF 举例：

| 字段 | 不专注片段 | 专注片段 | 为什么 |
|---|---|---|---|
| `recording_id` | `legacy_zqd_mixed_01_unfocus` | `legacy_zqd_mixed_01_focus` | 两行需要各自唯一。 |
| `source_recording_id` | `legacy_zqd_mixed_01` | `legacy_zqd_mixed_01` | 两行来自同一份物理 EDF。 |
| `session_group_id` | `legacy_zqd_mixed_01` | `legacy_zqd_mixed_01` | 划分时必须绑在一起，避免泄漏。 |

## 2. 采集时间

| 英文字段 | 中文含义 | 当前写法 / 使用方法 |
|---|---|---|
| `recorded_date` | 采集日期 | 从 EDF 文件头的开始时间提取，格式为 `YYYY-MM-DD`。 |
| `recorded_at_local` | 本地采集开始时间 | EDF 文件头记录的日期和时刻，格式为 `YYYY-MM-DD HH:MM:SS`。 |
| `recorded_at_source` | 采集时间来源 | 当前统一为 `edf_header`，表示来自 EDF 文件头。 |
| `file_modified_at_local` | 文件修改时间 | Windows 文件系统时间，只用于辅助追溯复制、保存或整理历史；不能替代采集时间。 |

注意：文件修改时间可能晚于实际录制结束，因为保存收尾、复制和移动都可能改变它。分析时使用 `recorded_at_local`，不要用 `file_modified_at_local` 推断实验开始时间。

## 3. 标签与标签依据

| 英文字段 | 中文含义 | 当前写法 / 使用方法 |
|---|---|---|
| `source_label` | 原始标签 | 尽量保留旧文件名或旧流程中的叫法，如 `focus`、`iu`、`ou`、`daze`、`unfocus`、`unknown`。它用于追溯，不应直接作为统一训练标签。 |
| `canonical_label` | 统一后的标签 | 新流程真正读取的标签：`focus`、`unfocus`、`rest` 或 `unknown`。其中 `iu`、`ou` 统一映射到 `unfocus`，`daze` 映射到 `rest`。 |
| `label_source` | 标签依据 | `filename_and_legacy_notebook`：文件名与旧 Notebook；`later_executed_specific_legacy_notebook`：较晚、专项且执行成功的 Notebook；`none`：没有可靠标签。 |

标签使用原则：当前二分类只使用 `canonical_label=focus` 或 `unfocus`；`rest` 是静息参考，不等于不专注；`unknown` 不进入训练、调参或测试。

## 4. 数据用途与划分状态

| 英文字段 | 中文含义 | 当前写法 / 使用方法 |
|---|---|---|
| `dataset_role` | 数据用途 | `legacy_baseline_candidate`：可进入旧基线候选池；`legacy_reference`：只作参考；`legacy_demo_reference`：过短演示记录。 |
| `split` | 训练/验证分配 | 当前候选数据均为 `unassigned`，表示尚未分配。`excluded_binary` 表示不进入二分类，`excluded_too_short` 表示因太短排除。后续主 Notebook 才能按组写出 train/validation 划分。 |
| `status` | 当前治理状态 | `candidate`：文件名明确的候选；`candidate_inferred_segment`：依据 Notebook 推断出的混合片段；`reference_rest`：静息参考；`excluded_too_short`：过短排除。 |

`dataset_role` 说明“原则上用来干什么”，`split` 说明“现在被分到哪一侧”，`status` 说明“这条记录目前经过了什么性质的判断”。三列不要混为一列。

## 5. 文件位置

| 英文字段 | 中文含义 | 当前写法 / 使用方法 |
|---|---|---|
| `edf_path` | EDF 原始文件路径 | 相对于仓库根目录的路径，是读取脑电数据的主要入口。 |
| `csv_path` | 配套 CSV 路径 | 有对应导出 CSV 时填写；没有则留空。留空不表示 EDF 缺失。 |
| `dsi_path` | 配套 DSI 路径 | 有设备原始/配套 DSI 文件时填写；没有则留空。 |

所有路径都使用仓库相对路径，这样换电脑或换仓库位置后仍可读取。原始文件名没有重命名，以免破坏旧 Notebook 引用。

## 6. 有效片段、采样与切窗参数

| 英文字段 | 中文含义 | 单位 | 当前写法 / 使用方法 |
|---|---|---|---|
| `recording_duration_s` | EDF 总时长 | 秒 | 从 EDF 文件头计算的物理录制总时长。 |
| `activity_start_s` | 有效活动开始点 | 秒 | 相对于 EDF 开头的偏移；包含该时刻。 |
| `activity_end_s` | 有效活动结束点 | 秒 | 相对于 EDF 开头的偏移；建议按半开区间 `[start, end)` 读取，不包含结束点。 |
| `sfreq_hz` | 采样率 | Hz | 当前 EEG 为 `300`，即每个通道每秒 300 个采样点。 |
| `n_signals` | EDF 信号总数 | 个 | 当前为 `26`；这是 EDF 中的信号数量，不等于最终用于建模的 EEG 通道数。 |
| `window_sec` | 窗口长度 | 秒 | 当前冻结为 `4` 秒。 |
| `step_sec` | 窗口步长 | 秒 | 当前冻结为 `2` 秒，因此相邻窗口有 2 秒重叠。 |

先按 `activity_start_s` 到 `activity_end_s` 截取有效片段，再切窗。不要先对整份混合 EDF 切窗后再按窗口序号猜标签。

## 7. 完整性与人工说明

| 英文字段 | 中文含义 | 当前写法 / 使用方法 |
|---|---|---|
| `sha256` | 文件指纹 | 对 EDF 内容计算的 SHA-256。用于检查文件是否被替换或修改；同一混合 EDF 的两行指向同一文件，因此哈希相同。 |
| `metadata_confidence` | 元数据证据摘要 | 用分号连接的机器可读证据标签，说明被试、时间、session 或切段顺序分别依据什么确定。它不是一个百分制置信分数。 |
| `notes` | 补充说明 | 给人阅读的来源、冲突、确认过程或限制说明。需要理解某条异常记录时优先看这一列。 |

`metadata_confidence` 当前会出现的片段含义：

| 证据标签 | 中文解释 |
|---|---|
| `subject_confirmed_by_owner` | 被试身份由数据负责人确认。 |
| `subject_from_filename` | 被试身份来自文件名前缀。 |
| `recorded_at_from_edf_header` | 采集开始时间来自 EDF 文件头。 |
| `session_inferred_from_filename` | session 序号/分组由文件名编号推断。 |
| `segment_order_supported_by_later_executed_specific_notebook` | 混合录制的前后状态顺序由较晚、专项且运行成功的 Notebook 支持。 |
| `label_unknown` | 没有足够证据给出状态标签。 |

## 8. 后续主 Notebook 应怎样使用

1. 只从本清单读取 `dataset_role=legacy_baseline_candidate` 的行。
2. 使用 `canonical_label`，不要直接使用 `source_label`。
3. 按 `session_group_id` 分组划分训练集和验证集，禁止按行或按窗口随机划分。
4. 按 `[activity_start_s, activity_end_s)` 截取，再使用 `window_sec` 和 `step_sec` 切窗。
5. Scaler、PCA 和 SVC 只在训练集 `fit`，验证集和以后锁定测试集只做 `transform` / `predict`。
6. 运行 `python scripts/validate_legacy_manifest.py`，确认清单与实际文件、文件头和哈希一致。

### 统一读取逻辑

主 Notebook 不应判断文件名中有没有 `mixed`，也不应把“前 10 分钟是什么状态”硬编码到代码里。对清单中的每一行都执行同一种操作：

```python
for row in candidate_rows:
    segment = read_edf_interval(
        row.edf_path,
        start_s=row.activity_start_s,
        end_s=row.activity_end_s,
    )
    label = row.canonical_label
    group = row.session_group_id
```

上面是读取契约的伪代码，实际实现会把秒数换算为采样点，并可按 `edf_path` 缓存已打开的 EDF。单状态数据的区间接近整条录制，mixed 数据的区间是 0–600 秒或 600–1200 秒；两者走完全相同的代码路径。

### 为什么不把 mixed EDF 物理切开

- 原始 EDF 保持不变，SHA-256 才能持续证明它没有被加工或替换。
- 不生成重复的大文件，也不会出现“切段文件与原文件哪个才是真值”的双入口。
- 标签和边界能在 CSV 中直接审查、修订和验证。
- 普通单状态数据、新 locked 数据也已经使用 `activity_start_s` / `activity_end_s`，所以这不是 mixed 专用机制。

只有在某个下游工具完全不能按区间读取 EDF 时，才值得额外生成可随时重建的派生片段；派生片段也不能取代本清单和原始 EDF。
