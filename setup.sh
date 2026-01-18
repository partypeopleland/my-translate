#!/bin/bash

# ==========================================
# TranslateGemma Setup Script
# ==========================================

# 1. Get Dynamic Paths (The key to portability)
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/.venv"
CLIENT_SCRIPT="$PROJECT_DIR/client.py"
PYTHON_EXEC="$VENV_DIR/bin/python3"

echo "=========================================="
echo "  Setting up TranslateGemma Environment"
echo "  Path: $PROJECT_DIR"
echo "=========================================="

# 2. Check for Ollama (Basic check)
if ! command -v ollama &> /dev/null; then
    echo "[!] Warning: 'ollama' command not found. Please ensure Ollama is installed."
fi

# 3. Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv "$VENV_DIR"
else
    echo "[*] Virtual environment already exists."
fi

# 4. Install dependencies
echo "[*] Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r requirements.txt -q

# 5. Make client executable
chmod +x "$CLIENT_SCRIPT"

# ==========================================
# Generate User Instructions
# ==========================================

# WSL Alias Command
ALIAS_CMD="alias trans='$PYTHON_EXEC $CLIENT_SCRIPT'"

# Windows PowerShell Function (Dynamically populated)
# We use a heredoc to create the file content
cat <<EOF > windows_setup_snippet.txt
# ==========================================================
# Copy and paste this function into your PowerShell Profile
# Run 'notepad \$PROFILE' in PowerShell to edit.
# ==========================================================

function trans {
    # Auto-generated paths from setup.sh
    \$wslPath = "$PROJECT_DIR"
    \$clientScript = "\$wslPath/client.py"
    \$venvPython = "\$wslPath/.venv/bin/python3"

    # Check for Pipe input
    if (\$Input.MoveNext()) {
        \$Input.Reset()
        \$inputStr = \$Input | Out-String
        \$inputStr | wsl \$venvPython \$clientScript
    }
    else {
        # Standard argument input
        \$argsStr = \$args -join " "
        wsl \$venvPython \$clientScript "\$argsStr"
    }
}
EOF

echo ""
echo "=========================================="
echo "  Setup Complete! "
echo "=========================================="
echo ""
echo "--- [ For WSL Users ] ---"
echo "Add this line to your ~/.bashrc or ~/.zshrc:"
echo ""
echo "  $ALIAS_CMD"
echo ""
echo "--- [ For Windows Users ] ---"
echo "I have generated a configuration snippet for you."
echo "Please verify the content of 'windows_setup_snippet.txt' and append it to your PowerShell profile."
echo ""
echo "  cat windows_setup_snippet.txt"
echo ""