# Knowledge Config Impact And Reindex

## Purpose

This spec defines how knowledge configuration changes should be classified and surfaced.

## Problem

The old knowledge configuration experience mixed:

1. build-time settings
2. query-time settings
3. graph-time settings
4. model settings
5. GraphRAG Project / query policy settings

The new system should classify changes by operational impact.

## Impact Classes

### Immediate Effect

Examples:

- retrieval thresholds
- route limits
- rerank limits
- default product mode display

Expected action:

```text
save only
```

### Text Reindex Required

Examples:

- text embedding model
- chunking settings

Expected action:

```text
save + rebuild text index
```

### Image Reindex Required

Examples:

- VL embedding model

Expected action:

```text
save + rebuild image or multimodal index
```

### Graph Update Required

Examples:

- GraphRAG Project schema
- extraction prompt
- graph extraction model

Expected action:

```text
save + update graph index
```

### Community Detection Required

Examples:

- graph changes that invalidate community grouping

Expected action:

```text
save + rerun community detection
```

### Community Report Required

Examples:

- community report prompt change
- community grouping change

Expected action:

```text
save + regenerate community reports
```

### Full Rebuild Required

Examples:

- standard to enhanced mode upgrade that needs graph and community generation
- chunking changes that invalidate multiple derived layers

Expected action:

```text
save + full rebuild
```

## API Contract

The config impact response should classify at least:

- `changed_fields`
- `immediate_effect_fields`
- `text_reindex_required`
- `image_reindex_required`
- `bm25_reindex_required`
- `graph_update_required`
- `community_detection_required`
- `community_report_required`
- `full_rebuild_required`
- `recommended_action`

## Reindex Action Contract

Supported actions should include at least:

- `text_index`
- `image_index`
- `bm25_index`
- `graph_index`
- `community_detection`
- `community_report`
- `full_rebuild`
