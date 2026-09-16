# New Paradigm v1

状态：`CURRENT`。已登记 2026-09-16 lyc focus ×3、unfocus ×3、observe control ×1，并完成单日 6-session leave-one-session-out first pass。session majority 为 6/6，window accuracy 为 98.07%；但录制顺序是 `F-F-F-U-U-U`，标签与 recording order 完全混杂。该结果仅为探索性单日结果，不代表跨日泛化。

## 研究目标

当前核心研究构念是 **task engagement / cognitive engagement（任务认知投入状态）**：人在工作、学习或其他任务中是否持续、主动地投入当前任务，未来以时间轴方式呈现状态变化。

New Paradigm v1 仍保留 `focus` / `unfocus` 作为当前实验操作标签，先采集标准化、平衡、跨 session、跨 recording day 的数据，再通过控制实验判断这些操作标签与更高层 engagement 构念的关系。它不是简单的“游戏专注 / 不专注分类器”，也不直接预测工作效率、正确率或反应速度。

`flow` 目前只作为未来希望研究的高投入状态，不能把当前 `focus` 等同于经过验证的 flow。正确率、反应时间、完成量等未来可以作为 external validation，但不作为 task engagement 的唯一标签定义。

2026-09-14 pilot 显示旧模型对新任务状态定义存在明显失配和 session variation。这个结果只说明需要重新标准化采集；不证明某个心理状态、反馈或 calibration 导致了变化。

## 第一阶段采集原则

- 同一任务条件、同一设备、尽量相同姿势和环境。
- 一个 EDF 只对应一个目标状态。
- 除目标精神状态或任务投入程度外，尽量不改变其他条件。
- 窗口只能作为同一 session 内的样本，不能计作独立 session。
- 采用假设驱动的 control ladder，不做所有变量的全因子排列组合；每一阶段优先攻击一个最大混杂，其余条件尽量固定。

第一轮 pilot 最低目标：

| subject | focus sessions | unfocus sessions |
|---|---:|---:|
| lyc | ≥4 | ≥4 |
| zyf | ≥4 | ≥4 |

正式版本目标：每人 focus ≥6、unfocus ≥6，覆盖至少 2–3 个 recording day。

## 未来模型计划

按以下顺序建立新模型：

1. `lyc-new personal`
2. `zyf-new personal`
3. `new-paradigm pooled`

第一轮训练只允许使用 `data/current/new_paradigm_v1/session_manifest.csv` 中符合资格的 New Paradigm v1 session。不得混入 legacy old data、author data、2026-09-14 LAB_FEEDBACK pilot 或 common6 historical training。

若 new-only 结果成立，再把 `new + old`、`new + author` 作为独立 ablation；不得静默改变主模型训练范围。

## 划分与评估

- 从第一天开始执行 session-level isolation；一个 EDF 的窗口不能跨 split。
- 有多个 recording day 后，优先增加 leave-one-day-out 分析。
- final holdout 必须在任何预测、模型选择、阈值调整之前预先登记并冻结。
- final holdout 从不参与 fit、模型选择、阈值调整或 calibration。

## 当前控制实验优先级

1. **C1 跨日 + 顺序随机化**：下一 recording day 在录制前预先确定交错/随机顺序，例如 `U-F-U-F-F-U`；开始后不得根据模型预测调整。Day 2 在任何预测前冻结，再使用 frozen 2026-09-16 model 做 prediction-only；有两个 recording day 后做 leave-one-day-out。
2. **C2 Motor confound**：已有主动认真打王者与认真观战王者；未来需要预先设计“有手部操作但认知投入低”的 control，不能虚构现有数据。
3. **C3 Active vs Passive Engagement**：比较主动完成任务与被动观看，区分 `attention to stimulus` 和 `active task engagement`。
4. **C4 Cross-task**：逐步从王者迁移到阅读、学习/做题、coding、网课/视频，判断是否存在跨任务稳定信号。
5. **C5 内部状态**：在主要混杂排查后，再系统研究 fatigue、sleepiness、mood、stress、arousal；记录并建模，而非假设可以彻底排除。

完整因素族、记录方式和每层解释边界见 [ENGAGEMENT_CONTROL_ROADMAP](ENGAGEMENT_CONTROL_ROADMAP.md)。当前研究重点由继续提高同日 accuracy 转为 **confound audit + cross-day validation + task engagement construct validation**。

## 保持不变

- 不重命名既有数据，不根据结果重标已有 session。
- `focus` / `unfocus` canonical labels、`observe` reference、historical replay 和 session-level isolation 保持不变。
- frozen 2026-09-16 baseline 不重训、不覆盖；模型 SHA256 为 `2b7b97f9f2399bcd3595df63a406fd66adfb470edc7f9390d8d67d45431d8e24`。
- 下一系统开发方向为 **Attention Dashboard**；系统展示不能先于构念与跨日验证得出过强结论。

## 入口

- 数据目录：[data/current/new_paradigm_v1](../../data/current/new_paradigm_v1/README.md)
- 数据协议：[DATA_PROTOCOL_V2](DATA_PROTOCOL_V2.md)
- 控制实验路线：[ENGAGEMENT_CONTROL_ROADMAP](ENGAGEMENT_CONTROL_ROADMAP.md)
- 当前校验：`scripts/validate_new_paradigm_data.py`
- 未来训练/评估入口预留为 `scripts/train_new_paradigm.py` 和 `scripts/evaluate_new_paradigm.py`；本轮不创建训练实现，继续复用 `eeg_pipeline_utils.py`，不复制预处理/特征管线。
