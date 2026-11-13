# GitHub Developer Assistant

The MCP server exposes GitHub user profiles, repositories, pull requests, and
issues through the GitHub REST API.

Each tool returns the complete JSON object supplied by its endpoint instead of
selecting a subset of fields. Repository, pull request, and issue tools support
GitHub API pagination through `per_page` (up to 100) and `page`; use successive
page numbers to retrieve additional results.

The repository tool also supports GitHub's `type`, `sort`, and `direction`
filters. The pull request tool supports `state`, `head`, `base`, `sort`, and
`direction`. The issue tool supports `state`, `labels`, `sort`, `direction`,
`since`, `creator`, `assignee`, and `mentioned`. Optional filters can be left
unset.

GitHub HTTP errors are raised to the MCP caller with their status and response
details, rather than being returned as incomplete or empty results.