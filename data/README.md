# 数据目录

这里是项目唯一的数据入口。

| 位置 | 用途 | 是否进入新管线 |
|---|---|---|
| `session_manifest.csv` | 正式 session 清单和标签真值 | 是，唯一入口 |
| `locked/YYYY-MM-DD/` | 新标准单状态录制；当前作为不可触碰的最终测试集 | 仅最终测试 |
| `legacy/mixed_20min/` | 旧 20 分钟混合状态录制，依赖人为切段假设 | 否 |
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
- `mixed_20min/` 存在切段顺序记录冲突，当前只封存，不再人工切段作训练。
