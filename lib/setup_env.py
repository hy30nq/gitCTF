"""Git-based CTF v2.0 — Environment setup (instructor tool).

Creates team repositories on GitHub and configures them.
Uses the admin config (.config.json) for initial setup.
"""

from __future__ import annotations

import json
import sys

from lib.utils import load_config, resolve_token
from lib.github_api import GitHub


def setup_env(admin_conf: str, token: str | None = None) -> None:
    config = load_config(admin_conf)
    token = resolve_token(token)
    if not token:
        print("[!] Token is required for setup")
        sys.exit(1)

    github = GitHub(config.get("player", "instructor"), token)
    repo_owner = config["repo_owner"]

    print(f"[*] Setting up CTF environment for org: {repo_owner}")

    teams = config.get("teams", {})
    for team_name, team_info in teams.items():
        if team_name == "instructor":
            continue
        repo_name = team_info["repo_name"]
        print(f"\n[*] Creating repo {repo_owner}/{repo_name}")

        data = json.dumps({
            "name": repo_name,
            "private": True,
            "auto_init": True,
            "description": f"Git-based CTF - {team_name} service repository",
        })

        r = github.post(f"/orgs/{repo_owner}/repos", data)
        if r is None:
            print(f"  [*] Repo may already exist, skipping")
        else:
            print(f"  [*] Created successfully")

    print("\n[*] Setup complete")
    print("[*] Next steps:")
    print("  1. Add team members as collaborators to their repos")
    print("  2. Share config.json with all participants")
    print("  3. Share your GPG public key with all teams")
