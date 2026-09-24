# Porting pstack from Cursor to Claude Code

This repository is a Claude Code port of [pstack](https://github.com/cursor/plugins/tree/main/pstack).

- Upstream commit: `12d587dfb20741cafc376c42c696c5f6e2a64487` (2026-09-23)
- Upstream version: `0.15.5`

This file records every mapping the port applies. Use it when you port a newer upstream version, so the same Cursor construct always becomes the same Claude Code construct.

## Layout

| Upstream | Port |
|---|---|
| `pstack/.cursor-plugin/plugin.json` | `plugins/pstack/.claude-plugin/plugin.json` |
| (none) | `.claude-plugin/marketplace.json` at the repository root |
| `pstack/skills/`, `pstack/agents/` | `plugins/pstack/skills/`, `plugins/pstack/agents/` |
| `cursor-team-kit/skills/{deslop,control-cli,control-ui}` | Bundled into `plugins/pstack/skills/`. See `plugins/pstack/THIRD_PARTY_NOTICES.md`. |

## Models

Claude Code subagents run Claude models only. The port uses the four Agent tool aliases.

| Alias | Model | Role in pstack |
|---|---|---|
| `fable` | Claude Fable 5.1 | Hardest tasks. One seat on every review panel. |
| `opus` | Claude Opus 5.5 | Judgment, prose, explainers, synthesizers. |
| `sonnet` | Claude Sonnet 5 | Code delegates, explorers, investigators, swarm workers. |
| `haiku` | Claude Haiku 4.5 | Cheap bulk reading (transcript slices). No effort control, 200K context. |

`inherit` as a configured value means: omit the Agent tool `model` parameter, so the subagent runs on the parent session's model. It replaces upstream's `inherit-parent` and `auto`.

Upstream role defaults map as follows.

| Role line | Upstream default | Port default |
|---|---|---|
| `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb` | `grok-4.7-xhigh-fast` | `sonnet` |
| `judgment and prose` | `claude-opus-5-5-max` | `opus` |
| `hardest tasks` | `claude-opus-5-5-max` | `fable` |
| `how explorer`, `why investigators`, `swarm workers` | `grok-4.7-xhigh-fast` | `sonnet` |
| `how explainer`, `why synthesizer` | `claude-opus-5-5-max` | `opus` |
| `reflect tooling` | `gpt-5.6-sol-max` | `opus` |
| `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-max` | `opus` |
| (recall's miners, no role line) | "a fast, cheap model" | `haiku` |
| `arena runners`, `arena cross-judge pool`, `architect runners`, `interrogate reviewers` | `claude-opus-5-5-max, gpt-5.6-sol-max, grok-4.7-xhigh-fast` | `fable, opus, sonnet` |

### Panel diversity

Upstream panels get their adversarial signal from three model vendors. The port's panels are three Claude models. They are different models, but they share a lineage, so their blind spots overlap more. The port compensates in `interrogate`, `arena`, and `architect` by giving each panel seat a distinct lens in addition to its distinct model. Where upstream prefers "a different model family from the parent", the port prefers "a different model from the parent".

### Effort and budget

Cursor encodes reasoning effort in the model slug (`-max`, `-xhigh`), so upstream's budget rewrote every slug's effort. The Claude Code Agent tool takes a model per spawn but no effort. Effort comes from the agent definition. So the port splits the two.

- **Effort** is fixed per pstack agent in its frontmatter (`effort: xhigh` for `poteto-agent` and `readonly-agent`). The main session's effort is the user's choice via `/effort`.
- **Budget** moves roles along the ladder `haiku < sonnet < opus < fable`. See `skills/setup-pstack/SKILL.md` for the exact rule.

## Configuration

| Upstream | Port |
|---|---|
| `~/.cursor/rules/pstack-models.mdc` (always-applied rule, `alwaysApply: true`) | `~/.claude/pstack/models.md` (plain file each skill reads by path) |
| "the `pstack-models.mdc` rule" | "the pstack model config" |

Claude Code has no documented always-applied rules directory. The skills already read the rule by path, so a plain file keeps the upstream mechanism.

## Tools and subagents

| Upstream (Cursor) | Port (Claude Code) |
|---|---|
| `Task` tool | `Agent` tool |
| `subagent_type: generalPurpose` | `subagent_type: general-purpose` |
| `subagent_type: "poteto-agent"` | `subagent_type: "pstack:poteto-agent"` |
| `subagent_type: "Comment Sicko"` | `subagent_type: "pstack:comment-sicko"` |
| `readonly: true`, or `readonly: false` with "must not write" | `subagent_type: "pstack:readonly-agent"` (`Edit`, `Write`, `NotebookEdit`, and `Agent` blocked, so it can neither edit nor delegate an edit; MCP kept) |
| `run_in_background: true` | Dropped. Claude Code subagents run in the background. |
| `is_background: true` (agent frontmatter) | `background: true` |
| `environment: "cloud"` | `isolation: "remote"` when the session offers it, else `isolation: "worktree"` for writers and no isolation for read-only work |
| Resuming a subagent | `SendMessage` to the agent's ID or name |
| `AskQuestion` | `AskUserQuestion` |
| "the `mcps/` directory Cursor exposes" | MCP tools in the session's tool list (`mcp__<server>__<tool>`), including deferred tools found with `ToolSearch` |
| "agent mode (readonly strips MCP)" | Dropped. Read-only agents keep MCP. |

## Skills

| Upstream (Cursor) | Port (Claude Code) |
|---|---|
| `/poteto-mode`, `/how`, and every other pstack slash command | `/pstack:poteto-mode`, `/pstack:how`, and so on. Plugin skills are namespaced. |
| Cross-skill routing by name | Unchanged in prose. Every pstack skill keeps `disable-model-invocation: true`, so the Skill tool cannot load one. A `SessionStart` hook (`hooks/session-start.sh`) tells the session where the skill files live and lists their exact names, so a routed skill is loaded by reading its `SKILL.md`. `poteto-mode` also says its siblings live at `../<name>/SKILL.md`, and the pstack agents carry the same pointer, since hooks do not reach subagents. |
| `name: Poteto Mode`, `name: Make Bot UI` | `name: poteto-mode`, `name: make-bot-ui` |
| Cursor mode frontmatter (`mode`, `icon`, `color`, `reminder`) | Dropped. |
| `.cursor/skills/`, `~/.cursor/skills/` | `.claude/skills/`, `~/.claude/skills/` |
| `~/.cursor/plugins/` | `~/.claude/plugins/` |
| Cursor's built-in `create-skill` | The `skill-creator` skill (`/skill-creator:skill-creator`, from the official Anthropic plugin marketplace) |
| Cursor's built-in `babysit` | Dropped. Claude Code has no built-in babysit. |
| `deslop`, `control-cli`, `control-ui` "from `cursor-team-kit`" | The bundled **deslop**, **control-cli**, **control-ui** skills |

## Transcripts

| Upstream (Cursor) | Port (Claude Code) |
|---|---|
| `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, slug = path without the leading slash, `/` → `-` | `~/.claude/projects/<slug>/<session-id>.jsonl`, slug = the absolute working directory with every non-alphanumeric character replaced by `-` (so `/home/you/proj` becomes `-home-you-proj`). Subagent transcripts live under `<session-id>/subagents/`. |
| "the system prompt names this path" | Derive the path from the working directory. |

The Claude Code transcript format is internal and can change between releases. Skills that mine transcripts read message text defensively and never depend on a field beyond `type`, `message`, `timestamp`, `cwd`, and `sessionId`.

## Wake mechanisms and cloud work

| Upstream (Cursor) | Port (Claude Code) |
|---|---|
| Cursor's `/loop` | Claude Code's `/loop` (fixed interval, or self-paced with no interval) |
| `/goal` | Claude Code's `/goal` |
| A watcher subagent that wakes you | A background Bash watcher or the `Monitor` tool. Completion notifications wake the session. |
| Cursor cloud agents, "cloud root", "cloud-sleeper wake chain" | Remote subagents (`isolation: "remote"`) when the session offers them. Otherwise local subagents in their own worktrees. For work that must outlive the session, a routine (`/schedule`). |
| "Cursor restart" | "a Claude Code restart" |
| "the Cursor dashboard" | `ListAgents`, or claude.ai/code for remote sessions |

## Not ported yet

- `make-bot-ui` wakes a Cursor Grok Bot routine over a Cursor webhook. The Claude Code counterpart is a routine with an API trigger. The skill is parked in `unported/make-bot-ui/` so it does not register.
- `automations/benny` depends on Cursor Automations with a Slack message trigger. Claude Code routines have no Slack trigger. The pack stays in `automations/benny/` with a notice. It never registered as skills.

## Fixes beyond the port

- `skills/poteto-mode/scripts/worktree-audit.sh` used BSD-only `stat -f` and `date -r` with errors suppressed. On Linux the most-recent-chat column came back empty, so a worktree a live session was using could be bucketed `safe`. The port picks GNU or BSD flags at startup and also searches the worktree's own transcript directory.
- Upstream playbooks re-read skills with `git show origin/main:pstack/skills/...` and run `node pstack/skills/...`, which only resolve inside the cursor/plugins repository. The port re-reads pstack's installed skill files, and `check-plan.mjs` checks for the matching `Re-read them at every tick` marker.

## Known gaps

- `typescript-best-practices` keeps upstream's `paths` frontmatter. Whether Claude Code auto-loads a skill by path is unverified, so treat it as loaded only when routed or invoked.
- Upstream's `reminder` frontmatter made `poteto-mode` re-prompt itself each turn in Cursor. The port moved its text into a **Sticky** paragraph in the skill body. Nothing re-injects it after context compaction.
- Subagents spawned as `general-purpose` (swarm workers, arena candidates) run at whatever effort Claude Code gives that built-in agent. Only pstack's own agents pin `xhigh`.
- Nesting depth for subagents that spawn subagents (orchestrate's sub-coordinators) is unverified in Claude Code. Upstream's "depth 3" claim was dropped.

## Verification

Run on 2026-09-24 against Claude Code with `claude --plugin-dir plugins/pstack`.

- `claude plugin validate --strict` passes for the marketplace and plugin manifests. In this Claude Code build it does not inspect skill or agent frontmatter.
- `claude plugin details pstack` loads 49 skills, 3 agents, and 1 `SessionStart` hook.
- `bun test orch watch-pr` in `skills/poteto-mode/scripts`: 52 pass, 0 fail.
- `tools/port-from-cursor.py` is idempotent. A second run changes 0 files.
- `check-plan.mjs` accepts the ported program template and reports `Program checklist lacks "Re-read them at every tick"` when that line is removed.
- `worktree-audit.sh` on a scratch repository with a transcript that touched one worktree: upstream reports `LAST_CHAT` empty and bucket `safe` on Linux. The port reports today's date and bucket `verify-recent-chat`.
- Live headless sessions confirmed the following:
  - The hook's context arrives with the plugin path resolved.
  - `pstack:readonly-agent` has no `Write`, `Edit`, or `Agent` tool and keeps the MCP tools.
  - `pstack:poteto-agent` resolves `${CLAUDE_PLUGIN_ROOT}` to the real `poteto-mode/SKILL.md`.
  - `/pstack:how` falls back to defaults with no config file, reads its template by relative path, and spawns `pstack:readonly-agent` on `opus`.
  - Asking for "pstack's unslop skill" makes the model read `skills/unslop/SKILL.md`. Before the hook listed skill names, it read `deslop` by mistake.
