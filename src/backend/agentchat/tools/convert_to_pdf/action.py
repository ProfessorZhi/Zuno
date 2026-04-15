import os
import shutil
import subprocess
import tempfile

from langchain.tools import tool

from agentchat.services.storage import storage_client
from agentchat.utils.file_utils import get_object_name_from_aliyun_url, get_save_tempfile
from agentchat.utils.helpers import get_now_beijing_time


@tool("docx_to_pdf", parse_docstring=True)
def convert_to_pdf(file_url: str):
    """
    Convert a user uploaded office document into a PDF download link.

    Args:
        file_url (str): Uploaded document URL.

    Returns:
        str: Conversion result message with a temporary download link.
    """
    return _convert_to_pdf(file_url)


def _convert_to_pdf(file_url: str):
    object_name = get_object_name_from_aliyun_url(file_url)
    file_name = file_url.split("/")[-1]
    file_path = get_save_tempfile(file_name)
    storage_client.download_file(object_name, file_path)

    if not os.path.isfile(file_path):
        return f"上传的文件 {os.path.basename(file_path)} 没有成功接收，请重新上传后再试。"

    file_extension = file_path.split(".")[-1].lower()
    supported_formats = [
        "docx",
        "doc",
        "odt",
        "rtf",
        "txt",
        "html",
        "htm",
        "xls",
        "xlsx",
        "ods",
        "ppt",
        "pptx",
        "odp",
    ]
    if file_extension not in supported_formats:
        return f"当前支持的格式有: {', '.join(supported_formats)}，暂不支持 {file_extension}。"

    office_binary = shutil.which("libreoffice") or shutil.which("soffice")
    if not office_binary:
        return "Docx 转 PDF 工具暂不可用：当前运行环境未安装 LibreOffice，请先补齐依赖。"

    try:
        output_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)

        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        pdf_filename = f"{base_filename}.pdf"
        local_pdf_path = os.path.join(output_dir, pdf_filename)

        process = subprocess.run(
            [
                office_binary,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if process.returncode != 0:
            return f"{os.path.basename(file_path)} 转换失败：{process.stderr or process.stdout}"

        if not os.path.exists(local_pdf_path):
            return f"{os.path.basename(file_path)} 转换失败：未生成 PDF 文件。"

        oss_object_name = f"convert_pdf/{pdf_filename}"
        storage_client.upload_local_file(oss_object_name, local_pdf_path)

        url = storage_client.sign_url_for_get(oss_object_name)
        now_time = get_now_beijing_time(delta=1)

        try:
            os.remove(file_path)
            os.remove(local_pdf_path)
            os.rmdir(output_dir)
        except OSError:
            pass

        return f"{os.path.basename(file_path)} 已转换为 PDF，下载链接：{url}，请在 {now_time} 前下载。"
    except Exception as err:
        return f"{os.path.basename(file_path)} 转换失败：{err}"
