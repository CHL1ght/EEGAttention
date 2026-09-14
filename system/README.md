# `system/`

这里是未来在线系统的原型目录，不属于当前离线实验主流程。当前内容只验证后端服务可以启动并响应健康检查；不会读取 EDF，也不会加载 pooled 或 personal model。

## 文件与子目录

| 路径 | 含义 | 当前状态 |
|---|---|---|
| `backend/` | 后端服务源码目录。 | 原型 |
| `backend/main.py` | 最小 FastAPI 应用，提供 `/health` 健康检查路由。 | 已实现健康检查，未接 EEG |
| `backend/README.md` | 后端启动方式、接口和与离线实验边界的说明。 | 文档 |
| `README.md` | 本目录的总体定位。 | 文档 |

## 与离线实验的边界

- `scripts/` 才是 EDF → 预处理 → 特征 → PCA → SVC → 保存/预测的正式入口。
- `system/backend/main.py` 当前不应被视为快速预测 notebook 的替代品。
- 若将来接入模型，必须明确使用哪个冻结 artifact，并继续保持 LOCKED_TEST 不参与任何 fit；本阶段不在此目录实现该功能。
