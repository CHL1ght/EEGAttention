# 这个目录是什么

这里记录我们运行旧上游深度模型得到的成绩表和曲线，不是作者自带的原始成绩。

## 它属于项目哪一步

Stage 0：原作者方案与数据

前一步：从论文和上游材料开始。
这一步：最初复现的是什么，原方案能否运行？
后一步：能跑作者数据后，需要检查自己的设备和任务录制。

完整故事：[实验阶段地图](../../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

最初复现的是什么，原方案能否运行？

## 输入从哪里来

data/reference/original_mat/ 的 34 个 MATLAB（MAT，保存数组的文件）与 notebooks/upstream/ 的原作者代码。

## 谁生成这里的文件

notebooks/upstream/；scripts/legacy/ 用于本仓库后续运行的历史复现。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [progress/](progress/README.md) | 这里保留旧上游复现任务的运行进度日志，供排查当时哪些任务完成。 | 目录 | 按子目录规则 |
| [roc_artifacts/](roc_artifacts/README.md) | 这里保存画旧模型 ROC 曲线所需的分数、标签和阈值数组。 | 目录 | 按子目录规则 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [roc_anova.png](roc_anova.png) | 历史结果或方案说明图片，不是模型输入。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [roc_feature_importance.png](roc_feature_importance.png) | 历史结果或方案说明图片，不是模型输入。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [roc_lcc.png](roc_lcc.png) | 历史结果或方案说明图片，不是模型输入。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [roc_pca.png](roc_pca.png) | 历史结果或方案说明图片，不是模型输入。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [roc_without_feature_reduction.png](roc_without_feature_reduction.png) | 历史结果或方案说明图片，不是模型输入。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_googlenet_part_detrend_plr_stft_bin_win_anova.xlsx](train_info_googlenet_part_detrend_plr_stft_bin_win_anova.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_googlenet_part_detrend_plr_stft_bin_win_fi.xlsx](train_info_googlenet_part_detrend_plr_stft_bin_win_fi.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_googlenet_part_detrend_plr_stft_bin_win_lcc.xlsx](train_info_googlenet_part_detrend_plr_stft_bin_win_lcc.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_googlenet_part_detrend_plr_stft_bin_win_pca.xlsx](train_info_googlenet_part_detrend_plr_stft_bin_win_pca.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_googlenet_part_detrend_plr_stft_bin_win.xlsx](train_info_googlenet_part_detrend_plr_stft_bin_win.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_group_part_detrend_plr_stft_bin_win_anova.xlsx](train_info_group_part_detrend_plr_stft_bin_win_anova.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_group_part_detrend_plr_stft_bin_win_fi.xlsx](train_info_group_part_detrend_plr_stft_bin_win_fi.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_group_part_detrend_plr_stft_bin_win_lcc.xlsx](train_info_group_part_detrend_plr_stft_bin_win_lcc.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_group_part_detrend_plr_stft_bin_win_pca.xlsx](train_info_group_part_detrend_plr_stft_bin_win_pca.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_group_part_detrend_plr_stft_bin_win.xlsx](train_info_group_part_detrend_plr_stft_bin_win.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_resnet18_part_detrend_plr_stft_bin_win_anova.xlsx](train_info_resnet18_part_detrend_plr_stft_bin_win_anova.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_resnet18_part_detrend_plr_stft_bin_win_fi.xlsx](train_info_resnet18_part_detrend_plr_stft_bin_win_fi.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_resnet18_part_detrend_plr_stft_bin_win_lcc.xlsx](train_info_resnet18_part_detrend_plr_stft_bin_win_lcc.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_resnet18_part_detrend_plr_stft_bin_win_pca.xlsx](train_info_resnet18_part_detrend_plr_stft_bin_win_pca.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [train_info_resnet18_part_detrend_plr_stft_bin_win.xlsx](train_info_resnet18_part_detrend_plr_stft_bin_win.xlsx) | 历史实验导出的表格，仅作来源追溯或结构查看。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

historical：用于理解早期方案。

## 我什么时候需要看这个目录

需要回答“最初复现的是什么，原方案能否运行？”时查看本目录文件。

## 不要误解

anova/fi/lcc/pca 是上游特征处理变体，不等同于当前冻结的 Scaler→PCA→SVC 链。
