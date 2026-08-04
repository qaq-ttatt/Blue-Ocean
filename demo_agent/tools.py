"""demo 智能体用到的自定义工具。"""
import ast
import operator
from datetime import datetime

from langchain_core.tools import tool

# 允许在表达式里出现的运算，避免直接用 eval
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


@tool
def calculator(expression: str) -> float:
    """对四则算术表达式求值，如 "3 * 4 + 2"。仅支持数字与 + - * / // % ** 运算。"""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
    except Exception as exc:  # noqa: BLE001 - demo 场景直接返回错误信息给模型
        return f"表达式求值失败: {exc}"
    return result


def _safe_eval(node: ast.AST) -> float:
    """只允许白名单运算的安全求值器。"""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不支持的表达式节点: {type(node).__name__}")


@tool
def current_time() -> str:
    """返回当前的本地日期与时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
