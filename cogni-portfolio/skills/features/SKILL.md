---
name: features
description: |
  This skill should be used when the user asks to "define features",
  "add a feature", "list features", "edit feature", "manage features",
  or "what does the product do". Manages market-independent features (IS layer).
---

# Feature Management

Define and manage market-independent product features -- the IS layer of the FAB framework. Features describe what a product or service IS, independent of any target market.

## Core Concept

A feature is a factual, market-independent statement about a product capability, specification, or function. Features do not include advantages or benefits -- those emerge when a feature meets a specific target market (handled by the `solutions` skill).

Good features are:
- **Specific**: "Real-time container orchestration monitoring" not "monitoring"
- **Factual**: Describe what exists, not what it enables
- **Market-neutral**: No mention of who benefits or how

## Workflow

### Adding Features

1. Ask the user to describe their product capabilities, or review existing product documentation
2. Extract distinct, market-independent features
3. For each feature, determine:
   - **slug**: kebab-case identifier (e.g., `cloud-monitoring`)
   - **name**: Human-readable name (e.g., "Cloud Infrastructure Monitoring")
   - **description**: 1-3 sentence factual description of what it IS
   - **category** (optional): Grouping label (e.g., "observability", "security")
4. Write each feature as a JSON file to `features/{slug}.json`

### Feature JSON Schema

```json
{
  "slug": "cloud-monitoring",
  "name": "Cloud Infrastructure Monitoring",
  "description": "Real-time monitoring of cloud infrastructure including servers, containers, and network components with automated alerting.",
  "category": "observability",
  "created": "2026-01-15"
}
```

Required: `slug`, `name`, `description`. Optional: `category`, `created`.

### Listing Features

Read all JSON files in the project's `features/` directory. Present as a table:

| Slug | Name | Category |
|---|---|---|
| cloud-monitoring | Cloud Infrastructure Monitoring | observability |

### Editing Features

Read the existing feature JSON, apply the user's changes, and write back. Changing a feature slug requires renaming the file and updating any dependent solutions.

### Bulk Import

When the user provides a product description, website content, or document:
1. Extract all distinct capabilities mentioned
2. Propose a list of features with suggested slugs and names
3. Let the user confirm, edit, or remove before creating files

## Important Notes

- Features are the foundation -- markets, solutions, and all downstream entities build on them
- Changing a feature slug after solutions exist requires renaming solution files (`{feature}--{market}.json`)
- Aim for 5-15 features per product; too many signals insufficient abstraction
- Each feature should be testable: "Does this product have this capability? Yes/No."
- Refer to `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md` for complete entity schemas
