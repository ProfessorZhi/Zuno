class KnowledgeTaskStatus:
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class KnowledgeTaskStage:
    uploaded = "uploaded"
    queued = "queued"
    parsing = "parsing"
    splitting = "splitting"
    rag_indexing = "rag_indexing"
    graph_extracting = "graph_extracting"
    graph_indexing = "graph_indexing"
    completed = "completed"
    failed = "failed"


PIPELINE_STAGES = [
    KnowledgeTaskStage.uploaded,
    KnowledgeTaskStage.queued,
    KnowledgeTaskStage.parsing,
    KnowledgeTaskStage.splitting,
    KnowledgeTaskStage.rag_indexing,
    KnowledgeTaskStage.graph_extracting,
    KnowledgeTaskStage.graph_indexing,
    KnowledgeTaskStage.completed,
]
