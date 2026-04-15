from __future__ import annotations

import re
from typing import Any, List, Tuple

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


USER_INPUT_PATTERN = re.compile(r"(?:用户输入|user\s*input)\s*[:：]", re.IGNORECASE)


def resolve_model_identity(model: Any) -> tuple[str, str]:
    model_name = getattr(model, "model_name", "") or getattr(model, "model", "")
    base_url = (
        getattr(model, "openai_api_base", "")
        or getattr(model, "base_url", "")
        or getattr(getattr(model, "client", None), "base_url", "")
    )
    return str(model_name or ""), str(base_url or "")


def is_minimax_model(model: Any = None, model_name: str = "", base_url: str = "") -> bool:
    if model is not None:
        resolved_model_name, resolved_base_url = resolve_model_identity(model)
        model_name = model_name or resolved_model_name
        base_url = base_url or resolved_base_url

    return "minimax" in model_name.lower() or "minimax" in base_url.lower()


def normalize_messages_for_model(
    messages: List[BaseMessage],
    model: Any = None,
    model_name: str = "",
    base_url: str = "",
) -> List[BaseMessage]:
    if not is_minimax_model(model=model, model_name=model_name, base_url=base_url):
        return messages

    system_contents: List[str] = []
    normalized_messages: List[BaseMessage] = []
    for message in messages:
        if isinstance(message, SystemMessage):
            if message.content:
                system_contents.append(str(message.content))
        else:
            normalized_messages.append(message)

    if not system_contents:
        return normalized_messages

    merged_system_prompt = "\n\n".join(system_contents).strip()
    if normalized_messages and isinstance(normalized_messages[0], HumanMessage):
        normalized_messages[0] = HumanMessage(
            content=f"{merged_system_prompt}\n\n用户输入：\n{normalized_messages[0].content}"
        )
    else:
        normalized_messages.insert(0, HumanMessage(content=merged_system_prompt))

    return normalized_messages


def strip_model_wrapper_from_user_input(content: str | None) -> str:
    if not content:
        return ""

    cleaned = str(content).replace("\r", "")
    matches = list(USER_INPUT_PATTERN.finditer(cleaned))
    if matches:
        return cleaned[matches[-1].end():].strip()

    return cleaned.strip()


def strip_think_tags(text: str) -> str:
    if not text:
        return ""

    visible_text = []
    inside_think = False
    remaining = text

    while remaining:
        if inside_think:
            end_index = remaining.find("</think>")
            if end_index == -1:
                break
            remaining = remaining[end_index + len("</think>"):]
            inside_think = False
            continue

        start_index = remaining.find("<think>")
        if start_index == -1:
            visible_text.append(remaining)
            break

        visible_text.append(remaining[:start_index])
        remaining = remaining[start_index + len("<think>"):]
        inside_think = True

    return "".join(visible_text)


def extract_visible_text_from_stream(chunk_content: str, inside_think: bool) -> Tuple[str, bool]:
    if not chunk_content:
        return "", inside_think

    visible_parts: List[str] = []
    remaining = chunk_content

    while remaining:
        if inside_think:
            end_index = remaining.find("</think>")
            if end_index == -1:
                return "".join(visible_parts), True
            remaining = remaining[end_index + len("</think>"):]
            inside_think = False
            continue

        start_index = remaining.find("<think>")
        if start_index == -1:
            visible_parts.append(remaining)
            break

        visible_parts.append(remaining[:start_index])
        remaining = remaining[start_index + len("<think>"):]
        inside_think = True

    return "".join(visible_parts), inside_think
