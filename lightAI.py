import subprocess
import socket
import sys

def run_command(command):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

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
    # Parse for Ethernet
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

def connect_to_wifi(ssid, password=None):
    """Connect to WIFI network."""
    if password:
        cmd = f'netsh wlan connect name="{ssid}"'
        # Note: For security, password is usually stored in profile
        # To add a profile: netsh wlan add profile filename="profile.xml"
        # But for simplicity, assume profile exists
    else:
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

def enable_adapter(name):
    """Enable network adapter."""
    stdout, stderr = run_command(f'netsh interface set interface "{name}" admin=enabled')
    if stderr:
        return f"Error: {stderr}"
    return stdout

def disable_adapter(name):
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

def parse_command(user_input):
    """Parse user input and execute command."""
    input_lower = user_input.lower()
    if 'check wifi' in input_lower or 'wifi status' in input_lower:
        return check_wifi_status()
    elif 'check ethernet' in input_lower or 'ethernet status' in input_lower:
        return check_ethernet_status()
    elif 'connect wifi' in input_lower:
        # Extract SSID
        parts = user_input.split()
        if len(parts) > 2:
            ssid = parts[2]
            return connect_to_wifi(ssid)
        else:
            return "Please specify WIFI name: connect wifi <SSID>"
    elif 'disconnect wifi' in input_lower:
        return disconnect_wifi()
    elif 'enable adapter' in input_lower:
        parts = user_input.split(' ', 2)
        if len(parts) > 2:
            name = parts[2]
            return enable_adapter(name)
        else:
            return "Please specify adapter name: enable adapter <name>"
    elif 'disable adapter' in input_lower:
        parts = user_input.split(' ', 2)
        if len(parts) > 2:
            name = parts[2]
            return disable_adapter(name)
        else:
            return "Please specify adapter name: disable adapter <name>"
    elif 'list adapters' in input_lower:
        return list_adapters()
    elif 'check internet' in input_lower:
        return check_internet()
    elif 'help' in input_lower:
        return """Available commands:
- check wifi: Check WIFI status
- check ethernet: Check Ethernet status
- connect wifi <SSID>: Connect to WIFI
- disconnect wifi: Disconnect from WIFI
- enable adapter <name>: Enable network adapter
- disable adapter <name>: Disable network adapter
- list adapters: List all adapters
- check internet: Check internet connectivity
- quit: Exit
"""
    else:
        return "Sorry, I didn't understand that. Type 'help' for commands."

def main():
    print("Hello! I'm LightAI. I can help with network tasks. Type 'help' for commands.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        response = parse_command(user_input)
        print(f"LightAI: {response}")

if __name__ == "__main__":
    main()