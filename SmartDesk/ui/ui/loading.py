"""
SmartDesk Loading Screen.
"""

import tkinter as tk


class LoadingScreen(tk.Frame):
    """Animated startup/loading screen."""

    def __init__(self, master, on_complete=None, duration=1400, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.on_complete = on_complete
        self.progress = 0
        self.duration = duration
        self._build()
        self.after(40, self._animate)

    def _build(self):
        tk.Label(
            self, text="SmartDesk", font=("Segoe UI", 38, "bold"),
            fg="white", bg="#0B1020"
        ).pack(expand=True, pady=(180, 0))

        tk.Label(
            self, text="Learn • Create • Achieve",
            font=("Segoe UI", 12), fg="#38BDF8", bg="#0B1020"
        ).pack(pady=(0, 25))

        self.canvas = tk.Canvas(
            self, width=360, height=8, bg="#1E293B",
            highlightthickness=0
        )
        self.canvas.pack()
        self.bar = self.canvas.create_rectangle(
            0, 0, 0, 8, fill="#38BDF8", outline=""
        )

        self.status = tk.Label(
            self, text="Loading SmartDesk...",
            font=("Segoe UI", 10), fg="#64748B", bg="#0B1020"
        )
        self.status.pack(pady=12)

    def _animate(self):
        self.progress += 4
        width = int(360 * self.progress / 100)
        self.canvas.coords(self.bar, 0, 0, width, 8)

        if self.progress < 100:
            self.after(max(15, self.duration // 25), self._animate)
        elif self.on_complete:
            self.after(150, self.on_complete)
