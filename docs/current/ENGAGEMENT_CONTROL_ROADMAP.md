# Task Engagement 控制变量路线图

状态：`CURRENT`。本路线图用于 New Paradigm v1 后续采集与解释，不改变 2026-09-16 已冻结的数据、标签或模型。

## 研究构念与边界

当前核心研究构念是 **task engagement / cognitive engagement（任务认知投入状态）**：人在一段工作或学习任务中是否持续、主动地投入当前任务。产品层目标是未来按时间轴估计这种状态的变化。

- 它不是简单的“游戏专注 / 不专注”二分类，也不直接等同于工作效率、正确率、反应速度或任务完成量。
- `focus` / `unfocus` 暂时保留为 New Paradigm v1 的**实验操作标签**；它们是当前采集条件，不是已经完成构念效度验证的普适真值。
- `flow`（心流）只作为未来可能研究的高投入状态；当前 `focus` 不得解释为已经验证的 flow。
- 正确率、反应时间和完成量可在未来作为 external validation，但不能单独定义 task engagement。
- `observe` 继续是 reference/control，不能改成二分类训练标签。

## 控制原则：假设驱动的 control ladder

不做所有变量的全因子排列组合。每一阶段优先攻击当前最大的混杂因素，其余采集条件尽量固定；只有前一层的主要替代解释得到检验后，才扩大任务或内部状态范围。

每轮采集在开始前完成：

1. 写清本轮主要假设、主要对照和固定条件。
2. 预先确定 session 顺序；开始录制后不得根据模型输出改变顺序。
3. 记录计划条件与实际条件、偏差、中断、设备/佩戴和辅助状态量。
4. 在任何预测前冻结当日 session 清单和角色；prediction-only 数据不得反向参与调参、重标或筛选。
5. 以完整 session 隔离窗口；有两个 recording day 后优先做 leave-one-day-out。

## 混杂因素族

| 因素族 | 需要记录或对照的内容 | 主要风险 |
|---|---|---|
| session / recording-day drift | 日期、录制顺序、电极/佩戴变化、时间漂移、疲劳随时间变化 | 模型识别日期或顺序，而非投入状态 |
| motor / physical activity | 主动手部操作、无手部操作、有操作但认知负荷低、姿势变化 | 模型识别肌电、动作或姿势 |
| active vs passive engagement | 主动打游戏、认真观战、被动观看、主动完成任务 | 把刺激注意误当成主动任务投入 |
| task domain | 游戏、阅读、做题、coding、网课/视频 | 模型只学到特定任务或界面 |
| physiological / arousal state | 清醒、疲劳、困倦、睡眠情况，适度记录 caffeine | 把唤醒或睡眠状态误当成 engagement |
| affect / stress | 情绪、压力、紧张程度、主观唤醒水平 | 把情绪或压力反应误当成 engagement |
| environment / acquisition | 噪声、场地、设备状态、电极接触和佩戴异常 | 模型识别采集质量或环境变化 |

这些变量并非都能“彻底排除”。内部状态和现实环境因素应先被记录，再在样本量允许时进入分层分析、敏感性分析或显式建模。

## C1：跨日 + 顺序随机化（最高优先级）

### 为什么先做

2026-09-16 的二分类录制顺序为 `F-F-F-U-U-U`。因此标签与 recording order 完全混杂；即使 6-session LOSO 很高，也不能区分 task condition 与时间、疲劳、设备、电极或其他 session drift。

### 下一 recording day 的具体方案

- 在录制前预先生成并保存 3 个 focus、3 个 unfocus 的交错/随机顺序，例如 `U-F-U-F-F-U`。
- 开始录制后不看预测来调整顺序，不因某段“看起来不好”而替换其角色。
- 尽量固定设备、佩戴流程、姿势、场地、任务版本、session 时长和间隔；记录任何实际偏差。
- Day 2 session 在首次预测前冻结清单、条件、顺序和用途。
- 加载 frozen 2026-09-16 model，对 Day 2 只做 prediction-only；不 fit、不校准、不调阈值、不选 session、不重标。
- 有两个 recording day 后，做 leave-one-day-out；报告 day-level 与 session-level 结果，不把窗口当作独立受试者。

主要检验问题是：在标签不再与顺序绑定、且跨日的条件下，模型输出是否仍随预先规定的操作条件变化。若失败，优先审计 day/order/acquisition drift，而不是继续刷同日准确率。

## C2：Motor confound

目标问题：模型是否主要在识别主动手部操作或相关肌电？

已有条件：

- 主动、认真打王者。
- 认真观战王者，减少主动手部操作；当前仅作为 observe prediction-only reference。

后续需要新增“**有手部操作但认知投入低**”的预先定义 control，并尽量固定视觉刺激、姿势和设备条件。该数据尚不存在，不在本路线图中虚构 session、结果或标签。

## C3：Active vs Passive Engagement

比较主动完成任务与被动观看，在尽可能相近的刺激材料和运动条件下检验：模型捕捉的是 `attention to stimulus`，还是 `active task engagement`。

这一层不能只用“认真观战被预测为什么”下结论；需要预先定义主动/被动条件、重复 session 和独立日期，并保留操作检查与主观辅助量。

## C4：Cross-task

在前述主要混杂得到初步约束后，逐步从王者迁移到阅读、学习/做题、coding、网课/视频。每次先增加一个任务族，保留同任务内对照，再检验跨任务预测。

目标不是证明所有任务完全相同，而是判断是否存在跨任务稳定的 engagement signal，并明确哪些成分只在特定 task domain 内成立。

## C5：内部状态

在跨日、顺序、运动和主动/被动等主要混杂排查后，再系统研究 fatigue、sleepiness、mood、stress 与 arousal。

这些状态应被记录并建模，而不是假设能够彻底排除。可先用于 session 分层和失败案例审计；样本量足够后再评估它们是否调节 engagement signal。

## 记录结构

- `session_manifest.csv`：继续保存 session 身份、日期时间、canonical 操作标签、任务描述、数据角色、文件路径、区间和哈希，是原始数据 provenance 的权威来源。
- `control_experiment_log_template.csv`：空白辅助模板，用 `session_id` 关联 manifest，保存预先计划、实际条件、录制顺序及 confound metadata / auxiliary measures。
- 主观 fatigue、sleepiness、mood、arousal 等量不是模型标签真值，也不能用于按结果重标既有 session。
- 模板字段可在真实 protocol 定稿前版本化调整；不得给未发生的 session 填写虚构行。

## 保持冻结的内容

- 既有 `focus` / `unfocus` canonical labels、`observe` reference 和 session-level isolation。
- frozen 2026-09-16 baseline 及其 SHA256：`2b7b97f9f2399bcd3595df63a406fd66adfb470edc7f9390d8d67d45431d8e24`。
- 2026-09-16 first pass 与 historical replay 的原始产物和解释边界。
- 已有 session 不因今天的模型结果或本路线图而重标、重命名或重新训练。
