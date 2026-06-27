# PHASE04：Workflow Verifier 与漂移测试

## 目标

把 Program 1 的工作流规则变成自动检查，防止后续再次出现 active program 混杂、phase 编号漂移、queued plan 被误执行、docs / agent 状态不一致。

## 范围

- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify_doc_boundaries.py`
- `.agent/scripts/verify_repo_hygiene.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_docs_entrypoints.py`
- `tests/repo/test_repo_hygiene.py`
- `tests/repo/test_repo_structure_consistency.py`

## 可并行线程

建议串行。Verifier 之间共享规则，多个写入线程容易产生重复或互相打架。

## 不做

- 不扩大到 runtime tests。
- 不新增重依赖。
- 不用测试掩盖文档漂移；要修根因。

## 验收

- Verifier 能识别 `.agent/programs` 只承载当前 active program。
- Verifier 能识别 queued plan pack 不能被 active current 引用为正在执行。
- Repo tests 覆盖新增规则。

## 验证

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```
