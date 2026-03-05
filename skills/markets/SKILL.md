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

A target market is defined by segmentation criteria (geography, company size, vertical, etc.) and sized using the TAM/SAM/SOM framework:

- **TAM** (Total Addressable Market): Total global demand for the capability category
- **SAM** (Serviceable Available Market): The portion reachable given geography, segment, and channel constraints
- **SOM** (Serviceable Obtainable Market): Realistically achievable share in 1-3 years

Markets matter because every downstream entity depends on them. Propositions combine a feature with a market. Customer profiles are market-scoped. Competitive analysis is proposition-scoped (and therefore market-scoped). Poorly defined markets propagate fuzzy thinking through the entire portfolio; precise markets make messaging, differentiation, and sizing sharper everywhere.

## Workflow

### 1. Propose Markets

Analyze existing products (read `products/`), their features (read `features/`), and the company context (read `portfolio.json`) to propose 3-7 candidate target markets. For each candidate, provide:

- Suggested slug and name
- Brief rationale (why this market fits these features)
- Initial segmentation criteria

Present candidates as a numbered list and ask the user to select which markets to pursue.

### 2. Size Selected Markets

For each selected market, determine TAM/SAM/SOM. Two modes:

**Web research (default)**: Delegate to a subagent (Agent tool) to search for market reports, analyst estimates, and industry data. Provide the subagent with:
- Market name and segmentation criteria
- Feature categories being addressed
- Geographic scope

Multiple agents can be launched in parallel for different markets.

**LLM estimation (fallback)**: When web search is unavailable, generate reasonable estimates from training knowledge. Clearly label these as estimates and note confidence level.

### 3. Create Market Entities

Write each market as a JSON file to `markets/{slug}.json`:

```json
{
  "slug": "mid-market-saas",
  "name": "Mid-Market SaaS Companies",
  "description": "SaaS companies with 50-500 employees and $5M-$100M ARR in DACH region.",
  "segmentation": {
    "geography": "DACH",
    "company_size": "50-500 employees",
    "revenue_range": "$5M-$100M ARR",
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

Required: `slug`, `name`, `description`. Optional: `segmentation`, `tam`, `sam`, `som`.

### 4. Review with User

Present proposed markets for review. Ask explicitly:

- Are these the right segments? Missing any obvious market?
- Do the segmentation criteria feel right — too narrow or too broad?
- Do the TAM/SAM/SOM numbers pass the gut check?
- Any markets that overlap and should be merged?

The user knows their business better than any research — iterate until the markets feel accurate.

### 5. Validate Against Portfolio

Cross-reference markets with existing portfolio entities:

- **Features**: Preview the Feature x Market matrix to show which propositions will need to be generated. Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to generate this overview.
- **Existing propositions**: Check if any propositions reference markets that don't exist (orphaned references)
- **Market overlap**: Flag markets with near-identical segmentation criteria — they may need merging

These checks catch gaps early: a market with zero relevant features suggests a misfit; a feature with no matching market suggests an untapped opportunity.

### Editing Markets

Read the existing market JSON, apply the user's changes, and write back. Changing a market slug requires renaming the file and updating any dependent entities (propositions in `propositions/`, customers in `customers/`, competitors in `competitors/`).

### Listing Markets

Read all JSON files in the project's `markets/` directory. Present as a table with segmentation summary and sizing status (sized vs. unsized).

## Market Selection Criteria

When proposing markets, prioritize segments where:
- Multiple features create combined value (proposition density)
- The company has existing relationships or domain expertise
- Market size justifies the effort (SOM > meaningful revenue threshold)
- Competitive intensity is manageable

## Important Notes

- Markets should be specific enough to produce distinct messaging but broad enough to represent real revenue opportunity
- Aim for 2-5 target markets; more than 7 usually means segments overlap
- TAM/SAM/SOM values are always estimates -- label sources clearly
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
