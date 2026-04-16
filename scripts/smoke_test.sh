#!/usr/bin/env bash
# Smoke test: run a quick Zork I play-through and verify basic output
set -e

PYTHON="${PYTHON:-python}"
GAME="zork1/zork1.zil"

if [ ! -f "$GAME" ]; then
    echo "ERROR: $GAME not found. Run from project root." >&2
    exit 1
fi

echo "Running smoke test..."

output=$(printf "look\nnorth\nopen mailbox\nquit\n" | "$PYTHON" -m zil_interpreter "$GAME" --json 2>&1)

if echo "$output" | grep -q "ZORK I"; then
    echo "PASS: Game title present"
else
    echo "FAIL: Game title missing" >&2
    echo "$output" >&2
    exit 1
fi

if echo "$output" | grep -q "West of House"; then
    echo "PASS: Starting room present"
else
    echo "FAIL: Starting room missing" >&2
    echo "$output" >&2
    exit 1
fi

if echo "$output" | grep -q "North of House"; then
    echo "PASS: Navigation works"
else
    echo "FAIL: Navigation not working" >&2
    echo "$output" >&2
    exit 1
fi

echo "All smoke tests passed."
