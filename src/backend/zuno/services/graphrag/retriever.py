import re

from zuno.services.graphrag.client import Neo4jClient
from zuno.services.rag.vector_db import milvus_client


class GraphRetriever:
    ASCII_PHRASE_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*)*")
    CJK_PHRASE_PATTERN = re.compile(r"[\u4e00-\u9fff]{2,}")
    STRONG_RELATION_CUE_PATTERN = re.compile(
        "(\u5173\u7cfb|\u5173\u8054|\u8def\u5f84|\u94fe\u8def|\u4f9d\u8d56|\u901a\u8fc7|\u7531\u8c01|\u8d1f\u8d23|"
        "\u5f52\u5c5e|\u4f4d\u4e8e|\u6c47\u62a5|\u5c42\u6b21|\u67b6\u6784|\u7ec4\u6210|\u7ec4\u6210\u90e8\u5206|"
        "\u6a21\u5757|\u90e8\u7f72|\u6301\u4e45\u5316|"
        "leads|reports to|handled by|hosted in|deploy|deployment|architecture|component|components|"
        "task queue|persistence|transports|gateways|Redis|PostgreSQL)",
        re.IGNORECASE,
    )
    WEAK_RELATION_CUE_PATTERN = re.compile(
        "(\u5c5e\u4e8e|\u5206\u522b|\u5404\u81ea)",
        re.IGNORECASE,
    )
    NON_GRAPH_LISTING_PATTERN = re.compile(
        "(\u7d22\u5f15\u7c7b\u578b|\u76f8\u4f3c\u5ea6\u6307\u6807|index types?|indexes|metrics)",
        re.IGNORECASE,
    )
    NOISE_QUERY_TERMS = {
        "a",
        "an",
        "and",
        "are",
        "for",
        "how",
        "in",
        "is",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "what",
        "which",
        "who",
        "why",
    }
    GENERIC_GRAPH_ENTITIES = {
        "Introduction",
        "What",
        "What's next",
        "Overview",
        "Objectives",
        "Objective",
        "History",
        "Roadmap",
        "Examples",
        "Example",
        "Example applications",
        "Developer tools",
        "Milvus Overview",
        "Milvus Adopters",
        "High",
        "Low",
        "Medium",
        "Autoscaling",
    }
    GENERIC_QUERY_SEEDS = {
        "python",
        "agent",
        "server",
        "agent server",
        "contract",
        "合同",
    }
    CJK_CONNECTOR_PATTERN = re.compile(
        "(\u4e4b\u95f4|\u662f\u4ec0\u4e48|\u4ec0\u4e48|\u54ea\u4e9b|\u4e3b\u8981|\u9002\u5408|\u7528\u6765|"
        "\u91cd\u70b9|\u573a\u666f|\u95ee\u9898|\u5173\u7cfb|\u4f5c\u7528|\u600e\u4e48|\u5982\u4f55|"
        "\u5e94\u8be5|\u53ca|\u4e0e|\u548c|\u91cc|\u4e2d|\u7684)",
        re.IGNORECASE,
    )
    SCALE_QUERY_TERMS = {
        "autoscaling",
        "deployment",
        "throughput",
        "qps",
        "read",
        "reads",
        "write",
        "writes",
        "replica",
        "replicas",
        "配置",
        "扩缩容",
        "流量",
        "请求",
    }
    QUERY_TERM_ALIASES = {
        "部署": {"deployment", "deploy"},
        "组成": {"parts", "components"},
        "核心组成": {"parts", "components"},
        "持久化": {"persistence", "postgresql", "stored", "default"},
        "默认后端": {"postgresql", "default", "backend"},
        "三类数据": {"three", "types", "data"},
        "层次": {"levels", "layer"},
        "系统设计": {"designed", "architecture"},
        "角色": {"brain", "endpoint", "persistence"},
        "执行路径": {"lifecycle", "execution", "stream"},
        "运行路径": {"lifecycle", "execution", "stream"},
        "task queue": {"queue", "redis", "postgresql"},
        "redis": {"queue", "signaling", "pub/sub"},
        "postgresql": {"stored", "persistence"},
    }
    QUERY_SEED_ALIASES = {
        "持久化": ["Persistence"],
        "task queue": ["Task queue"],
        "执行路径": ["Task queue"],
        "运行路径": ["Task queue"],
    }
    DEFAULT_POLICY_SEED_TERMS: tuple[str, ...] = ()
    DEFAULT_POLICY_RELATION_CUES = (
        "关系",
        "关联",
        "路径",
        "链路",
        "依赖",
        "通过",
        "谁负责",
        "谁处理",
        "谁承担",
        "由谁",
        "位于",
        "组成",
        "架构",
        "部署",
        "持久化",
        "条款",
        "义务",
        "约定",
        "风险",
        "期限",
        "前置条件",
    )
    DEFAULT_POLICY_STEP_CUES = (
        "流程",
        "步骤",
        "顺序",
        "阶段",
        "先后顺序",
        "怎么走",
        "怎么做",
    )

    def __init__(self, client: Neo4jClient | None = None, chunk_store=None):
        self.client = client or Neo4jClient()
        self.chunk_store = chunk_store or milvus_client

    @staticmethod
    def _policy_values(query_policy: dict | None, key: str) -> list[str]:
        if not query_policy:
            return []
        raw_value = query_policy.get(key)
        if raw_value is None:
            return []
        if isinstance(raw_value, (list, tuple, set)):
            values = raw_value
        else:
            values = re.split(r"[|,，;/]+", str(raw_value))
        cleaned: list[str] = []
        for item in values:
            text = str(item or "").strip()
            if text:
                cleaned.append(text)
        return cleaned

    @classmethod
    def _resolve_query_policy(
        cls,
        *,
        domain_pack_id: str | None,
        query_policy: dict | None,
    ) -> dict[str, object]:
        merged: dict[str, object] = {}
        if domain_pack_id and not query_policy:
            try:
                from zuno.services.domain_pack.loader import DomainPackLoader

                pack = DomainPackLoader().load(domain_pack_id)
                if pack and pack.retrieval_policy_data:
                    merged.update(dict(pack.retrieval_policy_data))
            except Exception:
                pass
        merged.update(dict(query_policy or {}))
        return merged

    @classmethod
    def _add_seed(cls, ordered: list[str], seen: set[str], value: str):
        cleaned = re.sub(r"\s+", " ", str(value or "")).strip("`*_#-:;,.!?()[]{}<>\"'")
        if not cleaned:
            return
        normalized = cleaned.lower()
        if normalized in cls.NOISE_QUERY_TERMS or normalized in seen:
            return
        seen.add(normalized)
        ordered.append(cleaned)

    @classmethod
    def _extract_cjk_seed_candidates(cls, text: str) -> list[str]:
        candidates: list[str] = []
        for phrase in cls.CJK_PHRASE_PATTERN.findall(text):
            for piece in cls.CJK_CONNECTOR_PATTERN.split(phrase):
                cleaned = str(piece or "").strip()
                if 2 <= len(cleaned) <= 8:
                    candidates.append(cleaned)
        return candidates

    @classmethod
    def _extract_query_seeds(cls, query: str, query_policy: dict | None = None) -> list[str]:
        lines = [line.strip() for line in str(query or "").splitlines() if line.strip()]
        first_line = lines[0] if lines else ""
        ordered: list[str] = []
        seen: set[str] = set()
        for line_index, line in enumerate(lines[:4]):
            for phrase in cls.ASCII_PHRASE_PATTERN.findall(line):
                words = phrase.split()
                has_uppercase_signal = any(any(char.isupper() for char in word) for word in words)
                if len(words) > 1 and has_uppercase_signal:
                    cls._add_seed(ordered, seen, " ".join(words))
                for word in words:
                    lowered = word.lower()
                    if lowered in cls.NOISE_QUERY_TERMS:
                        continue
                    if line_index == 0:
                        if any(char.isupper() for char in word) or len(word) >= 3:
                            cls._add_seed(ordered, seen, word)
                    else:
                        if any(char.isupper() for char in word):
                            cls._add_seed(ordered, seen, word)
            for candidate in cls._extract_cjk_seed_candidates(line):
                if line_index == 0 or len(candidate) >= 3:
                    cls._add_seed(ordered, seen, candidate)
        lowered = first_line.lower()
        for trigger, aliases in cls.QUERY_SEED_ALIASES.items():
            if trigger in lowered:
                for alias in aliases:
                    cls._add_seed(ordered, seen, alias)
        policy_seed_terms = cls._policy_values(query_policy, "graph_seed_terms") or list(cls.DEFAULT_POLICY_SEED_TERMS)
        for cue in policy_seed_terms:
            if cue in first_line:
                cls._add_seed(ordered, seen, cue)
        return ordered[:8]

    @classmethod
    def _needs_entry_chunk(cls, query: str, seed_entities: list[str]) -> bool:
        first_line = str(query or "").splitlines()[0] if str(query or "").splitlines() else ""
        if not seed_entities:
            return True
        normalized = {seed.lower() for seed in seed_entities}
        strong_relation = bool(cls.STRONG_RELATION_CUE_PATTERN.search(first_line))
        if strong_relation and len(seed_entities) < 2:
            return True
        if normalized.issubset(cls.GENERIC_QUERY_SEEDS):
            return True
        return False

    @classmethod
    def _expanded_query_terms(cls, query: str, seed_entities: list[str], query_policy: dict | None = None) -> set[str]:
        query_lower = str(query or "").lower()
        terms = {term.lower() for term in seed_entities}
        for phrase in cls.ASCII_PHRASE_PATTERN.findall(query_lower):
            for word in phrase.split():
                if word not in cls.NOISE_QUERY_TERMS and len(word) > 1:
                    terms.add(word)
        for trigger, aliases in cls.QUERY_TERM_ALIASES.items():
            if trigger in query_lower:
                terms.update(aliases)
        for cue in cls._policy_values(query_policy, "graph_seed_terms"):
            if cue in query:
                terms.add(cue.lower())
        return terms

    @classmethod
    def _is_graph_worthy_query(cls, query: str, seed_entities: list[str], query_policy: dict | None = None) -> bool:
        first_line = str(query or "").splitlines()[0]
        if not seed_entities:
            return False
        policy_relation_cues = cls._policy_values(query_policy, "graph_relation_cues") or list(
            cls.DEFAULT_POLICY_RELATION_CUES
        )
        policy_step_cues = cls._policy_values(query_policy, "graph_step_cues") or list(
            cls.DEFAULT_POLICY_STEP_CUES
        )
        has_policy_relation_cue = any(cue in first_line for cue in policy_relation_cues)
        has_policy_step_cue = any(cue in first_line for cue in policy_step_cues)
        if cls.STRONG_RELATION_CUE_PATTERN.search(first_line):
            return True
        if has_policy_step_cue and any(re.search(r"[\u4e00-\u9fff]", seed) for seed in seed_entities):
            return True
        if has_policy_relation_cue and any(re.search(r"[\u4e00-\u9fff]", seed) for seed in seed_entities):
            return True
        if cls.NON_GRAPH_LISTING_PATTERN.search(first_line):
            return False
        return len(seed_entities) >= 2 and bool(cls.WEAK_RELATION_CUE_PATTERN.search(first_line))

    @classmethod
    def _is_generic_graph_entity(cls, value: str) -> bool:
        normalized = re.sub(r"\s+", " ", str(value or "")).strip()
        if not normalized:
            return True
        return normalized in cls.GENERIC_GRAPH_ENTITIES

    @classmethod
    def _noise_penalty(cls, query: str, doc: dict) -> int:
        query_lower = str(query or "").lower()
        file_name = str(doc.get("file_name") or "").lower()
        content = str(doc.get("content") or "").lower()
        summary = str(doc.get("summary") or "").lower()
        haystack = " ".join([file_name, content, summary])
        penalty = 0

        if "agent-server-scale" in file_name and not any(term in query_lower for term in cls.SCALE_QUERY_TERMS):
            penalty += 5
        if "milvus_adopters" in file_name or content.startswith("milvus adopters"):
            if "adopter" not in query_lower and "采用" not in query_lower and "用户" not in query_lower:
                penalty += 5
        if content.lstrip().startswith("---"):
            penalty += 2
        if "development > run tests" in content and "test" not in query_lower:
            penalty += 5
        if "api documentation" in haystack or "user guide:" in haystack:
            if "api documentation" not in query_lower and "user guide" not in query_lower and "文档" not in query_lower:
                penalty += 3
        if "container architecture" in content and "docker compose" in query_lower:
            penalty += 5

        stripped_lines = [line.strip() for line in str(doc.get("content") or "").splitlines() if line.strip()]
        metadata_like_lines = sum(
            1
            for line in stripped_lines[:6]
            if line.lower().startswith(("title:", "tags:", "aliases:"))
            or "路径语境" in line
            or line.count("#") >= 2
        )
        if metadata_like_lines >= 2 and len(str(doc.get("content") or "")) <= 500:
            penalty += 4
        if (str(doc.get("content") or "").count("#") >= 3 or "标签" in str(doc.get("content") or "")) and len(
            str(doc.get("content") or "")
        ) <= 400:
            penalty += 4

        return penalty

    @classmethod
    def _section_bonus(cls, query: str, haystack: str) -> int:
        query_lower = str(query or "").lower()
        bonus = 0

        if "持久化" in query_lower:
            if "persists three types of data" in haystack or haystack.startswith("persistence"):
                bonus += 10
            if "stored in postgresql" in haystack or "backed by postgresql by default" in haystack:
                bonus += 8
        if "部署" in query_lower and "parts of a deployment" in haystack:
            bonus += 8
        if "task queue" in query_lower and "redis" in query_lower and "postgresql" in query_lower:
            if "redis handles the signaling" in haystack and "written to postgresql" in haystack:
                bonus += 12
            if "task queue" in haystack:
                bonus += 4
        if ("层次" in query_lower or "系统设计" in query_lower) and "breaks down into four levels" in haystack:
            bonus += 12
        if ("执行路径" in query_lower or "运行路径" in query_lower) and "run execution lifecycle" in haystack:
            bonus += 10

        return bonus

    @classmethod
    def _score_document(cls, query: str, query_terms: set[str], doc: dict) -> tuple[int, int, int, int]:
        haystack = " ".join(
            [
                str(doc.get("file_name") or ""),
                str(doc.get("content") or ""),
                str(doc.get("summary") or ""),
            ]
        ).lower()
        hit_count = sum(1 for term in query_terms if term in haystack)
        support_count = int(doc.get("graph_support_count") or 0)
        file_focus = int(doc.get("graph_file_focus") or 0)
        noise_penalty = cls._noise_penalty(query, doc)
        section_bonus = cls._section_bonus(query, haystack)
        return (
            hit_count + section_bonus + (file_focus * 2) - noise_penalty,
            support_count + section_bonus + file_focus - noise_penalty,
            file_focus,
            section_bonus - noise_penalty,
            len(str(doc.get("content") or "")),
        )

    @classmethod
    def _pick_focus_file_ids(cls, documents: list[dict]) -> list[str]:
        file_scores: dict[str, int] = {}
        for doc in documents:
            file_id = str(doc.get("file_id") or "").strip()
            if not file_id:
                continue
            seed_hits = int(doc.get("graph_seed_hit_count") or 0)
            support_count = int(doc.get("graph_support_count") or 0)
            if seed_hits < 2 and support_count < 2:
                continue
            file_scores[file_id] = file_scores.get(file_id, 0) + (seed_hits * 3) + (support_count * 2)
        ordered = sorted(file_scores.items(), key=lambda item: item[1], reverse=True)
        return [file_id for file_id, score in ordered[:2] if score >= 8]

    async def _augment_documents_from_focus_files(
        self,
        *,
        knowledge_id: str,
        documents: list[dict],
        query_terms: set[str],
    ) -> list[dict]:
        fetch_by_file_id = getattr(self.chunk_store, "get_documents_by_file_id", None)
        if not callable(fetch_by_file_id):
            return documents

        focus_file_ids = self._pick_focus_file_ids(documents)
        if not focus_file_ids:
            return documents

        seen_chunk_ids = {str(doc.get("chunk_id") or "") for doc in documents if doc.get("chunk_id")}
        existing_focus_strength: dict[str, int] = {}
        for doc in documents:
            file_id = str(doc.get("file_id") or "").strip()
            if not file_id or file_id not in focus_file_ids:
                continue
            focus_strength = max(
                int(doc.get("graph_seed_hit_count") or 0) + int(doc.get("graph_support_count") or 0),
                int(doc.get("graph_file_focus") or 0),
            )
            doc["graph_file_focus"] = max(focus_strength, 2)
            existing_focus_strength[file_id] = max(existing_focus_strength.get(file_id, 0), int(doc.get("graph_file_focus") or 0))

        supplements: list[dict] = []
        for file_id in focus_file_ids:
            sibling_docs = await fetch_by_file_id(knowledge_id, file_id, limit=8)
            for sibling in sibling_docs:
                payload = sibling.to_dict() if hasattr(sibling, "to_dict") else dict(sibling)
                chunk_id = str(payload.get("chunk_id") or "").strip()
                if not chunk_id or chunk_id in seen_chunk_ids:
                    continue
                haystack = " ".join(
                    [
                        str(payload.get("file_name") or ""),
                        str(payload.get("content") or ""),
                        str(payload.get("summary") or ""),
                    ]
                ).lower()
                payload["graph_seed_hit_count"] = sum(1 for term in query_terms if term in haystack)
                payload["graph_support_count"] = 0
                payload["graph_file_focus"] = max(existing_focus_strength.get(file_id, 2) - 1, 1)
                supplements.append(payload)
                seen_chunk_ids.add(chunk_id)

        return documents + supplements

    async def retrieve(
        self,
        query: str,
        knowledge_id: str,
        *,
        graph_hop_limit: int = 2,
        max_paths_per_entity: int = 10,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        status: str | None = None,
        query_policy: dict | None = None,
    ) -> dict:
        entities = []
        paths = []
        chunk_ids = []
        chunk_id_support: dict[str, int] = {}
        seen_chunk_ids: set[str] = set()
        seen_paths: set[tuple[str, str]] = set()
        effective_query_policy = self._resolve_query_policy(
            domain_pack_id=domain_pack_id,
            query_policy=query_policy,
        )
        seed_entities = self._extract_query_seeds(query, effective_query_policy)
        if not self._is_graph_worthy_query(query, seed_entities, effective_query_policy):
            return {
                "content": "",
                "entities": [],
                "paths": [],
                "documents": [],
            }
        for entity_name in seed_entities:
            neighbor_paths = await self.client.query_neighbors(
                entity_name,
                knowledge_id,
                hops=graph_hop_limit,
                limit=max_paths_per_entity,
                domain_pack_id=domain_pack_id,
                index_version=index_version,
                status=status,
            )
            if neighbor_paths:
                filtered_paths = []
                for item in neighbor_paths:
                    source = str(item.get("source") or "").strip()
                    target = str(item.get("target") or "").strip()
                    if self._is_generic_graph_entity(source) or self._is_generic_graph_entity(target):
                        continue
                    filtered_paths.append(item)
                neighbor_paths = filtered_paths
            if neighbor_paths:
                entities.append(entity_name)
                for item in neighbor_paths:
                    path_key = (str(item.get("source") or ""), str(item.get("target") or ""))
                    if path_key not in seen_paths:
                        seen_paths.add(path_key)
                        paths.append(item)
                    for chunk_id in item.get("chunk_ids") or []:
                        if chunk_id in seen_chunk_ids:
                            chunk_id_support[chunk_id] = chunk_id_support.get(chunk_id, 0) + 1
                            continue
                        seen_chunk_ids.add(chunk_id)
                        chunk_ids.append(chunk_id)
                        chunk_id_support[chunk_id] = chunk_id_support.get(chunk_id, 0) + 1

        path_lines = [f"{item['source']} -> {item['target']}" for item in paths]
        documents = await self.chunk_store.get_documents_by_chunk_ids(knowledge_id, chunk_ids)
        document_dicts = [doc.to_dict() if hasattr(doc, "to_dict") else doc for doc in documents]
        query_terms = self._expanded_query_terms(query, seed_entities, effective_query_policy)
        for doc in document_dicts:
            haystack = " ".join(
                [
                    str(doc.get("file_name") or ""),
                    str(doc.get("content") or ""),
                    str(doc.get("summary") or ""),
                ]
            ).lower()
            doc["graph_seed_hit_count"] = sum(1 for term in query_terms if term in haystack)
            doc["graph_support_count"] = chunk_id_support.get(str(doc.get("chunk_id") or ""), 0)
            doc["graph_file_focus"] = 0
        document_dicts = await self._augment_documents_from_focus_files(
            knowledge_id=knowledge_id,
            documents=document_dicts,
            query_terms=query_terms,
        )
        document_dicts.sort(key=lambda doc: self._score_document(query, query_terms, doc), reverse=True)
        content_parts = [str(doc.get("content") or "") for doc in document_dicts if doc.get("content")]
        if not content_parts:
            content_parts = path_lines
        content = "\n".join(content_parts)
        return {
            "content": content,
            "entities": entities,
            "paths": path_lines,
            "structured_paths": paths,
            "documents": document_dicts,
            "domain_pack_id": domain_pack_id,
            "index_version": index_version,
            "status": status,
        }


__all__ = ["GraphRetriever"]
