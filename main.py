import asyncio
from typing import Optional
from contextlib import AsyncExitStack


from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPHttpClient:
    def __init__(self, serverUrl: str):
        self.serverUrl = serverUrl
        self.session: Optional[ClientSession] = None
        self.exitStack = AsyncExitStack()

    async def connect(self):
        # ✅ async context manager로 transport 열기
        transport = await self.exitStack.enter_async_context(
            streamable_http_client(self.serverUrl)
        )

        self.session = ClientSession(*transport)
        await self.session.initialize()

        tools = (await self.session.list_tools()).tools
        print("✅ Connected MCP tools:")
        for tool in tools:
            print(f"- {tool.name}")

    async def getCompetitionRate(self, univName: str, major: str):
        if not self.session:
            raise RuntimeError("MCP session not initialized")

        return await self.session.call_tool(
            "getCompetitionRateTool",
            {
                "univName": univName,
                "major": major,
            },
        )


async def main():
    client = MCPHttpClient("http://127.0.0.1:8000/mcp")
    await client.connect()

    result = await client.getCompetitionRate(
        "가천대학교",
        "경영학과",
    )

    print("\n📦 Tool response:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())