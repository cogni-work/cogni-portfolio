---
name: resume-portfolio
description: |
  Resume, continue, or check status of a portfolio project.
  Use whenever the user mentions "continue portfolio", "resume portfolio",
  "pick up where I left off", "portfolio status", "what's next", "show progress",
  "where was I", "how far along", or opens a session that involves an existing
  cogni-portfolio project — even if they don't say "resume" explicitly.
---

# Portfolio Resume

Session entry point for returning to portfolio work. This skill orients the user by showing where they left off and what to do next — think of it as the dashboard view that keeps multi-session projects on track.

## Core Concept

Portfolio projects span multiple sessions and skills. Without a clear re-entry point, users lose context between sessions and waste time figuring out what they already did. This skill bridges that gap: it reads the project state, surfaces progress at a glance, and recommends the most valuable next step. The goal is to get the user back into productive flow within seconds.

## Workflow

### 1. Find Portfolio Projects

Scan the workspace for portfolio projects:

```bash
find . -maxdepth 3 -name "portfolio.json" -path "*/cogni-portfolio/*"
```

Each match represents a project (extract the slug from the directory name). If no projects are found, say so and suggest the `setup` skill.

### 2. Select Project

- One project found — use it automatically.
- Multiple projects — present them and ask which one to continue.

### 3. Run Project Status

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

The script returns JSON with `counts`, `phase`, `next_actions`, `completion`, and `claims`. These drive everything in the next steps.

### 4. Present Status Summary

Show a concise, scannable dashboard. Lead with the company name and project slug, then the progress table:

| Entity | Count | Status |
|--------|-------|--------|
| Products | N | |
| Features | N | |
| Markets | N | |
| Propositions | N / expected | pct% |
| Competitors | N / propositions | pct% |
| Customers | N / markets | pct% |
| Claims | N total | V verified, D deviated, U unverified |
| Uploads | N | pending ingestion (if > 0) |

After the table:
- **Phase** — translate the `phase` value into plain language (see reference below)
- **Uploads notice** — if `counts.uploads > 0`, always mention pending files regardless of phase
- **Gaps** — if `missing_propositions` is non-empty, list the first few missing pairs; note incomplete competitors/customers

Keep the tone warm and oriented toward action — this is a welcome-back moment, not a status report. The user should feel oriented, not overwhelmed.

### 5. Recommend Next Action

Present each entry from `next_actions` with the skill name and reason. Offer to proceed with the top recommendation immediately.

If the phase is `complete`, congratulate the user and suggest reviewing outputs or running `export` for additional deliverables.

## Phase Reference

| Phase | Meaning | What to do |
|-------|---------|------------|
| `products` | No products defined yet | Run `products` skill |
| `features` | Products exist, no features | Run `features` skill |
| `markets` | Features defined, no markets | Run `markets` skill |
| `propositions` | Feature x Market pairs need messaging | Run `propositions` skill |
| `enrichment` | Propositions exist, competitor/customer gaps remain | Run `compete` and/or `customers` |
| `verification` | Unverified or deviated claims pending | Run `verify` skill |
| `synthesis` | All entities complete, claims clean | Run `synthesize` skill |
| `export` | Overview generated, deliverables pending | Run `export` skill |
| `complete` | All workflow stages finished | Review outputs or re-export |
