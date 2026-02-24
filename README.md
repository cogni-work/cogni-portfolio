# cogni-portfolio

Portfolio messaging and solution planning tool for SMEs.

## Core Concept

A **product** groups related features into a named offering. A **feature** (IS) is product-inherent and market-independent. An **advantage** (DOES) and **benefit** (MEANS) are always market-specific. A product's complete value proposition for a market is composed from its feature-level solutions. Each **solution** maps one feature to one target market with its DOES and MEANS -- the atomic unit of messaging. The same feature produces different solutions for different markets.

## Data Model

| Entity | Description |
|---|---|
| **Product** | Named offering that bundles related features |
| **Feature** | What the product/service IS (capability, spec, function) — belongs to one product |
| **Target Market** | Defined by TAM, SAM, SOM sizing |
| **Solution** | Feature x Target Market -> Advantage (DOES) + Benefit (MEANS) |
| **Competitor** | Per solution: who else solves this for this market |
| **Customer Profile** | Per target market: ideal buyer characteristics |

## Workflow

1. **Setup** — create project and define company context
2. **Products** — define named offerings
3. **Features** — add features per product (market-independent)
4. **Markets** — propose and select target markets (TAM/SAM/SOM)
5. **Solutions** — for each Feature x Market pair, generate IS/DOES/MEANS messaging
6. **Enrichment** — analyze competitors and customer profiles per solution/market
7. **Synthesis** — generate structured messaging repository
8. **Export** — produce deliverables (markdown, XLSX)

Use `/resume-portfolio` to pick up where you left off. It detects the current phase and recommends the next action.

## Downstream Use

- **Proposals** — solution-specific sales documents for target customers
- **Marketing content** — market-specific messaging for campaigns, website, collateral

## Prerequisites

- XLSX export requires the `document-skills:xlsx` plugin to be available

## Framework Reference

FAB (Feature -> Advantage -> Benefit), also called IS/DOES/MEANS messaging pyramid. General B2B sales principle, not proprietary.

## License

Dual-licensed under [CC BY-NC-SA 4.0](LICENSE) for non-commercial use. Commercial licenses available — contact stephan@cogni-work.ai.
