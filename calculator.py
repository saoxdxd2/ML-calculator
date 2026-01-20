import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLineEdit, 
                             QLabel, QStackedWidget, QFrame, QFileDialog, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette
from engine import CalculatorEngine
import datetime
from brain import SimpleBrain

class PremiumButton(QPushButton):
    def __init__(self, text, color1="#3a3a3a", color2="#2a2a2a", text_color="white"):
        super().__init__(text)
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(50, 40)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color1}, stop:1 {color2});
                color: {text_color};
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color2}, stop:1 {color1});
                border: 1px solid rgba(0, 255, 204, 0.5);
            }}
            QPushButton:pressed {{
                background: #1a1a1a;
                padding-top: 7px;
                padding-left: 7px;
            }}
        """)

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = CalculatorEngine()
        self.last_analysis = None
        self.initUI()
        self.update_history_ui() # Load persistent history
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.show_welcome_overlay)

    def initUI(self):
        self.setWindowTitle("Antigravity Premium Calculator")
        self.setMinimumSize(700, 600)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #2d2d2d);
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_h_layout = QHBoxLayout(central_widget)
        self.main_h_layout.setContentsMargins(10, 10, 10, 10)
        self.main_h_layout.setSpacing(10)

        # Left Panel (Calculator)
        calc_container = QFrame()
        calc_container.setStyleSheet("""
            QFrame {
                background: rgba(45, 45, 45, 0.6);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setContentsMargins(20, 20, 20, 20)
        calc_layout.setSpacing(15)

        # Display Area
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(80)
        self.display.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 30, 0.8);
                color: #87CEEB;
                border: 1px solid rgba(135, 206, 235, 0.3);
                border-radius: 15px;
                padding: 10px;
                font-size: 24px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        calc_layout.addWidget(self.display)

        # Result Label
        self.result_label = QLabel("Ready for Analysis")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #aaa; font-size: 14px; font-style: italic;")
        calc_layout.addWidget(self.result_label)

        # Buttons Grid
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setSpacing(10)
        
        self.basic_buttons = [
            ('C', '#ff4d4d', '#ff6666'), ('Del', '#e67e22', '#d35400'), ('(', '#3a3a3a', '#4a4a4a'), (')', '#3a3a3a', '#4a4a4a'),
            ('7', '#3a3a3a', '#4a4a4a'), ('8', '#3a3a3a', '#4a4a4a'), ('9', '#3a3a3a', '#4a4a4a'), ('/', '#ff9500', '#ffaa33'),
            ('4', '#3a3a3a', '#4a4a4a'), ('5', '#3a3a3a', '#4a4a4a'), ('6', '#3a3a3a', '#4a4a4a'), ('*', '#ff9500', '#ffaa33'),
            ('1', '#3a3a3a', '#4a4a4a'), ('2', '#3a3a3a', '#4a4a4a'), ('3', '#3a3a3a', '#4a4a4a'), ('+', '#ff9500', '#ffaa33'),
            ('0', '#3a3a3a', '#4a4a4a'), ('.', '#3a3a3a', '#4a4a4a'), ('=', '#00ffcc', '#33ffdd', 'black'), ('^', '#ff9500', '#ffaa33')
        ]

        self.sci_buttons = [
            ('sin', '#444', '#555'), ('cos', '#444', '#555'), ('tan', '#444', '#555'), ('log', '#444', '#555'),
            ('asin', '#444', '#555'), ('acos', '#444', '#555'), ('atan', '#444', '#555'), ('sqrt', '#444', '#555'),
            ('pi', '#444', '#555'), ('e', '#444', '#555'), ('abs', '#444', '#555'), ('²', '#444', '#555')
        ]

        self.create_buttons(self.basic_buttons)
        calc_layout.addLayout(self.buttons_layout)

        # Mode Selection
        mode_layout = QHBoxLayout()
        self.basic_mode_btn = QPushButton("Basic")
        self.sci_mode_btn = QPushButton("Scientific")
        self.solve_mode_btn = QPushButton("Solve")
        
        for btn in [self.basic_mode_btn, self.sci_mode_btn, self.solve_mode_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60, 60, 60, 0.5);
                    color: #888;
                    border-radius: 8px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:hover { color: #00ffcc; background: rgba(80, 80, 80, 0.8); }
            """)
            mode_layout.addWidget(btn)
        
        self.basic_mode_btn.clicked.connect(self.show_basic)
        self.sci_mode_btn.clicked.connect(self.show_scientific)
        self.solve_mode_btn.clicked.connect(self.show_solve)
        
        calc_layout.addLayout(mode_layout)
        
        # Help Button
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(30, 30)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 204, 0.2);
                color: #00ffcc;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0, 255, 204, 0.4); }
        """)
        self.help_btn.clicked.connect(self.show_welcome_overlay)
        mode_layout.addWidget(self.help_btn)

        self.main_h_layout.addWidget(calc_container, 3)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color: #888; font-size: 11px; background: transparent;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Tip: Use 'Analyze' for a deep dive into any function.")

        # Right Panel (History)
        self.history_container = QFrame()
        self.history_container.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.4);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        history_layout = QVBoxLayout(self.history_container)
        
        history_title = QLabel("Session History")
        history_title.setStyleSheet("color: #00ffcc; font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        history_layout.addWidget(history_title)

        from PyQt6.QtWidgets import QListWidget
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #ccc;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background: rgba(0, 255, 204, 0.1);
                color: #00ffcc;
            }
        """)
        history_layout.addWidget(self.history_list)
        
        self.main_h_layout.addWidget(self.history_container, 1)

    def create_buttons(self, button_list):
        # Clear existing buttons
        for i in reversed(range(self.buttons_layout.count())): 
            item = self.buttons_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        row, col = 0, 0
        for btn_text, color1, color2, *txt_color in button_list:
            text_color = txt_color[0] if txt_color else "white"
            button = PremiumButton(btn_text, color1, color2, text_color)
            
            # Add Tooltips for UX
            self.set_button_tooltip(button, btn_text)
            
            button.clicked.connect(lambda checked, t=btn_text: self.on_button_click(t))
            self.buttons_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        self.buttons_layout.activate()

    def set_button_tooltip(self, button, text):
        tooltips = {
            'Analyze': 'Get roots, derivatives, and a plot of the function.',
            'Solve': 'Solve the equation for all variables.',
            'Export': 'Save a professional image report of your analysis.',
            'OCR': 'Scan a math problem from an image or paper.',
            'Guide': 'Get an AI-powered hint to help you solve the problem.',
            'C': 'Clear the display and results.',
            '=': 'Evaluate the mathematical expression.'
        }
        if text in tooltips:
            button.setToolTip(tooltips[text])
        elif text in ['sin', 'cos', 'tan', 'log', 'sqrt', '√']:
            button.setToolTip(f"Mathematical function: {text}")

    def update_history_ui(self):
        self.history_list.clear()
        for item in reversed(self.engine.history):
            self.history_list.addItem(f"[{item['timestamp']}] {item['type']}: {item['expression']}")

    def show_welcome_overlay(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Welcome to Antigravity Premium!")
        msg.setText("<h3>Quick Start Guide</h3>")
        msg.setInformativeText(
            "<b>Basic Mode</b>: Standard calculations.<br>"
            "<b>Scientific Mode</b>: Advanced math functions.<br>"
            "<b>Solve Mode</b>: The powerhouse. Use it to:<br>"
            " • <b>Solve</b>: Find variables in equations.<br>"
            " • <b>Analyze</b>: Get roots, derivatives, and plots.<br>"
            " • <b>OCR</b>: Scan math from paper/images.<br>"
            " • <b>Guide</b>: Get AI-powered hints.<br><br>"
            "<i>Tip: Hover over any button for a quick description!</i>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox { background-color: #2d2d2d; color: white; }
            QLabel { color: white; font-size: 13px; }
            QPushButton { background-color: #00ffcc; color: black; border-radius: 5px; padding: 5px; min-width: 60px; }
        """)
        msg.exec()

    def show_basic(self):
        self.display.setReadOnly(True)
        self.create_buttons(self.basic_buttons)
        if not self.isMaximized():
            self.setMinimumSize(700, 600)
            self.adjustSize()

    def show_scientific(self):
        self.display.setReadOnly(True)
        combined = self.sci_buttons + self.basic_buttons
        self.create_buttons(combined)
        if not self.isMaximized():
            self.setMinimumSize(700, 800)
            self.adjustSize()

    def show_solve(self):
        self.display.setReadOnly(False)
        self.display.setPlaceholderText("Enter equation (e.g., y = x^2 - 4)")
        self.display.clear()
        self.result_label.setText("Unified Analysis Mode")
        
        solve_buttons = [
            ('sin', '#444', '#333'), ('cos', '#444', '#333'), ('tan', '#444', '#333'), ('log', '#444', '#333'),
            ('π', '#444', '#333'), ('√', '#444', '#333'), ('²', '#444', '#333'), ('^', '#444', '#333'),
            ('(', '#444', '#333'), (')', '#444', '#333'), ('Solve', '#00ffcc', '#00ccaa', 'black'), ('Analyze', '#ff9500', '#cc7a00'), 
            ('Export', '#9b59b6', '#8e44ad'), ('OCR', '#3498db', '#2980b9'), ('Guide', '#f1c40f', '#f39c12', 'black'), 
            ('Del', '#e67e22', '#d35400'), ('C', '#ff4d4d', '#cc0000')
        ]
        self.create_buttons(solve_buttons)
        if not self.isMaximized():
            self.setMinimumSize(700, 600)
            self.adjustSize()

    def on_button_click(self, char):
        if char == 'C':
            self.display.clear()
            self.result_label.setText("Ready")
            self.status_bar.showMessage("Display cleared.")
        elif char == 'Del':
            text = self.display.text()
            self.display.setText(text[:-1])
            self.status_bar.showMessage("Last character removed.")
        elif char == '=':
            expression = self.display.text()
            result = self.engine.evaluate_expression(expression)
            self.result_label.setText(f"Result: {result}")
            self.update_history_ui()
            self.status_bar.showMessage(f"Evaluated: {expression}")
        elif char == 'Solve':
            equation = self.display.text()
            self.status_bar.showMessage("Solving equation...")
            QApplication.processEvents()
            solutions = self.engine.solve_equation(equation)
            self.result_label.setText(f"Solutions: {solutions}")
            self.update_history_ui()
            self.status_bar.showMessage("Equation solved.")
        elif char == 'Analyze':
            expr = self.display.text()
            self.status_bar.showMessage("Analyzing function and generating plot...")
            QApplication.processEvents()
            analysis = self.engine.analyze_function(expr)
            if "error" in analysis:
                self.result_label.setText(f"Error: {analysis['error']}")
                self.status_bar.showMessage("Analysis failed.")
            else:
                self.last_analysis = analysis
                report = f"<b>Bref:</b> {analysis['bref']}<br><b>Roots:</b> {analysis['roots']}<br><b>Deriv:</b> {analysis['derivative']}"
                self.result_label.setText(report)
                self.update_history_ui()
                self.status_bar.showMessage("Analysis complete. Plot opened.")
                import os
                if os.path.exists(analysis['plot_path']):
                    os.startfile(analysis['plot_path'])
        elif char == 'Export':
            if self.last_analysis:
                self.status_bar.showMessage("Exporting report...")
                QApplication.processEvents()
                filename = f"analysis_{int(datetime.datetime.now().timestamp())}.png"
                path = self.engine.export_report(self.last_analysis, filename)
                self.result_label.setText(f"Report exported to: {path}")
                self.status_bar.showMessage(f"Report saved to {filename}")
                import os
                os.startfile(path)
            else:
                self.result_label.setText("Analyze a function first to export!")
                self.status_bar.showMessage("Tip: Click 'Analyze' before 'Export'.")
        elif char == 'OCR':
            self.status_bar.showMessage("Select an image to scan...")
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                self.status_bar.showMessage("Extracting text from image...")
                QApplication.processEvents()
                text = self.engine.extract_text_from_image(file_path)
                self.display.setText(text)
                self.result_label.setText("Text extracted from image.")
                self.update_history_ui()
                self.status_bar.showMessage("OCR complete.")
            else:
                self.status_bar.showMessage("OCR cancelled.")
        elif char == 'Guide':
            expr = self.display.text()
            if expr:
                self.result_label.setText("AI is thinking...")
                self.status_bar.showMessage("AI is generating a hint...")
                QApplication.processEvents()
                guidance = self.engine.get_ai_guidance(expr)
                self.result_label.setText(f"<b>AI Guide:</b> {guidance}")
                self.update_history_ui()
                self.status_bar.showMessage("AI hint generated.")
            else:
                self.result_label.setText("Enter an expression for the AI to guide you!")
                self.status_bar.showMessage("Tip: Type a function or equation first.")
        elif char in ['sin', 'cos', 'tan', 'log', 'asin', 'acos', 'atan', 'abs', 'exp', '√']:
            symbol = 'sqrt(' if char == '√' else char + "("
            self.display.setText(self.display.text() + symbol)
        elif char == 'π':
            self.display.setText(self.display.text() + 'π')
        elif char == '²':
            self.display.setText(self.display.text() + '²')
        else:
            self.display.setText(self.display.text() + char)

    def resizeEvent(self, event):
        """Dynamic scaling of fonts based on window size."""
        super().resizeEvent(event)
        new_width = self.width()
        
        # Scale display font (smaller ratio for sky blue text)
        display_font_size = max(16, int(new_width / 25))
        self.display.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2d2d2d;
                color: #87CEEB;
                border: 1px solid rgba(135, 206, 235, 0.3);
                border-radius: 15px;
                padding: 10px;
                font-size: {display_font_size}px;
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        
        # Scale button fonts using QFontMetrics for exact fit
        from PyQt6.QtGui import QFontMetrics
        for i in range(self.buttons_layout.count()):
            widget = self.buttons_layout.itemAt(i).widget()
            if isinstance(widget, PremiumButton):
                # Calculate max font size that fits the button
                btn_w = widget.width() - 10
                btn_h = widget.height() - 10
                
                font = widget.font()
                size = 16 # Start with a reasonable size
                font.setPointSize(size)
                metrics = QFontMetrics(font)
                
                # Shrink if too big
                while (metrics.horizontalAdvance(widget.text()) > btn_w or metrics.height() > btn_h) and size > 8:
                    size -= 1
                    font.setPointSize(size)
                    metrics = QFontMetrics(font)
                
                # Grow if too small
                while metrics.horizontalAdvance(widget.text()) < btn_w * 0.8 and metrics.height() < btn_h * 0.8 and size < 24:
                    size += 1
                    font.setPointSize(size)
                    metrics = QFontMetrics(font)

                style = widget.styleSheet()
                import re
                new_style = re.sub(r"font-size: \d+px;", f"font-size: {size}px;", style)
                widget.setStyleSheet(new_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()
    sys.exit(app.exec())
