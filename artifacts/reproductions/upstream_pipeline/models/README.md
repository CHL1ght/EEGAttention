# 上游深度模型权重

文件名格式为：`{network}_model_part_detrend_plr_stft_bin_win{feature_variant}.pth`。

| 文件族 | 含义 |
|---|---|
| `googlenet_model_part_detrend_plr_stft_bin_win.pth` | GoogLeNet，无额外特征筛选。 |
| `googlenet_model_part_detrend_plr_stft_bin_win_anova.pth` | GoogLeNet + ANOVA。 |
| `googlenet_model_part_detrend_plr_stft_bin_win_fi.pth` | GoogLeNet + feature importance。 |
| `googlenet_model_part_detrend_plr_stft_bin_win_lcc.pth` | GoogLeNet + LCC。 |
| `googlenet_model_part_detrend_plr_stft_bin_win_pca.pth` | GoogLeNet + PCA。 |
| `resnet18_model_part_detrend_plr_stft_bin_win.pth` | ResNet18，无额外特征筛选。 |
| `resnet18_model_part_detrend_plr_stft_bin_win_anova.pth` | ResNet18 + ANOVA。 |
| `resnet18_model_part_detrend_plr_stft_bin_win_fi.pth` | ResNet18 + feature importance。 |
| `resnet18_model_part_detrend_plr_stft_bin_win_lcc.pth` | ResNet18 + LCC。 |
| `resnet18_model_part_detrend_plr_stft_bin_win_pca.pth` | ResNet18 + PCA。 |

`.pth` 是 PyTorch 权重，不是当前 sklearn 的 `pipeline.joblib`；由 `validate_reproduction_models.py` 做完整性检查。
