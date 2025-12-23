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
        # streamable_http_client는 (read, write, callback)을 반환
        read_stream, write_stream, _ = await self.exitStack.enter_async_context(
            streamable_http_client(self.serverUrl)
        )

        # ClientSession에는 read/write만 전달
        self.session = await self.exitStack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
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
    async def close(self):
        await self.exitStack.aclose()
        

async def main():
    client = MCPHttpClient("http://127.0.0.1:8000/mcp")
    await client.connect()

    result = await client.getCompetitionRate(
        "가야대학교",
        "간호학과",
    )

    print("\n📦 Tool response:")
    print(result)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())