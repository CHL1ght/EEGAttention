# EEGAttention 两个 Notebook 读法速记

## 先看哪个？
1. `EEG_train_22_20250226_annotated_CN.ipynb`：训练主流程，负责从原始 EEG 数据一路训练模型并导出结果。
2. `EEG_train_12_result_visualization_20250104_annotated_CN.ipynb`：结果汇总与可视化，负责读取第一个 notebook 生成的 Excel 表。

## 主流程一句话
原始 `.mat` EEG 数据 → 选 7 个通道 → 分成 focus/unfocus → 去基线漂移 → 0.2~43Hz 滤波 → STFT → 0~18Hz 分成 36 个频率 bin → 15 秒滑窗 → 7×36=252 维特征 → 训练模型 → 保存结果。

## 标签含义
- `focus = 1`
- `unfocus = 0`

## 模型分两类
- 传统机器学习：Decision Tree、Random Forest、KNN、Logistic Regression、SVM。
- 深度学习：ResNet-18、GoogLeNet。这里不是直接处理 EEG 图，而是把 252 维特征强行变成“伪图像”喂给预训练 CNN。

## 特征选择/降维方法
- `N/A`：不用降维。
- `ANOVA`：按 p 值筛特征。
- `Feat. Imp.`：按随机森林特征重要性筛特征。
- `LCC`：按特征和标签的 Pearson 相关系数筛特征。
- `PCA`：主成分降维。

## 最容易报错的地方
- `./originaldata/xxx.mat` 路径不对。
- `./result/` 或 `./model/` 文件夹不存在。
- `BaselineRemoval` 没装。
- `sklearnex` 没装，可以先注释掉相关两行。
- PyTorch/CUDA 版本不匹配。
- `pretrained=True` 可能联网下载模型权重。
