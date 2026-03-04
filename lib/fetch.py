"""Git-based CTF v2.0 — Fetch exploit from GitHub Issue.

Downloads an encrypted exploit from a GitHub Issue and decrypts it locally.
"""

from __future__ import annotations

from lib.utils import load_config, rmdir, rmfile, mkdir, random_string, resolve_token
from lib.issue import get_github_issue
from lib.crypto import decrypt_exploit
from lib.github_api import GitHub


def fetch(team: str, issue_no: str, conf: str,
          token: str | None = None) -> None:
    config = load_config(conf)
    token = resolve_token(token)
    repo_owner = config["repo_owner"]
    repo_name = config["teams"][team]["repo_name"]
    github = GitHub(config["player"], token)

    _, submitter, create_time, content = get_github_issue(
        repo_owner, repo_name, int(issue_no), github
    )

    tmpfile = f"/tmp/gitctf_{random_string(6)}.issue"
    with open(tmpfile, "w") as f:
        f.write(content)

    out_dir = f"exploit-{submitter}-{create_time}"
    rmdir(out_dir)
    mkdir(out_dir)

    team_key = config["player_team"]
    out_dir = decrypt_exploit(tmpfile, config, team_key, out_dir, submitter)
    if out_dir is not None:
        print(f"[*] Exploit fetched into {out_dir}")

    rmfile(tmpfile)
