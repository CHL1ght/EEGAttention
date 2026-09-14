# EEGAttention：从脑电波到现场反馈

## 30 秒看懂这个项目

我们想通过EEG（脑电信号）区分focus（专注）与unfocus（不专注）。先复现原作者方案，再用自己的EDF脑电文件训练模型；后来发现，把同一次录制的小片段随机分到训练和测试会让成绩虚高，于是改为按完整录制隔离，并封存独立测试数据。之后又检验个人模型和作者数据，当前最大的困难是换一次录制或换一种数据来源后，模型表现变差。

今天现场用几个已经训练好的模型观察反馈：先录一段，看结果，主动调整状态，再录一段比较。这个先导实验叫LAB_FEEDBACK（现场反馈探索），不是最终模型考试。

## 项目发展路线图

```text
原作者方案/数据
  ↓ 早期自采EEG探索
  ↓ Legacy pooled baseline（第一个冻结的多人通用模型）
  ↓ 独立LOCKED_TEST（只预测、禁止学习参数的测试数据）
  ↓ lyc / zyf personal models（各自只用自己的历史数据）
  ↓ Personal diagnosis（检查为什么个人模型没有稳定改善）
  ↓ Author-only model（单独检验作者数据）
  ↓ Common6通道对齐（双方都能可靠对应的六个测量位置）
  ↓ Our-common6 / Author-common6 / Mixed-common6（自采/作者/合并训练）
  ↓ 现场LAB_FEEDBACK QuickTest（已有模型的反馈与前后比较）
  ↓ 未来新的真正final holdout（事先封存且不看反馈的最终留出集）
```

下表连接每一步的问题、数据、结果与路径。详细故事见 [实验阶段地图](docs/EXPERIMENT_MAP.md)。脚本是来源索引，不是要求按顺序重新训练。

| 阶段与为什么做 | 数据 | 已得到的结论 | 脚本/入口 | 产物位置 |
|---|---|---|---|---|
| 0 原作者：先弄懂和复现方案 | 作者MAT | 保留来源与历史结果 | notebooks/upstream/ | artifacts/upstream_author/；artifacts/reproductions/ |
| 1 早期自采：检查自己的数据 | legacy EDF | 随机窗口高分不等于新录制泛化 | notebooks/legacy/self_recorded/ | artifacts/legacy/notebook_outputs/ |
| 2 正式基线：保存可重复模型 | 按组划分后的历史训练数据 | 历史验证准确率69.99% | scripts/legacy_baseline_v0.py | artifacts/legacy_baseline_v0/ |
| 3 独立测试：检验新录制 | 2026-09-07封存EDF | 总准确率降至55.30% | scripts/evaluate_locked_test.py | artifacts/locked_test/2026-09-07/ |
| 4 个人模型：检验同人训练 | lyc/zyf各自历史数据 | 未稳定胜过原通用模型 | scripts/train_subject_models.py；scripts/evaluate_subject_models.py | artifacts/subject_models/；artifacts/subject_model_comparison/ |
| 5 个人诊断：追查失败 | 历史数据与已有预测 | 预测偏向和录制条件变化值得关注 | scripts/diagnose_subject_models.py | artifacts/subject_model_diagnostics/ |
| 6 作者模型：检查作者内部可分性 | 23个作者MAT录制 | 七通道按录制验证约64.12% | scripts/train_cross_source_models.py | artifacts/author_models/author_only/ |
| 7 六通道：比较是否加入作者数据 | lyc/zyf历史 + 作者23段 | 混合模型相对自采六通道对照有改善 | scripts/cross_source_utils.py；scripts/train_cross_source_models.py；scripts/evaluate_cross_source_models.py | artifacts/common6_compatibility/；artifacts/author_models/author_common6/；artifacts/our_common6_models/；artifacts/mixed_models/；artifacts/cross_source_comparison/2026-09-14/ |
| 8 现场反馈：比较主动调整前后 | 真实数据回来后归入lab_feedback | 当前只建立入口/规则，尚无今天的新实验结论 | notebooks/lab_quick_test_legacy_model.ipynb | 结果默认只在内存；data/exploratory/lab_feedback/2026-09-14/为原始录制归档 |
| 未来最终留出：独立检验 | 未来事先规划的新数据 | 尚未开始 | 未来方案明确后登记 | 不将feedback数据直接改名成locked |

## 我从哪里开始

- 想知道为什么做这些实验 → [EXPERIMENT_MAP.md](docs/EXPERIMENT_MAP.md)。
- 不知道某个模型是什么 → [MODEL_CATALOG.md](docs/MODEL_CATALOG.md)，含术语解释。
- 想查某个文件路径 → [REPOSITORY_FILE_GUIDE.md](docs/REPOSITORY_FILE_GUIDE.md)。
- 今天要录制和看反馈 → [LAB_FEEDBACK规则](data/exploratory/lab_feedback/README.md)、[今天的目录](data/exploratory/lab_feedback/2026-09-14/README.md)、[QuickTest Notebook](notebooks/lab_quick_test_legacy_model.ipynb)。

## 现场怎么操作

在已有EEG Python环境中，从仓库根目录或notebooks目录打开QuickTest。第一段填EDF_PATH执行单文件模式；第二段填EDF_PATH_BEFORE / EDF_PATH_AFTER执行前后模式。lyc/zyf默认运行旧通用模型、本人模型、mixed-common6；zqd/unknown跳过个人模型。

pooled/personal使用完整24通道的240维特征；mixed-common6使用六通道的60维特征，两路都复用共享处理函数。文件名标签只用于计分。标签不同或身份不同/未知时不算改善差值。

今天命名例：`lyc_focus_202609141630_feedback0.edf` → `lyc_focus_202609141650_feedback1.edf`。同一次录制的EDF/CSV/DSI保持同一stem，放入`data/exploratory/lab_feedback/2026-09-14/`。包括feedback0在内都默认不训练、不作为最终测试；实际metadata等数据回来再填写。

## 目前结果怎么读

Balanced Accuracy（平衡准确率）分别算两类召回率后平均，避免被样本较多的一类主导。既有正式测试结果：

| 模型 | lyc平衡准确率 | zyf平衡准确率 |
|---|---:|---:|
| 原通用冻结模型 | 64.28% | 57.69% |
| lyc个人模型 | 47.67% | 51.80% |
| zyf个人模型 | 56.45% | 52.14% |
| 只用作者六通道 | 50.00% | 50.00% |
| 只用自采六通道 | 48.29% | 46.78% |
| 合并来源六通道 | 52.68% | 55.77% |

mixed相对our-common6提高4.39/8.99个百分点，但尚未超过原通用模型。Our reference（电压参考电极）=Pz；作者reference未知，通道对齐不意味着参考一致。结果仅作exploratory / channel-aligned but reference compatibility uncertain。完整既有结果见[比较报告](artifacts/cross_source_comparison/2026-09-14/REPORT.md)。

## 文件与数据边界

代码在[scripts/](scripts/README.md)，交互入口在[notebooks/](notebooks/README.md)，原始数据在[data/](data/README.md)，实验产物在[artifacts/](artifacts/README.md)，文档在[docs/](docs/README.md)，未来服务原型在[system/](system/README.md)。每个目录README都说明其阶段、来源和用途。

LOCKED_TEST只可预测、计分，不可fit（学习参数）、调参或挑选模型。现场feedback数据不能靠改文件名变成独立测试。旧模型、原始信号及历史报告保留原样；未来真正最终留出集需要重新规划。

## 只读验收

```powershell
python scripts/validate_legacy_manifest.py
python scripts/validate_locked_data.py
python scripts/validate_reproduction_models.py
python scripts/validate_quick_test.py
git diff --check
```

当前本机可使用 `C:\CHLight\1-Workconfig\Miniconda\envs\EEG\python.exe`。训练命令仅供查来源，不属于本轮验收。进度历史见[docs/progress/](docs/progress/README.md)。

## 上游参考

Wang, J.; Kim, S.-K. *Novel Machine Learning-Based Brain Attention Detection Systems*. Information 2025, 16, 25。

Aci, C.I.; Kaya, M.; Mishchenko, Y. *Distinguishing mental attention states of humans via an EEG-based passive BCI using machine learning methods*. Expert Systems with Applications 2019, 134, 153–166。
