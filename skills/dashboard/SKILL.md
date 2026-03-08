---
name: dashboard
description: |
  Generate an interactive HTML dashboard showing the full portfolio status.
  Use whenever the user mentions dashboard, portfolio dashboard, portfolio view,
  "show me the portfolio", "visualize portfolio", status overview, or wants to
  see all portfolio data in a browser — even if they don't say "dashboard".
---

# Portfolio Dashboard

Generate a self-contained HTML dashboard that visualizes the entire portfolio — entity counts, completion progress, the Feature x Market matrix, market sizing, pricing, competitors, customer profiles, and claims status. The dashboard opens in the user's browser and supports drill-down navigation into every entity.

## Core Concept

The dashboard turns scattered JSON entity files into a single visual overview. Unlike the text-based `resume-portfolio` skill (quick status check) or `synthesize` (markdown messaging repository), the dashboard is designed for visual exploration — clicking through entities, scanning the proposition matrix, comparing pricing across markets, and spotting gaps at a glance.

It matters because portfolio data lives in dozens of small JSON files that are hard to reason about in aggregate. A visual dashboard makes coverage, gaps, and relationships immediately visible without reading markdown or running shell commands.

## Workflow

### 1. Find the Active Portfolio Project

Scan the workspace for `portfolio.json` files under `cogni-portfolio/` paths. If multiple projects exist, ask the user which one to open. Store the resolved project directory path.

### 2. Generate the Dashboard

Run the dashboard generator script:

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/dashboard/scripts/generate-dashboard.py "<project-dir>" [--theme <path-to-theme.md>]
```

The script:
- Reads `portfolio.json` and all entity directories (products, features, markets, propositions, solutions, competitors, customers)
- Reads `cogni-claims/claims.json` if present
- Runs `project-status.sh` for counts and completion data
- Parses a cogni-workspace theme.md file for colors, typography, and status colors (auto-discovers cogni-work theme if no `--theme` is given)
- Generates a self-contained HTML file at `<project-dir>/output/dashboard.html`
- Returns JSON with `{"status": "ok", "path": "<output-path>", "theme": "<name>"}` on success

The theme is a runtime variable. Any cogni-workspace theme.md file works — the parser extracts color palette tokens (`**Name**: \`#HEX\``), status colors, and typography from the markdown. To use a different theme, pass `--theme <path>` pointing to any theme.md in the workspace's `themes/` directory.

### 3. Open in Browser

```bash
open "<project-dir>/output/dashboard.html"
```

Tell the user the dashboard is open. If they want to refresh after making changes to entities, just rerun the script.

## Dashboard Sections

The generated HTML includes these sections, all in a single-page app with drill-down panels:

1. **Header** — Company name, industry, project slug, last updated
2. **Phase & Progress** — Current workflow phase with visual progress bar, completion percentages per entity type
3. **Entity Counts** — Card grid showing products, features, markets, propositions, solutions, competitors, customers with counts and expected totals
4. **Feature x Market Matrix** — Interactive grid. Each cell is color-coded (green = proposition + solution, yellow = proposition only, red = missing). Click a cell to expand IS/DOES/MEANS, pricing tiers, and competitor summary
5. **Markets Overview** — Cards per market with TAM/SAM/SOM bars, region badge, segmentation criteria. Click to see customer profiles and all propositions targeting that market
6. **Products & Features** — Grouped by product, showing feature descriptions and which markets each feature targets
7. **Solutions & Pricing** — Table of all solutions with implementation timeline and pricing tiers (PoV/S/M/L)
8. **Competitive Landscape** — Per-proposition competitor cards with strengths/weaknesses
9. **Claims Status** — Verification summary (verified, unverified, deviated, resolved) with progress bar
10. **Next Actions** — Recommended next skills from project-status

## Important Notes

- The dashboard is read-only — it shows portfolio state, it does not modify entities
- The HTML file is fully self-contained (inline CSS + JS, no external dependencies)
- Re-running the script overwrites the previous dashboard
- The dashboard lives at `output/dashboard.html` alongside the synthesis README
