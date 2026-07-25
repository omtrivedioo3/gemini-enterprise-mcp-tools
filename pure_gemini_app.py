import os
import asyncio
from google import genai
from google.genai import types

# 100% pure standard MCP Client (NO ADK!)
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mcp-integration-503215"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-west1"

MCP_SERVER_URL = "https://gemini-enterprise-mcp-tools-ygbmijfr6q-uc.a.run.app/mcp"

def mcp_to_gemini_tool(mcp_tools) -> types.Tool:
    """Converts standard MCP tool schemas into Google Gemini tool schemas."""
    function_declarations = []
    for t in mcp_tools:
        # In MCP, t.inputSchema is a dict representing the JSON schema
        decl = types.FunctionDeclaration(
            name=t.name,
            description=t.description or "",
            parameters=t.inputSchema 
        )
        function_declarations.append(decl)
    
    return types.Tool(function_declarations=function_declarations)

async def main():
    print("1. Connecting to Cloud Run MCP Server using open-source 'mcp' SDK...")
    
    # We use the streamable HTTP client to connect to Cloud Run (since Cloud Run proxies SSE + POST on one route)
    async with streamable_http_client(url=MCP_SERVER_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            print("2. Fetching tools from MCP server...")
            response = await session.list_tools()
            tools = response.tools
            
            print(f"Found {len(tools)} tools:")
            for t in tools:
                print(f" - {t.name}")
                
            # Convert tools to Gemini format
            gemini_tool = mcp_to_gemini_tool(tools)
            
            print("\n3. Sending Query to pure Gemini SDK...")
            client = genai.Client()
            
            prompt = "What is the capital of France?"
            print(f"\nUser Prompt: '{prompt}'")
            
            # Start a chat session with the tools
            chat = client.chats.create(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    tools=[gemini_tool],
                    temperature=0.2,
                )
            )
            
            res = chat.send_message(prompt)
            print("\n=== GEMINI RESPONSE ===")
            if res.text:
                print(res.text)
            
            # If Gemini decides it needs to use a tool to answer the prompt
            if res.function_calls:
                print("\n=== GEMINI REQUESTED TOOL EXECUTION ===")
                for call in res.function_calls:
                    print(f"Executing: {call.name}({call.args})")
                    
                    # Call the tool directly on the MCP server using the MCP SDK
                    result = await session.call_tool(call.name, arguments=call.args)
                    
                    # Extract the text content from the MCP result
                    tool_text = "".join([c.text for c in result.content if c.type == "text"])
                    print(f"\n=== RAW TOOL RESULT FROM CLOUD RUN ===\n{tool_text}")
                    
                    # Optionally, you can send the tool result back to Gemini so it can read it
                    # (This is how agents summarize data)
                    print("\n4. Handing tool data back to Gemini to summarize...")
                    final_res = chat.send_message(
                        types.Part.from_function_response(
                            name=call.name,
                            response={"result": tool_text}
                        )
                    )
                    
                    print("\n=== FINAL GEMINI ANSWER ===")
                    print(final_res.text)

if __name__ == "__main__":
    asyncio.run(main())
