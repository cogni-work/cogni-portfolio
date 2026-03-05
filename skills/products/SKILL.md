---
name: products
description: |
  Define and manage the top-level product offerings in the portfolio.
  Use whenever the user mentions products, product lines, offerings,
  "what do we sell", product portfolio, product definition, pricing tiers,
  lifecycle stages, or wants to organize capabilities into named offerings
  — even if they don't say "product" explicitly.
---

# Product Management

Define and manage products -- the top-level grouping entity in the portfolio. Each product bundles a set of market-independent features and carries its own positioning, pricing tier, and lifecycle stage.

## Core Concept

A product is a named offering that bundles related features. Every feature must belong to exactly one product. Products are defined before features -- they provide the organizational context that makes feature definition purposeful.

This matters because products are the first entity to define after portfolio setup. Every downstream entity -- features, propositions, markets, customers, competitors -- traces back to products. A well-scoped product makes feature extraction natural and proposition generation focused; a poorly scoped product creates confusion that cascades through the entire portfolio.

Good products are:
- **Distinct**: Each product has a clear boundary separating it from other products
- **Marketable**: A product is something a customer can evaluate, purchase, or subscribe to
- **Feature-rich**: A product should contain 3-15 features; fewer suggests it is a feature, more suggests it should be split

## Workflow

### 1. Gather Product Intelligence

Build the product list from available sources:

- **User input**: Ask the user to describe their product offerings directly
- **Portfolio context** (`portfolio.json`): Company description often contains implicit product boundaries
- **Existing documentation**: The user may point to websites, pitch decks, or product pages

**Web research (optional)**: When the user provides a company URL or asks for research-backed products, delegate to a subagent (Agent tool) to extract product offerings from the company's website, documentation, or marketing pages. This is especially useful when the user hasn't formally documented their product portfolio yet.

### 2. Extract and Structure Products

For each distinct product, determine:

- **slug**: kebab-case identifier (e.g., `cloud-platform`)
- **name**: Human-readable name (e.g., "Cloud Platform")
- **description**: 1-3 sentence description of what the product is and who it serves
- **positioning** (optional): One-sentence value proposition
- **pricing_tier** (optional): Pricing category (e.g., "Starter", "Professional", "Enterprise")
- **maturity** (optional): Lifecycle stage -- one of `concept`, `development`, `launch`, `growth`, `mature`, `decline`
- **launch_date** (optional): When the product was or will be launched (YYYY-MM-DD)
- **version** (optional): Current version identifier

### 3. Product JSON Schema

```json
{
  "slug": "cloud-platform",
  "name": "Cloud Platform",
  "description": "Unified cloud infrastructure management platform for mid-market SaaS companies.",
  "positioning": "The most developer-friendly cloud management solution.",
  "pricing_tier": "Enterprise",
  "maturity": "growth",
  "launch_date": "2024-03-01",
  "version": "2.1",
  "created": "2026-01-15"
}
```

Required: `slug`, `name`, `description`. Optional: `positioning`, `pricing_tier`, `maturity`, `launch_date`, `version`, `created`.

Valid maturity values: `concept`, `development`, `launch`, `growth`, `mature`, `decline`.

Write each product as a JSON file to `products/{slug}.json`.

### 4. Review with User

Present proposed products as a table for review:

| Slug | Name | Maturity | Positioning |
|---|---|---|---|
| cloud-platform | Cloud Platform | growth | The most developer-friendly cloud management solution |

Ask explicitly:

- Are these the right product boundaries? Should any be merged or split?
- Missing any product lines?
- Do the names and descriptions feel accurate?
- Are the maturity stages right?

Iterate until the product set feels right. The user knows their portfolio best.

### 5. Validate Against Portfolio

Cross-reference products with existing portfolio entities:

- **Features**: Check which products already have features defined (scan `features/` for matching `product_slug`). Use `$CLAUDE_PLUGIN_ROOT/scripts/project-status.sh` to generate an overview.
- **Orphaned features**: Flag features that reference a product slug that doesn't exist
- **Coverage**: Flag products with zero features -- they need attention next
- **Overlap**: Flag products with near-identical descriptions -- they may need merging

These checks catch gaps early, before they cascade into downstream skills.

### Listing Products

Read all JSON files in the project's `products/` directory. Present as a table:

| Slug | Name | Maturity | Features |
|---|---|---|---|
| cloud-platform | Cloud Platform | growth | 5 |

To show the feature count, scan `features/` for files where `product_slug` matches the product slug.

### Editing Products

Read the existing product JSON, apply the user's changes, and write back. Changing a product slug requires renaming the file and updating the `product_slug` field in all dependent features.

### Deleting Products

A product can only be deleted if it has no features. If features exist, instruct the user to reassign or delete them first.

### Viewing Product Details

When the user asks about a specific product, show:
1. Product metadata (name, description, positioning, maturity, etc.)
2. List of features belonging to this product (scan `features/` for matching `product_slug`)
3. Count of propositions generated from those features

## Important Notes

- Products are the first entity to define after portfolio setup -- features, markets, and all downstream entities build on them
- Changing a product slug after features exist requires updating `product_slug` in all child features
- Aim for 1-5 products per portfolio; more than 7 usually signals overlapping product boundaries
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
