import json
from urllib.request import Request, urlopen

from fastapi.testclient import TestClient

from zuno.evals.rag_eval.local_rerank_server import create_app, run_dev_server


def test_local_rerank_server_ranks_overlap_higher():
    client = TestClient(create_app(model_name="bge-rerank-dev"))
    response = client.post(
        "/rerank",
        json={
            "model": "bge-rerank-dev",
            "input": {
                "query": "python keyword variable name",
                "documents": [
                    "quantum mechanics introduction",
                    "python keyword cannot be used as variable name",
                ],
            },
            "parameters": {"return_documents": True, "top_n": 2},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["output"]["results"][0]["index"] == 1
    assert payload["output"]["results"][0]["relevance_score"] >= payload["output"]["results"][1]["relevance_score"]


def test_local_rerank_run_dev_server_exposes_healthz():
    with run_dev_server(model_name="bge-rerank-dev", port=0) as server:
        with urlopen(f"{server['base_url'].removesuffix('/rerank')}/healthz", timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    assert payload["status"] == "ok"
    assert payload["model"] == "bge-rerank-dev"
    assert int(server["port"]) > 0


def test_local_rerank_run_dev_server_accepts_http_request():
    with run_dev_server(model_name="bge-rerank-dev", port=0) as server:
        request = Request(
            server["base_url"],
            data=json.dumps(
                {
                    "model": "bge-rerank-dev",
                    "input": {
                        "query": "graph relation",
                        "documents": ["graph relation path", "calendar planning"],
                    },
                    "parameters": {"return_documents": True, "top_n": 1},
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    assert payload["output"]["results"][0]["index"] == 0

