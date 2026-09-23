"""
SmartDesk Tools.
Search and calculator.
"""

import ast
import operator
import tkinter as tk
from tkinter import messagebox

from database import get_projects, get_notes


class ToolsScreen(tk.Frame):
    """Search and calculator tools."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self._build()

    def _build(self):
        tk.Label(
            self, text="🔎 Tools",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(anchor="w", padx=30, pady=25)

        search_card = tk.Frame(self, bg="#111827", padx=20, pady=20)
        search_card.pack(fill="x", padx=30)

        tk.Label(
            search_card, text="Search SmartDesk",
            font=("Segoe UI", 14, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w")

        row = tk.Frame(search_card, bg="#111827")
        row.pack(fill="x", pady=10)

        self.search_entry = tk.Entry(
            row, font=("Segoe UI", 12),
            bg="#1E293B", fg="white",
            insertbackground="white", relief="flat"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=8)

        tk.Button(
            row, text="Search", command=self.search,
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=15
        ).pack(side="left", padx=8)

        self.results = tk.Listbox(
            search_card, height=7,
            bg="#0F172A", fg="#CBD5E1",
            selectbackground="#2563EB", relief="flat"
        )
        self.results.pack(fill="x")

        calc = tk.Frame(self, bg="#111827", padx=20, pady=20)
        calc.pack(fill="x", padx=30, pady=20)

        tk.Label(
            calc, text="🧮 Calculator",
            font=("Segoe UI", 14, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w")

        self.expression = tk.Entry(
            calc, font=("Consolas", 16),
            bg="#1E293B", fg="white",
            insertbackground="white", relief="flat"
        )
        self.expression.pack(fill="x", pady=10, ipady=8)
        self.expression.bind("<Return>", lambda _: self.calculate())

        tk.Button(
            calc, text="Calculate", command=self.calculate,
            bg="#7C3AED", fg="white", relief="flat",
            cursor="hand2", padx=15
        ).pack(anchor="w")

        self.result = tk.Label(
            calc, text="Result: ",
            font=("Segoe UI", 13, "bold"),
            fg="#38BDF8", bg="#111827"
        )
        self.result.pack(anchor="w", pady=10)

    def search(self):
        query = self.search_entry.get().strip().lower()
        self.results.delete(0, "end")

        if not query:
            return

        for project in get_projects():
            if query in project["name"].lower() or query in project["path"].lower():
                self.results.insert("end", f"📁 {project['name']} | {project['path']}")

        for note in get_notes():
            if query in note["title"].lower() or query in note["content"].lower():
                self.results.insert("end", f"📝 {note['title']}")

        if self.results.size() == 0:
            self.results.insert("end", "No results found.")

    def calculate(self):
        expression = self.expression.get().strip()
        try:
            value = safe_calculate(expression)
            self.result.config(text=f"Result: {value}")
        except Exception as error:
            messagebox.showerror("Calculator", f"Invalid expression: {error}")


_ALLOWED = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression):
    """Safely evaluate basic arithmetic expressions."""

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](evaluate(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](
                evaluate(node.left), evaluate(node.right)
            )
        raise ValueError("Only basic arithmetic is supported.")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree)
