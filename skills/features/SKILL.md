---
name: features
description: |
  Define and manage market-independent product features (IS layer of FAB).
  Use whenever the user mentions features, capabilities, product specs,
  "what does it do", feature extraction, feature inventory, or wants to
  break a product into its component capabilities — even if they don't
  say "feature" explicitly.
---

# Feature Management

Define and manage market-independent product features -- the IS layer of the FAB framework. Features describe what a product or service IS, independent of any target market. Every feature belongs to exactly one product.

## Core Concept

A feature is a factual, market-independent statement about a product capability, specification, or function. Features do not include advantages or benefits -- those emerge when a feature meets a specific target market (handled by the `propositions` skill).

This matters because features are the foundation of the entire portfolio. Every downstream entity -- propositions, competitors, customers, export deliverables -- traces back to features. Vague or overlapping features propagate confusion through the whole pipeline; precise features make everything downstream sharper.

Good features are:
- **Specific**: "Real-time container orchestration monitoring" not "monitoring"
- **Factual**: Describe what exists, not what it enables
- **Market-neutral**: No mention of who benefits or how

## Workflow

### 1. Select Product

Check that at least one product exists in `products/`. If none exist, tell the user to define products first using the `products` skill. If only one product exists, use it automatically. If multiple exist, ask the user which product these features belong to.

### 2. Gather Feature Intelligence

Build the feature list from available sources:

- **User input**: Ask the user to describe their product capabilities directly
- **Existing product docs** (`products/{slug}.json`): The product description often contains implicit features
- **Proposition backfill** (`propositions/`): If propositions already exist, their feature references reveal what features are assumed

**Web research (optional)**: When the user provides a product URL or asks for research-backed features, delegate to a subagent (Agent tool) to extract capabilities from the product's website, documentation, or marketing pages. This is especially useful for products where the user hasn't documented all capabilities yet.

### 3. Extract and Structure Features

For each distinct capability, determine:

- **slug**: kebab-case identifier (e.g., `cloud-monitoring`)
- **product_slug**: The slug of the parent product (e.g., `cloud-platform`)
- **name**: Human-readable name (e.g., "Cloud Infrastructure Monitoring")
- **description**: 1-3 sentence factual description of what it IS
- **category** (optional): Grouping label (e.g., "observability", "security")

### 4. Feature JSON Schema

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

Write each feature as a JSON file to `features/{slug}.json`.

### 5. Review with User

Present proposed features as a table for review:

| Slug | Product | Name | Category |
|---|---|---|---|
| cloud-monitoring | cloud-platform | Cloud Infrastructure Monitoring | observability |

Ask explicitly:
- Are these the right capabilities? Missing anything?
- Any features that overlap or should be merged?
- Do the names and descriptions feel accurate?

Iterate until the feature set feels right. The user knows their product best.

### 6. Validate Against Portfolio

Cross-reference features with existing portfolio entities:

- **Products**: Every feature must reference a valid `product_slug`
- **Propositions**: Check if any propositions reference features that don't exist (orphaned references)
- **Coverage**: Flag products that have zero features -- they need attention

These checks catch data model inconsistencies early, before they cascade into downstream skills.

### Editing Features

Read the existing feature JSON, apply the user's changes, and write back. Changing a feature slug requires renaming the file and updating any dependent propositions. Changing `product_slug` reassigns the feature to a different product.

### Listing Features

Read all JSON files in the project's `features/` directory. Present grouped by product, with category subgrouping where categories exist.

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
- **Content Language**: Read `portfolio.json` in the project root. If a `language` field is present, generate all user-facing text content (feature names, descriptions) in that language. JSON field names and slugs remain in English. If no `language` field is present, default to English.
- **Communication Language**: If `portfolio.json` has a `language` field, communicate with the user in that language (status messages, instructions, recommendations, questions). Technical terms, skill names, and CLI commands remain in English. Default to English if no `language` field is present.
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
