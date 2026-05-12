<!-- 用法见 templates/README.md。决策规则见 CLAUDE.md §1。 -->
---
type: train
date_started: YYYY-MM-DD
date_finished: YYYY-MM-DD
config: src/configs/train/<file>.yaml
commit: <40-char SHA>
base_checkpoint: <ckpt 路径 / null>
hardware: <8 × A100 等>
inputs: [NN]    # 触发本次训练的 step (通常是 implement 或重大决策)
---

# NN · <训练目标一句话>

## 配置
- data mix: <数据集 + 比例>
- 训练步数: <total / target>
- 关键超参: <lr / batch / etc.>

## 过程
- 时长: <hours>
- 异常 / 中断 / 恢复: <如有>

## Checkpoint
| step | metric | 路径 | 用途 |
|---|---|---|---|
| 100k | success_rate=0.78 | s3://... | 中间 |
| 150k | success_rate=0.87 | s3://... | **选用** |

## 选用理由
<为什么选这个 ckpt 进入后续 eval>
