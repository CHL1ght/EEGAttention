# EEG 数据协议 v1

> 状态：`HISTORICAL / protocol v1`。本文保留旧 legacy、LOCKED_TEST 与 LAB_FEEDBACK 的原始规则；CURRENT 采集与 manifest 规则见 [DATA_PROTOCOL_V2.md](../docs/current/DATA_PROTOCOL_V2.md)。

本协议从 2026-09-08 起作为项目的唯一正式数据口径。

## 1. 标签来源

- 每次录制只包含一种状态：`focus`（专注）、`unfocus`（不专注）或 `rest`（静息态）。
- 不依赖软件 marker。标签由文件名和 `session_manifest.csv` 共同确定。
- `focus` / `unfocus` 是当前为兼容数据入口保留的 canonical label；研究语义正在转向 `high / low task engagement`（高 / 低任务投入度），不能把数据标签直接表述为“心流检测”。`attention`、`engagement`、`arousal` 和 `immersion/flow-like state` 不是同一概念。
- 高唤醒不等于高投入：紧张、恐惧和兴奋都可能提高 `arousal`。恐怖游戏如被采集，只作为“高投入 + 高唤醒”的额外 probe，不作为 `focus` 的唯一标准定义。
- `death` 是当前静息态文件的早期命名；清单统一标为 `rest`，但保留原文件名用于追溯。
- 当前正式任务是 `focus` vs `unfocus` 二分类；`rest` 只用于基线或质量检查，不并入 `unfocus`，也不计入二分类指标。
- 旧 `multiclass_10min` 中文件名明确的 `focus` 可作为 Legacy 二分类的 `focus`，`iu` 和 `ou` 可合并为 `unfocus`；`daze` 只作静息参考。
- 没有可追溯标签的旧数据不得进入正式训练、调参或测试。`mixed_20min` 仅使用清单明确登记的 `0–600 s=unfocus`、`600–1200 s=focus` 片段；顺序依据较晚且实际运行过的专项 Notebook，并在清单中保留与早期通用讲解稿冲突的说明。
- 同一个混合 EDF 的两个片段必须按共同的 `source_recording_id` / `session_group_id` 整体划分，禁止分散到训练与验证两侧。

### 1.1 采集语义与 marker 边界

- 正式采集优先采用“一个 session / 一个 EDF / 一种状态”，不在同一 EDF 中途切换标签。
- `Trigger` 和 `EDF Annotations` 可以按设备默认方式保留，但当前没有经过验证的实时 marker 编码方案；不要把 `0/1/2/3` 等类别编号当作硬件 marker 编码，也不要用 Trigger 单独推断标签。
- 现场记录的 `attention`、`engagement`、`arousal`、`immersion` 评分是探索性主观标签，不是临床或标准化量表，不能单独证明 flow。

## 2. 有效活动区间

录制时长可能比实际测试活动略长，因此不直接把 EDF 全长都当作有效样本。

- 默认丢弃每段开头 30 秒和结尾 30 秒。
- 清单中的 `activity_start_s`、`activity_end_s` 是唯一有效区间；以后若掌握某次活动的准确起止时间，可以逐行覆盖默认值。
- 有效区间不足 5 分钟的数据可以保存，但标记为 `excluded_short`，不计入正式指标。静息态标记为 `reference_rest`。

## 3. 唯一窗口规范

- 窗长：4 秒。
- 步长：2 秒（50% 重叠）。
- 仅保留完整落在有效活动区间内的窗口。
- 尾部不足 4 秒的残段直接丢弃，不补零。
- 窗口继承整段 session 的标签；单个文件内不发生标签切换。

4 秒窗口兼顾频域特征稳定性和未来在线反馈速度。15 秒聚合和约 1 秒 STFT 帧仍可作为特征内部计算或对照实验，但不再改变“一个正式样本窗口”的定义。

## 4. 划分与防泄漏

顺序固定为：

`读取清单 → 按完整 session/被试划分 → 在各自集合内切窗口 → 特征 → 模型 → 报告`

- `dataset_role=locked_test` 的文件禁止参与训练、特征选择、阈值选择、超参数选择和模型挑选。
- 相邻窗口高度相关，禁止把同一 session 的窗口随机拆到训练集和测试集。
- 主指标至少按完整 session 汇总；有足够被试后，优先报告按被试留一或独立被试测试。
- 旧 notebook 中的随机窗口结果只作为历史流程检查，不作为模型泛化结论。

## 5. 锁定规则

- 只有预先指定为独立最终测试的录制，才放入 `data/locked/YYYY-MM-DD/` 并在 `session_manifest.csv` 登记；现场反馈探索录制按第7节进入 `data/exploratory/lab_feedback/`。
- EDF、CSV、DSI 原文件不得覆盖或就地编辑。
- EDF 的 SHA-256 写入清单；验收脚本发现哈希变化时必须失败。
- `dataset_role=locked_test` 的数据禁止用于训练、调参、特征选择、阈值选择或模型选择；不能根据这批数据的表现调整模型后，仍将其称作独立测试集。
- 正式使用前运行 `scripts/validate_locked_data.py`。只有 `status=ready` 且通过验收的数据才进入锁定测试。

## 6. 2026-09-14 现场采集补充

- 固定设备事实：使用 `DSIStreamer`；目标配置为 300 Hz、24 个 EEG 通道、Pz reference，并保留 `Trigger` 与 `EDF Annotations`。
- 采集前必须现场核对 headset / serial、Trigger Source（`Wired` / `Wireless`）、输出目录、文件 basename，以及 EDF、CSV、DSI 是否实际导出。仓库文档不代表仓库能够控制 DSIStreamer。
- 旧采集计划保留在 [`locked/2026-09-14/recording_plan.md`](locked/2026-09-14/recording_plan.md)。今天执行LAB_FEEDBACK规则，见 [`exploratory/lab_feedback/2026-09-14/README.md`](exploratory/lab_feedback/2026-09-14/README.md)；旧通用现场记录模板不能替代本节feedback metadata。

## 7. LAB_FEEDBACK：现场反馈探索数据（2026-09-14新增）

LAB_FEEDBACK（现场看模型反馈、主动调整状态再录制的探索实验）的机器字段为 `dataset_role=lab_feedback`。整组实验包括尚未看到本轮反馈的feedback0和看到反馈后的feedback1+。它不是LOCKED_TEST（冻结测试数据，仅预测、禁止任何fit），也不是默认训练集。

今天流程：第一段自然状态 → QuickTest预测 → 人看到结果 → 主动调整专注/不专注状态 → 第二段录制 → 比较固定模型的预测方向。即便feedback0未看本轮反馈，它仍属于此探索方案，不能事后挑选为最终留出样本。

### 7.1 路径与命名

`data/exploratory/lab_feedback/YYYY-MM-DD/`；今天为`data/exploratory/lab_feedback/2026-09-14/`。此轮只建立README和规则，不创建假EDF、假metadata或假结果。

命名保持parser兼容：`subject_status_timestamp_extra.edf`。例如：

- `lyc_focus_202609141630_feedback0.edf`：本轮首次、未看反馈。
- `lyc_focus_202609141650_feedback1.edf`：看第一轮结果后主动调整。
- 第三轮以`feedback2`结尾；unfocus实验同理。

同一录制的EDF、CSV、DSI保持同一stem。若需规范原始导出文件名，保留原始名字、原路径与哈希的对应关系；不改信号内容，不覆盖同名文件。不能根据脑电内容猜身份。

### 7.2 数据返回后才登记metadata

每个EDF一行，计划使用日期目录内的`metadata.csv`；本轮不提前创建记录。至少定义：

| 字段 | 含义与填写规则 |
|---|---|
| subject_id | 可确认的受试者身份；不确认则unknown，不猜测 |
| intended_label | 录制任务预期focus/unfocus；不是从模型预测倒填的真实心理状态 |
| timestamp | 录制开始本地时间；与文件名一致，保留Asia/Shanghai时区 |
| feedback_round | 整数0、1、2…；每组前后比较独立计数 |
| feedback_seen_before_recording | round=0为false；round>=1为true；若实际反馈历史不符合规则，记录异常并人工确认，不能只靠文件名伪造false |
| task | 实际做的任务，不能用预测结果替代描述 |
| notes | 状态调整、运动/说话、异常、反馈内容、此前其它实验反馈等 |
| dataset_role | 固定lab_feedback |
| eligible_for_training | 固定false |
| eligible_for_final_test | 固定false |
| pair_id | 同一受试者、同一任务/目标状态的一组前后录制关联号 |
| edf_path / csv_path / dsi_path | 仓库相对路径；未导出的配套文件留空并说明 |
| edf_sha256 / csv_sha256 / dsi_sha256 | 原始文件SHA-256；缺失文件不伪造哈希 |
| original_filename | 原始导出名；若规范重命名，保留追溯信息 |

身份和预期标签要由采集记录核实，文件名只是QuickTest的便捷入口；发生冲突时暂停将其当成有效A/B对照。

### 7.3 固定整理流程

原始EDF/CSV/DSI → 确认subject/intended label/timestamp → 确认feedback round和是否看过反馈 → 保留原始文件 → 计算SHA-256 → 登记metadata → 运行QuickTest → 保存探索性分析结果。

QuickTest本身只返回内存结果。需要保存时，未来使用单独的探索结果目录（例如`artifacts/lab_feedback/YYYY-MM-DD/run_id/`），记录输入哈希、模型哈希、代码版本、全文件活动区间、预测、标签及metadata路径；当前不预造结果文件。

默认不加入`legacy_manifest.csv`训练候选，不加入`session_manifest.csv`的LOCKED_TEST。现有训练入口只接受data/legacy中的候选；现有正式测试入口只接受data/locked中的已登记记录。预测漂亮不构成数据晋升理由。以后要训练，必须单独作明确决定、记录新版本/用途/批准依据并保留lab_feedback来源；已看反馈的数据不能晋升为独立final holdout。

### 7.4 QuickTest解释与最终留出

现场按全EDF的[0,duration)提取4秒窗、2秒步长；正式LOCKED_TEST仍用原manifest活动区间。两者分数不能互相覆盖。pooled/personal用240维；mixed-common6用60维，只执行load/transform/predict/compare。

同一已确认受试者、同一标签的不同EDF允许显示描述性Accuracy差值；不同标签不计算改善Δ，未知/不同受试者也不计算。单标签下Accuracy与target比例相同；两者不是独立证据。只有另行预先规划、从未受模型反馈或选择影响的新数据，才可能作为未来真正final holdout。
