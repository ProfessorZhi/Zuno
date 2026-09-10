# Transcript — rb-2026-09-10-architecture-part-a-007

Mode: `CHATGPT_AUTO`  
Zuno base: `a13ff27c9c4291ea70d81c41520917d2b75bcd86`  
Resume anchor: `ProfessorZhi/internship-work@6107321bdcaced8688c0e462d8b0a85b2744c4fe:resume/00_resume_versions/Zuno_v3+CodingAgent+SFTDPO_简历/Agent开发工程师／AI应用工程师+Zuno／CodingAgent／SFTDPO_ToolCalling层次澄清／可追问_简历草稿_v5.md`  
Target: Agent 开发工程师 / AI 应用工程师 — system-design / architecture walkthrough  
Blue profile: `canonical-part-a-first`

本轮只压力测试当前 Human Part A 的架构叙事。简历快照用于固定候选上下文，不重新评审简历 wording。

## Turn 1 — Generic Host 已经很强，Zuno 还剩什么

**Scenario / claim:** simple baseline and replaceability  
**Attack angle:** Build / Buy / simplification

**Red question**

如果 Dify、LangGraph 或一个普通 Agent Host 已经能提供会话、Workflow、RAG、Tool Calling、Checkpoint 和模型调用，为什么还需要 Zuno？如果回答只是“法律场景更复杂”，这仍然不足以证明要有自己的 Runtime、Domain 和九个责任域。请从一条最简单任务开始，说明什么时候应该直接复用通用平台，什么时候才增加 Zuno 的责任。

**Red hidden intent**

验证文档是否尊重简单 baseline，是否把 framework capability 与 Zuno business authority 分开，以及 Native Runtime 是否有退出条件。

**Expected evidence**

Project / Architecture / Runtime Part A；必要时 Decisions / Evidence 用于 Current / Target 边界。

**Blue answer**

“合同第 8 条写了什么”可以继续使用普通应用服务、受控 RAG 和成熟模型 SDK；拥有 Runtime、GraphRAG 或 Formal Admission 并不要求所有请求经过这些机制。复杂度从任务跨越材料准备、人工复核、长期正式结果、恢复或现实副作用以后才出现。通用 Host 可以继续拥有 UI、会话、通用编排和 Checkpoint；Zuno 只保留平台不能替法律业务决定的长期语义，例如当前任务材料是否足够、机器结果何时进入正式业务、正式结果在新证据后是否仍有效、外部动作是否真的发生，以及下一次受保护动作是否仍被允许。Runtime 本身也有退出条件：Generic Host + Legal Backend 如果能满足长期状态、恢复正确性和控制可解释性，自研 Runtime 应保持很薄甚至退出主路径。

**Blue source trace**

- `docs/project/README.md` — “通用平台之后仍然留下的法律责任”
- `docs/architecture/architecture.md` — “从普通法律问答开始”与责任边界收缩
- `docs/modules/runtime/README.md` — “当成熟框架已经够用时，Runtime 应该尽量薄”

**Verifier result:** PASS. 回答区分了 baseline、平台复用、Zuno authority 和删除条件，没有把 Target 写成 Current。  
**Finding type:** NONE  
**Next action:** next scenario

## Turn 2 — 98/100 材料与否定性结论

**Scenario / claim:** Knowledge readiness / evidence coverage  
**Attack angle:** epistemic completeness

**Red question**

100 份材料里 98 份已经处理，两份扫描件还没 OCR。用户问的不是“合同第 8 条是什么”，而是“全部材料里是不是从来没有约定提前到期？”你甚至不知道缺失两份里写了什么，Readiness 怎么可能判断它们是否影响问题？如果系统只是因为已处理材料里没搜到就回答“没有”，Knowledge 边界仍然不成立。

**Red hidden intent**

攻击“task-specific readiness”是否被误写成模型能够预知缺失内容；验证 retrieval miss 与 negative fact 是否分离。

**Expected evidence**

Knowledge Part A 的 readiness、retrieval miss、negative claim 边界。

**Blue answer**

Readiness 不需要假装知道未处理材料的内容。对要求覆盖“全部材料”的否定性问题，只要要求范围中仍有关键材料未进入可查询状态，系统就没有资格把当前 retrieval miss 升级成“事实不存在”。它可以表达“当前已处理范围未发现”，或者阻断完整结论并暴露缺失范围。只有问题明确缩小到已经准备好的材料，或者任务要求的覆盖条件得到满足，才可以继续形成相应范围内的判断。Knowledge 负责说明覆盖和检索缺口，正式法律判断仍由 Domain 接纳。

**Blue source trace**

- `docs/modules/knowledge/README.md` — “一百份材料上传成功，任务仍可能不能开始”
- `docs/modules/knowledge/README.md` — “检索负责找到候选，不负责把‘没找到’写成事实”

**Verifier result:** PASS. 回答没有声称系统能预知缺失材料，明确使用 covered scope / incomplete coverage。  
**Finding type:** NONE  
**Next action:** next scenario

## Turn 3 — Domain 已提交，Runtime 只剩旧 Checkpoint

**Scenario / claim:** crash recovery authority  
**Attack angle:** duplicate formal admission

**Red question**

Domain transaction 已经成功，Runtime 在下一份 Checkpoint 之前崩溃。重启后只有旧 Checkpoint。为什么不能直接按 Checkpoint 重放？如果 Domain 查询暂时不可用，你是继续执行、回滚，还是等待？谁有资格宣布这次正式业务提交发生过？

**Red hidden intent**

验证恢复 authority 是否真正落在 Domain durable fact，而不是把 Checkpoint、Queue 或 Controller 状态升级成业务真相。

**Expected evidence**

Domain / Runtime Part A；被追到精确恢复条件时可进入 Engineering Reference。

**Blue answer**

旧 Checkpoint 只能证明 Runtime 上次记录到哪里，不能证明正式业务提交没有发生。恢复先查询 Domain 的耐久记录和对应正式提交证明；已存在就修 Runtime projection，不重复提交，不存在才按当前版本和条件重新进入提交路径。Domain 查询暂时不可用时，Runtime 没有更强事实支持再次写正式结果，应等待/重试 owner query 或进入受控阻塞，而不是把“查不到”解释成“没发生”。正式业务是否成立由 Domain 的耐久事实证明。

**Blue source trace**

- `docs/modules/domain/README.md` — “一次成功提交必须在调用方崩溃后仍然能够被证明”
- `docs/modules/runtime/README.md` — “Domain 已经提交而 Checkpoint 还没写时，恢复必须先相信业务事实”
- `docs/architecture/reference.md` — Domain commit / matching AdmissionReceipt recovery rule

**Verifier result:** PASS. Owner-first recovery 闭环，未把基础设施 availability 误当业务不存在。  
**Finding type:** NONE  
**Next action:** next scenario

## Turn 4 — POST timeout，而且远端没有可靠查询能力

**Scenario / claim:** external effect unknown  
**Attack angle:** blind retry / exactly-once claim

**Red question**

你向外围法院系统 POST，一发送就 timeout。更糟的是对方既没有可靠 idempotency key，也没有查询接口。你怎么恢复？如果回答“重试三次”，会重复提交；如果回答“标失败”，也可能撒谎。Zuno 到底承诺什么？

**Red hidden intent**

验证 Outcome Unknown 是否是正式可保留状态，以及系统是否诚实承认自动化上限。

**Expected evidence**

Effects Part A。

**Blue answer**

越过 send boundary 后，本地 timeout 不能证明远端失败。系统保留 Outcome Unknown，不自动重做同类副作用。优先用远端幂等键、业务唯一键、查询 API、回执或 correlation 对账；这些机器能力都不存在时，自动化上限就是人工确认。长期无法确认可以保持 unresolved 并升级人工，而不是为了让状态机结束猜成成功或失败。Zuno 不承诺跨外部系统绝对 exactly-once；它承诺稳定逻辑动作身份、减少本地重复，并在未知时通过 Reconcile 收敛或显式停在未知。

**Blue source trace**

- `docs/modules/effects/README.md` — “结果未知是一种需要保留的事实”
- `docs/modules/effects/README.md` — exactly-once 边界与人工对账

**Verifier result:** PASS. 文档明确给出了不可自动恢复时的停止条件。  
**Finding type:** NONE  
**Next action:** next scenario

## Turn 5 — 10:00 有权限，10:20 已经撤权

**Scenario / claim:** continuous authorization  
**Attack angle:** stale authorization / already-sent data

**Red question**

任务 10:00 合法启动，10:12 权限撤销，10:20 Worker 准备再次读取正文并调用外部模型。如果模型请求在撤权前已经发出，撤权还能做什么？如果请求还没发，谁重新检查？不要用“持续鉴权”四个字代替执行边界。

**Red hidden intent**

验证授权是否绑定新风险动作，并区分控制未来与改写历史。

**Expected evidence**

Security Part A，必要时 Model Gateway / Effects。

**Blue answer**

持续授权发生在新的受保护动作边界，而不是每毫秒轮询。10:20 的重新读取、模型外发、Secret 获取或高风险 Tool 调用必须消费当前安全决定；真正读取的 Knowledge、真正外发的 Model Gateway、真正发送 Effect 的 Effects 在各自 I/O 点执行门。撤权前已经合法发出的数据不会被“撤回历史”；后续返回的模型结果能否继续使用、发布或正式接纳，要重新检查当前条件。权限撤销控制未来使用，不提供时间倒流。

**Blue source trace**

- `docs/modules/security/README.md` — “授权发生在真正产生新风险的边界”
- `docs/modules/security/README.md` — “安全失去新鲜度时，高风险动作宁可停下来”

**Verifier result:** PASS. Decision / enforcement / historical fact 三层关系清楚。  
**Finding type:** NONE  
**Next action:** next scenario

## Turn 6 — 九个责任域真的是从故事里长出来的吗

**Scenario / claim:** architecture narrative causality  
**Attack angle:** responsibility derivation / reader mental model

**Red question**

你说九个责任域不是先验模块表，而是同一案件里的冲突自然逼出来的。那我不看模块表，只听前面的 Architecture 故事：为什么 Application & Integration 必须作为一类独立责任存在？Knowledge、Domain、Runtime、Model Gateway、Effects、Security、Evaluation 我都能指出对应失败，但 Application 到底保护了什么失败？

**Red hidden intent**

验证总体 Architecture 是否真的在归纳前完整推导全部九类责任，而不是只把部分模块场景化后仍在表格里补剩余 taxonomy。

**Expected evidence**

Architecture Part A；Application Part A 仅用于判断缺口是否已有下钻解释。

**Blue answer**

Application 模块正文能够回答：一次任务会先受理、随后计算结束、之后正式 WorkProduct 才成立，再经历发布、交付和新证据导致的 stale；一个 `status=success` 无法代表这些不同时间线。Application 组合各 Owner 已经成立的事实，为外部 Host 提供稳定的任务、发布、交付和失效传播语义，但不拥有 Knowledge、Domain、Security 或 Effect truth。

不过，总体 `architecture.md` 在九责任域表出现以前没有把这条产品生命周期作为一个独立失败场景完整走出来。它从普通应用服务开始，也提到成果可能已经交付，但没有像 Knowledge 的 98/100、Runtime 的 crash、Effects 的 timeout 那样明确展示“accepted / draft / formal / delivered / stale 被一个全局 success 混淆”的失败。因此读者只读总体 Architecture 时，01 的存在理由弱于其余责任域，需要跳到 01 模块正文才能补齐。

**Blue source trace**

- `docs/architecture/architecture.md` — running case before “这些反复出现的冲突才形成九个责任域”
- `docs/modules/application/README.md` — “同一个‘完成’会在一项任务里发生好几次”

**Verifier result:** FINDING. 这不是 Authority 或 decomposition 缺失；01 的精确职责已经存在，缺的是总体 Architecture 对该职责的场景推导。修复会改变第一次阅读的因果完整性，但不改变 Architecture Truth。  
**Finding type:** NARRATIVE_GAP  
**Next action:** close round; create independent bounded Architecture Part A repair and retest with a different product-lifecycle scenario.
