#!/bin/bash
# MediCare Clinic — macOS/Linux Server Launcher

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   MediCare Clinic — Backend Server           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python3 not found!${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  Install with: brew install python3"
    else
        echo "  Install with: sudo apt install python3 python3-pip"
    fi
    exit 1
fi
echo -e "${GREEN}[OK] Python3 found${NC}"

# Activate virtual environment
VENV_PATH="backend/venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo -e "${GREEN}[OK] Virtual environment activated${NC}"
else
    echo -e "${YELLOW}[WARN] No venv found. Run: python3 setup.py${NC}"
fi

# Start server
echo ""
echo -e "${GREEN}Starting MediCare Clinic server...${NC}"
echo -e "  ${CYAN}→ API:     http://127.0.0.1:8000/api/${NC}"
echo -e "  ${CYAN}→ Admin:   http://127.0.0.1:8000/admin/ (admin/admin123)${NC}"
echo -e "  ${YELLOW}→ Frontend: Open frontend/index.html in browser${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

cd backend
python manage.py runserver 0.0.0.0:8000
