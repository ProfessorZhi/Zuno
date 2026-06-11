from zuno.services.storage import storage_client
from zuno.settings import app_settings
from zuno.utils.file_utils import get_object_storage_base_path


class UploadService:
    @staticmethod
    def build_storage_public_url(object_name: str) -> str:
        base_url = (app_settings.storage.active.base_url or "").rstrip("/")
        return f"{base_url}/{object_name.lstrip('/')}"

    @classmethod
    def upload_bytes(cls, *, filename: str, content: bytes, content_type: str | None = None) -> str:
        object_name = get_object_storage_base_path(filename)
        public_url = cls.build_storage_public_url(object_name)
        storage_client.upload_file(
            object_name,
            content,
            content_type=content_type or None,
        )
        return public_url


__all__ = ["UploadService"]
