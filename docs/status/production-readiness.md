# Production Readiness

status: implementation_available_measurement_blocked

鏈枃浠跺彧缁存姢鐘舵€佷簨瀹炴簮锛屼笉鎵挎媴瀹屾暣鐩爣鏋舵瀯璁捐銆傚畬鏁翠骇鍝佷笌杩愯鏋舵瀯浠?`docs/architecture/architecture.md` 涓哄噯銆?

## Current
## Goal01 State Correction

2026-07-20 Goal01 audit reopened PHASE11 from completed to `in_progress`. LocalQueue, SQLite runtime batch, target-blocked OCR/VLM diagnostics, and incomplete Human Review evidence do not prove the original full PHASE11 production default path.

Current phase state: PHASE05 completed; PHASE06 completed; PHASE07 completed; PHASE11 reopened/in_progress; PHASE08 ready because it only depends on PHASE04-PHASE07; PHASE12 仍 planned and waits for PHASE08 completed 与 PHASE11 completed. Do not claim PHASE11 completed, quality proven, full CI passed, or production ready.

Zuno 褰撳墠鍓嶅彴瀹氫綅鏄?Lean Complete Agentic GraphRAG Product锛氭湰鍦颁紭鍏堛€佺煭鏈熷彲闂幆銆佸彲婕旂ず銆佸彲璇勬祴銆佸彲鎭㈠鐨勪紒涓氱煡璇嗗簱 Agent 浜у搧銆?

宸插叿澶囩殑鏈湴瀹炵幇鍩虹嚎鍖呮嫭锛?

- Product & API锛欰gentChat銆亀orkspace銆乲nowledge/file銆乵essage銆乵odel/tool DTO 鍜岄儴鍒?task/event surface銆?
- Product Runtime Batch锛歚ARCH-PRODUCT-001` 鍒?`ARCH-PRODUCT-080` 宸茶揪鍒?`implementation_available`锛岀粺涓€ Web/Desktop/External API Contract銆丳roduct 涓嶆垚涓虹浜?Controller銆丆ommand Journal銆丆ommandReceipt銆佸箓绛夊啿绐併€丳rojection/AuthorizedView/SSE/Cursor銆両nterrupt/Signal/Approval/UNKNOWN Effect銆丷unOutcome銆乁pload/Parse/Index/Searchable銆丄rtifact/Publication/Delivery/Render/Read銆佸叏閾捐矾鎺堟潈銆丄ctionToken銆丼anitization銆丼andbox銆丏esktop typed IPC銆丒xternal API replay protection銆丏elete/Correction/Retention銆丼LO 鍜?Target-to-Current evidence gate 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Product Surface runtime batch 闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE05 鎴栧叏 Program 鍏抽棴銆?
- Input & Knowledge锛氭枃鏈被鏂囨。 ingestion銆乴ocal object store銆乨urable ingestion store銆乧hunk/index銆乺etrieval銆丟raphRAG銆乪vidence-span hardening surface 鍜岀湡瀹?text PDF SourceSpan vertical slice銆?
- Input Runtime Batch锛歚ARCH-ING-001` 鍒?`ARCH-ING-080` 宸茶揪鍒?`implementation_available`锛孲ourceObject 涓嶅彲鍙樹繚瀛樸€佸璞℃彁浜ゆ牎楠屻€丳arseJob 鐢熷懡鍛ㄦ湡銆丳arserWorker succeeded / blocked 璺緞銆丼ourceSpan provenance銆乭andoff envelope銆乹ueue/outbox/reconciler銆佺紦瀛樸€佹牸寮忎繚鐪熴€佸垹闄?receipt銆乴egal hold銆佸閲忋€佸畨鍏?profile銆乀race/API 鍜?Target-to-Current evidence gate 鍧囧彲鏈哄櫒楠岃瘉锛汸HASE11 宸茬敱 Coordinator Closure 鎵瑰噯涓?completed锛屼絾涓嶄唬琛?quality proven 鎴?production ready銆?- Agent Core锛欸eneralAgent single loop銆丮odel Gateway surface銆佺粺涓€ runtime service銆丼trategy / Plan-and-Execute / ReAct step execution銆丷eflection / Replan / Grounded Synthesis 鍜?Memory pre/post commit baseline銆?
- Agent Runtime Batch锛歚ARCH-AGENT-001` 鍒?`ARCH-AGENT-080` 宸茶揪鍒?`implementation_available`锛孲ingle Controller銆丳lan/ReAct/Reflection/Replan/Reflexion 鍒嗗眰銆丷untime State 搴忓垪鍖栨仮澶嶃€丅udget/Deadline銆佺粺涓€鍏ュ彛 Contract銆両nterrupt/Resume銆丷ef-only Graph State銆丷untimeEvent/Trace銆丏AG銆丳lanVersion/GoalVersion銆丼tep/Action/BranchResult銆丒ffect UNKNOWN/Reconcile銆丗inal Gate/Publication/RunOutcome銆丗ailure/Budget/Recovery/ResultValidity/Outbox/Reconciler 鍜屾槑纭椂闂磋涔夊潎鍙満鍣ㄩ獙璇侊紱杩欏彧浠ｈ〃 Agent Core runtime batch 闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE08 鎴栧叏 Program 鍏抽棴銆?
- Model Gateway Runtime Batch锛歚ARCH-MODEL-001` 鍒?`ARCH-MODEL-088` 宸茶揪鍒?`implementation_available`锛岀粺涓€ Gateway 璋冪敤鍏ュ彛銆丷ole/Operation 鍒嗙銆佷笉鍙彉 Binding銆丏ispatch 鍓?Budget Gate銆丆all/Attempt 鐙珛鐘舵€併€佸崟涓€ selected response銆丼tructured Output 鏈湴鏍￠獙銆丷epair 纭畾鎬ц褰曘€丳rovider/Gateway/Product Streaming 鍒嗗眰銆丼tream Chunk 椤哄簭鍘婚噸鏍￠獙銆乀imeout UNKNOWN/Reconcile銆丷etry/Fallback/Repair/Escalation/Replan Proposal 鎺у埗鍔ㄤ綔鍒嗙銆丟ateway 涓嶆縺娲?PlanVersion 鎴栦慨鏀?RunOutcome銆丒mbedding/Rerank/Vision/Transcription/Classification/Judge operation result contract銆丣udge 涓嶄綔涓哄敮涓€璐ㄩ噺璇佹槑銆丆ontext Compression lineage/constraint/conflict/distortion-risk 淇濈暀銆丮emory/Security/Tool 杈撳嚭鍙舰鎴?candidate/proposal銆乁sage/Pricing/Quota/CAS 杈圭晫銆丳rovider Health 绐楀彛璇佹嵁銆丆ircuit key 闅旂銆丆apability degrade/stale/revoke 鐢熷懡鍛ㄦ湡銆丱peration-specific Adapter Conformance 涓?SDK/API/Model Mapping 鍙樺寲閲嶉獙銆佹湭鐭?Provider signal fail-closed銆丟ateway Config Snapshot 鍐呭瀵诲潃銆丆onfig Activation Validation/Replay/Canary/CAS/Rollback gate銆丆all 鍥哄畾 Config Snapshot銆丳rovider/Model 鐢熷懡鍛ㄦ湡銆丒mergency Disable 鍜?Retirement 鍘嗗彶淇濈暀銆丄dmission 灞傜骇瀹归噺銆佺鎴峰叕骞?Reserved Capacity/闃查ゥ楗裤€佹帓闃熻姹?Deadline/Security/Budget/Config 缁戝畾銆丱verload Backpressure/Load Shedding 涓嶇粫杩?Security/Validation/Usage/Audit/Budget gate銆佷笁绫?Cache 鍒嗙銆丷esult Cache 榛樿鍏抽棴涓旀寜绉熸埛鍜岀増鏈殧绂汇€丆ache Hit Reuse Receipt銆丷evocation/Deletion/Model Retirement/Validity 鍙樺寲澶辨晥 Cache銆佺増鏈寲 Operational Command銆侀珮椋庨櫓 Command Authorization/Approval/Expected Generation/Audit銆佺嫭绔?Retention Binding銆乀ombstone/Visibility Revocation/Physical Cleanup/Verification 鍒犻櫎椤哄簭銆丩egal Hold銆丼LI/SLO 缁村害銆丷eadiness 璇佹嵁闂ㄧ銆丄dapter/API/SDK rollout銆丳rovider API Sunset銆丒xperiment gate/assignment銆丼hadow Call/Result銆丷esultValidity 浜嬩欢銆佺ǔ瀹?Failure Code銆丼uggested Control Action銆丏omain Event銆丳rojection/Source Fact銆丱wnership銆乂ersioned Envelope銆丼torage Layering銆丆ompatibility Facade銆丮igration Integrity銆乁nknown quarantine銆丗ault Recovery 鍜?Current Evidence Gate 杈圭晫鍧囧彲鏈哄櫒楠岃瘉锛汸HASE07 宸茬敱 Coordinator Closure 鎵瑰噯涓?completed锛屼絾涓嶄唬琛?quality proven 鎴?production ready銆?- Capability & Tool锛歝apability registry/control plane銆乼ool adapters銆丮CP/tool surfaces銆乤pproval/resume/idempotency trace baseline銆?
- Capability Runtime Batch锛歚ARCH-CAP-001` 鍒?`ARCH-CAP-080` 宸茶揪鍒?`implementation_available`锛孋apability/Skill/Tool/Provider taxonomy銆佹ā鍨?proposal-only銆丆rossModuleEnvelope銆乽nknown fail-closed/quarantine銆丼killVersion immutability銆乨iscovery/load/resource/policy/supply-chain/revocation銆丆apabilityDefinition/Version/Binding/Conformance/FailureDomain/ConnectorPack銆丄vailability Snapshot/Entry銆丼election/Fallback銆乪xact version pinning銆乮nventory revalidation銆乺esult validity/reuse銆乻ecurity constraint/trust/audit ownership銆乨omain/object/projection persistence boundary銆乼ransaction/outbox/CAS/recovery/fencing銆乬eneric adapter families銆乻tructured manifest銆乨raft-only discovery銆乧ustom extension銆乁NKNOWN side-effect retry boundary銆乻tructured trace/event 鍜?Current Evidence Gate 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Capability / Skill 妯″潡鏈壒闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE14 鎴栧叏 Program 鍏抽棴銆?
- Tool Runtime Batch锛歚ARCH-TOOL-001` 鍒?`ARCH-TOOL-080` 宸茶揪鍒?`implementation_available`锛孴oolDefinition ownership銆丳lanner projection boundary銆丟ateway execution path銆乮mmutable ToolVersion銆両nstallation/Activation split銆丒xposure/Execute split銆丄ctionProposal producer guard銆丳reparedToolAction aggregate銆乧anonical hash銆乀argetResourceSet銆丒ffectProfile銆乻ecret-free prepared action銆乤pproval/security/audit/claim/dispatch ordering銆丄ttempt/Receipt/Effect/Reconciliation/Compensation/Cancellation 鐘舵€佹満銆乷utput firewall銆丆LI/OpenAPI/SDK/MCP/Browser/Async adapter governance銆乺esource conflict銆乺eplan barrier銆乼imeout/deadline銆乫ailure namespace銆乷utbox/domain fact transaction銆乻ecret lease銆乻andbox fail-closed銆乧apacity gate ordering銆乧anary/drain/retired history/ObjectRef/legal hold/SLO/allowlist/readiness evidence 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Tool Runtime 妯″潡鏈壒闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE15 鎴栧叏 Program 鍏抽棴銆?
- Security Runtime Batch锛歚ARCH-SEC-001` 鍒?`ARCH-SEC-060` 宸茶揪鍒?`implementation_available`锛孭rincipal/WorkloadIdentity銆乼enant/workspace isolation銆丱rgUnit/Membership/DelegatedAdminScope銆乁I permission mapping銆丄ctionSet銆乪xplicit deny/default deny銆丟rant lineage/revocation銆丄gent/Task/Session grant intersection銆丳olicyVersion/PAP/PDP/PEP/PIP/simulation/shadow銆丄uthorizationDecision/explanation/Epoch銆乮nput/output detection銆乧lassification/redaction/information flow/declassification/action intent銆丮emory/Multimodal/Knowledge/Citation/Model gates銆丳reparedToolAction hash銆丄pproval replay protection銆乪xecute-time epoch review銆乁NKNOWN Effect reconciliation銆丮CP audience/token/On-Behalf-Of/CredentialVersionRef銆丼ecretLease銆丼andbox/Network/SSRF銆丼upplyChain/Break-glass/Incident銆佸畨鍏ㄤ簨瀹?outbox/audit/recovery/storage/checkpoint/product projection/eval/release/readiness evidence 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Security 妯″潡鏈壒闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE05 鎴栧叏 Program 鍏抽棴銆?
- Memory Runtime Batch锛歚ARCH-MEM-001` 鍒?`ARCH-MEM-060` 宸茶揪鍒?`implementation_available`锛學orking/Session/Long-term lifecycle銆丒pisodic/Semantic/Procedural taxonomy銆乸rojection boundary銆丆ontextPackVersion immutable read view銆丼ession Summary/raw split銆丆andidate/Governance銆丮emoryVersion/source trace銆乺etrieval scope/ACL/security ordering銆乧ompression/fidelity/tool payload/protected set/budget/token validation銆乺ehydration銆丷eflexion/Procedural promotion銆乧onsolidation/freshness/conflict/state machines銆乸rojection publication/index receipt銆乮dempotent commit/checkpoint/CAS/UNKNOWN reconcile銆乸rivacy delete/legal hold銆佸畨鍏ㄨ竟鐣屻€乵odel proposal銆乵odel routing/upgrade銆乼race/outcome/eval銆丳ostgreSQL/ObjectRef/rebuildable projection/CrossModuleEnvelope/readiness evidence 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Memory 妯″潡鏈壒闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE13 鎴栧叏 Program 鍏抽棴銆?
- Knowledge Runtime Batch锛歚ARCH-KNOW-001` 鍒?`ARCH-KNOW-030` 宸茶揪鍒?`implementation_available`锛孉gent Core retrieval decision boundary銆丒videnceRequirement銆乻napshot/security/budget pinning銆並nowledgeVersion acceptance銆乫ixed retrieval graph銆乨ynamic RetrievalPlan/RetrievalRound銆佸 retriever idempotent reducer銆乺esult validation銆乫usion/RRF/rerank/model slot銆乬raph SourceSpan backlink銆丒videnceLedger/Frontier銆乤uthority/temporal/conflict/citation eligibility銆乧orrective retrieval銆乺etry/correct/replan separation銆乻top/budget/cancellation/recovery/version lifecycle銆乨eletion propagation銆乼yped event銆乪val comparability銆乹uality release gate 鍜?config separation 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Knowledge 妯″潡鏈壒闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE12 鎴栧叏 Program 鍏抽棴銆?
- XMOD Runtime Batch锛歚ARCH-XMOD-001` 鍒?`ARCH-XMOD-010` 宸茶揪鍒?`implementation_available`锛屽叡浜?Contract 鍞竴 Owner銆丳roducer/Consumer/Storage/Failure Owner 瑕嗙洊銆丒ffective Epoch/Generation/Deadline銆丷eceipt 涓嶅啋鍏呴鍩熸垚鍔熴€丳reparedAction 鍥涙柟鎷嗗垎銆丮andatory Audit Backpressure銆両ndex Publish/Visibility 鍗忚銆乂ersion/Enum compatibility銆丗ailure Prefix 鍘婚噸鍜?ADR/merge audit evidence 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Wave 1 Cross-module Contract 娌荤悊鎵规鏀跺彛锛屼笉浠ｈ〃 PHASE03 鎴栧叏 Program 鍏抽棴銆?
- Governance & Observability锛歭ocal trace/eval helpers銆丒nterpriseRAG paired eval runner銆乫ailure bucket diagnostics銆乸rofile completeness diagnostics 鍜?release gate output surface銆?
- Observability Runtime Batch锛歚ARCH-OBS-001` 鍒?`ARCH-OBS-024`銆乣ARCH-OBS-RAG-001` 鍒?`ARCH-OBS-RAG-020` 宸茶揪鍒?`implementation_available`锛孴race Context/Tree銆丒nvelope Versioning銆丏edup銆丱rdering銆丩ifecycle銆丄gent/Model/Retrieval/Tool Trace銆丼ecurity Redaction銆両mmutable Audit銆丼ampling銆丒xternal Sink銆丷etention/Legal Hold銆丒val Dataset/Case銆丒val Recovery銆丣udge Policy銆丗ailure Bucket銆丅enchmark Comparability銆丳rofile Completeness銆丷elease Gate銆丮easurement Status銆丒vidence Registry銆丳rojection Rebuild銆丵uality Proven銆丷AG Core Five銆丷oute/Graph/Source/Fusion/Rerank/Agentic Loop Trace銆丒valuation Slice銆丄gent Efficiency銆丵uality-constrained Efficiency銆丆ost/Latency Attribution銆丆ore Five Release Gate 鍜?Reproducible Evidence 鍧囧彲鏈哄櫒楠岃瘉锛涜繖鍙唬琛?Observability / Eval 妯″潡鏈壒闇€姹傛敹鍙ｏ紝涓嶄唬琛?PHASE06 鎴栧叏 Program 鍏抽棴銆?- PHASE05 completed锛歋ecurity Control Plane 鍦ㄥ畬鏁?Phase Scope 鍐呰揪鍒?`implementation_available`锛孋losure Decision 瑙?`docs/evidence/phase05-coordinator-closure.md`锛涜繖涓嶄唬琛?production ready銆?- PHASE06 completed锛歄bservability Minimum Black Box 鍦ㄥ畬鏁?Phase Scope 鍐呰揪鍒?`implementation_available`锛孋losure Decision 瑙?`docs/evidence/phase06-coordinator-closure.md`锛涜繖涓嶄唬琛?PHASE20 Eval/Release Gate銆乹uality proven 鎴?production ready銆?- Local Infrastructure锛歋QLite/SQLModel銆乴ocal object store銆乧onfig銆乨atabase/storage surfaces銆?
- PHASE04 P04-T04锛歅ostgreSQL Idempotency Claim Service 宸茶揪鍒?`implementation available`锛屽寘鍚?tenant-scoped canonical hash銆乷wner/generation/expiry fencing銆佸苟鍙戝崟璧㈠銆乭eartbeat銆乤bort銆佽繘绋嬮€€鍑哄悗鐨?effect reconciliation 涓?result replay锛涘畠涓嶇瓑浜庨鍩熸垚鍔燂紝涔熶笉浠ｈ〃 PHASE04 宸插叧闂€?
- PHASE04 P04-T05锛歅ostgreSQL Lease/Fencing Worker Coordinator 宸茶揪鍒?`implementation available`锛屼娇鐢ㄦ暟鎹簱鏃堕挓銆乪poch/fencing token銆乭eartbeat銆佹樉寮?handoff 涓庡悓浜嬪姟 fenced commit锛屽苟閫氳繃杩涚▼宕╂簝銆佹殏鍋溿€乧ancel race 鍜?TCP network partition锛涘畠涓嶇瓑浜庨鍩熺粨鏋滄垚鍔燂紝涔熶笉浠ｈ〃 PHASE04 宸插叧闂€?
- PHASE04 P04-T01锛氶粯璁ゆ暟鎹簱璺緞宸茶揪鍒?`implementation available`锛屽簲鐢ㄧ敱鍞竴 `PostgresRuntime` 鎻愪緵 sync/async SQLModel Session Factory锛孌AO 鍐欏叆鐢?Domain UoW 缁熶竴鎻愪氦锛屽苟閫氳繃鐪熷疄 PostgreSQL 鐨勮法 Repository 鍥炴粴銆乼enant 闅旂銆乼imeout銆佸彇娑堛€乨eadlock/serialization retry boundary銆乸ool exhaustion 涓?connection-loss recovery锛涘畠涓嶄唬琛?PHASE04 宸插叧闂€?
- PHASE04 P04-T02锛歅ostgreSQL Schema 杩佺Щ宸茶揪鍒?`implementation available`锛屼娇鐢ㄥ敮涓€ Alembic revision chain 鍜屽喕缁撴樉寮?baseline锛岃鐩?31 寮犻鍩熻〃涓?24 寮犲熀纭€璁炬柦琛ㄧ殑 ownership/drift銆佺┖搴撳線杩斻€佹棦鏈夊簱鎺ョ銆侀噸澶嶈縼绉汇€佽縼绉婚攣銆佸湪绾?index銆佹笎杩涚害鏉熼獙璇併€佹寔涔?backfill 涓?forward-fix锛涘畠涓嶄唬琛ㄩ鍩熸暟鎹凡 cutover锛屼篃涓嶄唬琛?PHASE04 宸插叧闂€?
- PHASE04 P04-T03锛歍ransactional Outbox/Inbox 涓庣湡瀹?RabbitMQ transport 宸茶揪鍒?`implementation available`锛孭roduct 棰嗗煙浜嬪疄涓?Outbox銆両nbox 涓?Memory 棰嗗煙浜嬪疄鍒嗗埆鍚屼簨鍔℃彁浜わ紝瑕嗙洊 confirm銆丄CK/NACK銆乺edelivery銆乨uplicate銆佷笉鍚?hash quarantine銆乷rdering watermark銆乺etry/backoff銆丏LQ/replay銆乥acklog銆乥roker restart 涓?network partition锛決ueue receipt 涓嶇瓑浜庨鍩熸垚鍔燂紝涔熶笉浠ｈ〃 PHASE04 宸插叧闂€?
- PHASE04 P04-T06 MinIO / Official Checkpointer 瀛愯寖鍥达細鐪熷疄 S3-compatible Object Store 宸茶揪鍒?`implementation available`锛岃鐩?staging/multipart/hash/commit/visibility銆丳ostgreSQL Manifest銆乧ommit 鍚庡け鑱斿璐︺€佸彧璇?committed gate銆乨elete/restore銆乤uthorization銆乺etention/legal hold銆乴ifecycle銆乻torage restart 涓庣鏀?quarantine锛涘畼鏂?`langgraph.checkpoint.postgres.PostgresSaver` 宸茬敱 Coordinator Decision 鎵瑰噯骞跺畬鎴愮湡瀹?PostgreSQL setup銆佸浠?put銆乺estart restore銆乼hread isolation銆亀rites銆乨elta channel history銆乨elete cleanup銆乬raph-level interrupt/resume after restart銆佹暣 thread retention cleanup銆乸artial prune/run delete fail-closed銆乮nfra generation 瀵硅处銆乻tale generation reject銆佺湡瀹?`pg_dump`/`pg_restore` 鍚庣敱瀹樻柟 saver 璇诲彇銆乻chema upgrade recovery锛屼互鍙婄粍鍚堟晠闅滃悗 checkpoint/history/delta channel 鎭㈠锛汷bject 鎴?Checkpoint receipt 涓嶇瓑浜庨鍩熸垚鍔燂紝P04-T06 宸插畬鎴愪絾涓嶄唬琛?PHASE04 宸插叧闂€?
- PHASE04 P04-T07 Operator 瀛愯寖鍥达細PostgreSQL/RabbitMQ/MinIO 鐨?health銆乺eadiness銆乧apacity銆乥acklog銆乼race correlation銆乫ailure owner/retry owner/recovery owner 鍜岀粨鏋勫寲 operator snapshot 宸茶揪鍒?`implementation available`锛涜 telemetry 涓嶄骇鐢?Eval verdict锛屼篃涓嶄唬琛ㄨ法棰嗗煙 Projection Replay銆乧ombined-service fault 鎴?PHASE04 宸插叧闂€?
- PHASE04 P04-T07 Capacity Admission 瀛愯寖鍥达細`ARCH-INFRA-031/032/033` 宸茶揪鍒?`implementation available`锛孭ostgreSQL `infra_capacity_admissions` / `infra_capacity_reservations` 鎻愪緵 drain flag銆乬eneration銆乤tomic reservation銆乷wner-fenced release 鍜?capacity exhaustion backpressure锛涘畠涓嶈瘉鏄庢墍鏈?Product銆丄gent銆丮odel 鎴?Tool runtime 宸叉帴鍏ワ紝涔熶笉鍏抽棴 PHASE04銆?
- PHASE04 P04-T07 Mandatory Audit 瀛愯寖鍥达細`ARCH-INFRA-054/055` 宸茶揪鍒?`implementation available`锛孭ostgreSQL `infra_audit_channels` / `infra_mandatory_audit_events` 鎻愪緵 durable audit receipt銆乪ffect 鍓?durable audit gate銆乫ail-closed audit capacity mode锛屼互鍙?effect observed 鍚?capacity 閲婃斁锛涘畠涓嶈瘉鏄庢墍鏈?Tool銆丳roduct銆丄gent銆丮odel 鎴?Security runtime 宸叉帴鍏ワ紝涔熶笉鍏抽棴 PHASE04銆?
- PHASE04 P04-T07 Cutover Snapshot 瀛愯寖鍥达細`ARCH-INFRA-048/049` 宸茶揪鍒?`implementation available`锛孭ostgreSQL `infra_cutover_targets` / `infra_cutover_snapshots` / `infra_active_snapshot_refs` 鎻愪緵 Generation/CAS cutover activation銆乤ctive snapshot reference 鍜?retirement guard锛涘畠涓嶈瘉鏄庡畬鏁?Product recovery cutover銆丳ITR銆丷ecoverySet 鎴?official Checkpointer restore锛屼篃涓嶅叧闂?PHASE04銆?
- PHASE04 P04-T07 Recovery Watermark 瀛愯寖鍥达細`ARCH-INFRA-022/052` 宸茶揪鍒?`implementation available`锛孭ostgreSQL `infra_recovery_watermarks` / `infra_recovery_sets` / `infra_recovery_set_members` 鎻愪緵鏉冨▉涓庢淳鐢熺粍浠?watermark 璁板綍銆丷ecoverySet 瀵归綈妫€鏌ャ€乵ismatch fail-closed 鍜?verification hash锛涘畠涓嶅崟鐙瘉鏄?PITR銆丳roduct Projection Replay 鎴?official Checkpointer restore锛岃繖浜涚敱鍚勮嚜 verifier 璇佹槑锛涘畠涓嶅叧闂?PHASE04銆?
- PHASE04 P04-T07 Secret Rotation / Tenant Hit 瀛愯寖鍥达細`ARCH-INFRA-035/058` 宸茶揪鍒?`implementation available`锛孭ostgreSQL `infra_secret_versions` / `infra_secret_rotation_heads` / `infra_secret_leases` 鎻愪緵 generation-fenced secret version activation銆乴ease receipt 鍜?rollback锛宍infra_cross_tenant_hits` 鎻愪緵璺ㄧ鎴峰懡涓殑 fail-closed/quarantine 鎸佷箙璇佹嵁锛涘畠涓嶈瘉鏄庣敓浜?KMS銆佺湡瀹?secret material custody銆丳ITR 鎴?official Checkpointer restore锛屼篃涓嶅叧闂?PHASE04銆?
- PHASE04 P04-T07 PITR Alignment 瀛愯寖鍥达細`ARCH-INFRA-029` 宸茶揪鍒?`implementation_available`锛宍tools/scripts/verify_phase04_pitr_alignment.py` 浣跨敤涓存椂鐪熷疄 PostgreSQL primary/recovery 瀹瑰櫒銆乄AL archive銆乣pg_basebackup` 鍜?recovery target time锛岃瘉鏄?DB/Object/Checkpoint/Index RecoverySet 鍦?PITR 鍚庝繚鎸佸榻愶紝target time 涔嬪悗鐨?derived index watermark 涓嶄細娣峰叆鎭㈠缁撴灉锛涘畠涓嶈瘉鏄庤法棰嗗煙 Projection Replay銆乧ombined-service fault 鎴?PHASE04 closure銆?
- PHASE04 P04-T07 DR Profile 瀛愯寖鍥达細`docs/governance/infrastructure-dr-profile.yaml` 宸茶揪鍒?`implementation available`锛屾槑纭?PostgreSQL銆丱bject Manifest/MinIO銆丷abbitMQ Outbox/Inbox銆乷fficial Checkpointer銆丳roduct Projection Replay銆丳ITR 鍜?combined-service fault 鐨?RPO/RTO/Owner/Recovery Owner銆侀獙璇佸懡浠ゃ€乪vidence ref 涓?cutover fail-closed policy锛涜法棰嗗煙 Projection Replay 浠嶆槸 Phase-level blocker銆?
- PHASE04 P04-T07 Infrastructure Capability Profile 瀛愯寖鍥达細`InfrastructureCapabilityProfileV1` 鍜?`DataServiceCapabilityV1` 宸茶揪鍒?`implementation available`锛宲rofile frozen銆佹樉寮?versioned銆乧anonical hash 鏍￠獙锛孌eveloper CI 涓?Server Product 鍏辩敤 typed contract锛屽苟澹版槑姣忎釜 Data Service 鐨?config hash銆乻upported/unsupported semantics 鍜?authoritative/rebuildable 杈圭晫锛涘畠涓嶄唬琛?official Checkpointer銆丳ITR銆佸畬鏁?RecoverySet 鎴栦紒涓?index adapter 宸插畬鎴愩€?
- PHASE04 P04-T07 Backup/Service Boundary 瀛愯寖鍥达細`ARCH-INFRA-026/041` 宸茶揪鍒?`implementation available`锛孊ackup Scope/RPO/Encryption/Verify profile 鍜?PostgreSQL/RabbitMQ/Object/Checkpoint typed service boundary 鍧囧彲鏈哄櫒楠岃瘉锛涘畠涓嶈瘉鏄庣敓浜?encrypted backup銆丳ITR銆佸畬鏁?RecoverySet 鎴?official Checkpointer restore銆?
- PHASE04 P04-T07 Checkpoint Boundary / Version 瀛愯寖鍥达細`ARCH-INFRA-021/023` 宸茶揪鍒?`implementation available`锛宍agent_runtime_checkpoints` 涓?`infra_checkpoints` 鐨?owner/receipt 杈圭晫銆乣Checkpoint Commit != Domain Commit`銆佷互鍙?CHECKPOINT adapter/schema unknown version fail-closed 鍧囧彲鏈哄櫒楠岃瘉锛涘畠涓嶈瘉鏄?official LangGraph PostgreSQL Checkpointer runtime 宸插畨瑁呮垨鍙仮澶嶃€?
- PHASE04 P04-T07 Restore/Cutover Completion Gate 瀛愯寖鍥达細`ARCH-INFRA-027/028/053` 宸茶揪鍒?`implementation available`锛宐ackup completed銆乺estore isolated before cutover 鍜?recovery cutover explicit allow 鍧囩敱 fail-closed gate 淇濇姢锛涘畠涓嶈瘉鏄庡畬鏁?Backup/Restore/PITR銆丷ecoverySet 鎴?official Checkpointer restore銆?
- PHASE04 P04-T07 Infrastructure Docs Governance 瀛愯寖鍥达細`ARCH-INFRA-001/002` 宸茶揪鍒?`implementation available`锛孖nfrastructure 鏂囨。鐨?Current/Target/Future/Explicitly Not Selected 鍒嗗眰銆佸敮涓€姝ｅ紡 Target 鏂囨。銆丄gent 闀滃儚銆乤rchitecture canonical 鍥涙枃浠堕泦鍚堜笌 entrypoint verifier 鍧囧彲鏈哄櫒楠岃瘉锛涘畠涓嶈瘉鏄庝换浣?runtime adapter 鎴栨仮澶嶉棴鐜€?
- PHASE04 P04-T07 Infrastructure / Domain Boundary 瀛愯寖鍥达細鍩虹璁炬柦 receipt 杈圭晫宸茶揪鍒?`implementation available`锛孮ueue ACK銆丷abbitMQ delivery銆丱bject Commit銆両dempotency Claim銆丱bject Manifest visibility 鍜?operator telemetry 鍧囪 verifier 鍥哄畾涓轰笉鑳借В閲婃垚棰嗗煙鎴愬姛锛涢鍩熺粓灞€浠嶇敱 Product銆両nput銆並nowledge銆丄gent Core銆丮emory銆乀ool 绛?owner 鎸佹湁銆?
- PHASE04 P04-T07 Reconciler Supervision Boundary 瀛愯寖鍥达細`ARCH-INFRA-039` 宸茶揪鍒?`implementation available`锛孖dempotencyWorkerSupervisor 鐨?owner/generation/expiry fencing銆乺econcile/no-reexecution锛屼互鍙?LeaseWorkerCoordinator 鐨?heartbeat銆佸悓浜嬪姟 fenced commit銆乧rash handoff 鍜?PostgreSQL partition fail-closed 鍧囨湁鏈哄櫒璇佹嵁锛涘畠涓嶈瘉鏄庢墍鏈変骇鍝?Reconciler 宸叉帴鍏ャ€?
- PHASE04 P04-T07 Infrastructure Typed Port 瀛愯寖鍥达細Local/Developer CI 涓?Server Product 宸插叡鐢ㄥ悓涓€ `InfrastructureCapabilityProfileV1` / `DataServiceCapabilityV1` typed port surface锛屽苟瑕嗙洊 PostgreSQL銆丷abbitMQ銆丱bject銆丆heckpoint銆乂ector銆丟raph銆丩exical銆丆ache銆丼ecret 鍜?Telemetry service kind锛泆nknown service kind fail closed锛屼絾 official Checkpointer 绛?target adapter 浠嶆湭瀹屾垚銆?
- PHASE04 P04-T07 Tenant Isolation Profile 瀛愯寖鍥达細`TenantIsolationProfileV1` 宸茶揪鍒?`implementation available`锛孖nfrastructure Capability Profile 涓瘡涓?service kind 閮芥湁 tenant scope銆侀粯璁?target銆佸己闅旂閫夐」銆乧ross-tenant action 鍜?evidence ref锛涜繍琛屾椂 hit gate 鐢?Secret Rotation / Tenant Hit 瀛愯寖鍥磋ˉ璇併€?
- PHASE04 P04-T07 Tenant Physical Constraints 瀛愯寖鍥达細`ARCH-INFRA-034` 宸茶揪鍒?`implementation available`锛孭ostgreSQL銆丷abbitMQ銆丱bject ref/MinIO 鍜?Operator telemetry 鐨勫綋鍓嶈瘉鎹妸 tenant scope 鏀惧叆鐗╃悊閿€佸崗璁?header銆乷bject target/auth hook 鎴?snapshot 绾︽潫锛涘畠涓嶈瘉鏄?official Checkpointer锛岃繍琛屾椂 cross-tenant hit quarantine/fail-closed 鐢?`ARCH-INFRA-058` gate 琛ヨ瘉銆?
- PHASE04 P04-T07 Upgrade Compatibility Profile 瀛愯寖鍥达細`UpgradeCompatibilityProfileV1` 宸茶揪鍒?`implementation available`锛孖nfrastructure Capability Profile 涓瘡涓?service kind 閮芥湁鏄惧紡 adapter/schema version銆乺ead/write/rollback compatible versions銆乽nknown-version fail-closed action 鍜?canonical content hash锛涘畠涓嶈瘉鏄?live rolling upgrade銆乷fficial Checkpointer integration 鎴栧畬鏁?recovery replay銆?
- PHASE04 P04-T07 Adapter Conformance Profile 瀛愯寖鍥达細`AdapterConformanceProfileV1` 宸茶揪鍒?`implementation available`锛孌eveloper CI 涓?Server Product 瀵规瘡涓?service kind 鍏辩敤 conformance suite version銆乻upported/unsupported semantics銆乺equired test refs 鍜?evidence ref锛屽苟瀵?unsupported local semantic fail-fast锛涘畠涓嶈瘉鏄庢墍鏈夋湭鏉?enterprise adapter 宸插疄鐜般€?
- PHASE04 P04-T07 Release Provenance Manifest 瀛愯寖鍥达細`ReleaseManifestV1` 宸茶揪鍒?`implementation available`锛屾湰鍦扮湡瀹?PostgreSQL/RabbitMQ/MinIO 鐨?source commit銆佽繍琛屼腑 image id bundle銆丆ompose network/port refs銆乧onfig hash銆乵igration versions銆乤dapter versions銆乧ompatibility evidence 涓?provenance refs 鍙満鍣ㄩ獙璇侊紱瀹冧笉璇佹槑 production application image release銆佸閮?SBOM/signing銆乷fficial Checkpointer 鎴栧畬鏁?recovery replay銆?
- PHASE04 P04-T07 Redis Optional Boundary 瀛愯寖鍥达細`DataServiceCapabilityV1` 涓?Redis/CACHE boundary 宸茶揪鍒?`implementation available`锛孯edis 鍙綔涓?optional acceleration cache锛岄潪鏉冨▉銆佸彲浠庢潵婧愰噸寤猴紝涓斾笉杩涘叆 PHASE04 required real services 鎴?release adapter provenance锛涘畠涓嶈瘉鏄?Redis HA銆乫ailover銆乺ate-limit acceleration 鎴?enterprise deployment銆?
- PHASE04 P04-T07 Derived Index Boundary 瀛愯寖鍥达細`DataServiceCapabilityV1` 涓?VECTOR/Milvus銆丟RAPH/Neo4j 鍜?LEXICAL/BM25/Search boundary 宸茶揪鍒?`implementation available`锛屼笁鑰呭潎涓?versioned銆乶on-authoritative銆乺ebuildable from source锛屼笖涓嶈繘鍏?PHASE04 required release adapter provenance锛涘畠涓嶈瘉鏄庤繖浜?server adapter銆乿isibility receipt銆乤cceptance gate 鎴?rebuild drill 宸插疄鐜般€?
- PHASE04 P04-T07 Contract Ownership Boundary 瀛愯寖鍥达細`ARCH-INFRA-046/047/056` 宸茶揪鍒?`implementation available`锛孖ndex write/receipt/visibility 涓?Knowledge acceptance 鍒嗗眰銆両ndexManifest/Acceptance 褰掗鍩?Owner銆丳reparedToolAction/ActionProposal/SecurityApproval/AuditPersistence owner 涓嶉噸鍙犲潎鍙満鍣ㄩ獙璇侊紱瀹冧笉璇佹槑 index adapter runtime銆乀ool effect runtime 鎴?audit durable-before-effect runtime 宸插畬鎴愩€?

## Short-term Closure Gap

P0锛?

- Agentic GraphRAG fixed benchmark 璺戦€氬苟杈惧埌 baseline gate銆?
- 鎵€鏈夌湡瀹炴ā鍨嬭皟鐢ㄧ粺涓€杩涘叆 Model Runtime / Gateway銆?
- 缁熶竴 Agent Core 鐪熷疄闂幆锛歋trategy銆丳lan-and-Execute銆丷eAct銆丱bservation銆丷eflection銆丷eplan銆丷eflexion銆丮emory 鍜?Retrieval 杩涘叆鍚屼竴鏉″彲鎵ц銆佸彲鎭㈠銆佸彲娴嬮噺閾捐矾銆?
- Corrective Agentic GraphRAG锛歚RETRIEVE_MORE -> replan -> execute_step` 鐪熷疄鍥炶矾銆丒videnceLedger 鍜?failure bucket corrective action 鍙娴嬨€?
- Agent run trace 鎸佷箙鍖栧苟鍙煡鐪嬨€?

P1锛?

- task / planner / retrieval / approval 鐘舵€佹湰鍦版寔涔呭寲銆?
- 鑷冲皯涓€涓湡瀹?text PDF parser 宸茶窇閫?source span citation锛涙壂鎻?OCR PDF 浠嶈繑鍥?needs_ocr锛屼笉 fake index銆?
- 2-3 涓湡瀹?Tool 瀹屾垚 approval / timeout / trace 闂幆銆?
- Memory ContextPack 鍦ㄧ湡瀹?AgentChat 涓彲瑙傛祴銆?
- Reflexion candidate -> review -> approved -> future ContextPack reuse銆?
- Skill metadata -> instruction -> resource 鐨勬笎杩涘紡鍔犺浇 trace銆?

P2锛?

- 鍓嶇 E2E銆侀」鐩紨绀鸿剼鏈拰鍙鐜板惎鍔ㄦ柟寮忋€?

## Measurement Blocked

Agentic GraphRAG 褰撳墠涓嶈兘鍐欐垚 quality completed銆?

```text
implementation available
measurement blocked
quality not yet proven
```

blocked 鍘熷洜锛?

- PHASE13 sample-8 宸茶繍琛?EnterpriseRAG paired runner锛屼絾鏈湴 profile runner 鍥?embedding model/base_url 鏈厤缃€岃緭鍑?`blocked_not_measured`锛宍measured_case_count=0`銆?
- PHASE13 sample-80 浠嶅洜浠撳簱娌℃湁 tracked fixed 80-case set 鑰?blocked銆?
- release gate 鐜板湪鍙湪 `standard_rag`銆乣deep_graphrag` 鍜?`agentic_graphrag` 閮藉畬鎴愬悓涓€ fixed case set 鏃跺啓 `fixed_benchmark`锛沺rofile 涓嶅畬鏁存椂杈撳嚭 `profile_completeness.blocked_reason`銆?

璇佹嵁鍏ュ彛锛?

- `docs/evidence/unified-agent-runtime-phase13-release-gate.md`
- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/closure-summary.md`

蹇呴』淇濈暀鐨勮川閲忛棬锛?

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 涓嶅緱鎭跺寲
```

blocked銆乸repared銆乺untime observed 鍜?measured 蹇呴』涓ユ牸鍖哄垎銆傜己 trace 瀛楁鏃惰緭鍑?`unavailable_due_to_missing_trace_fields`锛屼笉寰楃紪閫?failure bucket銆?

## Completed

杩戞湡鍙綔涓?completed 鐨勫唴瀹瑰彧闄愬凡缁忕敱浠ｇ爜銆佹祴璇曘€乼race/eval 鎴?verifier 鏀拺鐨勬湰鍦板疄鐜板熀绾垮拰鏂囨。/guardrail 鏀跺彛銆?

鍘嗗彶 program 瀹屾垚浜嬪疄淇濈暀鍦細

- `docs/history/programs/README.md`

鍘嗗彶瀹屾垚涓嶇瓑浜庡綋鍓?quality gate 宸查€氳繃銆?

## Future Optional

浠ヤ笅鍐呭鏄彲閫夋湭鏉ユ墿灞曪紝涓嶆槸鐭湡 blocker锛?

- Redis 楂樼骇缂撳瓨銆並afka銆並ubernetes銆丼ervice Mesh 鍜屽鍖哄煙閮ㄧ讲銆?
- Managed PostgreSQL / Managed Queue / Managed Object Store 鏄儴缃插舰鎬侀€夋嫨锛屼笉鏄綋鍓嶆湰鍦板疄鐜板畬鎴愯瘉鎹€?
- 澶栭儴 Milvus / Neo4j 闆嗙兢鍜屽垎甯冨紡 graph/vector index 鐨勪紒涓氱骇閮ㄧ讲銆?
- 澶嶆潅 SSO / DLP / Vault銆丗irecracker銆?
- 澶ц妯″湪绾胯瘎娴嬪钩鍙板拰浼佷笟杩愮淮闂ㄦ埛銆?
- 澶ч噺 parser/provider 骞惰鎺ュ叆銆丱CR/VLM enrichment 骞冲彴鍖栥€?
- Single Controller 涓嬪 Agent Role 鍗忎綔鏄湭鏉ュ彲鍏煎鏂瑰悜锛涗骇鍝佺骇鑷不 Multi-Agent runtime 浠嶆槸鏇撮暱鏈?Future Optional銆?

PHASE04 completed锛歅ostgreSQL銆丷abbitMQ銆丮inIO / S3-compatible Object Store 鍜屽畼鏂?LangGraph PostgreSQL Checkpointer 鐨?canonical integration / graph interrupt-resume / retention-cleanup / backup-restore / schema-upgrade / Generic Replay Framework / combined-service fault 瀛愯寖鍥村凡鏈夌湡瀹炴湰鍦?Docker 璇佹嵁骞惰揪鍒?`implementation available`锛汼QLite銆佹湰鍦板璞″瓨鍌ㄥ拰鏈湴闃熷垪浠嶅彧浣滀负 Developer/CI adapter 淇濈暀銆侾HASE05 completed锛孭HASE06 completed锛孭HASE07 completed锛孭HASE11 completed锛汸HASE08 ready锛孭HASE12 浠?planned锛汸HASE09鈥?2 涓嶅緱鎻愬墠鍐掑厖 Current銆?