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
- At least 1 proposition generated (Feature x Market)
- portfolio.json has company context filled in

Also check claim verification status if `.claims/claims.json` exists:
- Read the claims registry and count by status
- If unverified or deviated claims exist, warn the user:
  ```
  Claim Verification Warning:
  - N unverified claims (not yet checked against sources)
  - N deviated claims (source discrepancies detected)
  Recommendation: Run the verify skill before synthesis.
  ```
- Allow synthesis to proceed if the user chooses, but flag unverified content in output

Warn the user about gaps but allow synthesis with partial data if they choose to proceed.

## Workflow

### 1. Load All Entities

Read all entity files from the project directory:
- `portfolio.json` for company context
- All `products/*.json`
- All `features/*.json`
- All `markets/*.json`
- All `propositions/*.json`
- All `competitors/*.json` (if available)
- All `customers/*.json` (if available)

### 2. Load Claim Verification Status

If `.claims/claims.json` exists, read it and build a lookup of claim status by statement text. This enables marking claims in the output with their verification status.

Claim status indicators for output:
- Verified claims: no marker needed (trusted)
- Resolved claims: no marker needed (user-approved)
- Deviated claims: mark with `[unverified]` in the output
- Unverified claims: mark with `[unverified]` in the output
- Source unavailable: mark with `[source unavailable]` in the output

### 3. Generate README.md

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

## Proposition Messaging Matrix
[Table: Feature x Market with IS/DOES/MEANS for each cell, grouped by product]

## Market Deep Dives
[For each market:]
### [Market Name]
#### Customer Profile
[Buyer profiles from customers/{market}.json]
#### Propositions by Product
[All propositions targeting this market, grouped by product, with full IS/DOES/MEANS]
#### Competitive Landscape
[Competitor analysis for each proposition in this market]

## Feature Deep Dives
[For each feature:]
### [Feature Name] (Product: [Product Name])
#### Cross-Market Messaging
[How this feature's messaging varies across markets]
```

### 4. Generate Per-Market Summaries

For each market, create `output/{market-slug}.md` with:
- Market definition and sizing
- Customer profile
- All propositions targeting this market
- Competitive analysis per proposition
- Recommended messaging priorities

### 5. Present Summary

Show the user:
- Total entities synthesized (W products, X features, Y markets, Z propositions)
- Completion percentage
- Files generated in `output/`
- Suggested next steps (export for proposals or marketing)

## Important Notes

- Synthesis is non-destructive -- it reads entity files and writes only to `output/`
- Re-running synthesis overwrites previous `output/` content
- The messaging repository is the input for the `export` skill
- Incomplete portfolios produce incomplete synthesis -- gaps are noted in the output
- If `.claims/claims.json` exists, claim verification status is reflected in the output
- Claims marked `[unverified]` signal that the source has not been checked -- readers should treat these with appropriate caution
