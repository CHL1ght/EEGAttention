# `data/legacy/multiclass_10min/`

这里保存旧单状态自采记录。每个 EDF 是信号入口；同名 CSV 是设备导出的时序 sidecar，同名 DSI 是部分 session 的采集软件 sidecar。当前 baseline 只读取清单批准的 EDF，不根据文件内容猜 subject。

## lyc 文件

无 subject 前缀的 `focusN`、`iuN`、`ouN` 属于 lyc，由数据负责人确认并登记在 manifest：

- `focus1.edf`–`focus9.edf` 及对应 `focus1.csv`–`focus9.csv`；`focus3.dsi`、`focus4.dsi`、`focus6.dsi` 是额外 sidecar。
- `iu1.edf`–`iu4.edf` 及对应 CSV；`iu3.dsi`、`iu4.dsi` 是额外 sidecar。
- `ou1.edf`–`ou3.edf` 及对应 CSV；`ou3.dsi` 是额外 sidecar。
- `daze1.edf/.csv`、`daze2.edf/.csv`：静息参考，不进入二分类。

每个列出的 `.edf` 是独立信号文件；同名 `.csv`/`.dsi` 不是额外 EDF session，也不单独送入模型。

## zyf 文件

带 `zyf_` 前缀的文件属于 zyf：

- `zyf_focus1.edf`–`zyf_focus4.edf` 及对应 CSV。
- `zyf_iu1.edf`、`zyf_iu2.edf` 及对应 CSV。
- `zyf_ou1.edf`–`zyf_ou3.edf` 及对应 CSV。
- `zyf_daze1.edf/.csv`、`zyf_daze2.edf/.csv`：静息参考，不进入二分类。

## 标签和当前 personal model 范围

`focus → focus`，`iu/ou → unfocus`，`daze → rest`。本阶段 personal training 实际使用 manifest 中 lyc 的 19 个唯一 EDF、zyf 的 12 个唯一 EDF；zqd 的数据不在本目录，而在 `mixed_20min/` 中且被排除。原始文件一律只读。
