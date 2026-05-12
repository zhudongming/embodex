<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: eval-real
date: YYYY-MM-DD
checkpoint: NN:step-NNN
robot: <aloha | mobile-aloha | ur5 | ...>
operator: <人名>
inputs: [NN]
---

# NN · <真机测试一句话>

## 设置
- 任务: <pick-and-place / fold / ...>
- 工作区 / 标定: <尺寸 + 标定日期>
- episode 数: <N> (M seed × K ep)
- 安全协议: <速度 / 力限制>

## 数据 artifacts
<文件路径,真机数据必须保存>
- 第三视角视频: <path>
- 腕部视频: <path>
- obs / action: <path>
- robot state / event log: <path>

## 结果
- success_rate: <数字>
- per-task / per-seed: <细分>

## 问题观察
| ep | 时间 | kind | 描述 | 处理 |
|---|---|---|---|---|
| 3 | 12.4s | failure | <描述> | <建 issue step / 忽略> |
| 17 | 8.1s | jitter | <描述> | <暂忽略 / 待观察> |

## 人类评价
<≥ 30 字。说清楚哪些好、哪些差、与上次对比、看到的问题>

## 归因
<结果来自模型 / 数据 / heuristic / 环境变化? 不能归因时标 confounded>

## 后续
<下一步: 建 failure / 加 heuristic / 完成>
