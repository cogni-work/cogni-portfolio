---
name: solutions
description: |
  Define implementation plans and pricing tiers for propositions to build customer business cases.
  Use whenever the user mentions solutions, implementation plan, pricing model, business case,
  "why pay", investment ballpark, proof of value, PoV, implementation complexity, project scope,
  or wants to attach commercial terms to a proposition — even without saying "solution".
---

# Solution Planning

Define implementation plans and pricing tiers per proposition -- the commercial layer that turns messaging into a customer business case.

## Core Concept

A solution answers the buyer's two remaining questions after they've seen a proposition: "What does it take to implement this?" and "What will it cost?" Without a solution, a proposition is marketing copy. With a solution, it becomes a fundable project.

This matters because the gap between "we like this" and "we're buying this" is almost always an implementation plan and a price tag. Buyers need to see a path from kickoff to value delivery and a ballpark investment they can put in a budget request. Proposals, business cases, and sales decks all draw from solution data -- if the commercial grounding is missing or unconvincing, every downstream deliverable falls flat.

Each solution maps 1:1 to a proposition (same slug). It contains:

- **Implementation plan**: Phased project outline with duration ballparks -- enough for a buyer to understand the journey from kickoff to value delivery
- **Pricing tiers**: Four complexity levels (proof-of-value, small, medium, large) with price and scope -- enough for a buyer to self-select and budget

## Workflow

### 1. Identify Pending Solutions

Run the project status script to find propositions without solutions:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

The `missing_solutions` array lists propositions that lack solution files.

### 2. Generate Solutions

Two generation modes:

**Single solution**: Generate one solution interactively. Read the proposition, its parent feature, the product, and the market JSON files, then design the implementation plan and pricing tiers with the user.

**Batch generation**: For multiple pending solutions, delegate each to the `solution-planner` agent. Launch agents in parallel for independent propositions. Each agent reads the full context chain (proposition -> feature -> product -> market) and produces a complete solution.

**Web research (optional)**: When the user wants market-calibrated pricing, delegate to a subagent (Agent tool) to search for industry pricing benchmarks, competitor packaging, and implementation timeline data for the relevant market segment. This is especially useful when the user is unsure about price points or wants to validate ballparks against market norms.

### 3. Gather Context

For each solution, read (in parallel where possible):

- **Proposition JSON** (`propositions/{slug}.json`) -- IS/DOES/MEANS messaging defines what the solution must deliver
- **Feature JSON** (`features/{feature-slug}.json`) -- the underlying capability
- **Product JSON** (`products/{product-slug}.json`) -- positioning, pricing tier, and maturity inform price range
- **Market JSON** (`markets/{market-slug}.json`) -- region (for currency), segmentation (for scope assumptions), buyer context

The product's pricing tier and maturity signal where pricing should land. The market's segmentation informs scope assumptions. The proposition's DOES statement defines what the implementation must deliver end-to-end.

### 4. Define Implementation Plan

Create a phased implementation plan. Keep it lean -- 2-5 phases, each with:

- **phase**: Short phase name (e.g., "Discovery & Scoping")
- **duration_weeks**: Ballpark duration in weeks
- **description**: What happens in this phase -- deliverables, activities, milestones

Common phase patterns by engagement type:

**Proof-of-value / pilot**: Discovery (1-2w) -> Pilot execution (2-4w) -> Evaluation & report (1w)

**Standard implementation**: Discovery & scoping (2w) -> Core build/deploy (4-8w) -> Integration & testing (2-4w) -> Tuning & handover (2w)

**Advisory / strategy**: Current state assessment (2w) -> Strategy & roadmap (2-4w) -> Implementation support (4-8w) -> Review & optimize (2w)

**Platform rollout**: Discovery (2w) -> Foundation deployment (4w) -> Team-by-team rollout (4-8w) -> Optimization & enablement (2-4w)

Choose whichever pattern fits the capability being delivered. These are starting points -- adapt freely based on what the proposition actually requires.

The plan should be realistic but not a project charter. It gives the buyer enough structure to understand the commitment and timeline.

### 5. Define Pricing Tiers

Set four pricing tiers reflecting increasing implementation complexity:

| Tier | Purpose | Buyer Signal |
|---|---|---|
| proof_of_value | Low-risk entry, validate fit | "We need to prove it works here first" |
| small | Minimum viable implementation | "We want this for one team or project" |
| medium | Standard implementation | "We want this across the department" |
| large | Enterprise-scale rollout | "We want this organization-wide" |

Each tier needs:
- **price**: Numeric value (ballpark for business case planning, not a binding quote)
- **currency**: ISO currency code matching the market's region
- **scope**: One sentence describing what's included at this tier

**Pricing calibration:**
- Product pricing tier and maturity inform the range -- a "growth" product commands different prices than a "concept" stage offering
- Market segmentation sets buyer expectations -- mid-market expects different price points than enterprise
- TAM/SAM data provides a sanity check -- pricing should be plausible within the market's ACV range
- The proposition's DOES statement justifies pricing -- more transformative outcomes support higher price points
- Each tier should represent meaningfully more scope, not just a price increase

The proof-of-value tier is critical -- it's the buyer's lowest-risk entry point and often determines whether a conversation becomes a deal.

### 6. Write Solution Entities

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

### 7. Review with User

Present solutions grouped by product or market. Ask explicitly:

- Does the implementation plan reflect how you actually deliver this?
- Are the phase durations realistic for this market segment?
- Do the pricing tiers feel right for this buyer? Too high? Too low?
- Would a buyer in this market self-select into the right tier?
- Is the proof-of-value scope compelling enough to get a foot in the door?

Iterate until the commercial terms feel credible. The user knows their delivery model and pricing power best.

### 8. Validate Against Portfolio

Cross-reference solutions with existing portfolio entities:

- **Propositions**: Every solution must reference a valid `proposition_slug` in `propositions/`
- **Orphaned solutions**: Flag solutions that reference propositions that don't exist
- **Currency consistency**: Pricing currency should align with the market's region
- **Price coherence**: Flag solutions where proof_of_value > small or small > medium (inverted tiers)
- **Implementation coverage**: The phases should plausibly deliver the proposition's DOES statement

Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to check coverage.

### Editing Solutions

Read the existing solution JSON, apply the user's changes, and write back. Changing the proposition slug requires renaming the file and updating internal slug fields.

### Listing Solutions

Read all JSON files in the project's `solutions/` directory. Present as a table:

| Proposition | PoV | Small | Medium | Large | Phases | Timeline |
|---|---|---|---|---|---|---|
| cloud-monitoring--mid-market-saas-dach | 15K EUR | 50K EUR | 120K EUR | 250K EUR | 3 | 8 weeks |

Include the total implementation timeline (sum of phase durations) so the user can see the full picture at a glance.

### Deleting Solutions

A solution can be deleted freely -- it has no downstream dependents. Confirm with the user before deleting.

## Important Notes

- Propositions must exist before solutions can be created -- use the `propositions` skill first
- Prices are ballparks for business case planning, not binding quotes
- Currency should match the market's region (EUR for DACH/EU, USD for US/NA, etc.)
- The proof-of-value tier is critical -- it's the buyer's lowest-risk entry point
- Implementation phases should map to the proposition's DOES statement (what gets delivered)
- The `solution-planner` agent handles individual solution generation when delegated from batch mode
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
