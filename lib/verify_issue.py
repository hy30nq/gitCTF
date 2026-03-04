"""Git-based CTF v2.0 — Issue verification.

Fetches a GitHub Issue (exploit submission), decrypts it, and verifies
the exploit against the target service. All computation is local.
"""

from __future__ import annotations

import os

from lib.utils import random_string, rmdir, rmfile, mkdir, load_config
from lib.git import clone, list_branches, get_latest_commit_hash
from lib.issue import get_github_issue
from lib.crypto import decrypt_exploit
from lib.verify_exploit import verify_exploit
from lib.github_api import GitHub


def verify_issue(defender: str, repo_name: str, issue_no: int,
                 config: dict, github: GitHub,
                 target_commit: str | None = None) -> tuple:
    """Returns (branch, commit, submitter, log) or (None, None, submitter, log)."""
    timeout = config["exploit_timeout"]["exercise_phase"]
    repo_owner = config["repo_owner"]

    title, submitter, create_time, content = get_github_issue(
        repo_owner, repo_name, issue_no, github
    )

    # Issue title convention: "exploit-[branch_name]"
    target_branch = title[8:]

    clone(repo_owner, repo_name)

    tmpfile = f"/tmp/gitctf_{random_string(6)}.issue"
    tmpdir = f"/tmp/gitctf_{random_string(6)}.dir"

    with open(tmpfile, "w") as f:
        f.write(content)

    mkdir(tmpdir)
    result = decrypt_exploit(tmpfile, config, defender, tmpdir, submitter)
    rmfile(tmpfile)

    if result is None:
        rmdir(tmpdir)
        rmdir(repo_name)
        return None, None, submitter, "GPG decryption failed"

    branches = list_branches(repo_name)

    candidates = []
    if target_branch in branches and target_commit is None:
        commit = get_latest_commit_hash(repo_name, create_time, target_branch)
        candidates.append((target_branch, commit))

    verified_branch = None
    verified_commit = None
    log = f"About {title} (exploit-service branch)\n"

    for branch, commit in candidates:
        if branch in title:
            result, log = verify_exploit(
                tmpdir, repo_name, commit, timeout, config, log=log
            )
        else:
            result, _ = verify_exploit(
                tmpdir, repo_name, commit, timeout, config
            )

        if result:
            verified_branch = branch
            verified_commit = commit
            break

    rmdir(tmpdir)
    rmdir(repo_name)

    if verified_branch is None:
        print(f"[*] Exploit did not work against branch '{target_branch}'")
    else:
        print(f"[*] Exploit verified against branch '{verified_branch}'")

    return verified_branch, verified_commit, submitter, log
