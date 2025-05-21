"""
用户端 client
    调用大语言模型： 硅基流程替代openai client
    调用mcp服务端：mcp_server
"""
import asyncio
import json

import requests
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict


class UserClient:

    def __init__(self, script="mcp_server.py", model="Pro/deepseek-ai/DeepSeek-V3", url="https://api.siliconflow.cn/v1/chat/completions"):
        self.url = url
        self.model = model
        self.mcp_client = Client(script)
        self.openai_client = OpenAI(base_url='', api_key="None")
        self.messages = [
            {
                "role": "system",
                "content": "你是一个AI助手，你需要借助工具，回答用户问题。"
            }
        ]
        self.tools = []

    async def prepare_tools(self):
        tools = await self.mcp_client.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
            }
            for tool in tools
        ]
        return tools

    async def chat(self, messages: List[Dict]):
        if not self.tools:
            self.tools = await self.prepare_tools()

        payload = {
            "model": self.model,
            "stream": False,
            "max_tokens": 512,
            "enable_thinking": True,
            "thinking_budget": 4096,
            "min_p": 0.05,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "stop": [],
            "messages": messages,
            "tools": self.tools
        }
        headers = {
            "Authorization": "Bearer sk-xkmpyoaangdwwjirbwajaifivchxeqarueggkgaafnauikkd",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", self.url, json=payload, headers=headers)
        response_data = response.json()  # Parse the JSON response

        if response_data["choices"][0]["finish_reason"] != "tool_calls":
            # Normal message
            return response_data["choices"][0]["message"]

        for tool_call in response_data["choices"][0]["message"]["tool_calls"]:
            # MCP message
            tool_response = await self.mcp_client.call_tool(tool_call["function"]["name"],json.loads(tool_call["function"]["arguments"]))

            self.messages.append({
                "role": "assistant",
                "content": tool_response[0].text
            })

            print(self.messages)

            return await self.chat(self.messages)

    async def loop(self):
        async with self.mcp_client:
            while True:
                question = input("User: ")
                message = {
                    "role": "user",
                    "content": question
                }
                self.messages.append(message)
                response_message = await self.chat(self.messages)
                print("AI: ", response_message["content"])


async def main():
    user_client = UserClient()
    await user_client.loop()

if __name__ == '__main__':
    asyncio.run(main())