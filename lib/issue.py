"""Git-based CTF v2.0 — GitHub Issue operations.

Exploits are submitted as GitHub Issues to the target team's repo.
All scoring data ultimately derives from these Issues.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from lib.github_api import GitHub
from lib.utils import iso8601_to_timestamp


def create_label(repo_owner: str, repo_name: str, label_name: str,
                 color: str, desc: str, github: GitHub) -> None:
    query = f"/repos/{repo_owner}/{repo_name}/labels"
    data = json.dumps({"name": label_name, "description": desc, "color": color})
    github.post_quiet(query, data)


def update_label(repo_owner: str, repo_name: str, issue_no: int,
                 github: GitHub, label: str) -> None:
    query = f"/repos/{repo_owner}/{repo_name}/issues/{issue_no}"
    github.patch(query, json.dumps({"labels": [label]}))


def make_github_issue(repo_owner: str, repo_name: str, title: str,
                      body: str, github: GitHub) -> None:
    query = f"/repos/{repo_owner}/{repo_name}/issues"
    data = json.dumps({"title": title, "body": body})
    r = github.post(query, data, 201)
    if r is None:
        print(f'[!] Could not create issue "{title}"')
    else:
        print(f'[*] Successfully created issue "{title}"')


def get_github_issue(repo_owner: str, repo_name: str, issue_no: int,
                     github: GitHub) -> tuple[str, str, int, str]:
    query = f"/repos/{repo_owner}/{repo_name}/issues/{issue_no}"
    r = github.get(query)
    if r is None:
        print(f"[!] Could not get issue #{issue_no}")
        raise SystemExit(1)

    print(f"[*] Successfully obtained issue #{issue_no}")
    title = r["title"]
    submitter = r["user"]["login"]
    create_time = r["created_at"]
    content = r["body"]
    create_ts = int(iso8601_to_timestamp(create_time))
    return title, submitter, create_ts, content


def submit_issue(title: str, encrypted_exploit: str, target_team: str,
                 config: dict, github: GitHub) -> None:
    repo_owner = config["repo_owner"]
    repo_name = config["teams"][target_team]["repo_name"]

    with open(encrypted_exploit) as f:
        content = f.read().rstrip()

    make_github_issue(repo_owner, repo_name, title, content, github)


def is_closed(repo_owner: str, repo_name: str, issue_no: int,
              github: GitHub) -> bool:
    query = f"/repos/{repo_owner}/{repo_name}/issues/{issue_no}"
    r = github.get(query)
    if r is None:
        return True
    return r.get("closed_at") is not None


def create_comment(repo_owner: str, repo_name: str, issue_no: int,
                   comment: str, github: GitHub) -> None:
    query = f"/repos/{repo_owner}/{repo_name}/issues/{issue_no}/comments"
    github.post(query, json.dumps({"body": comment}), 201)


def close_issue(repo_owner: str, repo_name: str, issue_no: int,
                github: GitHub) -> None:
    query = f"/repos/{repo_owner}/{repo_name}/issues/{issue_no}"
    github.patch(query, json.dumps({"state": "closed"}))
