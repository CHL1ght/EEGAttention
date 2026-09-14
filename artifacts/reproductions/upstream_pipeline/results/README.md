# 上游复现结果

本目录包含上游深度模型的训练表、ROC 图片和 ROC 数值缓存。

| 文件族 | 含义 |
|---|---|
| `train_info_googlenet_*.xlsx` | GoogLeNet 在不同特征变体上的训练/评估表。 |
| `train_info_resnet18_*.xlsx` | ResNet18 在不同特征变体上的训练/评估表。 |
| `train_info_group_*.xlsx` | 上游 group 版本的训练/评估表。 |
| `roc_*.png` | 不同特征处理方式的 ROC 图片。 |
| `roc_artifacts/` | 与 ROC 图片对应的数值缓存。 |
| `progress/` | 深度 worker 的日志和 JSON 摘要。 |

其中的 `anova/fi/lcc/pca` 是上游特征处理变体，不等同于当前 legacy baseline 的 PCA pipeline。
