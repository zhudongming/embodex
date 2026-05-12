<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: eval-sim
date: YYYY-MM-DD
checkpoint: NN:step-NNN           # 引用本 task 训练 step 的 ckpt
config: src/configs/eval/<file>.yaml
evaluator: src/eval/<file>.py
---

# NN · <评测对象一句话>

## 结果
- success_rate: <数字>
- per_task: <细分>
- baseline / paper 对比: <gap>

## 归因
<结果的可能原因。引用前置 step (训练 / 实现) 解释>

## 后续
<下一步建议: 调头 / 继续 / 完成 / 真机>
