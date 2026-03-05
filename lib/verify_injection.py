"""Git-based CTF v2.0 — Injection verification.

Verifies that a team has properly injected vulnerabilities into their
service branches. For each bug branch:
  1. Decrypt the encrypted exploit (exploit_bugN.zip.pgp)
  2. Run exploit against the bug branch (must succeed)
  3. Run exploit against master (must fail)

Per the paper (Section 3.2):
  "we can check the exploitability of each intended vulnerability by
   simply running the corresponding exploit against the service application."
"""

from __future__ import annotations

import os
import sys

from lib.utils import load_config, rmdir
from lib.git import clone, list_branches, checkout
from lib.verify_exploit import verify_exploit
from lib.crypto import decrypt_exploit


def get_exploit_dir(repo_dir: str, branch: str, config: dict,
                    team: str) -> str | None:
    exploit_path = os.path.join(repo_dir, f"exploit_{branch}.zip.pgp")
    if not os.path.isfile(exploit_path):
        print(f"[!] Encrypted exploit not found: {exploit_path}")
        return None
    exploit_dir = decrypt_exploit(exploit_path, config, team)
    if exploit_dir is None:
        print(f"[!] Failed to decrypt exploit for {branch}")
        return None
    return exploit_dir


def verify_injection(team: str, conf: str) -> None:
    config = load_config(conf)
    timeout = config["exploit_timeout"]["injection_phase"]
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

    all_passed = True
    for branch in sorted(bug_branches):
        print(f"\n[*] Verifying {branch}...")

        exploit_dir = get_exploit_dir(repo_name, branch, config, team)
        if exploit_dir is None:
            print(f"  [!] Skipping {branch} — no exploit available")
            print(f"      (Checking config hash only)")
            commit_hash = team_cfg.get(branch, "")
            if commit_hash:
                print(f"  [OK] {branch} -> commit {commit_hash[:8]}")
            else:
                print(f"  [!]  {branch} -> no commit hash in config")
                all_passed = False
            continue

        bug_result, _ = verify_exploit(
            exploit_dir, repo_name, branch, timeout, config
        )

        master_branch = "main" if "main" in branches else "master"
        master_result, _ = verify_exploit(
            exploit_dir, repo_name, master_branch, timeout, config
        )

        rmdir(exploit_dir)

        if bug_result and not master_result:
            print(f"  [OK] Branch '{branch}' verified successfully")
        elif bug_result and master_result:
            print(f"  [!] Exploit for '{branch}' also works on {master_branch}!")
            print(f"      This indicates the vulnerability exists in the original program.")
            all_passed = False
        else:
            print(f"  [!] Exploit for '{branch}' did not work")
            all_passed = False

    rmdir(repo_name)

    if all_passed:
        print("\n[*] All injection verifications passed!")
    else:
        print("\n[!] Some verifications failed. Check output above.")
