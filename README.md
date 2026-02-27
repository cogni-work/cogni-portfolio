# Portfolio Messaging Plugin

A portfolio messaging and solution planning plugin for Claude Code. Helps SMEs build structured, market-specific value propositions using the IS/DOES/MEANS (FAB) framework — from product definition through competitive analysis to export-ready deliverables.

> **Note**: This plugin assists with B2B messaging strategy and portfolio planning. All outputs — especially market sizing, competitive intelligence, and claim verification — should be reviewed by domain experts before use in sales materials, proposals, or strategic decisions.

## Installation

```bash
claude plugins add cogni-portfolio
```

## Skills

| Skill | Description |
|-------|-------------|
| `setup` | Create a new portfolio project — capture company context, initialize directory structure, and generate portfolio.json |
| `products` | Define and manage named product offerings with positioning, pricing tier, maturity, and versioning |
| `features` | Add market-independent capabilities (IS layer) per product, with bulk import from documentation |
| `markets` | Discover and size target markets with TAM/SAM/SOM — via LLM estimation or delegated web research |
| `solutions` | Generate IS/DOES/MEANS messaging for each Feature x Market pair, individually or in batch |
| `compete` | Analyze 3-5 competitors per solution with positioning, strengths, weaknesses, and differentiation |
| `customers` | Create ideal customer profiles and buyer personas per target market |
| `verify` | Orchestrate claim verification for research-backed assertions (delegates to cogni-claims plugin) |
| `synthesize` | Generate structured messaging repository with per-market summaries and integrated claim status |
| `export` | Produce deliverables — solution proposals, market briefs, portfolio workbooks (markdown and XLSX) |
| `resume-portfolio` | Detect current workflow phase and recommend next actions for an existing project |

## Agents

| Agent | Description |
|-------|-------------|
| `market-researcher` | Web research agent for TAM/SAM/SOM sizing data with claim submission for verification |
| `competitor-researcher` | Web research agent for competitive intelligence per solution with claim tracking |
| `solution-generator` | Generates IS/DOES/MEANS messaging for a single Feature x Market pair with optional web research |

## Example Workflows

### Full Portfolio Build

1. Run `/setup` to create a new project and define your company context
2. Run `/products` to define your named offerings
3. Run `/features` to add capabilities per product
4. Run `/markets` to discover and size 3-7 target markets
5. Run `/solutions` to generate IS/DOES/MEANS messaging for all Feature x Market pairs
6. Run `/compete` to analyze competitors per solution
7. Run `/customers` to create buyer personas per market
8. Run `/verify` to check research-backed claims against sources
9. Run `/synthesize` to generate the messaging repository
10. Run `/export` to produce proposals, briefs, and workbooks

### Resume Existing Work

1. Run `/resume-portfolio` to detect your current phase and see progress
2. Follow the recommended next action

### Quick Market Entry Analysis

1. Run `/setup` with a focused product scope
2. Run `/features` to define key capabilities
3. Run `/markets` with web research for validated sizing
4. Run `/solutions` to generate messaging for priority markets
5. Run `/export market-brief` to produce market-specific content

## Data Model

All entities are stored as JSON files in the project directory:

| Entity | Storage | Key Fields |
|--------|---------|------------|
| Project | `portfolio.json` | company name, description, industry |
| Product | `products/{slug}.json` | name, positioning, pricing tier, maturity |
| Feature | `features/{slug}.json` | product_slug, name, description, category |
| Market | `markets/{slug}.json` | name, segmentation, TAM/SAM/SOM |
| Solution | `solutions/{feature}--{market}.json` | IS/DOES/MEANS statements, evidence |
| Competitor | `competitors/{feature}--{market}.json` | name, positioning, strengths, weaknesses |
| Customer | `customers/{market}.json` | role, pain points, buying criteria |

## Dependencies

This plugin works standalone for core messaging workflows. Optional integrations enhance specific capabilities:

- **cogni-claims plugin** — Required for `/verify` (claim verification against cited sources)
- **document-skills:xlsx plugin** — Required for XLSX export in `/export`

> **Note:** Without these plugins, you can still build the full portfolio through synthesis. Verification and XLSX export will be unavailable.

## License

Dual-licensed under [CC BY-NC-SA 4.0](LICENSE) for non-commercial use. Commercial licenses available — contact stephan@cogni-work.ai.
