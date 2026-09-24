---
name: setup-pstack
description: Configure which Claude model pstack uses per role and how much budget it spends. Writes `~/.claude/pstack/models.md`, which overrides the skill defaults. Use for /pstack:setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
disable-model-invocation: true
---

# Setup pstack

Write `~/.claude/pstack/models.md`, the file every pstack skill reads for its per-role model.

## Steps

### 1. Know the choices

A role takes one of the Agent tool's model aliases, or `inherit`.

- `fable` is Claude Fable 5.1, the most capable and the most expensive.
- `opus` is Claude Opus 5.5.
- `sonnet` is Claude Sonnet 5, fast and cheaper.
- `haiku` is Claude Haiku 4.5, the cheapest. It has a 200K context and no effort control, so keep it to bulk reading.
- `inherit` runs the role on the parent session's model. Skills omit the Agent `model` parameter for it.

The ladder, cheapest first, is `haiku` < `sonnet` < `opus` < `fable`. There is nothing to detect. If the session rejects an alias, for example because an organization disables a model, say so and offer only the rest.

### 2. Load current state

The default role-to-model mapping is the file shape in step 5. If `~/.claude/pstack/models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from the defaults. A line whose role is not in step 5 is from a retired role. Drop it. A value that is not one of the five choices needs a choice.

If `~/.cursor/rules/pstack-models.mdc` exists, the user ran Cursor pstack before. Offer once to carry its choices over, translating `claude-opus-*` and `gpt-*` to `opus`, `claude-sonnet-*` and `grok-*` to `sonnet`, and `inherit-parent` or `auto` to `inherit`.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Use AskUserQuestion. Offer these four options with these exact labels, and name the current budget when the file records one.

- `unlimited — every role one tier up`
- `large — the defaults`
- `medium — no fable`
- `small — every role one tier down`

**(b) Apply it.** Build the working table from the defaults in step 5. On a re-run, keep any role whose value differs from its default. Then apply the budget to the other roles.

- `large` leaves the defaults.
- `unlimited` moves every single-model role one tier up the ladder. `fable` stays `fable`.
- `medium` moves every single-model `fable` role down to `opus`.
- `small` moves every single-model role one tier down the ladder. `haiku` stays `haiku`.
- `inherit` never moves.

Panel roles (arena runners, arena cross-judge pool, architect runners, interrogate reviewers) take a fixed list per budget, so their entries stay distinct models. `unlimited` and `large` use `fable, opus, sonnet`. `medium` and `small` use `opus, sonnet, haiku`.

Effort is not part of the budget. pstack's own agents run at `xhigh` effort, set in their definitions. The main session's effort is the user's to set with `/effort`.

**(c) Show the roles and confirm.** Show every role with its model. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the five choices. Use AskUserQuestion. For panel roles the value is a list, and one subagent runs per entry, `inherit` entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena selects one value from it that differs from the parent's model when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every value written must be `fable`, `opus`, `sonnet`, `haiku`, or `inherit`. If a chosen value is anything else, stop and ask again.

### 5. Write the file

Create `~/.claude/pstack/` if it does not exist, then write `~/.claude/pstack/models.md` with a `# budget` line naming the chosen label and one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape, with the `large` defaults:

```
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# Values are fable, opus, sonnet, haiku, or inherit. With inherit the role runs on the parent session's model (omit the Agent `model` parameter). An inherit entry in a panel list still counts toward its fan-out.
# budget: large
feature, refactoring: sonnet
bug-fix: sonnet
perf-issue: sonnet
hillclimb: sonnet
judgment and prose: opus
hardest tasks: fable
how explorer: sonnet
how explainer: opus
why investigators: sonnet
why synthesizer: opus
reflect tooling: opus
reflect judgment, divergent, synthesizer: opus
arena runners: fable, opus, sonnet
arena cross-judge pool: fable, opus, sonnet
swarm workers: sonnet
architect runners: fable, opus, sonnet
interrogate reviewers: fable, opus, sonnet
```

### 6. Confirm

Tell the user the file was written. pstack skills read it each time they spawn a subagent, so it applies from the next pstack run. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /pstack:create-verification-skill." On yes, read and follow the sibling `create-verification-skill` skill (`../create-verification-skill/SKILL.md`). On no, move on without pushing.
