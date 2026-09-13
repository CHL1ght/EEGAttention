# 2026-09-14（周一）正式 EEG 采集计划

> 本文是现场执行框架，不是已完成的 session 清单；未确认的条件不预先写入 `session_manifest.csv`，也不生成伪造数据文件。

## 1. 实验目标与概念边界

本批数据探索的是 `task engagement / cognitive engagement`（任务投入度 / 认知投入度），不是简单判断“有没有注意”，也不是直接进行“心流检测”。

- `attention`、`engagement`、`arousal`、`immersion/flow-like state` 不是同一个概念。
- 当前数据层仍使用兼容既有 validator 的 canonical label：`focus`、`unfocus`、`rest`。研究语义可在记录中写成 high / low task engagement，但不要擅自迁移标签体系。
- 恐怖游戏可作为 **high engagement + high arousal probe**；恐惧、紧张或兴奋会提高唤醒程度，因此不能把恐怖游戏单独当作标准 `focus` 真值。
- 每段结束立即填写四项 1–7 主观评分；这些评分是探索性标签，不是临床 / 标准化量表，也不能单独证明 flow。

## 2. 采集前必须确认

以下事项在正式录制前必须由现场人员确认。未确认前不要生成正式 session 名称或 manifest 行。

### MUST CONFIRM BEFORE RECORDING：低投入条件

同任务条件下如何稳定诱导 `unfocus` / low engagement 目前尚未确定，不能替用户假设。

不能简单用“游戏 vs 发呆 / 刷视频”代替高低投入：这样模型可能学到任务类型、视觉刺激、动作、眼动或面部肌电差异，而不是 engagement 本身。

现场需确认并记录：低投入条件的具体任务、指令、持续时间、何时开始 / 结束、是否仍进行同一游戏任务，以及为什么该条件代表较低任务投入。若无法确认，记录为未知，不凭印象补写。

### 其他 MUST CONFIRM BEFORE RECORDING 项

- `lyc` 的王者荣耀具体模式 / 版本和是否点陪玩；若存在语音交流或本人持续讲话，必须在该段 notes 中如实记录。
- `zyf` 的下棋具体平台 / 模式 / 版本，以及恐怖游戏的具体名称、版本和 probe 指令；恐怖游戏是否采用现有 canonical label 需现场确认，并保留“高投入 + 高唤醒 probe”的语义说明，不静默当作唯一 `focus` 定义。
- 每位被试的实际 session 顺序、每段目标时长和补录安排。顺序不要固定为 `focus -> unfocus -> focus -> unfocus`；应采用交叉 / 平衡的可执行顺序，或把实际顺序完整记录下来。
- headset / serial number、Trigger Source（`Wired` / `Wireless`）、输出目录、basename 以及 EDF / CSV / DSI 三种输出是否都产生。
- 是否保留设备默认 Trigger / Annotations。当前没有经过验证的实时 marker 编码方案；不得临时建立 marker 标签表，不得把 `0/1/2/3` 类别 ID 当作硬件编码。

## 3. 固定采集口径

| 项目 | 明日规则 |
|---|---|
| 软件 | `DSIStreamer` |
| 目标采样率 | 300 Hz |
| EEG 通道 | 24 个 |
| 参考 | Pz |
| 其他信号 | `Trigger`、`EDF Annotations` |
| 文件粒度 | 一个 session / 一个 EDF / 一种实验状态 |
| canonical label | `focus`、`unfocus` 或 `rest`；由文件名 + manifest / notes 决定 |
| marker | 可按设备默认保留，但不承担标签真值 |
| 窗口 | 4 秒窗、2 秒步长 |
| buffer | 默认首尾各 30 秒；实际有效活动起止必须现场记录 |
| 锁定目录 | `data/locked/2026-09-14/` |

30 秒只是默认 buffer。`valid_activity_start` / `valid_activity_end` 必须依据现场真实任务起止填写，不能在录制后凭印象猜。

## 4. 建议现场时间框架

这是执行框架，不为填满时间强制制造无意义录制；实际顺序、暂停和补录都写入 notes。

| 时间 | 现场事项 |
|---|---|
| 16:00–16:30 | 设备连接、佩戴、信号检查；确认 DSIStreamer 为 300 Hz / 24 EEG / Pz；记录 headset / serial 与 Trigger Source；做 1–2 分钟测试采集；检查 EDF、CSV、DSI 是否正常保存 |
| 16:30–16:45 | 正式实验说明；确认每位被试的高 / 低投入任务、低投入定义、文件 basename 与录制顺序 |
| 16:45–18:15 | 第一轮正式采集；每段采用单一状态，结束后立即填写记录模板与自评 |
| 18:15–18:30 | 休息与文件完整性检查，不覆盖已有文件 |
| 18:30–19:15 | 第二轮、补录或恐怖游戏 probe；probe 的任务和语义单独记录 |
| 19:15–20:00 | 复制原始文件；核对命名；填写 metadata / notes；登记 SHA-256；更新 manifest；确认原始文件完整性 |

### 被试与任务记录边界

- `lyc`：王者荣耀是主要高投入任务。若点陪玩、语音交流或持续讲话，记录具体情况；讲话、面部肌肉和动作可能产生 EEG / 肌电伪迹。
- `zyf`：下棋是相对低情绪刺激的高投入任务；恐怖游戏是额外的高投入 + 高唤醒 probe，不是标准高专注唯一真值。
- 低投入 / `unfocus` 条件尚未定稿，必须完成上面的确认后才能录制和命名。

## 5. Session、命名与记录

- 单段可按约 10–15 分钟设计，但不是不可修改的硬规则；实际 `start_time`、`end_time`、有效活动起止和中断都要记录。
- 避免让状态标签与疲劳 / 时间顺序完全绑定。若现场无法平衡顺序，至少记录真实顺序。
- 延续现有命名规律：`被试_focus_序号_YYYYMMDD.edf`、`被试_unfocus_序号_YYYYMMDD.edf` 或 `被试_rest_序号_YYYYMMDD.edf`。例如：`lyc_focus1_20260914.edf`、`lyc_unfocus1_20260914.edf`、`zyf_focus1_20260914.edf`。这些只是命名示例，不是预先承诺的 session 清单。
- EDF、CSV、DSI 使用相同 basename；序号在现场确认，禁止覆盖任何已有文件。
- 每段结束立即复制 [`data/recording_notes_template.md`](../../recording_notes_template.md) 填写一份记录。详细任务 / 异常 / 自评放在记录中；`session_manifest.csv` 保持现有 schema，不为本次采集增加字段。

## 6. DSIStreamer 现场 checklist

- [ ] DSIStreamer 已正确启动；仓库本身不控制采集软件
- [ ] 配置确认：300 Hz
- [ ] 配置确认：24 个 EEG 通道
- [ ] 配置确认：Pz reference
- [ ] 输出含 `Trigger` / `EDF Annotations`
- [ ] headset / serial 已记录
- [ ] Trigger Source 已记录（`Wired` / `Wireless`）
- [ ] 输出目录已确认
- [ ] basename 已确认，且不会覆盖已有数据
- [ ] 1–2 分钟测试采集成功
- [ ] 测试 EDF 可读取
- [ ] 测试 CSV 已同步导出
- [ ] DSI 原始格式是否导出已记录
- [ ] 正式每段都为单一状态
- [ ] 真实有效活动起止已记录
- [ ] 该段结束后 metadata、四项自评和异常已填写

## 7. 采集结束与 LOCKED_TEST 验收

1. 将实际产生的 EDF / CSV / DSI 原始文件放入 `data/locked/2026-09-14/`；不覆盖、不就地编辑。
2. 只有确认过的真实文件才登记到 `data/session_manifest.csv`；使用现有 19 列，不增加字段。
3. 为每个 EDF 登记 SHA-256，并核对 EDF、CSV、DSI basename 与路径。
4. 运行只读验收：

   ```powershell
   python scripts/validate_locked_data.py
   python scripts/validate_legacy_manifest.py
   ```

5. `dataset_role=locked_test` 的数据禁止训练、调参、特征选择、阈值选择和模型选择；不得根据本批表现调整模型后仍把它称作独立测试集。

