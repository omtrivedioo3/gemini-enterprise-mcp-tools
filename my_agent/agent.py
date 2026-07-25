import os
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# Fix for google-auth trying to use aiohttp for mTLS
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mcp-integration-503215"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-west1"

params = StreamableHTTPConnectionParams(url="https://gemini-enterprise-mcp-tools-ygbmijfr6q-uc.a.run.app/mcp")
mcp_toolset = McpToolset(
    connection_params=params, 
    tool_name_prefix="enterprise_mcp"
)

agent = Agent(
    name="my_agent",
    instruction="You are a helpful AI assistant connected to a set of MCP tools. Answer the user's questions by utilizing the tools.",
    tools=[mcp_toolset],
    model='gemini-2.5-flash'
)

from google.adk.apps import App
app = App(name="my_agent", root_agent=agent)
