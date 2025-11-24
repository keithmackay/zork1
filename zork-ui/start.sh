#!/usr/bin/env bash

# Zork Terminal UI Launcher
# This script starts the Bun-based terminal UI for Zork

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Starting Zork Terminal Interface      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if Bun is installed
if ! command -v bun &> /dev/null; then
    echo -e "${RED}Error: Bun is not installed${NC}"
    echo ""
    echo "Install Bun with:"
    echo "  curl -fsSL https://bun.sh/install | bash"
    echo ""
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if ZIL interpreter is available
if ! python3 -c "import zil_interpreter" 2>/dev/null; then
    echo -e "${YELLOW}Warning: ZIL interpreter module may not be properly installed${NC}"
    echo "Make sure you're running from the correct directory"
    echo ""
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    bun install
    echo ""
fi

# Start the terminal UI
echo -e "${GREEN}Launching game...${NC}"
echo ""
bun run src/index.ts
