import json
import os
from typing import Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from loguru import logger
from tavily import TavilyClient

from agentchat.core.models.manager import ModelManager
from agentchat.services.deepsearch.configuration import Configuration
from agentchat.services.deepsearch.prompts import (
    answer_instructions,
    get_current_date,
    query_writer_instructions,
    reflection_instructions,
)
from agentchat.services.deepsearch.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)

load_dotenv()


def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is not set")
    return TavilyClient(api_key=api_key)


def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    configurable = Configuration.from_runnable_config(config)

    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    llm = ModelManager.get_conversation_model()
    current_date = get_current_date()
    research_topic = get_research_topic(state["messages"])

    formatted_prompt = f"""
    {query_writer_instructions.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state["initial_search_query_count"],
    )}

    请用JSON格式回复，包含以下两个键:
    {{
        "rationale": "简要解释这些查询与研究主题的相关性",
        "query": ["查询1", "查询2"]
    }}
    """

    response = llm.invoke(formatted_prompt)
    content = response.content

    try:
        result = json.loads(content)
        queries = result.get("query", [])
        if not queries:
            queries = [research_topic]
        return {"search_query": queries}
    except Exception:
        logger.error("解析查询生成结果失败，回退到原始研究主题")
        return {"search_query": [research_topic]}


def continue_to_web_research(state: QueryGenerationState):
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    search_query = state["search_query"]
    query_id = state["id"]

    logger.info(f"Executing search: {search_query}")

    try:
        response = get_tavily_client().search(
            query=search_query,
            max_results=10,
            time_range="month",
            include_raw_content="markdown",
            country="china",
        )

        formatted_results = format_tavily_results(response)
        sources = []
        for idx, result in enumerate(response.get("results", [])):
            source_id = f"{query_id}-{idx}"
            source_url = result.get("url", "")
            source_title = result.get("title", "未知标题")
            sources.append(
                {
                    "short_url": f"https://search.result/{source_id}",
                    "value": source_url,
                    "label": source_title,
                }
            )

        logger.info(f"Found {len(response.get('results', []))} search results")
        return {
            "sources_gathered": sources,
            "search_query": [search_query],
            "web_research_result": [formatted_results],
        }
    except Exception as exc:
        logger.error(f"Search failed: {exc}")
        return {
            "sources_gathered": [],
            "search_query": [search_query],
            "web_research_result": [f"搜索失败: {exc}"],
        }


def format_tavily_results(response: Dict) -> str:
    if not response.get("results"):
        return "未找到相关结果"

    formatted = []
    for result in response["results"]:
        url = result.get("url", "")
        title = result.get("title", "")
        content = result.get("content", "")
        formatted.append(f"[{title}]({url})\n内容: {content}")

    return "\n\n".join(formatted)


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    llm = ModelManager.get_conversation_model()

    current_date = get_current_date()
    research_topic = get_research_topic(state["messages"])
    summaries = "\n\n---\n\n".join(state["web_research_result"])

    formatted_prompt = f"""
    {reflection_instructions.format(
        current_date=current_date,
        research_topic=research_topic,
        summaries=summaries,
    )}
    """

    response = llm.invoke(formatted_prompt)
    content = response.content

    try:
        result = json.loads(content)
        is_sufficient = result.get("is_sufficient", True)
        knowledge_gap = result.get("knowledge_gap", "")
        follow_up_queries = result.get("follow_up_queries", [])

        logger.info(f"Reflection result: {'sufficient' if is_sufficient else 'insufficient'}")
        if not is_sufficient:
            logger.info(f"Knowledge gap: {knowledge_gap}")
            logger.info(f"Follow-up queries: {follow_up_queries}")

        return {
            "is_sufficient": is_sufficient,
            "knowledge_gap": knowledge_gap,
            "follow_up_queries": follow_up_queries,
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state["search_query"]),
        }
    except Exception:
        logger.error("解析反思结果失败，默认研究已足够")
        return {
            "is_sufficient": True,
            "knowledge_gap": "",
            "follow_up_queries": [],
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state["search_query"]),
        }


def evaluate_research(state: ReflectionState, config: RunnableConfig) -> OverallState:
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        logger.info("Research completed, preparing final answer")
        return "finalize_answer"
    return [
        Send(
            "web_research",
            {
                "search_query": follow_up_query,
                "id": state["number_of_ran_queries"] + int(idx),
            },
        )
        for idx, follow_up_query in enumerate(state["follow_up_queries"])
    ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    llm = ModelManager.get_conversation_model()

    current_date = get_current_date()
    research_topic = get_research_topic(state["messages"])
    summaries = "\n---\n\n".join(state["web_research_result"])

    formatted_prompt = f"""
    {answer_instructions.format(
        current_date=current_date,
        research_topic=research_topic,
        summaries=summaries,
    )}
    """

    response = llm.invoke(formatted_prompt)
    content = response.content

    logger.info("Final answer generated")

    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in content:
            content = content.replace(source["short_url"], source["value"])
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=content)],
        "sources_gathered": unique_sources,
    }


def get_research_topic(messages):
    if not messages:
        return ""

    if len(messages) == 1:
        return messages[-1].content

    for message in reversed(messages):
        if hasattr(message, "type") and message.type == "human":
            return message.content
        if hasattr(message, "role") and message.role == "user":
            return message.content

    return messages[-1].content


builder = StateGraph(OverallState, config_schema=Configuration)
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)
builder.add_edge(START, "generate_query")
builder.add_conditional_edges("generate_query", continue_to_web_research, ["web_research"])
builder.add_edge("web_research", "reflection")
builder.add_conditional_edges("reflection", evaluate_research, ["web_research", "finalize_answer"])
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
