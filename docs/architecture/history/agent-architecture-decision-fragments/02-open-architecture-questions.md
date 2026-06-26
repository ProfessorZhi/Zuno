# Open Architecture Questions

## Near-Term Questions

1. Should the first GraphRAG Project example be contract review?
2. Should `graphrag_project_id` live in knowledge config first or in a separate
   project table first?
3. How much compatibility reading for `domain_pack_id` is required during
   migration?
4. Should DRIFT be visible in advanced settings immediately, or initially hidden
   behind Auto?
5. Should Prompt Tuning v1 start as manual prompt versioning before auto tuning?
6. Which eval fixture proves Enhanced Mode without hurting Basic baseline?
7. Should query prompt version and extraction prompt version be separate fields
   from the start?

## Future Questions

1. If Java business services arrive, should Python call Java over HTTP, gRPC, or
   a message bus?
2. Which business workflow justifies Java first?
3. What traffic or operational signal would justify microservice extraction?
4. Which long-running jobs justify independent workers?
5. Which task type justifies multi-agent beyond the current supervisor proof?
6. Does future multi-tenancy require tenant fields in all project/index tables?

## Non-Blocking Rule

Future questions do not block near-term FastAPI/LangGraph/RAG/GraphRAG cleanup.
