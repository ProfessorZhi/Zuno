# ADR 0004：补登记既有 QueueClient 旁路

status: accepted
date: 2026-07-17
owner: Coordinator / Infrastructure / Knowledge
decision_scope: corrective_allowlist_registration

## 背景

P04-T03 审计发现 `src/backend/zuno/platform/services/queue/{client,runner,workers}.py` 在 PHASE01 之前已经存在并被 Knowledge ingestion 调用，但 P01-T05 legacy bypass inventory 漏记了该路径。该 compatibility worker 直接 publish，且 `consume_once` 在领域 handler 返回前 ACK，不满足 canonical Transactional Outbox/Inbox 边界。

PHASE02 规定 temporary allowlist 只能减少，新增旁路默认失败。这里不是批准新增实现，也不是延长 canonical cutover；这是对 pre-existing Current Truth 漏项的纠正。若不补登记，Inventory、Allowlist 与真实代码不一致，guard 会错误地把既有风险隐藏起来。

## 决议

1. 将该既有路径同时补入 `legacy-bypass-inventory.yaml` 与 `temporary-allowlist.yaml`。
2. 分类固定为 `direct_queue_bypass`，不得作为 P04-T03 completion evidence。
3. Canonical gateway 固定为 `zuno.platform.queue` 的 PostgreSQL Outbox、RabbitMQ publisher confirm、Session Inbox 和 domain commit 后 ACK。
4. Migration owner 为 PHASE11 Knowledge ingestion；deadline 为 PHASE11；最终 removal task 为 P22-T03。
5. 本决议不允许新增 caller、扩大 glob、降低 ACK/Inbox/tenant/hash guard，或把 Local Queue / legacy QueueClient 解释为 Server Product Current。

## 验证

- `python tools/scripts/verify_phase02_compatibility_boundaries.py`
- `python tools/scripts/phase02_compatibility_runtime.py --check`
- `python tools/scripts/verify_current_program.py`
- `python tools/scripts/verify_phase04_domain_event_adoption.py`

## 后果

Allowlist 数量因纠正历史漏项临时增加一项，但风险、Owner、deadline、guard 和 removal task 现在可机器追踪。PHASE11 必须迁移现有 caller；P22-T03 删除该 compatibility surface。任何新的 direct queue bypass 仍默认 CI Fail。
