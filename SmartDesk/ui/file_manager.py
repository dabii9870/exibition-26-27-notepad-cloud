"""
SmartDesk File and Project Manager.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from config import PROJECTS_DIR
from database import (
    save_project, get_projects, set_project_pinned,
    add_recent_file
)


class FileManagerScreen(tk.Frame):
    """Project/file manager."""

    def __init__(self, master, on_open=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.on_open = on_open
        self._build()
        self.refresh()

    def _build(self):
        toolbar = tk.Frame(self, bg="#111827", padx=12, pady=10)
        toolbar.pack(fill="x")

        buttons = [
            ("New Project", self.new_project),
            ("Add Existing", self.add_existing),
            ("Refresh", self.refresh),
        ]

        for text, command in buttons:
            tk.Button(
                toolbar, text=text, command=command,
                bg="#1E293B", fg="white", relief="flat",
                cursor="hand2", padx=12
            ).pack(side="left", padx=3)

        self.listbox = tk.Listbox(
            self, bg="#0F172A", fg="#E2E8F0",
            selectbackground="#2563EB",
            font=("Segoe UI", 11), relief="flat"
        )
        self.listbox.pack(fill="both", expand=True, padx=20, pady=20)
        self.listbox.bind("<Double-Button-1>", self.open_selected)

    def refresh(self):
        self.listbox.delete(0, "end")
        self.projects = get_projects()

        for project in self.projects:
            pin = "📌 " if project["is_pinned"] else ""
            self.listbox.insert(
                "end",
                f"{pin}{project['name']}  |  {project['path']}"
            )

    def new_project(self):
        directory = filedialog.askdirectory(
            title="Choose project folder"
        )
        if not directory:
            return

        path = Path(directory)
        save_project(
            path.name,
            str(path),
            "project",
            False
        )
        self.refresh()

    def add_existing(self):
        path = filedialog.askopenfilename(
            title="Choose a file"
        )
        if not path:
            return

        file_path = Path(path)
        save_project(
            file_path.stem,
            str(file_path),
            file_path.suffix.lstrip(".") or "text",
            False
        )
        add_recent_file(str(file_path))
        self.refresh()

    def open_selected(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return

        project = self.projects[selection[0]]

        if self.on_open:
            self.on_open(project)

    def toggle_pin(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        project = self.projects[selection[0]]
        set_project_pinned(
            project["path"],
            not bool(project["is_pinned"])
        )
        self.refresh()
