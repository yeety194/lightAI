import subprocess


def run_command(command: str):
    """Run a shell command and return output, error, and exit code."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1
