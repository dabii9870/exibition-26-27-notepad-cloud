"""
SmartDesk Focus Timer.
"""

import tkinter as tk

from config import (
    DEFAULT_FOCUS_MINUTES,
    DEFAULT_SHORT_BREAK_MINUTES,
)
from database import save_focus_session, log_activity


class FocusScreen(tk.Frame):
    """Pomodoro-style focus timer."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.remaining = DEFAULT_FOCUS_MINUTES * 60
        self.running = False
        self.mode = "Focus"
        self._build()
        self._update_display()

    def _build(self):
        tk.Label(
            self, text="⏱️ Focus Timer",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(pady=(60, 10))

        self.mode_label = tk.Label(
            self, text="Focus",
            font=("Segoe UI", 14, "bold"),
            fg="#38BDF8", bg="#0B1020"
        )
        self.mode_label.pack()

        self.timer = tk.Label(
            self, text="25:00",
            font=("Segoe UI", 64, "bold"),
            fg="white", bg="#0B1020"
        )
        self.timer.pack(pady=20)

        controls = tk.Frame(self, bg="#0B1020")
        controls.pack()

        self.start_button = tk.Button(
            controls, text="Start", command=self.toggle,
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=25, pady=10
        )
        self.start_button.pack(side="left", padx=5)

        tk.Button(
            controls, text="Reset", command=self.reset,
            bg="#334155", fg="white", relief="flat",
            cursor="hand2", padx=25, pady=10
        ).pack(side="left", padx=5)

    def toggle(self):
        self.running = not self.running
        self.start_button.config(
            text="Pause" if self.running else "Start"
        )
        if self.running:
            self._tick()

    def _tick(self):
        if not self.running:
            return

        if self.remaining <= 0:
            if self.mode == "Focus":
                minutes = DEFAULT_FOCUS_MINUTES
                save_focus_session(minutes)
                log_activity("focus", f"Completed {minutes}-minute focus session")
                self.mode = "Break"
                self.remaining = DEFAULT_SHORT_BREAK_MINUTES * 60
            else:
                self.mode = "Focus"
                self.remaining = DEFAULT_FOCUS_MINUTES * 60

            self.mode_label.config(text=self.mode)

        else:
            self.remaining -= 1

        self._update_display()

        if self.running:
            self.after(1000, self._tick)

    def _update_display(self):
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.timer.config(text=f"{minutes:02d}:{seconds:02d}")

    def reset(self):
        self.running = False
        self.mode = "Focus"
        self.remaining = DEFAULT_FOCUS_MINUTES * 60
        self.mode_label.config(text="Focus")
        self.start_button.config(text="Start")
        self._update_display()
