from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from tools.evals.zuno.multihop_eval.adapters.common import read_json_or_jsonl, read_json_or_jsonl_text, write_jsonl
from tools.evals.zuno.multihop_eval.adapters.hotpotqa import normalize_records as normalize_hotpotqa
from tools.evals.zuno.multihop_eval.adapters.musique import normalize_records as normalize_musique
from tools.evals.zuno.multihop_eval.adapters.twowiki import normalize_records as normalize_twowiki


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_RAW_ROOT = REPO_ROOT / "data" / "evals" / "multihop" / "raw"
DEFAULT_NORMALIZED_ROOT = REPO_ROOT / "data" / "evals" / "multihop" / "normalized"


@dataclass(frozen=True)
class DownloadPlan:
    dataset: str
    split: str
    url: str
    raw_name: str
    extracted_name: str | None
    normalizer: Callable[[list[dict]], list[dict]]
    archive: bool = False
    gdown_id: str | None = None
    fallback_urls: tuple[str, ...] = ()


def resolve_download_plan(*, dataset: str, split: str) -> DownloadPlan:
    normalized_dataset = dataset.strip().lower()
    normalized_split = split.strip().lower()
    if normalized_dataset == "hotpotqa":
        file_name = "hotpot_dev_fullwiki_v1.json" if normalized_split == "dev_fullwiki" else "hotpot_dev_distractor_v1.json"
        return DownloadPlan(
            dataset="hotpotqa",
            split=normalized_split,
            url=f"http://curtis.ml.cmu.edu/datasets/hotpot/{file_name}",
            raw_name=file_name,
            extracted_name=file_name,
            normalizer=normalize_hotpotqa,
            fallback_urls=(
                f"https://huggingface.co/datasets/namlh2004/hotpotqa/resolve/main/{file_name}?download=true",
            ),
        )
    if normalized_dataset in {"twowiki", "2wiki", "2wikimultihopqa"}:
        return DownloadPlan(
            dataset="2wikimultihopqa",
            split=normalized_split,
            url="https://www.dropbox.com/s/ms2m13252h6xubs/data_ids_april7.zip?dl=1",
            raw_name="data_ids_april7.zip",
            extracted_name=f"data_ids/{normalized_split}.json",
            normalizer=normalize_twowiki,
            archive=True,
        )
    if normalized_dataset == "musique":
        file_name = f"musique_ans_v1.0_{normalized_split}.jsonl"
        return DownloadPlan(
            dataset="musique",
            split=normalized_split,
            url="https://drive.google.com/uc?id=1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h",
            raw_name="musique_v1.0.zip",
            extracted_name=f"data/{file_name}",
            normalizer=normalize_musique,
            archive=True,
            gdown_id="1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h",
            fallback_urls=(
                "https://drive.usercontent.google.com/download?id=1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h&confirm=t",
            ),
        )
    raise ValueError(f"Unsupported dataset: {dataset}")


def _download_url(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            output.write_bytes(response.read())
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise RuntimeError(f"failed to download {url}: {error}") from error
    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"download produced an empty file: {output}")


def _looks_like_html(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    prefix = path.read_bytes()[:512].decode("utf-8", errors="ignore").lstrip().lower()
    return prefix.startswith("<!doctype html") or prefix.startswith("<html")


def _download_with_fallbacks(primary_url: str, fallback_urls: tuple[str, ...], output: Path) -> None:
    errors: list[str] = []
    for url in (primary_url, *fallback_urls):
        try:
            _download_url(url, output)
            if _looks_like_html(output):
                raise RuntimeError("downloaded HTML instead of dataset payload")
            return
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("all download sources failed: " + " | ".join(errors))


def _download_with_gdown(plan: DownloadPlan, output: Path) -> None:
    if not plan.gdown_id:
        _download_with_fallbacks(plan.url, plan.fallback_urls, output)
        return
    gdown = shutil.which("gdown")
    if not gdown:
        _download_with_fallbacks(plan.url, plan.fallback_urls, output)
        return
    result = subprocess.run(
        [gdown, "--id", plan.gdown_id, "--output", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gdown failed for {plan.dataset}: {result.stderr or result.stdout}")
    if _looks_like_html(output):
        raise RuntimeError(f"gdown downloaded HTML instead of archive for {plan.dataset}")


def _extract_archive(archive_path: Path, extract_root: Path) -> None:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_root)
    except zipfile.BadZipFile as error:
        raise RuntimeError(f"invalid zip archive: {archive_path}") from error


def _is_valid_archive(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0 or _looks_like_html(path):
        return False
    return zipfile.is_zipfile(path)


def _read_archive_member(archive_path: Path, member_name: str) -> list[dict]:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            target_names = {member_name, Path(member_name).name}
            chosen = None
            for info in archive.infolist():
                if info.filename in target_names or Path(info.filename).name in target_names:
                    chosen = info.filename
                    break
            if not chosen:
                raise FileNotFoundError(f"could not locate archive member: {member_name}")
            raw_bytes = archive.read(chosen)
    except zipfile.BadZipFile as error:
        raise RuntimeError(f"invalid zip archive: {archive_path}") from error
    return read_json_or_jsonl_text(
        text=raw_bytes.decode("utf-8"),
        source=member_name,
    )


def _locate_extracted(raw_root: Path, extracted_name: str | None, raw_file: Path) -> Path:
    if not extracted_name:
        return raw_file
    direct = raw_root / extracted_name
    if direct.exists():
        return direct
    matches = list(raw_root.rglob(Path(extracted_name).name))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"could not locate extracted dataset file: {extracted_name}")


def normalize_dataset(plan: DownloadPlan, raw_path: Path, output_path: Path, *, sample: int | None = None) -> list[dict]:
    records = read_json_or_jsonl(raw_path)
    if sample is not None:
        records = records[: max(sample, 0)]
    normalized = plan.normalizer(records)
    write_jsonl(output_path, normalized)
    return normalized


def normalize_dataset_from_records(
    plan: DownloadPlan,
    records: list[dict],
    output_path: Path,
    *,
    sample: int | None = None,
) -> list[dict]:
    if sample is not None:
        records = records[: max(sample, 0)]
    normalized = plan.normalizer(records)
    write_jsonl(output_path, normalized)
    return normalized


def download_and_normalize(
    *,
    dataset: str,
    split: str,
    sample: int | None,
    raw_root: Path = DEFAULT_RAW_ROOT,
    normalized_root: Path = DEFAULT_NORMALIZED_ROOT,
) -> Path:
    plan = resolve_download_plan(dataset=dataset, split=split)
    dataset_raw_root = raw_root / plan.dataset
    raw_file = dataset_raw_root / plan.raw_name
    should_download = not raw_file.exists()
    if plan.archive and raw_file.exists() and not _is_valid_archive(raw_file):
        raw_file.unlink(missing_ok=True)
        should_download = True
    if should_download:
        if plan.gdown_id:
            _download_with_gdown(plan, raw_file)
        else:
            _download_with_fallbacks(plan.url, plan.fallback_urls, raw_file)
    suffix = f"sample{sample}" if sample is not None else "full"
    output_path = normalized_root / plan.dataset / f"{plan.split}_{suffix}.jsonl"
    if plan.archive and plan.extracted_name:
        records = _read_archive_member(raw_file, plan.extracted_name)
        normalize_dataset_from_records(plan, records, output_path, sample=sample)
    else:
        extracted = _locate_extracted(dataset_raw_root, plan.extracted_name, raw_file)
        normalize_dataset(plan, extracted, output_path, sample=sample)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and normalize multi-hop eval datasets.")
    parser.add_argument("--dataset", required=True, choices=["hotpotqa", "twowiki", "2wikimultihopqa", "musique"])
    parser.add_argument("--split", default="dev")
    parser.add_argument("--sample", type=int, default=None)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--normalized-root", type=Path, default=DEFAULT_NORMALIZED_ROOT)
    args = parser.parse_args()

    try:
        output = download_and_normalize(
            dataset=args.dataset,
            split=args.split,
            sample=args.sample,
            raw_root=args.raw_root,
            normalized_root=args.normalized_root,
        )
    except Exception as error:
        raise SystemExit(f"dataset download failed: {error}") from error
    print(json.dumps({"output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
