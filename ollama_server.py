import requests
from requests.exceptions import RequestException

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Import Ollama functions for summarization
from ollama import chat, ChatResponse
from ollama import Client
client = Client()

# Create an MCP server instance with the identifier "wiki-summary"
mcp = FastMCP("Vulnerability-Incident-Response")

@mcp.tool()
def Create_Vulnerability_Incident_Response_Plan(vuln_summary: str) -> str:
    """
    Analyze the vulnerability search results and generate a corresponding Vulnerability Incident Response Plan.

    Usage:
        Create_Vulnerability_Incident_Response_Pla("Vulnerability Summary")
    """
    try:

        # Create the summarization prompt for Ollama
        prompt = f"Create a detailed incident response playbook for handling a {vuln_summary}"

        # Call the Ollama model to generate a summary
        client = Client(host='http://dgx08.its.albany.edu:8375')

        response: ChatResponse = client.chat(model='llama3.2:latest', messages=[
            {'role': 'user', 'content': prompt},
        ])
        summary = response.message.content.strip()
        return summary

    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e))) from e
    except RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Request error: {str(e)}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error: {str(e)}")) from e

# Set up the SSE transport for MCP communication.
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> None:
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())

# Create the Starlette app with two endpoints:
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8002)
