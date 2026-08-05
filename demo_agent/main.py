"""demo 智能体的命令行入口。

用法：
    python -m demo_agent.main "帮我算一下 (123 + 45) * 2"
    python -m demo_agent.main          # 进入交互式对话
    启用 MCP 工具：在 .env 中设置 MCP_SERVERS（JSON），见 .env.example
"""
import asyncio
import sys
from contextlib import suppress

from dotenv import load_dotenv

from demo_agent.agent import build_agent
from demo_agent.hooks import DebugCallbackHandler


async def _ask(agent, question: str) -> None:
    result = await agent.ainvoke(
        {"messages": [("user", question)]},
        config={"callbacks": [DebugCallbackHandler()]},
    )
    print("智能体:", result["messages"][-1].content)
    print()


async def main() -> None:
    load_dotenv()

    agent = await build_agent()

    if len(sys.argv) > 1:
        await _ask(agent, " ".join(sys.argv[1:]))
        return

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
        await _ask(agent, question)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
