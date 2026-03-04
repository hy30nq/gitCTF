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

if [ "${GRADER_MODE}" = "scan" ]; then
    echo "[*] Running one-shot scan..."
    python3 gitctf.py eval --scan --conf "${CONFIG_PATH:-config.json}"
else
    echo "[*] Starting continuous grading loop..."
    python3 gitctf.py eval --conf "${CONFIG_PATH:-config.json}"
fi
