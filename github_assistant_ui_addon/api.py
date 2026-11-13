
import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mcpclient.client import Client, stdio_client, server_params, process_query


SERVER_SCRIPT_PATH = os.getenv("MCP_SERVER_PATH", "/Users/dharmateja/Downloads/Github_developer_assisstant_using_MCP/server.py")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start MCP server and establish the connection once
    async with Client(
        stdio_client(server_params(SERVER_SCRIPT_PATH))
    ) as client:
        app.state.mcp_client = client
        yield


app = FastAPI(
    title="GitHub Developer Assistant",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


def extract_tool_data(result):
    """Convert MCP tool result into JSON-compatible Python data."""
    if getattr(result, "structuredContent", None):
        return result.structuredContent

    content_items = []
    for item in getattr(result, "content", []):
        if hasattr(item, "text"):
            try:
                content_items.append(json.loads(item.text))
            except json.JSONDecodeError:
                content_items.append(item.text)

    if len(content_items) == 1:
        return content_items[0]
    return content_items


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/repos")
async def repositories(username: str = Query(...)):
    try:
        result = await app.state.mcp_client.call_tool(
            "get_github_user_repos",
            {"username": username}
        )
        return {"repositories": extract_tool_data(result)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/issues")
async def issues(owner: str, repo: str):
    try:
        result = await app.state.mcp_client.call_tool(
            "get_user_issues",
            {"owner": owner, "repo": repo}
        )
        return {"issues": extract_tool_data(result)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/pulls")
async def pull_requests(owner: str, repo: str):
    try:
        result = await app.state.mcp_client.call_tool(
            "get_user_pull_requests",
            {"owner": owner, "repo": repo}
        )
        return {"pull_requests": extract_tool_data(result)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        client = app.state.mcp_client

        answer = await process_query(
            client,
            request.message
        )

        return {"answer": answer}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
