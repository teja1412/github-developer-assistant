# GitHub Developer Assistant

An MCP-based GitHub integration that exposes GitHub account information and repository activities as tools through the Model Context Protocol (MCP).

## Overview

GitHub Developer Assistant provides a standardized way for AI applications to interact with GitHub data through an MCP server.

Instead of implementing separate GitHub API integrations for every AI application, the project exposes reusable MCP tools that allow compatible MCP clients to retrieve user profiles, repositories, pull requests, and issues.

The server communicates with GitHub using the GitHub REST API and returns the requested information to the connected MCP client.

## Architecture

```text
        AI Application / MCP Host
                  |
                  |
              MCP Client
                  |
                  | STDIO Transport
                  |
              MCP Server
                  |
          GitHub Developer
              Assistant
                  |
             HTTPX Client
                  |
           GitHub REST API
                  |
        -----------------------
        |          |          |
      Users    Repositories  Issues
                   |
              Pull Requests
```

## Features

The MCP server currently exposes the following tools:

| Tool | Description |
|---|---|
| `get_github_user_info` | Retrieves GitHub user profile information. |
| `get_github_user_repos` | Retrieves repositories belonging to a GitHub user. |
| `get_user_pull_requests` | Retrieves pull requests for a specified repository and owner. |
| `get_user_issues` | Retrieves issues for a specified repository and owner. |

### Key Capabilities

- Exposes GitHub functionality through MCP tools.
- Integrates with GitHub REST APIs using HTTPX.
- Supports authenticated API requests using a GitHub Personal Access Token.
- Provides reusable tools that can be accessed by compatible MCP clients.
- Uses STDIO as the MCP communication transport.

## Technology Stack

- **Language:** Python
- **Protocol:** Model Context Protocol (MCP)
- **MCP SDK:** Python MCP SDK
- **API Integration:** GitHub REST API
- **HTTP Client:** HTTPX
- **Authentication:** GitHub Personal Access Token
- **Transport:** STDIO

## Configuration

### Prerequisites

- Python 3.13 or compatible project environment
- GitHub account
- GitHub Personal Access Token
- An MCP-compatible client

### Environment Variables

Configure the following environment variable:

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | GitHub Personal Access Token used for authenticated API requests. |

The server can also make requests without a token, subject to GitHub's unauthenticated API rate limits.

## Project Structure

```text
github-developer-assistant/
│
├── server.py
├── pyproject.toml
├── README.md
└── mcp-client/
```

## Running the Server

1. Clone the repository.
2. Set up the Python environment and install the dependencies declared in `pyproject.toml`.
3. Configure the `GITHUB_TOKEN` environment variable if authenticated access is required.
4. Start the MCP server using the project's server entry point.
5. Configure an MCP-compatible client to launch and communicate with the server over STDIO.

## Potential Enhancements

- Add more GitHub operations, such as branches, commits, and code search.
- Introduce configurable pagination and filtering for repository, issue, and pull request retrieval.
- Improve error handling and API response validation.
- Expand MCP client integration and documentation.
- Add automated tests for the exposed MCP tools.

