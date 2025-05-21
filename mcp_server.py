"""
1，创建 fastmcp实例
2，创建函数，添加文档
3，增加@mcp.tool注解
4，运行服务
"""

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def get_weather(city: str):
    """
    获取对应城市的天气
    :param city: 城市
    :return: 城市天气的描述
    """
    return f"{city}今天的天气暴雨， 29度"

if __name__ == '__main__':
    mcp.run()