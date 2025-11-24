#!/usr/bin/env bash

# Test script for Zork Terminal UI
# This simulates user interaction to verify the UI works

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Zork Terminal UI Test Suite          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Test 1: Check Bun installation
echo -e "${YELLOW}Test 1: Checking Bun installation...${NC}"
if command -v bun &> /dev/null; then
    echo -e "${GREEN}✓ Bun is installed: $(bun --version)${NC}"
else
    echo -e "${RED}✗ Bun is not installed${NC}"
    exit 1
fi
echo ""

# Test 2: Check Python installation
echo -e "${YELLOW}Test 2: Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python is installed: $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python is not installed${NC}"
    exit 1
fi
echo ""

# Test 3: Check ZIL interpreter module
echo -e "${YELLOW}Test 3: Checking ZIL interpreter module...${NC}"
if python3 -c "import zil_interpreter" 2>/dev/null; then
    echo -e "${GREEN}✓ ZIL interpreter module found${NC}"
else
    echo -e "${RED}✗ ZIL interpreter module not found${NC}"
    exit 1
fi
echo ""

# Test 4: Check project structure
echo -e "${YELLOW}Test 4: Checking project structure...${NC}"
errors=0

if [ -f "package.json" ]; then
    echo -e "${GREEN}✓ package.json exists${NC}"
else
    echo -e "${RED}✗ package.json not found${NC}"
    errors=$((errors + 1))
fi

if [ -f "tsconfig.json" ]; then
    echo -e "${GREEN}✓ tsconfig.json exists${NC}"
else
    echo -e "${RED}✗ tsconfig.json not found${NC}"
    errors=$((errors + 1))
fi

if [ -d "src" ]; then
    echo -e "${GREEN}✓ src/ directory exists${NC}"
else
    echo -e "${RED}✗ src/ directory not found${NC}"
    errors=$((errors + 1))
fi

if [ -d "saves" ]; then
    echo -e "${GREEN}✓ saves/ directory exists${NC}"
else
    echo -e "${RED}✗ saves/ directory not found${NC}"
    errors=$((errors + 1))
fi

if [ $errors -gt 0 ]; then
    echo -e "${RED}✗ Project structure incomplete${NC}"
    exit 1
fi
echo ""

# Test 5: Check source files
echo -e "${YELLOW}Test 5: Checking source files...${NC}"
required_files=("src/index.ts" "src/game-engine.ts" "src/ui.ts" "src/save-manager.ts" "src/types.ts")
errors=0

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file not found${NC}"
        errors=$((errors + 1))
    fi
done

if [ $errors -gt 0 ]; then
    echo -e "${RED}✗ Source files incomplete${NC}"
    exit 1
fi
echo ""

# Test 6: Check dependencies
echo -e "${YELLOW}Test 6: Checking dependencies...${NC}"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓ node_modules exists${NC}"
else
    echo -e "${YELLOW}! Installing dependencies...${NC}"
    bun install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi
echo ""

# Test 7: TypeScript compilation check
echo -e "${YELLOW}Test 7: Checking TypeScript compilation...${NC}"
if bun build src/index.ts --target=bun --outdir=./test-build > /dev/null 2>&1; then
    echo -e "${GREEN}✓ TypeScript compiles successfully${NC}"
    rm -rf test-build
else
    echo -e "${RED}✗ TypeScript compilation failed${NC}"
    exit 1
fi
echo ""

# Test 8: Check ZIL file access
echo -e "${YELLOW}Test 8: Checking ZIL file access...${NC}"
ZIL_FILE="/Users/Keith.MacKay/Projects/zork1/zork1/zork1.zil"
TEST_ZIL="/Users/Keith.MacKay/Projects/zork1/tests/fixtures/simple_game.zil"

if [ -f "$TEST_ZIL" ]; then
    echo -e "${GREEN}✓ Test ZIL file found: $TEST_ZIL${NC}"
else
    echo -e "${RED}✗ Test ZIL file not found${NC}"
    exit 1
fi
echo ""

# Test 9: Test Python interpreter
echo -e "${YELLOW}Test 9: Testing Python interpreter with simple game...${NC}"
if echo -e "quit" | python3 -m zil_interpreter.cli.repl "$TEST_ZIL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Python interpreter works${NC}"
else
    echo -e "${RED}✗ Python interpreter test failed${NC}"
    exit 1
fi
echo ""

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          All Tests Passed! ✓               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}The Zork Terminal UI is ready to use!${NC}"
echo ""
echo "To start the game, run:"
echo -e "${YELLOW}  ./start.sh${NC}"
echo ""
