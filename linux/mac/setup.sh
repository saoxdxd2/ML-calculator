#!/bin/bash

echo "--------------------------------------------------"
echo "   Antigravity Premium Calculator Installer      "
echo "--------------------------------------------------"

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "Error: Python3 is not installed. Please install it first."
    exit 1
fi

# Check for Tesseract
if ! command -v tesseract &> /dev/null
then
    echo "Warning: Tesseract OCR not found. OCR features will be disabled."
    echo "To enable OCR, install Tesseract (e.g., 'brew install tesseract' or 'sudo apt install tesseract-ocr')."
fi

# Check for Git and install if missing
if ! command -v git &> /dev/null
then
    echo "Git not found. Attempting to install..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install git
        else
            echo "Homebrew not found. Please install Git manually or install Homebrew first."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y git
    fi
fi

echo "Step 1: Creating Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo "Step 2: Installing Dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 3: Building Standalone Executor..."
python3 build_app.py

echo "Step 4: Creating Desktop Shortcut (Racourci)..."
DESKTOP_DIR="$HOME/Desktop"
APP_NAME="AntigravityCalculator"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac: Create a small launcher script on the Desktop
    LAUNCHER="$DESKTOP_DIR/$APP_NAME.command"
    echo "#!/bin/bash" > "$LAUNCHER"
    echo "cd \"$(pwd)\" && ./dist/$APP_NAME.app/Contents/MacOS/$APP_NAME" >> "$LAUNCHER"
    chmod +x "$LAUNCHER"
    echo "Mac shortcut created on Desktop."
else
    # Linux: Create a .desktop file
    SHORTCUT="$DESKTOP_DIR/$APP_NAME.desktop"
    echo "[Desktop Entry]" > "$SHORTCUT"
    echo "Name=$APP_NAME" >> "$SHORTCUT"
    echo "Exec=$(pwd)/dist/$APP_NAME" >> "$SHORTCUT"
    echo "Icon=$(pwd)/icon.png" >> "$SHORTCUT" # Assuming an icon exists or will be added
    echo "Type=Application" >> "$SHORTCUT"
    echo "Terminal=false" >> "$SHORTCUT"
    chmod +x "$SHORTCUT"
    echo "Linux shortcut created on Desktop."
fi

echo "--------------------------------------------------"
echo "Installation Complete!"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Your Mac App is in: dist/AntigravityCalculator.app"
else
    echo "Your Linux Binary is in: dist/AntigravityCalculator"
fi
echo "The shortcut has been added to your Desktop."
echo "--------------------------------------------------"
