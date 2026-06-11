from __future__ import annotations

import argparse
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
BASE_MANIFEST = BASE_DIR / "corpus" / "contract_review" / "manifest.json"

PARTY_VARIANTS = [
    ("星河科技有限公司", "澄远科技有限公司"),
    ("云川数据服务有限公司", "明栈数据服务有限公司"),
    ("启明零售有限公司", "嘉禾零售有限公司"),
    ("沐光软件有限公司", "景曜软件有限公司"),
    ("海岳银行股份有限公司", "恒岚银行股份有限公司"),
    ("远航制造有限公司", "北辰制造有限公司"),
    ("远航控股有限公司", "北辰控股有限公司"),
    ("锦程置业有限公司", "辰裕置业有限公司"),
    ("橙点餐饮管理有限公司", "禾味餐饮管理有限公司"),
    ("辰星医疗器械有限公司", "华辰医疗器械有限公司"),
    ("凌越精密制造有限公司", "越衡精密制造有限公司"),
    ("启元健康科技有限公司", "元启健康科技有限公司"),
    ("清流云服务有限公司", "清岳云服务有限公司"),
    ("曜石消费电子有限公司", "曜华消费电子有限公司"),
    ("华鼎渠道管理有限公司", "华宸渠道管理有限公司"),
    ("迅维网络科技有限公司", "迅桥网络科技有限公司"),
    ("深联运维有限公司", "深域运维有限公司"),
]

AMOUNT_VARIANTS = [
    ("人民币120万元", "人民币128万元"),
    ("人民币80万元", "人民币88万元"),
    ("人民币36万元", "人民币40万元"),
    ("人民币500万元", "人民币520万元"),
    ("人民币18万元", "人民币19万元"),
    ("人民币36万元", "人民币38万元"),
    ("人民币800万元", "人民币860万元"),
]

TERM_VARIANTS = [
    ("5个工作日", "6个工作日"),
    ("10个工作日", "12个工作日"),
    ("15日", "18日"),
    ("24小时", "12小时"),
    ("30日", "25日"),
    ("90日", "75日"),
]


def _variantize(text: str, *, round_index: int) -> str:
    output = str(text)
    for index, (source, target) in enumerate(PARTY_VARIANTS):
        if (index + round_index) % 2 == 0:
            output = output.replace(source, target)
    for index, (source, target) in enumerate(AMOUNT_VARIANTS):
        if (index + round_index) % 3 == 0:
            output = output.replace(source, target)
    for index, (source, target) in enumerate(TERM_VARIANTS):
        if (index + round_index) % 4 == 0:
            output = output.replace(source, target)
    return output


def build_scaled_corpus(*, output_dir: Path, copies_per_file: int) -> dict:
    manifest = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    output_files_dir = output_dir / "files"
    output_files_dir.mkdir(parents=True, exist_ok=True)

    generated_files: list[dict] = []
    for item in manifest.get("files", []):
        source_path = BASE_MANIFEST.parent / "files" / str(item["file_name"])
        original_text = source_path.read_text(encoding="utf-8")

        original_target = output_files_dir / str(item["file_name"])
        original_target.write_text(original_text, encoding="utf-8")
        generated_files.append(
            {
                "file_name": str(item["file_name"]),
                "prepared_path": str(item["file_name"]),
                "category": item.get("category", "markdown_txt"),
                "extension": item.get("extension", ".md"),
                "relative_path": f"files/{item['file_name']}",
            }
        )

        stem = Path(str(item["file_name"])).stem
        suffix = Path(str(item["file_name"])).suffix
        for round_index in range(1, copies_per_file + 1):
            variant_name = f"{stem}__variant_{round_index}{suffix}"
            variant_text = _variantize(original_text, round_index=round_index)
            (output_files_dir / variant_name).write_text(variant_text, encoding="utf-8")
            generated_files.append(
                {
                    "file_name": variant_name,
                    "prepared_path": variant_name,
                    "category": item.get("category", "markdown_txt"),
                    "extension": item.get("extension", ".md"),
                    "relative_path": f"files/{variant_name}",
                }
            )

    scaled_manifest = {
        "source": "contract_review_scale",
        "dataset": "src/backend/agentchat/evals/rag_eval/datasets/contract_review_graph_relation_small.jsonl",
        "source_root": str(output_files_dir),
        "referenced_file_count": len(generated_files),
        "missing_file_count": 0,
        "missing_files": [],
        "files": generated_files,
    }
    (output_dir / "manifest.json").write_text(json.dumps(scaled_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return scaled_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a larger local contract-review corpus with distractor variants.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BASE_DIR / "corpus" / "contract_review_scale",
    )
    parser.add_argument("--copies-per-file", type=int, default=4)
    args = parser.parse_args()

    manifest = build_scaled_corpus(output_dir=args.output_dir, copies_per_file=max(args.copies_per_file, 0))
    print(json.dumps({"output_dir": str(args.output_dir), "file_count": len(manifest["files"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
