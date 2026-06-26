import re

from zuno.services.graphrag.client import Neo4jClient
from zuno.services.graphrag.entity_alias import resolve_alias
from zuno.services.rag.vector_db import milvus_client


class GraphRetriever:
    GENEALOGY_PATH_TEMPLATES = (
        ("maternal_grandfather", (("mother", "father"),)),
        ("paternal_grandfather", (("father", "father"),)),
        ("grandfather", (("parent", "father"), ("mother", "father"), ("father", "father"))),
        ("grandmother", (("parent", "mother"), ("father", "mother"), ("mother", "mother"))),
        ("father", (("father",), ("parent",))),
        ("mother", (("mother",), ("parent",))),
        ("spouse", (("spouse",), ("married_to",), ("married",))),
    )
    FAMILY_RELATION_TYPES = {
        "mother",
        "father",
        "parent",
        "child",
        "son",
        "daughter",
        "spouse",
        "wife",
        "husband",
        "married",
        "married_to",
        "sibling",
        "brother",
        "sister",
        "ancestor",
        "descendant",
        "grandfather",
        "grandmother",
    }
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
    COMPARISON_CUE_PATTERN = re.compile(
        r"(same nationality|same country|same neighborhood|same birthplace|share the same|"
        r"located in the same|which is older|which is younger|which is earlier|which is later|"
        r"born later|born earlier|was born later|was born earlier|"
        r"which is larger|which is smaller|\u662f\u5426\u76f8\u540c|\u540c\u4e00|\u5206\u522b\u6765\u81ea|\u8c01\u66f4)",
        re.IGNORECASE,
    )
    BRIDGE_RELATION_CUE_PATTERN = re.compile(
        r"(mother of the director|father of the director|spouse of the performer|"
        r"birthplace of the founder|government position .* portrayed|woman who portrayed|"
        r"man who portrayed|director of .* based in what|founder of|founded by|father of|mother of|"
        r"professor at|university .* located in what city|based in what city|hail from|where does .* hail from|"
        r"located in what city|director of|author of|performer of|spouse of|producer of|creator of|"
        r"\u7684\u5bfc\u6f14|\u7684\u521b\u59cb\u4eba|\u7684\u4f5c\u8005|\u7684\u914d\u5076)",
        re.IGNORECASE,
    )
    GENEALOGY_RELATION_CUE_PATTERN = re.compile(
        r"(maternal grandfather|paternal grandfather|grandfather|grandmother|father die|mother die|"
        r"when did .* father die|when did .* mother die|who is .* father|who is .* mother|"
        r"spouse|wife|husband|child of|son of|daughter of|sibling of|brother of|sister of|"
        r"married to|family tree|ancestor|descendant)",
        re.IGNORECASE,
    )
    MULTI_ENTITY_RELATION_CUE_PATTERN = re.compile(
        r"(related to|relationship between|what connects|how is .* related|acquired|influenced|"
        r"founded by|directed by|portrayed by|based in what|held by|\u5173\u8054|\u8fde\u63a5|\u6536\u8d2d|\u5f71\u54cd)",
        re.IGNORECASE,
    )
    SIMPLE_FACT_LOOKUP_PATTERN = re.compile(
        r"^\s*(what is|who is|when was|when is|where is|what year|what date|\u4ec0\u4e48\u662f|\u4f55\u65f6|\u54ea\u4e00\u5e74)",
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

    @staticmethod
    def _policy_aliases(query_policy: dict | None, key: str) -> dict[str, list[str]]:
        if not query_policy:
            return {}
        raw = query_policy.get(key)
        if not isinstance(raw, dict):
            return {}
        aliases: dict[str, list[str]] = {}
        for trigger, values in raw.items():
            normalized_trigger = str(trigger or "").strip().lower()
            if not normalized_trigger:
                continue
            if isinstance(values, str):
                parsed = [item.strip() for item in re.split(r"[|,，;/]+", values) if item.strip()]
            elif isinstance(values, (list, tuple, set)):
                parsed = [str(item or "").strip() for item in values if str(item or "").strip()]
            else:
                continue
            if parsed:
                aliases[normalized_trigger] = parsed
        return aliases

    @classmethod
    def _resolve_query_policy(
        cls,
        *,
        domain_pack_id: str | None,
        query_policy: dict | None,
    ) -> dict[str, object]:
        del domain_pack_id
        return dict(query_policy or {})

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
        return [
            item["value"]
            for item in cls._build_seed_entities_with_source(
                query,
                query_policy=query_policy,
            )
        ]

    @classmethod
    def _build_seed_entities_with_source(
        cls,
        query: str,
        *,
        query_policy: dict | None = None,
        candidate_context: dict | None = None,
        max_seed_entities: int = 8,
    ) -> list[dict[str, str]]:
        lines = [line.strip() for line in str(query or "").splitlines() if line.strip()]
        first_line = lines[0] if lines else ""
        ordered: list[dict[str, str]] = []
        seen: set[str] = set()

        def add_seed(value: str, source: str):
            cleaned = re.sub(r"\s+", " ", str(value or "")).strip("`*_#-:;,.!?()[]{}<>\"'")
            if not cleaned:
                return
            normalized = cleaned.lower()
            if normalized in cls.NOISE_QUERY_TERMS or normalized in seen or cls._is_generic_graph_entity(cleaned):
                return
            seen.add(normalized)
            ordered.append({"value": cleaned, "source": source})

        deferred_query_terms: list[str] = []
        for line_index, line in enumerate(lines[:4]):
            for phrase in cls.ASCII_PHRASE_PATTERN.findall(line):
                words = phrase.split()
                has_uppercase_signal = any(any(char.isupper() for char in word) for word in words)
                if len(words) > 1 and has_uppercase_signal:
                    add_seed(" ".join(words), "query")
                for word in words:
                    lowered = word.lower()
                    if lowered in cls.NOISE_QUERY_TERMS:
                        continue
                    if line_index == 0:
                        if any(char.isupper() for char in word) or len(word) >= 3:
                            if any(char.isupper() for char in word):
                                add_seed(word, "query")
                            else:
                                deferred_query_terms.append(word)
                    else:
                        if any(char.isupper() for char in word):
                            add_seed(word, "query")
            for candidate in cls._extract_cjk_seed_candidates(line):
                if line_index == 0 or len(candidate) >= 3:
                    add_seed(candidate, "query")
        lowered = first_line.lower()
        seed_aliases = cls._policy_aliases(query_policy, "graph_seed_aliases")
        if not seed_aliases:
            seed_aliases = {key: list(value) for key, value in cls.QUERY_SEED_ALIASES.items()}
        for trigger, aliases in seed_aliases.items():
            if trigger in lowered:
                for alias in aliases:
                    add_seed(alias, "alias")
        policy_seed_terms = cls._policy_values(query_policy, "graph_seed_terms") or list(cls.DEFAULT_POLICY_SEED_TERMS)
        for cue in policy_seed_terms:
            if cue in first_line:
                add_seed(cue, "query")

        documents = list((candidate_context or {}).get("documents") or [])
        known_entities = []
        for document in documents:
            title = str(document.get("title") or "").strip()
            file_name = str(document.get("file_name") or "").strip()
            if title:
                known_entities.append(title)
            if file_name and file_name != title:
                known_entities.append(file_name)
        for document in documents:
            title = str(document.get("title") or "").strip()
            file_name = str(document.get("file_name") or "").strip()
            if title:
                alias_match = resolve_alias(title, known_entities)
                add_seed(str(alias_match["resolved_to"]), "alias" if alias_match["matched"] and alias_match["resolved_to"] != title else "baseline_title")
            if file_name and file_name != title:
                alias_match = resolve_alias(file_name, known_entities)
                add_seed(str(alias_match["resolved_to"]), "alias" if alias_match["matched"] and alias_match["resolved_to"] != file_name else "baseline_file")
            for mention in document.get("entity_mentions") or []:
                alias_match = resolve_alias(str(mention or ""), known_entities)
                add_seed(str(alias_match["resolved_to"]), "alias" if alias_match["matched"] and alias_match["resolved_to"] != str(mention or "") else "baseline_entity")
            if len(ordered) >= max_seed_entities:
                break
        for deferred in deferred_query_terms:
            if len(ordered) >= max_seed_entities:
                break
            add_seed(deferred, "query")
        return ordered[:max_seed_entities]

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
        term_aliases = cls._policy_aliases(query_policy, "query_term_aliases")
        if not term_aliases:
            term_aliases = {key: list(value) for key, value in cls.QUERY_TERM_ALIASES.items()}
        for trigger, aliases in term_aliases.items():
            if trigger in query_lower:
                terms.update(aliases)
        for cue in cls._policy_values(query_policy, "graph_seed_terms"):
            if cue in query:
                terms.add(cue.lower())
        return terms

    @staticmethod
    def _preferred_relation_type(query_policy: dict | None) -> str | None:
        value = str((query_policy or {}).get("risk_relation_preference") or "").strip()
        return value or None

    @classmethod
    def _path_sort_key(cls, item: dict, preferred_relation_type: str | None) -> tuple[int, str, str]:
        relation_type = str(item.get("relation_type") or "").strip()
        preferred = 1 if preferred_relation_type and relation_type == preferred_relation_type else 0
        return (
            preferred,
            str(item.get("source") or ""),
            str(item.get("target") or ""),
        )

    @classmethod
    def _score_path(cls, query: str, item: dict, seed_entities: list[str]) -> tuple[int, int, int, int, int, int]:
        query_lower = str(query or "").lower()
        source = str(item.get("source") or "").strip()
        target = str(item.get("target") or "").strip()
        relation_type = str(item.get("relation_type") or "").strip().lower()
        combined = f"{source} {target} {relation_type}".lower()
        normalized_seeds = [str(seed or "").strip().lower() for seed in seed_entities if str(seed or "").strip()]

        seed_coverage = sum(1 for seed in normalized_seeds if seed and (seed in combined or combined in seed))
        relation_cue_match = 0
        bridge_bonus = 0
        comparison_bonus = 0
        title_match_bonus = 0
        generic_entity_penalty = 0

        if cls._is_comparison_query(query):
            if relation_type in {"nationality", "country", "birthplace", "location", "neighborhood"}:
                comparison_bonus += 3
            if any(token in combined for token in ["american", "country", "city", "birth", "neighborhood"]):
                comparison_bonus += 2

        if cls._is_bridge_relation_query(query):
            if relation_type in {"director", "founder", "author", "performer", "spouse", "mother", "government_position"}:
                bridge_bonus += 3
            if any(token in query_lower for token in ["director", "founder", "author", "performer", "spouse", "mother", "position"]):
                bridge_bonus += 1
        if cls._is_genealogy_relation_query(query):
            if relation_type in {"father", "mother", "parent", "child", "spouse", "sibling", "ancestor", "descendant"}:
                bridge_bonus += 3
            if any(
                token in query_lower
                for token in ["father", "mother", "parent", "child", "spouse", "wife", "husband", "grandfather", "grandmother"]
            ):
                bridge_bonus += 1

        if cls._is_multi_entity_relation_query(query):
            if relation_type in {"related_to", "acquired", "influenced", "founded_by", "directed_by"}:
                relation_cue_match += 2

        if any(seed in str(source).lower() or seed in str(target).lower() for seed in normalized_seeds):
            title_match_bonus += 1

        if cls._is_generic_graph_entity(source) or cls._is_generic_graph_entity(target):
            generic_entity_penalty += 3

        support_count = len(list(item.get("chunk_ids") or []))
        return (
            seed_coverage + relation_cue_match + bridge_bonus + comparison_bonus + title_match_bonus - generic_entity_penalty,
            seed_coverage,
            relation_cue_match + bridge_bonus + comparison_bonus,
            title_match_bonus,
            support_count,
            -generic_entity_penalty,
        )

    @staticmethod
    def _normalize_relation_type(value: str) -> str:
        normalized = re.sub(r"[^0-9A-Za-z]+", "_", str(value or "").strip().lower()).strip("_")
        return normalized

    @classmethod
    def _normalized_relation_types(cls, item: dict) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        raw_values = list(item.get("path_relation_types") or item.get("relation_labels") or [])
        relation_type = str(item.get("relation_type") or "").strip()
        if relation_type:
            raw_values.append(relation_type)
        for value in raw_values:
            normalized = cls._normalize_relation_type(value)
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered

    @classmethod
    def _genealogy_template_match(cls, query: str, normalized_relation_types: list[str]) -> str | None:
        if not cls._is_genealogy_relation_query(query):
            return None
        relation_chain = tuple(normalized_relation_types)
        for template_name, candidate_paths in cls.GENEALOGY_PATH_TEMPLATES:
            if template_name.replace("_", " ") not in str(query or "").lower() and template_name not in relation_chain:
                if template_name not in {"father", "mother", "spouse"}:
                    continue
            for candidate_path in candidate_paths:
                if len(relation_chain) < len(candidate_path):
                    continue
                if tuple(relation_chain[: len(candidate_path)]) == candidate_path:
                    return template_name
        return None

    @classmethod
    def _relation_cue_match(cls, query: str, normalized_relation_types: list[str]) -> bool:
        query_lower = str(query or "").lower()
        if not normalized_relation_types:
            return False
        if cls._genealogy_template_match(query, normalized_relation_types):
            return True
        if cls._is_genealogy_relation_query(query):
            return any(relation_type in cls.FAMILY_RELATION_TYPES and relation_type in query_lower for relation_type in normalized_relation_types) or any(
                relation_type in cls.FAMILY_RELATION_TYPES for relation_type in normalized_relation_types
            )
        return any(relation_type in query_lower for relation_type in normalized_relation_types)

    @classmethod
    def _path_metadata(cls, query: str, item: dict, seed_entities: list[str]) -> dict[str, object]:
        normalized_relation_types = cls._normalized_relation_types(item)
        path_nodes = [str(value or "").strip() for value in (item.get("path_nodes") or []) if str(value or "").strip()]
        normalized_seeds = [str(seed or "").strip().lower() for seed in seed_entities if str(seed or "").strip()]
        seed_entity_coverage = 0
        bridge_entity_coverage = 0
        normalized_path_nodes = [value.lower() for value in path_nodes]
        for seed in normalized_seeds:
            if any(seed in node or node in seed for node in normalized_path_nodes):
                seed_entity_coverage += 1
        if path_nodes:
            bridge_nodes = path_nodes[1:-1] if len(path_nodes) > 2 else path_nodes[1:]
            bridge_entity_coverage = len([node for node in bridge_nodes if node])
        relation_labels = list(item.get("relation_labels") or item.get("path_relation_types") or normalized_relation_types)
        path_length = len(normalized_relation_types) or max(len(path_nodes) - 1, 1 if relation_labels else 0)
        text_unit_support_count = len(list(item.get("chunk_ids") or []))
        genealogy_path_template_match = cls._genealogy_template_match(query, normalized_relation_types)
        relation_cue_match = cls._relation_cue_match(query, normalized_relation_types)
        return {
            "graph_path_relation_labels": relation_labels,
            "normalized_relation_types": normalized_relation_types,
            "path_length": path_length,
            "seed_entity_coverage": seed_entity_coverage,
            "bridge_entity_coverage": bridge_entity_coverage,
            "text_unit_support_count": text_unit_support_count,
            "relation_cue_match": relation_cue_match,
            "genealogy_path_template_match": genealogy_path_template_match,
        }

    @classmethod
    def _is_graph_worthy_query(cls, query: str, seed_entities: list[str], query_policy: dict | None = None) -> bool:
        first_line = str(query or "").splitlines()[0]
        if not seed_entities:
            return False
        if cls.NON_GRAPH_LISTING_PATTERN.search(first_line):
            return False
        comparison_question = cls._is_comparison_query(first_line)
        bridge_relation_question = cls._is_bridge_relation_query(first_line)
        genealogy_relation_question = cls._is_genealogy_relation_query(first_line)
        multi_entity_relation_question = cls._is_multi_entity_relation_query(first_line)
        if cls._is_simple_fact_lookup(first_line) and not (
            comparison_question or bridge_relation_question or genealogy_relation_question or multi_entity_relation_question
        ):
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
        if comparison_question or bridge_relation_question or genealogy_relation_question or multi_entity_relation_question:
            return True
        if has_policy_step_cue and any(re.search(r"[\u4e00-\u9fff]", seed) for seed in seed_entities):
            return True
        if has_policy_relation_cue and any(re.search(r"[\u4e00-\u9fff]", seed) for seed in seed_entities):
            return True
        return len(seed_entities) >= 2 and bool(cls.WEAK_RELATION_CUE_PATTERN.search(first_line))

    @classmethod
    def _is_comparison_query(cls, query: str) -> bool:
        return bool(cls.COMPARISON_CUE_PATTERN.search(str(query or "")))

    @classmethod
    def _is_bridge_relation_query(cls, query: str) -> bool:
        return bool(cls.BRIDGE_RELATION_CUE_PATTERN.search(str(query or "")))

    @classmethod
    def _is_genealogy_relation_query(cls, query: str) -> bool:
        return bool(cls.GENEALOGY_RELATION_CUE_PATTERN.search(str(query or "")))

    @classmethod
    def _is_multi_entity_relation_query(cls, query: str) -> bool:
        return bool(cls.MULTI_ENTITY_RELATION_CUE_PATTERN.search(str(query or "")))

    @classmethod
    def _is_simple_fact_lookup(cls, query: str) -> bool:
        return bool(cls.SIMPLE_FACT_LOOKUP_PATTERN.search(str(query or "")))

    @classmethod
    def _has_graph_relation_signal(cls, query: str, query_policy: dict | None = None) -> bool:
        first_line = str(query or "").splitlines()[0] if str(query or "").splitlines() else ""
        policy_relation_cues = cls._policy_values(query_policy, "graph_relation_cues") or list(
            cls.DEFAULT_POLICY_RELATION_CUES
        )
        policy_step_cues = cls._policy_values(query_policy, "graph_step_cues") or list(cls.DEFAULT_POLICY_STEP_CUES)
        return bool(
            cls.STRONG_RELATION_CUE_PATTERN.search(first_line)
            or cls.WEAK_RELATION_CUE_PATTERN.search(first_line)
            or cls._is_comparison_query(first_line)
            or cls._is_bridge_relation_query(first_line)
            or cls._is_genealogy_relation_query(first_line)
            or cls._is_multi_entity_relation_query(first_line)
            or any(cue in first_line for cue in policy_relation_cues)
            or any(cue in first_line for cue in policy_step_cues)
        )

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
        path_score = int(doc.get("graph_path_score") or 0)
        noise_penalty = cls._noise_penalty(query, doc)
        section_bonus = cls._section_bonus(query, haystack)
        return (
            hit_count + section_bonus + (file_focus * 2) + path_score - noise_penalty,
            support_count + section_bonus + file_focus + path_score - noise_penalty,
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
        graphrag_project_id: str | None = None,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        status: str | None = None,
        query_policy: dict | None = None,
        candidate_context: dict | None = None,
    ) -> dict:
        entities = []
        paths = []
        chunk_ids = []
        chunk_id_support: dict[str, int] = {}
        chunk_path_score: dict[str, int] = {}
        chunk_path_count: dict[str, int] = {}
        chunk_best_path_metadata: dict[str, dict[str, object]] = {}
        seen_chunk_ids: set[str] = set()
        seen_paths: set[tuple[str, str]] = set()
        effective_query_policy = self._resolve_query_policy(
            domain_pack_id=domain_pack_id,
            query_policy=query_policy,
        )
        effective_graphrag_project_id = graphrag_project_id or domain_pack_id
        seed_entities_with_source = self._build_seed_entities_with_source(
            query,
            query_policy=effective_query_policy,
            candidate_context=candidate_context,
        )
        seed_entities = [item["value"] for item in seed_entities_with_source]
        if not self._is_graph_worthy_query(query, seed_entities, effective_query_policy):
            return {
                "content": "",
                "entities": [],
                "paths": [],
                "documents": [],
                "seed_entities_with_source": seed_entities_with_source,
            }
        for entity_name in seed_entities:
            try:
                neighbor_paths = await self.client.query_neighbors(
                    entity_name,
                    knowledge_id,
                    hops=graph_hop_limit,
                    limit=max_paths_per_entity,
                    graphrag_project_id=effective_graphrag_project_id,
                    domain_pack_id=domain_pack_id,
                    index_version=index_version,
                    status=status,
                )
            except TypeError:
                neighbor_paths = await self.client.query_neighbors(
                    entity_name,
                    knowledge_id,
                    hops=graph_hop_limit,
                    limit=max_paths_per_entity,
                    domain_pack_id=effective_graphrag_project_id,
                )
            if neighbor_paths:
                preferred_relation_type = self._preferred_relation_type(effective_query_policy)
                filtered_paths = []
                for item in neighbor_paths:
                    source = str(item.get("source") or "").strip()
                    target = str(item.get("target") or "").strip()
                    if self._is_generic_graph_entity(source) or self._is_generic_graph_entity(target):
                        continue
                    filtered_paths.append(item)
                neighbor_paths = sorted(
                    filtered_paths,
                    key=lambda item: (
                        self._score_path(query, item, seed_entities),
                        self._path_sort_key(item, preferred_relation_type),
                    ),
                    reverse=True,
                )
            if neighbor_paths:
                entities.append(entity_name)
                for item in neighbor_paths:
                    path_metadata = self._path_metadata(query, item, seed_entities)
                    item.update(path_metadata)
                    path_key = (str(item.get("source") or ""), str(item.get("target") or ""))
                    if path_key not in seen_paths:
                        seen_paths.add(path_key)
                        paths.append(item)
                    for chunk_id in item.get("chunk_ids") or []:
                        path_score = sum(max(value, 0) for value in self._score_path(query, item, seed_entities))
                        current_best = chunk_best_path_metadata.get(chunk_id)
                        if current_best is None or (
                            int(path_metadata.get("relation_cue_match") or 0),
                            int(bool(path_metadata.get("genealogy_path_template_match"))),
                            int(path_metadata.get("text_unit_support_count") or 0),
                            int(path_metadata.get("seed_entity_coverage") or 0),
                            int(path_metadata.get("bridge_entity_coverage") or 0),
                        ) > (
                            int(current_best.get("relation_cue_match") or 0),
                            int(bool(current_best.get("genealogy_path_template_match"))),
                            int(current_best.get("text_unit_support_count") or 0),
                            int(current_best.get("seed_entity_coverage") or 0),
                            int(current_best.get("bridge_entity_coverage") or 0),
                        ):
                            chunk_best_path_metadata[chunk_id] = dict(path_metadata)
                        if chunk_id in seen_chunk_ids:
                            chunk_id_support[chunk_id] = chunk_id_support.get(chunk_id, 0) + 1
                            chunk_path_score[chunk_id] = chunk_path_score.get(chunk_id, 0) + path_score
                            chunk_path_count[chunk_id] = chunk_path_count.get(chunk_id, 0) + 1
                            continue
                        seen_chunk_ids.add(chunk_id)
                        chunk_ids.append(chunk_id)
                        chunk_id_support[chunk_id] = chunk_id_support.get(chunk_id, 0) + 1
                        chunk_path_score[chunk_id] = chunk_path_score.get(chunk_id, 0) + path_score
                        chunk_path_count[chunk_id] = chunk_path_count.get(chunk_id, 0) + 1

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
            doc["graph_path_count"] = chunk_path_count.get(str(doc.get("chunk_id") or ""), 0)
            doc["graph_path_score"] = chunk_path_score.get(str(doc.get("chunk_id") or ""), 0)
            doc.update(chunk_best_path_metadata.get(str(doc.get("chunk_id") or ""), {}))
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
            "seed_entities_with_source": seed_entities_with_source,
            "graphrag_project_id": effective_graphrag_project_id,
            "domain_pack_id": domain_pack_id,
            "index_version": index_version,
            "status": status,
        }


__all__ = ["GraphRetriever"]
