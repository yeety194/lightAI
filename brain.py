import importlib.util
import shutil
import subprocess
import sys
import re
from typing import Optional

REQUIRED_PACKAGES = ["torch", "transformers"]


def _pip_available() -> bool:
    return shutil.which("pip") is not None or importlib.util.find_spec("pip") is not None


def _install_dependencies():
    if not _pip_available():
        raise SystemExit(
            "Required dependencies are missing and pip is not available.\n"
            "On Arch Linux, install pip with: sudo pacman -S python-pip\n"
            "Then install dependencies with: python -m pip install -e .\n"
            "Or install the packages directly: python -m pip install torch transformers\n"
        )

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", *REQUIRED_PACKAGES],
            check=True,
        )
    except subprocess.CalledProcessError as install_error:
        raise SystemExit(
            "Unable to install required dependencies automatically. "
            "Please install 'torch' and 'transformers' manually with pip."
        ) from install_error


try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
except ImportError:
    print("Required packages are missing. Attempting to install them...")
    _install_dependencies()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

print("Initializing LightAI brain with local model (first run may download weights)...")
model_name = "mistralai/Mistral-7B-Instruct-v0.2"
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=dtype,
    device_map="auto" if device == "cuda" else None,
    low_cpu_mem_usage=True if device == "cuda" else False,
)
model.eval()

print("✓ LightAI brain ready.")

def generate_response(prompt: str, max_length: int = 500) -> str:
    """Generate a response using the local model."""
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
        else:
            response = response[len(prompt):].strip()
        return response
    except Exception as e:
        return f"I encountered an error: {str(e)}"


def parse_tool_call(response: str) -> Optional[tuple]:
    """Parse if the model intends to call a tool from its response."""
    tools_mentioned = {
        "check_wifi": "check_wifi_status",
        "wifi status": "check_wifi_status",
        "ethernet": "check_ethernet_status",
        "connect to": "connect_to_wifi",
        "disconnect": "disconnect_wifi",
        "enable adapter": "enable_adapter",
        "disable adapter": "disable_adapter",
        "list adapters": "list_adapters",
        "internet": "check_internet",
    }

    response_lower = response.lower()
    for trigger, tool_name in tools_mentioned.items():
        if trigger in response_lower:
            if tool_name == "connect_to_wifi":
                match = re.search(r'(?:to|name|ssid)[\s:]*["\']?([a-zA-Z0-9\-_.]+)["\']?', response_lower)
                if match:
                    return (tool_name, {"ssid": match.group(1)})
                return (tool_name, {})
            elif tool_name in ["enable_adapter", "disable_adapter"]:
                match = re.search(r'(?:adapter|interface)[\s:]*["\']?([a-zA-Z0-9\-_.]+)["\']?', response_lower)
                if match:
                    return (tool_name, {"name": match.group(1)})
                return (tool_name, {})
            return (tool_name, {})
    return None