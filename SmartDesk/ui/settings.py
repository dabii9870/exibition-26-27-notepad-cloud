"""
SmartDesk Settings UI.
"""

import tkinter as tk
from tkinter import messagebox

from config import DEFAULT_THEME, THEMES, AUTOSAVE_ENABLED
from database import get_setting, set_setting


class SettingsScreen(tk.Frame):
    """Application settings."""

    def __init__(self, master, on_theme_change=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.on_theme_change = on_theme_change
        self._build()

    def _build(self):
        tk.Label(
            self, text="⚙️ Settings",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(anchor="w", padx=30, pady=25)

        appearance = tk.Frame(self, bg="#111827", padx=25, pady=20)
        appearance.pack(fill="x", padx=30, pady=10)

        tk.Label(
            appearance, text="Appearance",
            font=("Segoe UI", 15, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w", pady=(0, 15))

        theme_value = get_setting("theme", DEFAULT_THEME)
        if theme_value not in THEMES:
            theme_value = DEFAULT_THEME
        self.theme = tk.StringVar(value=theme_value)

        tk.Label(
            appearance, text="Theme",
            fg="#CBD5E1", bg="#111827"
        ).pack(side="left")

        tk.OptionMenu(
            appearance, self.theme, *THEMES.keys()
        ).pack(side="left", padx=15)

        tk.Button(
            appearance, text="Apply",
            command=self.apply_theme,
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=15
        ).pack(side="left")

        editor = tk.Frame(self, bg="#111827", padx=25, pady=20)
        editor.pack(fill="x", padx=30, pady=10)

        tk.Label(
            editor, text="Editor",
            font=("Segoe UI", 15, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w", pady=(0, 15))

        autosave = get_setting(
            "autosave",
            str(AUTOSAVE_ENABLED)
        )

        self.autosave = tk.BooleanVar(
            value=autosave.lower() == "true"
        )

        tk.Checkbutton(
            editor,
            text="Enable autosave",
            variable=self.autosave,
            command=self.save_autosave,
            bg="#111827", fg="#CBD5E1",
            selectcolor="#1E293B",
            activebackground="#111827",
            activeforeground="white"
        ).pack(anchor="w")

        account = tk.Frame(self, bg="#111827", padx=25, pady=20)
        account.pack(fill="x", padx=30, pady=10)

        tk.Label(
            account, text="Data",
            font=("Segoe UI", 15, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(
            account,
            text="SmartDesk stores application data in its data/ folder.",
            fg="#94A3B8", bg="#111827"
        ).pack(anchor="w")

    def apply_theme(self):
        theme = self.theme.get()
        set_setting("theme", theme)

        if self.on_theme_change:
            self.on_theme_change(theme)
        else:
            messagebox.showinfo(
                "SmartDesk",
                f"{theme.title()} theme saved."
            )

    def save_autosave(self):
        set_setting(
            "autosave",
            str(self.autosave.get())
        )
