"""
SmartDesk Editor UI.
Notepad-style text editor with Python execution.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from database import add_recent_file, increment_stat, log_activity
from core.python_runner import run_python_file


class EditorScreen(tk.Frame):
    """Text and Python editor."""

    def __init__(self, master, file_path=None, on_close=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.file_path = Path(file_path) if file_path else None
        self.on_close = on_close
        self._build()
        if self.file_path:
            self.load_file()

    def _build(self):
        toolbar = tk.Frame(self, bg="#111827", padx=10, pady=8)
        toolbar.pack(fill="x")

        for text, command in [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("Save As", self.save_as),
        ]:
            tk.Button(
                toolbar, text=text, command=command,
                bg="#1E293B", fg="white", relief="flat",
                cursor="hand2", padx=12
            ).pack(side="left", padx=3)

        self.run_button = tk.Button(
            toolbar, text="▶ Run Python", command=self.run_python,
            bg="#16A34A", fg="white", relief="flat",
            cursor="hand2", padx=12
        )
        self.run_button.pack(side="left", padx=10)

        tk.Button(
            toolbar, text="Close", command=self.close,
            bg="#7F1D1D", fg="white", relief="flat",
            cursor="hand2", padx=12
        ).pack(side="right")

        self.title_label = tk.Label(
            toolbar, text="Untitled", font=("Segoe UI", 10, "bold"),
            fg="#CBD5E1", bg="#111827"
        )
        self.title_label.pack(side="right", padx=15)

        editor_frame = tk.Frame(self, bg="#0B1020")
        editor_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.text = tk.Text(
            editor_frame, wrap="none",
            undo=True, font=("Consolas", 12),
            bg="#0F172A", fg="#E2E8F0",
            insertbackground="white",
            selectbackground="#2563EB",
            relief="flat", padx=15, pady=15
        )
        self.text.pack(side="left", fill="both", expand=True)

        y_scroll = tk.Scrollbar(editor_frame, command=self.text.yview)
        y_scroll.pack(side="right", fill="y")
        self.text.config(yscrollcommand=y_scroll.set)

        output_frame = tk.Frame(self, bg="#111827")
        output_frame.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(
            output_frame, text="Output",
            font=("Segoe UI", 10, "bold"),
            fg="#38BDF8", bg="#111827"
        ).pack(anchor="w", padx=10, pady=5)

        self.output = tk.Text(
            output_frame, height=7,
            font=("Consolas", 10),
            bg="#020617", fg="#CBD5E1",
            relief="flat"
        )
        self.output.pack(fill="x", padx=10, pady=(0, 10))

        self.update_run_button()

    def update_run_button(self):
        is_python = self.file_path and self.file_path.suffix.lower() == ".py"
        self.run_button.config(state="normal" if is_python else "disabled")

    def new_file(self):
        self.file_path = None
        self.title_label.config(text="Untitled")
        self.text.delete("1.0", "end")
        self.output.delete("1.0", "end")
        self.update_run_button()

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Python files", "*.py"),
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.file_path = Path(path)
            self.load_file()

    def load_file(self):
        try:
            content = self.file_path.read_text(encoding="utf-8")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.title_label.config(text=self.file_path.name)
            add_recent_file(str(self.file_path))
            self.update_run_button()
        except Exception as error:
            messagebox.showerror("SmartDesk", str(error))

    def save_file(self):
        if not self.file_path:
            return self.save_as()

        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text(
                self.text.get("1.0", "end-1c"),
                encoding="utf-8"
            )
            increment_stat("files_saved")
            log_activity("save", str(self.file_path))
            self.title_label.config(text=self.file_path.name)
            self.update_run_button()
        except Exception as error:
            messagebox.showerror("SmartDesk", str(error))

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.file_path = Path(path)
            self.save_file()

    def run_python(self):
        if not self.file_path:
            messagebox.showwarning("SmartDesk", "Save the Python file first.")
            return

        self.save_file()
        result = run_python_file(self.file_path)

        self.output.delete("1.0", "end")
        if result["output"]:
            self.output.insert("end", result["output"])

        if result["error"]:
            self.output.insert("end", "\n" + result["error"])

        if result["success"]:
            increment_stat("python_runs")
            log_activity("python_run", str(self.file_path))

    def close(self):
        if self.on_close:
            self.on_close()
