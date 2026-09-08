# Legacy 数据说明

`legacy_manifest.csv` 每一列的中文含义和后续读取规则见 [`../legacy_manifest_dictionary.md`](../legacy_manifest_dictionary.md)。

Legacy 是项目早期自采数据的封存区。原始 EDF、CSV 和 DSI 不在此目录内修改。

## `multiclass_10min/`

这批文件每个 EDF 只对应一种状态，是 `legacy_baseline_v0` 的候选训练/验证来源。具体身份由 `../legacy_manifest.csv` 记录，不再由新代码自行猜测文件名。

标签映射：

| 原标签 | 当前口径 | 用途 |
|---|---|---|
| `focus` | `focus` | 二分类候选数据 |
| `iu` | `unfocus` | 二分类候选数据 |
| `ou` | `unfocus` | 二分类候选数据 |
| `daze` | `rest` | 静息参考，排除二分类 |

数据负责人已确认：无被试名前缀的文件来自 `lyc`，`zyf_` 前缀文件来自 `zyf`。清单中的 `subject_id`、`recording_id` 和 `session_group_id` 均使用这两个明确标识；原始文件名不改，避免破坏旧 Notebook 引用，也便于用 SHA-256 对照原件。

时间字段按以下证据填写：

- `recorded_date`：便于筛选的采集日期。
- `recorded_at_local`：EDF 文件头记录的本地采集起始时间，精确到秒。
- `recorded_at_source`：固定为 `edf_header`。
- `file_modified_at_local`：Windows 文件“修改日期”，用于交叉核对。

目前登记的 39 个 EDF，其文件修改时间都晚于文件头起始时间约“录制时长 + 保存开销”，两者能够互相印证。因此清单把更接近真实采集开始的 EDF 文件头时间作为主时间，修改时间作为证据保留；这些时间均未附加无法从文件确认的时区偏移。

`session_group_id` 按“被试 + 文件编号”保守分组。例如 `focus1/iu1/ou1/daze1` 被视为同一个可能的历史 session 组，防止后续把可能同次录制的条件拆到训练和验证两边。如果以后找到准确日期/实验记录，再修正该分组。

## `mixed_20min/`

这批文件采用固定的 20 分钟实验设计。两个旧 Notebook 对顺序的文字记录相反，现按以下证据确定：

- `multi_edf_training_explained.ipynb` 较早，作为通用讲解稿，写的是“前 10 分钟专注，后 10 分钟不专注”。
- `multi_edf_original_self_5comparisons_count_channels.ipynb` 较晚，专门针对这批自采 EDF，明确设置 `SELF_SEGMENT_ORDER = "unfocus_first"`，并已经实际成功读取全部 9 个有效文件、为两个片段各提取 585 个旧流程窗口。

因此清单采用较晚且实际运行过的专项 Notebook：

- `0–600 s`：`unfocus`
- `600–1200 s`：`focus`
- `1200 s` 之后：实验状态没有可靠记录，不使用

有效混合录制包括 `lyc`、`zqd`、`zyf` 各 3 个文件。每个 EDF 在清单中登记为两个逻辑片段，但共享同一个 `source_recording_id` 和 `session_group_id`；后续划分数据时必须让同一 EDF 的两个片段整体进入同一侧，不能一个训练、一个测试。

`data_0001_raw.edf` 只有 2.5 秒，是早期设置/演示文件，短于一个 4 秒窗口。它会进入总清单，但标为 `excluded_too_short`，不参与训练。

## 验收

在使用 Legacy 数据前运行：

```powershell
python scripts/validate_legacy_manifest.py
```

验收会检查 39 个 EDF 是否全部登记，以及身份、两类时间证据、混合片段边界、路径、标签映射、分组、采样率、信号数、时长和 SHA-256 是否一致。
