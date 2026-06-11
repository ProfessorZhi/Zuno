from __future__ import annotations

import asyncio
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src/backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from agentchat.evals.rag_eval.run_eval import NO_EVIDENCE_ANSWER, _build_answer


async def _verify_supported_case() -> list[str]:
    errors: list[str] = []
    sample = {
        "id": "strict_grounded_supported_demo",
        "query": "服务商何时删除备份数据？",
        "reference_answer": "在完成数据导出后删除备份数据。",
    }
    contexts = [
        {
            "file_name": "数据处理附录.md",
            "chunk_id": "chunk-supported-1",
            "content": "处理方应先向控制方导出相关数据，并在导出完成后删除备份数据。",
        }
    ]
    answer = await _build_answer(
        sample,
        contexts,
        answer_mode="strict_grounded",
        domain_pack_id="contract_review",
    )
    if str(answer.get("answer") or "") == NO_EVIDENCE_ANSWER:
        errors.append("supported case should not degrade to NO_RELEVANT_EVIDENCE_FOUND")
    if (answer.get("support_verdict") or {}).get("status") != "supported":
        errors.append("supported case should produce support_verdict=supported")
    if len(list(answer.get("citations") or [])) <= 0:
        errors.append("supported case should keep citations")
    if int((answer.get("evidence_bundle") or {}).get("citation_count") or 0) <= 0:
        errors.append("supported case should keep evidence_bundle citation_count")
    return errors


async def _verify_unsupported_case() -> list[str]:
    errors: list[str] = []
    sample = {
        "id": "strict_grounded_unsupported_demo",
        "query": "服务商何时删除备份数据？",
        "reference_answer": "证据不足时应保守失败。",
    }
    contexts = [
        {
            "file_name": "采购框架协议.md",
            "chunk_id": "chunk-unsupported-1",
            "content": "甲方应在完成验收并收到增值税专用发票后支付合同价款。",
        }
    ]
    answer = await _build_answer(
        sample,
        contexts,
        answer_mode="strict_grounded",
        domain_pack_id="contract_review",
    )
    if str(answer.get("answer") or "") != NO_EVIDENCE_ANSWER:
        errors.append("unsupported case should degrade to NO_RELEVANT_EVIDENCE_FOUND")
    if (answer.get("support_verdict") or {}).get("status") != "insufficient_evidence":
        errors.append("unsupported case should produce support_verdict=insufficient_evidence")
    if list(answer.get("citations") or []):
        errors.append("unsupported case should clear citations")
    if int((answer.get("evidence_bundle") or {}).get("document_count") or 0) <= 0:
        errors.append("unsupported case should still keep evidence_bundle document_count")
    return errors


async def _run() -> list[str]:
    errors: list[str] = []
    errors.extend(await _verify_supported_case())
    errors.extend(await _verify_unsupported_case())
    return errors


def main() -> int:
    errors = asyncio.run(_run())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("public demo strict grounding verification failed.")
        return 1
    print("public demo strict grounding verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
