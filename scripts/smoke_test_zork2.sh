#!/usr/bin/env bash
set -e
PYTHON="${PYTHON:-python3}"
# Support running from project root (like smoke_test.sh) or from scripts/
GAME="${GAME:-../zork2/zork2/zork2.zil}"

if [ ! -f "$GAME" ]; then
    echo "SKIP: Zork II not found at $GAME"
    exit 0
fi

PASS=0
FAIL=0

check() {
    local desc="$1"
    local pattern="$2"
    local output="$3"
    if echo "$output" | grep -qi "$pattern"; then
        echo "  PASS: $desc"
        PASS=$((PASS+1))
    else
        echo "  FAIL: $desc (expected: $pattern)"
        echo "  Output snippet: $(echo "$output" | head -5)"
        FAIL=$((FAIL+1))
    fi
}

echo "=== Zork II Smoke Test ==="
OUTPUT=$(printf "quit\n" | "$PYTHON" -m zil_interpreter "$GAME" --json 2>&1)

check "Game loads (no crash)" "." "$OUTPUT"
check "Zork II in output" "ZORK" "$OUTPUT"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
