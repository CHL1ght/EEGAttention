# 数据目录

这里是项目唯一的数据入口。

## 本目录直接文件

| 文件 | 代表什么 | 是否可修改 |
|---|---|---|
| `README.md` | 数据目录导航、数据源优先级和使用方式。 | 可更新文档。 |
| `DATA_PROTOCOL.md` | 正式标签、活动区间、4s/2s 窗口、session 划分和 LOCKED_TEST 禁止事项。 | 规则变更需留痕。 |
| `legacy_manifest.csv` | 旧数据的唯一身份/标签/时间/用途/路径/哈希登记；训练脚本只从它读取。 | 不应随意重排或覆盖。 |
| `legacy_manifest_dictionary.md` | legacy manifest 30 列的数据字典。 | 可更新文档。 |
| `session_manifest.csv` | 正式 locked/reference session 登记；评估脚本的唯一正式测试入口。 | 新 session 追加，禁止覆盖原行。 |
| `recording_notes_template_simplified.md` | 现场采集后填写的 session 记录模板。 | 模板可迭代。 |

| 位置 | 用途 | 是否进入新管线 |
|---|---|---|
| `session_manifest.csv` | 正式 session 清单和标签真值 | 是，唯一入口 |
| `legacy_manifest.csv` | `legacy_dataset_v0` 的录制身份、采集时间证据、标签映射、用途和哈希 | 是，旧 baseline 的唯一候选入口 |
| `locked/YYYY-MM-DD/` | 新标准单状态录制；当前作为不可触碰的最终测试集 | 仅最终测试 |
| `legacy/mixed_20min/` | 旧 20 分钟固定顺序录制；按清单中的片段边界读取 | Legacy 候选，必须按完整 EDF 分组 |
| `legacy/multiclass_10min/` | 旧单状态自采记录 | 候选 Legacy 训练/验证集；须由新主 Notebook 按完整 EDF 划分 |
| `reference/original_mat/` | 论文/上游项目的 MATLAB 参考数据 | 仅历史复现 |

子目录 README：

- [`legacy/README.md`](legacy/README.md)：旧自采数据及两个数据族。
- [`locked/README.md`](locked/README.md)：正式测试和采集计划。
- [`reference/README.md`](reference/README.md)：上游 MAT 数据。

EDF、CSV、DSI、MAT 原始文件均不得在仓库内就地编辑；需要修正身份、标签或活动区间时更新清单并保留哈希/说明。

## 新数据怎么放

1. 每个文件只录一种状态，文件名使用：`被试_focus_序号_YYYYMMDD.edf`、`被试_unfocus_序号_YYYYMMDD.edf` 或 `被试_rest_序号_YYYYMMDD.edf`。
2. 配套 CSV/DSI 使用相同主体名；不要覆盖旧文件。
3. 放入 `data/locked/YYYY-MM-DD/`。
4. 在 `session_manifest.csv` 增加一行，填写活动有效起止秒数；不清楚时采用首尾各 30 秒缓冲。
5. 运行 `scripts/validate_locked_data.py`，确认时长、采样率、通道、哈希、标签和窗口数全部通过。

2026-09-14 的现场执行框架见 [`locked/2026-09-14/recording_plan.md`](locked/2026-09-14/recording_plan.md)，每段录制后的空白记录模板见 [`recording_notes_template_simplified.md`](recording_notes_template_simplified.md)。模板中的任务、说话、异常和四项主观评分不改变现有 manifest schema；真实录制完成后再把已确认的字段写入现有 19 列清单。

当前 `focus/unfocus` 仍是数据层 canonical label，研究表述逐步转向高 / 低任务投入度。高唤醒（例如恐惧）不等同于高投入；恐怖游戏应记录为额外的高投入 + 高唤醒 probe，不自动成为 `focus` 的唯一标准。当前 Trigger 不承担标签真值。

详细规则见 [DATA_PROTOCOL.md](DATA_PROTOCOL.md)。

## Legacy 二分类口径

- `focus` 保持为 `focus`。
- `iu` 和 `ou` 合并为 `unfocus`。
- `daze` 作静息参考，不进入当前二分类。
- `mixed_20min/` 按较晚且实际运行过的专项 Notebook，统一解释为前 10 分钟 `unfocus`、后 10 分钟 `focus`；较早的通用讲解稿写反，清单中保留了这一来源冲突。

mixed 的状态和边界直接写在 `legacy_manifest.csv` 的 `canonical_label`、`activity_start_s`、`activity_end_s` 中，不依赖另一份隐藏映射。未来主 Notebook 对所有数据统一按“路径 + 起点 + 终点 + 标签”读取，不需要针对 mixed 文件名写特判。

当前清单覆盖 39 个 EDF，共 48 行逻辑记录：43 个二分类候选片段（`focus=22`、`unfocus=21`）、4 个静息参考录制和 1 个过短演示记录。候选片段的 `split` 仍为 `unassigned`，留给规范主 Notebook 按完整 `session_group_id` 分配。

清单 30 列的逐项中文解释、允许值和使用方法见 [`legacy_manifest_dictionary.md`](legacy_manifest_dictionary.md)。

旧数据中无姓名前缀的文件已由数据负责人确认为 `lyc`。原始文件名保持不变，身份和时间统一以 `legacy_manifest.csv` 为准；采集开始时间取 EDF 文件头，Windows 修改时间另列用于核对。
