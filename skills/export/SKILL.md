---
name: export
description: |
  Generate portfolio deliverables — proposals, marketing briefs, XLSX workbooks.
  Use whenever the user mentions export, proposal, brief, collateral, spreadsheet,
  "send to Excel", "create a deck", deliverable, "download portfolio", or wants
  to turn portfolio data into something shareable — even without saying "export".
---

# Portfolio Export

Transform portfolio entities into polished, shareable deliverables. This is where the portfolio's value becomes tangible — proposals close deals, briefs align marketing teams, and workbooks enable stakeholder analysis.

## Core Concept

Export reads entity files directly (products, features, markets, propositions, competitors, customers) and produces standalone deliverables. Each export type serves a different audience and purpose, but all draw from the same underlying data. The quality of exports depends on the completeness of upstream entities — missing competitors or customers won't block export, but the output will be thinner.

## Export Types

### 1. Proposition Proposal (Markdown)

A sales proposal for a specific proposition, targeting a specific customer in a specific market.

**Output**: `output/proposals/{feature-slug}--{market-slug}.md`

**Content structure**:

```markdown
# [Proposition headline — the MEANS statement]

## Executive Summary
[2-3 sentences: what we offer (IS), what it does for this buyer (DOES),
why it matters (MEANS). This is the entire proposal compressed into a paragraph.]

## The Challenge
[Customer pain points from the customer profile. Frame the buyer's world
before the solution exists — make them feel understood. Reference specific
pain points from customers/{market-slug}.json.]

## Our Approach
[IS and DOES statements expanded. Explain the capability and its
market-specific advantage. Be concrete — name the feature, describe
the mechanism, quantify the improvement where evidence supports it.]

## Why Us
[Differentiation from competitor analysis. Don't trash competitors —
position the proposition's unique angle. Reference specific competitor
weaknesses only where they contrast with genuine strengths.]

## Evidence
[From the proposition's evidence array. Present as brief case studies
or data points. Mark any [unverified] claims clearly.]

## Implementation Approach
[From the solution's implementation phases — phased plan with
durations. Only include if a solution exists for this proposition.]

## Investment
[Pricing tiers table from the solution — PoV, Small, Medium, Large
with price, currency, and scope. Framed as investment levels,
not a price list. Only include if a solution exists.]

## Next Steps
[Concrete call to action appropriate for B2B context:
demo scheduling, pilot program, technical evaluation.]
```

**Trigger**: "Create a proposal for [feature] in [market]"

### 2. Market Brief (Markdown)

Marketing content package for a specific target market, covering all propositions that address it.

**Output**: `output/briefs/{market-slug}.md`

**Content structure**:

```markdown
# [Market Name] — Marketing Brief

## Market Overview
[From market definition: segmentation, TAM/SAM/SOM, key dynamics]

## Target Buyer
[From customer profile: role, seniority, pain points, buying criteria.
Write as a portrait of the person, not a data dump.]

## Value Propositions
[All propositions targeting this market, each with IS/DOES/MEANS.
Group by product. For each, include a one-line elevator pitch
derived from the MEANS statement.]

## Competitive Positioning
[Aggregated differentiation across all propositions in this market.
Identify themes — where the portfolio consistently wins.]

## Recommended Messaging Themes
[3-5 messaging angles that cut across propositions. These are the
themes a marketing team would use in campaigns, not individual
proposition messages.]
```

**Trigger**: "Create a marketing brief for [market]"

### 3. Portfolio Workbook (XLSX)

Structured spreadsheet with all portfolio data for analysis and sharing.

**Output**: `output/portfolio.xlsx`

**Sheets**:
- **Products**: All products with positioning, pricing tier, and maturity
- **Features**: All features with descriptions, categories, and parent product
- **Markets**: All markets with segmentation and TAM/SAM/SOM
- **Proposition Matrix**: Feature x Market grid with IS/DOES/MEANS, grouped by product
- **Solutions**: Implementation phases and pricing tiers per proposition
- **Competitors**: Competitive analysis per proposition
- **Customers**: Buyer profiles per market
- **Summary**: Portfolio statistics and completion status

To create the XLSX file, use the `document-skills:xlsx` skill. Prepare the data as structured content and delegate spreadsheet creation. If `document-skills:xlsx` is not available, offer CSV files instead — one per sheet, in `output/csv/`.

**Trigger**: "Export portfolio to Excel" or "generate spreadsheet"

### 4. Full Export

Generate all deliverables at once: proposals for each proposition, briefs for each market, and the portfolio workbook.

**Trigger**: "Export everything" or "full export"

## Workflow

### 1. Check Prerequisites

Read `output/README.md` to confirm synthesis has been run. If not, suggest running the `synthesize` skill first.

If `cogni-claims/claims.json` exists, read it and check for unresolved deviations or unverified claims. If found, warn the user:
```
Claim Status: N unverified, N deviated (unresolved)
Exports will include verification status markers for unverified claims.
Consider running the verify skill first for highest-quality output.
```

### 2. Determine Export Scope

Infer the export type from the user's request. Only ask for clarification if genuinely ambiguous — if they said "create a proposal for cloud-monitoring in mid-market-saas", go directly to proposal generation without asking.

When the request is vague ("export my portfolio"), present the options:
- A specific proposal (which proposition?)
- A specific brief (which market?)
- The portfolio workbook
- Everything

### 3. Gather Source Data

Read all entity files relevant to the export type:
- **Proposals** need: the proposition, its feature, its product, the market, the customer profile, the competitor analysis, and the solution (if available)
- **Briefs** need: the market, all propositions targeting it, customer profile, and all competitor analyses for those propositions
- **Workbook** needs: everything

When source data is incomplete (no customer profile, no competitors), proceed anyway but note the gap in the output. A proposal without competitor data skips the "Why Us" section rather than inventing differentiation. A brief without customer data uses the market definition to approximate the buyer profile and flags this.

### 4. Generate Deliverables

Write each deliverable following the content structures above. Keep these principles in mind:

**Tone**: Professional but direct. B2B buyers are busy — lead with value, not preamble. Avoid marketing superlatives ("revolutionary", "best-in-class") in favor of specific, defensible claims.

**Length**: Proposals should be 1-2 pages. Briefs should be 2-3 pages. Enough to be useful, short enough to actually get read.

**Claims**: If `cogni-claims/claims.json` exists, cross-reference evidence statements. Mark unverified or deviated claims with `[unverified]`. Include a "Data Quality" note when unverified claims are present, advising readers to validate flagged data points independently.

### 5. Present Results

List generated files with paths. Suggest how to use each deliverable:
- Proposals: share with sales team, customize per prospect
- Briefs: distribute to marketing for campaign planning
- Workbook: share with leadership for portfolio review

## Important Notes

- Exports read from entity files directly, not from `output/README.md` — they are independently generated
- All exports go to subdirectories within `output/`
- Re-running an export overwrites previous output for that deliverable
- **Content Language**: Read `portfolio.json` in the project root. If a `language` field is present, generate all user-facing text content (proposals, briefs, summaries) in that language. JSON field names and slugs remain in English. If no `language` field is present, default to English.
- Running `synthesize` first is recommended but not strictly required
