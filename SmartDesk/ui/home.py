import tkinter as tk
from tkinter import messagebox

import database


class HomeScreen(tk.Frame):

    def __init__(
        self,
        parent,
        on_open=None,
        on_new_project=None,
        **kwargs
    ):

        super().__init__(
            parent,
            bg="#0B1020"
        )

        self.on_open = on_open
        self.on_new_project = on_new_project

        self.build_ui()

        self.refresh()

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):

        # -----------------------------------------------------
        # Header
        # -----------------------------------------------------

        header = tk.Frame(
            self,
            bg="#0B1020"
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(25, 15)
        )

        tk.Label(
            header,
            text="🏠 Home",
            font=(
                "Segoe UI",
                24,
                "bold"
            ),
            fg="white",
            bg="#0B1020"
        ).pack(
            anchor="w"
        )

        tk.Label(
            header,
            text="Welcome back to SmartDesk",
            font=(
                "Segoe UI",
                11
            ),
            fg="#94A3B8",
            bg="#0B1020"
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

        # -----------------------------------------------------
        # New project button
        # -----------------------------------------------------

        tk.Button(
            header,
            text="＋ New Project",
            command=self.new_project,
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=16,
            pady=9
        ).pack(
            anchor="e",
            pady=(10, 0)
        )

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        stats_frame = tk.Frame(
            self,
            bg="#0B1020"
        )

        stats_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.projects_card = self.create_card(
            stats_frame,
            "📁",
            "Projects",
            "0"
        )

        self.focus_card = self.create_card(
            stats_frame,
            "⏱",
            "Focus Minutes",
            "0"
        )

        self.quiz_card = self.create_card(
            stats_frame,
            "📝",
            "Quiz Attempts",
            "0"
        )

        self.notes_card = self.create_card(
            stats_frame,
            "📒",
            "Notes",
            "0"
        )

        self.projects_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        self.focus_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8
        )

        self.quiz_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8
        )

        self.notes_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0)
        )

        # -----------------------------------------------------
        # Content area
        # -----------------------------------------------------

        content = tk.Frame(
            self,
            bg="#0B1020"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        # -----------------------------------------------------
        # Pinned projects
        # -----------------------------------------------------

        pinned_frame = tk.Frame(
            content,
            bg="#111827"
        )

        pinned_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        tk.Label(
            pinned_frame,
            text="📌 Pinned Projects",
            font=(
                "Segoe UI",
                13,
                "bold"
            ),
            fg="white",
            bg="#111827"
        ).pack(
            anchor="w",
            padx=15,
            pady=15
        )

        self.pinned_list = tk.Listbox(
            pinned_frame,
            bg="#0F172A",
            fg="#E2E8F0",
            selectbackground="#2563EB",
            selectforeground="white",
            font=(
                "Segoe UI",
                10
            ),
            relief="flat",
            bd=0
        )

        self.pinned_list.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.pinned_list.bind(
            "<Double-Button-1>",
            self.open_pinned
        )

        # -----------------------------------------------------
        # Recent files
        # -----------------------------------------------------

        recent_frame = tk.Frame(
            content,
            bg="#111827"
        )

        recent_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(8, 0)
        )

        tk.Label(
            recent_frame,
            text="🕘 Recently Opened",
            font=(
                "Segoe UI",
                13,
                "bold"
            ),
            fg="white",
            bg="#111827"
        ).pack(
            anchor="w",
            padx=15,
            pady=15
        )

        self.recent_list = tk.Listbox(
            recent_frame,
            bg="#0F172A",
            fg="#E2E8F0",
            selectbackground="#2563EB",
            selectforeground="white",
            font=(
                "Segoe UI",
                10
            ),
            relief="flat",
            bd=0
        )

        self.recent_list.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.recent_list.bind(
            "<Double-Button-1>",
            self.open_recent
        )

    # =========================================================
    # STAT CARD
    # =========================================================

    def create_card(
        self,
        parent,
        icon,
        title,
        value
    ):

        card = tk.Frame(
            parent,
            bg="#111827",
            height=105
        )

        card.pack_propagate(
            False
        )

        tk.Label(
            card,
            text=icon,
            font=(
                "Segoe UI Emoji",
                18
            ),
            bg="#111827",
            fg="white"
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 0)
        )

        value_label = tk.Label(
            card,
            text=value,
            font=(
                "Segoe UI",
                18,
                "bold"
            ),
            bg="#111827",
            fg="white"
        )

        value_label.pack(
            anchor="w",
            padx=15
        )

        tk.Label(
            card,
            text=title,
            font=(
                "Segoe UI",
                9
            ),
            bg="#111827",
            fg="#94A3B8"
        ).pack(
            anchor="w",
            padx=15
        )

        # Store the value label so refresh()
        # can update it later.

        card.value_label = value_label

        return card

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):

        try:

            projects = database.get_projects()

        except Exception:

            projects = []

        try:

            pinned = database.get_pinned_projects()

        except Exception:

            pinned = []

        try:

            recent = database.get_recent_files(
                10
            )

        except Exception:

            recent = []

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        try:

            self.projects_card.value_label.config(
                text=str(
                    len(projects)
                )
            )

            self.focus_card.value_label.config(
                text=str(
                    database.get_stat(
                        "focus_minutes"
                    )
                )
            )

            self.quiz_card.value_label.config(
                text=str(
                    database.get_stat(
                        "quiz_attempts"
                    )
                )
            )

            self.notes_card.value_label.config(
                text=str(
                    len(database.get_notes())
                )
            )

        except Exception:
            pass

        # -----------------------------------------------------
        # Pinned
        # -----------------------------------------------------

        self.pinned_list.delete(
            0,
            "end"
        )

        self.pinned_projects = list(
            pinned
        )

        if not pinned:

            self.pinned_list.insert(
                "end",
                "No pinned projects yet."
            )

        else:

            for project in pinned:

                self.pinned_list.insert(
                    "end",
                    f"📌 {project['name']}"
                )

        # -----------------------------------------------------
        # Recent
        # -----------------------------------------------------

        self.recent_list.delete(
            0,
            "end"
        )

        self.recent_files = list(
            recent
        )

        if not recent:

            self.recent_list.insert(
                "end",
                "No recently opened projects."
            )

        else:

            for item in recent:

                path = item["path"]

                if path.startswith(
                    "smartdesk://"
                ):

                    name = path.split(
                        "/"
                    )[-1]

                else:

                    name = path

                self.recent_list.insert(
                    "end",
                    f"📝 {name}"
                )

    # =========================================================
    # NEW PROJECT
    # =========================================================

    def new_project(self):

        if self.on_new_project:

            self.on_new_project()

            return

        if self.on_open:

            self.on_open(
                None
            )

    # =========================================================
    # OPEN PINNED
    # =========================================================

    def open_pinned(self, event=None):

        selection = self.pinned_list.curselection()

        if not selection:
            return

        index = selection[0]

        if index >= len(
            self.pinned_projects
        ):
            return

        project = self.pinned_projects[
            index
        ]

        if self.on_open:

            self.on_open(
                project
            )

    # =========================================================
    # OPEN RECENT
    # =========================================================

    def open_recent(self, event=None):

        selection = self.recent_list.curselection()

        if not selection:
            return

        index = selection[0]

        if index >= len(
            self.recent_files
        ):
            return

        item = self.recent_files[
            index
        ]

        try:

            project = database.get_project_by_path(
                item["path"]
            )

        except Exception:

            project = None

        if project and self.on_open:

            self.on_open(
                project
            )

    # =========================================================
    # PUBLIC REFRESH
    # =========================================================

    def update(self):

        self.refresh()