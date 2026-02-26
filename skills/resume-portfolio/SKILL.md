---
name: resume-portfolio
description: |
  This skill should be used when the user asks to "continue portfolio",
  "resume portfolio", "pick up where I left off", "portfolio status",
  "what's next", or "show progress". Session entry point for ongoing projects.
---

# Portfolio Resume

Session entry point for continuing portfolio work. Detects where the user left off and recommends the next action.

## Workflow

### 1. Find Portfolio Projects

Scan the workspace for portfolio projects:

```bash
find . -maxdepth 3 -name "portfolio.json" -path "*/cogni-portfolio/*"
```

Each match represents a project. Extract the project slug from the directory name.

If no projects are found, tell the user no portfolio projects exist and suggest using the `setup` skill to create one.

### 2. Select Project

- If exactly one project is found, use it automatically.
- If multiple projects are found, present them to the user and ask which one to continue.

### 3. Run Project Status

Run the status script on the selected project directory:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

Parse the JSON output. The key fields are:
- `counts` -- entity counts per type
- `phase` -- current workflow phase (products, features, markets, solutions, enrichment, synthesis, export, complete)
- `next_actions` -- ordered list of recommended skills with reasons
- `completion` -- percentage progress for solutions, competitors, customers

### 4. Present Status Summary

Display a concise status dashboard:

**Header**: Company name (from portfolio.json) + project slug

**Progress table**:

| Entity | Count | Status |
|--------|-------|--------|
| Products | N | ... |
| Features | N | ... |
| Markets | N | ... |
| Solutions | N / expected | pct% |
| Competitors | N / solutions | pct% |
| Customers | N / markets | pct% |
| Claims | N total | V verified, D deviated, U unverified |

**Current phase**: The `phase` value, explained in plain language.

**Gaps**: If `missing_solutions` is non-empty, list the first few missing pairs. If competitors or customers are incomplete, note the counts.

### 5. Recommend Next Action

Present each entry from `next_actions`:
- Skill name and reason from the JSON
- Offer to proceed with the first recommended action

If the phase is `complete`, congratulate the user and suggest reviewing the output or running `export` for additional deliverables.

## Phase Reference

| Phase | Meaning |
|-------|---------|
| `products` | Portfolio initialized but no products defined |
| `features` | Products exist but no features added |
| `markets` | Features defined but no target markets |
| `solutions` | Feature x Market pairs need IS/DOES/MEANS messaging |
| `enrichment` | Solutions exist but competitor or customer analysis incomplete |
| `verification` | Claims submitted but unverified or deviated -- run verify skill |
| `synthesis` | All entities complete and claims verified, ready to generate overview |
| `export` | Overview generated, ready for deliverable export |
| `complete` | All workflow stages finished |
