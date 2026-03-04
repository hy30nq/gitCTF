"""Git-based CTF v2.0 — Issue verification.

Per the paper (Section 3.3):
  "To evaluate an attack against intended vulnerabilities, we run the
   attack against p1, p2, ..., pk as well as the original program p.
   We then observe in which version the attack returns a valid flag.
   If the exploit works only on one of the modified programs, we can
   immediately identify which vulnerability has been attacked by the
   exploit. If the exploit works only on the original program, we
   consider it as an attack against an unintended vulnerability."

This module implements that exact algorithm:
  1. Clone the target repo
  2. Decrypt the submitted exploit
  3. Run exploit against each bug branch (p1..pk) AND master (p)
  4. Determine intended vs unintended based on results
"""

from __future__ import annotations

import os

from lib.utils import random_string, rmdir, rmfile, mkdir, load_config, print_and_log
from lib.git import clone, list_branches, get_latest_commit_hash, checkout
from lib.issue import get_github_issue
from lib.crypto import decrypt_exploit
from lib.verify_exploit import verify_exploit
from lib.github_api import GitHub

UNINTENDED = "unintended"


def _get_bug_branches(config: dict, defender: str) -> dict[str, str]:
    """Return {branch_name: commit_hash} for all bug branches of a team."""
    team_cfg = config["teams"].get(defender, {})
    bugs = {}
    for key, val in team_cfg.items():
        if key.startswith("bug") and val:
            bugs[key] = val
    return bugs


def verify_issue(defender: str, repo_name: str, issue_no: int,
                 config: dict, github: GitHub,
                 target_commit: str | None = None) -> tuple:
    """
    Verify an exploit submission against all versions of the service.

    Returns (vuln_type, commit, submitter, log) where:
      - vuln_type: "bug1", "bug2", etc. for intended, "unintended" for unintended, None for failure
      - commit: the commit hash of the exploited version
      - submitter: GitHub username of the attacker
      - log: detailed verification log
    """
    timeout = config["exploit_timeout"]["exercise_phase"]
    repo_owner = config["repo_owner"]
    log = ""

    title, submitter, create_time, content = get_github_issue(
        repo_owner, repo_name, issue_no, github
    )

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

    log = print_and_log(f"[*] Evaluating exploit from {submitter}: {title}", log)

    bug_branches = _get_bug_branches(config, defender)
    all_branches = list_branches(repo_name)

    # --- Run exploit against each bug branch (p1, p2, ..., pk) ---
    succeeded_on = []

    for branch_name in sorted(bug_branches.keys()):
        if branch_name not in all_branches:
            log = print_and_log(f"  [!] Branch '{branch_name}' not found in repo, skipping", log)
            continue

        log = print_and_log(f"  [*] Testing against {branch_name}...", log)
        success, log = verify_exploit(
            tmpdir, repo_name, branch_name, timeout, config, log=log
        )
        if success:
            commit = bug_branches[branch_name]
            succeeded_on.append((branch_name, commit))
            log = print_and_log(f"  [OK] Exploit works on {branch_name}", log)
        else:
            log = print_and_log(f"  [--] Exploit does NOT work on {branch_name}", log)

    # --- Run exploit against master/main (the original program p) ---
    master_branch = "main" if "main" in all_branches else "master"
    log = print_and_log(f"  [*] Testing against {master_branch} (original)...", log)

    master_commit = get_latest_commit_hash(repo_name, create_time, master_branch)
    master_success, log = verify_exploit(
        tmpdir, repo_name, master_branch, timeout, config, log=log
    )

    rmdir(tmpdir)
    rmdir(repo_name)

    # --- Determine intended vs unintended (paper algorithm) ---

    if not succeeded_on and not master_success:
        log = print_and_log("[!] Exploit did not work on any version", log)
        return None, None, submitter, log

    if len(succeeded_on) == 1 and not master_success:
        branch, commit = succeeded_on[0]
        log = print_and_log(
            f"[*] INTENDED vulnerability: {branch} (commit {commit[:8]})", log
        )
        return branch, commit, submitter, log

    if master_success and not succeeded_on:
        log = print_and_log(
            f"[*] UNINTENDED vulnerability (works on {master_branch} only)", log
        )
        return UNINTENDED, master_commit, submitter, log

    if master_success and succeeded_on:
        log = print_and_log(
            f"[*] UNINTENDED vulnerability (works on {master_branch} + "
            f"{[b for b,c in succeeded_on]})", log
        )
        return UNINTENDED, master_commit, submitter, log

    if len(succeeded_on) > 1:
        branch, commit = succeeded_on[0]
        log = print_and_log(
            f"[*] Exploit works on multiple bug branches: "
            f"{[b for b,c in succeeded_on]}. Counting as {branch}.", log
        )
        return branch, commit, submitter, log

    return None, None, submitter, log
