---
name: features
description: |
  This skill should be used when the user asks to "define features",
  "add a feature", "list features", "edit feature", "manage features",
  "capabilities", or "what does the product do". Manages market-independent
  features (IS layer).
---

# Feature Management

Define and manage market-independent product features -- the IS layer of the FAB framework. Features describe what a product or service IS, independent of any target market. Every feature belongs to exactly one product.

## Core Concept

A feature is a factual, market-independent statement about a product capability, specification, or function. Features do not include advantages or benefits -- those emerge when a feature meets a specific target market (handled by the `propositions` skill).

Good features are:
- **Specific**: "Real-time container orchestration monitoring" not "monitoring"
- **Factual**: Describe what exists, not what it enables
- **Market-neutral**: No mention of who benefits or how

## Workflow

### Adding Features

1. First, check that at least one product exists in `products/`. If no products exist, instruct the user to define products first using the `products` skill.
2. Ask the user which product this feature belongs to (or determine from context if only one product exists)
3. Ask the user to describe their product capabilities, or review existing product documentation
4. Extract distinct, market-independent features
5. For each feature, determine:
   - **slug**: kebab-case identifier (e.g., `cloud-monitoring`)
   - **product_slug**: The slug of the parent product (e.g., `cloud-platform`)
   - **name**: Human-readable name (e.g., "Cloud Infrastructure Monitoring")
   - **description**: 1-3 sentence factual description of what it IS
   - **category** (optional): Grouping label (e.g., "observability", "security")
6. Write each feature as a JSON file to `features/{slug}.json`

### Feature JSON Schema

```json
{
  "slug": "cloud-monitoring",
  "product_slug": "cloud-platform",
  "name": "Cloud Infrastructure Monitoring",
  "description": "Real-time monitoring of cloud infrastructure including servers, containers, and network components with automated alerting.",
  "category": "observability",
  "created": "2026-01-15"
}
```

Required: `slug`, `product_slug`, `name`, `description`. Optional: `category`, `created`.

### Listing Features

Read all JSON files in the project's `features/` directory. Present as a table:

| Slug | Product | Name | Category |
|---|---|---|---|
| cloud-monitoring | cloud-platform | Cloud Infrastructure Monitoring | observability |

### Editing Features

Read the existing feature JSON, apply the user's changes, and write back. Changing a feature slug requires renaming the file and updating any dependent propositions. Changing `product_slug` reassigns the feature to a different product.

### Bulk Import

When the user provides a product description, website content, or document:
1. Determine or ask which product the features belong to
2. Extract all distinct capabilities mentioned
3. Propose a list of features with suggested slugs and names
4. Let the user confirm, edit, or remove before creating files

## Important Notes

- Products must exist before features can be created -- use the `products` skill first
- Features are the foundation -- markets, propositions, and all downstream entities build on them
- Changing a feature slug after propositions exist requires renaming proposition files (`{feature}--{market}.json`)
- Aim for 5-15 features per product; too many signals insufficient abstraction
- Each feature should be testable: "Does this product have this capability? Yes/No."
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
