---
name: solutions
description: |
  Define implementation plans and pricing tiers for propositions to build customer business cases.
  Use whenever the user mentions solutions, implementation plan, pricing model, business case,
  "why pay", investment ballpark, proof of value, PoV, implementation complexity, project scope,
  reprice, adjust pricing, competitive pricing, or wants to attach commercial terms to a
  proposition — even without saying "solution".
---

# Solution Planning

Co-develop implementation plans and pricing tiers per proposition with the user -- the commercial layer that turns messaging into a customer business case.

## Core Concept

A solution answers the buyer's two remaining questions after they've seen a proposition: "What does it take to implement this?" and "What will it cost?" Without a solution, a proposition is marketing copy. With a solution, it becomes a fundable project.

This skill works interactively. Rather than generating a complete solution and asking the user to approve it, walk through each component -- phases, effort, pricing -- step by step. Present proposals, get feedback, adjust, and only move to the next component once the current one feels right. The user knows their delivery model and market better than any template.

Each solution maps 1:1 to a proposition (same slug). It contains:

- **Implementation plan**: Phased project outline with duration ballparks
- **Pricing tiers**: Four complexity levels (proof-of-value, small, medium, large) with price and scope

## Workflow

### 1. Identify What to Work On

If the user names a specific proposition, start there. Otherwise, run the project status script to find propositions without solutions:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-status.sh "<project-dir>"
```

The `missing_solutions` array lists propositions that lack solution files. Present the list and let the user pick which one(s) to work on.

### 2. Gather Context

For the selected proposition, read (in parallel where possible):

- **Proposition JSON** (`propositions/{slug}.json`) -- IS/DOES/MEANS messaging defines what the solution must deliver
- **Feature JSON** (`features/{feature-slug}.json`) -- the underlying capability
- **Product JSON** (`products/{product-slug}.json`) -- positioning, pricing tier, and maturity inform price range
- **Market JSON** (`markets/{market-slug}.json`) -- region (for currency), segmentation (for scope assumptions), buyer context
- **Competitor JSON** (`competitors/{slug}.json`, if it exists) -- competitor pricing and positioning inform calibration

Summarize the key context for the user in 2-3 sentences before proposing anything. This grounds the conversation.

### 3. Co-develop Implementation Phases

Present an initial proposal for the implementation phases based on the proposition's DOES statement and the engagement type. Explain your reasoning -- why these phases, why this sequence.

Common phase patterns by engagement type:

**Proof-of-value / pilot**: Discovery (1-2w) -> Pilot execution (2-4w) -> Evaluation & report (1w)

**Standard implementation**: Discovery & scoping (2w) -> Core build/deploy (4-8w) -> Integration & testing (2-4w) -> Tuning & handover (2w)

**Advisory / strategy**: Current state assessment (2w) -> Strategy & roadmap (2-4w) -> Implementation support (4-8w) -> Review & optimize (2w)

**Platform rollout**: Discovery (2w) -> Foundation deployment (4w) -> Team-by-team rollout (4-8w) -> Optimization & enablement (2-4w)

Present the proposed phases as a table:

| # | Phase | Duration | What happens |
|---|-------|----------|--------------|
| 1 | Discovery & Scoping | 2 weeks | ... |
| 2 | Core Build | 6 weeks | ... |
| ... | ... | ... | ... |

Then ask:
- Does this match how you actually deliver this kind of work?
- Any phases to add, remove, or rename?
- Are the durations realistic?

Iterate until the phases feel right before moving to pricing.

### 4. Co-develop Pricing Tiers

Once phases are agreed, propose four pricing tiers. Each tier represents a meaningfully different scope of engagement -- not just a price increase.

| Tier | Purpose | Buyer Signal |
|---|---|---|
| proof_of_value | Low-risk entry, validate fit | "We need to prove it works here first" |
| small | Minimum viable implementation | "We want this for one team or project" |
| medium | Standard implementation | "We want this across the department" |
| large | Enterprise-scale rollout | "We want this organization-wide" |

Present the proposal as a table showing price, scope, and the reasoning behind each price point:

| Tier | Price | Scope | Rationale |
|---|---|---|---|
| Proof of Value | 15,000 EUR | Single environment, 2-week pilot | Low-risk entry, covers discovery + pilot effort |
| Small | 50,000 EUR | One team, basic setup | Minimum viable, ~8 weeks delivery |
| Medium | 120,000 EUR | Department-wide, full features | Standard engagement, ~12 weeks |
| Large | 250,000 EUR | Organization-wide, dedicated CSM | Enterprise rollout, ~16 weeks |

**Pricing calibration signals:**
- Product pricing tier and maturity -- a "growth" product commands different prices than a "concept" offering
- Market segmentation -- mid-market expects different price points than enterprise
- TAM/SAM data -- pricing should be plausible within the market's ACV range
- The proposition's DOES statement -- more transformative outcomes support higher price points
- Competitor pricing (if available) -- position relative to known alternatives

Then ask:
- Do these price points feel right for this market?
- Is the proof-of-value scope compelling enough to get a foot in the door?
- Would a buyer self-select into the right tier, or are the scope jumps unclear?
- Too high? Too low? Any tier feel off?

Iterate until the pricing feels credible.

### 5. Write Solution Entity

Once both phases and pricing are agreed, write the solution to `solutions/{feature-slug}--{market-slug}.json`:

```json
{
  "slug": "cloud-monitoring--mid-market-saas-dach",
  "proposition_slug": "cloud-monitoring--mid-market-saas-dach",
  "implementation": [
    {
      "phase": "Discovery & Setup",
      "duration_weeks": 2,
      "description": "Requirements gathering, environment audit, monitoring strategy definition"
    }
  ],
  "pricing": {
    "proof_of_value": {
      "price": 15000,
      "currency": "EUR",
      "scope": "Single environment, 2-week guided pilot with defined success criteria"
    },
    "small": { "price": 50000, "currency": "EUR", "scope": "..." },
    "medium": { "price": 120000, "currency": "EUR", "scope": "..." },
    "large": { "price": 250000, "currency": "EUR", "scope": "..." }
  },
  "created": "2026-03-05"
}
```

Required: `slug`, `proposition_slug`, `implementation` (array with at least one phase), `pricing` (object with all four tiers)
Optional: `created`

### 6. Validate Against Portfolio

Cross-reference with existing entities:

- **Propositions**: Every solution must reference a valid `proposition_slug` in `propositions/`
- **Currency consistency**: Pricing currency should align with the market's region
- **Price coherence**: Flag solutions where proof_of_value > small or small > medium (inverted tiers)
- **Implementation coverage**: Phases should plausibly deliver the proposition's DOES statement

Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to check coverage.

## Repricing from Competitive Analysis

When competitor data exists or the user has just run competitive analysis, the user may want to recalibrate pricing. This is a focused flow that touches only pricing -- not implementation phases.

### Repricing Workflow

1. **Read the competitor file** (`competitors/{slug}.json`) for the solution's proposition
2. **Read the existing solution** to see current pricing
3. **Analyze competitor positioning** -- extract any pricing signals, market positioning, and stated weaknesses from the competitor data
4. **Present a comparison** showing current pricing alongside competitive context:

| Tier | Current Price | Competitive Context |
|---|---|---|
| PoV | 15,000 EUR | Competitor X starts at 20K, Competitor Y offers free trial |
| Small | 50,000 EUR | Competitor X charges 65K for similar scope |
| ... | ... | ... |

5. **Propose adjusted pricing** with rationale tied to competitive positioning -- e.g., undercut on PoV to win entry, match on medium where differentiation is strong, premium on large where competitors are weak
6. **Iterate with the user** until the adjusted pricing feels right
7. **Update the solution JSON** -- only the pricing object changes, implementation stays as-is

**Web research (optional)**: When the user wants market-calibrated pricing beyond what the competitor file contains, delegate to a subagent to search for industry pricing benchmarks, competitor packaging pages, and deal size data for the relevant segment.

## Batch Generation

For multiple pending solutions, delegate each to the `solution-planner` agent. Launch agents in parallel for independent propositions. Each agent reads the full context chain (proposition -> feature -> product -> market) and produces a complete solution.

Batch mode skips the interactive co-development steps -- use it when the user wants to generate many solutions quickly and review them afterward. The user can then pick individual solutions to refine interactively.

## Editing Solutions

Read the existing solution JSON, apply the user's changes, and write back. The interactive flow applies here too -- present the current state, propose changes, iterate.

## Listing Solutions

Read all JSON files in the project's `solutions/` directory. Present as a table:

| Proposition | PoV | Small | Medium | Large | Phases | Timeline |
|---|---|---|---|---|---|---|
| cloud-monitoring--mid-market-saas-dach | 15K EUR | 50K EUR | 120K EUR | 250K EUR | 3 | 8 weeks |

Include the total implementation timeline (sum of phase durations).

## Deleting Solutions

A solution can be deleted freely -- it has no downstream dependents. Confirm with the user before deleting.

## Important Notes

- Propositions must exist before solutions can be created -- use the `propositions` skill first
- Prices are ballparks for business case planning, not binding quotes
- Currency should match the market's region (EUR for DACH/EU, USD for US/NA, etc.)
- The proof-of-value tier is critical -- it's the buyer's lowest-risk entry point
- Implementation phases should map to the proposition's DOES statement
- The `solution-planner` agent handles individual solution generation in batch mode
- Competitor data feeds pricing calibration -- run `compete` first for better-grounded prices
- **Content Language**: Read `portfolio.json` in the project root. If a `language` field is present, generate all user-facing text content (phase descriptions, scope text, rationale) in that language. JSON field names and slugs remain in English. If no `language` field is present, default to English.
- **Communication Language**: If `portfolio.json` has a `language` field, communicate with the user in that language (status messages, instructions, recommendations, questions). Technical terms, skill names, and CLI commands remain in English. Default to English if no `language` field is present.
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
