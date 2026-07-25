# Enterprise MCP Agent Architecture

This repository contains a modular, Serverless AI architecture built completely independently of the Google Agent Development Kit (ADK). It leverages the pure `google.genai` SDK and the open-source Model Context Protocol (MCP), deeply integrated into the Gemini Enterprise (Vertex AI Agent Builder) UI via OpenAPI.

## 🏗️ Architecture

1. **MCP Tool Server (`server.py`)**: A standard FastMCP server that exposes tools (Wikipedia, Math, GitHub). Completely decoupled from any LLM logic.
2. **Custom Gemini App (`fastapi_app.py`)**: A standalone FastAPI Python backend. It connects to the MCP server, processes user prompts using the Gemini 2.5 Flash model via the standard SDK, handles complex multi-tool execution loops, and returns clean JSON.
3. **Gemini Enterprise Playbook**: The Google Cloud enterprise front-end. It uses the `openapi.json` spec to seamlessly route user messages from the enterprise UI directly to the Custom Gemini App.

## 🚀 Deployment Instructions

### 1. Deploy the MCP Server
```bash
gcloud run deploy gemini-enterprise-mcp-tools \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --command "uvicorn,server:app,--host,0.0.0.0,--port,8080"
```

### 2. Deploy the FastAPI App
```bash
gcloud run deploy gemini-enterprise-mcp-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --command "uvicorn,fastapi_app:app,--host,0.0.0.0,--port,8080"
```
*(Note: Ensure you are authenticated and have the correct GCP project set up.)*

---

## 🔗 How to Integrate with Gemini Enterprise (Vertex AI Agent Builder)

Follow these exact steps to embed the custom FastAPI app into the Gemini Enterprise UI.

### Step 1: Prepare the OpenAPI Spec
1. Get the auto-generated OpenAPI spec from the FastAPI app (usually at `/openapi.json`).
2. Open `openapi.json` and make two manual modifications for Agent Builder compatibility:
   * **Downgrade Version:** Change `"openapi": "3.1.0"` to `"openapi": "3.0.0"`.
   * **Add Server URL:** Add the Cloud Run URL to the top level:
     ```json
     "servers": [
       {
         "url": "https://<YOUR_FASTAPI_CLOUD_RUN_URL>"
       }
     ]
     ```

### Step 2: Create the Agent
1. In the Google Cloud Console, search for **Agent Builder** (or Gemini Enterprise Agent Platform).
2. Go to **Apps** -> **Create App**.
3. Select **Agent** -> **Build your own**.
4. Give it a Display Name. **CRITICAL:** Set the Location to `us-central1`. Click Create.

### Step 3: Create the OpenAPI Tool
1. In your new Agent dashboard, click **Tools** on the left menu.
2. Click **Create Tool** -> **OpenAPI**.
3. **Name:** `CustomGeminiApp`
4. **Description:** "Custom Gemini Backend via REST API."
5. **Schema:** Paste your modified `openapi.json` into the JSON block.
6. **Authentication:** 
   * **Authentication Type:** Select `Service agent token`
   * **Service agent auth type:** Select `ID token`
7. Click **Save**.

### Step 4: Configure the Playbook
1. Go to **Playbooks** on the left menu and click on the **Default Generative Playbook**.
2. **Goal:** Paste the following:
   > `You are an enterprise AI assistant. Your goal is to answer user questions by routing them to the custom Gemini backend.`
3. **Instructions:** Paste the following markdown list:
   ```markdown
   - When a user asks a question, you MUST use the ${TOOL: CustomGeminiApp}.
   - Pass the user's message as the `prompt` parameter to the tool.
   - Take the `response` string returned by the tool and display it directly to the user.
   ```
4. **Available Tools:** At the bottom of the page, ensure the checkbox next to `CustomGeminiApp` is checked.
5. Click **Save**.

### Step 5: Test & Publish!
1. Use the **Preview** chat on the right side of the screen to send a test message.
2. Once working, go to the **Integrations** tab to generate a Web Widget (Dialogflow Messenger) snippet, or connect it to Google Chat, Slack, or Microsoft Teams.

---
**Cost:** The entire backend is Serverless (Cloud Run scales to zero) and the Playbook has no hourly uptime fee. This architecture costs $0.00 when idle!
