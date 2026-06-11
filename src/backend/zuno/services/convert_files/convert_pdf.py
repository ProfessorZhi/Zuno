import os
import platform
import subprocess
import sys

from loguru import logger


def convert_to_pdf(input_path):
    if not os.path.exists(input_path):
        raise ValueError(f"鏂囦欢涓嶅瓨鍦? {input_path}")

    filename, ext = os.path.splitext(input_path)
    output_path = filename + ".pdf"
    supported_formats = [
        ".docx",
        ".doc",
        ".odt",
        ".rtf",
        ".txt",
        ".html",
        ".htm",
        ".xls",
        ".xlsx",
        ".ods",
        ".ppt",
        ".pptx",
        ".odp",
    ]

    if ext.lower() not in supported_formats:
        raise ValueError(f"涓嶆敮鎸佺殑鏂囦欢绫诲瀷: {ext}锛屾敮鎸佺殑鏍煎紡鏈? {', '.join(supported_formats)}")

    try:
        libreoffice_cmd = get_libreoffice_command()
        output_dir = os.path.dirname(output_path) or "../rag"
        cmd = [
            libreoffice_cmd,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            input_path,
        ]

        logger.info(f"鎵ц鍛戒护: {' '.join(cmd)}")
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if process.returncode != 0:
            logger.error(f"杞崲澶辫触: {process.stderr}")
            raise ValueError(f"LibreOffice杞崲澶辫触: {process.stderr}")
        if not os.path.exists(output_path):
            raise ValueError(f"杞崲鍚庣殑PDF鏂囦欢鏈壘鍒? {output_path}")

        logger.info(f"宸茶浆鎹负PDF: {output_path}")
        return output_path
    except Exception as exc:
        logger.error(f"杞崲澶辫触: {exc}")
        raise ValueError(f"杞崲澶辫触: {exc}")


def get_libreoffice_command():
    system = platform.system()

    if system == "Windows":
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return "soffice"

    if system == "Darwin":
        possible_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return "soffice"

    for cmd in ["libreoffice", "soffice"]:
        try:
            subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return cmd
        except FileNotFoundError:
            continue

    logger.warning("鏈壘鍒癓ibreOffice锛屼娇鐢ㄩ粯璁ゅ懡浠?libreoffice'")
    return "libreoffice"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("璇锋彁渚涗竴涓杞崲鐨勬枃浠惰矾寰勩€? ")
        logger.info("绀轰緥: python convert_to_pdf.py example.docx")
        sys.exit(1)

    file_path = sys.argv[1]
    convert_to_pdf(file_path)


__all__ = ["convert_to_pdf", "get_libreoffice_command"]
