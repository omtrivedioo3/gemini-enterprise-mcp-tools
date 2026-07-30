# Enterprise MCP Agent Architecture

This repository contains a modular, Serverless AI architecture built completely independently of the Google Agent Development Kit (ADK). It leverages the pure `google.genai` SDK and the open-source Model Context Protocol (MCP), deeply integrated into the Gemini Enterprise (Vertex AI Agent Builder) UI.

## 🏗️ Architecture

1. **MCP Tool Server (`mcp_server.py`)**: A standard FastMCP server that exposes tools (Wikipedia, Math, GitHub). Completely decoupled from any LLM logic.
2. **Custom Gemini App (`mcp_client_app.py`)**: A standalone FastAPI Python backend client. It connects to the MCP server, processes user prompts using the Gemini 2.5 Flash model via the standard SDK, handles complex multi-tool execution loops, and returns clean JSON.
3. **Client UI (`client_ui.html`)**: A frontend user interface for interacting with the Custom Gemini App.
4. **Gemini Enterprise Playbook**: The Google Cloud enterprise front-end can natively connect to the MCP server to directly expose these tools to a Vertex AI agent.

## 🚀 Deployment Instructions

### 1. Deploy the MCP Server
```bash
gcloud run deploy gemini-enterprise-mcp-tools \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --command "uvicorn,mcp_server:app,--host,0.0.0.0,--port,8080"
```

### 2. Deploy the FastAPI App Client
```bash
gcloud run deploy gemini-enterprise-mcp-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --command "uvicorn,mcp_client_app:app,--host,0.0.0.0,--port,8080"
```
*(Note: Ensure you are authenticated and have the correct GCP project set up.)*

---

## 🔗 How to Integrate with Gemini Enterprise (Vertex AI Agent Builder)

Follow these exact steps to connect the **MCP Server** directly to Vertex AI Agent Builder.

### Step 1: Create the Agent
1. In the Google Cloud Console, search for **Agent Builder** (or Gemini Enterprise Agent Platform).
2. Go to **Apps** -> **Create App**.
3. Select **Agent** -> **Build your own**.
4. Give it a Display Name. **CRITICAL:** Set the Location to `us-central1`. Click Create.

### Step 2: Configure the MCP Tool
1. In your new Agent dashboard, click **Tools** on the left menu.
2. Click **Create Tool** -> **Model Context Protocol (MCP)** (if available in UI, otherwise follow standard MCP integration steps provided by Google Cloud).
3. Connect the tool directly to the Cloud Run URL of the deployed `gemini-enterprise-mcp-tools` service.
4. Ensure your agent is configured to use the MCP tools for its generated responses.

### Step 3: Configure the Playbook
1. Go to **Playbooks** on the left menu and click on the **Default Generative Playbook**.
2. **Goal:** Paste the following:
   > `You are an enterprise AI assistant. Your goal is to answer user questions using your MCP tools.`
3. **Available Tools:** At the bottom of the page, ensure the MCP tools are enabled.
4. Click **Save**.

### Step 4: Test & Publish!
1. Use the **Preview** chat on the right side of the screen to send a test message.
2. Once working, go to the **Integrations** tab to generate a Web Widget (Dialogflow Messenger) snippet, or connect it to Google Chat, Slack, or Microsoft Teams.

---
**Cost:** The entire backend is Serverless (Cloud Run scales to zero) and the Playbook has no hourly uptime fee. This architecture costs $0.00 when idle!
