"""Git-based CTF v2.0 — Automated evaluation (instructor tool).

Polls GitHub Notifications for new exploit submissions (Issues),
verifies them locally via Docker, and pushes results to the
scoreboard repository on GitHub.

Per the paper: "instructors can run a script to fetch the submitted
attacks and evaluate them automatically."

No server. Just a loop: poll GitHub → clone → Docker verify → push score.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time

from lib.utils import (
    load_config, rmdir, rmfile, run_command, iso8601_to_timestamp,
    is_timeover, resolve_token,
)
from lib.github_api import GitHub, get_github_path
from lib.git import clone, get_next_commit_hash
from lib.issue import (
    is_closed, create_comment, close_issue,
    create_label, update_label, get_github_issue,
)
from lib.verify_issue import verify_issue

MSG_FILE = "msg"


def failure_action(repo_owner: str, repo_name: str, issue_no: int,
                   comment: str, noti_id: str, github: GitHub) -> None:
    create_label(repo_owner, repo_name, "failed", "000000",
                 "Verification failed.", github)
    update_label(repo_owner, repo_name, issue_no, github, "failed")
    create_comment(repo_owner, repo_name, issue_no, comment, github)
    close_issue(repo_owner, repo_name, issue_no, github)
    mark_as_read(noti_id, github)


def get_target_repos(config: dict) -> list[str]:
    return [config["teams"][t]["repo_name"] for t in config["teams"]]


def get_issues(target_repos: list[str], github: GitHub) -> tuple[list, int]:
    issues = []
    try:
        notifications, interval = github.poll("/notifications")
    except Exception:
        return [], 60

    for noti in reversed(notifications):
        if not noti.get("unread"):
            continue
        if noti["subject"]["type"] != "Issue":
            continue
        repo_name = noti["repository"]["name"]
        if repo_name not in target_repos:
            continue
        num = int(noti["subject"]["url"].split("/")[-1])
        noti_id = noti["url"].split("/")[-1]
        gen_time = iso8601_to_timestamp(noti["updated_at"])
        issues.append((repo_name, num, noti_id, gen_time))

    return issues, interval


def mark_as_read(noti_id: str, github: GitHub) -> None:
    github.patch(f"/notifications/threads/{noti_id}", None)


def get_defender(config: dict, target_repo: str) -> str | None:
    for team in config["teams"]:
        if config["teams"][team]["repo_name"] == target_repo:
            return team
    return None


def sync_scoreboard(scoreboard_dir: str) -> None:
    run_command("git reset --hard", scoreboard_dir)
    run_command("git pull", scoreboard_dir)


def write_score(stamp: float, info: dict, scoreboard_dir: str, pts: int) -> None:
    path = os.path.join(scoreboard_dir, "score.csv")
    with open(path, "a") as f:
        f.write(
            f"{stamp},{info['attacker']},{info['defender']},"
            f"{info['branch']},{info['bugkind']},{pts}\n"
        )


def write_message(info: dict, scoreboard_dir: str, pts: int) -> None:
    path = os.path.join(scoreboard_dir, MSG_FILE)
    with open(path, "w") as f:
        a, d, b, k = info["attacker"], info["defender"], info["branch"], info["bugkind"]
        f.write(f"[Score] {a} +{pts}\n\n")
        if pts == 0:
            f.write(f"{d} defended `{b}` {a} with {k}")
        else:
            f.write(f"{a} attacked `{b}` {k} of {d}")


def commit_and_push(scoreboard_dir: str) -> bool:
    _, _, r = run_command("git add score.csv", scoreboard_dir)
    if r != 0:
        print("[!] Failed to git add score.csv")
        return False
    _, _, r = run_command(f"git commit -F {MSG_FILE}", scoreboard_dir)
    if r != 0:
        print("[!] Failed to commit")
        return False
    _, _, r = run_command("git push origin master", scoreboard_dir)
    if r != 0:
        # Try main branch
        _, _, r = run_command("git push origin main", scoreboard_dir)
        if r != 0:
            print("[!] Failed to push score")
            return False
    rmfile(os.path.join(scoreboard_dir, MSG_FILE))
    return True


def find_last_attack(scoreboard_dir: str, timestamp: float,
                     info: dict) -> str | None:
    path = os.path.join(scoreboard_dir, "score.csv")
    if not os.path.isfile(path):
        return None
    last_commit = None
    with open(path) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if len(row) < 6:
                continue
            if int(float(row[0])) >= int(timestamp) and len(row[4]) == 40:
                if (row[1] == info["attacker"] and row[2] == info["defender"]
                        and row[3] == info["branch"]):
                    last_commit = row[4]
    return last_commit


def process_issue(repo_name: str, num: int, noti_id: str, config: dict,
                  gen_time: float, github: GitHub,
                  scoreboard: str) -> None:
    repo_owner = config["repo_owner"]

    if is_closed(repo_owner, repo_name, num, github):
        mark_as_read(noti_id, github)
        return

    create_label(repo_owner, repo_name, "eval", "DA0019",
                 "Exploit is under review.", github)
    update_label(repo_owner, repo_name, num, github, "eval")

    defender = get_defender(config, repo_name)
    if defender is None:
        print(f"[!] Unknown target repo: {repo_name}")
        return

    branch, commit, attacker, log = verify_issue(
        defender, repo_name, num, config, github
    )

    if branch is None:
        log_text = f"```\n{log}```"
        failure_action(repo_owner, repo_name, num,
                       log_text + "\n\n[*] The exploit did not work.",
                       noti_id, github)
        return

    if config["individual"].get(attacker, {}).get("team") == defender:
        failure_action(repo_owner, repo_name, num,
                       f"[*] Self-attack is not allowed: {attacker}",
                       noti_id, github)
        return

    create_label(repo_owner, repo_name, "verified", "9466CB",
                 "Successfully verified.", github)
    update_label(repo_owner, repo_name, num, github, "verified")

    info = {
        "attacker": attacker, "defender": defender,
        "branch": branch, "bugkind": commit,
    }

    sync_scoreboard(scoreboard)
    unintended_pts = config["unintended_pts"]
    write_score(gen_time, info, scoreboard, unintended_pts)
    write_message(info, scoreboard, unintended_pts)
    commit_and_push(scoreboard)
    mark_as_read(noti_id, github)


def prepare_scoreboard(url: str) -> str:
    path = get_github_path(url)
    parts = path.split("/")
    scoreboard_dir = ".score"
    clone(parts[0], parts[1], False, scoreboard_dir)
    return scoreboard_dir


def start_eval(config: dict, github: GitHub) -> None:
    target_repos = get_target_repos(config)
    scoreboard = prepare_scoreboard(config["score_board"])
    finalize = False

    while not finalize:
        if is_timeover(config):
            finalize = True

        issues, interval = get_issues(target_repos, github)
        if not issues:
            print(f"[*] No news. Sleep for {interval} seconds.")
            time.sleep(interval)
            continue

        print(f"[*] {len(issues)} new issues.")
        for repo, num, noti_id, gen_time in issues:
            process_issue(repo, num, noti_id, config, gen_time, github, scoreboard)

    print("[*] Time is over!")


def evaluate(conf: str, token: str) -> None:
    config = load_config(conf)
    token = resolve_token(token) or token
    if not token:
        print("[!] Token is required for eval")
        sys.exit(1)
    github = GitHub(config["player"], token)
    start_eval(config, github)
