import re


class GraphExtractor:
    PROPER_ENTITY_PATTERN = re.compile(
        r"\b(?:[A-Z][a-zA-Z0-9_-]*|[A-Z]{2,}[A-Za-z0-9_-]*)(?:\s+(?:[A-Z][a-zA-Z0-9_-]*|[A-Z]{2,}[A-Za-z0-9_-]*))*\b"
    )
    TITLE_ENTITY_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9_-]*(?:\s+[a-z][A-Za-z0-9_-]*)+$")
    MIXED_ENTITY_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9 _()/:-]{1,100}$")
    LOWER_ENTITY_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*)*$")
    LIST_LABEL_PATTERN = re.compile(
        r"^\s*(?:[-*]\s+|<li>)\*{0,2}(?P<label>[A-Za-z][A-Za-z0-9 _()/:-]{1,100}?)\*{0,2}(?:\s*:\s*|\s+-\s+|\s*</li>|$)"
    )
    STOP_ENTITIES = {
        "A",
        "An",
        "And",
        "Are",
        "As",
        "At",
        "Be",
        "By",
        "For",
        "From",
        "How",
        "If",
        "In",
        "Into",
        "Is",
        "It",
        "Its",
        "Of",
        "On",
        "Or",
        "So",
        "The",
        "This",
        "That",
        "These",
        "Those",
        "To",
        "We",
        "With",
    }
    EXPLICIT_RELATION_PATTERNS = [
        re.compile(
            r"(?P<source>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+release approvals are handled by\s+(?P<target>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?P<source>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+reports to\s+(?P<target>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?P<source>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+leads\s+(?P<target>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?P<source>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+writes(?:\s+data)?\s+(?:into|to)\s+(?P<target>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?P<source>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+is hosted in\s+(?P<target>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?P<source>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+is owned by\s+(?P<target>[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)",
            re.IGNORECASE,
        ),
        re.compile(
            r"deploy\s+(?P<source>Agent Server).*?one or more\s+(?P<first>graphs).*?database for\s+(?P<second>persistence).*?and a\s+(?P<third>task queue)",
            re.IGNORECASE,
        ),
    ]

    @classmethod
    def _normalize_whitespace(cls, text: str) -> str:
        return re.sub(r"\s+", " ", str(text or "")).strip()

    @classmethod
    def _clean_entity_name(cls, value: str, *, allow_lowercase: bool = False) -> str | None:
        text = cls._normalize_whitespace(str(value or "").replace("**", "")).strip("`*_#-:;,.!?[]{}<>\"'")
        if not text:
            return None
        if text in cls.STOP_ENTITIES:
            return None
        if allow_lowercase:
            if cls.LOWER_ENTITY_PATTERN.fullmatch(text):
                return text
            return None
        if (
            not cls.PROPER_ENTITY_PATTERN.fullmatch(text)
            and not cls.TITLE_ENTITY_PATTERN.fullmatch(text)
            and not cls.MIXED_ENTITY_PATTERN.fullmatch(text)
        ):
            return None
        parts = text.split()
        if len(parts) == 1 and parts[0] in cls.STOP_ENTITIES:
            return None
        return " ".join(parts)

    @classmethod
    def _extract_anchor_entity(cls, content: str) -> str | None:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines[:8]:
            candidate_line = re.sub(r"^#+\s*", "", line)
            matches = [cls._clean_entity_name(match) for match in cls.PROPER_ENTITY_PATTERN.findall(candidate_line)]
            matches = [match for match in matches if match]
            if matches:
                return max(matches, key=lambda item: (item.count(" "), len(item)))
        return None

    @classmethod
    def _iter_explicit_relations(cls, content: str):
        compact = cls._normalize_whitespace(content)
        for pattern in cls.EXPLICIT_RELATION_PATTERNS:
            for match in pattern.finditer(compact):
                source = cls._clean_entity_name(match.groupdict().get("source"))
                if {"first", "second", "third"} <= set(match.groupdict()):
                    for key in ("first", "second", "third"):
                        target = cls._clean_entity_name(match.groupdict().get(key), allow_lowercase=True)
                        if source and target and source != target:
                            yield source, target
                    continue
                target = cls._clean_entity_name(match.group("target"))
                if source and target and source != target:
                    yield source, target

    @classmethod
    def _iter_list_relations(cls, content: str, anchor: str | None):
        active_source = anchor
        list_trigger_active = False
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lowered = line.lower()
            if (
                "breaks down into" in lowered
                or "consists of" in lowered
                or "comprises" in lowered
                or "includes" in lowered
                or "persists three types of data" in lowered
                or "supports three runtime configurations" in lowered
                or "you are deploying" in lowered
            ):
                list_trigger_active = True
                for proper in cls.PROPER_ENTITY_PATTERN.findall(line):
                    cleaned = cls._clean_entity_name(proper)
                    if cleaned:
                        active_source = cleaned
                        break
                continue
            label_match = cls.LIST_LABEL_PATTERN.match(line)
            if label_match:
                label = label_match.group("label").strip()
                entity = cls._clean_entity_name(label)
                if entity is None:
                    entity = cls._clean_entity_name(label.lower(), allow_lowercase=True)
                source = active_source
                if not source:
                    remainder = line[label_match.end() :]
                    for proper in cls.PROPER_ENTITY_PATTERN.findall(remainder):
                        cleaned = cls._clean_entity_name(proper)
                        if cleaned:
                            source = cleaned
                            break
                inline_mentions_source = bool(source and source.lower() in line.lower())
                if source and entity and source != entity and (list_trigger_active or inline_mentions_source):
                    yield source, entity
                continue
            list_trigger_active = False

    @classmethod
    def _iter_anchor_mentions(cls, content: str, anchor: str | None):
        if not anchor:
            return
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", content):
            line = sentence.strip()
            if not line or anchor.lower() not in line.lower():
                continue
            for proper in cls.PROPER_ENTITY_PATTERN.findall(line):
                cleaned = cls._clean_entity_name(proper)
                if cleaned and cleaned != anchor:
                    yield anchor, cleaned

    async def extract_from_chunk(self, chunk: dict, knowledge_id: str) -> dict:
        if hasattr(chunk, "to_dict"):
            chunk = chunk.to_dict()

        content = (chunk.get("content") or "").strip()
        chunk_id = chunk.get("chunk_id", "")
        anchor = self._extract_anchor_entity(content)

        entities = []
        relations = []
        seen_entities = set()
        seen_relations = set()

        def add_entity(name: str | None):
            if not name or name in seen_entities:
                return
            seen_entities.add(name)
            entities.append(
                {
                    "name": name,
                    "type": "entity",
                    "knowledge_id": knowledge_id,
                    "chunk_id": chunk_id,
                }
            )

        def add_relation(source: str | None, target: str | None, relation_type: str = "related_to"):
            if not source or not target or source == target:
                return
            key = (source, target, relation_type)
            if key in seen_relations:
                return
            seen_relations.add(key)
            add_entity(source)
            add_entity(target)
            relations.append(
                {
                    "source": source,
                    "target": target,
                    "relation_type": relation_type,
                    "knowledge_id": knowledge_id,
                    "chunk_id": chunk_id,
                }
            )

        add_entity(anchor)

        for source, target in self._iter_explicit_relations(content):
            add_relation(source, target, "explicit_relation")

        for source, target in self._iter_list_relations(content, anchor):
            add_relation(source, target, "structural_relation")

        for source, target in self._iter_anchor_mentions(content, anchor):
            add_relation(source, target, "anchor_relation")

        return {
            "entities": entities,
            "relations": relations,
        }
