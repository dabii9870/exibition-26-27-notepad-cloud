"""
SmartDesk Statistics Dashboard.
"""

import tkinter as tk

from database import get_stat, get_recent_activity


class StatisticsScreen(tk.Frame):
    """Displays SmartDesk usage statistics."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self._build()

    def _build(self):
        tk.Label(
            self, text="📊 Statistics",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(anchor="w", padx=30, pady=25)

        grid = tk.Frame(self, bg="#0B1020")
        grid.pack(fill="x", padx=25)

        stats = [
            ("Files Saved", "files_saved"),
            ("Python Runs", "python_runs"),
            ("Focus Minutes", "focus_minutes"),
            ("Quiz Attempts", "quiz_attempts"),
            ("Correct Answers", "quiz_correct"),
        ]

        for index, (label, key) in enumerate(stats):
            card = tk.Frame(grid, bg="#111827", padx=20, pady=18)
            card.grid(
                row=0, column=index, sticky="ew", padx=5
            )
            grid.columnconfigure(index, weight=1)

            tk.Label(
                card, text=str(get_stat(key)),
                font=("Segoe UI", 22, "bold"),
                fg="#38BDF8", bg="#111827"
            ).pack()

            tk.Label(
                card, text=label,
                font=("Segoe UI", 9),
                fg="#94A3B8", bg="#111827"
            ).pack()

        activity = tk.Frame(self, bg="#111827")
        activity.pack(fill="both", expand=True, padx=30, pady=25)

        tk.Label(
            activity, text="Recent Activity",
            font=("Segoe UI", 15, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w", padx=15, pady=15)

        listbox = tk.Listbox(
            activity, bg="#0F172A", fg="#CBD5E1",
            selectbackground="#2563EB", relief="flat"
        )
        listbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for item in get_recent_activity():
            description = item["description"] or item["activity_type"]
            listbox.insert(
                "end",
                f"{item['created_at']}  •  {description}"
            )
