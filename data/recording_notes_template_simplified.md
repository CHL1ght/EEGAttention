# EEG 现场采集记录模板（精简版）

每个 session / EDF 单独记录一份。**只记会变化、会影响解释的数据**；固定设备参数不在每段重复填写。

> 固定采集配置（300 Hz、24 路 EEG、Pz 参考等）由项目协议统一记录。  

## 每段必填

```yaml
date: 2026-09-14
subject: lyc / zyf
file_basename:
condition: focus / unfocus / rest
task: # 王者荣耀 / 下棋 / 恐怖游戏等
mode: # 排位、人机、棋局难度等；没有特别信息可写 normal

start_time:
end_time:

self_report:
  attention: 1-7
  engagement: 1-7
  arousal: 1-7
  immersion: 1-7

notes: # 只记录真正影响本段数据的情况；没有就写 none
```

## 四项自评怎么打

- `attention`：1 = 几乎没注意任务；4 = 一般；7 = 持续高度集中
- `engagement`：1 = 很敷衍/机械完成；4 = 一般；7 = 非常投入、主动想做好
- `arousal`：1 = 很平静或困倦；4 = 正常清醒；7 = 非常兴奋/紧张/激活
- `immersion`：1 = 很容易游离；4 = 一般；7 = 高度沉浸，明显忽略外界/时间

这些是探索性主观评分，不等于标准化量表，也不能单独证明“心流”。

## `notes` 什么时候需要写

只在有明显情况时写，例如：

- 持续讲话 / 陪玩语音很多
- 明显大动作
- 游戏或任务暂停、中断
- 信号明显异常
- 软件异常
- 被试自己感觉这段其实没有达到预期状态

没有这些情况直接写：

```yaml
notes: none
```

## 示例 A：lyc 王者荣耀高投入

```yaml
date: 2026-09-14
subject: lyc
file_basename: lyc_focus1_20260914
condition: focus
task: 王者荣耀
mode: 排位 / 陪玩

start_time: 16:50
end_time: 17:02

self_report:
  attention: 6
  engagement: 7
  arousal: 4
  immersion: 6

notes: 陪玩语音较少，无明显中断
```

## 示例 B：zyf 恐怖游戏 probe

恐怖游戏用于观察 **high engagement + high arousal**，不要因为“恐怖”就自动认为它等于标准 `focus`。

```yaml
date: 2026-09-14
subject: zyf
file_basename: # 录制前确认 canonical label 后再命名
condition: # focus / unfocus / rest，录制前确认
task: 恐怖游戏
mode: 游戏名 + 模式

start_time: 18:35
end_time: 18:47

self_report:
  attention: 7
  engagement: 7
  arousal: 7
  immersion: 6

notes: 恐怖刺激明显；无任务中断
```

## 录制结束后的统一收尾

这些不用每段都手填进本模板，最后统一处理即可：

- 确认 EDF / CSV / DSI 文件成功保存且没有覆盖旧文件
- 按项目规则登记有效区间（默认可先参考首尾 30 秒 buffer）
- 更新 `session_manifest.csv`
- 计算并登记 EDF SHA-256
- 保持 `data/locked/` 数据只用于独立测试，不用于训练或调参
