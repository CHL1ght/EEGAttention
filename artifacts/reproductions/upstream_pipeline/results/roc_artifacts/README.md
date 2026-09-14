# 上游 ROC 数值缓存

这里的 `.npz` 文件按模型/特征变体保存 ROC 曲线所需的 score、label 或阈值数组。文件族包括 `DT`、`KNN`、`LR`、`RF`、`SVM`、`googlenet_part_detrend_plr_stft_bin_win` 和 `resnet18_part_detrend_plr_stft_bin_win`，每个族可能有无后缀、`anova`、`fi`、`lcc`、`pca` 版本。

它们是上游历史可视化输入，不是当前 pooled/personal 模型输出；当前结果请看 `artifacts/subject_model_comparison/`。
