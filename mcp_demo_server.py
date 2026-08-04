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


if __name__ == "__main__":
    mcp.run()
