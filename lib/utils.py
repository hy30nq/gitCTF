"""Git-based CTF v2.0 — Utility functions."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import string
import subprocess
import sys
import time
from pathlib import Path

import dateutil.parser
import dateutil.tz


def random_string(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def rmdir(path: str | Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def rmfile(path: str | Path) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def mkdir(path: str | Path) -> None:
    os.makedirs(path, exist_ok=True)


def base_dir() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def project_root() -> str:
    return os.path.dirname(base_dir())


def run_command(cmd: str, cwd: str | None = None,
                timeout: int | None = None) -> tuple[str, str, int]:
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 124


def load_config(config_file: str) -> dict:
    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Cannot load configuration file {config_file}")
        print(repr(e))
        sys.exit(1)


def docker_cleanup(container_name: str) -> None:
    print(f"[*] Clean up container '{container_name}'")
    run_command(f"docker rm -f {container_name}")


def iso8601_to_timestamp(s: str) -> float:
    dt = dateutil.parser.parse(s)
    utc = dt.astimezone(dateutil.tz.tzutc())
    return utc.timestamp()


def is_timeover(config: dict) -> bool:
    return time.time() > iso8601_to_timestamp(config["end_time"])


def get_dirname(path: str) -> str:
    path = path.rstrip("/")
    idx = path.rfind("/")
    return path if idx == -1 else path[idx + 1:]


def print_and_log(msg: str, log: str | None = None) -> str | None:
    print(msg)
    if log is not None:
        log += msg + "\n"
    return log


def resolve_token(token: str | None) -> str | None:
    """Return token from argument or GITHUB_TOKEN env var."""
    if token:
        return token
    return os.environ.get("GITHUB_TOKEN")
