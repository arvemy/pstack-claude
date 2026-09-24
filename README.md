# pstack for Claude Code

A Claude Code port of [poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack). The plugin lives in [`plugins/pstack`](./plugins/pstack/README.md). This repository is also its marketplace.

```
/plugin marketplace add arvemy/pstack-claude
/plugin install pstack@pstack-claude
```

Then run `/pstack:setup-pstack` and use `/pstack:poteto-mode`.

[`PORTING.md`](./PORTING.md) records every Cursor-to-Claude-Code mapping, the known gaps, and how the port was verified. [`tools/port-from-cursor.py`](./tools/port-from-cursor.py) reapplies the mechanical part to a newer upstream copy.
