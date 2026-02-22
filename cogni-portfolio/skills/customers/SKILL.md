---
name: customers
description: |
  This skill should be used when the user asks to "customer profiles",
  "ideal buyer", "buyer persona", "target customer", "buying center",
  or "who buys this". Creates customer profiles per target market.
---

# Customer Profiling

Create ideal customer profiles (ICPs) for each target market. Customer profiles describe who buys, why they buy, and how they make purchasing decisions.

## Core Concept

Customer profiles are market-scoped, not solution-scoped. All solutions targeting "mid-market SaaS" share the same customer profile because the buyer is the same person regardless of which feature they are evaluating. The profile captures the buyer's world -- their pain points, decision criteria, and information habits.

## Workflow

### 1. Select Markets

List existing markets (read `markets/` directory) and identify those without customer files. Present options:

- Create profiles for all markets without them
- Create a profile for a specific market

### 2. Gather Customer Intelligence

For each market, build the customer profile from available context:

- **Company context** (`portfolio.json`): Industry knowledge informs buyer types
- **Market definition** (`markets/{slug}.json`): Segmentation criteria constrain the buyer
- **Solution messaging** (`solutions/`): DOES/MEANS statements reveal which pain points are being addressed
- **User input**: The user may know their buyers well -- ask directly

### 3. Build Customer Profiles

For each market, define 1-3 buyer profiles (one primary, others secondary). For each profile capture:

- **Role**: Job title or function (e.g., "VP Engineering")
- **Seniority**: Level in organization (e.g., "C-1", "Director-level")
- **Pain points**: Top 3-5 problems they face daily (relevant to the portfolio's features)
- **Buying criteria**: What they evaluate when choosing a solution (e.g., "Time to value under 2 weeks")
- **Information sources**: Where they learn about solutions (e.g., "Peer recommendations", "Industry podcasts")
- **Decision role**: Their role in the purchase (economic buyer, technical evaluator, champion, etc.)

### 4. Write Customer Entities

Write to `customers/{market-slug}.json` (same slug as the market):

```json
{
  "slug": "mid-market-saas",
  "market_slug": "mid-market-saas",
  "profiles": [
    {
      "role": "VP Engineering",
      "seniority": "C-1",
      "pain_points": [
        "Growing infrastructure complexity outpacing team capacity",
        "Alert fatigue leading to missed critical incidents"
      ],
      "buying_criteria": [
        "Time to value under 2 weeks",
        "Total cost under $100K/year"
      ],
      "information_sources": ["Hacker News", "Peer recommendations"],
      "decision_role": "Economic buyer and technical evaluator"
    }
  ],
  "created": "2026-01-25"
}
```

### 5. Validate Against Solutions

Cross-reference customer pain points with solution DOES/MEANS statements. Each pain point should connect to at least one solution's advantage. Flag gaps where:
- A pain point has no matching solution
- A solution addresses a pain point not listed in the customer profile

## Important Notes

- Customer files share the same slug as their parent market
- One customer file per market, containing an array of buyer profiles
- The primary buyer profile should be the person who initiates the purchase decision
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
