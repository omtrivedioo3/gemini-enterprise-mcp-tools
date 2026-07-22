# Use the official Python lightweight image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install standard dependencies for the MCP server
# We include uvicorn and starlette so it can run as a web server
RUN pip install --no-cache-dir mcp httpx uvicorn starlette sse-starlette

# Copy the server file into the container
COPY server.py /app/server.py

# Expose the port (Cloud Run defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Run the server script
CMD ["python", "server.py"]
