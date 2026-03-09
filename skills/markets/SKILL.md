---
name: markets
description: |
  Discover, evaluate, and size target markets for the portfolio.
  Use whenever the user mentions target markets, market segments, TAM SAM SOM,
  market sizing, "which markets to enter", market selection, addressable market,
  segmentation, or wants to define who they're selling to — even if they don't
  say "market" explicitly.
---

# Market Discovery and Sizing

Propose, evaluate, and size target markets for the portfolio. Each market is a distinct customer segment where features translate into specific advantages and benefits.

## Core Concept

A target market is defined by a **region** and **segmentation criteria** (company size, vertical, etc.), sized using TAM/SAM/SOM:

- **TAM** (Total Addressable Market): Total global demand for the capability category
- **SAM** (Serviceable Available Market): The portion reachable given region, segment, and channel constraints
- **SOM** (Serviceable Obtainable Market): Realistically achievable share in 1-3 years

Every market belongs to exactly one **region** — a standardized trading area from the region taxonomy (see `$CLAUDE_PLUGIN_ROOT/skills/setup/references/regions.json`). The same customer segment in different regions produces separate market entities because sizing, messaging, competitors, and buyer behaviour differ by region. A "Mid-Market SaaS" segment in DACH and in the US are two distinct markets with independent TAM/SAM/SOM, propositions, and competitive landscapes.

Markets matter because every downstream entity depends on them. Propositions combine a feature with a market. Customer profiles are market-scoped. Competitive analysis is proposition-scoped (and therefore market-scoped). Poorly defined markets propagate fuzzy thinking through the entire portfolio; precise markets make messaging, differentiation, and sizing sharper everywhere.

## Workflow

### 1. Select Target Regions

Before proposing market segments, establish which regions to target. Read the region taxonomy from `$CLAUDE_PLUGIN_ROOT/skills/setup/references/regions.json` and present the available regions. Ask the user which regions to focus on — a typical expansion path starts narrow (e.g., `de` or `dach`) and widens over time (`eu`, `us`, etc.).

If markets already exist, show a region summary of current coverage:

| Region | Markets | Propositions |
|---|---|---|
| dach | 2 | 6 |
| us | 0 | 0 |

This makes expansion gaps visible at a glance.

### 2. Propose Markets

Analyze existing products (read `products/`), their features (read `features/`), and the company context (read `portfolio.json`) to propose 3-7 candidate target markets per selected region. For each candidate, provide:

- Suggested slug (format: `{segment}-{region}`, e.g., `mid-market-saas-dach`)
- Name (include region in parentheses, e.g., "Mid-Market SaaS Companies (DACH)")
- Region code
- Brief rationale (why this market fits these features in this region)
- Initial segmentation criteria (non-geographic)

Present candidates as a numbered list and ask the user to select which markets to pursue.

### 3. Size Selected Markets

For each selected market, determine TAM/SAM/SOM. Two modes:

**Web research (default)**: Delegate to a subagent (Agent tool) to search for market reports, analyst estimates, and industry data. Provide the subagent with:
- Market name and segmentation criteria
- Feature categories being addressed
- Region (use the region's scope countries for targeted search queries)

Multiple agents can be launched in parallel for different markets. Use the region's default currency from the taxonomy for sizing values.

**LLM estimation (fallback)**: When web search is unavailable, generate reasonable estimates from training knowledge. Clearly label these as estimates and note confidence level.

### 4. Create Market Entities

Write each market as a JSON file to `markets/{slug}.json`. The slug format is `{segment}-{region}`:

```json
{
  "slug": "mid-market-saas-dach",
  "name": "Mid-Market SaaS Companies (DACH)",
  "region": "dach",
  "description": "SaaS companies with 50-500 employees and EUR 5M-100M ARR in DACH region.",
  "segmentation": {
    "company_size": "50-500 employees",
    "revenue_range": "EUR 5M-100M ARR",
    "vertical": "Software as a Service"
  },
  "tam": {
    "value": 5000000000,
    "currency": "EUR",
    "description": "Total addressable market for cloud monitoring in global SaaS",
    "source": "Gartner 2025"
  },
  "sam": {
    "value": 500000000,
    "currency": "EUR",
    "description": "Serviceable market in DACH mid-market SaaS",
    "source": "Internal estimate"
  },
  "som": {
    "value": 15000000,
    "currency": "EUR",
    "description": "Obtainable share in first 3 years",
    "source": "Bottom-up: 150 customers x 100K EUR ACV"
  },
  "created": "2026-01-15"
}
```

Required: `slug`, `name`, `region`, `description`. Optional: `segmentation`, `tam`, `sam`, `som`.

The `region` must be a valid code from the region taxonomy (`$CLAUDE_PLUGIN_ROOT/skills/setup/references/regions.json`). Use the region's default currency for TAM/SAM/SOM values. Do not put geography in `segmentation` — that is expressed by `region`.

### 5. Review with User

Present proposed markets for review. Ask explicitly:

- Are these the right segments? Missing any obvious market?
- Do the segmentation criteria feel right — too narrow or too broad?
- Do the TAM/SAM/SOM numbers pass the gut check?
- Any markets that overlap and should be merged?

The user knows their business better than any research — iterate until the markets feel accurate.

### 6. Validate Against Portfolio

Cross-reference markets with existing portfolio entities:

- **Features**: Preview the Feature x Market matrix to show which propositions will need to be generated. Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to generate this overview.
- **Existing propositions**: Check if any propositions reference markets that don't exist (orphaned references)
- **Market overlap**: Flag markets with near-identical segmentation criteria — they may need merging

These checks catch gaps early: a market with zero relevant features suggests a misfit; a feature with no matching market suggests an untapped opportunity.

### Editing Markets

Read the existing market JSON, apply the user's changes, and write back. Changing a market slug requires a cascading rename — this is not optional, as orphaned references break downstream skills:

1. Rename the market file from `markets/{old-slug}.json` to `markets/{new-slug}.json` and update `slug` inside
2. Run the cascade script to update all dependent entities (propositions, solutions, competitors, customers):
   ```bash
   $CLAUDE_PLUGIN_ROOT/scripts/cascade-rename.sh <project-dir> market <old-slug> <new-slug>
   ```
3. Report the script's output (changed files) to the user

### Listing Markets

Read all JSON files in the project's `markets/` directory. Present as a table grouped by region with segmentation summary and sizing status:

| Region | Market | Vertical | Size | TAM | SOM |
|---|---|---|---|---|---|
| dach | mid-market-saas-dach | SaaS | 50-500 emp | EUR 5B | EUR 15M |
| dach | enterprise-fintech-dach | Fintech | 500+ emp | EUR 8B | EUR 20M |
| us | (none) | — | — | — | — |

## Market Selection Criteria

When proposing markets, prioritize segments where:
- Multiple features create combined value (proposition density)
- The company has existing relationships or domain expertise
- Market size justifies the effort (SOM > meaningful revenue threshold)
- Competitive intensity is manageable

## Important Notes

- Markets should be specific enough to produce distinct messaging but broad enough to represent real revenue opportunity
- Aim for 2-5 target markets per region; more than 7 per region usually means segments overlap
- The same segment in different regions = different markets (different sizing, messaging, competitors)
- TAM/SAM/SOM values are always estimates -- label sources clearly and use the region's default currency
- Valid region codes are defined in `$CLAUDE_PLUGIN_ROOT/skills/setup/references/regions.json`
- **Content Language**: Read `portfolio.json` in the project root. If a `language` field is present, generate all user-facing text content (market descriptions, segmentation labels, rationale) in that language. JSON field names and slugs remain in English. If no `language` field is present, default to English.
- **Communication Language**: If `portfolio.json` has a `language` field, communicate with the user in that language (status messages, instructions, recommendations, questions). Technical terms, skill names, and CLI commands remain in English. Default to English if no `language` field is present.
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
