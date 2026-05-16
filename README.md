# LightAI - Local Network Assistant

LightAI is a local AI assistant for Windows and Linux network management. It runs entirely offline using a local LLM and supports conversational interaction with network tools for WIFI, Ethernet, and adapter control.

## Features

- **Local AI brain**: Runs a local LLM model without external APIs
- **Network management**: Check WIFI/Ethernet status, connect/disconnect WIFI, enable/disable adapters
- **Connectivity checks**: Verify if internet access is available
- **Modular project**: Separate `lightAI.py`, `brain.py`, `network_tools.py`, and `utils.py`

## Requirements

- Python 3.10+ recommended
- Windows or Linux OS
- `torch`
- `transformers`
- `nmcli` / NetworkManager on Linux for Wi-Fi management
- `pip` or `python -m ensurepip` if pip is not already installed

## Setup

1. Open a terminal and activate your virtual environment if you have one.

Linux example:

```bash
source .venv/bin/activate
```

Windows PowerShell example:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies from `pyproject.toml`:

```bash
python -m pip install -e .
```

### Arch Linux setup

On Arch Linux, make sure `pip` is installed first:

```bash
sudo pacman -Syu python-pip
```

Then install dependencies:

```bash
python -m pip install -e .
```

If you prefer Arch packages for PyTorch, you can also install:

```bash
sudo pacman -S python-pytorch
```

and then install only `transformers` with pip:

```bash
python -m pip install transformers
```

3. If you prefer direct installation instead of editable mode:

```powershell
python -m pip install torch transformers
```

If `pip` is not available on Arch Linux, install it with:

```bash
sudo pacman -S python-pip
```

If you are on a different Linux distribution, use your distro's package manager or install `pip` via Python packaging support.

## Usage

Run the assistant:

```powershell
python lightAI.py
```

First run may download the local model weights. After that, LightAI works offline.

### Example prompts

- `Check my WIFI status`
- `Connect to my home network`
- `Disconnect from WIFI`
- `Enable the Ethernet adapter`
- `List all adapters`
- `Is my internet connection active?`

Type `quit`, `exit`, or `bye` to end the session.

## Project Structure

- `lightAI.py` - main application and conversation loop
- `brain.py` - local model loading and response generation
- `network_tools.py` - network command helper functions
- `utils.py` - shared utility functions
- `pyproject.toml` - dependency and package metadata

## Notes

- The assistant uses the model `mistralai/Mistral-7B-Instruct-v0.2` locally.
- For better performance, use a machine with a GPU. CPU-only use is supported but slower.
- Network commands may require administrator privileges.

## License

Add your license here.

## Disclaimer

This tool performs network operations on your system. Use it responsibly and at your own risk.