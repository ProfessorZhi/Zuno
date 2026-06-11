import os
import tempfile

import pandas as pd
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import TextSplitter


def excel_loader(path: str, text_splitter: TextSplitter):
    csv_path = path.replace("xlsx", "csv")
    df = pd.read_excel(path)
    df.to_csv(csv_path)

    loader = CSVLoader(csv_path, encoding="utf-8")
    delete_cache_file(csv_path)
    result = loader.load_and_split(text_splitter=text_splitter)
    return result


def delete_cache_file(path: str):
    if os.path.exists(path):
        os.remove(path)


async def excel_to_txt(file_path: str) -> str:
    suffix = os.path.splitext(file_path)[1].lower()
    if suffix not in {".xls", ".xlsx"}:
        raise ValueError("Not an excel file")

    fd, txt_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)

    with open(txt_path, "w", encoding="utf-8") as file:
        xls = pd.ExcelFile(file_path)

        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)

            file.write(f"\n===== Sheet: {sheet_name} =====\n")

            if df.empty:
                continue

            df = df.fillna("")
            for _, row in df.iterrows():
                line = "\t".join(map(str, row.tolist()))
                file.write(line + "\n")

    return txt_path


__all__ = ["delete_cache_file", "excel_loader", "excel_to_txt"]
