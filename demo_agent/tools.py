"""demo 智能体用到的自定义工具。"""
import ast
import base64
import hashlib
import operator
import random
import re
import uuid
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


@tool
def count_words(text: str) -> int:
    """统计一段文字的字数：英文单词按空格分词，中文按字符计数。"""
    words = re.findall(r"[A-Za-z]+", text)
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return len(words) + cjk


@tool
def hash_text(text: str, algorithm: str = "sha256") -> str:
    """计算文本的哈希摘要，算法可选 sha256 / md5 / sha1。"""
    try:
        return hashlib.new(algorithm, text.encode("utf-8")).hexdigest()
    except ValueError as exc:
        return f"不支持的哈希算法: {exc}"


@tool
def base64_tool(text: str, mode: str = "encode") -> str:
    """对文本做 base64 编码（mode=encode）或解码（mode=decode）。"""
    try:
        if mode == "encode":
            return base64.b64encode(text.encode("utf-8")).decode("ascii")
        if mode == "decode":
            return base64.b64decode(text).decode("utf-8")
    except Exception as exc:  # noqa: BLE001 - demo 场景直接返回错误信息给模型
        return f"base64 {mode} 失败: {exc}"
    return "mode 只能是 encode 或 decode"


@tool
def random_number(min_value: int = 1, max_value: int = 100) -> int:
    """生成 [min_value, max_value] 区间内的随机整数，如 random_number(1, 6)。"""
    if min_value > max_value:
        return f"min_value 不能大于 max_value: {min_value} > {max_value}"
    return random.randint(min_value, max_value)


@tool
def random_choice(options: str) -> str:
    """从逗号分隔的选项里随机选一个，如 random_choice("石头,剪刀,布")。"""
    items = [item.strip() for item in options.split(",") if item.strip()]
    if not items:
        return "选项不能为空，请用逗号分隔多个选项"
    return random.choice(items)


@tool
def random_uuid() -> str:
    """生成一个随机 UUID（版本 4），如 "550e8400-e29b-41d4-a716-446655440000"。"""
    return str(uuid.uuid4())


@tool
def regex_match(text: str, pattern: str) -> bool:
    """判断 text 是否匹配正则 pattern（部分匹配即可），如 regex_match("abc123", r"[a-z]+\d+")。"""
    try:
        return re.search(pattern, text) is not None
    except re.error as exc:
        return f"正则表达式无效: {exc}"


@tool
def regex_search(text: str, pattern: str) -> list:
    """用正则 pattern 在 text 中查找所有匹配的子串，如 regex_search("a1 b22 c333", r"[a-z]\d+")。"""
    try:
        return re.findall(pattern, text)
    except re.error as exc:
        return f"正则表达式无效: {exc}"


@tool
def regex_replace(text: str, pattern: str, replacement: str) -> str:
    """用正则 pattern 在 text 中查找并替换为 replacement，替换所有匹配，如 regex_replace("a1 b2", r"\d", "#")。"""
    try:
        return re.sub(pattern, replacement, text)
    except re.error as exc:
        return f"正则表达式无效: {exc}"
