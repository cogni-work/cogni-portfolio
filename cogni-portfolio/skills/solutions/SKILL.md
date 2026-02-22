---
name: solutions
description: |
  This skill should be used when the user asks to "generate solutions",
  "create messaging", "IS DOES MEANS", "feature advantage benefit",
  "map features to markets", or "FAB messaging". Generates solution messaging
  per Feature x Market combination.
---

# Solution Generation

Generate IS/DOES/MEANS messaging for each Feature x Market combination. This is the core of the portfolio -- transforming market-independent features into market-specific value propositions.

## Core Framework

The IS/DOES/MEANS (FAB) messaging pyramid:

- **IS** (Feature): What the product capability is -- factual, market-independent. Copied from the feature entity.
- **DOES** (Advantage): What the feature achieves for this specific market -- the functional or operational improvement. Market-specific.
- **MEANS** (Benefit): What the advantage means for the buyer -- the business outcome or emotional payoff. Market-specific.

The same feature produces different DOES and MEANS statements for different markets because buyers in each segment face different problems, use different language, and value different outcomes.

## Workflow

### 1. Identify Pending Solutions

Run the project status script to find missing solutions:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

The `missing_solutions` array lists Feature x Market pairs without solution files.

### 2. Generate Solutions

Two generation modes:

**Single solution**: Generate one solution interactively. Read the feature and market JSON files, then craft IS/DOES/MEANS statements with the user.

**Batch generation**: For multiple pending solutions, delegate each to the `solution-generator` agent. Launch agents in parallel for independent Feature x Market pairs.

### 3. Solution Quality Criteria

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

### 4. Write Solution Entities

Write each solution to `solutions/{feature-slug}--{market-slug}.json`:

```json
{
  "slug": "cloud-monitoring--mid-market-saas",
  "feature_slug": "cloud-monitoring",
  "market_slug": "mid-market-saas",
  "is_statement": "Real-time cloud infrastructure monitoring with automated alerting for servers, containers, and network components.",
  "does_statement": "Reduces mean-time-to-resolution by 60% through intelligent alert correlation, eliminating alert fatigue in growing engineering teams.",
  "means_statement": "Mid-market SaaS companies maintain 99.95% uptime SLAs without hiring additional SRE staff, protecting revenue during rapid scaling.",
  "evidence": [
    "Average MTTR reduction of 58% across beta customers (n=12)"
  ],
  "created": "2026-01-20"
}
```

Required: `slug`, `feature_slug`, `market_slug`, `is_statement`, `does_statement`, `means_statement`
Optional: `evidence`, `created`

### 5. Review with User

After generation, present solutions grouped by feature or by market (user's preference). Allow the user to refine wording before finalizing.

## Hybrid Research Mode

By default, generate solutions from LLM knowledge and company context. When the user requests research-backed messaging:

- Use web research to validate claims and find supporting evidence
- Search for industry benchmarks relevant to each market segment
- Add findings to the `evidence` array

## Important Notes

- The `is_statement` should closely match the feature description but may be slightly tailored for market context
- Never use the same DOES/MEANS across different markets -- that signals the markets aren't distinct enough
- Evidence is optional but strengthens downstream proposals
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
