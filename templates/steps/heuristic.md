<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: heuristic
date: YYYY-MM-DD
code: src/inference/heuristics/<name>.py
inputs: [NN]                      # 触发本规则的 failure / analysis
---

# NN · <规则一句话>

## 规则
<什么情况触发,做什么>

## 实现位置
- 代码: src/inference/heuristics/<name>.py
- 集成点: src/inference/<entry>.py
- 测试: src/tests/integration/test_<name>.py
- 开关: <config flag,若有>

## 来源依据
<来自哪个 failure / analysis,≥30 字说明为什么需要>

## 删除条件
<什么情况下这条规则可以退休>
