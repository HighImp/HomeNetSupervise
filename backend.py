from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
import yaml
from typing import List, Dict, Optional
import os
from scanner import check_services, inspect_target, autoscan_network
from pydantic import BaseModel
import asyncio
from fastapi.responses import StreamingResponse
import json
import subprocess
import re
from functools import lru_cache
from datetime import datetime, timedelta
import logging

app = FastAPI(title="HomeNetSupervise")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Cache für die ARP-Tabelle
arp_cache = {
    'table': {},
    'last_update': None,
    'update_interval': timedelta(minutes=5)
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Load OUI data from oui.json and normalize keys
with open('oui.json', 'r') as f:
    raw_oui_data = json.load(f)
    oui_data = {k.replace('-', '').upper(): v for k, v in raw_oui_data.items()}

# Log the first 10 OUI keys after loading
logging.info(f"First 10 OUI keys: {list(oui_data.keys())[:10]}")

async def update_arp_table():
    """Aktualisiere die ARP-Tabelle im Hintergrund."""
    global arp_cache
    try:
        result = subprocess.run(['arp-scan', '--localnet', '--quiet'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            new_table = {}
            for line in result.stdout.split('\n'):
                match = re.match(r'^(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f:]{17})', line.strip(), re.I)
                if match:
                    ip, mac = match.groups()
                    new_table[ip] = mac
            arp_cache['table'] = new_table
            arp_cache['last_update'] = datetime.now()
    except Exception:
        pass

def get_arp_table() -> tuple:
    """Run arp-scan --localnet and return a mapping IP->MAC and MAC->Vendor."""
    arp_table = {}
    vendor_table = {}
    try:
        result = subprocess.run(['arp-scan', '--localnet', '--quiet'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logging.info(f"ARP-Scan output: {result.stdout}")
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                # arp-scan output: IP MAC [Vendor]
                parts = line.strip().split()
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1]
                    vendor = ' '.join(parts[2:])
                    arp_table[ip] = mac
                    vendor_table[mac] = vendor[:20]  # Limit vendor to 20 chars
                    logging.info(f"Found vendor for {mac}: {vendor[:20]}")
                    logging.info(f"Found MAC address: {mac}, Manufacturer: {get_vendor(mac)}")
                    # Add additional logging for MAC address processing and OUI lookup
                    oui = mac.replace(':', '').upper()[:6]
                    logging.info(f"Processing MAC address: {mac}, OUI: {oui}, Manufacturer: {oui_data.get(oui, 'Not found')}")
                elif len(parts) == 2:
                    ip = parts[0]
                    mac = parts[1]
                    arp_table[ip] = mac
    except Exception as e:
        logging.error(f"Error in get_arp_table: {e}")
    logging.info(f"ARP table: {arp_table}")
    logging.info(f"Vendor table: {vendor_table}")
    return arp_table, vendor_table

def load_config() -> Dict:
    """Load configuration from YAML file."""
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            if not config:
                config = {}
    else:
        config = {}
    # Setze Defaults, falls Keys fehlen
    if 'services' not in config or config['services'] is None:
        config['services'] = []
    if 'devices' not in config or config['devices'] is None:
        config['devices'] = []
    if 'default_ports' not in config or config['default_ports'] is None:
        config['default_ports'] = [80, 443, 22, 21, 25, 1433, 3306, 5432, 27017]
    return config

def save_config(config: Dict):
    """Save configuration to YAML file."""
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f)

@app.get("/")
async def root():
    """Redirect to the web interface."""
    return RedirectResponse(url="/static/index.html")

@app.get("/status")
async def get_status():
    """Get status of all services."""
    config = load_config()
    services = config.get('services', [])
    # Sortiere nach IP
    def ip_key(s):
        return list(map(int, s.get('host', '0.0.0.0').split('.')))
    services_sorted = sorted(services, key=ip_key)
    return await check_services(services_sorted)

@app.get("/devices")
async def get_devices():
    """Get all devices with open ports count."""
    config = load_config()
    devices = config.get('devices', [])
    services = config.get('services', [])
    arp_table, vendor_table = get_arp_table()
    
    # Count open ports for each device
    for device in devices:
        device['open_ports'] = sum(1 for service in services if service['host'] == device['ip'])
        # Add vendor info to device
        mac = device.get('mac', '')
        vendor = get_vendor(mac)
        device['vendor'] = vendor
        logging.info(f"Device {device['ip']} with MAC {mac} has vendor: {vendor}")
    
    # Sort by IP
    def ip_key(d):
        return list(map(int, d.get('ip', '0.0.0.0').split('.')))
    return sorted(devices, key=ip_key)

@app.get("/config")
async def get_config():
    """Get the current configuration."""
    return load_config()

class InspectRequest(BaseModel):
    host: str
    ports: List[int]

@app.post("/inspect")
async def inspect_host(request: InspectRequest):
    """Manually inspect a host and its ports."""
    try:
        return await inspect_target(request.host, request.ports)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AutoscanRequest(BaseModel):
    subnet: str
    ports: List[int] = None

@app.post("/autoscan")
async def autoscan(request: Request):
    try:
        data = await request.json()
        subnet = data.get('subnet')
        ports = data.get('ports', [])
        
        if not subnet or not ports:
            raise HTTPException(status_code=400, detail="Subnet and ports are required")
        
        config = load_config()
        arp_table, vendor_table = get_arp_table()
        logging.info(f"Autoscan ARP table: {arp_table}")
        logging.info(f"Autoscan vendor table: {vendor_table}")

        found_services = []
        found_devices = []

        async def scan_progress():
            try:
                async for progress, result in autoscan_network(subnet, ports):
                    if result:
                        if isinstance(result, dict) and result.get("type") == "devices":
                            # Save found devices
                            for device in result["devices"]:
                                if not any(d.get('ip') == device['ip'] for d in config['devices']):
                                    device['mac'] = arp_table.get(device['ip'], '')
                                    logging.info(f"New device: {device}")
                                    config['devices'].append(device)
                                    found_devices.append(device)
                        else:
                            # Collect found services
                            found_services.append(result)
                    yield json.dumps({
                        "progress": progress,
                        "message": f"Scanning: {progress}%"
                    }) + "\n"
                # Nach dem Scan: Alle gefundenen offenen Ports als Dienste speichern
                new_services = 0
                for service in found_services:
                    if not any(s.get('host') == service['host'] and s.get('port') == service['port'] for s in config['services']):
                        config['services'].append(service)
                        new_services += 1
                save_config(config)
                # Extrahiere alle gefundenen Ports (unique, sortiert)
                found_ports = sorted({s['port'] for s in found_services})
                yield json.dumps({
                    "progress": 100,
                    "message": f"Scan abgeschlossen. {len(found_services)} offene Ports gefunden, {new_services} neue Dienste gespeichert.",
                    "services": found_services,
                    "devices": found_devices,
                    "found_ports": found_ports
                }) + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(scan_progress(), media_type="application/x-ndjson")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ServiceUpdate(BaseModel):
    name: str
    host: str
    port: int

@app.put("/service/{index}")
async def update_service(index: int, service: ServiceUpdate):
    """Update a service in the configuration."""
    config = load_config()
    if index < 0 or index >= len(config['services']):
        raise HTTPException(status_code=404, detail="Service not found")
    
    config['services'][index] = service.dict()
    save_config(config)
    return config['services'][index]

@app.delete("/service/{index}")
async def delete_service(index: int):
    """Delete a service from the configuration."""
    config = load_config()
    if index < 0 or index >= len(config['services']):
        raise HTTPException(status_code=404, detail="Service not found")
    
    deleted_service = config['services'].pop(index)
    save_config(config)
    return deleted_service

class DeviceUpdate(BaseModel):
    alias: str
    ip: str

@app.put("/device/{index}")
async def update_device(index: int, device: DeviceUpdate):
    """Update a device in the configuration."""
    config = load_config()
    if index < 0 or index >= len(config['devices']):
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_dict = device.dict()
    # Behalte die existierende MAC-Adresse
    device_dict['mac'] = config['devices'][index].get('mac', '')
    config['devices'][index] = device_dict
    save_config(config)
    return config['devices'][index]

@app.delete("/device/{index}")
async def delete_device(index: int):
    """Delete a device from the configuration."""
    config = load_config()
    if index < 0 or index >= len(config['devices']):
        raise HTTPException(status_code=404, detail="Device not found")
    
    deleted_device = config['devices'].pop(index)
    save_config(config)
    return deleted_device

@app.get("/export")
async def export_config():
    """Export devices and services in simplified format."""
    config = load_config()
    export_data = {
        'devices': [{'alias': d['alias'], 'ip': d['ip']} for d in config.get('devices', [])],
        'services': [{'name': s['name'], 'host': s['host'], 'port': s['port']} for s in config.get('services', [])]
    }
    return export_data

@app.post("/import")
async def import_config(request: Request):
    """Import devices and services from simplified format."""
    try:
        data = await request.json()
        config = load_config()
        
        # Import devices
        for device in data.get('devices', []):
            if not any(d['ip'] == device['ip'] for d in config['devices']):
                config['devices'].append({
                    'alias': device['alias'],
                    'ip': device['ip'],
                    'mac': ''  # MAC wird beim nächsten Autoscan aktualisiert
                })
        
        # Import services
        for service in data.get('services', []):
            if not any(s['host'] == service['host'] and s['port'] == service['port'] for s in config['services']):
                config['services'].append({
                    'name': service['name'],
                    'host': service['host'],
                    'port': service['port']
                })
        
        save_config(config)
        return {"message": "Import successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_vendor(mac: str) -> str:
    """Get vendor information using the oui.json file."""
    if not mac:
        return ""
    try:
        # Extract the first 6 characters of the MAC address (OUI)
        oui = mac.replace(':', '').replace('-', '').upper()[:6]
        vendor = oui_data.get(oui, "")
        logging.info(f"MAC: {mac}, OUI: {oui}, Vendor found: {vendor}")
        return vendor
    except Exception as e:
        logging.error(f"Error in get_vendor for MAC {mac}: {e}")
        return ""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 