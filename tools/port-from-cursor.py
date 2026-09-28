#!/usr/bin/env python3
"""Apply the context-free Cursor -> Claude Code renames from PORTING.md to the pstack plugin tree.

Usage: tools/port-from-cursor.py [plugin_dir]   (default: plugins/pstack)

Idempotent. Only touches Markdown under README.md, docs/, skills/, and agents/, plus the
poteto-mode tools' package.json and bun.lock. Skips the
bundled cursor-team-kit skills (copied unmodified), unported/, and automations/. The port
drops make-bot-ui and automations/benny (see PORTING.md), so delete them after copying upstream.
Context-dependent edits (model defaults, read-only spawns, transcripts, cloud agents) are done by hand.
"""

import re
import sys
from pathlib import Path

BUNDLED = {"deslop", "control-cli", "control-ui"}

root = Path(sys.argv[1] if len(sys.argv) > 1 else "plugins/pstack")
skill_names = sorted(
    (p.name for p in (root / "skills").iterdir() if p.is_dir()),
    key=len,
    reverse=True,
)

RULES = [
    ("generalPurpose", r"\bgeneralPurpose\b", "general-purpose"),
    ("AskQuestion", r"\bAskQuestion\b", "AskUserQuestion"),
    ("user skills dir", r"~/\.cursor/skills/", "~/.claude/skills/"),
    ("project skills dir", r"(?<![\w~])\.cursor/skills/", ".claude/skills/"),
    ("plugins dir", r"~/\.cursor/plugins/", "~/.claude/plugins/"),
    ("poteto-agent type", r'subagent_type: "poteto-agent"', 'subagent_type: "pstack:poteto-agent"'),
    ("Comment Sicko type", r'subagent_type: "Comment Sicko"', 'subagent_type: "pstack:comment-sicko"'),
    ("Cursor /loop", r"Cursor's `/loop`", "Claude Code's `/loop`"),
    ("/loop built-in", r"`/loop` is Cursor's built-in", "`/loop` is Claude Code's built-in"),
    ("Cursor restart", r"\bCursor restart\b", "Claude Code restart"),
    ("tools package name", r"@cursor-skill/", "@pstack/"),
    (
        "slash commands",
        r"(?<![\w/.:~-])/(" + "|".join(map(re.escape, skill_names)) + r")(?![\w-])",
        r"/pstack:\1",
    ),
]


def targets():
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        top = rel.parts[0]
        if top in {"unported", "automations"}:
            continue
        if top == "skills" and rel.parts[1] in BUNDLED:
            continue
        if top in {"README.md", "docs", "skills", "agents"}:
            yield path
    for name in ("package.json", "bun.lock"):
        yield root / "skills/poteto-mode/scripts" / name


ALT_TEXT = re.compile(r"(!\[[^\]]*\])")


def apply(name, pattern, replacement, text):
    if name != "slash commands":
        return re.subn(pattern, replacement, text)
    # Image alt text describes the picture, which shows upstream's bare commands.
    parts = ALT_TEXT.split(text)
    total = 0
    for i in range(0, len(parts), 2):
        parts[i], n = re.subn(pattern, replacement, parts[i])
        total += n
    return "".join(parts), total


counts = {name: 0 for name, _, _ in RULES}
changed = 0
for path in targets():
    text = path.read_text()
    new = text
    for name, pattern, replacement in RULES:
        new, n = apply(name, pattern, replacement, new)
        counts[name] += n
    if new != text:
        path.write_text(new)
        changed += 1

for name, n in counts.items():
    print(f"{n:5d}  {name}")
print(f"{changed:5d}  files changed")
