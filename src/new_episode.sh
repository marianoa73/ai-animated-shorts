#!/usr/bin/env bash
set -eu
name=${1:-}
case "$name" in ''|*[!a-z0-9-]*|-*) echo 'Use a lowercase identifier: new_episode.sh my-episode'; exit 1;; esac
root=$(cd "$(dirname "$0")/.." && pwd)
[ ! -e "$root/episodes/$name" ] || { echo 'Episode already exists'; exit 1; }
mkdir "$root/episodes/$name"
cp "$root/episodes/example/script.json" "$root/episodes/$name/script.json"
echo "Created episodes/$name/script.json; edit it before generating."
