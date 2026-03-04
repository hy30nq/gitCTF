"""Git-based CTF v2.0 — Service verification.

Clones a team's repo, checks out a branch, builds the Docker image,
and runs it to verify the service works. All local.
"""

from __future__ import annotations

from lib.utils import load_config, docker_cleanup, run_command, rmdir
from lib.git import clone, checkout


def verify_service(team: str, branch: str, service_port: str,
                   host_port: str, conf: str) -> None:
    config = load_config(conf)
    repo_owner = config["repo_owner"]
    repo_name = config["teams"][team]["repo_name"]
    container_name = f"{repo_name}-{branch}"

    print(f"[*] Cloning {repo_owner}/{repo_name}")
    clone(repo_owner, repo_name)

    print(f"[*] Checking out branch '{branch}'")
    checkout(repo_name, branch)

    print(f"[*] Building Docker image")
    _, err, ret = run_command(f"docker build -t {container_name} .", repo_name)
    if ret != 0:
        print(f"[!] Docker build failed:\n{err}")
        rmdir(repo_name)
        return

    print(f"[*] Running service on {host_port}:{service_port}")
    _, err, ret = run_command(
        f"docker run -d --name {container_name} "
        f"-p {host_port}:{service_port} {container_name}"
    )
    if ret != 0:
        print(f"[!] Docker run failed:\n{err}")
    else:
        print(f"[*] Service is running (container: {container_name})")
        print(f"[*] To stop: docker rm -f {container_name}")

    rmdir(repo_name)
