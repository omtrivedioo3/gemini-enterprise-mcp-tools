# Gemini Enterprise MCP Tools

This repository contains a custom **Model Context Protocol (MCP)** server built in Python. It acts as an "Omni Agent" that provides AI models (like Gemini) with external tools so they can perform tasks they natively cannot do, such as reading real-time data or performing complex math.

This project is specifically designed to be deployed to **Google Cloud Run** and integrated into **Gemini Enterprise via Vertex AI Extensions**.

## 🛠️ Tools Included

This single MCP server exposes **8 different tools** to the AI:

1. **`get_current_time`**: Allows the AI to know the exact atomic date and time (AI models do not have an internal clock).
2. **`get_github_user`**: Fetches live, real-time statistics (followers, repos, bio) for any GitHub user via the public GitHub API.
3. **`search_wikipedia`**: Searches Wikipedia and returns a list of matching article titles (The "Search" step).
4. **`get_wikipedia_summary`**: Reads the introductory paragraphs of a specific Wikipedia article (The "Read" step).
5. **`add`**: Adds two numbers together.
6. **`subtract`**: Subtracts two numbers.
7. **`multiply`**: Multiplies two numbers.
8. **`divide`**: Divides two numbers safely.

## 🚀 How to Test Locally

If you want to test the server locally on your machine, we use the visual **MCP Inspector**.

Run this command in the terminal at the root of the project:
```bash
npx @modelcontextprotocol/inspector uv run --with mcp --with httpx server.py
```
This will open a local web dashboard where you can manually click on the tools, provide arguments, and see the exact JSON outputs that Gemini would receive.

## ☁️ How to Deploy to Gemini Enterprise

Because Gemini Enterprise is a cloud platform, it cannot run local scripts on your laptop. You must deploy this server to the cloud.

### 1. Deploy the Code
This repository includes a `Dockerfile` that packages the Python server into a Web Server using Server-Sent Events (SSE). 
- Go to the **Google Cloud Console**.
- Navigate to **Cloud Run**.
- Click **Create Service** -> **Continuously deploy from a repository**.
- Link this GitHub repository. Cloud Run will automatically build the `Dockerfile` and give you a public URL (e.g., `https://your-agent.a.run.app`).

### 2. Update the OpenAPI Schema
- Open the `openapi.yaml` file in this repository.
- Replace the `- url: ...` placeholder on line 8 with your new Cloud Run URL.

### 3. Connect to Vertex AI
- In the Google Cloud Console, navigate to **Vertex AI > Agent Builder > Extensions**.
- Click **Create Extension**.
- Name it (e.g., "Enterprise Omni Tools") and upload your updated `openapi.yaml` file.
- Gemini Enterprise will instantly register the 8 tools and allow your workspace users to trigger them during chat!

## 📂 Project Structure

- `server.py`: The core Python logic using the `FastMCP` library. Contains all 8 tool definitions.
- `Dockerfile`: The instructions for Google Cloud Run on how to build and host the Web Server.
- `openapi.yaml`: The schema map required by Vertex AI to understand the structure of the tools.
- `client.py` *(Optional)*: A local Python script used for simulating how Gemini Enterprise routes tool calls under the hood.
