---
name: solutions
description: |
  Define implementation plans and pricing tiers for propositions to build customer business cases.
  Use whenever the user mentions solutions, implementation plan, pricing model, business case,
  "why pay", investment ballpark, proof of value, PoV, implementation complexity, project scope,
  or wants to attach commercial terms to a proposition — even without saying "solution".
---

# Solution Planning

Define implementation plans and pricing tiers per proposition — the commercial layer that turns messaging into a customer business case.

## Core Concept

A solution answers the question: "What does it take to implement this, and what will it cost?" It bridges the gap between a proposition's promise (IS/DOES/MEANS) and the buyer's investment decision. Without a solution, a proposition is marketing copy. With a solution, it becomes a fundable project.

Each solution maps 1:1 to a proposition (same slug). It contains two things:

- **Implementation plan**: Phased project outline with duration ballparks — enough for a buyer to understand the journey from kickoff to value delivery
- **Pricing tiers**: Four complexity levels (proof-of-value, small, medium, large) with price and scope — enough for a buyer to self-select and budget

This matters because downstream deliverables (proposals, business cases) need commercial grounding. A proposal without implementation steps and pricing is a brochure. A proposal with ballpark investment and a clear path to value is a decision document.

## Workflow

### 1. Identify Pending Solutions

Run the project status script to find propositions without solutions:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

The `missing_solutions` array lists propositions that lack solution files.

### 2. Gather Context

For each solution, read:
- The proposition JSON (`propositions/{slug}.json`) — IS/DOES/MEANS and evidence
- The feature JSON (`features/{feature-slug}.json`) — what the capability is
- The product JSON (`products/{product-slug}.json`) — positioning and pricing tier context
- The market JSON (`markets/{market-slug}.json`) — buyer context and segment size

The product's pricing tier and maturity inform the price range. The market's segmentation informs scope assumptions. The proposition's DOES statement defines what the implementation must deliver.

### 3. Define Implementation Plan

Create a phased implementation plan. Keep it lean — 2-5 phases, each with:

- **phase**: Short phase name (e.g., "Discovery & Setup")
- **duration_weeks**: Ballpark duration in weeks
- **description**: What happens in this phase — deliverables, activities, milestones

Common patterns:
- **Proof-of-value**: Discovery (1-2 weeks) -> Pilot (2-4 weeks) -> Evaluation (1 week)
- **Full implementation**: Discovery (2 weeks) -> Core deployment (4-8 weeks) -> Integration (2-4 weeks) -> Tuning & Handover (2 weeks)

The plan should be realistic but not a project charter. It gives the buyer enough structure to understand the commitment and timeline.

### 4. Define Pricing Tiers

Set four pricing tiers that reflect increasing implementation complexity:

| Tier | Purpose | Typical Scope |
|---|---|---|
| proof_of_value | Low-risk entry, validate fit | Limited scope, short timeline, success criteria |
| small | Minimum viable implementation | Core functionality, single team/environment |
| medium | Standard implementation | Full functionality, multiple teams/environments |
| large | Enterprise-scale rollout | Full stack, organization-wide, dedicated support |

Each tier needs:
- **price**: Numeric value (ballpark, not a quote)
- **currency**: ISO currency code (match the market's region)
- **scope**: One sentence describing what's included at this tier

Price ranges should be internally consistent (each tier roughly 2-3x the previous) and credible for the market segment. A mid-market SaaS buyer expects different price points than an enterprise buyer.

### 5. Write Solution Entities

Write each solution to `solutions/{feature-slug}--{market-slug}.json`:

```json
{
  "slug": "cloud-monitoring--mid-market-saas-dach",
  "proposition_slug": "cloud-monitoring--mid-market-saas-dach",
  "implementation": [
    {
      "phase": "Discovery & Setup",
      "duration_weeks": 2,
      "description": "Requirements gathering, environment audit, monitoring strategy definition"
    },
    {
      "phase": "Core Deployment",
      "duration_weeks": 4,
      "description": "Agent rollout, alerting rules, dashboard configuration, integration with existing tools"
    },
    {
      "phase": "Tuning & Handover",
      "duration_weeks": 2,
      "description": "Alert threshold optimization, team training, runbook documentation"
    }
  ],
  "pricing": {
    "proof_of_value": {
      "price": 15000,
      "currency": "EUR",
      "scope": "Single environment, 2-week guided pilot with defined success criteria"
    },
    "small": {
      "price": 50000,
      "currency": "EUR",
      "scope": "Up to 50 nodes, basic alerting, 8-week implementation"
    },
    "medium": {
      "price": 120000,
      "currency": "EUR",
      "scope": "Up to 200 nodes, advanced alerting and dashboards, 12-week implementation"
    },
    "large": {
      "price": 250000,
      "currency": "EUR",
      "scope": "Unlimited nodes, full observability stack, 16-week implementation with dedicated CSM"
    }
  },
  "created": "2026-03-05"
}
```

Required: `slug`, `proposition_slug`, `implementation` (array with at least one phase), `pricing` (object with all four tiers)
Optional: `created`

### 6. Review with User

Present solutions grouped by product or market. Ask explicitly:

- Does the implementation plan reflect how you actually deliver this?
- Are the phase durations realistic for this market segment?
- Do the pricing tiers feel right for this buyer? Too high? Too low?
- Would a buyer in this market self-select into the right tier?
- Is the proof-of-value scope compelling enough to get a foot in the door?

Iterate until the commercial terms feel credible. The user knows their delivery model and pricing power best.

### 7. Validate Against Portfolio

Cross-reference solutions with existing portfolio entities:

- **Propositions**: Every solution must reference a valid `proposition_slug` in `propositions/`
- **Orphaned solutions**: Flag solutions that reference propositions that don't exist
- **Currency consistency**: Pricing currency should align with the market's region
- **Price coherence**: Flag solutions where proof_of_value > small or small > medium (inverted tiers)

Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to check coverage.

### Editing Solutions

Read the existing solution JSON, apply the user's changes, and write back. Changing the proposition slug requires renaming the file and updating internal slug fields.

### Listing Solutions

Read all JSON files in the project's `solutions/` directory. Present as a table:

| Proposition | PoV | Small | Medium | Large | Phases |
|---|---|---|---|---|---|
| cloud-monitoring--mid-market-saas-dach | 15K EUR | 50K EUR | 120K EUR | 250K EUR | 3 |

### Deleting Solutions

A solution can be deleted freely — it has no downstream dependents. Confirm with the user before deleting.

## Important Notes

- Propositions must exist before solutions can be created — use the `propositions` skill first
- Prices are ballparks for business case planning, not binding quotes
- Currency should match the market's region (EUR for DACH/EU, USD for US/NA, etc.)
- The proof-of-value tier is critical — it's the buyer's lowest-risk entry point
- Implementation phases should map to the proposition's DOES statement (what gets delivered)
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
