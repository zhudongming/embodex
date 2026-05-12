# embodex

VLA 工程库。构建机器人具身大脑系统,让 AI 服务物理世界。
工作纪律见 `CLAUDE.md`,模板用法见 `templates/README.md`。

## 目录

```
CLAUDE.md              工作纪律 (开工先读)
templates/             模板 (task / step / paper)
  README.md            模板用法 + step type 选择
  task-README.md       task 目录的 README 起点
  paper.md             论文笔记模板 (VLA 范式标签 + 透明度元数据)
  steps/               8 种 step type 模板
kb/                    知识库
  papers/              论文深度笔记 (template: templates/paper.md)
  models/              模型卡片 (template: model.md)
  datasets/            数据集卡片 (template: dataset.md)
  techniques/          技术卡片 (template: technique.md)
tasks/                 探索任务 (按需创建,YYYY-MM-<描述>/)
src/                   代码 (models / data / training / inference / eval / configs / scripts / tests)
tools/                 codex-session.sh · lint.py
```

`tasks/` 和 `src/` 按需创建；冷启动仓库中没有这两个目录是正常状态。

## 入门

新接手:

1. `CLAUDE.md` (5 分钟)
2. `templates/README.md` (10 分钟)
3. 开干

> 命令块里的 `$NAME` 是 shell 变量,先 `export` / `set` 再执行;**不要**直接粘贴含 `<占位>` 的命令(`<` 会被 shell 当 redirect)。

启动新 task:

```bash
TASK_NAME=pi05-reproduction   # 改成自己的任务名
DESC=pi05-architecture        # 第一个 step 的简述
mkdir -p tasks/$(date +%Y-%m)-$TASK_NAME/
cp templates/task-README.md tasks/$(date +%Y-%m)-$TASK_NAME/README.md
cp templates/steps/theory.md tasks/$(date +%Y-%m)-$TASK_NAME/01-theory-$DESC.md
```

新增论文笔记:

```bash
PAPER_ID=pi05
cp templates/paper.md kb/papers/$PAPER_ID.md
```

新增模型/数据集/技术卡片:

```bash
ID=pi05
cp kb/models/model.md kb/models/$ID.md
cp kb/datasets/dataset.md kb/datasets/$ID.md
cp kb/techniques/technique.md kb/techniques/$ID.md
```

## Codex 协作

```bash
source tools/codex-session.sh
codex_call <session-key> "你的 prompt"  # 续接 session, 节省 token + 留 rollout
codex_end  <session-key>                # 任务结束释放
```

关键决策在 task 文件 frontmatter 记录 `codex_rollout: <UUID>`。

## Lint

```bash
python3 tools/lint.py
```

扫 `tasks/`、`kb/` 下 `*.md`,防 `TBD` / `TODO` / `___` / `<placeholder>`；`kb/papers/` 还会检查旧 Obsidian/MOC 链接、仓库外 PDF 路径和 PDF 完整性字段。模板自身豁免(以 `_` 开头的文件 + stem 含 "template" 的文件 + `kb/{models,datasets,techniques}/{model,dataset,technique}.md`)。

## 旧版迁移注意

仓库曾用 HL (Heuristic Learning, Weng 2026) 框架,已于 2026-05-12 替换为 lean。如果你之前装过 HL 时代的 git hooks (`tools/install-hooks.sh`),它们会指向已删除的脚本,导致后续 commit 报错:

```bash
rm -f .git/hooks/pre-commit .git/hooks/commit-msg
```

新框架不强制安装 hooks;CI 跑 `python3 tools/lint.py` 即可。
