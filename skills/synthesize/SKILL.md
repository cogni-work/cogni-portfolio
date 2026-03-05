---
name: synthesize
description: |
  Aggregate all portfolio entities into a structured messaging repository.
  Use whenever the user mentions synthesize, portfolio overview, messaging repository,
  aggregate portfolio, portfolio summary, "put it all together", "compile portfolio",
  or wants a single document covering all products, markets, and propositions —
  even if they don't say "synthesize" explicitly.
---

# Portfolio Synthesis

Aggregate all portfolio entities into a structured messaging repository — the definitive reference document for sales and marketing messaging.

## Core Concept

Synthesis is where scattered entity files become a coherent story. Products, features, markets, propositions, competitors, and customers each live in isolated JSON files optimized for creation and editing. But no one reads JSON files — sales teams need a document they can scan before a call, marketing teams need a matrix they can mine for campaign angles, and leadership needs a single view of the portfolio's coverage and gaps.

The messaging repository (`output/README.md`) serves all three audiences. Its structure mirrors the way people actually use portfolio data: top-down from company overview through products and markets, then deep dives that cross-reference entities. The Proposition Messaging Matrix is the centrepiece — it makes Feature x Market coverage visible at a glance, revealing both strengths (where messaging is sharp) and gaps (where it's missing or generic).

This matters because synthesis is the quality gate before deliverables. If the README reads well, exports (proposals, briefs, workbooks) will be strong. If it exposes thin messaging or missing entities, the user knows exactly where to go back and improve.

## Prerequisites

Before synthesis, verify the portfolio is sufficiently complete:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/validate-entities.sh "<project-dir>"
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

Minimum requirements:
- At least 1 product, 1 feature (with valid product_slug), 1 market, and 1 proposition
- `portfolio.json` has company context filled in

If `cogni-claims/claims.json` exists, check claim verification status:
- Count claims by status (verified, deviated, unverified, source unavailable)
- If unverified or deviated claims exist, warn the user and recommend running the `verify` skill first
- Allow synthesis to proceed if the user chooses — flag unverified content in the output

Warn about gaps but allow synthesis with partial data if the user chooses to proceed. An incomplete synthesis is more useful than no synthesis — gaps become visible and actionable.

## Workflow

### 1. Load All Entities

Read all entity files from the project directory:
- `portfolio.json` for company context
- All `products/*.json`, `features/*.json`, `markets/*.json`, `propositions/*.json`
- All `solutions/*.json` (if available — implementation plans and pricing)
- All `competitors/*.json` and `customers/*.json` (if available)

If `cogni-claims/claims.json` exists, build a lookup of claim status by statement text for marking claims in the output:
- Verified / resolved claims: no marker needed (trusted)
- Deviated / unverified claims: mark with `[unverified]`
- Source unavailable: mark with `[source unavailable]`

### 2. Generate README.md

Write `output/README.md` as the main messaging repository. The structure is designed so each section serves a different use case — the top sections give quick orientation, the matrix gives coverage visibility, and the deep dives provide the detail needed for specific sales or marketing tasks.

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

## Solution Overview
[For each solution: proposition, implementation phases summary, pricing tiers table (PoV/S/M/L)]

## Market Deep Dives
[For each market:]
### [Market Name]
#### Customer Profile
[Buyer profiles from customers/{market}.json]
#### Propositions by Product
[All propositions targeting this market, grouped by product, with full IS/DOES/MEANS]
#### Solution Plans
[Implementation phases and pricing tiers for each proposition in this market, if solution exists]
#### Competitive Landscape
[Competitor analysis for each proposition in this market]

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
- All propositions targeting this market
- Competitive analysis per proposition
- Recommended messaging priorities

These standalone market files are useful for handing directly to a sales rep or marketing lead who owns a specific segment.

### 4. Review with User

Present a synthesis summary before finalizing:

- Total entities synthesized (W products, X features, Y markets, Z propositions)
- Completion percentage from project-status
- Coverage gaps (missing propositions, markets without customer profiles, propositions without competitor analysis)
- Claim verification status (if applicable)
- Files generated in `output/`

Ask explicitly:
- Does the README structure capture what you need?
- Any sections to expand or trim?
- Ready to proceed to export, or want to fill gaps first?

The user may want to iterate — go back and add missing entities, then re-synthesize. This is the intended workflow: synthesize exposes gaps, upstream skills fill them, re-synthesize produces a more complete repository.

## Important Notes

- Synthesis is non-destructive — it reads entity files and writes only to `output/`
- Re-running synthesis overwrites previous `output/` content
- The messaging repository is the primary input for the `export` skill
- Incomplete portfolios produce incomplete synthesis — gaps are noted in the output
- Claims marked `[unverified]` signal the source has not been checked — readers should treat these with appropriate caution
