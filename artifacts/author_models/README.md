# `author_models/`

这里保存只使用原作者 MATLAB 数据训练的模型，不覆盖 `legacy_baseline_v0` 或 lyc/zyf personal model。两个 author 模型都复用共享预处理、窗口、Welch 特征、StandardScaler、PCA 和 RBF SVC；训练与验证都不读取 LOCKED_TEST。

| 子目录 | 内容 |
|---|---|
| `author_only/` | 23 个有效 author recording 的 author-only pipeline、recording-level GroupKFold 验证和 MAT 结构审计。 |
| `author_common6/` | 同一 23 个 author recording 只取 `F7,F3,P7,O1,O2,P8` 的 common6 pipeline；`AF4` 被主动舍弃，用于与 DSI-24 的探索性跨来源比较。 |
| `README.md` | 本目录边界说明。 |
