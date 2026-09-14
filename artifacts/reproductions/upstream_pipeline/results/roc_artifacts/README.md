# 这个目录是什么

这里保存画旧模型 ROC 曲线所需的分数、标签和阈值数组。

## 它属于项目哪一步

Stage 0：原作者方案与数据

前一步：从论文和上游材料开始。
这一步：最初复现的是什么，原方案能否运行？
后一步：能跑作者数据后，需要检查自己的设备和任务录制。

完整故事：[实验阶段地图](../../../../../docs/EXPERIMENT_MAP.md)；名词和模型：[模型字典](../../../../../docs/MODEL_CATALOG.md)。

## 为什么会有这个目录

最初复现的是什么，原方案能否运行？

## 输入从哪里来

data/reference/original_mat/ 的 34 个 MATLAB（MAT，保存数组的文件）与 notebooks/upstream/ 的原作者代码。

## 谁生成这里的文件

notebooks/upstream/；scripts/legacy/ 用于本仓库后续运行的历史复现。

## 这个目录里的文件

| 文件 | 普通人解释 | 手写/生成 | 是否允许修改 |
|---|---|---|---|
| [DT_anova.npz](DT_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [DT_fi.npz](DT_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [DT_lcc.npz](DT_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [DT_pca.npz](DT_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [DT.npz](DT.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_part_detrend_plr_stft_bin_win_anova.npz](googlenet_part_detrend_plr_stft_bin_win_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_part_detrend_plr_stft_bin_win_fi.npz](googlenet_part_detrend_plr_stft_bin_win_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_part_detrend_plr_stft_bin_win_lcc.npz](googlenet_part_detrend_plr_stft_bin_win_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_part_detrend_plr_stft_bin_win_pca.npz](googlenet_part_detrend_plr_stft_bin_win_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_part_detrend_plr_stft_bin_win.npz](googlenet_part_detrend_plr_stft_bin_win.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [KNN_anova.npz](KNN_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [KNN_fi.npz](KNN_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [KNN_lcc.npz](KNN_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [KNN_pca.npz](KNN_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [KNN.npz](KNN.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [LR_anova.npz](LR_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [LR_fi.npz](LR_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [LR_lcc.npz](LR_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [LR_pca.npz](LR_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [LR.npz](LR.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [resnet18_part_detrend_plr_stft_bin_win_anova.npz](resnet18_part_detrend_plr_stft_bin_win_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_part_detrend_plr_stft_bin_win_fi.npz](resnet18_part_detrend_plr_stft_bin_win_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_part_detrend_plr_stft_bin_win_lcc.npz](resnet18_part_detrend_plr_stft_bin_win_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_part_detrend_plr_stft_bin_win_pca.npz](resnet18_part_detrend_plr_stft_bin_win_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_part_detrend_plr_stft_bin_win.npz](resnet18_part_detrend_plr_stft_bin_win.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [RF_anova.npz](RF_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [RF_fi.npz](RF_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [RF_lcc.npz](RF_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [RF_pca.npz](RF_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [RF.npz](RF.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [SVM_anova.npz](SVM_anova.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [SVM_fi.npz](SVM_fi.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [SVM_lcc.npz](SVM_lcc.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [SVM_pca.npz](SVM_pca.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [SVM.npz](SVM.npz) | 历史数组或缓存；必须配原生成流程，不能直接喂给现场模型。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

historical：用于理解早期方案。

## 我什么时候需要看这个目录

需要回答“最初复现的是什么，原方案能否运行？”时查看本目录文件。

## 不要误解

这些是上游历史可视化输入，不是 pooled/personal/mixed 的现场预测；本轮不据此调整阈值。
