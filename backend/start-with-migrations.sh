#!/bin/bash
# Wrapper script that runs migrations before starting the backend
# Use this with PM2 to ensure migrations are always applied

set -e

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

echo -e "${CYAN}=== Starting PMS Backend with Migrations ===${NC}"
echo -e "${GRAY}Backend directory: $BACKEND_DIR${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${GRAY}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d "env" ]; then
    echo -e "${GRAY}Activating virtual environment...${NC}"
    source env/bin/activate
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
if python -m alembic upgrade head; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
    echo ""
else
    echo -e "${RED}✗ Migration failed!${NC}"
    echo -e "${YELLOW}Backend will not start due to migration failure.${NC}"
    exit 1
fi

# Start the backend
echo -e "${YELLOW}Starting uvicorn server...${NC}"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
