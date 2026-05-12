#!/usr/bin/env python3
"""Lean lint · 防占位符。

scope:
  - tasks/**/*.md
  - kb/**/*.md

排除 (按惯例):
  - 文件名以 `_` 开头 (如 `_template.md`)
  - kb/{models,datasets,techniques}/{model,dataset,technique}.md (保留的模板卡片)
  - 任何包含 `template` 子串的 stem (大小写不敏感)

规则:
  - 禁: `TBD` / `TODO` / `___` / `<占位>`
  - kb/papers/*.md 额外禁:
      * 旧 Obsidian/MOC 链接: `[[moc-*]]` / `[[wiki/...]]`
      * 仓库外 PDF 路径: `raw/papers/...` / `/home/dm/Documents/...`
      * frontmatter 旧字段: `appendix_pages:`
      * `source_quality` 为 PDF 视觉类时缺少 v1.7.2 PDF 完整性字段
  - 跳过 (4 类 literal 全部适用):
      * fenced code block (``` 或 ~~~ 之间的内容)
      * 行内 `code`
  - 跳过 (仅 `<占位>` 额外适用):
      * HTML 注释 `<!-- ... -->` 与关闭标签 `</...>`
      * 合法 autolink: `<https://...>` / `<mailto:...>` / `<user@host>`
      * 单 token HTML tag (白名单内): `<br/>` / `<details>` / `<i>`
  - 仍误判时,把模板加 `_` 前缀或改名含 `template`,或在 fenced code block 内书写

exit codes:
  0 → 通过
  1 → 命中占位符
  2 → 读文件 / 未知 flag 等"工具自身错"

用法: python3 tools/lint.py [--quiet]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 3 个 kb 内保留模板卡片 (paper.md 在 templates/ 下, 本就不被扫到)
TEMPLATE_FILES = {
    Path("kb/models/model.md"),
    Path("kb/datasets/dataset.md"),
    Path("kb/techniques/technique.md"),
}

SCAN_DIRS = ["tasks", "kb"]
KNOWN_FLAGS = {"--quiet"}

# 三个明文占位符
LITERAL_PATTERNS = [
    (re.compile(r"\bTBD\b"), "TBD"),
    (re.compile(r"\bTODO\b"), "TODO"),
    (re.compile(r"___"), "___"),
]

STRUCTURAL_PATTERNS = [
    (re.compile(r"\[\[moc-[^\]]+\]\]"), "legacy-moc-link"),
    (re.compile(r"\[\[wiki/[^\]]+\]\]"), "legacy-wiki-link"),
    (re.compile(r"\braw/papers/"), "external-pdf-path"),
    (re.compile(r"/home/dm/Documents/"), "external-pdf-path"),
]

PDF_VISUAL_SOURCE_QUALITIES = {
    "pdf_visual",
    "pdf_visual_partial",
    "pdf_visual_indirect",
}

PDF_REQUIRED_FRONTMATTER_FIELDS = {
    "paper_version",
    "pdf_pages_total",
    "pdf_pages_main",
    "pdf_pages_appendix",
    "pdf_completeness_verified",
}

# `<占位>` 候选:首字符非 ! 非 /,内部不含 < > \n
ANGLE_PATTERN = re.compile(r"<[^!/<>\n][^<>\n]*>")

# 在 ANGLE_PATTERN 命中后用以过滤掉合法构造的前缀检测
_AUTOLINK_PREFIXES = ("http://", "https://", "ftp://", "mailto:")
_EMAIL_RE = re.compile(r"^[^<>\s@]+@[^<>\s@]+\.[^<>\s]+$")
_HTML_TAGS = {
    "br",
    "details",
    "summary",
    "i",
    "b",
    "em",
    "strong",
    "code",
    "kbd",
    "sub",
    "sup",
    "hr",
    "img",
    "a",
    "p",
    "div",
    "span",
}

# fenced code block 起止
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

# 行内 `code` 段
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def is_template(rel: Path) -> bool:
    if rel in TEMPLATE_FILES:
        return True
    name = rel.name
    if name.startswith("_"):
        return True
    if "template" in rel.stem.lower():
        return True
    return False


def is_legit_angle_content(inner: str) -> bool:
    """ANGLE_PATTERN 命中后判断括号内是否是合法构造而非占位符。

    采用保守策略 (宁可错报占位符,不放过真占位符):
    - URL/邮箱 autolink: 通过
    - HTML tag 仅识别两种形式: 单 token (`br`/`br/`/`details`) 或带 `key="value"` 属性
    - `<foo bar>` / `<论文标题>` / `<arXiv:YYMM>` 等不通过 → 报为占位符
    """
    s = inner.strip()
    if not s:
        return False
    # autolink: <https://...> / <mailto:...>
    if any(s.startswith(p) for p in _AUTOLINK_PREFIXES):
        return True
    # 邮箱 autolink: <user@host.tld>
    if _EMAIL_RE.match(s):
        return True
    # HTML tag 单 token: <br> / <br/> / <details> / <i>
    m = re.match(r"^([a-z][a-zA-Z0-9]*)\s*/?$", s)
    if m and m.group(1) in _HTML_TAGS:
        return True
    # HTML tag 带属性 (含 ="…"): <a href="…"> / <img src="…">
    if re.match(r'^[a-z][a-zA-Z0-9]*(\s+[a-zA-Z][\w-]*\s*=\s*"[^"]*")+\s*/?$', s):
        return True
    return False


def scan_file(path: Path) -> tuple[list[tuple[int, str, str]], str | None]:
    """返回 (placeholder_findings, read_error_msg)。两者互斥:有 error 则 findings=[]。"""
    findings: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [], f"{type(e).__name__}: {e}"

    rel = path.relative_to(ROOT)

    # frontmatter structural checks for instantiated paper notes.
    lines = text.splitlines()
    if rel.parts[:2] == ("kb", "papers") and len(lines) >= 2 and lines[0].strip() == "---":
        end = None
        for i, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                end = i
                break
        if end is not None:
            fm_lines = lines[1 : end - 1]
            keys: set[str] = set()
            source_quality = None
            for offset, line in enumerate(fm_lines, 2):
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)", line)
                if not m:
                    continue
                key, value = m.group(1), m.group(2).split("#", 1)[0].strip()
                keys.add(key)
                if key == "source_quality":
                    source_quality = value
                if key == "appendix_pages":
                    findings.append((offset, "legacy-frontmatter", line.strip()))
            if source_quality in PDF_VISUAL_SOURCE_QUALITIES:
                missing = sorted(PDF_REQUIRED_FRONTMATTER_FIELDS - keys)
                if missing:
                    findings.append((1, "missing-pdf-frontmatter", f"missing: {', '.join(missing)}"))

    in_fence = False
    for lineno, line in enumerate(lines, 1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # 用占位符把行内 `code` 抹掉再扫,避免 `<https://x>` 等代码片段误报
        cleaned = _INLINE_CODE_RE.sub(" ", line)
        for pat, label in LITERAL_PATTERNS:
            if pat.search(cleaned):
                findings.append((lineno, label, line.strip()))
        for pat, label in STRUCTURAL_PATTERNS:
            if pat.search(cleaned):
                findings.append((lineno, label, line.strip()))
        for m in ANGLE_PATTERN.finditer(cleaned):
            if is_legit_angle_content(m.group(0)[1:-1]):
                continue
            findings.append((lineno, "<占位>", line.strip()))
            break  # 一行只报一次 <占位>,避免噪音
    return findings, None


def collect_targets() -> list[Path]:
    targets: list[Path] = []
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            rel = p.relative_to(ROOT)
            if is_template(rel):
                continue
            targets.append(p)
    return sorted(targets)


def main() -> int:
    quiet = "--quiet" in sys.argv
    unknown = [a for a in sys.argv[1:] if a not in KNOWN_FLAGS]
    if unknown:
        print(f"❌ unknown flag(s): {unknown}; known: {sorted(KNOWN_FLAGS)}", file=sys.stderr)
        return 2

    targets = collect_targets()

    # 空状态语义区分:目录不存在 vs 目录存在但无 .md
    if not targets:
        existing = [d for d in SCAN_DIRS if (ROOT / d).exists()]
        missing = [d for d in SCAN_DIRS if not (ROOT / d).exists()]
        if not quiet:
            if existing and missing:
                print(f"Lean lint: scan dirs present={existing}, missing={missing}; nothing to scan (vacuous pass)")
            elif existing:
                print(f"Lean lint: dirs {existing} exist but no .md files yet (vacuous pass)")
            else:
                print(f"Lean lint: scan dirs {SCAN_DIRS} not yet created; lean cold-start (vacuous pass)")
        return 0

    if not quiet:
        print(f"Lean lint: scanning {len(targets)} files")

    placeholder_count = 0
    read_errors: list[tuple[Path, str]] = []
    for p in targets:
        findings, err = scan_file(p)
        rel = p.relative_to(ROOT)
        if err is not None:
            read_errors.append((rel, err))
            print(f"{rel}: read-error: {err}", file=sys.stderr)
            continue
        for lineno, label, snippet in findings:
            placeholder_count += 1
            print(f"{rel}:{lineno}: {label}: {snippet}")

    if read_errors:
        print(f"\n❌ {len(read_errors)} file(s) unreadable — lint contract broken", file=sys.stderr)
        return 2
    if placeholder_count:
        print(f"\n❌ {placeholder_count} lint issue(s) found")
        return 1
    if not quiet:
        print("✓ no lint issues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
