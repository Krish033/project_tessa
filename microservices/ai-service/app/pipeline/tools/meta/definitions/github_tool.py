import httpx
import subprocess
import shutil
from typing import Dict, Any, Optional


async def github(
    action: str = "repo_info",
    repo: Optional[str] = None,
    number: Optional[int] = None,
    state: str = "open"
) -> Dict[str, Any]:
    """Interact with GitHub API or gh CLI for issues, pull requests, and repository info.
    
    Args:
        action: 'repo_info', 'issue_list', 'pr_list', 'issue_view', or 'pr_view'.
        repo: Repository name in 'owner/repo' format (e.g. 'torvalds/linux').
        number: Optional issue or PR number.
        state: State filter ('open', 'closed', 'all').
    """
    gh_cli = shutil.which("gh")
    if gh_cli and repo:
        try:
            if action == "repo_info":
                res = subprocess.run([gh_cli, "repo", "view", repo, "--json", "name,description,stargazerCount,forkCount,url"], capture_output=True, text=True, timeout=15)
                if res.returncode == 0:
                    import json
                    return json.loads(res.stdout)
            elif action == "issue_list":
                res = subprocess.run([gh_cli, "issue", "list", "-R", repo, "--state", state, "--limit", "10", "--json", "number,title,author,createdAt,url"], capture_output=True, text=True, timeout=15)
                if res.returncode == 0:
                    import json
                    return {"repo": repo, "issues": json.loads(res.stdout)}
            elif action == "pr_list":
                res = subprocess.run([gh_cli, "pr", "list", "-R", repo, "--state", state, "--limit", "10", "--json", "number,title,author,createdAt,url"], capture_output=True, text=True, timeout=15)
                if res.returncode == 0:
                    import json
                    return {"repo": repo, "pull_requests": json.loads(res.stdout)}
        except Exception:
            pass

    # GitHub REST API fallback
    headers = {"User-Agent": "TessaAI/1.0", "Accept": "application/vnd.github.v3+json"}
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if not repo:
                return {"error": "Repository ('owner/repo') is required."}

            if action == "repo_info":
                url = f"https://api.github.com/repos/{repo}"
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return {
                    "name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "open_issues": data.get("open_issues_count"),
                    "url": data.get("html_url")
                }
            elif action == "issue_list":
                url = f"https://api.github.com/repos/{repo}/issues?state={state}&per_page=10"
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                issues = []
                for item in resp.json():
                    if "pull_request" not in item:
                        issues.append({
                            "number": item.get("number"),
                            "title": item.get("title"),
                            "author": item.get("user", {}).get("login"),
                            "url": item.get("html_url")
                        })
                return {"repo": repo, "issues": issues}
            elif action == "pr_list":
                url = f"https://api.github.com/repos/{repo}/pulls?state={state}&per_page=10"
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                prs = []
                for item in resp.json():
                    prs.append({
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "author": item.get("user", {}).get("login"),
                        "url": item.get("html_url")
                    })
                return {"repo": repo, "pull_requests": prs}
            else:
                return {"error": f"Unknown github action: '{action}'"}

    except Exception as e:
        return {"error": f"GitHub API error: {str(e)}"}
