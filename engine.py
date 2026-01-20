import math
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import pytesseract
from PIL import Image
from typing import Union, List, Tuple

class CalculatorEngine:
    def __init__(self):
        self.x = sp.Symbol('x')
        self.history_file = "history_log.json"
        self.history = self._load_history()
        self.ai_model = None
        self.ai_tokenizer = None

    def _load_history(self):
        """Loads history from a JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        """Saves history to a JSON file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except:
            pass

    def _load_ai(self):
        """Loads the lightweight AI model if not already loaded with lazy imports."""
        if self.ai_model is None:
            try:
                # Lazy imports to prevent startup crashes due to DLL errors
                from transformers import T5ForConditionalGeneration, T5Tokenizer
                import torch
                
                model_name = "google/t5-small"
                self.ai_tokenizer = T5Tokenizer.from_pretrained(model_name)
                self.ai_model = T5ForConditionalGeneration.from_pretrained(model_name)
                self.ai_model.eval()
                self.torch_module = torch # Store for later use
            except Exception as e:
                raise RuntimeError(f"AI Initialization Failed: {str(e)}")

    def _add_to_history(self, type: str, expression: str, result: any):
        import datetime
        self.history.append({
            "type": type,
            "expression": expression,
            "result": str(result),
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        if len(self.history) > 100:
            self.history.pop(0)
        self._save_history()

    def _auto_close_parentheses(self, expression: str) -> str:
        """Automatically appends missing closing parentheses."""
        open_count = expression.count('(')
        close_count = expression.count(')')
        if open_count > close_count:
            expression += ')' * (open_count - close_count)
        return expression

    def _preprocess(self, expression: str) -> str:
        """Preprocesses the expression to map user-friendly symbols to SymPy/Python equivalents."""
        # Map ^ to ** for power if not already handled by transformations
        # Map != to something SymPy understands or handle it as a boolean check
        # For now, we'll focus on common math symbols
        replacements = {
            '^': '**',
            '²': '**2',
            '÷': '/',
            '×': '*',
            'π': 'pi',
            '√': 'sqrt'
        }
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        return expression

    def evaluate_expression(self, expression: str) -> Union[float, complex, str]:
        """Evaluates a standard mathematical expression with robust parsing."""
        try:
            expression = self._auto_close_parentheses(expression)
            expression = self._preprocess(expression)
            transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
            expr = parse_expr(expression, transformations=transformations)
            
            # If it's a boolean expression (like 5 != 3), evaluate it
            if isinstance(expr, (bool, sp.logic.boolalg.BooleanAtom, sp.core.relational.Relational)):
                result = bool(expr)
            elif hasattr(expr, 'is_Boolean') and expr.is_Boolean:
                result = bool(expr)
            else:
                result = float(expr.evalf())
            
            self._add_to_history("Eval", expression, result)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def solve_equation(self, equation_str: str) -> List:
        """Solves an equation for any variables found in the expression."""
        try:
            equation_str = self._auto_close_parentheses(equation_str)
            equation_str = self._preprocess(equation_str)
            transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
            expr = parse_expr(equation_str, transformations=transformations)
            
            # Detect variables (free symbols)
            vars = list(expr.free_symbols)
            if not vars:
                return ["No variables found to solve for."]
            
            # Solve for all detected variables
            solutions = sp.solve(expr, vars)
            self._add_to_history("Solve", equation_str, solutions)
            return solutions
        except Exception as e:
            return [f"Error: {str(e)}"]

    def matrix_operations(self, op: str, *matrices: np.ndarray) -> Union[np.ndarray, float, str]:
        """Performs linear algebra operations using numpy."""
        try:
            if op == "add":
                return np.add(matrices[0], matrices[1])
            elif op == "multiply":
                return np.dot(matrices[0], matrices[1])
            elif op == "det":
                return np.linalg.det(matrices[0])
            elif op == "inv":
                return np.linalg.inv(matrices[0])
            elif op == "eig":
                return np.linalg.eig(matrices[0])
            else:
                return "Unknown operation"
        except Exception as e:
            return f"Error: {str(e)}"

    def plot_function(self, expression_str: str, x_range: Tuple[float, float] = (-10, 10)):
        """Plots a function using matplotlib."""
        try:
            expr = sp.sympify(expression_str)
            f = sp.lambdify(self.x, expr, "numpy")
            x_vals = np.linspace(x_range[0], x_range[1], 400)
            y_vals = f(x_vals)

            plt.figure(figsize=(8, 6))
            plt.plot(x_vals, y_vals, label=f"y = {expression_str}")
            plt.axhline(0, color='black', lw=1)
            plt.axvline(0, color='black', lw=1)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            plt.title(f"Plot of {expression_str}")
            
            # Save to a temporary file for display if needed, or just show
            # For now, we'll just return the plot object or save it
            plot_path = "C:\\Users\\sao\\Documents\\calculator\\last_plot.png"
            plt.savefig(plot_path)
            plt.close()
            return plot_path
        except Exception as e:
            return f"Error: {str(e)}"

    def analyze_function(self, expression_str: str) -> dict:
        """Provides a comprehensive analysis of a function."""
        try:
            expression_str = self._auto_close_parentheses(expression_str)
            expr = sp.sympify(expression_str)
            analysis = {
                "expression": expression_str,
                "roots": sp.solve(expr, self.x),
                "derivative": sp.diff(expr, self.x),
                "integral": sp.integrate(expr, self.x),
                "bref": self.get_bref_analysis(expr),
                "plot_path": self.plot_function(expression_str)
            }
            self._add_to_history("Analysis", expression_str, analysis['bref'])
            return analysis
        except Exception as e:
            return {"error": str(e)}

    def get_bref_analysis(self, expr: sp.Expr) -> str:
        """Returns a human-readable summary of the mathematical properties."""
        try:
            bref = []
            if expr.is_polynomial(self.x):
                deg = sp.degree(expr, self.x)
                bref.append(f"Polynomial of degree {deg}")
            
            if expr.has(sp.sin, sp.cos, sp.tan):
                bref.append("Trigonometric function")
            
            if expr.has(sp.log):
                bref.append("Logarithmic function")
            
            roots = sp.solve(expr, self.x)
            bref.append(f"Has {len(roots)} root(s)")
            
            return " | ".join(bref) if bref else "General mathematical expression"
        except:
            return "Complex mathematical expression"

    def export_report(self, analysis: dict, filename: str = "report.png"):
        """Exports the analysis report as a high-quality image."""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.axis('off')
            
            text = f"Mathematical Analysis Report\n"
            text += f"----------------------------\n\n"
            text += f"Expression: {analysis['expression']}\n"
            text += f"Bref: {analysis['bref']}\n"
            text += f"Roots: {analysis['roots']}\n"
            text += f"Derivative: {analysis['derivative']}\n"
            text += f"Integral: {analysis['integral']}\n"
            
            plt.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=12, verticalalignment='top', family='monospace')
            
            # Embed the plot if it exists
            if os.path.exists(analysis['plot_path']):
                from matplotlib.offsetbox import OffsetImage, AnnotationBbox
                img = plt.imread(analysis['plot_path'])
                imagebox = OffsetImage(img, zoom=0.5)
                ab = AnnotationBbox(imagebox, (0.5, 0.3), frameon=False)
                ax.add_artist(ab)
            
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        except Exception as e:
            return f"Export Error: {str(e)}"

    def extract_text_from_image(self, image_path: str) -> str:
        """Extracts mathematical text from an image using OCR."""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            # Basic cleanup
            text = text.replace('\n', ' ').strip()
            self._add_to_history("OCR", image_path, text)
            return text
        except Exception as e:
            return f"OCR Error: {str(e)}"

    def get_ai_guidance(self, expression: str) -> str:
        """Provides AI-powered hints/explanation for a math expression."""
        try:
            self._load_ai()
            # Refined prompt for T5 to focus on hints
            input_text = f"provide a math hint for: {expression}"
            input_ids = self.ai_tokenizer.encode(input_text, return_tensors="pt")
            
            with self.torch_module.no_grad():
                outputs = self.ai_model.generate(input_ids, max_length=100)
            
            guidance = self.ai_tokenizer.decode(outputs[0], skip_special_tokens=True)
            self._add_to_history("AI Hint", expression, guidance)
            return guidance
        except Exception as e:
            return f"AI Hint unavailable: {str(e)}"

import os
if __name__ == "__main__":
    # Quick test
    engine = CalculatorEngine()
    print(f"Eval sin(pi/2): {engine.evaluate_expression('sin(pi/2)')}")
    print(f"Eval 2^3: {engine.evaluate_expression('2^3')}")
    print(f"Eval 5²: {engine.evaluate_expression('5²')}")
    print(f"Eval 5 != 3: {engine.evaluate_expression('5 != 3')}")
    print(f"Eval 2*4: {engine.evaluate_expression('2*4')}")
    print(f"Eval 2(3+4): {engine.evaluate_expression('2(3+4)')}")
    print(f"Solve x^2 - 4: {engine.solve_equation('x^2 - 4')}")
    print(f"Solve y = x + 5: {engine.solve_equation('y - (x + 5)')}")
    print(f"Solve a + b = 10: {engine.solve_equation('a + b - 10')}")
    print(f"Matrix Det: {engine.matrix_operations('det', np.array([[1, 2], [3, 4]]))}")
