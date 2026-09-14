# 这个目录是什么

这里是旧上游深度网络训练得到的权重文件，不是现场 QuickTest 使用的模型。

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
| [googlenet_model_part_detrend_plr_stft_bin_win_anova.pth](googlenet_model_part_detrend_plr_stft_bin_win_anova.pth) | GoogLeNet + ANOVA。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_model_part_detrend_plr_stft_bin_win_fi.pth](googlenet_model_part_detrend_plr_stft_bin_win_fi.pth) | GoogLeNet + feature importance。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_model_part_detrend_plr_stft_bin_win_lcc.pth](googlenet_model_part_detrend_plr_stft_bin_win_lcc.pth) | GoogLeNet + LCC。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_model_part_detrend_plr_stft_bin_win_pca.pth](googlenet_model_part_detrend_plr_stft_bin_win_pca.pth) | GoogLeNet + PCA。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [googlenet_model_part_detrend_plr_stft_bin_win.pth](googlenet_model_part_detrend_plr_stft_bin_win.pth) | GoogLeNet，无额外特征筛选。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [README.md](README.md) | 本目录为什么存在、属于哪一步，以及各文件怎么看。 | 手写维护 | 可维护，保留来源与实验边界 |
| [resnet18_model_part_detrend_plr_stft_bin_win_anova.pth](resnet18_model_part_detrend_plr_stft_bin_win_anova.pth) | ResNet18 + ANOVA。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_model_part_detrend_plr_stft_bin_win_fi.pth](resnet18_model_part_detrend_plr_stft_bin_win_fi.pth) | ResNet18 + feature importance。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_model_part_detrend_plr_stft_bin_win_lcc.pth](resnet18_model_part_detrend_plr_stft_bin_win_lcc.pth) | ResNet18 + LCC。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_model_part_detrend_plr_stft_bin_win_pca.pth](resnet18_model_part_detrend_plr_stft_bin_win_pca.pth) | ResNet18 + PCA。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |
| [resnet18_model_part_detrend_plr_stft_bin_win.pth](resnet18_model_part_detrend_plr_stft_bin_win.pth) | ResNet18，无额外特征筛选。 | 采集或程序生成 | 不就地覆盖；需另存版本并留痕 |

## 当前状态

historical：用于理解早期方案。

## 我什么时候需要看这个目录

需要回答“最初复现的是什么，原方案能否运行？”时查看本目录文件。

## 不要误解

.pth 是 PyTorch 权重，不是 sklearn 的 pipeline.joblib；完整性由 scripts/validate_reproduction_models.py 检查。
