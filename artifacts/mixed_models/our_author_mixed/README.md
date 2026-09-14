# `our_author_mixed/`

本目录记录 `our+author mixed model` 的训练门禁结果。

| 文件 | 含义 |
|---|---|
| `channel_alignment.csv` | our historical EDF 和 LOCKED_TEST EDF 的 common7 明确映射检查。 |
| `BLOCKED.json` | mixed 训练未执行的机器可读原因。 |
| `BLOCKED.md` | mixed 训练/测试被阻塞的文字说明。 |
| `README.md` | 本目录说明。 |

由于当前 EDF 缺少 `P7/P8/AF4`，没有调用 Scaler/PCA/SVC fit，也没有生成 mixed pipeline。
