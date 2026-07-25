import asyncio
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
import httpx

async def main():
    params = StreamableHTTPConnectionParams(url="https://gemini-enterprise-mcp-tools-ygbmijfr6q-uc.a.run.app/mcp")
    mcp_toolset = McpToolset(connection_params=params, tool_name_prefix="test")
    session = await mcp_toolset._mcp_session_manager.create_session()
    print("Connected successfully with ADK!")
    # let's see what session URL was negotiated
    # Actually wait, ADK's McpToolset probably uses mcp_client.sse under the hood!
    
if __name__ == "__main__":
    asyncio.run(main())
