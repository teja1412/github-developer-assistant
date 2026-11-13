# GitHub Assistant UI add-on

This is a UI-only add-on. It does **not** replace or modify your MCP server.

## Added files
- `api.py` — FastAPI bridge to the MCP client
- `frontend/` — React + Vite chat UI

The frontend's Repositories, Issues, and Pull requests views load data from
`/api/repos`, `/api/issues`, and `/api/pulls`. You can search repositories by
GitHub username, then open issues or pull requests for a selected repository.

## Run the UI
Run the API from the repository root so Python can resolve the sibling `mcpclient/`
directory. The root `uv` project installs the MCP client dependencies, including
`google-genai`.

Terminal A (API, from the repository root):
```bash
uv sync
uv run uvicorn github_assistant_ui_addon.api:app --reload --port 8000
```

Terminal B (frontend):
```bash
cd github_assistant_ui_addon/frontend
npm install
npm run dev
```

Set `GENAI_API_KEY` for the Gemini client, then open http://localhost:5173.
If GitHub's unauthenticated API rate limit is exceeded, set `GITHUB_TOKEN` in
the API terminal before starting Uvicorn; the MCP server uses it for authenticated
GitHub API requests.
