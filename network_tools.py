import platform
import shutil
import socket
from utils import run_command


def _is_windows():
    return platform.system().lower().startswith("win")


def _is_linux():
    return platform.system().lower() == "linux"


def _has_command(name: str):
    return shutil.which(name) is not None


def _format_command_result(stdout: str, stderr: str, returncode: int):
    if returncode == 0:
        return stdout or "Command completed successfully."
    if stderr:
        return f"Error: {stderr}"
    return f"Error: command failed with exit code {returncode}."


def check_wifi_status():
    """Check WIFI status."""
    if _is_windows():
        stdout, stderr, code = run_command('netsh wlan show interfaces')
        return _format_command_result(stdout, stderr, code)

    if _is_linux():
        if _has_command("nmcli"):
            stdout, stderr, code = run_command('nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status')
            if code == 0 and stdout:
                wifi_lines = [line for line in stdout.splitlines() if ":wifi:" in line]
                if wifi_lines:
                    return "\n".join(wifi_lines)
                return "No Wi-Fi device is currently active or connected."
            return _format_command_result(stdout, stderr, code)

        stdout, stderr, code = run_command('iwconfig 2>/dev/null')
        return _format_command_result(stdout, stderr, code)

    return "Wi-Fi status checks are supported only on Windows and Linux."


def check_ethernet_status():
    """Check Ethernet status."""
    if _is_windows():
        stdout, stderr, code = run_command('ipconfig')
        if code != 0:
            return _format_command_result(stdout, stderr, code)
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

    if _is_linux():
        stdout, stderr, code = run_command('ip -brief link')
        return _format_command_result(stdout, stderr, code)

    return "Ethernet status checks are supported only on Windows and Linux."


def connect_to_wifi(ssid: str):
    """Connect to WIFI network."""
    if _is_windows():
        stdout, stderr, code = run_command(f'netsh wlan connect name="{ssid}"')
        return _format_command_result(stdout, stderr, code)

    if _is_linux():
        if not _has_command("nmcli"):
            return "Error: nmcli is required on Linux to connect to Wi-Fi. Install NetworkManager or use your desktop network tool."
        stdout, stderr, code = run_command(f'nmcli device wifi connect "{ssid}"')
        if code != 0 and "password" in stderr.lower():
            return f"Error: {stderr}\nIf this network requires a password, provide it with nmcli or use your system network manager."
        return _format_command_result(stdout, stderr, code)

    return "Wi-Fi connection is supported only on Windows and Linux."


def disconnect_wifi():
    """Disconnect from WIFI."""
    if _is_windows():
        stdout, stderr, code = run_command('netsh wlan disconnect')
        return _format_command_result(stdout, stderr, code)

    if _is_linux():
        if not _has_command("nmcli"):
            return "Error: nmcli is required on Linux to disconnect Wi-Fi. Install NetworkManager or use your desktop network tool."
        stdout, stderr, code = run_command('nmcli -t -f DEVICE,TYPE,STATE device status')
        if code != 0:
            return _format_command_result(stdout, stderr, code)
        for line in stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 3 and parts[1] == "wifi" and parts[2] == "connected":
                device = parts[0]
                stdout2, stderr2, code2 = run_command(f'nmcli device disconnect "{device}"')
                return _format_command_result(stdout2, stderr2, code2)
        return "No connected Wi-Fi device found."

    return "Wi-Fi disconnection is supported only on Windows and Linux."


def enable_adapter(name: str):
    """Enable network adapter."""
    if _is_windows():
        stdout, stderr, code = run_command(f'netsh interface set interface "{name}" admin=enabled')
        return _format_command_result(stdout, stderr, code)

    if _is_linux():
        stdout, stderr, code = run_command(f'ip link set dev "{name}" up')
        if code != 0:
            return f"Error: {stderr}\nThis command may require root privileges."
        return f"Interface '{name}' enabled."

    return "Adapter control is supported only on Windows and Linux."


def disable_adapter(name: str):
    """Disable network adapter."""
    if _is_windows():
        stdout, stderr, code = run_command(f'netsh interface set interface "{name}" admin=disabled')
        return _format_command_result(stdout, stderr, code)

    if _is_linux():
        stdout, stderr, code = run_command(f'ip link set dev "{name}" down')
        if code != 0:
            return f"Error: {stderr}\nThis command may require root privileges."
        return f"Interface '{name}' disabled."

    return "Adapter control is supported only on Windows and Linux."


def list_adapters():
    """List network adapters."""
    if _is_windows():
        stdout, stderr, code = run_command('netsh interface show interface')
        return _format_command_result(stdout, stderr, code)

    if _is_linux():
        if _has_command("nmcli"):
            stdout, stderr, code = run_command('nmcli device status')
            if code == 0:
                return stdout
        stdout, stderr, code = run_command('ip -brief link')
        return _format_command_result(stdout, stderr, code)

    return "Adapter listing is supported only on Windows and Linux."


def check_internet():
    """Check internet connectivity."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return "Internet is connected."
    except OSError:
        return "No internet connection."
