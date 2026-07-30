import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Environment variables for Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mcp-integration-503215"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-west1"

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8080/mcp")

app = FastAPI(
    title="Gemini Content Generator API",
    description="A custom pure-Gemini API that uses MCP tools."
)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("client_ui.html", "r") as f:
        return f.read()

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    used_tools: list[str] = []

def mcp_to_gemini_tool(mcp_tools) -> types.Tool:
    function_declarations = []
    for t in mcp_tools:
        decl = types.FunctionDeclaration(
            name=t.name,
            description=t.description or "",
            parameters=t.inputSchema 
        )
        function_declarations.append(decl)
    return types.Tool(function_declarations=function_declarations)

@app.post("/chat", response_model=ChatResponse)
async def generate_content(req: ChatRequest):
    print(f"==> Received prompt: {req.prompt}")
    used_tools = []
    
    # 1. Connect to Cloud Run MCP server
    async with streamable_http_client(url=MCP_SERVER_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            # 2. Fetch Tools
            response = await session.list_tools()
            gemini_tool = mcp_to_gemini_tool(response.tools)
            
            # 3. Send Request to Gemini
            client = genai.Client()
            chat = client.chats.create(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    tools=[gemini_tool],
                    temperature=0.2,
                )
            )
            
            res = chat.send_message(req.prompt)
            
            # 4. Handle Tool Execution (if Gemini asks for it)
            while res.function_calls:
                parts = []
                for call in res.function_calls:
                    print(f"==> Executing Tool: {call.name}({call.args})")
                    used_tools.append(call.name)
                    
                    tool_result = await session.call_tool(call.name, arguments=call.args)
                    tool_text = "".join([c.text for c in tool_result.content if c.type == "text"])
                    
                    parts.append(types.Part.from_function_response(
                        name=call.name,
                        response={"result": tool_text}
                    ))
                
                # Hand data back to Gemini
                res = chat.send_message(parts)
            
            final_text = res.text or "Error: No text response from model."
            print(f"==> Final Response: {final_text}\n")
            return ChatResponse(response=final_text, used_tools=used_tools)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
