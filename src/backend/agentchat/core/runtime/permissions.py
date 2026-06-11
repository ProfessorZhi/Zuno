from __future__ import annotations


def runtime_permissions() -> dict:
    return {
        "allow_tools": True,
        "allow_graph_retrieval": True,
        "allow_vector_retrieval": True,
    }
