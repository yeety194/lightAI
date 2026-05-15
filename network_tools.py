import socket
from utils import run_command


def check_wifi_status():
    """Check WIFI status."""
    stdout, stderr = run_command('netsh wlan show interfaces')
    if stderr:
        return f"Error: {stderr}"
    return stdout


def check_ethernet_status():
    """Check Ethernet status."""
    stdout, stderr = run_command('ipconfig')
    if stderr:
        return f"Error: {stderr}"
    lines = stdout.split('\n')
    ethernet_info = []
    in_adapter = False
    for line in lines:
        if 'Ethernet adapter' in line:
            in_adapter = True
            ethernet_info.append(line)
        elif in_adapter and line.strip() == '':
            break
        elif in_adapter:
            ethernet_info.append(line)
    return '\n'.join(ethernet_info) if ethernet_info else "No Ethernet adapter found."


def connect_to_wifi(ssid: str):
    """Connect to WIFI network."""
    cmd = f'netsh wlan connect name="{ssid}"'
    stdout, stderr = run_command(cmd)
    if stderr:
        return f"Error: {stderr}"
    return stdout


def disconnect_wifi():
    """Disconnect from WIFI."""
    stdout, stderr = run_command('netsh wlan disconnect')
    if stderr:
        return f"Error: {stderr}"
    return stdout


def enable_adapter(name: str):
    """Enable network adapter."""
    stdout, stderr = run_command(f'netsh interface set interface "{name}" admin=enabled')
    if stderr:
        return f"Error: {stderr}"
    return stdout


def disable_adapter(name: str):
    """Disable network adapter."""
    stdout, stderr = run_command(f'netsh interface set interface "{name}" admin=disabled')
    if stderr:
        return f"Error: {stderr}"
    return stdout


def list_adapters():
    """List network adapters."""
    stdout, stderr = run_command('netsh interface show interface')
    if stderr:
        return f"Error: {stderr}"
    return stdout


def check_internet():
    """Check internet connectivity."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return "Internet is connected."
    except OSError:
        return "No internet connection."
