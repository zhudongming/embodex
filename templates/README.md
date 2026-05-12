# Templates 使用指南

> 模板是 checklist,不是 schema。它们防止你忘记关键信息,不限制怎么写。
> 决策规则总入口在 `CLAUDE.md`,本文档专注"模板怎么用"。

## 1. 工作流

工作流的完整规则见 `CLAUDE.md §1`(开始 task / 推进 task / 结束 task / 慢快循环 / 并行 / 改进依据)。

本文档专注"每一步用哪个模板、怎么填"。

## 2. 我该用哪个模板?

| 我在做什么 | 用哪个 step type |
|---|---|
| 调研论文 / 综合 kb 内容,提假设 | `theory` |
| 写代码 / 改代码 (任何要 commit 的) | `implement` |
| 启动一次训练 | `train` |
| 跑仿真评测 | `eval-sim` |
| 跑真机评测 | `eval-real` |
| 综合多个前置 step,归因 + 决策 | `analysis` |
| 真机/仿真出现非预期现象 | `issue` |
| 引入推理时的新规则 | `heuristic` |

**不确定?** 看产出物的主要价值: 假设 → `theory`; 代码 → `implement`; 数字 → `eval-*`; 决策 → `analysis`。

## 3. 文件命名

- **task 目录**: `tasks/YYYY-MM-<描述>/` 例 `tasks/2026-05-pi05-reproduction/`
- **task 内文件**: `NN-<type>-<短描述>.md`,NN 是两位数字按时序递增 (01, 02, 03...)
- **论文笔记**: `kb/papers/<paper-id>.md`

## 4. 引用语法

| 引用对象 | 写法 | 例 |
|---|---|---|
| 同 task 内前置 step | step 号 | `inputs: [03, 04]` |
| 某 step 的 checkpoint | `NN:step-NNN` | `checkpoint: 03:step-150k` |
| 某 step 的某 episode | `NN:episode-N` | `source: 05:episode-3` |
| 跨 task | `<task-dir>/<NN>` | `inputs: [2026-05-pi05-reproduction/04]` |
| 论文笔记某节 | `kb/papers/xxx.md#§X.Y` | `sources: [kb/papers/pi05.md#§4.2]` |
| 代码 / 配置 | 相对仓库根路径 | `code: src/models/pi05/policy.py` |
| Codex rollout | UUID 字符串 | `codex_rollout: <UUID>` |

## 5. 字段语义

### `issue.kind` (选一个)

| 值 | 含义 | 例 |
|---|---|---|
| `failure` | 硬失败 success=0 | 抓空、超时、碰撞 |
| `jitter` | 输出抖动 | action 跳变 |
| `invalid` | 无效动作 | 出 action 但无效果 |
| `degrade` | 指标退化 | 训练越久 success 越低 |
| `instability` | 不稳定 | 同 seed 两次差很多 |
| `slow` | 延迟超预算 | 推理 > 100ms |
| `partial` | 部分完成 | 任务做了 60% |
| `anomaly` | 意外行为 | 做对了但方式怪 |
| `other` | 其他 | — |

### `issue.severity` / `status`

- `severity`: `minor` (可接受) / `notable` (值得跟进) / `blocking` (阻塞下一步)
- `status`: `observed` (仅记录) / `investigating` / `workaround` / `fixed` / `accepted` (知道但不修)

### `task-README.status`

- `active` 进行中 / `completed` 已完成 / `abandoned` 放弃 (末尾说明原因)

### `paper.priority`

- `P0` 核心主线 — 全文细读 + PDF 视觉读
- `P1` 重点跟进 — 重点章节细读 / 借鉴方法
- `P2` 旁证 — 主要数字 + 关键架构, 横向参考
- `P3` 仅索引 — 仅作索引条目, 不展开正文

字段语义详见 `templates/paper.md:33` frontmatter 注释。

## 6. 完整示范

一个真实 task 长这样:

```
tasks/2026-05-pi05-reproduction/
├── README.md                                  # status, 时间线, 最终结论
├── 01-theory-pi05-architecture.md             # 读 kb/papers/pi05.md, 提假设
├── 02-implement-baseline.md                   # 写代码, commit a1b2c3
├── 03-train-baseline.md                       # 72h, ckpt @150k
├── 04-eval-sim-baseline.md                    # LIBERO 0.87 (gap -5%)
├── 05-eval-real-first.md                      # ALOHA 0.72, 见 grasp_slip
├── 06-issue-grasp-slip.md                     # 深挖湿润物体问题
├── 07-implement-force-adaptive.md             # 写 heuristic 代码
├── 08-heuristic-force-adaptive.md             # 引入新规则记录
├── 09-eval-real-retest.md                     # 加 heuristic 后 0.81
└── 10-analysis-final.md                       # 总结, status→completed
```

**串起来的方式**: 每个 step 通过 frontmatter `inputs:` 引用前置 step,README 时间线持续追加。

## 7. 常见混淆

**`implement` vs `heuristic`**: implement 是代码改动记录,heuristic 是规则引入记录。如果你写的代码就是某个 heuristic,**先 implement 再 heuristic**(两个 step)。

**`issue` vs `analysis`**: issue 聚焦一个**具体问题**(一个失败、一种抖动),analysis 综合**多个数据点**做归因决策。一个 analysis 可引用多个 issue。

**`theory` step vs `kb/papers/*.md`**: kb/papers/ 是论文完整笔记,长期保留。theory step 是 task 中应用论文做的具体分析。theory **引用** kb/,**不重复** kb/。

## 8. 边界情况

- **小改动不值得开 step**: 改个 typo 直接 commit,不建 step
- **新型工作不属于 8 种 type**: 先做,做完讨论是否加新 type
- **写不出某段**: 先空着或写一句话占位,后续 step 可能补
- **绝不写** `TBD` / `TODO` / `___` / `<占位>` (lint 标红);eval-real 人评 建议 ≥ 30 字(约定,非 lint 硬校验,review 时会被回退)

**慢循环必须**有 implement + train step,不能跳过——否则 ckpt 失忆。
