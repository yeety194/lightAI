# LightAI - Local Network Assistant

LightAI is a local AI assistant for Windows network management. It runs entirely offline using a local LLM and supports conversational interaction with network tools for WIFI, Ethernet, and adapter control.

## Features

- **Local AI brain**: Runs a local LLM model without external APIs
- **Network management**: Check WIFI/Ethernet status, connect/disconnect WIFI, enable/disable adapters
- **Connectivity checks**: Verify if internet access is available
- **Modular project**: Separate `lightAI.py`, `brain.py`, `network_tools.py`, and `utils.py`

## Requirements

- Python 3.10+ recommended
- Windows OS
- `torch`
- `transformers`

## Setup

1. Open PowerShell and activate your virtual environment if you have one:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies from `pyproject.toml`:

```powershell
python -m pip install -e .
```

3. If you prefer direct installation instead of editable mode:

```powershell
python -m pip install torch transformers
```

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