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
replacement = '''### 可信身份为什么不能来自调用方自己提交的字段

前端或 Host 可以携带 tenant、role、matter 等字段，但这些值只是输入声明，不是权限事实。如果后台 Worker 直接相信请求里的 `role=admin` 或 tenant id，攻击者就可以通过修改参数提升权限，异步恢复也会失去可信身份来源。

可信 principal、tenant membership 和 role 必须来自经过验证的身份上下文、受控目录或可信 Host assertion。01 可以负责认证协议和上下文绑定，08 决定这个主体当前能做什么；Prompt、材料正文、模型输出和 Tool 参数都不能把自己升级成权限来源。

这个边界也解释了为什么多租户 Scope 要随着资源引用传播：离开原 HTTP 请求以后，系统仍然要知道当前动作依赖哪个可信身份和事项范围，而不是从普通业务字段重新猜。

### Approval 为什么自己也有生命周期

一次批准不是永久通行证。动作参数、目标资源、ToolVersion、SecurityEpoch、有效期或审批策略发生语义相关变化后，旧 Approval 可能已经不再适用；被撤销或过期的批准也不能因为某个 Runtime Checkpoint 仍写着 granted 就继续使用。

因此 Approval 需要区分 pending、granted、denied、expired、revoked、invalidated 等足以支持当前门禁的状态，并始终绑定它实际批准的动作。这里的重点不是制造复杂审批工作流，而是确保“曾经有人点过同意”不会被误解成未来任意版本动作的权限证明。

''' + end
path.write_text(left + replacement + right, encoding="utf-8")
Path(__file__).unlink()
