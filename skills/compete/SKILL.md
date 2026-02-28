---
name: compete
description: |
  This skill should be used when the user asks to "analyze competitors",
  "competitive analysis", "competitor research", "who competes",
  "competitive landscape", "battle card", or "competitive positioning".
  Analyzes competitors per proposition.
---

# Competitive Analysis

Analyze the competitive landscape for each proposition (Feature x Market combination). Competitors are proposition-specific because the same feature competes against different players in different markets.

## Core Concept

Competitive analysis is scoped to propositions, not features or markets alone. A "cloud monitoring" feature may compete against Datadog in mid-market SaaS but against Splunk in enterprise fintech. The competitive positioning and differentiation are always market-dependent.

## Workflow

### 1. Select Propositions to Analyze

List existing propositions (read `propositions/` directory) and identify those without competitor files. Present options to the user:

- Analyze all pending propositions
- Analyze a specific proposition
- Analyze all propositions for a specific market

### 2. Research Competitors

For each selected proposition, identify 3-5 relevant competitors. Two modes:

**LLM knowledge (default)**: Identify known competitors based on the feature category and market segment. Clearly note that competitor data is based on training knowledge and may not reflect latest positioning.

**Web research (recommended)**: Delegate to the `competitor-researcher` agent which searches for:
- Companies offering similar capabilities in this market
- Recent competitive moves, pricing changes, product launches
- Market analyst reports and comparisons

### 3. Structure Competitor Analysis

For each competitor, capture:

- **Name**: Company or product name
- **Positioning**: Their stated value proposition for this market
- **Strengths**: What they do well (3-5 points)
- **Weaknesses**: Where they fall short (3-5 points)
- **Differentiation**: How the user's proposition is specifically different/better

### 4. Write Competitor Entities

Write to `competitors/{feature-slug}--{market-slug}.json` (same slug as the proposition):

```json
{
  "slug": "cloud-monitoring--mid-market-saas",
  "proposition_slug": "cloud-monitoring--mid-market-saas",
  "competitors": [
    {
      "name": "Datadog",
      "source_url": "https://example.com/datadog-review",
      "positioning": "Full-stack observability for cloud-scale",
      "strengths": ["Brand recognition", "Broad integrations"],
      "weaknesses": ["Expensive at scale", "Complex for mid-market"],
      "differentiation": "Purpose-built for mid-market complexity at 40% lower cost"
    }
  ],
  "created": "2026-01-25"
}
```

### 5. Review with User

Present competitor analysis per proposition. The user may know competitors the research missed, or may disagree with positioning claims. Iterate until accurate.

## Differentiation Guidelines

Strong differentiation statements:
- Reference a specific weakness of the competitor
- Connect to the proposition's DOES or MEANS statement
- Are verifiable or at least defensible
- Avoid generic claims ("better", "faster", "cheaper" without specifics)

## Important Notes

- Competitor files share the same slug as their parent proposition
- One competitor file per proposition, containing an array of all competitors
- Competitive intelligence ages quickly -- note the date of analysis
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
