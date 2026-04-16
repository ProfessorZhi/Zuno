from typing import Dict


class Text2SQLAgent:
    def __init__(self, db_config: Dict | None = None):
        _ = db_config
        raise NotImplementedError(
            "Text2SQLAgent is temporarily disabled during the PostgreSQL migration. "
            "It must be adapted to PostgreSQL catalog queries before use."
        )
