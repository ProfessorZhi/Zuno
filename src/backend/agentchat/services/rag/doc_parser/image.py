import base64
import os
import tempfile
from datetime import datetime, timedelta
from uuid import uuid4

from agentchat.core.models.manager import ModelManager
from agentchat.schema.chunk import ChunkModel


def describe_image(image_path: str) -> str:
    vl_model = ModelManager.get_qwen_vl_model()
    image_type = image_path.split(".")[-1]
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    response = vl_model.invoke(
        input=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{image_type};base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": "图中描绘的是什么景象？要求：1.字数不超过100字。2.直接输出图片描述文本",
                    },
                ],
            },
        ],
    )
    return response.content.strip()


def image_to_txt(image_path: str):
    description = describe_image(image_path)
    fd, txt_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(description)

    return txt_path


def build_image_chunk(
    *,
    file_id: str,
    file_name: str,
    knowledge_id: str,
    source_url: str,
    image_name: str,
    description: str,
) -> ChunkModel:
    update_time = datetime.utcnow() + timedelta(hours=8)
    chunk_id = f"{os.path.splitext(image_name)[0]}_{uuid4().hex}"
    return ChunkModel(
        chunk_id=chunk_id[:128] if len(chunk_id) > 128 else chunk_id,
        content=description.strip(),
        file_id=file_id,
        file_name=file_name,
        knowledge_id=knowledge_id,
        update_time=update_time.isoformat(),
        modality="image",
        source_url=source_url,
    )
