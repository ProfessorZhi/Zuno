from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

replacements = {
    "docs/modules/01-application-integration.md": [
        (
            "01 应把 admission control 当成产品语义的一部分：哪些请求可以立即处理，哪些可以排队，哪些应该让客户端稍后重试，哪些简单任务可以走更短路径。",
            "01 应把流量准入（load admission）当成产品语义的一部分：哪些请求可以立即处理，哪些可以排队，哪些应该让客户端稍后重试，哪些简单任务可以走更短路径。",
        ),
    ],
    "docs/modules/04-agent-runtime-control.md": [
        (
            "### Runtime Admission Control 为什么和 Step 并行度是两个问题",
            "### Runtime 负载准入为什么和 Step 并行度是两个问题",
        ),
        (
            "运行时 admission control 可以按 task class、priority、budget 和资源 profile 决定立即激活、排队或拒绝；已经激活的 Run 再由 scheduler 决定哪些 Ready Step 现在派发。",
            "运行时负载准入可以按 task class、priority、budget 和资源 profile 决定立即激活、排队或拒绝；已经激活的 Run 再由 scheduler 决定哪些 Ready Step 现在派发。",
        ),
    ],
    "docs/modules/06-tool-runtime-effects.md": [
        (
            "是否需要 resource version、业务唯一约束、串行化或远端 CAS，要由具体 Tool 语义决定。06 至少必须让 ToolDefinition 表达这种并发前提，而不能把“我们有 idempotency key”误写成“所有并发都安全”。",
            "是否需要 resource version、业务唯一约束、串行化或远端 CAS，要由具体 Tool 语义决定。06 至少要在 Tool 语义中明确这种并发前提是否存在；具体由哪个字段或 Contract 表达留到 Detail Design，而不能把“我们有 idempotency key”误写成“所有并发都安全”。",
        ),
    ],
}

for relative, pairs in replacements.items():
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise RuntimeError(f"missing text in {relative}: {old}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")

Path(__file__).unlink()
