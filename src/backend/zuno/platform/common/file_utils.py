# encoding=utf-8
import json
import logging
import os
import tempfile
from urllib.parse import urlparse
from uuid import uuid4

import aiofiles

from zuno.utils.date_utils import get_beijing_date_str


def format_file_size(size_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
    return f"{round(size_bytes, 2)}{units[unit_index]}"


def load_file_to_obj(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logging.error(f"Error loading scene prompts: {exc}")
        return {}


def get_object_storage_base_path(file_name):
    beijing_time = get_beijing_date_str()
    file_type = get_file_type(file_name)
    new_file_name = reset_file_name(file_name)
    return f"files/{beijing_time}/{file_type}/{new_file_name}"


def get_file_type(file_name):
    return file_name.split(".")[-1]


def reset_file_name(file_name):
    file_type = get_file_type(file_name)
    base_name = os.path.splitext(file_name)[0]
    return f"{base_name}_{str(uuid4().hex)[:10]}.{file_type}"


async def save_upload_file(upload_file):
    temp = tempfile.mkdtemp()
    file_name = os.path.basename(upload_file.file_name)
    file_path = os.path.join(temp, file_name)
    async with aiofiles.open(file_path, "wb") as file:
        content = await upload_file.read()
        await file.write(content)
    return file_path


def get_object_name_from_aliyun_url(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.path.lstrip("/")


def get_object_key_from_public_url(url: str, bucket_name: str = "") -> str:
    parsed_url = urlparse(url)
    object_key = parsed_url.path.lstrip("/") if parsed_url.scheme else url.lstrip("/")
    if bucket_name:
        bucket_prefix = f"{bucket_name.strip('/')}/"
        if object_key.startswith(bucket_prefix):
            object_key = object_key[len(bucket_prefix) :]
    return object_key


def get_save_tempfile(file_name):
    temp = tempfile.mkdtemp()
    file_name = os.path.basename(file_name)
    return os.path.join(temp, file_name)


def get_images_dir(images_dir: str = "images"):
    temp = tempfile.mkdtemp()
    return os.path.join(temp, images_dir)


def get_markdown_dir():
    return get_images_dir("markdown")


def get_convert_markdown_images_dir():
    temp = tempfile.mkdtemp()
    images_path = os.path.join(temp, "images")
    return temp, images_path


def generate_unique_filename(file_name: str, file_suffix: str = None) -> str:
    file_name = os.path.basename(file_name)
    stem = file_name.split(".")[0]
    suffix = file_suffix or file_name.split(".")[-1]
    return f"{stem}_{uuid4().hex}.{suffix}"


async def get_oss_object_name(file_path, knowledge_id):
    file_name = os.path.basename(file_path)
    file_suffix = file_name.split(".")[-1]
    stem = os.path.splitext(file_name)[0]
    object_name = f"/{knowledge_id}/{stem}_{uuid4().hex}.{file_suffix}"
    return object_name


async def read_upload_file(file_path):
    async with aiofiles.open(file_path, "r") as file:
        content = await file.read()
    return content


__all__ = [
    "format_file_size",
    "generate_unique_filename",
    "get_convert_markdown_images_dir",
    "get_file_type",
    "get_images_dir",
    "get_markdown_dir",
    "get_object_key_from_public_url",
    "get_object_name_from_aliyun_url",
    "get_object_storage_base_path",
    "get_oss_object_name",
    "get_save_tempfile",
    "load_file_to_obj",
    "read_upload_file",
    "reset_file_name",
    "save_upload_file",
]
