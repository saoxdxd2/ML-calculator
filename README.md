# Antigravity Premium Calculator 🚀

A state-of-the-art, AI-powered mathematical suite designed for students, engineers, and researchers.

## ✨ Features

- **Premium UI**: Glassmorphism aesthetics with dynamic scaling and a sky-blue display.
- **AI Hint System**: Get intelligent mathematical hints and explanations (T5-small).
- **OCR Integration**: Scan math problems directly from images or paper.
- **Advanced Analysis**: Roots, derivatives, integrals, and "Bref" human-readable summaries.
- **Persistent History**: Your sessions are automatically saved and reloaded.
- **Export Reports**: Generate professional PNG reports with plots and analysis.
- **Cross-Platform**: Native executors for Windows, Mac, and Linux.

## 🚀 Installation & Usage

### One-Command Installation (Mac/Linux)
Copy and paste this into your terminal for a complete setup:
```bash
git clone https://github.com/yourusername/calculator.git && cd calculator && chmod +x setup.sh && ./setup.sh
```


### Mac & Linux (Automated)
1. Open your terminal in the project folder.
2. Run the installer:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. This will set up your environment and build a native executor for your system.

### Manual Setup (Developers)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python calculator.py
   ```

## 🛠 Requirements
- **Python 3.10+**
- **Tesseract OCR**: Required for the OCR feature.
  - Windows: Install via [vcpkg](https://github.com/UB-Mannheim/tesseract/wiki).
  - Mac: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`

---
*Built with ❤️ by Sao.*

