<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: implement
date: YYYY-MM-DD
commit: <40-char SHA>
changes:                          # 本次改了哪些代码 / 配置
  - src/path/file.py (new | modified)
inputs: [NN]                      # 依据的前置 step
---

# NN · <实现了什么>

## 目的
<对应哪个理论分析或失败修复>

## 实现概要
<3-5 句说做了什么,详见 commit diff>

## 关键决策
<实现过程中的非平凡选择,以及理由>

## 未尽事项
<已知但本次没做的,后续 step 可能要处理>
