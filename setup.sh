#!/bin/bash

# Define directories
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/.venv"
CLIENT_SCRIPT="$PROJECT_DIR/client.py"

echo "=========================================="
echo "  Setting up TranslateGemma Environment"
echo "=========================================="

# 1. Create Virtual Environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv "$VENV_DIR"
else
    echo "[*] Virtual environment already exists."
fi

# 2. Install dependencies into the virtual environment
echo "[*] Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r requirements.txt -q

# 3. Make client executable
chmod +x "$CLIENT_SCRIPT"

# 4. Generate the exact alias command
# We use the python executable INSIDE the venv
PYTHON_EXEC="$VENV_DIR/bin/python3"
ALIAS_CMD="alias trans='$PYTHON_EXEC $CLIENT_SCRIPT'"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="

echo ""
echo "Please copy and paste the following line into your terminal"
echo "(and add it to your ~/.bashrc or ~/.zshrc for permanence):"

echo ""
echo "  $ALIAS_CMD"

echo ""
echo "Try it out:"
echo "  trans \"Hello World\""
