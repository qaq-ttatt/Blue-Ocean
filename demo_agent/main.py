"""demo 智能体的命令行入口。

用法：
    python -m demo_agent.main "帮我算一下 (123 + 45) * 2"   # 单次提问
    python -m demo_agent.main                              # 交互式对话
    python -m demo_agent.main -r                           # 交互式对话（恢复上次会话）
    启用 MCP 工具：在 .env 中设置 MCP_SERVERS（JSON），见 .env.example
"""
import argparse
import asyncio
from contextlib import suppress

from dotenv import load_dotenv
from langchain_core.load import dumps, loads
from langchain_core.messages import AIMessage, AnyMessage

from demo_agent.agent import build_agent
from demo_agent.hooks import DebugCallbackHandler

# 最多保留的历史消息条数（含中间的 ToolMessage 等），防止长对话超出上下文窗口
MAX_HISTORY_MESSAGES = 20

# 会话历史持久化文件（已加入 .gitignore）
CHAT_HISTORY_FILE = "chat_history.json"


def _trim_history(messages: list) -> list:
    """裁剪历史：只保留最近 MAX_HISTORY_MESSAGES 条，且以 AI 回答结尾。

    若裁剪后末尾残留未配对的中间消息（如 ToolMessage），继续向前丢弃，
    保证下一轮追加用户消息时历史是完整的消息对，而不是孤立的工具消息。
    """
    trimmed = messages[-MAX_HISTORY_MESSAGES:]
    while trimmed and not isinstance(trimmed[-1], AIMessage):
        trimmed.pop()
    return trimmed


async def _stream_chat(agent, messages: list) -> dict:
    """流式调用智能体：逐 token 打印 agent 回答，返回合并后的完整消息历史。

    stream_mode="messages" 返回 (消息块, 元数据) 序列；同一消息 id 的块
    用 merge() 合并成完整消息，供后续多轮记忆使用。
    """
    merged: dict[str, AnyMessage] = {}
    print("智能体: ", end="", flush=True)
    async for chunk, metadata in agent.astream(
        {"messages": messages},
        stream_mode="messages",
        config={"callbacks": [DebugCallbackHandler()]},
    ):
        # 只打印 agent 节点的文本增量；工具调用消息 content 为空，天然被跳过
        if metadata.get("langgraph_node") == "agent" and chunk.content and not chunk.tool_calls:
            print(chunk.content, end="", flush=True)
        if chunk.id in merged:
            merged[chunk.id] = merged[chunk.id].merge(chunk)
        else:
            merged[chunk.id] = chunk
    print()
    return {"messages": list(merged.values())}


def _save_history(messages: list) -> None:
    """把会话历史序列化到本地文件，供下次 --resume 恢复。"""
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as fh:
        fh.write(dumps(messages, pretty=True))


def _load_history() -> list:
    """从本地文件恢复会话历史；文件不存在或损坏时返回空列表。"""
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as fh:
            return loads(fh.read())
    except (FileNotFoundError, ValueError):
        return []


async def _ask(agent, messages: list, question: str) -> None:
    """把问题追加到会话，流式回答，历史写回会话并持久化。"""
    messages.append(("user", question))
    messages[:] = _trim_history((await _stream_chat(agent, messages))["messages"])
    _save_history(messages)


async def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Demo 智能体命令行入口")
    parser.add_argument("question", nargs="*", help="单次提问内容；缺省进入交互式对话")
    parser.add_argument("-r", "--resume", action="store_true", help="恢复上次会话历史")
    parser.add_argument(
        "-p",
        "--preset",
        default=None,
        help="提示词预设，可选: default / 翻译专家 / 编程助手 / 写作助手 / 数据分析师 / 英文助手 / 产品经理（缺省用 OPENAI_PRESET 或 default）",
    )
    args = parser.parse_args()

    agent = await build_agent(preset=args.preset)
    messages: list = _load_history() if args.resume else []

    if args.question:
        await _ask(agent, messages, " ".join(args.question))
        return

    if args.resume and messages:
        print(f"已恢复上次会话（{len(messages)} 条消息）。")
    print("Demo 智能体已就绪，输入问题开始对话（输入 exit / quit 退出）。")
    while True:
        try:
            question = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            break
        await _ask(agent, messages, question)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
