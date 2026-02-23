---
name: export
description: |
  This skill should be used when the user asks to "export portfolio",
  "create proposal", "generate spreadsheet", "marketing brief",
  "export messaging", or "create deliverable". Generates downstream
  deliverables in markdown and XLSX formats.
---

# Portfolio Export

Generate downstream deliverables from the portfolio messaging repository. Supports two output formats: markdown narratives and XLSX data files.

## Export Types

### 1. Solution Proposal (Markdown)

A sales proposal for a specific solution, targeting a specific customer in a specific market.

**Output**: `output/proposals/{feature-slug}--{market-slug}.md`

**Content structure**:
- Executive summary (MEANS statement as headline)
- The challenge (customer pain points from customer profile)
- Our approach (IS and DOES statements)
- Why us (differentiation from competitor analysis)
- Evidence (from solution evidence array)
- Next steps

**Trigger**: "Create a proposal for [feature] in [market]"

### 2. Market Brief (Markdown)

Marketing content package for a specific target market, covering all solutions that address it.

**Output**: `output/briefs/{market-slug}.md`

**Content structure**:
- Market overview (from market definition)
- Target buyer (from customer profile)
- Value propositions (all solutions targeting this market)
- Competitive positioning (aggregated differentiation)
- Recommended messaging themes

**Trigger**: "Create a marketing brief for [market]"

### 3. Portfolio Workbook (XLSX)

Structured spreadsheet with all portfolio data for analysis and sharing.

**Output**: `output/portfolio.xlsx`

**Sheets**:
- **Products**: All products with positioning, pricing tier, and maturity
- **Features**: All features with descriptions, categories, and parent product
- **Markets**: All markets with segmentation and TAM/SAM/SOM
- **Solution Matrix**: Feature x Market grid with IS/DOES/MEANS, grouped by product
- **Competitors**: Competitive analysis per solution
- **Customers**: Buyer profiles per market
- **Summary**: Portfolio statistics and completion status

**Trigger**: "Export portfolio to Excel" or "generate spreadsheet"

To create the XLSX file, use the `document-skills:xlsx` skill. Prepare the data as structured content and delegate spreadsheet creation.

### 4. Full Export

Generate all deliverables at once: proposals for each solution, briefs for each market, and the portfolio workbook.

**Trigger**: "Export everything" or "full export"

## Workflow

### 1. Check Prerequisites

Read `output/README.md` to confirm synthesis has been run. If not, suggest running the `synthesize` skill first.

If `.claims/claims.json` exists, read it and check for unresolved deviations or unverified claims. If found, warn the user:
```
Claim Status: N unverified, N deviated (unresolved)
Exports will include verification status markers for unverified claims.
Consider running the verify skill first for highest-quality output.
```

### 2. Determine Export Scope

Ask the user what to export:
- A specific proposal (which solution?)
- A specific brief (which market?)
- The portfolio workbook
- Everything

### 3. Generate Deliverables

Read the relevant entity files and generate output. For markdown exports, write directly. For XLSX, delegate to `document-skills:xlsx`.

### 4. Present Results

List generated files with paths and sizes. Suggest how to use each deliverable.

## Important Notes

- Exports read from entity files, not from `output/README.md` -- they are independently generated
- Running `synthesize` first is recommended but not strictly required
- Proposals and briefs use professional but concise language suitable for B2B contexts
- XLSX export requires the `document-skills:xlsx` skill to be available
- All exports go to subdirectories within `output/`
- If `.claims/claims.json` exists, claims with status `deviated` or `unverified` are marked with `[unverified]` in markdown exports and flagged in the XLSX Summary sheet
- Proposals and briefs include a "Data Quality" note when unverified claims are present, advising readers to validate flagged data points independently
