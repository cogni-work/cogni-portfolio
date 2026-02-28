---
name: markets
description: |
  This skill should be used when the user asks to "discover markets",
  "target markets", "TAM SAM SOM", "market sizing", "select markets",
  "add a market", or "which markets to target". Proposes and sizes target markets.
---

# Market Discovery and Sizing

Propose, evaluate, and size target markets for the portfolio. Each market is a distinct customer segment where features translate into specific advantages and benefits.

## Core Concept

A target market is defined by segmentation criteria (geography, company size, vertical, etc.) and sized using the TAM/SAM/SOM framework:

- **TAM** (Total Addressable Market): Total global demand for the capability category
- **SAM** (Serviceable Available Market): The portion reachable given geography, segment, and channel constraints
- **SOM** (Serviceable Obtainable Market): Realistically achievable share in 1-3 years

## Workflow

### 1. Propose Markets

Analyze existing products (read `products/`), their features (read `features/`), and the company context (read `portfolio.json`) to propose 3-7 candidate target markets. For each candidate, provide:

- Suggested slug and name
- Brief rationale (why this market fits these features)
- Initial segmentation criteria

Present candidates as a numbered list and ask the user to select which markets to pursue.

### 2. Size Selected Markets

For each selected market, determine TAM/SAM/SOM. Two modes are available:

**LLM estimation (default)**: Generate reasonable estimates from training knowledge. Clearly label these as estimates and note confidence level.

**Web research (optional)**: When the user requests research-backed sizing, delegate to the `market-researcher` agent which performs web searches for market data. Invoke with:
- Market name and segmentation criteria
- Feature categories being addressed
- Geographic scope

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

### 4. Review Feature x Market Matrix

After markets are defined, show the user the Feature x Market matrix to preview which propositions will need to be generated:

| Feature \ Market | mid-market-saas | enterprise-fintech |
|---|---|---|
| cloud-monitoring | pending | pending |
| api-gateway | pending | pending |

Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to generate this overview.

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
