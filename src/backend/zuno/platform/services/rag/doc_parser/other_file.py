import csv
import json
import os
import shutil
import tempfile

from bs4 import BeautifulSoup


async def other_file_to_txt(file_path: str) -> str:
    suffix = os.path.splitext(file_path)[1].lower()

    if suffix == ".txt":
        return file_path

    fd, txt_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)

    if suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        with open(txt_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    elif suffix in {".html", ".htm"}:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        text = soup.get_text(separator="\n", strip=True)

        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(text)
    elif suffix == ".csv":
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

        with open(txt_path, "w", encoding="utf-8") as file:
            for row in rows:
                file.write("\t".join(row) + "\n")
    else:
        shutil.copyfile(file_path, txt_path)

    return txt_path


__all__ = ["other_file_to_txt"]
