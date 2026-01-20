import os
import sys
import subprocess

def build():
    print("Starting Antigravity Premium Calculator Build Process...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define the command
    # --noconsole: Don't show terminal on Windows
    # --onefile: Bundle everything into a single executable (optional, can be slow to start)
    # --name: Name of the executable
    # --add-data: Include additional files (like icons or the history log if needed)
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--name=AntigravityCalculator",
        "--onefile",
        "--exclude-module=PyQt5",
        "calculator.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    print("\nBuild Complete!")
    if sys.platform == "win32":
        print(f"Your Windows executor is in: {os.path.abspath('dist/AntigravityCalculator.exe')}")
    elif sys.platform == "darwin":
        print(f"Your Mac executor is in: {os.path.abspath('dist/AntigravityCalculator.app')}")
    else:
        print(f"Your Linux executor is in: {os.path.abspath('dist/AntigravityCalculator')}")

if __name__ == "__main__":
    build()
