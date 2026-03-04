#!/usr/bin/env python3
"""
Git-based CTF v2.0

A fully distributed, serverless attack-and-defense CTF framework.
All data lives on GitHub. No dedicated server required.

Original authors: SeongIl Wi, Jaeseung Choi, Sang Kil Cha (KAIST)
v2.0 rewrite: Python 3.11+, modern APIs, enhanced security.

Licensed under the Apache License, Version 2.0
"""

import sys
import argparse

LOGO = r"""
   ___ _ _        _                        _     ___  _____  ___
  / _ (_) |_     | |__   __ _ ___  ___  __| |   / __\/__   \/ __\
 / /_\/ | __|____| '_ \ / _` / __|/ _ \/ _` |  / /     / /\/ _\
/ /_\\| | ||_____| |_) | (_| \__ \  __/ (_| | / /___  / / / /
\____/|_|\__|    |_.__/ \__,_|___/\___|\__,_| \____/  \/  \/
                                                        v2.0
"""


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--conf", default="config.json",
                        help="config file path (default: config.json)")
    parser.add_argument("--token", default=None,
                        help="GitHub personal access token (or set GITHUB_TOKEN env)")


def cmd_verify_service(args: argparse.Namespace) -> None:
    from lib.verify_service import verify_service
    verify_service(args.team, args.branch, args.service_port, args.host_port,
                   args.conf)


def cmd_verify_exploit(args: argparse.Namespace) -> None:
    from lib.verify_exploit import verify_exploit_cmd
    verify_exploit_cmd(args.exploit, args.service_dir, args.branch,
                       args.timeout, args.conf, args.encrypt)


def cmd_verify_injection(args: argparse.Namespace) -> None:
    from lib.verify_injection import verify_injection
    verify_injection(args.team, args.conf)


def cmd_submit(args: argparse.Namespace) -> None:
    from lib.submit import submit
    submit(args.exploit, args.service_dir, args.branch, args.target,
           args.conf, args.token)


def cmd_fetch(args: argparse.Namespace) -> None:
    from lib.fetch import fetch
    fetch(args.team, args.issue, args.conf, args.token)


def cmd_score(args: argparse.Namespace) -> None:
    from lib.show_score import show_score
    show_score(args.token, args.conf)


def cmd_eval(args: argparse.Namespace) -> None:
    from lib.evaluate import evaluate
    evaluate(args.conf, args.token, getattr(args, 'scan', False))


def cmd_hash(args: argparse.Namespace) -> None:
    from lib.get_hash import get_hash
    get_hash(args.conf, args.token)


def cmd_setup(args: argparse.Namespace) -> None:
    from lib.setup_env import setup_env
    setup_env(args.conf, args.token)


def cmd_exec_service(args: argparse.Namespace) -> None:
    from lib.execute import exec_service
    exec_service(args.service_name, args.service_dir,
                 args.host_port, args.service_port)


def cmd_exec_exploit(args: argparse.Namespace) -> None:
    from lib.execute import exec_exploit
    exec_exploit(args.service_name, args.exploit_dir,
                 args.ip, int(args.port), int(args.timeout))


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="gitctf",
        description="Git-based CTF v2.0 — Fully distributed CTF framework",
    )
    sub = root.add_subparsers(dest="command", help="available commands")

    # --- verify service ---
    p = sub.add_parser("verify-service", help="verify a team's service Docker builds and runs")
    p.add_argument("--team", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--host-port", default="4000")
    p.add_argument("--service-port", default="4000")
    add_common(p)
    p.set_defaults(func=cmd_verify_service)

    # --- verify exploit ---
    p = sub.add_parser("verify-exploit", help="verify an exploit against a service")
    p.add_argument("--exploit", required=True, metavar="DIR")
    p.add_argument("--service-dir", required=True, metavar="DIR")
    p.add_argument("--branch", required=True)
    p.add_argument("--timeout", required=True, type=int)
    p.add_argument("--encrypt", action="store_true", default=False)
    add_common(p)
    p.set_defaults(func=cmd_verify_exploit)

    # --- verify injection ---
    p = sub.add_parser("verify-injection", help="verify all injected vulnerabilities for a team")
    p.add_argument("--team", required=True)
    add_common(p)
    p.set_defaults(func=cmd_verify_injection)

    # --- submit ---
    p = sub.add_parser("submit", help="submit an encrypted exploit as a GitHub Issue")
    p.add_argument("--exploit", required=True, metavar="DIR")
    p.add_argument("--service-dir", required=True, metavar="DIR")
    p.add_argument("--branch", required=True)
    p.add_argument("--target", required=True, help="target team name")
    add_common(p)
    p.set_defaults(func=cmd_submit)

    # --- fetch ---
    p = sub.add_parser("fetch", help="fetch and decrypt an exploit from a GitHub Issue")
    p.add_argument("--team", required=True)
    p.add_argument("--issue", required=True, help="issue number")
    add_common(p)
    p.set_defaults(func=cmd_fetch)

    # --- score ---
    p = sub.add_parser("score", help="fetch score.csv from GitHub and display scoreboard")
    add_common(p)
    p.set_defaults(func=cmd_score)

    # --- eval ---
    p = sub.add_parser("eval", help="[instructor] poll GitHub notifications and auto-grade")
    p.add_argument("--scan", action="store_true", default=False,
                   help="one-shot scan mode: process all open exploit issues directly")
    add_common(p)
    p.set_defaults(func=cmd_eval)

    # --- hash ---
    p = sub.add_parser("hash", help="[instructor] get latest commit hash for each branch")
    add_common(p)
    p.set_defaults(func=cmd_hash)

    # --- setup ---
    p = sub.add_parser("setup", help="[instructor] setup CTF environment on GitHub")
    add_common(p)
    p.set_defaults(func=cmd_setup)

    # --- exec service ---
    p = sub.add_parser("exec-service", help="run a service in Docker locally")
    p.add_argument("--service-dir", required=True)
    p.add_argument("--service-name", required=True)
    p.add_argument("--host-port", default="4000")
    p.add_argument("--service-port", default="4000")
    p.set_defaults(func=cmd_exec_service)

    # --- exec exploit ---
    p = sub.add_parser("exec-exploit", help="run an exploit in Docker locally")
    p.add_argument("--exploit-dir", required=True)
    p.add_argument("--service-name", required=True)
    p.add_argument("--ip", default="127.0.0.1")
    p.add_argument("--port", default="4000")
    p.add_argument("--timeout", required=True, type=int)
    p.set_defaults(func=cmd_exec_exploit)

    return root


def main() -> None:
    if len(sys.argv) < 2:
        print(LOGO)

    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
