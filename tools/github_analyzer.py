import os
import httpx

GITHUB_API = "https://api.github.com"
TIMEOUT = 10.0

async def fetch_github_profile(username: str) -> dict:
    """Fetch a founder's GitHub profile and extract behavioral signals."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"token {token}"} if token else {}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Basic profile
        user_resp = await client.get(f"{GITHUB_API}/users/{username}", headers=headers)
        if user_resp.status_code != 200:
            return {"error": f"GitHub user '{username}' not found", "username": username}
        user = user_resp.json()

        # Repos — sorted by last updated, grab top 10
        repos_resp = await client.get(
            f"{GITHUB_API}/users/{username}/repos",
            headers=headers,
            params={"sort": "updated", "per_page": 10, "type": "owner"},
        )
        if repos_resp.status_code in (403, 429):
            # Rate-limited — surface this clearly so it isn't mistaken for "no repos"
            return {"error": f"GitHub rate limit hit for '{username}' (HTTP {repos_resp.status_code})", "username": username}
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        # Commit activity on most recently active repo
        commit_signals = {}
        if repos:
            top_repo = repos[0]["name"]
            commits_resp = await client.get(
                f"{GITHUB_API}/repos/{username}/{top_repo}/commits",
                headers=headers,
                params={"per_page": 30, "author": username},
            )
            if commits_resp.status_code == 200:
                commits = commits_resp.json()
                messages = [c.get("commit", {}).get("message", "")[:120] for c in commits[:10]]
                dates = [c.get("commit", {}).get("author", {}).get("date", "") for c in commits]
                commit_signals = {
                    "recent_repo": top_repo,
                    "commits_sampled": len(commits),
                    "recent_messages": messages,
                    "commit_dates": dates[:5],
                }

        # Language breakdown across repos
        lang_counts: dict[str, int] = {}
        for r in repos[:5]:
            lang = r.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        top_languages = sorted(lang_counts, key=lang_counts.get, reverse=True)[:5]

        # Account age signal
        created_at = user.get("created_at", "")

        return {
            "username": username,
            "name": user.get("name"),
            "bio": user.get("bio"),
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "account_created": created_at,
            "top_languages": top_languages,
            "repos": [
                {
                    "name": r["name"],
                    "language": r.get("language"),
                    "stars": r.get("stargazers_count", 0),
                    "forks": r.get("forks_count", 0),
                    "description": r.get("description", "")[:100] if r.get("description") else "",
                }
                for r in repos[:10]
            ],
            "commit_signals": commit_signals,
        }


async def analyze_repo_patterns(username: str, repo_name: str) -> dict:
    """Deep-dive commit pattern analysis for a specific repo."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"token {token}"} if token else {}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        commits_resp = await client.get(
            f"{GITHUB_API}/repos/{username}/{repo_name}/commits",
            headers=headers,
            params={"per_page": 30},
        )
        commits = commits_resp.json() if commits_resp.status_code == 200 else []

        langs_resp = await client.get(
            f"{GITHUB_API}/repos/{username}/{repo_name}/languages",
            headers=headers,
        )
        languages = langs_resp.json() if langs_resp.status_code == 200 else {}

        return {
            "repo": repo_name,
            "total_commits_sampled": len(commits),
            "commit_messages": [c.get("commit", {}).get("message", "")[:100] for c in commits[:10]],
            "languages": languages,
        }
