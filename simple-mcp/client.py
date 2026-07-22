import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

async def main():
    print("Starting MCP Client and connecting to Python Server...")
    
    # 1. Configure the MCP Transport to run our Python server
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "--with", "mcp", "--with", "httpx", server_path]
    )

    # Initialize Gemini
    client = genai.Client()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to MCP Server!\n")
            
            # 2. Get tools from MCP
            tools_response = await session.list_tools()
            
            # 3. Convert MCP Tools to Gemini Function Declarations
            gemini_tools = []
            for tool in tools_response.tools:
                # Map JSON Schema to Gemini Schema
                properties = {}
                for prop_name, prop_info in tool.inputSchema.get("properties", {}).items():
                    # Simplified type mapping
                    prop_type_str = prop_info.get("type", "string").upper()
                    if prop_type_str == "INTEGER" or prop_type_str == "NUMBER":
                        prop_type = types.Type.INTEGER
                    else:
                        prop_type = types.Type.STRING
                        
                    properties[prop_name] = types.Schema(
                        type=prop_type,
                        description=prop_info.get("description", "")
                    )
                
                gemini_tools.append(types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters=types.Schema(
                                type=types.Type.OBJECT,
                                properties=properties,
                                required=tool.inputSchema.get("required", [])
                            )
                        )
                    ]
                ))

            # 4. Start Chat Session
            chat = client.chats.create(
                model="gemini-1.5-pro",
                config=types.GenerateContentConfig(
                    tools=gemini_tools,
                    system_instruction="You are a helpful AI assistant. You have access to tools that can search Wikipedia and OpenStreetMap. Use them if the user asks for real-world locations or factual information.",
                    temperature=0.0,
                )
            )

            print("🤖 Gemini is ready! Ask it a question (type 'exit' to quit).")
            print("Example: 'Search for the Eiffel Tower coordinates and tell me its history.'\n")

            while True:
                try:
                    prompt = input("You: ")
                except EOFError:
                    break
                    
                if prompt.lower() == 'exit':
                    break
                
                print("Gemini is thinking... ", end="", flush=True)
                
                try:
                    response = chat.send_message(prompt)
                    
                    # 5. Handle Tool Calls
                    while response.function_calls:
                        call = response.function_calls[0]
                        print(f"\n⚙️  Gemini is using tool: [{call.name}] with args: {call.args}")
                        
                        # Execute the tool on the MCP Server
                        result = await session.call_tool(call.name, arguments=call.args)
                        
                        tool_result_text = ""
                        if result.content and len(result.content) > 0:
                            tool_result_text = result.content[0].text
                            
                        print(f"✅ Tool finished. Sending results back to Gemini...")
                        
                        # Send result back to Gemini
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name=call.name,
                                response={"result": tool_result_text}
                            )
                        )
                    
                    print(f"\nGemini: {response.text}\n")
                except Exception as e:
                    print(f"\nError communicating with Gemini: {e}\n")

if __name__ == "__main__":
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: Please export your GEMINI_API_KEY environment variable first!")
        sys.exit(1)
        
    asyncio.run(main())
