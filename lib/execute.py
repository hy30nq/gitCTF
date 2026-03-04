"""Git-based CTF v2.0 — Local Docker execution.

Run services and exploits in Docker containers on the local machine.
No server involved — everything runs on the participant's own machine.
"""

from __future__ import annotations

from lib.utils import run_command, docker_cleanup


def exec_service(service_name: str, service_dir: str,
                 host_port: str, service_port: str) -> None:
    print(f"[*] Building service image '{service_name}'")
    _, err, ret = run_command(
        f"docker build -t {service_name} .", service_dir
    )
    if ret != 0:
        print(f"[!] Docker build failed: {err}")
        return

    print(f"[*] Running service on port {host_port}:{service_port}")
    run_command(
        f"docker run -d --name {service_name} "
        f"-p {host_port}:{service_port} {service_name}"
    )
    print(f"[*] Service '{service_name}' is running")


def exec_exploit(service_name: str, exploit_dir: str,
                 ip: str, port: int, timeout: int) -> None:
    exploit_image = f"exploit-{service_name}"
    print(f"[*] Building exploit image '{exploit_image}'")
    _, err, ret = run_command(f"docker build -t {exploit_image} .", exploit_dir)
    if ret != 0:
        print(f"[!] Docker build failed: {err}")
        return

    container_name = f"exploit-{service_name}-run"
    print(f"[*] Running exploit against {ip}:{port} (timeout={timeout}s)")
    out, err, ret = run_command(
        f"timeout {timeout} docker run --rm --name {container_name} "
        f"--network host "
        f"{exploit_image} {ip} {port}"
    )
    if ret != 0:
        print(f"[!] Exploit failed: {err}")
    else:
        print(out)
