---
name: synthesize
description: |
  This skill should be used when the user asks to "synthesize portfolio",
  "messaging repository", "portfolio overview", "aggregate portfolio",
  or "portfolio summary". Generates the complete structured messaging repository.
---

# Portfolio Synthesis

Aggregate all portfolio entities into a structured messaging repository -- the definitive reference document for sales and marketing messaging.

## Prerequisites

Before synthesis, verify the portfolio is sufficiently complete. Run validation:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/validate-entities.sh "<project-dir>"
```

And check project status:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

Minimum requirements for synthesis:
- At least 1 product defined
- At least 1 feature defined (with valid product_slug)
- At least 1 market defined
- At least 1 solution generated (Feature x Market)
- portfolio.json has company context filled in

Warn the user about gaps but allow synthesis with partial data if they choose to proceed.

## Workflow

### 1. Load All Entities

Read all entity files from the project directory:
- `portfolio.json` for company context
- All `products/*.json`
- All `features/*.json`
- All `markets/*.json`
- All `solutions/*.json`
- All `competitors/*.json` (if available)
- All `customers/*.json` (if available)

### 2. Generate README.md

Write a comprehensive `output/README.md` as the main messaging repository document. Structure:

```markdown
# [Company Name] Portfolio Messaging Repository

## Company Overview
[From portfolio.json]

## Products
[For each product: name, description, positioning, maturity, pricing tier]

## Product Deep Dives
[For each product:]
### [Product Name]
#### Features
[Table of features belonging to this product with IS descriptions]

## Target Markets
[For each market: description, segmentation, TAM/SAM/SOM summary]

## Solution Messaging Matrix
[Table: Feature x Market with IS/DOES/MEANS for each cell, grouped by product]

## Market Deep Dives
[For each market:]
### [Market Name]
#### Customer Profile
[Buyer profiles from customers/{market}.json]
#### Solutions by Product
[All solutions targeting this market, grouped by product, with full IS/DOES/MEANS]
#### Competitive Landscape
[Competitor analysis for each solution in this market]

## Feature Deep Dives
[For each feature:]
### [Feature Name] (Product: [Product Name])
#### Cross-Market Messaging
[How this feature's messaging varies across markets]
```

### 3. Generate Per-Market Summaries

For each market, create `output/{market-slug}.md` with:
- Market definition and sizing
- Customer profile
- All solutions targeting this market
- Competitive analysis per solution
- Recommended messaging priorities

### 4. Present Summary

Show the user:
- Total entities synthesized (W products, X features, Y markets, Z solutions)
- Completion percentage
- Files generated in `output/`
- Suggested next steps (export for proposals or marketing)

## Important Notes

- Synthesis is non-destructive -- it reads entity files and writes only to `output/`
- Re-running synthesis overwrites previous `output/` content
- The messaging repository is the input for the `export` skill
- Incomplete portfolios produce incomplete synthesis -- gaps are noted in the output
