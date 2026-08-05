"""构建 LangChain ReAct 智能体。"""
import json
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from demo_agent.tools import (
    base64_tool,
    calculator,
    count_words,
    current_time,
    days_between,
    hash_text,
    is_prime,
    unit_convert,
)

SYSTEM_PROMPT = (
    "你是一个乐于助人的助手。回答问题时可以调用工具："
    "涉及算术运算时使用 calculator，询问时间/日期或日期差时使用 current_time / days_between，"
    "统计字数用 count_words，计算哈希摘要用 hash_text，base64 编解码用 base64_tool，"
    "单位换算用 unit_convert，判断质数用 is_prime，"
    "涉及天气、掷骰子、行情、汇率、名言或密码时使用 MCP 提供的工具。"
)


def _load_mcp_servers() -> dict:
    """从 MCP_SERVERS 环境变量读取 MCP 服务器配置（JSON 对象）。"""
    raw = os.getenv("MCP_SERVERS")
    if not raw:
        return {}
    try:
        servers = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"MCP_SERVERS 不是合法的 JSON: {exc}") from exc
    if not isinstance(servers, dict):
        raise ValueError(
            'MCP_SERVERS 必须是 JSON 对象，如 {"mcp-demo": {"transport": "stdio", "command": "python", "args": ["mcp_demo_server.py"]}}'
        )
    return servers


async def build_agent(
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    mcp_servers: dict | None = None,
):
    """构造 ChatOpenAI + 可选 MCP 工具，返回 ReAct 智能体。

    模型参数缺省时从环境变量读取：OPENAI_MODEL / OPENAI_BASE_URL / OPENAI_API_KEY。
    MCP 服务器缺省时从 MCP_SERVERS 环境变量读取（JSON）。MCP 工具每次调用
    独立建立 session，无需手动关闭连接。
    """
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "未找到 OPENAI_API_KEY。请参考 .env.example 复制一份 .env 并填入 key，"
            "或通过环境变量 / build_agent(api_key=...) 传入。"
        )
    llm = ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0,
    )

    tools = [
        calculator,
        current_time,
        count_words,
        hash_text,
        base64_tool,
        unit_convert,
        is_prime,
        days_between,
    ]

    config = mcp_servers if mcp_servers is not None else _load_mcp_servers()
    if config:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        mcp_tools = await MultiServerMCPClient(config).get_tools()
        tools += mcp_tools
        print(f"已从 MCP 加载 {len(mcp_tools)} 个工具: {[t.name for t in mcp_tools]}")

    return create_react_agent(llm, tools=tools, prompt=SYSTEM_PROMPT)
