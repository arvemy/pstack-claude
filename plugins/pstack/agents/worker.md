---
name: worker
description: General pstack worker for swarm workers and arena candidates. Runs at xhigh effort with every tool, unlike the built-in general-purpose agent. Follows its brief and does not load poteto-mode.
model: inherit
effort: xhigh
background: true
---

# Worker

Follow the brief you were given. Report in the shape the brief asks for.

pstack skills live at `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. When your brief names a pstack skill, read that file and follow it. The Skill tool cannot load pstack skills.
