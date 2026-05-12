<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
status: active                    # active | completed | abandoned
started: YYYY-MM-DD
target: <一句话目标,含可量化指标>
predecessor: <上一个 task 路径,如有>
---

# <task 标题>

## 目标
<2-3 句说清楚要做什么、为什么、衡量标准>

## 起点
- baseline: <ckpt 路径 / from-scratch / 上个 task 的产出>
- 主要参考: <kb/papers/xxx.md 等>

## 时间线
<每个 step 完成后追加一行: YYYY-MM-DD  NN-<type>-<描述>  → 关键结果>

## 最终结论
<task 完成时填: 达成情况 + 沉淀去向 (kb 更新 / 新 ckpt / 新 heuristic)>
