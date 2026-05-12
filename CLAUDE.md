# CLAUDE.md

> Agent 工作纪律。开工读一遍,日常按 §4 走。

## §0 目标

构建 VLA 工程系统,让机器人服务物理世界。

当前 release 周期: 桌面操作 ≥90% / 全身 ≥75% / 推理延迟 ≤100ms。

**两类工程任务**: 论文复现 · 模型改进。

**协作分工**:
- **Claude Code (CC)**: 主执行 — 代码、实验、文档
- **claude.ai**: 战略讨论、设计审查、跨 session 知识沉淀
- **Codex**: 独立第三方 — 大假设空间任务 review / 双写 / critique
- **人类**: 高代价决策审核 (重训前 / 真机安全 / release)

**Codex 调用纪律**:
- 走 `tools/codex-session.sh` 的 `codex_call <key>` / `codex_end <key>`,裸 `codex exec` 禁用
- 一个任务一个 session key,任务结束 `codex_end` 释放
- 独立起草阶段 CC 与 Codex 互不看对方草稿(避免锚定),review 阶段可互看
- 关键决策的 Codex rollout 在 task 文件中引用其 UUID 作为依据

## §1 工作流

每段独立的探索 = 一个 task,task 内按时序展开:

```
理论 → 实现 → 训练 → 评测 ─┬─→ 分析 ──┐
                            │           ├─→ 继续 / 调头 / 完成
                            └─→ 问题 ───┤
                                        │
                                  → 引入 heuristic
```

### 1.1 开始一个 task

接到任务时:
1. 评估是否构成独立 task(有明确目标 + 可量化标准)。是 → 建 `tasks/YYYY-MM-<描述>/`,从 `templates/task-README.md` 复制 README;否 → 在已有 task 内续 step
2. README 写清楚: 目标(含量化指标)、起点(baseline ckpt 路径 / 上个 task / from-scratch)、主要参考(kb/papers/ 文件)
3. 第一个 step 通常是 `theory`(读论文)或 `implement`(直接动手)

### 1.2 推进 task

完成一个 step 后,看产出决定下一步:

| 上一步产出 | 通常的下一步 |
|---|---|
| theory 提了假设 | implement (写代码验证) |
| implement 改了代码 | train (慢循环) 或 eval-sim (快循环) |
| train 出了 ckpt | eval-sim (先仿真) |
| eval-sim 有数字 | eval-real (上真机) 或 analysis (归因) |
| eval-real 见问题 | issue (深挖) |
| issue 找出原因 | implement 或 heuristic (修) |
| heuristic 加规则 | eval-real (验证规则有效) |
| analysis 决策 | 继续 (回 implement) / 调头 (回 theory) / 完成 |

这是**指引,不是强制**——CC 可按情况跳过中间步骤。每完成一步,在 task README 时间线追加一行。

### 1.3 结束 task

什么时候 task 算完成:
- **达成目标** → README `status: completed` + 最终结论
- **无进展转新方向** → `status: abandoned` + 末尾说明
- **目标分裂** → 当前 task 写结论,开新 task,frontmatter `predecessor:` 引用

完成时**沉淀**:
- 新理解 → 更新 `kb/papers/*.md`
- 新基线 → README 标记新 ckpt 路径
- 新规则 → `src/inference/heuristics/` 已就位 + heuristic step 已记录

### 1.4 慢/快循环判定

- 需要**重训**才能验证 → 慢循环(必须 implement + train step,完成时真机验证)
- **推理一次**就能验证 → 快循环(可跳过 train,直接 eval-real)
- 不确定 → 归慢循环

### 1.5 并行运行

慢循环训练(几小时-几天)期间,**快循环不停**:
- 慢循环 task 在 train step 等待训练完成
- 快循环可在另一 task 内基于现有 ckpt 推进
- 多 task 并存是常态,不要求"一时只一 task"

### 1.6 改进依据

任何代码改动 / 训练参数变化,在 implement 或 train step 的"目的"段必须说明依据:
- **实验记录**: 引用前置 eval / issue step
- **理论分析**: 引用前置 theory step 或 `kb/papers/*.md`

两者结合更佳。空凭直觉改 → 不通过 §4 提交清单。

## §2 目录结构

```
tasks/YYYY-MM-<描述>/   一次探索: 内含 NN-<type>-*.md 按时序编号
kb/papers/              论文深度笔记 (template: templates/paper.md)
kb/models/              模型卡片 (template: kb/models/model.md)
kb/datasets/            数据集卡片 (template: kb/datasets/dataset.md)
kb/techniques/          技术卡片 (template: kb/techniques/technique.md)
src/                    代码: models/ data/ training/ inference/ eval/ configs/ scripts/ tests/
tools/                  lint.py, codex-session.sh
```

**type 枚举**: `theory` `implement` `train` `eval-sim` `eval-real` `analysis` `issue` `heuristic`

**按需创建**: 子目录在真有内容时再建(如 `src/inference/heuristics/` 等第一条规则出现再建)。

## §3 引用

frontmatter 用路径或 step 号:

```yaml
sources: [kb/papers/pi05.md#§4.2]              # 知识库
code: src/models/pi05/policy.py                # 代码
config: src/configs/eval/libero-spatial.yaml   # 配置
checkpoint: 03:step-150k                       # 同 task 第 03 步的 ckpt
inputs: [03, 04]                               # 分析依赖的前置步骤
codex_rollout: <UUID>                          # Codex 参与时的 rollout 引用
```

跨 task: `2026-05-pi05-reproduction/04`。

## §4 提交前自查

- [ ] 改了 NN 训练相关 → 有训练记录文件 + ckpt 路径
- [ ] 跑了实验 → 有对应 eval / real 文件
- [ ] 真机出问题(失败/抖动/无效/退化) → 有 issue 文件含现象 + 重现步骤
- [ ] 真机数据(视频/obs/action/人评)已保存,文件中给路径
- [ ] Codex 参与的决策 → task 文件中引用 rollout UUID
- [ ] commit message: 一句话改了什么 + 引用相关 task / 文件

## §5 task 完成

更新 task README:
- `status: completed`
- 时间线列出所有 step
- 结论 + 沉淀去向(kb 更新 / 新 baseline ckpt / 新 heuristic 路径)

---

*简短即纪律。规则按实战触发再加。*
