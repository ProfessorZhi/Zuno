import mimetypes

import oss2
from loguru import logger

from zuno.settings import app_settings


class OSSClient:
    def __init__(self):
        auth = oss2.Auth(
            access_key_id=app_settings.storage.oss.access_key_id,
            access_key_secret=app_settings.storage.oss.access_key_secret,
        )
        self.bucket = oss2.Bucket(
            auth=auth,
            endpoint=app_settings.storage.oss.endpoint,
            bucket_name=app_settings.storage.oss.bucket_name,
        )

    def upload_file(self, object_name, data, content_type: str | None = None):
        try:
            resolved_content_type = (
                content_type
                or mimetypes.guess_type(object_name)[0]
                or "application/octet-stream"
            )
            headers = {"Content-Type": resolved_content_type}
            result = self.bucket.put_object(object_name, data, headers=headers)
            logger.info(f"File uploaded successfully, status code: {result.status}")
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to upload file: {exc}")

    def upload_local_file(self, object_name, local_file):
        try:
            result = self.bucket.put_object_from_file(object_name, local_file)
            logger.info(f"Local file uploaded successfully, status code: {result.status}")
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to upload file : {exc}")

    def delete_bucket(self):
        try:
            self.bucket.delete_bucket()
            logger.info("Bucket deleted successfully")
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to delete bucket: {exc}")

    def sign_url_for_get(self, object_name, expiration=3600):
        try:
            return self.bucket.sign_url("GET", object_name, expiration, slash_safe=True)
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to generate GET URL for {object_name}: {exc}")

    def download_file(self, object_name, local_file):
        try:
            self.bucket.get_object_to_file(object_name, local_file)
            logger.info(f"File {object_name} downloaded successfully to {local_file}")
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to download {object_name} to {local_file}: {exc}")

    def get_file_bytes(self, object_name):
        try:
            return self.bucket.get_object(object_name).read()
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to read {object_name}: {exc}")
            return b""

    def list_files_in_folder(self, folder_path):
        try:
            if folder_path and not folder_path.endswith("/"):
                folder_path += "/"

            files_url = []
            for obj in oss2.ObjectIterator(
                self.bucket, prefix=folder_path, delimiter="/"
            ):
                if not obj.is_prefix():
                    files_url.append(obj.key)
            return [file_url for file_url in files_url if not file_url.endswith("/")]
        except oss2.exceptions.OssError as exc:
            logger.error(f"Failed to list files in folder {folder_path}: {exc}")
            return []


__all__ = ["OSSClient"]
