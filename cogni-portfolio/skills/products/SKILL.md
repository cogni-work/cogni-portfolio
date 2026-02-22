---
name: products
description: |
  This skill should be used when the user asks to "define products",
  "add a product", "list products", "edit product", "manage products",
  or "what products do we offer". Manages products that group features.
---

# Product Management

Define and manage products -- the top-level grouping entity in the portfolio. Each product bundles a set of market-independent features and carries its own positioning, pricing tier, and lifecycle stage.

## Core Concept

A product is a named offering that bundles related features. Every feature must belong to exactly one product. Products are defined before features -- they provide the organizational context that makes feature definition purposeful.

Good products are:
- **Distinct**: Each product has a clear boundary separating it from other products
- **Marketable**: A product is something a customer can evaluate, purchase, or subscribe to
- **Feature-rich**: A product should contain 3-15 features; fewer suggests it is a feature, more suggests it should be split

## Workflow

### Adding Products

1. Ask the user to describe their product offerings, or review existing product documentation
2. Extract distinct, nameable products
3. For each product, determine:
   - **slug**: kebab-case identifier (e.g., `cloud-platform`)
   - **name**: Human-readable name (e.g., "Cloud Platform")
   - **description**: 1-3 sentence description of what the product is and who it serves
   - **positioning** (optional): One-sentence value proposition
   - **pricing_tier** (optional): Pricing category (e.g., "Starter", "Professional", "Enterprise")
   - **maturity** (optional): Lifecycle stage -- one of `concept`, `development`, `launch`, `growth`, `mature`, `decline`
   - **launch_date** (optional): When the product was or will be launched (YYYY-MM-DD)
   - **version** (optional): Current version identifier
4. Write each product as a JSON file to `products/{slug}.json`

### Product JSON Schema

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
3. Count of solutions generated from those features

## Important Notes

- Products are the first entity to define after portfolio setup -- features, markets, and all downstream entities build on them
- Changing a product slug after features exist requires updating `product_slug` in all child features
- Aim for 1-5 products per portfolio; more than 7 usually signals overlapping product boundaries
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
