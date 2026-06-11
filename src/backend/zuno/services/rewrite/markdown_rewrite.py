import asyncio
import base64
import os
import re
from urllib.parse import urljoin

from loguru import logger

from zuno.core.models.manager import ModelManager

from zuno.settings import app_settings


class MarkdownRewrite:
    def __init__(self, **kwargs):
        self.client = None

    def _get_client(self):
        if self.client is None:
            self.client = ModelManager.get_qwen_vl_model()
        return self.client

    async def _get_image_dict(self, markdown_path):
        parent_dir = os.path.dirname(markdown_path)
        images_dir = os.path.join(parent_dir, "images")
        image_path_dict = {}
        if os.path.exists(images_dir):
            for path in os.listdir(images_dir):
                image_path_dict[path] = os.path.join(images_dir, path)
        return image_path_dict

    async def _read_markdown(self, markdown_path):
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Markdown 文件未找到: {markdown_path}")
        with open(markdown_path, "r", encoding="utf-8") as file:
            return file.read()

    async def request_vl(self, image_path):
        image_type = image_path.split(".")[-1]
        base64_image = await MarkdownRewrite.encode_image(image_path)
        response = await self._get_client().ainvoke(
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
                            "text": "图中描绘的是什么景象? 要求:1.字数不超过100字。2.直接输出图片描述文本",
                        },
                    ],
                },
            ],
        )
        logger.debug(f"{image_path} 中的描述信息为 {response.content}")
        return response.content

    async def async_request_vl(self, image, image_path):
        result = await self.request_vl(image_path)
        return image, result

    async def get_image_description(self, image_path_dict):
        semaphore = asyncio.Semaphore(3)

        async def limited_request(image, image_path):
            async with semaphore:
                return await self.async_request_vl(image, image_path)

        tasks = [limited_request(image, image_path) for image, image_path in image_path_dict.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        image_desc_dict = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"图片描述信息出现错误: {result}")
                continue

            image, desc = result
            image_desc_dict[image] = desc
        return image_desc_dict

    async def process_markdown(self, markdown_text, image_oss_dict, image_desc_dict):
        pattern = r"!\[.*?\]\((.*?)\)"

        def replace_image(match):
            image_url = match.group(1)
            image_oss_object_name = image_oss_dict.get(os.path.basename(image_url))
            image_desc = image_desc_dict.get(os.path.basename(image_url))
            return f"![{image_desc}]({urljoin(app_settings.storage.active.base_url, image_oss_object_name)})"

        result = re.sub(pattern, replace_image, markdown_text)
        return result

    async def run_rewrite(self, markdown_path, image_oss_dict):
        markdown_text = await self._read_markdown(markdown_path)
        image_path_dict = await self._get_image_dict(markdown_path)
        image_desc_dict = await self.get_image_description(image_path_dict)
        new_markdown_text = await self.process_markdown(markdown_text, image_oss_dict, image_desc_dict)

        with open(markdown_path, "w", encoding="utf-8") as file:
            file.write(new_markdown_text)
        logger.info("Markdown 文档已经重写完成")

    @staticmethod
    async def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


class LazyMarkdownRewrite:
    def __init__(self):
        self._rewriter = None

    def _get_rewriter(self) -> MarkdownRewrite:
        if self._rewriter is None:
            self._rewriter = MarkdownRewrite()
        return self._rewriter

    def __getattr__(self, item):
        return getattr(self._get_rewriter(), item)


markdown_rewriter = LazyMarkdownRewrite()


__all__ = ["LazyMarkdownRewrite", "MarkdownRewrite", "markdown_rewriter"]
