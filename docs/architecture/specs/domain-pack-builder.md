# Domain Pack Builder

## Purpose

This spec defines the Domain Pack Builder as an independent product and backend resource.

## Resource Truth

A Domain Pack is not a temporary per-knowledge toggle.

It is a reusable domain template that may be shared by multiple knowledge bases.

## Builder Responsibilities

The builder should support:

1. representative file upload
2. representative file selection from an existing knowledge base
3. AI-generated draft assets
4. manual review before publish
5. published versions that can later be bound by knowledge bases

## Draft Asset Surface

The draft may include:

- `pack.yaml`
- `schema.json`
- `extraction_prompt.md`
- `retrieval_policy.yaml`
- `answer_template.md`
- `report_template.md`
- `community_report_prompt.md`
- `eval_dataset.jsonl`

## Safety Rule

The system must not:

1. silently use every file in a knowledge base as builder input
2. silently publish a generated draft
3. silently rebind or rebuild knowledge bases after a pack change

Human approval is required between:

```text
draft generation
  -> draft review
  -> publish
  -> optional knowledge binding change
```

## Binding Rule

Publishing a Domain Pack does not automatically rebuild any knowledge base.

Knowledge bases may later choose to:

1. bind the new pack
2. keep the existing pack
3. switch pack and then trigger the necessary rebuild action
