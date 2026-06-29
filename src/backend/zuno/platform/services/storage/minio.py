import io
import json
import mimetypes

from loguru import logger
from minio import Minio
from minio.error import S3Error

from zuno.settings import app_settings


class MinioClient:
    def __init__(self):
        self.client = Minio(
            secure=False,
            endpoint=app_settings.storage.minio.endpoint,
            access_key=app_settings.storage.minio.access_key_id,
            secret_key=app_settings.storage.minio.access_key_secret,
        )
        self.bucket_name = app_settings.storage.minio.bucket_name
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.success(f"Minio Bucket: {self.bucket_name} created success")
        self._ensure_public_read_policy()

    def _ensure_public_read_policy(self):
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}"],
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"],
                    },
                ],
            }
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
        except S3Error as exc:
            logger.error(
                f"Failed to set public read policy for bucket {self.bucket_name}: {exc}"
            )

    def upload_file(self, object_name, data, content_type: str | None = None):
        try:
            if isinstance(data, (bytes, bytearray)):
                data_stream = io.BytesIO(data)
                length = len(data)
            else:
                data = data.encode("utf-8") if isinstance(data, str) else data
                data_stream = io.BytesIO(data)
                length = len(data)
            resolved_content_type = (
                content_type
                or mimetypes.guess_type(object_name)[0]
                or "application/octet-stream"
            )
            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length,
                content_type=resolved_content_type,
            )
            logger.info(f"File uploaded successfully: {object_name}")
        except S3Error as exc:
            logger.error(f"Failed to upload file: {exc}")

    def upload_local_file(self, object_name, local_file):
        try:
            self.client.fput_object(self.bucket_name, object_name, local_file)
            logger.info(f"Local file uploaded successfully: {object_name}")
        except S3Error as exc:
            logger.error(f"Failed to upload file : {exc}")

    def delete_bucket(self):
        try:
            self.client.remove_bucket(self.bucket_name)
            logger.info("Bucket deleted successfully")
        except S3Error as exc:
            logger.error(f"Failed to delete bucket: {exc}")

    def sign_url_for_get(self, object_name, expiration=3600):
        try:
            from datetime import timedelta

            return self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(seconds=expiration)
            )
        except S3Error as exc:
            logger.error(f"Failed to generate GET URL for {object_name}: {exc}")

    def download_file(self, object_name, local_file):
        try:
            self.client.fget_object(self.bucket_name, object_name, local_file)
            logger.info(f"File {object_name} downloaded successfully to {local_file}")
        except S3Error as exc:
            logger.error(f"Failed to download {object_name} to {local_file}: {exc}")

    def get_file_bytes(self, object_name):
        response = None
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as exc:
            logger.error(f"Failed to read {object_name}: {exc}")
            return b""
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def list_files_in_folder(self, folder_path):
        try:
            if folder_path and not folder_path.endswith("/"):
                folder_path += "/"

            objects = self.client.list_objects(
                self.bucket_name, prefix=folder_path, recursive=False
            )
            return [
                obj.object_name
                for obj in objects
                if not obj.is_dir and not obj.object_name.endswith("/")
            ]
        except S3Error as exc:
            logger.error(f"Failed to list files in folder {folder_path}: {exc}")
            return []


__all__ = ["MinioClient"]
