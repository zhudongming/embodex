<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: analysis
date: YYYY-MM-DD
inputs: [NN, NN]                  # 本次分析读了哪些前置 step
sources: [kb/papers/xxx.md]       # 引用知识库 (如有)
---

# NN · <分析主题一句话>

## 数据
<引用 inputs 中的关键数字>

## 对照前置假设
<回看相关 theory step 的假设,逐条对照实际结果>

## 归因
<结果的可能原因,标证据强度: 强 / 中等 / 弱>

## 决策
<下一步做什么: 继续 / 调头 / 完成>

## 待办
<具体下一步 step 列表>
