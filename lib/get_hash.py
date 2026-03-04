"""Git-based CTF v2.0 — Get commit hashes (instructor tool).

Fetches the latest commit hash for each branch of each team's
repository via the GitHub API. Used by instructors to record the
injection phase state.
"""

from __future__ import annotations

from lib.utils import load_config, resolve_token
from lib.github_api import GitHub


def get_hash(conf: str, token: str | None = None) -> None:
    config = load_config(conf)
    token = resolve_token(token)
    github = GitHub(config["player"], token)
    repo_owner = config["repo_owner"]

    for team, info in config["teams"].items():
        if team == "instructor":
            continue
        repo_name = info["repo_name"]
        print(f"\n[*] {team} ({repo_name})")

        r = github.get(f"/repos/{repo_owner}/{repo_name}/branches")
        if r is None:
            print("  [!] Failed to fetch branches")
            continue

        for branch in r:
            name = branch["name"]
            sha = branch["commit"]["sha"]
            print(f"  {name:<20s} : {sha}")
