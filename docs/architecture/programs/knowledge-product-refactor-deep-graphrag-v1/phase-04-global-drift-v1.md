# Phase 4: Global Search / DRIFT-like V1

## Goal

Let enhanced retrieval answer both:

1. broad global theme questions
2. broad questions that still require local evidence

## Global Search V1

```text
query
  -> top community reports
  -> map
  -> reduce
  -> answer
```

Metadata should include:

- `used_communities`
- `map_results`
- `reduce_trace`
- `supporting_chunks`

## DRIFT-like V1

```text
query
  -> top community reports
  -> broad initial answer
  -> limited follow-up questions
  -> local graph search for each follow-up
  -> final answer
```

V1 limit:

- one follow-up round only

Metadata should include:

- `drift_trace`
- `follow_up_questions`
- `used_communities`
- `used_paths`
