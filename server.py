import httpx
from fastmcp import FastMCP

mcp = FastMCP(
    name="EnterpriseAgent"
)

@mcp.tool()
async def search_wikipedia(query: str, limit: int = 5) -> str:
    """Search Wikipedia for a given query and return a list of matching article titles and snippets.
    
    Args:
        query: The search term (e.g., 'Quantum computing')
        limit: Maximum number of results to return (default: 5)
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "utf8": "1",
        "format": "json",
        "srlimit": limit
    }
    
    headers = {"User-Agent": "MCP-Wikipedia-Agent/1.0 (test@example.com)"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("query", {}).get("search", [])
        if not results:
            return f"No Wikipedia articles found for '{query}'."
            
        formatted_results = [f"Title: {res['title']}\nSnippet: {res['snippet']}..." for res in results]
        return "\n\n".join(formatted_results)

@mcp.tool()
async def get_wikipedia_summary(title: str) -> str:
    """Get the introductory summary extract of a specific Wikipedia article.
    
    Args:
        title: The exact title of the Wikipedia article (e.g., 'Python (programming language)')
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": "1",
        "titles": title,
        "format": "json",
        "explaintext": "1"
    }
    
    headers = {"User-Agent": "MCP-Wikipedia-Agent/1.0 (test@example.com)"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                return f"Error: The page '{title}' does not exist on Wikipedia."
            return page_data.get("extract", "No summary available.")
            
        return "Unknown error occurred while fetching the summary."



@mcp.tool()
async def get_github_user(username: str) -> str:
    """Get real-time statistics for a GitHub user (like followers and public repos). AI models do not have live GitHub data.
    
    Args:
        username: The GitHub username to look up
    """
    url = f"https://api.github.com/users/{username}"
    # GitHub requires a User-Agent header
    headers = {"User-Agent": "MCP-Testing-Agent/1.0 (test@example.com)"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)
        if response.status_code != 200:
            return f"Error: Could not find a GitHub user named '{username}'."
            
        data = response.json()
        repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        bio = data.get("bio", "No bio provided")
        name = data.get("name") or username
        
        return f"GitHub User {name}:\n- Public Repos: {repos}\n- Followers: {followers}\n- Bio: {bio}"

@mcp.tool()
async def get_current_time() -> str:
    """Get the exact current date and time in UTC. AI models do not have a built-in clock, so this tool provides the exact current time."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return f"The exact current date and time is: {now.strftime('%A, %B %d, %Y at %H:%M:%S UTC')}"

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: The first number
        b: The second number
    """
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first.
    
    Args:
        a: The number to subtract from
        b: The number to subtract
    """
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.
    
    Args:
        a: The first number
        b: The second number
    """
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> str:
    """Divide the first number by the second.
    
    Args:
        a: The numerator
        b: The denominator
    """
    if b == 0:
        return "Error: Cannot divide by zero."
    return str(a / b)

import asyncio
import os

if __name__ == "__main__":
    print(f"Starting MCP server on port {os.getenv('PORT', 8080)}")

    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
            path="/mcp",
        )
    )