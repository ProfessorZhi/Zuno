from zuno.services.storage.minio import MinioClient
from zuno.services.storage.oss import OSSClient
from zuno.settings import app_settings


class LazyStorageClient:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if app_settings.storage.mode == "minio":
                self._client = MinioClient()
            else:
                self._client = OSSClient()
        return self._client

    def __getattr__(self, item):
        return getattr(self._get_client(), item)


storage_client = LazyStorageClient()


__all__ = ["LazyStorageClient", "MinioClient", "OSSClient", "storage_client"]
