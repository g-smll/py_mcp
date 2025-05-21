"""
1, 创建客户端
2，获取执行工具（资源，prompt）
3，执行工具
"""
import asyncio

from fastmcp import Client


async def run():
    client = Client('mcp_server.py')

    async with client:
        tools = await client.list_tools()

        tool = tools[0]
        result = await client.call_tool(tool.name, {"city": "云南"})
        print(result)


if __name__ == '__main__':
    asyncio.run(run())
