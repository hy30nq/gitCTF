#!/bin/sh
set -e

echo "=== Git-based CTF Grader ==="
echo "Mode: ${GRADER_MODE:-poll}"
echo "Config: ${CONFIG_PATH:-config.json}"

if [ ! -f "${CONFIG_PATH:-config.json}" ]; then
    echo "[!] Config file not found: ${CONFIG_PATH:-config.json}"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "[!] GITHUB_TOKEN is not set"
    exit 1
fi

export GITHUB_TOKEN

git config --global user.email "gitctf@local"
git config --global user.name "gitctf-grader"
git config --global credential.helper \
    "!f() { echo password=${GITHUB_TOKEN}; }; f"

echo "[*] Waiting for Docker (dind) to be ready..."
MAX_WAIT=30
WAITED=0
while ! docker info >/dev/null 2>&1; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ "$WAITED" -ge "$MAX_WAIT" ]; then
        echo "[!] Docker daemon not available after ${MAX_WAIT}s"
        exit 1
    fi
done
echo "[*] Docker daemon is ready"

export PYTHONUNBUFFERED=1

if [ "${GRADER_MODE}" = "scan" ]; then
    echo "[*] Running one-shot scan..."
    python3 -u gitctf.py eval --scan --conf "${CONFIG_PATH:-config.json}"
else
    echo "[*] Starting continuous grading loop..."
    python3 -u gitctf.py eval --conf "${CONFIG_PATH:-config.json}"
fi
