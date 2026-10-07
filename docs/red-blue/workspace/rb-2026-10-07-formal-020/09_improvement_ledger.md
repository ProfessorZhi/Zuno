# Improvement Ledger — rb-2026-10-07-formal-020

```text
improvement_ledger_status: APPROVED
change_effective_scope: NEXT_ROUND_ONLY
current_round_verdict_recomputed: false
base_sha: 7d3081f2ccaa20c7eeb0bfff75206d08584a6e51
user_decision_2026_10_07:
  A组(IMP-020-01/02/03): APPROVED_FOR_NEXT_ROUND — 三条 P0 安全项下一轮作为最高优先级处理
  IMP-020-10: APPROVED_APPLIED — 已知边界已写入 docs/project/README.md（本轮应用）
  下一轮 frozen resume: 采用 10_next_resume_candidate.md
applied_this_round: IMP-020-10 → docs/project/README.md「Commit 历史不能单独证明个人 Ownership」
```

**本文件曾为提案，现已获用户批准（2026-10-07）。** 除 `IMP-020-10` 外，其余条目一律 `NEXT_ROUND_ONLY`；本轮 verdict 不因本文件而改变。

**判定纪律（贯穿全表）：**

- 系统本身没问题、只是候选人没讲清的 → `NARRATIVE_GAP` / `SIMULATED_RESUME_GAP`，**`proposed_change: none`**。
- 设计写了但代码没有的 → `IMPLEMENTATION_GAP`，如实标 Target。
- 只有 Owner / Authority / State / Contract / Recovery / Security / Build-Buy 因果本身不成立，才进 `ARCHITECTURE_GAP`。
- **不制造任何收益数字。** 所有量化的 TBD 一律标 `MEASUREMENT_NEEDED`，不填估计值。

**Controller 独立验证声明：** 下表 A 组的三条安全发现与 S01 默认开启链，由 Controller 亲自打开源码复核过（`file:line` 见「证据」列）。其余条目沿用 Blue 架构侧的 `source_check`，标注为 `BLUE_VERIFIED`。

---

## A 组 · 安全 / fail-open（最高优先级）

### IMP-020-01 — 知识就绪状态在读取路径上默认开启

```text
来源: S01（第一轮）+ N02（第二轮扩围）
gap_type: IMPLEMENTATION_GAP（语义上是 ARCHITECTURE_GAP 的一角：Readiness 存在第二个所有者）
fact_layer: Current
证据 (Controller 实开):
  platform/services/retrieval/planner.py:91
  platform/services/retrieval/orchestrator.py:861
  platform/services/rag/handler.py:486
  platform/services/application/knowledge/query_service.py:155-156
  platform/services/graphrag/community/service.py:41
  platform/services/graphrag/community/models.py:35
  api/services/product/runtime_engine.py:2862  (graph_available=True 硬编码)
现状: 读取路径上是 `or "ready"`。缺配置、缺 health_status、缺字段 → 一律判定为「就绪」。
      写入侧 `mark_ready` 有严格判定；读取侧绕过它。文档声称「平台不存在全局绿灯」。
风险: 未就绪的知识库会被当作就绪使用。这不是崩溃，是**静默地用不可信知识作答**。
      对法律场景，静默错误比报错贵得多。
建议: 读取侧改为 fail-closed —— 缺失即 `unknown`，由调用方显式决定是否降级。
代价 / 退出条件: 会让当前依赖「默认可用」的路径开始报未就绪；
      若实测发现大量路径确实没有 health 数据源，则应先补数据源再收紧，而不是反向放宽。
priority: P0
```

### IMP-020-02 — per-user MCP 配置读取 / 删除缺少归属校验（IDOR）

```text
来源: S04
gap_type: ARCHITECTURE_GAP（Security Authority 不完整）
fact_layer: Current
证据 (Controller 实开):
  api/v1/mcp_user_config.py:51-60   GET  /mcp_user_config/{config_id} → 只传 config_id
  api/v1/mcp_user_config.py:82-92   DELETE /mcp_user_config/delete   → 只传 config_id
  api/services/mcp_user_config.py:74, :121
对照: api/v1/mcp_user_config.py:64-79 的 update 路径**是**传 `user_id=login_user.user_id` 的。
现状: 读与删两条路径拿到了 `login_user` 却从不传入 service，仅凭 `config_id` 操作。
该配置承载 per-user MCP 的 APPCODE / API Key。
风险: 任何已登录用户凭 config_id 可读取或删除他人凭据。
建议: 两条路径补 owner 校验（与 update 一致），并加一条回归测试。
代价 / 退出条件: 低。行为收紧，可能影响前端直接凭 id 取配置的用法 —— 需先确认没有这种依赖。
priority: P0
```

### IMP-020-03 — 出站效果工具关闭 TLS 校验且携带凭据

```text
来源: S11
gap_type: IMPLEMENTATION_GAP
fact_layer: Current
证据 (Controller 实开):
  capability/tools/delivery/action.py:44-49
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
  同函数上方: headers = {"Authorization": f"APPCODE {api_key}"}
现状: 一次携带 APPCODE 的出站请求，TLS 证书与主机名都不校验。
风险: 凭据在中间人面前完全暴露；且这是**外部副作用**路径，不是只读查询。
建议: 恢复默认校验。若因目标端证书问题必须放宽，应改为固定指纹 / 固定 CA，而不是全关。
代价 / 退出条件: 若目标端证书确实不可用，会立即失败 —— 这正是应当暴露的信号。
priority: P0
```

---

## B 组 · 只做了一半的实现

### IMP-020-04 — 五张 memory 写入表里四张只写不读

```text
来源: N01（由 Red 的 Q128 翻出，第一轮 Blue 未看到）
gap_type: IMPLEMENTATION_GAP
fact_layer: Current
证据: BLUE_VERIFIED
  memory_use_traces / context_pack_versions / memory_candidates_v2 / memory_snapshots
  四个表名字面量全仓各只出现一次，且均为 INSERT；全仓零个 FROM。
现状: 写入管道建成，读取端没有消费方。
风险: 「可观测 / 可审计」的叙述建立在这四张表上，但没有任何东西在读它们。
      这不是死代码（写侧在跑），是**只进不出的数据**。
建议: 二选一 —— 要么补上消费方（审计 / 回放 / 评测），要么停止写入。
      **不建议保留现状。**
代价 / 退出条件: 补消费方是新增复杂度，需先说明哪个真实 failure 需要它；
      说不出就直接停写。见 IMP-020-10 的减法原则。
priority: P1
```

### IMP-020-05 — 回收侧两个维护入口都没有驱动

```text
来源: S07（第一轮）+ N03（第二轮强化）
gap_type: IMPLEMENTATION_GAP
fact_layer: Current
证据: BLUE_VERIFIED
  escalate_due_reconciliations 与 timeout_due_async_jobs 均无非测试调用方；
  main.py 与 platform/queue/ 中零 scheduler / cron 命中。
现状: 未确认的副作用「会在 15 分钟后升级」这个语义，没有东西去触发它。
风险: 崩溃窗口里的 unknown effect 会永远停在 pending，无人对账。
建议: 接入调度（或明确说明它由外部系统驱动，并补上那份证据）。
代价 / 退出条件: 若生产实际有外部调度，则本条降级为 DOC_GAP，只需补文档。
      **先确认外部是否已有驱动，再动手。**
priority: P1
```

### IMP-020-06 — ADR-0005 与实际运行路径分叉

```text
来源: S05（第一轮）+ A39/A113（候选人独立复现）
gap_type: ARCHITECTURE_GAP（Contract 与 Current 不一致）
fact_layer: Current vs Target
证据: BLUE_VERIFIED + 候选人自述
  docs/decisions/0005-official-langgraph-postgres-checkpointer.md:14-16 要求官方 saver 为唯一基座且不允许自研桥替代
  实际主路径: graph.compile() 不传 checkpointer，走自研 RuntimeGraphCheckpointer
  官方实现存在但无生产 caller: agent/runtime/phase08.py，且有测试反向禁止某个 cutover 文件
现状: 「ADR 要求的」和「主线跑的」是两条路。
风险: 任何依 ADR-0005 做出的推理都会失准。这是本轮唯一一条**契约层**的不一致。
建议: 二选一 —— 要么补一份 superseding ADR 承认自研桥，要么把主线切到官方 saver。
      **不允许维持「ADR 说 A、代码做 B」而不作声。**
代价 / 退出条件: 切官方 saver 会触碰恢复语义（Domain 已提交 / checkpoint 未写的窗口），
      风险高，需要先有 IMP-020-11 的测量。补 superseding ADR 成本低，但不能掩盖分叉本身。
priority: P1
```

---

## C 组 · 可以做减法（本轮「删除优于扩展」的落地）

### IMP-020-07 — 直删清单

```text
来源: Blue Architecture Reflection §6.1
gap_type: NO_ZUNO_CHANGE（删除不改变语义，只去掉没有 owner 的复杂度）
fact_layer: Current
候选删除项（每条都在代码里有定位；§6.3 另附「不建议删」清单防误删）:
  1. agent/runtime/planning/ 整套零 caller 执行器
     （ReplanBarrierExecutor / JoinControlDecisionEngine / ParallelRecoveryPlanner /
       Phase21CrashRecoveryMatrix / DynamicStepWorker / BranchResultFencer）
     —— 删执行器、留契约类（domain 层有引用）
  2. recovery.py 的 RESEND_OUTBOX 执行路径
  3. sqlite_store.py:318 append_plan_version
  4. agent/runtime/phase08.py（见 IMP-020-06，删它需要先决定 ADR 走向）
  5. contracts.py:61 RuntimeLimits.timeout_ms（死字段）
  6. nodes/core.py:488 agent_id="agent_run"（死维度）
  7. capability/tools/delivery/action.py:47-49 两行 TLS 关闭（见 IMP-020-03）
  8. retrieval/fusion.py 的英文 HotpotQA 词典
     （ENTITY_STOPWORDS / BRIDGE_RELATION_CUES / GENEALOGY_RELATION_CUES）
  9. 9 个无来源标注的硬编融合阈值
priority: P1（第 7 项随 IMP-020-03 升 P0）
```

### IMP-020-08 — 收敛成开关（不删）

```text
  1. 四张只写不读的 memory 审计表（见 IMP-020-04）
  2. multi_agent_enabled —— 不再当「能力」讲。
     依据: product/runtime_batch.py:428 明确**拒绝**在产品面开启它（A54 修正后更硬）。
priority: P2
```

---

## D 组 · 表达 / 简历（**明确不得走架构改动**）

### IMP-020-09 — 简历五条的处置

```text
来源: Red Final Evaluation §4
gap_type: SIMULATED_RESUME_GAP
proposed_change: none ← 这一条**不允许**转成任何架构改动
处置: 保留 1 条（第 2 条 GraphRAG 排序回退，附两条硬上限）/ 降级改写 4 条（第 1、3、4、5 条）/ 删除 0 条
理由: 五条核心事实都有 commit 支撑；漂的是**动词强度**，不是事实。
改写方向（只给方向，不代写）:
  第 1 条 —— 「固定路由边界」收缩为「固定 direct route 一侧的准入与参数抽取边界；
            ReAct 回落侧无回归断言」（A200 当场改写的那句）
  第 3 条 —— 保留 5-query smoke 的具体范围，去掉任何可被读成「更准」的措辞
  第 4/5 条 —— 强化动词与机制的对应；`prepare_context()` 今日已非函数（A24）
priority: P0（下一轮 Resume Gate 前必须处理）
```

### IMP-020-10 — 历史真实性层的取证缺口（本轮最重的一条）

```text
来源: A51/A52/A58/A62 + Red Final NOT_ESTABLISHED 判定
gap_type: OWNERSHIP_GAP
fact_layer: Historical · Unknown
证据: 候选人自述 + 根提交 eafeb1c2
  仓库 2161 个 commit 中，人类身份只有 ProfessorZhi / WenHi Huang(=vince) 及自动化。
  用作者字段无法区分「我」与「团队」。
  另一个结构性事实: 根提交 eafeb1c2（2026-04-15）与候选人能自证的第一笔改动同日，
  因此「我加入时系统已存在」这句话在 git 里没有任何证据。
现状: 简历上「我重构了 MCP Tool Calling」这类主张，在本仓库历史里**既不能证实也不能证伪**。
建议: **不制造 Ownership。** 只做两件允许做的事 ——
  (a) 把这条缺口写进 `docs/project/README.md` 的已知边界，让后续任何人不再重复踩；
  (b) 若用户手上有仓库外的证据（会议纪要、Issue、Review、私有分支），走正常 provenance 补录流程。
proposed_change: none（不得新增机制、不得倒推归属）
priority: P0（治理级，不是工程级）
```

---

## E 组 · 流程 / 方法论

### IMP-020-11 — 盲 Red 不得把怀疑写成对系统的断言

```text
来源: 06_workflow_retrospective §2
证据: Q112 —— Red 从「你对 planning 做了 caller 审计、没对 tool_runtime 做」
      外推为「gateway 大概也没接线」。实际 gateway 真接线
      （capability/runtime.py:861；assert_audit_durable_for_effect 在活路径上）。
建议: Red Skill 新增一条 —— 盲 Red 只能把怀疑写成**问题**，不能写成结论。
priority: P0
```

### IMP-020-12 — `source_check` 收紧为「本轮真的打开过的行」

```text
来源: 06_workflow_retrospective §3.2
证据: 第一轮 3 处引用路径缺陷（S02/S03/S08）在第二轮才被自我勘误。
建议: Blue Skill 规则改为 —— 没实开的不写进 source_check；写不出就标 Unknown。
priority: P0
```

### IMP-020-13 — `BLUE_ARCHITECTURE_REFLECTION` 禁止与 Red Final 并行

```text
来源: 06_workflow_retrospective §3.2（Controller 自身调度失误）
证据: 架构审判第 1–8 节在 Red Final 到位前写成，第 9.3 节在它到位后整体重写。
      协议对该阶段的输入明确包含 04_red_evaluation.md，并行违反协议。
建议: Harness 增加阶段依赖约束，禁止并行启动。
priority: P0
```

### IMP-020-14 — 隔离输入改为暂存目录 + 查证行为认证通道

```text
来源: 06_workflow_retrospective §4.2 / §4.3
证据 (a): Red Final 的一次 `ls -la` 回显了两份封存件的文件名与大小（未读内容，已主动披露）。
证据 (b): Red Final 自述无法区分 A113 的「真的去查了记录」与「高水平构造」；
          该次由 Controller 人工核实 provenance 原文后判为通过。
建议:
  (a) 盲角色的允许输入先复制到一个独立暂存目录，只把该目录交给它；
  (b) 为「查证行为」建立独立认证通道（例如要求引用必须附带该行原文片段，
      片段与本轮产物之外的可核来源比对）。
priority: P1
```

### IMP-020-15 — 治理标准不得同时充当答案模板

```text
来源: 06_workflow_retrospective §4.4（本轮最微妙的一条）
证据: A183 —— 候选人承认其「边界」字段的形态被它读过的 interview-acceptance-standard.md 塑造过。
      第一轮 Red 曾把「自曝密度」判为最强真实性信号。
现状: 衡量诚实的标准，同时也是生成诚实外观的模板。指标被优化掉了。
建议:
  (a) 文档层面分离：攻击标准（Red 读）与回答格式（Blue 读）拆成两份，不再共用；
  (b) 建立**测量点轮换**机制 —— 每轮换一个真实性观测量，
      例如从「他认了多少边界」换成「他认的边界里有多少事后被证明是他自己造成的」。
proposed_change: none（这是流程改动，不是 Zuno 架构改动）
priority: P1
```

---

## 汇总

| 组 | 条目 | 最高优先级 |
| --- | --- | --- |
| A 安全 / fail-open | 3 | P0 ×3 |
| B 只做一半 | 3 | P1 ×3 |
| C 减法 | 2 | P1 |
| D 表达 / 简历 | 2 | P0 ×2（`proposed_change: none`） |
| E 流程 / 方法论 | 5 | P0 ×4, P1 ×3 |

**用户决定（2026-10-07）：**

- **A 组三条 P0（IMP-020-01 / 02 / 03）→ `APPROVED_FOR_NEXT_ROUND`。** 三条在下一轮作为最高优先级处理。**本轮不应用**（`NEXT_ROUND_ONLY`）。
- **IMP-020-10 → `APPROVED_APPLIED`。** 已知边界已写入 [`docs/project/README.md`](../../../project/README.md) 的「团队与个人参与的边界」节。这是本轮唯一被应用的一条。
- **下一轮 frozen resume → 采用 [`10_next_resume_candidate.md`](10_next_resume_candidate.md)。**
- **B / C / D（IMP-020-09）/ E 组：** 用户未逐条表态，维持 `NEXT_ROUND_ONLY` 提案状态，留待下一轮 Resume Gate 前处理。

其中 D 组两条（IMP-020-09 / IMP-020-10）**不允许**转为架构改动 —— 这条纪律不因批准而改变；`IMP-020-10` 的应用方式是**写边界**，不是新增机制。

**本轮没有产生任何收益数字，也没有制造任何 Personal Ownership。**
