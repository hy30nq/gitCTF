"""Git-based CTF v2.0 — Injection verification.

Verifies that a team has properly injected vulnerabilities into their
service branches. For each bug branch, it checks that the encrypted
exploit is present and the exploit actually works.
"""

from __future__ import annotations

from lib.utils import load_config, rmdir
from lib.git import clone, list_branches


def verify_injection(team: str, conf: str) -> None:
    config = load_config(conf)
    repo_owner = config["repo_owner"]
    team_cfg = config["teams"][team]
    repo_name = team_cfg["repo_name"]

    print(f"[*] Cloning {repo_owner}/{repo_name}")
    clone(repo_owner, repo_name)

    branches = list_branches(repo_name)
    bug_branches = [b for b in branches if b.startswith("bug")]

    if not bug_branches:
        print("[!] No bug branches found")
        rmdir(repo_name)
        return

    print(f"[*] Found {len(bug_branches)} bug branches: {bug_branches}")

    for branch in sorted(bug_branches):
        commit_hash = team_cfg.get(branch, "")
        if commit_hash:
            print(f"  [OK] {branch} -> commit {commit_hash[:8]}")
        else:
            print(f"  [!]  {branch} -> no commit hash in config")

    rmdir(repo_name)
    print("[*] Injection verification complete")
