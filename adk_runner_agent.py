import os
import asyncio
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
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

    print("2. Initializing ADK Agent with Memory Session...")
    agent = Agent(
        name="my_adk_agent",
        instruction="You are a helpful AI assistant connected to a set of MCP tools. Answer the user's questions by utilizing the tools. When tools are called, summarize their results.",
        tools=[mcp_toolset],
        model='gemini-2.5-flash'
    )
    
    # Use InMemorySessionService to satisfy Runner requirement
    session_service = InMemorySessionService()
    
    # Create the runner
    runner = Runner(
        agent=agent, 
        app_name="my_adk_agent", 
        session_service=session_service,
        auto_create_session=True
    )
    
    prompt = "Can you get the GitHub statistics for user: omtrivedioo3?"
    print(f"\n3. Sending Query: '{prompt}'\n")
    
    print("=== GEMINI'S RUNNER RESPONSE ===")
    
    from google.genai import types
    content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    # Runner automatically handles tool execution loop!
    async for event in runner.run_async(
        new_message=content, 
        user_id="test_user", 
        session_id="test_session"
    ):
        if event.content and hasattr(event.content, "parts") and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(part.text, end="", flush=True)
                elif hasattr(part, "function_call") and part.function_call:
                    print(f"\n[Agent Calling Tool]: {part.function_call.name}")
                elif hasattr(part, "function_response") and part.function_response:
                    print(f"\n[Tool Returned]: {str(part.function_response.response)[:100]}...\n")
    print("\n")

if __name__ == "__main__":
    asyncio.run(main())
