#!/usr/bin/env python3
import argparse
import requests
import sys
import subprocess
import time
import os
from pathlib import Path

# Config
SERVER_PORT = 8989
SERVER_URL = f"http://localhost:{SERVER_PORT}/translate"
SCRIPT_DIR = Path(__file__).parent.absolute()
SERVER_SCRIPT = SCRIPT_DIR / "server.py"
LOG_FILE = SCRIPT_DIR / "server.log"

def is_server_running():
    try:
        # Just a simple connection check
        requests.get(f"http://localhost:{SERVER_PORT}/docs", timeout=0.2)
        return True
    except requests.ConnectionError:
        return False
    except Exception:
        return False

def start_server():
    """Starts the server in the background."""
    print("Initializing translation service...", file=sys.stderr)
    try:
        with open(LOG_FILE, "a") as log:
            subprocess.Popen(
                [sys.executable, str(SERVER_SCRIPT)],
                stdout=log,
                stderr=log,
                start_new_session=True # Detach from current terminal
            )
        # Wait for server to be ready
        retries = 20 # 2 seconds max
        for _ in range(retries):
            if is_server_running():
                return True
            time.sleep(0.1)
        return False
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="TranslateGemma CLI")
    parser.add_argument("text", help="Text to translate")
    parser.add_argument("-s", "--source", help="Source language (zh, en, ja)", default=None)
    parser.add_argument("-t", "--target", help="Target language (zh, en, ja)", default=None)
    
    args = parser.parse_args()

    # 1. Check/Start Server
    if not is_server_running():
        if not start_server():
            print("Error: Could not start the translation service.", file=sys.stderr)
            print(f"Check logs at: {LOG_FILE}", file=sys.stderr)
            sys.exit(1)

    # 2. Send Request
    payload = {
        "text": args.text,
        "source_lang": args.source,
        "target_lang": args.target
    }

    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Simple Output
        print(data["translated_text"])
        
    except requests.exceptions.HTTPError as e:
        print(f"Server Error: {e.response.text}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
