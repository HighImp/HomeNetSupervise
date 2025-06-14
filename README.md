# HomeNetSupervise

A powerful network monitoring tool for home networks that automatically detects and monitors devices, services, and open ports.

## Features

- 🔍 Automatic network device detection
- 🌐 Port scanning and service monitoring
- 📊 Clear overview of all network devices and services
- 🔄 Real-time status monitoring
- 📱 Responsive web interface
- 🔐 MAC address detection and vendor identification
- 💾 Configuration import/export

## System Requirements

- Python 3.8 or higher
- Linux operating system (for ARP scanning)
- Network access to the subnet to be monitored

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HighImp/HomeNetSupervise.git
cd HomeNetSupervise
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the application:
```bash
python backend.py
```

5. Access the web interface:
```
http://localhost:8000
```

## Configuration

The application can be configured via the `config.yaml` file:

```yaml
# Example configuration
network:
  subnet: "192.168.178.0/24"  # Network to monitor
  scan_interval: 300          # Scan interval in seconds (5 minutes)
  port_scan_timeout: 1        # Timeout per port in seconds
  max_concurrent_scans: 10    # Maximum number of concurrent scans
```

## Usage

### Autoscan
1. Open the web interface
2. Navigate to the "Autoscan" section
3. Enter the subnet to scan (e.g., 192.168.178.0/24)
4. Select the ports to scan
5. Start the scan

### Single Device Scan
1. Select a device from the list
2. Click "Scan Ports"
3. Wait for the results

### Export/Import Configuration
1. Use the "Export Configuration" or "Import Configuration" buttons
2. Configuration will be saved/loaded as a JSON file

## Security Notes

- The application requires root privileges for ARP scanning
- Ensure only authorized users have access to the web interface
- Use HTTPS in production environments

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please create a Pull Request or open an Issue for suggestions.

## Support

For problems or questions:
1. Check the [Issues](https://github.com/HighImp/HomeNetSupervise/issues)
2. Create a new Issue if your problem is not documented 