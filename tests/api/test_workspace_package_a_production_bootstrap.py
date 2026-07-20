from types import SimpleNamespace

from zuno.api.services.workspace_task_runtime import (
    build_package_a_production_ingestion_runtime,
)


def test_package_a_production_bootstrap_builds_minio_postgres_runtime():
    calls: dict[str, object] = {}
    engine = object()

    def object_store_factory(**kwargs):
        calls["object_store"] = kwargs
        return "minio-store"

    def durable_object_store_factory(**kwargs):
        calls["durable_object_store"] = kwargs
        return "durable-minio-store"

    def runtime_factory(**kwargs):
        calls["runtime"] = kwargs
        return "package-a-runtime"

    settings = SimpleNamespace(
        storage=SimpleNamespace(
            mode="minio",
            minio=SimpleNamespace(
                endpoint="minio:9000",
                access_key_id="minioadmin",
                access_key_secret="minioadmin",
            ),
        )
    )

    runtime = build_package_a_production_ingestion_runtime(
        engine=engine,
        settings=settings,
        object_store_factory=object_store_factory,
        durable_object_store_factory=durable_object_store_factory,
        runtime_factory=runtime_factory,
    )

    assert runtime == "package-a-runtime"
    assert calls["object_store"] == {
        "endpoint": "minio:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "secure": False,
    }
    assert calls["durable_object_store"] == {
        "store": "minio-store",
        "engine": engine,
        "owner": "workspace.file_upload",
    }
    assert calls["runtime"] == {
        "engine": engine,
        "object_store": "durable-minio-store",
        "worker_id": "workspace-file-upload",
    }


def test_package_a_production_bootstrap_stays_unconfigured_without_minio_credentials():
    engine = object()
    settings = SimpleNamespace(
        storage=SimpleNamespace(
            mode="minio",
            minio=SimpleNamespace(
                endpoint="127.0.0.1:9000",
                access_key_id="",
                access_key_secret="",
            ),
        )
    )

    runtime = build_package_a_production_ingestion_runtime(
        engine=engine,
        settings=settings,
    )

    assert runtime is None
