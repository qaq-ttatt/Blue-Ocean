"""构建 LangChain ReAct 智能体。"""
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from demo_agent.tools import calculator, current_time

SYSTEM_PROMPT = (
    "你是一个乐于助人的助手。回答问题时可以调用工具："
    "涉及算术运算时使用 calculator，询问时间/日期时使用 current_time。"
)


def build_agent(
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
):
    """构造 ChatOpenAI 并返回 ReAct 智能体。

    参数缺省时从环境变量读取：OPENAI_MODEL / OPENAI_BASE_URL / OPENAI_API_KEY。
    其中 OPENAI_BASE_URL 可选，指向任意兼容 OpenAI 协议的服务商。
    """
    llm = ChatOpenAI(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        base_url=base_url or os.getenv("OPENAI_BASE_URL"),
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        temperature=0,
    )
    return create_react_agent(
        llm,
        tools=[calculator, current_time],
        prompt=SYSTEM_PROMPT,
    )
