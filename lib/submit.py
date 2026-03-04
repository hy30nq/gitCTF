"""Git-based CTF v2.0 — Exploit submission.

Verifies the exploit locally, encrypts it with GPG, then submits it as
a GitHub Issue to the target team's repository. The entire attack
history is stored on GitHub.
"""

from __future__ import annotations

import sys

from lib.utils import load_config, rmfile, resolve_token
from lib.verify_exploit import verify_exploit
from lib.crypto import encrypt_exploit
from lib.issue import submit_issue
from lib.github_api import GitHub


def submit(exploit_dir: str, service_dir: str, branch: str,
           target: str, conf: str, token: str | None = None) -> None:
    config = load_config(conf)
    token = resolve_token(token)
    timeout = config["exploit_timeout"]["exercise_phase"]

    result, _ = verify_exploit(exploit_dir, service_dir, branch, timeout, config)
    if not result:
        print("[!] Your exploit did not work")
        sys.exit(1)

    print(f"[*] Exploit verified against branch '{branch}'")

    signer = config["player"]
    encrypted = encrypt_exploit(exploit_dir, target, config, signer)
    if encrypted is None:
        print("[!] Failed to encrypt exploit")
        sys.exit(1)

    issue_title = f"exploit-{branch}"
    github = GitHub(config["player"], token)
    submit_issue(issue_title, encrypted, target, config, github)

    rmfile(encrypted)
