# 实验阶段地图：项目为什么一步步走到这里

第一次阅读请按顺序看；查模型用 [MODEL_CATALOG.md](MODEL_CATALOG.md)，查路径用 [REPOSITORY_FILE_GUIDE.md](REPOSITORY_FILE_GUIDE.md)。这里记录既有实验，本轮只改文档和现场推理，不重训、不更新正式分数。

Accuracy（准确率）是所有窗口中预测正确的比例；Balanced Accuracy（平衡准确率）是分别算focus/unfocus召回率再平均，避免样本多的一类掩盖另一类。窗口是从长录制截取的4秒片段；相邻窗口会重叠，不能视为独立受试者。

## Stage 0：原作者方案与数据

研究问题：最初复现的是什么，原方案能否运行？

输入数据：data/reference/original_mat/ 的 34 个 MATLAB（MAT，保存数组的文件）与 notebooks/upstream/ 的原作者代码。

使用脚本：notebooks/upstream/；scripts/legacy/ 用于本仓库后续运行的历史复现。

输出目录：artifacts/upstream_author/ 保存上游原有结果；artifacts/reproductions/upstream_pipeline/ 保存我们运行后得到的数组、权重和结果。

关键模型：原作者分类器与历史深度模型；不是今天 QuickTest 的模型。

关键结论：确认方案与数据来源。历史随机窗口分数不能当作新录制泛化成绩。

下一步为什么出现：能跑作者数据后，需要检查自己的设备和任务录制。

## Stage 1：早期自采 EEG 探索

研究问题：模型在自己的数据上能否区分专注和不专注？为什么以前分数很高？

输入数据：data/legacy/multiclass_10min/ 和 data/legacy/mixed_20min/：39 个 EDF（脑电信号文件）。CSV/DSI 是设备配套导出。

使用脚本：notebooks/legacy/self_recorded/；scripts/validate_legacy_manifest.py 核对后续建立的清单。

输出目录：artifacts/legacy/notebook_outputs/；data/legacy_manifest.csv 登记标签、身份、区间与来源。

关键模型：早期多分类和二分类探索模型。

关键结论：同一录制切成的相邻窗口很相似，随机分配窗口可能让模型在测试中见到熟悉的录制条件，分数虚高。旧单状态 iu/ou 归为 unfocus，daze 只作静息参考；旧 mixed 前10分钟 unfocus、后10分钟 focus。

下一步为什么出现：需要按完整录制隔离、并能保存全套处理步骤的正式基线。

## Stage 2：Legacy pooled baseline

研究问题：怎样得到第一个可以保存、复查并重复预测的正式模型？

输入数据：data/legacy_manifest.csv 批准的历史候选：按 session group（一次或一组关联录制）划分后，只有 train 侧进入拟合。旧 pooled 范围包含 zqd；后来的 personal/common6 才排除 zqd。

使用脚本：scripts/legacy_baseline_v0.py；scripts/eeg_pipeline_utils.py。复查只用 --check-existing，不运行训练入口。

输出目录：artifacts/legacy_baseline_v0/：模型、训练/验证划分、配置、预测和冻结哈希。

关键模型：Existing pooled frozen：把多名受试者的历史训练数据合起来训练的通用模型。

关键结论：历史验证 Accuracy 69.99%、Balanced Accuracy 69.64%。保存 StandardScaler（缩放特征）→ PCA（压缩特征）→ SVC（分类）全链，避免丢失训练时的处理状态。

下一步为什么出现：历史验证不错，不代表新的独立录制也能达到同样效果。

## Stage 3：独立 LOCKED_TEST

研究问题：面对从未参与训练的新录制，旧模型表现如何？

输入数据：data/locked/2026-09-07/：lyc/zyf 各3段二分类录制，共2389个正式窗口；另1段静息参考。

使用脚本：scripts/validate_locked_data.py；scripts/evaluate_locked_test.py。

输出目录：artifacts/locked_test/2026-09-07/；标签、有效区间和哈希见 data/session_manifest.csv。

关键模型：Existing pooled frozen。

关键结论：LOCKED_TEST（冻结测试数据，只能预测，不能参与任何 fit，即学习参数）首轮总 Accuracy 55.30%、Balanced Accuracy 59.91%，明显低于历史验证。按整个 EDF/session 隔离，防止同一次录制的窗口跨集合。

下一步为什么出现：怀疑不同人的差异影响模型，于是检验个人模型。

## Stage 4：lyc / zyf personal models

研究问题：只用同一个人的历史数据训练，会不会更适合这个人？

输入数据：lyc 的19个历史EDF/12组、zyf 的12个历史EDF/7组；各自只用自己的历史候选。

使用脚本：scripts/train_subject_models.py 生成已保存模型；scripts/evaluate_subject_models.py 比较三个已训练模型。

输出目录：artifacts/subject_models/；artifacts/subject_model_comparison/2026-09-07/。

关键模型：lyc personal、zyf personal（只使用一个人历史数据训练的模型），另以旧 pooled 对照。

关键结论：个人模型未稳定优于 pooled：lyc personal→lyc Balanced Accuracy 47.67%，zyf personal→zyf 52.14%。lyc personal→zyf Accuracy 67.94% 看似高，但 Balanced Accuracy 仅51.80%。

下一步为什么出现：不能只看一个准确率，需要检查预测偏向、类别比例和不同录制。

## Stage 5：Personal diagnosis

研究问题：个人模型为什么在历史留出录制约75%，新录制却接近50%？

输入数据：原历史候选与已保存的 personal/LOCKED_TEST 预测文件。

使用脚本：scripts/diagnose_subject_models.py（历史诊断会训练各折，本轮不执行）；测试侧只统计已有预测。

输出目录：artifacts/subject_model_diagnostics/2026-09-07/。

关键模型：旧 pooled 与两个人模型；诊断折模型不是新增正式现场模型。

关键结论：lyc personal→zyf 把98.57%的窗口预测为 focus，说明较高 Accuracy 主要来自类别偏向。历史按组留一的 Balanced Accuracy 约75%只汇总含两类的有效折；不是所有折都可计算。结果支持 session/domain shift（新录制条件/数据分布变化）的嫌疑，尚不能证明单一原因。

下一步为什么出现：增加不同录制来源可能有帮助，因此检查作者数据是否可分并能否共同训练。

## Stage 6：Author-only model

研究问题：按完整录制隔离后，原作者数据本身还有可分性吗？

输入数据：沿用上游选择的23个 author MAT recording（完整录制）：3–7、10–14、17–21、24–27、31–34；每段前600秒focus，后600秒unfocus。

使用脚本：scripts/cross_source_utils.py；scripts/train_cross_source_models.py --model author-only（已运行，本轮不重训）。

输出目录：artifacts/author_models/author_only/。

关键模型：author-only-7ch：只用作者数据、七通道训练的模型。

关键结论：GroupKFold（按完整 recording/session 分组交叉验证）Accuracy / Balanced Accuracy 都为64.12% ±4.37%。仍有可分性；它使用共享Welch方法，不是对上游STFT流程的逐行复现。

下一步为什么出现：作者与自采通道不同，必须先选可可靠对应的共同通道。

## Stage 7：Common6 通道对齐与 Mixed

研究问题：在相同六通道输入下，加入作者训练数据能否改善新录制表现？

输入数据：common6（我们的EDF与作者MAT都能可靠对应的六个EEG通道）：F7,F3,P7,O1,O2,P8。T5/T6依据设备和命名证据对应P7/P8；舍弃AF4。

使用脚本：scripts/verify_common6_compatibility.py；scripts/train_cross_source_models.py 的 author-common6 / our-common6 / mixed-common6；scripts/evaluate_cross_source_models.py --channel-set common6。

输出目录：artifacts/common6_compatibility/；artifacts/author_models/author_common6/；artifacts/our_common6_models/；artifacts/mixed_models/our_author_mixed_common6/；artifacts/cross_source_comparison/2026-09-14/。

关键模型：author-common6（仅作者）、our-common6（仅lyc/zyf历史）、mixed-common6（两种来源合并）。

关键结论：mixed 相比 our 在lyc/zyf LOCKED_TEST Balanced Accuracy增加4.39/8.99个百分点，分别为52.68%/55.77%；仍未超过旧pooled的64.28%/57.69%。Our reference（电压参考电极）=Pz已确认，作者reference未知，跨来源结论保持 exploratory / channel-aligned but reference compatibility uncertain。

下一步为什么出现：现场用三种代表模型看反馈方向，再规划未来不看反馈的新最终留出集。

## Stage 8：LAB_FEEDBACK exploratory recording

研究问题：人看到模型反馈后主动调整状态，多个模型预测方向会不会一致变化？

输入数据：真实录制返回后放 data/exploratory/lab_feedback/2026-09-14/；当前只建规则，未登记任何新EEG。

使用脚本：notebooks/lab_quick_test_legacy_model.ipynb；scripts/subject_model_utils.py 的 run_quick_test / compare_quick_tests。

输出目录：QuickTest结果默认只在内存；未来探索结果另存并登记模型/输入哈希，不能覆盖正式实验结果。

关键模型：旧 pooled + 对应 personal + mixed-common6；zqd/unknown 跳过 personal。

关键结论：LAB_FEEDBACK（现场看模型反馈后调整状态的探索实验）包含feedback0及后续轮次；全部默认禁止训练和最终测试。只报告描述性前后变化，不作为因果证明。

下一步为什么出现：将来预先规定任务和评估方案，再收集不看反馈、从未用于调参的新 final holdout（最终留出集）；当前旧测试已被多次查看，不可再次声称全新盲测。

## 项目结论的边界

Cross-source differences may reflect subject, session, device, task/paradigm, preprocessing representation, and unresolved author-reference differences.

在当前实际数据表示下，加入跨来源 training recordings 与更好的 LOCKED_TEST 泛化相关；不构成单一原因的归因。术语与模型详见 [模型字典](MODEL_CATALOG.md)。历史阻塞快照在 [兼容性审计](../artifacts/common6_compatibility/2026-09-14/README.md)，原实验报告不改写。
