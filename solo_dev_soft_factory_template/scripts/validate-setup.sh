#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Validating Solo Software Factory Setup..."
echo ""

ERRORS=0
WARNINGS=0

check_port() {
    local port=$1
    local service=$2
    local env_var=$3
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗ Port $port ($service) is already in use${NC}"
        echo -e "  ${YELLOW}→ Set $env_var in .env to use a different port${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓ Port $port ($service) is available${NC}"
    fi
}

check_command() {
    local cmd=$1
    local desc=$2
    
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓ $desc is installed${NC}"
    else
        echo -e "${RED}✗ $desc is not installed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

check_file() {
    local file=$1
    local desc=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $desc exists${NC}"
    else
        echo -e "${YELLOW}⚠ $desc does not exist${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
}

echo "1️⃣  Checking required commands..."
check_command "docker" "Docker"
check_command "docker-compose" "Docker Compose"
check_command "node" "Node.js"
check_command "npm" "npm"
check_command "python3" "Python 3"
check_command "git" "Git"
echo ""

echo "2️⃣  Checking configuration files..."
check_file ".env" ".env file"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo -e "  ${YELLOW}→ Run: cp .env.example .env${NC}"
fi
check_file "apps/web/package.json" "Frontend package.json"
check_file "apps/api/requirements.txt" "Backend requirements.txt"
echo ""

echo "3️⃣  Checking port availability..."
if [ -f ".env" ]; then
    source .env
fi

API_PORT=${API_PORT:-8000}
WEB_PORT=${WEB_PORT:-3000}
REDIS_PORT=${REDIS_PORT:-6379}
DB_PORT=${DB_PORT:-5432}

check_port $API_PORT "API" "API_PORT"
check_port $WEB_PORT "Web" "WEB_PORT"
check_port $REDIS_PORT "Redis" "REDIS_PORT"
check_port $DB_PORT "PostgreSQL" "DB_PORT"
echo ""

echo "4️⃣  Checking Node.js dependencies..."
if [ -f "apps/web/package.json" ]; then
    if [ -d "apps/web/node_modules" ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend dependencies not installed${NC}"
        echo -e "  ${YELLOW}→ Run: cd apps/web && npm install${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗ Frontend package.json missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "5️⃣  Checking Python environment..."
if [ -f "apps/api/requirements.txt" ]; then
    if python3 -c "import fastapi" 2>/dev/null; then
        echo -e "${GREEN}✓ Python dependencies appear to be installed${NC}"
    else
        echo -e "${YELLOW}⚠ Python dependencies may not be installed${NC}"
        echo -e "  ${YELLOW}→ Run: cd apps/api && pip install -r requirements.txt${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Backend requirements.txt missing${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "6️⃣  Checking Docker status..."
if docker info &> /dev/null; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    echo -e "  ${YELLOW}→ Start Docker Desktop or Docker daemon${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✨ All checks passed! Ready to start development.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: make dev"
    echo "  2. Open: http://localhost:$WEB_PORT"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Setup has $WARNINGS warning(s) but should work.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Address warnings above (optional)"
    echo "  2. Run: make dev"
    echo "  3. Open: http://localhost:$WEB_PORT"
else
    echo -e "${RED}❌ Setup has $ERRORS error(s) that must be fixed.${NC}"
    echo ""
    echo "Please address the errors above before proceeding."
    exit 1
fi