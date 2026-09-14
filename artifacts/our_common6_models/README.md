# `artifacts/our_common6_models/`

本目录保存只使用我们自己的历史 EDF、且按已确认 nomenclature adapter 对齐到 common6 的模型。训练数据只来自明确身份的 `lyc` 与 `zyf` historical candidate；`zqd`、unknown identity 和 `LOCKED_TEST` 均排除。

| 子目录/文件 | 含义 |
|---|---|
| `pooled_common6/` | `our-common6` pooled pipeline、训练清单、recording-level GroupKFold 验证、混淆矩阵、配置和运行哈希。 |
| `README.md` | 本目录的数据范围、模型边界和产物索引。 |

## 特征与隔离

EDF 通道通过 `scripts/cross_source_utils.py` 统一映射：`F7-Pz→F7`、`F3-Pz→F3`、`T5-Pz→P7`、`O1-Pz→O1`、`O2-Pz→O2`、`T6-Pz→P8`。每个 recording/session 是最小分组单位；同一 EDF 产生的所有窗口不会跨 GroupKFold train/validation。

共享算法仍是 `MNE EDF → 128 Hz/0.5–43 Hz → 4 s/2 s 窗口 → 60 维 Welch 频带特征 → StandardScaler → PCA → RBF SVC`。最终 pipeline 只在 historical candidate 上 fit。

当前 common6 跨源解释必须保留 `exploratory / channel-aligned but author MAT reference compatibility uncertain`；Our EDF reference 为 Pz，author MAT reference 未知。
