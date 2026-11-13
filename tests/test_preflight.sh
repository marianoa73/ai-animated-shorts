#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
mkdir -p cache
tmp=$(mktemp -d "$PWD/cache/preflight.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/docker" <<'MOCK'
#!/bin/sh
[ "${DOCKER_FAIL:-0}" = 0 ]
MOCK
cat > "$tmp/uname" <<'MOCK'
#!/bin/sh
echo "${MOCK_ARCH:-x86_64}"
MOCK
cat > "$tmp/df" <<'MOCK'
#!/bin/sh
printf 'Filesystem 1024-blocks Used Available Capacity Mounted\n'
printf 'fake 99999999 0 %s 0%% .\n' "${MOCK_FREE:-99999999}"
MOCK
chmod +x "$tmp/"*
export PATH="$tmp:$PATH"
bash src/preflight.sh > "$tmp/result"
if MOCK_ARCH=aarch64 bash src/preflight.sh > "$tmp/result"; then exit 1; fi
if MOCK_FREE=100 bash src/preflight.sh > "$tmp/result"; then exit 1; fi
if DOCKER_FAIL=1 bash src/preflight.sh > "$tmp/result"; then exit 1; fi
echo 'OK: 4 preflight cases (pass, CPU, disk, Docker/Compose)'
