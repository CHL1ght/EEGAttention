# 数据目录

这里是项目唯一的数据入口。

| 位置 | 用途 | 是否进入新管线 |
|---|---|---|
| `session_manifest.csv` | 正式 session 清单和标签真值 | 是，唯一入口 |
| `legacy_manifest.csv` | `legacy_dataset_v0` 的录制身份、采集时间证据、标签映射、用途和哈希 | 是，旧 baseline 的唯一候选入口 |
| `locked/YYYY-MM-DD/` | 新标准单状态录制；当前作为不可触碰的最终测试集 | 仅最终测试 |
| `legacy/mixed_20min/` | 旧 20 分钟固定顺序录制；按清单中的片段边界读取 | Legacy 候选，必须按完整 EDF 分组 |
| `legacy/multiclass_10min/` | 旧单状态自采记录 | 候选 Legacy 训练/验证集；须由新主 Notebook 按完整 EDF 划分 |
| `reference/original_mat/` | 论文/上游项目的 MATLAB 参考数据 | 仅历史复现 |

## 新数据怎么放

1. 每个文件只录一种状态，文件名使用：`被试_focus_序号_YYYYMMDD.edf`、`被试_unfocus_序号_YYYYMMDD.edf` 或 `被试_rest_序号_YYYYMMDD.edf`。
2. 配套 CSV/DSI 使用相同主体名；不要覆盖旧文件。
3. 放入 `data/locked/YYYY-MM-DD/`。
4. 在 `session_manifest.csv` 增加一行，填写活动有效起止秒数；不清楚时采用首尾各 30 秒缓冲。
5. 运行 `scripts/validate_locked_data.py`，确认时长、采样率、通道、哈希、标签和窗口数全部通过。

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
