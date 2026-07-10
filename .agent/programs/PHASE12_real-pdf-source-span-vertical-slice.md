# PHASE12_real-pdf-source-span-vertical-slice

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE12
    state: planned
    title: 真实 PDF SourceSpan 纵向切片
    depends_on: PHASE11
    next_phase: PHASE13

    ## 目标

    使用 PyMuPDF 完成至少一个真实 PDF 从上传、解析、IR、chunk、index、retrieval、citation 到 Agent answer 的纵向闭环。

    ## 当前事实

    文档 ingestion/index baseline 已存在，但真实 PDF parser + source-span citation vertical slice 仍是 closure gap。

    ## 目标增量

    实现 PyMuPDF adapter：page/block/text、page、bbox、offset、diagnostics、DocumentVersion、CitationChunk/ParentChunk、SourceSpan。OCR/VLM 不在本 Phase。

    ## 代码落点

    ```text
src/backend/zuno/knowledge/ingestion/parsers/pymupdf_adapter.py
src/backend/zuno/knowledge/ingestion/parse_gateway.py
src/backend/zuno/knowledge/ingestion/contracts.py
tests/fixtures/documents/<small-real-pdf>.pdf
tests/knowledge/test_pdf_source_span_vertical.py
tests/e2e/test_pdf_agent_answer.py
```

    ## 实施步骤

    1. 确认并固定 PyMuPDF 依赖。
2. 输出 CanonicalDocumentIR。
3. block 保存 page、bbox、block index、offset。
4. chunk 保留覆盖 spans。
5. parent 只做 context expansion；citation 指 SourceSpan。
6. version/checksum 变化旧 citation 标 stale。
7. parser failure 不 fake index。
8. 使用小型合法 fixture PDF。
9. EvidenceLedger 保存 PDF span。
10. final citation 指 page/block。

    ## 关键代码草图

    ```python
class PyMuPDFParserAdapter:
    parser_id="pymupdf"
    def parse(self, source):
        doc=fitz.open(source.local_path)
        blocks=[]
        for page_index,page in enumerate(doc):
            for block_index,block in enumerate(page.get_text("blocks")):
                x0,y0,x1,y1,text,*_=block
                blocks.append(DocumentBlock(
                    block_id=...,
                    text=normalize(text),
                    source_span=SourceSpan(
                        document_id=source.document_id,
                        document_version_id=source.version_id,
                        page_number=page_index+1,
                        bbox=[x0,y0,x1,y1],
                        block_index=block_index,
                    ),
                ))
        return CanonicalDocumentIR(...)
```

    ## 测试

    golden fixture、多页 span、corrupt blocked、version stale、grain boundary、evidence text、final page citation、无 OCR claim。

    ## 验收标准

    真实 PDF E2E；SourceSpan 完整；UI/API 可展示页码；parser failure 真实。

    ## Windows PowerShell 验证

    ```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath 'F:\internship-work\resume&resume project\02_projects\Zuno'
$VenvPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$Python = if (Test-Path -LiteralPath $VenvPython) { (Resolve-Path -LiteralPath $VenvPython).Path } else { 'python' }
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'src\backend').Path
```
```powershell
$Targets=@('-m','pytest','-q','tests\knowledge\test_pdf_source_span_vertical.py','tests\e2e\test_pdf_agent_answer.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'PDF vertical tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    PyMuPDF 不可用则 Phase blocked，不用伪 parser。扫描 PDF 返回 needs_ocr。

    ## 文档与状态同步

    更新 ingestion、input topic、production-readiness。

    ## Phase 完成报告

    Codex 必须报告：

    1. 修改文件和 owner。
    2. 新增或修改的 contract。
    3. 真实调用链。
    4. 测试命令与结果。
    5. trace、restart 或 eval 证据。
    6. 未完成和 blocked 项。
    7. commit SHA。
    8. 下一 Phase 是否满足依赖。
