import os
import asyncio
from google import genai
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# Fix for google-auth trying to use aiohttp for mTLS
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mcp-integration-503215"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-west1"

async def main():
    print("1. Connecting directly to Cloud Run MCP Server...")
    params = StreamableHTTPConnectionParams(url="https://gemini-enterprise-mcp-tools-ygbmijfr6q-uc.a.run.app/mcp")
    mcp_toolset = McpToolset(
        connection_params=params, 
        tool_name_prefix="enterprise_mcp"
    )

    print("2. Fetching tools from the MCP server...")
    tools = await mcp_toolset.get_tools_with_prefix()
    
    print(f"Found {len(tools)} tools!")
    for t in tools:
        print(f" - {t.name}")

    # Extract the OpenAPI schemas from the MCP tools
    declarations = [t._get_declaration() for t in tools if t._get_declaration()]
    gemini_tool = types.Tool(function_declarations=declarations)
    
    print("\n3. Sending Query to Gemini...\n")
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Can you get the GitHub statistics for user: omtrivedioo3?",
        config=types.GenerateContentConfig(
            tools=[gemini_tool],
            temperature=0.2,
        )
    )
    
    print("\n=== GEMINI RESPONSE ===")
    if response.text:
        print(response.text)
    
    if response.function_calls:
        print("\n=== FUNCTION CALLS MADE BY GEMINI ===")
        session = await mcp_toolset._mcp_session_manager.create_session()
        for call in response.function_calls:
            print(f"Tool Used: {call.name}")
            print(f"Arguments: {call.args}")
            
            # Find the actual McpTool object
            matched_tool = next((t for t in tools if t.name == call.name), None)
            if matched_tool:
                print(f"Executing tool {call.name} directly on MCP server...")
                # Call underlying server directly
                result = await session.call_tool(
                    matched_tool.raw_mcp_tool.name, 
                    arguments=call.args
                )
                print("\n=== TOOL EXECUTION RESULT ===")
                print(result)

if __name__ == "__main__":
    asyncio.run(main())
