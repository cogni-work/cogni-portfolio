# cogni-portfolio

Portfolio messaging and solution planning tool for SMEs.

## Core Concept

A **product** groups related features into a named offering. A **feature** (IS) is product-inherent and market-independent. An **advantage** (DOES) and **benefit** (MEANS) are always market-specific. A **solution** = one feature mapped to a specific target market with its DOES and MEANS. The same feature produces different solutions for different markets.

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

1. Define products (named offerings)
2. Add features per product (market-independent)
3. Propose and select target markets (TAM/SAM/SOM)
4. For each Feature x Market combination: generate advantage and benefit messaging
5. Per solution: analyze competitors and customer profiles
6. Output: structured messaging repository

## Downstream Use

- **Proposals** — solution-specific sales documents for target customers
- **Marketing content** — market-specific messaging for campaigns, website, collateral

## Framework Reference

FAB (Feature -> Advantage -> Benefit), also called IS/DOES/MEANS messaging pyramid. General B2B sales principle, not proprietary.

## License

Dual-licensed under [CC BY-NC-SA 4.0](LICENSE) for non-commercial use. Commercial licenses available — contact stephan@cogni-work.ai.
