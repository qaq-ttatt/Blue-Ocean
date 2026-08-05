"""智能体运行时的调试回调（hooks），在终端打印模型思考与工具调用过程。"""
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler


class DebugCallbackHandler(BaseCallbackHandler):
    """打印模型思考与工具调用过程的回调，方便观察 ReAct 的执行流程。"""

    def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs: Any) -> None:
        print("  ↳ 模型思考中…")

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
        name = serialized.get("name", "?")
        print(f"  ↳ 调用工具 {name}({input_str})")

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        print(f"  ↳ 工具返回: {output}")
