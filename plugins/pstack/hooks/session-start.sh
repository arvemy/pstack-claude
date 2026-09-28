#!/usr/bin/env bash
set -euo pipefail

root="${1:-${CLAUDE_PLUGIN_ROOT:-}}"
[ -n "$root" ] || exit 0

skills=$(find "$root/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -exec dirname {} \; | xargs -n1 basename | sort | paste -sd, - | sed 's/,/, /g')

context="pstack is installed. Its skills live at ${root}/skills/<name>/SKILL.md, and the names are exactly these: ${skills}. Every pstack skill is user-invoked only, so the Skill tool cannot load one. When a pstack file or the user tells you to run, apply, or read a pstack skill, whether it writes \`/pstack:how\`, \`/how\`, or \"the **how** skill\", read ${root}/skills/how/SKILL.md (substituting that exact name) and follow it. pstack's agents are pstack:poteto-agent, pstack:readonly-agent, pstack:worker, and pstack:comment-sicko. pstack's model config is ~/.claude/pstack/models.md."

escaped=$(printf '%s' "$context" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$escaped"
