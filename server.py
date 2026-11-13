from mcp.server import MCPServer
import httpx
import os

mcp = MCPServer("Github_developer_assisstant")


def github_api_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_api_error(response: httpx.Response, resource: str) -> str:
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        return "GitHub API rate limit exceeded. Set GITHUB_TOKEN and restart the API."
    return f"Failed to fetch {resource} (HTTP {response.status_code}): {response.text}"


@mcp.tool(description="Get detailed information about a GitHub User profile, account, and public activity metadata.")
def get_github_user_info(username: str) -> dict:
    """Get detailed information about the GitHub User."""

    with httpx.Client() as client:
        response = client.get(
            f"https://api.github.com/users/{username}",
            headers=github_api_headers()
        )

    if response.status_code == 200:
        data = response.json()
        return {
            "login": data.get("login"),
            "id": data.get("id"),
            "node_id": data.get("node_id"),
            "user_view_type": data.get("user_view_type"),
            "name": data.get("name"),
            "company": data.get("company"),
            "blog": data.get("blog"),
            "location": data.get("location"),
            "email": data.get("email"),
            "bio": data.get("bio"),
            "twitter_username": data.get("twitter_username"),
            "public_repos": data.get("public_repos"),
            "public_gists": data.get("public_gists"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "hireable": data.get("hireable"),
            "avatar_url": data.get("avatar_url"),
            "url": data.get("url"),
            "html_url": data.get("html_url"),
            "type": data.get("type"),
            "site_admin": data.get("site_admin"),
            "followers_url": data.get("followers_url"),
            "following_url": data.get("following_url"),
            "repos_url": data.get("repos_url"),
            "gists_url": data.get("gists_url"),
            "starred_url": data.get("starred_url"),
            "subscriptions_url": data.get("subscriptions_url"),
            "organizations_url": data.get("organizations_url"),
            "events_url": data.get("events_url"),
            "received_events_url": data.get("received_events_url")
        }

    return {"error": github_api_error(response, "user information")}


@mcp.tool(description="Get detailed information about a user's public GitHub repositories.")
def get_github_user_repos(username: str) -> list:
    """Get detailed information about the User's GitHub Repositories."""

    with httpx.Client() as client:
        responses = client.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "sort": "updated"},
            headers=github_api_headers()
        )

    if responses.status_code == 200:
        repos = []

        for response in responses.json():
            repos.append({
                "id": response.get("id"),
                "node_id": response.get("node_id"),
                "name": response.get("name"),
                "full_name": response.get("full_name"),
                "owner": response.get("owner", {}).get("login"),
                "private": response.get("private"),
                "description": response.get("description"),
                "homepage": response.get("homepage"),
                "language": response.get("language"),
                "languages_url": response.get("languages_url"),
                "topics": response.get("topics"),
                "visibility": response.get("visibility"),
                "fork": response.get("fork"),
                "forks_count": response.get("forks_count"),
                "stargazers_count": response.get("stargazers_count"),
                "watchers_count": response.get("watchers_count"),
                "subscribers_count": response.get("subscribers_count"),
                "open_issues_count": response.get("open_issues_count"),
                "size": response.get("size"),
                "default_branch": response.get("default_branch"),
                "has_issues": response.get("has_issues"),
                "has_projects": response.get("has_projects"),
                "has_wiki": response.get("has_wiki"),
                "has_downloads": response.get("has_downloads"),
                "has_discussions": response.get("has_discussions"),
                "archived": response.get("archived"),
                "disabled": response.get("disabled"),
                "allow_forking": response.get("allow_forking"),
                "license": response.get("license", {}).get("name") if response.get("license") else None,
                "created_at": response.get("created_at"),
                "updated_at": response.get("updated_at"),
                "pushed_at": response.get("pushed_at"),
                "url": response.get("url"),
                "html_url": response.get("html_url"),
                "clone_url": response.get("clone_url"),
                "ssh_url": response.get("ssh_url"),
                "git_url": response.get("git_url"),
                "svn_url": response.get("svn_url"),
                "archive_url": response.get("archive_url"),
                "branches_url": response.get("branches_url"),
                "commits_url": response.get("commits_url"),
                "contents_url": response.get("contents_url"),
                "issues_url": response.get("issues_url"),
                "pulls_url": response.get("pulls_url"),
                "releases_url": response.get("releases_url"),
                "milestones_url": response.get("milestones_url"),
                "issue_comment_url": response.get("issue_comment_url"),
                "git_commits_url": response.get("git_commits_url")
            })

        return repos

    return {"error": github_api_error(responses, "user repositories")}


@mcp.tool(description="Get detailed information about pull requests in a GitHub repository.")
def get_user_pull_requests(repo: str, owner: str) -> list:
    """Get detailed information about the User's GitHub Pull Requests."""

    with httpx.Client() as client:
        responses = client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            params={"state": "all", "per_page": 100, "sort": "updated", "direction": "desc"},
            headers=github_api_headers()
        )

    if responses.status_code == 200:
        pull_requests = []

        for response in responses.json():
            pull_requests.append({
                "id": response.get("id"),
                "number": response.get("number"),
                "node_id": response.get("node_id"),
                "title": response.get("title"),
                "body": response.get("body"),
                "user": response.get("user", {}).get("login"),
                "author_association": response.get("author_association"),
                "state": response.get("state"),
                "draft": response.get("draft"),
                "locked": response.get("locked"),
                "html_url": response.get("html_url"),
                "url": response.get("url"),
                "diff_url": response.get("diff_url"),
                "patch_url": response.get("patch_url"),
                "issue_url": response.get("issue_url"),
                "head_ref": response.get("head", {}).get("ref"),
                "head_label": response.get("head", {}).get("label"),
                "head_sha": response.get("head", {}).get("sha"),
                "head_repo": response.get("head", {}).get("repo", {}).get("full_name") if response.get("head", {}).get("repo") else None,
                "base_ref": response.get("base", {}).get("ref"),
                "base_label": response.get("base", {}).get("label"),
                "base_sha": response.get("base", {}).get("sha"),
                "base_repo": response.get("base", {}).get("repo", {}).get("full_name") if response.get("base", {}).get("repo") else None,
                "created_at": response.get("created_at"),
                "updated_at": response.get("updated_at"),
                "closed_at": response.get("closed_at"),
                "merged_at": response.get("merged_at"),
                "merge_commit_sha": response.get("merge_commit_sha"),
                "merged": response.get("merged"),
                "assignee": response.get("assignee", {}).get("login") if response.get("assignee") else None,
                "assignees": [assignee.get("login") for assignee in response.get("assignees", [])],
                "requested_reviewers": [reviewer.get("login") for reviewer in response.get("requested_reviewers", [])],
                "requested_teams": [team.get("slug") for team in response.get("requested_teams", [])],
                "labels": [label.get("name") for label in response.get("labels", [])],
                "milestone": response.get("milestone", {}).get("title") if response.get("milestone") else None,
                "commits_url": response.get("commits_url"),
                "review_comments_url": response.get("review_comments_url"),
                "review_comment_url": response.get("review_comment_url"),
                "comments_url": response.get("comments_url"),
                "statuses_url": response.get("statuses_url"),
                "comments": response.get("comments"),
                "review_comments": response.get("review_comments"),
                "maintainer_can_modify": response.get("maintainer_can_modify"),
                "auto_merge": response.get("auto_merge")
            })

        return pull_requests

    return {"error": github_api_error(responses, "user pull requests")}


@mcp.tool(description="Get detailed information about issues in a GitHub repository.")
def get_user_issues(repo: str, owner: str) -> list:
    """Get detailed information about the User's GitHub Issues."""

    with httpx.Client() as client:
        responses = client.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            params={"state": "all", "per_page": 100, "sort": "updated", "direction": "desc"},
            headers=github_api_headers()
        )

    if responses.status_code == 200:
        issues = []

        for response in responses.json():

            # GitHub Issues endpoint also returns pull requests.
            if "pull_request" in response:
                continue

            issues.append({
                "id": response.get("id"),
                "node_id": response.get("node_id"),
                "number": response.get("number"),
                "title": response.get("title"),
                "body": response.get("body"),
                "user": response.get("user", {}).get("login"),
                "author_association": response.get("author_association"),
                "state": response.get("state"),
                "state_reason": response.get("state_reason"),
                "html_url": response.get("html_url"),
                "url": response.get("url"),
                "created_at": response.get("created_at"),
                "updated_at": response.get("updated_at"),
                "closed_at": response.get("closed_at"),
                "closed_by": response.get("closed_by", {}).get("login") if response.get("closed_by") else None,
                "assignee": response.get("assignee", {}).get("login") if response.get("assignee") else None,
                "assignees": [assignee.get("login") for assignee in response.get("assignees", [])],
                "labels": [label.get("name") for label in response.get("labels", [])],
                "milestone": response.get("milestone", {}).get("title") if response.get("milestone") else None,
                "comments": response.get("comments"),
                "locked": response.get("locked"),
                "active_lock_reason": response.get("active_lock_reason"),
                "reactions": response.get("reactions"),
                "performed_via_github_app": response.get("performed_via_github_app")
            })

        return issues

    return {"error": github_api_error(responses, "user issues")}


if __name__ == "__main__":
    mcp.run(transport="stdio")
