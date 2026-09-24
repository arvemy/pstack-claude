# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Install is two commands, and setup is a short conversation.

## Install the plugin

In a Claude Code session, run:

```text
/plugin marketplace add arvemy/pstack-claude
/plugin install pstack@pstack-claude
```

Claude Code confirms the plugin is installed. From a shell, the same two steps are:

```bash
claude plugin marketplace add arvemy/pstack-claude
claude plugin install pstack@pstack-claude
```

To work on pstack itself, clone the repository to `~/pstack-claude` and load the plugin straight from the checkout:

```bash
claude --plugin-dir ~/pstack-claude/plugins/pstack
```

Plugin skills are namespaced. Every pstack command carries the `pstack:` prefix, as in `/pstack:poteto-mode`.

## Pick your models

Run:

```text
/pstack:setup-pstack
```

[`/pstack:setup-pstack`](../../skills/setup-pstack/SKILL.md) asks for a budget, shows you each role (code delegates, judgment, the review panels) with its Claude model, and asks what you want. Answer the questions. It writes `~/.claude/pstack/models.md`, a small config file every pstack skill reads.

Out of the box, code delegates, explorers, investigators, and swarm workers run on `sonnet` (Claude Sonnet 5). Prose, judgment, explainers, and synthesizers run on `opus` (Claude Opus 5.5). The hardest tasks run on `fable` (Claude Fable 5.1). The review panels in `/pstack:arena`, `/pstack:architect`, and `/pstack:interrogate` seat `fable`, `opus`, and `sonnet`, one seat each. Three Claude models share a lineage, so each seat also gets its own review lens.

The budget moves roles along the ladder `haiku` < `sonnet` < `opus` < `fable`. Setup offers four budgets:

- `unlimited — every role one tier up`
- `large — the defaults`
- `medium — no fable`
- `small — every role one tier down`

The budget doesn't change effort. pstack's own agents run at `xhigh` effort, set in their definitions. Your main session's effort is yours to set with `/effort`.

You only override what you care about. A role with no line in the file keeps the skill's default. To restore a default, delete that role's line. A rerun of `/pstack:setup-pstack` keeps any role whose model differs from the default. If you ran pstack in Cursor before, setup offers once to carry your old choices over.

You might be wondering how to run a role on your session's own model. Set it to `inherit` and pstack omits the Agent tool's `model` parameter, so the subagent runs on the parent session's model. `inherit` is not a model alias. For a panel role the value is a list, and one subagent runs per entry, `inherit` entries included, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/pstack:swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/pstack:setup-pstack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/pstack:create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.claude/skills/verify-<app>/`, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/pstack:create-verification-skill` yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers when it earns its place.

pstack skills read `~/.claude/pstack/models.md` each time they spawn a subagent, so your choices apply from the next pstack run.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/pstack:poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/pstack:poteto-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `/pstack:poteto-mode` is sticky. It stays on for the conversation until you opt out by saying so.

Next: [Route work through `/pstack:poteto-mode`](./02-poteto-mode.md).
