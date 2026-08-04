"""demo 智能体的命令行入口。

用法：
    python -m demo_agent.main "帮我算一下 (123 + 45) * 2"
    python -m demo_agent.main          # 进入交互式对话
"""
import sys

from dotenv import load_dotenv

from demo_agent.agent import build_agent


def _ask(agent, messages: list, question: str) -> None:
    """把问题追加到会话并调用智能体，回答写回会话（支持多轮记忆）。"""
    messages.append(("user", question))
    result = agent.invoke({"messages": messages})
    messages[:] = result["messages"]
    print("智能体:", messages[-1].content)
    print()


def main() -> None:
    load_dotenv()

    agent = build_agent()
    messages: list = []

    if len(sys.argv) > 1:
        _ask(agent, messages, " ".join(sys.argv[1:]))
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
        _ask(agent, messages, question)


if __name__ == "__main__":
    main()
