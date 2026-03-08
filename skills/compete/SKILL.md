---
name: compete
description: |
  Analyze competitors for portfolio propositions — competitive landscape,
  battle cards, positioning, differentiation. Use whenever the user mentions
  competitors, competitive analysis, "who else does this", SWOT, win/loss,
  how a proposition stacks up, or wants to understand competitive positioning
  in a market — even if they don't say "compete" explicitly.
---

# Competitive Analysis

Analyze the competitive landscape for each proposition (Feature x Market combination). Competitors are proposition-specific because the same feature competes against different players in different markets.

## Core Concept

Competitive analysis is scoped to propositions, not features or markets alone. A "cloud monitoring" feature may compete against Datadog in mid-market SaaS but against Splunk in enterprise fintech. The competitive positioning and differentiation are always market-dependent.

## Workflow

### 1. Select Propositions to Analyze

List existing propositions (read the `propositions/` directory in the project root) and identify those without corresponding competitor files in `competitors/`. If no propositions exist yet, tell the user they need to create propositions first (via the `propose` skill) before competitive analysis can begin.

Present options to the user:

- Analyze all pending propositions
- Analyze a specific proposition
- Analyze all propositions for a specific market

### 2. Research Competitors

For each selected proposition, identify 3-5 relevant competitors. Two modes:

**Web research (default)**: Use the Agent tool to delegate to the `competitor-researcher` agent, which searches for:
- Companies offering similar capabilities in this market
- Recent competitive moves, pricing changes, product launches
- Market analyst reports and comparisons

Multiple agents can be launched in parallel for different propositions.

**LLM knowledge (fallback)**: When web search is unavailable, identify known competitors based on the feature category and market segment. Clearly note that competitor data is based on training knowledge and may not reflect latest positioning.

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
- The competitor-researcher agent automatically submits verifiable claims (pricing, market share, positioning quotes) to the claims workspace for downstream verification
- **Content Language**: Read `portfolio.json` in the project root. If a `language` field is present, generate all user-facing text content (positioning, strengths/weaknesses, differentiation statements) in that language. JSON field names and slugs remain in English. If no `language` field is present, default to English.
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
