# 模型字典：这些模型分别学了什么

不知道项目为什么走到这里，先看 [实验阶段地图](EXPERIMENT_MAP.md)。下面所有模型都是已经保存的实验产物；本轮不重新训练。现场默认使用旧pooled、对应personal、mixed-common6。

## 先认识几个词

- EEG：脑电信号；EDF是自采信号文件，MAT是作者数据的数组文件。
- historical candidate：允许用于训练的历史自采候选；最终是否进入fit还要看该实验的划分。
- pooled model：合并多名受试者数据训练的通用模型。
- personal model：只使用一个受试者历史数据训练的模型。
- recording/session：完整录制；session group可把关联的多个EDF放在同一组。
- common6：EDF和MAT可以可靠对应的六个共同EEG通道。
- fit：从数据学习参数；transform：应用已经学好的处理；predict：输出预测。
- LOCKED_TEST：冻结测试数据，只能预测计分，禁止参与fit和调参。
- LAB_FEEDBACK：现场看反馈并调整状态的探索数据，feedback0也属于这一类；不默认训练或最终测试。
- GroupKFold：按完整recording/session分组交叉验证；一组的全部窗口只在同一侧。
- Welch频带特征：把波形转成各频率范围内的能量数字，每通道五个频段×两种能量表示=10个数。
- StandardScaler → PCA → RBF SVC：先按训练统计缩放这些数，再压缩维度，最后分类。
- Accuracy：预测正确的窗口比例；Balanced Accuracy：分别算两类召回率再平均，避免被样本多的类别主导。
- reference：电压测量使用的参考电极；位置对应不等于参考电极一致。

## Existing pooled frozen model

一句话：第一套保存完整处理步骤、供后续实验对照的多人通用模型。

为什么会有它：需要一个能重复预测新EDF的正式起点。 对应 [Stage 2](EXPERIMENT_MAP.md)。

训练数据：legacy_manifest.csv中候选数据按完整组划分后的训练侧，包含lyc、zyf、zqd；不是把全部候选都拟合进去。

没有使用：历史validation侧、LOCKED_TEST、LAB_FEEDBACK。

输入通道：完整24个EEG通道，保持EDF原顺序。

特征：24 × 10 = 240维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：个人模型或author模型微调，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/legacy_baseline_v0/](../artifacts/legacy_baseline_v0/README.md)。

训练入口：`scripts/legacy_baseline_v0.py`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：现场与研究的固定参考。

当前结果：历史validation Acc69.99% / Bal69.64%；LOCKED_TEST lyc65.54% /64.28%，zyf46.11% /57.69%。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## lyc personal

一句话：只用lyc历史数据训练的个人模型。

为什么会有它：检验消除跨人差异是否能改善新录制预测。 对应 [Stage 4](EXPERIMENT_MAP.md)。

训练数据：lyc：19个EDF、12个session group，6741个窗口。

没有使用：zyf、zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

输入通道：完整24个EEG通道。

特征：24 × 10 = 240维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：新用户微调或模型校准，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/subject_models/lyc/](../artifacts/subject_models/lyc/README.md)。

训练入口：`scripts/train_subject_models.py`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：lyc现场与旧pooled/mixed对照。

当前结果：LOCKED_TEST lyc Acc46.68% / Bal47.67%；zyf67.94% /51.80%，后者预测focus98.57%，存在明显偏向。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## zyf personal

一句话：只用zyf历史数据训练的个人模型。

为什么会有它：检验同一个人的历史数据是否足够应付新的录制条件。 对应 [Stage 4](EXPERIMENT_MAP.md)。

训练数据：zyf：12个EDF、7个session group，4483个窗口。

没有使用：lyc、zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

输入通道：完整24个EEG通道。

特征：24 × 10 = 240维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：新用户微调或模型校准，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/subject_models/zyf/](../artifacts/subject_models/zyf/README.md)。

训练入口：`scripts/train_subject_models.py`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：zyf现场与旧pooled/mixed对照。

当前结果：LOCKED_TEST lyc Acc45.79% / Bal56.45%；zyf41.35% /52.14%。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## author-only-7ch

一句话：只使用原作者23个MAT录制、保留七通道的模型。

为什么会有它：检查作者数据在完整录制隔离后是否仍能区分两类。 对应 [Stage 6](EXPERIMENT_MAP.md)。

训练数据：作者recordings 3–7、10–14、17–21、24–27、31–34；共13754窗口。

没有使用：任何自采训练数据、LOCKED_TEST、LAB_FEEDBACK；未选中的11个MAT。

输入通道：F7,F3,P7,O1,O2,P8,AF4。

特征：7 × 10 = 70维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：个人模型或author模型微调，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/author_models/author_only/](../artifacts/author_models/author_only/README.md)。

训练入口：`scripts/train_cross_source_models.py --model author-only`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：保留作者数据内部基线；不作默认现场模型。

当前结果：5-fold GroupKFold Acc/Bal均64.12% ±4.37%；未进行正式七通道跨EDF比较。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## author-common6

一句话：只用作者23个录制、去掉AF4后训练的六通道模型。

为什么会有它：比较去掉AF4的影响，并检查作者模型直接预测自采数据的表现。 对应 [Stage 7](EXPERIMENT_MAP.md)。

训练数据：与author-only-7ch相同23个MAT录制、13754窗口。

没有使用：自采历史数据、zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

输入通道：F7,F3,P7,O1,O2,P8。

特征：6 × 10 = 60维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：个人模型或author模型微调，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/author_models/author_common6/](../artifacts/author_models/author_common6/README.md)。

训练入口：`scripts/train_cross_source_models.py --model author-common6`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：作者内部通道对照和跨来源研究，不默认显示在现场界面。

当前结果：GroupKFold Acc/Bal均64.69% ±4.29%；LOCKED_TEST lyc37.56% /50.00%，zyf33.17% /50.00%，全部预测unfocus。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## our-common6

一句话：只用lyc与zyf历史数据、限制为六个共同通道的通用模型。

为什么会有它：给mixed提供相同输入通道数的对照，避免混淆增加数据与更换通道。 对应 [Stage 7](EXPERIMENT_MAP.md)。

训练数据：lyc+zyf历史候选：31个EDF、19组、11224窗口。

没有使用：作者数据、zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

输入通道：F7,F3,P7/T5,O1,O2,P8/T6。

特征：6 × 10 = 60维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：个人模型或author模型微调，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/our_common6_models/pooled_common6/](../artifacts/our_common6_models/pooled_common6/README.md)。

训练入口：`scripts/train_cross_source_models.py --model our-common6`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：研究用同通道对照，不作为默认现场展示。

当前结果：GroupKFold Acc69.83% ±6.98%，Bal69.51% ±7.21%；LOCKED_TEST lyc44.46% /48.29%，zyf36.03% /46.78%。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## mixed-common6

一句话：把我们的lyc/zyf历史数据与原作者23个录制合起来，只使用双方能可靠对应的六个通道训练的通用SVC模型。

为什么会有它：测试增加跨来源、跨录制的训练数据多样性，是否与新session泛化改善相关。 对应 [Stage 7](EXPERIMENT_MAP.md)。

训练数据：lyc历史候选 + zyf历史候选 + author23个MAT recording；共42组、24978窗口。

没有使用：zqd、未知身份、LOCKED_TEST、LAB_FEEDBACK。

输入通道：F7,F3,P7/T5,O1,O2,P8/T6。

特征：6 × 10 = 60维 Welch频带特征；128 Hz、0.5–43 Hz滤波、4秒窗/2秒步长。

模型：StandardScaler → PCA(保留95%方差) → RBF SVC(C=10, class_weight=balanced)。这些参数已固定。

它不是：个人模型或author模型微调，也不是用LOCKED_TEST学习的模型。SVC沿用历史probability配置；QuickTest只调用predict，不新增校准步骤。

产物位置：[artifacts/mixed_models/our_author_mixed_common6/](../artifacts/mixed_models/our_author_mixed_common6/README.md)。

训练入口：`scripts/train_cross_source_models.py --model mixed-common6`；这里只标出可追溯入口，不要求新人执行训练。

目前用途：研究跨录制/跨来源泛化；现场QuickTest的第三个代表模型。

当前结果：GroupKFold Acc67.19% ±3.27%，Bal67.31% ±3.26%；LOCKED_TEST lyc47.48% /52.68%，zyf51.03% /55.77%。相对our-common6 Bal增加4.39/8.99个百分点。 此处 Acc/Bal为Accuracy/Balanced Accuracy，±表示五折标准差，不是置信区间。

## 为什么 common7 曾被 blocked

blocked（阻塞）表示当时未满足输入条件，没有生成模型。旧common7 adapter未采用T5/T6别名且要求AF4，所以当时记录P7/P8/AF4缺失。后来依据权威命名与DSI-24设备证据确认T5↔P7、T6↔P8，并主动去掉AF4，形成新的common6路径；旧七通道尝试只保留历史记录。

## 跨来源和现场结论的限制

Our reference=Pz confirmed；author MAT reference=unknown。跨来源结果统一为 exploratory / channel-aligned but reference compatibility uncertain。差异可能反映受试者、session、设备、任务、预处理表示和未解决的作者reference差异。

在当前实际数据表示下，加入跨来源training recordings与更好的LOCKED_TEST泛化相关。mixed尚未在Balanced Accuracy上超过原pooled。不能把author-common6全部预测unfocus直接解释为作者数据无效。

QuickTest按全文件计分，不使用正式LOCKED_TEST清单的活动区间；即使用同一个EDF也可能得到不同分数。文件名标签只表示预期状态，单个同标签EDF的Accuracy等于目标类预测比例。现场前后变化不等于正式泛化改善。
