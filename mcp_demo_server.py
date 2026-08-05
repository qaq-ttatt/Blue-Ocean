"""一个最小的 stdio MCP 示例服务器，供 demo 智能体通过 MCP 协议调用。

由智能体按 MCP_SERVERS 配置自动拉起（stdio 子进程），无需手动启动：
    python mcp_demo_server.py
"""
import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-demo")

_CONDITIONS = ("晴", "多云", "小雨", "阴天", "雷阵雨")


@mcp.tool()
def get_weather(city: str) -> str:
    """返回指定城市的当前天气（演示数据，非真实预报）。"""
    return (
        f"{city}：{random.choice(_CONDITIONS)}，"
        f"{random.randint(15, 35)}°C，湿度 {random.randint(40, 90)}%"
    )


@mcp.tool()
def roll_dice(sides: int = 6) -> int:
    """掷一个指定面数的骰子（默认 6 面）。"""
    return random.randint(1, sides)


@mcp.tool()
def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """在摄氏度(C)、华氏度(F)、开尔文(K) 之间转换温度。

    示例: convert_temperature(25, "C", "F") -> 77.0
    """
    unit = from_unit.strip().upper()
    target = to_unit.strip().upper()
    if unit not in {"C", "F", "K"} or target not in {"C", "F", "K"}:
        raise ValueError("from_unit / to_unit 仅支持 C / F / K")
    kelvin = {"C": value + 273.15, "F": (value - 32) * 5 / 9 + 273.15, "K": value}[unit]
    return {"C": kelvin - 273.15, "F": kelvin * 9 / 5 - 459.67, "K": kelvin}[target]


if __name__ == "__main__":
    mcp.run()
