#!/usr/bin/env bash
set -eu
command -v docker >/dev/null || { echo 'FAIL: Docker is required'; exit 1; }
docker compose version >/dev/null || { echo 'FAIL: Docker Compose plugin is required'; exit 1; }
docker info >/dev/null 2>&1 || { echo 'FAIL: Docker daemon is not accessible'; exit 1; }
[ "$(uname -m)" = x86_64 ] || { echo 'FAIL: rendering requires x86_64 CPU'; exit 1; }
free_kb=$(df -Pk . | awk 'END {print $4}')
[ "$free_kb" -ge 26214400 ] || { echo 'FAIL: at least 25 GiB free disk required'; exit 1; }
ram_kb=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
if [ "$ram_kb" -lt 16777216 ]; then echo 'WARN: at least 16 GiB RAM recommended'; fi
echo 'OK: Docker, Compose, daemon, x86_64 and free disk'
