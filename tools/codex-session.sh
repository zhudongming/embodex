#!/usr/bin/env bash
# codex-session.sh — codex CLI 的会话续接小工具
#
# 用途: 让 CC (或人) 跨多次 `codex exec` 调用保持同一对话上下文,
#       避免每轮重新铺背景, 同时把会话历史留在 ~/.codex/sessions/ 可审计。
#
# 用法:
#   source tools/codex-session.sh
#   codex_call <key> "<prompt>"   # 首次自动新建并记 UUID, 之后自动 resume
#   codex_end  <key>              # 任务结束清掉 sid 文件 (codex 历史仍保留)
#   codex_sid  <key>              # 打印当前 session UUID
#   codex_list                    # 列出当前活跃的 session_key
#
# 设计要点 (踩过的坑):
#   - resume 不接受 -s/-C 等首启标志, sandbox/cwd 由原 session 继承
#   - codex stdout 第一行常是 "Reading additional input from stdin..." (非 JSON),
#     必须 grep '^{' 过滤后再喂 jq
#   - 永远不传 --ephemeral, 否则后续无法 resume
#   - session 文件: ~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<UUID>.jsonl
#
# 依赖: codex (>= 0.130.0), python3, mktemp

_codex_sid_file() { printf '/tmp/codex-%s.sid' "$1"; }

# UUID 校验: 标准 8-4-4-4-12 hex
_codex_is_valid_uuid() {
  [[ "$1" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]
}

_codex_check_deps() {
  command -v codex   >/dev/null || { echo "❌ codex not in PATH" >&2; return 1; }
  command -v python3 >/dev/null || { echo "❌ python3 not in PATH" >&2; return 1; }
}

# 从 codex --json 输出里提取 thread_id (跳过 stdin 提示等非 JSON 行)
_codex_extract_thread_id() {
  python3 - "$1" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line.startswith('{'):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get('type') == 'thread.started':
            print(obj.get('thread_id', ''))
            break
PY
}

# 主入口: codex_call <key> "<prompt>"
codex_call() {
  if [[ $# -lt 2 ]]; then
    echo "usage: codex_call <key> \"<prompt>\"" >&2
    return 2
  fi
  _codex_check_deps || return 1

  local key="$1"; shift
  local prompt="$*"
  local sid_file out rc
  sid_file=$(_codex_sid_file "$key")
  out=$(mktemp /tmp/codex-out.XXXXXX) || {
    echo "[codex-session] ❌ mktemp failed — cannot capture codex output" >&2
    return 2
  }

  if [[ -s "$sid_file" ]]; then
    # ----- resume 路径 -----
    local tid
    tid=$(tr -d '[:space:]' < "$sid_file")
    if ! _codex_is_valid_uuid "$tid"; then
      echo "[codex-session] ⚠️  sid file '$sid_file' malformed: '$tid' — removing, please retry" >&2
      rm -f "$sid_file" "$out"
      return 1
    fi
    codex exec resume "$tid" --json "$prompt" | tee "$out"
    rc=${PIPESTATUS[0]}
    if [[ $rc -ne 0 ]]; then
      echo "[codex-session] ⚠️  resume failed (rc=$rc) for key='$key' UUID=$tid — removing sid file; next call will start a new session" >&2
      rm -f "$sid_file"
    fi
  else
    # ----- 首启路径 -----
    codex exec --json "$prompt" | tee "$out"
    rc=${PIPESTATUS[0]}
    if [[ $rc -eq 0 ]]; then
      local tid
      tid=$(_codex_extract_thread_id "$out")
      if _codex_is_valid_uuid "$tid"; then
        echo "$tid" > "$sid_file"
        echo "[codex-session] new session for key='$key': $tid" >&2
      else
        echo "[codex-session] ⚠️  could not capture thread_id from first turn — session not resumable" >&2
        # rc=3: 首启 codex 返回 ok 但 thread_id 抓不到, 标为降级状态让调用方可侦测
        rc=3
      fi
    fi
  fi

  rm -f "$out"
  return $rc
}

# 显式结束: 删 sid 文件 (codex 自己的 rollout 文件不动, 仍可手动 resume)
codex_end() {
  if [[ $# -ne 1 ]]; then
    echo "usage: codex_end <key>" >&2
    return 2
  fi
  local sid_file
  sid_file=$(_codex_sid_file "$1")
  if [[ -f "$sid_file" ]]; then
    local tid
    tid=$(cat "$sid_file")
    rm -f "$sid_file"
    echo "[codex-session] ended key='$1' (UUID was $tid; rollout file kept in ~/.codex/sessions/)" >&2
  else
    echo "[codex-session] no active session for key='$1'" >&2
  fi
}

# 查看某 key 当前的 session UUID
codex_sid() {
  if [[ $# -ne 1 ]]; then
    echo "usage: codex_sid <key>" >&2
    return 2
  fi
  local sid_file
  sid_file=$(_codex_sid_file "$1")
  if [[ -s "$sid_file" ]]; then
    cat "$sid_file"
  else
    echo "no active session for key='$1'" >&2
    return 1
  fi
}

# 列出所有活跃的 session_key
codex_list() {
  shopt -s nullglob
  local files=(/tmp/codex-*.sid)
  shopt -u nullglob
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "no active codex sessions"
    return 0
  fi
  printf '%-30s  %s\n' "KEY" "UUID"
  local f key tid
  for f in "${files[@]}"; do
    key="${f#/tmp/codex-}"; key="${key%.sid}"
    tid=$(cat "$f" 2>/dev/null)
    printf '%-30s  %s\n' "$key" "$tid"
  done
}
