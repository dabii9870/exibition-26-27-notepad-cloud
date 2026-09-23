"""
SmartDesk Home Dashboard.
"""

import tkinter as tk

from database import get_pinned_projects, get_recent_files, get_stat


class HomeScreen(tk.Frame):
    """Main SmartDesk dashboard."""

    def __init__(self, master, on_open=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.on_open = on_open
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#0B1020")
        header.pack(fill="x", padx=30, pady=25)

        tk.Label(
            header, text="Welcome to SmartDesk",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(side="left")

        tk.Button(
            header, text="Open Workspace",
            command=lambda: self._open("files"),
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=18, pady=9
        ).pack(side="right")

        stats = tk.Frame(self, bg="#0B1020")
        stats.pack(fill="x", padx=30)

        self._stat_card(stats, "Projects", len(get_pinned_projects()), 0)
        self._stat_card(stats, "Focus Minutes", get_stat("focus_minutes"), 1)
        self._stat_card(stats, "Quiz Attempts", get_stat("quiz_attempts"), 2)
        self._stat_card(stats, "Notes", get_stat("notes_created"), 3)

        body = tk.Frame(self, bg="#0B1020")
        body.pack(fill="both", expand=True, padx=30, pady=25)

        self._panel(body, "📌 Pinned Projects", self._pinned_content, 0)
        self._panel(body, "🕘 Recent Files", self._recent_content, 1)

    def _stat_card(self, parent, title, value, column):
        parent.grid_columnconfigure(column, weight=1)
        card = tk.Frame(parent, bg="#111827", padx=20, pady=18)
        card.grid(row=0, column=column, sticky="ew", padx=6)
        tk.Label(card, text=str(value), font=("Segoe UI", 24, "bold"),
                 fg="#38BDF8", bg="#111827").pack()
        tk.Label(card, text=title, font=("Segoe UI", 10),
                 fg="#94A3B8", bg="#111827").pack()

    def _panel(self, parent, title, builder, column):
        parent.grid_columnconfigure(column, weight=1)
        panel = tk.Frame(parent, bg="#111827")
        panel.grid(row=0, column=column, sticky="nsew", padx=6)
        parent.grid_rowconfigure(0, weight=1)
        tk.Label(panel, text=title, font=("Segoe UI", 14, "bold"),
                 fg="white", bg="#111827").pack(anchor="w", padx=18, pady=15)
        builder(panel)

    def _pinned_content(self, panel):
        projects = get_pinned_projects()
        if not projects:
            tk.Label(panel, text="No pinned projects yet.",
                     fg="#64748B", bg="#111827").pack(pady=20)
        for project in projects[:8]:
            tk.Button(
                panel, text=f"📁 {project['name']}",
                command=lambda p=project: self._open(p),
                anchor="w", bg="#1E293B", fg="white",
                relief="flat", cursor="hand2"
            ).pack(fill="x", padx=15, pady=3)

    def _recent_content(self, panel):
        recent = get_recent_files()
        if not recent:
            tk.Label(panel, text="No recently opened files.",
                     fg="#64748B", bg="#111827").pack(pady=20)
        for item in recent[:8]:
            tk.Button(
                panel, text=f"📄 {item['path']}",
                command=lambda p=item: self._open(p),
                anchor="w", bg="#1E293B", fg="white",
                relief="flat", cursor="hand2"
            ).pack(fill="x", padx=15, pady=3)

    def _open(self, item):
        if self.on_open:
            self.on_open(item)
