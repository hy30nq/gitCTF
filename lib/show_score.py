"""Git-based CTF v2.0 — Scoreboard display.

Fetches score.csv from the GitHub scoreboard repository and computes
scores locally. Generates a score.html file with a time-series graph.
No server — just a script that reads from GitHub.

Per the paper: "students as well as instructors can run our script to
see the current scoreboard."
"""

from __future__ import annotations

import csv
import io
import os
import time
from string import Template

from lib.utils import load_config, iso8601_to_timestamp, is_timeover, resolve_token
from lib.github_api import GitHub, decode_content, get_github_path


def compute_score(score: dict, attacker: str, points: int) -> None:
    score[attacker] = score.get(attacker, 0) + points


def compute_unintended(start: float, end: float, freq: float,
                       pts: float) -> int:
    return int((end - start) / freq) * int(pts)


def update_deferred(score: dict, hist: dict, freq: float,
                    pts: float, end_time: str) -> None:
    now = time.time()
    end_ts = min(now, iso8601_to_timestamp(end_time))
    for attack_id, start_time in hist.items():
        attacker = attack_id.split("_")[0]
        p = compute_unintended(start_time, end_ts, freq, pts)
        compute_score(score, attacker, p)


def display_score(data: str, freq: float, unintended_pts: float,
                  end_time: str, pin_time: float | None = None) -> dict | None:
    reader = csv.reader(io.StringIO(data), delimiter=",")
    score: dict[str, int] = {}
    history: set[str] = set()
    unint_hist: dict[str, float] = {}

    for row in reader:
        if len(row) < 6:
            continue
        t = float(row[0])
        attacker, defender, branch, kind = row[1], row[2], row[3], row[4]
        points = int(row[5])
        attack_id = f"{attacker}_{defender}_{branch}"
        event_id = f"{attack_id}_{kind}"

        if pin_time is not None and t >= pin_time:
            break
        if event_id in history:
            continue
        history.add(event_id)

        if attack_id in unint_hist and points == 0:
            s = unint_hist[attack_id]
            p = compute_unintended(s, t, freq, unintended_pts)
            compute_score(score, attacker, p)
            unint_hist.pop(attack_id, None)
        else:
            unint_hist[attack_id] = t

    update_deferred(score, unint_hist, freq, unintended_pts, end_time)

    if pin_time is None:
        for team, pts in sorted(score.items(), key=lambda x: x[1], reverse=True):
            print(f"  {team:<20s}: {pts}")
        return None
    return score


def make_html(log: dict, config: dict) -> None:
    tmpl_path = os.path.join(os.path.dirname(__file__), "..", "templates",
                             "score.template")
    if not os.path.isfile(tmpl_path):
        # Use legacy template if available
        tmpl_path = os.path.join(os.path.dirname(__file__), "..",
                                 "_legacy", "score.template")
    if not os.path.isfile(tmpl_path):
        print("[*] score.template not found, skipping HTML generation")
        return

    with open(tmpl_path) as f:
        html = f.read()

    players = list(config.get("individual", {}).keys())
    col_var = ""
    for player in players:
        col_var += f'    data.addColumn("number","{player}");\n'

    graph_data = ""
    for key in sorted(log):
        graph_data += f"        [{key}, "
        for player in players:
            val = log[key].get(player, 0) if log[key] else 0
            graph_data += f"{val}, "
        graph_data = graph_data.rstrip(", ") + "],\n"

    s = Template(html)
    result = s.safe_substitute(column=col_var, data=graph_data)

    with open("score.html", "w") as f:
        f.write(result)
    print("[*] Generated score.html")


def show_score(token: str | None, conf: str) -> None:
    config = load_config(conf)
    token = resolve_token(token)
    scoreboard_url = config["score_board"]
    freq = float(config["round_frequency"])
    unintended_pts = float(config["unintended_pts"])
    end_time = config["end_time"]
    start_time = config["start_time"]

    path = get_github_path(scoreboard_url)
    g = GitHub(config["player"], token)

    if g.get(f"/repos/{path}") is None:
        print(f"[!] Cannot access scoreboard repo: {path}")
        return

    r = g.get(f"/repos/{path}/contents/score.csv")
    if r is None:
        print("[!] Cannot fetch score.csv")
        return

    csv_data = decode_content(r)
    print("[*] Current scoreboard:")
    display_score(csv_data, freq, unintended_pts, end_time)

    graph_start = int(iso8601_to_timestamp(start_time))
    graph_end = (
        int(iso8601_to_timestamp(end_time)) if is_timeover(config)
        else int(time.time())
    )

    log = {}
    hour = 0
    for i in range(graph_start, graph_end, 3600):
        log[hour] = display_score(csv_data, freq, unintended_pts, end_time, float(i))
        hour += 1

    make_html(log, config)
