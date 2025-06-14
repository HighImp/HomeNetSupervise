#!/bin/bash

# Exit on error
set -e

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

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-venv arp-scan

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -e .

echo "Creating configuration directories..."
mkdir -p config network

echo "Creating default configuration files..."
cat > config/config.yaml << EOL
# Scan Configuration
# This file contains scan-related settings and network ranges

# Network ranges to scan
network_ranges:
  - "192.168.1.0/24"  # Default home network
  - "192.168.178.0/24"  # Alternative home network

# Default ports to scan
default_ports:
  - 80    # HTTP
  - 443   # HTTPS
  - 22    # SSH
  - 21    # FTP
  - 25    # SMTP
  - 1433  # MSSQL
  - 3306  # MySQL
  - 5432  # PostgreSQL
  - 27017 # MongoDB
  - 5000  # Common for web services
  - 8080  # Alternative HTTP port
  - 8443  # Alternative HTTPS port

# Scan settings
scan_settings:
  timeout: 2      # Timeout in seconds for port scans
  threads: 10     # Number of concurrent scan threads
  interval: 300   # Scan interval in seconds (5 minutes)
EOL

cat > network/network.yaml << EOL
# Network Configuration
# This file contains the list of devices and services in your network

devices:
  - alias: "Router"
    ip: "192.168.1.1"
    mac: ""
  - alias: "NAS"
    ip: "192.168.1.2"
    mac: ""
  - alias: "Printer"
    ip: "192.168.1.3"
    mac: ""

services:
  - name: "Router Web Interface"
    host: "192.168.1.1"
    port: 80
  - name: "NAS Web Interface"
    host: "192.168.1.2"
    port: 5000
  - name: "Printer Web Interface"
    host: "192.168.1.3"
    port: 80
EOL

echo -e "${GREEN}Installation completed!${NC}"
echo -e "Start the application with: ${GREEN}source venv/bin/activate && python backend.py${NC}"
echo -e "The application will be available at ${GREEN}http://localhost:8000${NC}" 