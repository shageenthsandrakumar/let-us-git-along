import os
import httpx

GITHUB_API = "https://api.github.com"

async def fetch_github_profile(username):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"token {token}"} if token else {}
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(f"{GITHUB_API}/users/{username}", headers=headers)
        if user_resp.status_code != 200:
            return {"error": f"User {username} not found"}
        user_data = user_resp.json()
        repos_resp = await client.get(f"{GITHUB_API}/users/{username}/repos", headers=headers, params={"sort": "updated", "per_page": 10})
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
        return {
            "username": username,
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "repos": [{"name": r["name"], "language": r.get("language"), "stars": r.get("stargazers_count", 0)} for r in repos_data[:10]],
        }

async def analyze_repo_patterns(username, repo_name):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"token {token}"} if token else {}
    async with httpx.AsyncClient() as client:
        commits_resp = await client.get(f"{GITHUB_API}/repos/{username}/{repo_name}/commits", headers=headers, params={"per_page": 30})
        commits = commits_resp.json() if commits_resp.status_code == 200 else []
        langs_resp = await client.get(f"{GITHUB_API}/repos/{username}/{repo_name}/languages", headers=headers)
        languages = langs_resp.json() if langs_resp.status_code == 200 else {}
        return {
            "repo": repo_name,
            "total_commits_sampled": len(commits),
            "commit_messages": [c.get("commit", {}).get("message", "")[:100] for c in commits[:10]],
            "languages": languages,
        }
