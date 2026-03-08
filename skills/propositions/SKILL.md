---
name: propositions
description: |
  Generate and manage IS/DOES/MEANS (FAB) value propositions per Feature x Market pair.
  Use whenever the user mentions propositions, messaging, value props, IS DOES MEANS,
  feature advantage benefit, FAB, "map features to markets", "why should they buy",
  differentiation, or wants to articulate market-specific value — even if they don't
  say "proposition" explicitly.
---

# Proposition Generation

Generate and manage IS/DOES/MEANS messaging for each Feature x Market combination. Propositions are where the portfolio comes alive -- transforming market-independent features into market-specific value that buyers recognize and pay for.

## Core Concept

A proposition answers the question: "Why should a buyer in THIS market care about THIS feature?" It does so through the IS/DOES/MEANS (FAB) messaging pyramid:

- **IS** (Feature): What the product capability is -- factual, market-independent. Restated from the feature entity.
- **DOES** (Advantage): What the feature achieves for this specific market -- the functional or operational improvement. Market-specific.
- **MEANS** (Benefit): What the advantage means for the buyer -- the business outcome or emotional payoff. Market-specific.

The same feature produces different DOES and MEANS statements for different markets because buyers in each segment face different problems, use different language, and value different outcomes. If the DOES/MEANS could apply to any market, the messaging is too generic and the markets may not be distinct enough.

This matters because propositions are the bridge between what you build and what the market buys. Every downstream deliverable -- competitor battlecards, customer profiles, pitch decks, proposals -- draws from proposition messaging. Weak propositions produce weak sales materials; sharp propositions make differentiation obvious.

## Workflow

### 1. Identify Pending Propositions

Run the project status script to find missing propositions:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

The `missing_propositions` array lists Feature x Market pairs without proposition files. Review the Feature x Market matrix to understand coverage gaps.

### 2. Generate Propositions

Two generation modes:

**Single proposition**: Generate one proposition interactively. Read the feature, its parent product, and the market JSON files, then craft IS/DOES/MEANS statements with the user.

**Batch generation**: For multiple pending propositions, delegate each to the `proposition-generator` agent. Launch agents in parallel for independent Feature x Market pairs.

**Web research (optional)**: When the user requests research-backed messaging, delegate to a subagent (Agent tool) to search for industry benchmarks, competitor claims, and supporting evidence relevant to each market segment. Add findings to the `evidence` array. This is especially useful for quantifying DOES statements with real market data.

### 3. Proposition Quality Criteria

Strong IS/DOES/MEANS statements follow these patterns:

**IS** (restate from feature, may be slightly adapted for market context):
- Factual, capability-focused
- No superlatives or marketing language

**DOES** (market-specific advantage):
- Quantified where possible ("reduces X by Y%")
- References the specific pain point of this market segment
- Action-oriented verb (reduces, eliminates, accelerates, enables)

**MEANS** (market-specific benefit):
- Business outcome the buyer cares about
- References the buyer's strategic goals or KPIs
- Connects operational advantage to commercial impact

### 4. Write Proposition Entities

Write each proposition to `propositions/{feature-slug}--{market-slug}.json`:

```json
{
  "slug": "cloud-monitoring--mid-market-saas",
  "feature_slug": "cloud-monitoring",
  "market_slug": "mid-market-saas",
  "is_statement": "Real-time cloud infrastructure monitoring with automated alerting for servers, containers, and network components.",
  "does_statement": "Reduces mean-time-to-resolution by 60% through intelligent alert correlation, eliminating alert fatigue in growing engineering teams.",
  "means_statement": "Mid-market SaaS companies maintain 99.95% uptime SLAs without hiring additional SRE staff, protecting revenue during rapid scaling.",
  "evidence": [
    {
      "statement": "Average MTTR reduction of 58% across beta customers (n=12)",
      "source_url": "https://example.com/case-study",
      "source_title": "Cloud Monitoring Case Study 2025"
    },
    {
      "statement": "3 of 5 mid-market SaaS customers eliminated dedicated on-call rotation",
      "source_url": null,
      "source_title": null
    }
  ],
  "created": "2026-01-20"
}
```

Required: `slug`, `feature_slug`, `market_slug`, `is_statement`, `does_statement`, `means_statement`
Optional: `evidence`, `created`

Each evidence entry is an object with `statement` (required), `source_url` (string or null), and `source_title` (string or null). Entries from web research include the source URL for claim verification; entries without a source use null.

### 5. Review with User

Present propositions grouped by feature or by market (user's preference). Ask explicitly:

- Does the IS statement accurately reflect the feature?
- Does the DOES statement reference a real pain point for this market?
- Does the MEANS statement connect to an outcome this buyer would measure or care about?
- Could this DOES/MEANS apply to a different market? If yes, it needs sharpening.
- Any evidence claims that feel inflated or unsupported?

Iterate until the messaging feels accurate and differentiated. The user knows their buyers best.

### 6. Validate Against Portfolio

Cross-reference propositions with existing portfolio entities:

- **Features**: Every proposition must reference a valid `feature_slug` in `features/`
- **Markets**: Every proposition must reference a valid `market_slug` in `markets/`
- **Orphaned propositions**: Flag propositions that reference features or markets that don't exist
- **Duplicate messaging**: Flag propositions with near-identical DOES/MEANS across different markets -- this signals the markets may not be distinct enough

Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to generate an overview of coverage gaps and orphaned references.

### Editing Propositions

Read the existing proposition JSON, apply the user's changes, and write back. Changing a feature or market slug requires renaming the file to match the `{feature-slug}--{market-slug}.json` convention and updating the internal slug fields.

### Listing Propositions

Read all JSON files in the project's `propositions/` directory. Present as a table grouped by feature or market:

| Feature | Market | DOES (summary) | Evidence |
|---|---|---|---|
| cloud-monitoring | mid-market-saas | Reduces MTTR by 60% | 2 sources |

### Deleting Propositions

A proposition can be deleted freely -- it has no downstream dependents. Confirm with the user before deleting.

## Important Notes

- Features and markets must exist before propositions can be created -- use the `features` and `markets` skills first
- Product positioning and pricing tier provide useful context for crafting DOES/MEANS statements
- Aim for one proposition per Feature x Market pair; missing pairs show up in `project-status.sh` output
- Evidence is optional but strengthens downstream proposals and enables claim verification
- Changing a feature or market slug after propositions exist requires renaming proposition files
- **Content Language**: Read `portfolio.json` in the project root. If a `language` field is present, generate all user-facing text content (IS/DOES/MEANS statements, evidence descriptions) in that language. JSON field names and slugs remain in English. If no `language` field is present, default to English.
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
