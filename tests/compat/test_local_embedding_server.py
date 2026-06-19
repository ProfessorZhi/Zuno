import json
from urllib.request import urlopen

from fastapi.testclient import TestClient

from zuno.evals.rag_eval.local_embedding_server import create_app, run_dev_server


def test_local_embedding_server_healthz():
    client = TestClient(create_app(model_name="bge-m3-dev", dimension=8))
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["model"] == "bge-m3-dev"
    assert payload["dimension"] == 8


def test_local_embedding_server_returns_openai_compatible_embeddings():
    client = TestClient(create_app(model_name="bge-m3-dev", dimension=8))
    response = client.post(
        "/v1/embeddings",
        json={
            "model": "bge-m3-dev",
            "input": ["hello", "world"],
            "encoding_format": "float",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "list"
    assert payload["model"] == "bge-m3-dev"
    assert len(payload["data"]) == 2
    assert len(payload["data"][0]["embedding"]) == 8


def test_run_dev_server_exposes_healthz():
    with run_dev_server(model_name="bge-m3-dev", dimension=8, port=0) as server:
        with urlopen(f"{server['base_url'].removesuffix('/v1')}/healthz", timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    assert payload["status"] == "ok"
    assert payload["model"] == "bge-m3-dev"
    assert payload["dimension"] == 8
    assert int(server["port"]) > 0


def test_local_embedding_server_keeps_related_texts_closer_than_unrelated_texts():
    client = TestClient(create_app(model_name="bge-m3-dev", dimension=32))
    response = client.post(
        "/v1/embeddings",
        json={
            "model": "bge-m3-dev",
            "input": [
                "Agent Server task queue uses Redis for signaling and PostgreSQL for run data.",
                "What does Agent Server task queue store in Redis and PostgreSQL?",
                "Python dataclasses generate __init__ and repr methods.",
            ],
        },
    )
    payload = response.json()["data"]
    q1 = payload[0]["embedding"]
    q2 = payload[1]["embedding"]
    q3 = payload[2]["embedding"]

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    assert dot(q1, q2) > dot(q1, q3)


def test_local_embedding_server_bridges_chinese_query_and_english_doc_terms():
    client = TestClient(create_app(model_name="bge-m3-dev", dimension=32))
    response = client.post(
        "/v1/embeddings",
        json={
            "model": "bge-m3-dev",
            "input": [
                "Milvus 的系统设计被拆成哪四个层次？各自承担什么角色？",
                "The system breaks down into four levels: access layer, coordinator service, worker nodes, and storage.",
                "Python dataclasses generate __init__ and repr methods.",
            ],
        },
    )
    payload = response.json()["data"]
    q = payload[0]["embedding"]
    related = payload[1]["embedding"]
    unrelated = payload[2]["embedding"]

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    assert dot(q, related) > dot(q, unrelated)

