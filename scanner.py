import asyncio
from typing import List, Dict, AsyncGenerator, Tuple, Optional
from async_lru import alru_cache
import ipaddress
import re
import subprocess
import socket

async def ping_host(host: str, timeout: float = 1.0) -> bool:
    """Ping a host and return True if successful."""
    try:
        process = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', host,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(process.communicate(), timeout=timeout)
        return process.returncode == 0
    except (asyncio.TimeoutError, Exception):
        return False

async def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return False

async def check_services(services: List[Dict]) -> List[Dict]:
    """Check the status of multiple services."""
    results = []
    for service in services:
        name = service.get('name', 'Unknown')
        host = service.get('host', '')
        port = service.get('port', 0)
        port_result = await check_port(host, port) if port > 0 else False
        results.append({
            'name': name,
            'host': host,
            'port': port,
            'port_open': port_result
        })
    return results

async def inspect_target(host: str, ports: List[int]) -> Dict:
    """Manually inspect a target host and its ports."""
    if not host or not ports:
        raise ValueError("Host and ports are required")
    ping_result = await ping_host(host)
    port_results = {}
    for port in ports:
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError(f"Invalid port number: {port}")
        port_results[port] = await check_port(host, port)
    return {
        'host': host,
        'ping': ping_result,
        'ports': port_results
    }

async def get_mac_address(ip: str) -> str:
    """Get MAC address for an IP using arp."""
    try:
        process = await asyncio.create_subprocess_exec(
            'arp', '-n', ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            # Parse arp output to get MAC address
            output = stdout.decode()
            match = re.search(r'([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})', output)
            if match:
                return match.group(1)
    except Exception:
        pass
    return "Unknown"

async def get_dns_name(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""

async def autoscan_network(subnet: str, ports: List[int]) -> AsyncGenerator[Tuple[int, Optional[Dict]], None]:
    """Scan a subnet for hosts and check ports in parallel."""
    try:
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$', subnet):
            raise ValueError("Invalid subnet format. Use CIDR notation (e.g., 192.168.1.0/24)")
        network = ipaddress.ip_network(subnet, strict=False)
        hosts = [str(ip) for ip in network.hosts()]
        total_hosts = len(hosts)
        found_services = []
        found_devices = []

        async def ping_and_ports(ip):
            if await ping_host(ip):
                mac = await get_mac_address(ip)
                dns = await get_dns_name(ip)
                found_devices.append({
                    "alias": f"Unknown Device ({ip})",
                    "mac": mac,
                    "ip": ip,
                    "dns": dns
                })
                port_tasks = [check_port(ip, port) for port in ports]
                port_results = await asyncio.gather(*port_tasks)
                services = []
                for port, is_open in zip(ports, port_results):
                    if is_open:
                        services.append({
                            "name": f"Unknown Service ({ip}:{port})",
                            "host": ip,
                            "port": port
                        })
                return services
            return []

        tasks = [ping_and_ports(ip) for ip in hosts]
        for idx, coro in enumerate(asyncio.as_completed(tasks), 1):
            services = await coro
            found_services.extend(services)
            progress = int((idx / total_hosts) * 100)
            for service in services:
                yield progress, service
            if not services:
                yield progress, None

        # Sortiere Geräte nach IP
        found_devices.sort(key=lambda d: list(map(int, d['ip'].split('.'))))
        yield 100, {"type": "devices", "devices": found_devices}

    except Exception as e:
        raise ValueError(f"Error during network scan: {str(e)}")

async def check_host(host: str) -> bool:
    """Check if a host is reachable using ping."""
    return await ping_host(host)

if __name__ == '__main__':
    # Example usage
    async def main():
        test_services = [
            {'name': 'Test Service 1', 'host': '127.0.0.1', 'port': 80},
            {'name': 'Test Service 2', 'host': '8.8.8.8', 'port': 53}
        ]
        results = await check_services(test_services)
        print("Service Check Results:")
        for result in results:
            print(f"{result['name']}:")
            print(f"  Host: {result['host']}")
            print(f"  Port: {result['port']}")
            print(f"  Port Open: {'✓' if result['port_open'] else '✗'}")
            print()
    asyncio.run(main()) 