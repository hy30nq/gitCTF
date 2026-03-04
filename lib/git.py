"""Git-based CTF v2.0 — Git operations.

All git operations happen locally — clone repos, checkout branches, read
commit history. No server involved.
"""

from __future__ import annotations

from lib.utils import run_command, rmdir


def clone(repo_owner: str, repo_name: str, is_private: bool = True,
          dest: str | None = None) -> None:
    target = dest or repo_name
    rmdir(target)
    import os
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        url = f"https://{token}@github.com/{repo_owner}/{repo_name}.git"
    elif is_private:
        url = f"git@github.com:{repo_owner}/{repo_name}.git"
    else:
        url = f"https://github.com/{repo_owner}/{repo_name}.git"
    _, err, ret = run_command(f"git clone {url} {target}")
    if ret != 0:
        print(f"[!] git clone failed: {err}")


def checkout(repo_dir: str, branch: str) -> None:
    run_command(f"git checkout -f {branch}", repo_dir)


def list_branches(repo_dir: str) -> list[str]:
    out, _, _ = run_command("git branch -r", repo_dir)
    branches = []
    for line in out.strip().split("\n"):
        line = line.strip()
        if "->" in line:
            continue
        if line.startswith("origin/"):
            branches.append(line[7:])
    return branches


def get_latest_commit_hash(repo_dir: str, before_time: str | int,
                           branch: str) -> str:
    """Get the latest commit hash on a branch before a given timestamp."""
    cmd = f'git log origin/{branch} --before="{before_time}" --format=%H -1'
    out, _, _ = run_command(cmd, repo_dir)
    return out.strip()


def get_next_commit_hash(repo_dir: str, branch: str,
                         after_hash: str) -> str:
    """Get the commit hash right after the given hash on a branch."""
    cmd = (f"git log origin/{branch} --reverse --format=%H "
           f"--ancestry-path {after_hash}..origin/{branch}")
    out, _, _ = run_command(cmd, repo_dir)
    lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
    return lines[0] if lines else ""
