#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Starting HomeNetSupervise installation...${NC}"

# Check Python version
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${GREEN}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -e .

# Create config directory
echo -e "${GREEN}Creating config directory...${NC}"
mkdir -p config

# Create example configuration
echo -e "${GREEN}Creating example configuration...${NC}"
cat > config/config.yaml << EOL
network:
  subnet: "192.168.178.0/24"  # Network to monitor
  scan_interval: 300          # Scan interval in seconds (5 minutes)
  port_scan_timeout: 1        # Timeout per port in seconds
  max_concurrent_scans: 10    # Maximum number of concurrent scans
EOL

echo -e "${GREEN}Installation completed!${NC}"
echo -e "Start the application with: ${GREEN}python backend.py${NC}"
echo -e "The application will be available at ${GREEN}http://localhost:8000${NC}" 