"""
SmartDesk Focus Timer.
"""

import tkinter as tk
from tkinter import messagebox

from config import (
    DEFAULT_FOCUS_MINUTES,
    DEFAULT_SHORT_BREAK_MINUTES,
)
from database import get_setting, set_setting, save_focus_session, log_activity


class FocusScreen(tk.Frame):
    """Pomodoro-style focus timer."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        try:
            configured_seconds = get_setting("focus_duration_seconds")
            if configured_seconds is None:
                configured_seconds = int(
                    get_setting("focus_minutes", DEFAULT_FOCUS_MINUTES)
                ) * 60
            configured_seconds = int(configured_seconds)
        except Exception:
            configured_seconds = DEFAULT_FOCUS_MINUTES * 60
        self.focus_duration_seconds = max(1, min(10800, configured_seconds))
        self.focus_minutes = max(1, (self.focus_duration_seconds + 59) // 60)
        self.remaining = self.focus_duration_seconds
        self.running = False
        self.mode = "Focus"
        self._build()
        self._update_display()

    def _build(self):
        tk.Label(
            self, text="⏱️ Focus Timer",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(pady=(32, 10))

        self.mode_label = tk.Label(
            self, text="Focus",
            font=("Segoe UI", 14, "bold"),
            fg="#38BDF8", bg="#0B1020"
        )
        self.mode_label.pack()

        duration = tk.Frame(self, bg="#0B1020")
        duration.pack(pady=(16, 0))

        self.minutes_value = tk.StringVar(
            value=str(self.focus_duration_seconds // 60)
        )
        self.seconds_value = tk.StringVar(
            value=str(self.focus_duration_seconds % 60)
        )
        self.minutes_input = self._duration_input(
            duration,
            "Minutes",
            self.minutes_value,
            0,
            180,
        )
        self.seconds_input = self._duration_input(
            duration,
            "Seconds",
            self.seconds_value,
            0,
            59,
        )

        tk.Button(
            duration,
            text="Set Time",
            command=self.apply_duration,
            bg="#1E293B",
            fg="white",
            activebackground="#334155",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
        ).pack(side="left", padx=(12, 0), pady=(19, 0))
        self.minutes_input.bind("<Return>", self.apply_duration)
        self.seconds_input.bind("<Return>", self.apply_duration)

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

    def _duration_input(self, parent, label, variable, minimum, maximum):
        field = tk.Frame(parent, bg="#0B1020")
        field.pack(side="left", padx=6)
        tk.Label(
            field,
            text=label,
            font=("Segoe UI", 10),
            fg="#CBD5E1",
            bg="#0B1020",
        ).pack(anchor="w", pady=(0, 4))
        spinbox = tk.Spinbox(
            field,
            from_=minimum,
            to=maximum,
            width=5,
            textvariable=variable,
            font=("Segoe UI", 12),
            justify="center",
            bg="#172033",
            fg="white",
            insertbackground="white",
            buttonbackground="#334155",
            relief="flat",
        )
        spinbox.pack(ipady=6)
        return spinbox

    def apply_duration(self, event=None):
        try:
            minutes = int(self.minutes_value.get())
            seconds = int(self.seconds_value.get())
        except ValueError:
            messagebox.showerror(
                "Focus Timer",
                "Enter whole numbers for minutes and seconds.",
            )
            self._restore_duration_inputs()
            return "break" if event else False

        if not 0 <= minutes <= 180 or not 0 <= seconds <= 59 or minutes * 60 + seconds == 0:
            messagebox.showerror(
                "Focus Timer",
                "Enter a time from 00:01 through 180:00.",
            )
            self._restore_duration_inputs()
            return "break" if event else False

        total_seconds = minutes * 60 + seconds
        try:
            set_setting("focus_duration_seconds", str(total_seconds))
            set_setting("focus_minutes", str((total_seconds + 59) // 60))
        except Exception as error:
            messagebox.showerror("Focus Timer", f"Could not save focus length:\n\n{error}")
            return "break" if event else False

        self.focus_duration_seconds = total_seconds
        self.focus_minutes = (total_seconds + 59) // 60
        self.mode = "Focus"
        self.remaining = total_seconds
        self.mode_label.config(text="Focus")
        self._update_display()
        return "break" if event else True

    def _restore_duration_inputs(self):
        self.minutes_value.set(str(self.focus_duration_seconds // 60))
        self.seconds_value.set(str(self.focus_duration_seconds % 60))

    def toggle(self):
        if not self.running and not self.apply_duration():
            return
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
                minutes = self.focus_minutes
                save_focus_session(minutes)
                log_activity(
                    "focus",
                    f"Completed {self.focus_duration_seconds // 60:02d}:"
                    f"{self.focus_duration_seconds % 60:02d} focus session",
                )
                self.mode = "Break"
                self.remaining = DEFAULT_SHORT_BREAK_MINUTES * 60
            else:
                self.mode = "Focus"
                self.remaining = self.focus_duration_seconds

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
        self.remaining = self.focus_duration_seconds
        self._restore_duration_inputs()
        self.mode_label.config(text="Focus")
        self.start_button.config(text="Start")
        self._update_display()
