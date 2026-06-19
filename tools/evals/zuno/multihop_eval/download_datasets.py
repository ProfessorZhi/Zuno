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

from tools.evals.zuno.multihop_eval.adapters.common import read_json_or_jsonl, write_jsonl
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


def _download_with_gdown(plan: DownloadPlan, output: Path) -> None:
    if not plan.gdown_id:
        _download_url(plan.url, output)
        return
    gdown = shutil.which("gdown")
    if not gdown:
        _download_url(plan.url, output)
        return
    result = subprocess.run(
        [gdown, "--id", plan.gdown_id, "--output", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gdown failed for {plan.dataset}: {result.stderr or result.stdout}")


def _extract_archive(archive_path: Path, extract_root: Path) -> None:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_root)
    except zipfile.BadZipFile as error:
        raise RuntimeError(f"invalid zip archive: {archive_path}") from error


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
    if not raw_file.exists():
        if plan.gdown_id:
            _download_with_gdown(plan, raw_file)
        else:
            _download_url(plan.url, raw_file)
    if plan.archive:
        _extract_archive(raw_file, dataset_raw_root)
    extracted = _locate_extracted(dataset_raw_root, plan.extracted_name, raw_file)
    suffix = f"sample{sample}" if sample is not None else "full"
    output_path = normalized_root / plan.dataset / f"{plan.split}_{suffix}.jsonl"
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

