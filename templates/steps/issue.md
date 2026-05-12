<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: issue
date: YYYY-MM-DD
kind:    # failure=硬失败 jitter=抖动 invalid=无效动作 degrade=指标退化
         # instability=同seed不稳 slow=超延迟 partial=部分完成 anomaly=意外行为 other
severity:    # minor=可接受 notable=值得跟进 blocking=阻塞下一步
source: NN:episode-N | NN:metric    # 问题首次出现的位置
status:    # observed=记录 investigating=分析中 workaround=临时方案
           # fixed=已修 accepted=知道但不修
inputs: [NN]    # 触发本 issue 的前置 step
---

# NN · <问题一句话>

## 现象
<客观可观测: 数字 / 视频时刻 / 异常指标 + 上下文>

## 重现 (若能重现)
```bash
git checkout <commit>
<具体命令>
```
预期看到: <现象>

## 假设
- (A) <可能原因 1> — 证据强度: 强 / 中 / 弱
- (B) <可能原因 2> — 证据强度: 强 / 中 / 弱

## 已知禁忌
<未来不要试的方向 + 原因。若是新问题,留空>

## 处理
<workaround / fix / 接受现状 / 待观察。引用后续 step>

## 教训
<这次暴露了什么? 决策时缺什么信息?>
