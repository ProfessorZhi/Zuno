from pathlib import Path

root = Path(__file__).resolve().parents[2]
path = root / "docs/modules/08-security-governance.md"
text = path.read_text(encoding="utf-8")
start = "### Break-glass 为什么需要比普通管理员权限更强的审计\n"
end = "### Audit 数据本身为什么也需要最小化和生命周期\n"
if start not in text or end not in text:
    raise SystemExit("security example boundaries not found")
left, tail = text.split(start, 1)
_, right = tail.split(end, 1)
path.write_text(left + end + right, encoding="utf-8")
Path(__file__).unlink()
