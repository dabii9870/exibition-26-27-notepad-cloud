import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


class BoredScreen(tk.Frame):
    def __init__(self, parent, on_exit=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_exit = on_exit
        self.app = self.winfo_toplevel()
        self.process = None
        self.poll_job = None

        script = Path(__file__).resolve().parents[1] / "exibition.py"
        try:
            self.process = subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(script.parent),
            )
            self.app.withdraw()
            self.poll_job = self.after(300, self._check_activity)
        except Exception as error:
            messagebox.showerror("Bored", f"Could not open activities:\n\n{error}")
            self._return_home()

    def _check_activity(self):
        self.poll_job = None
        if self.process and self.process.poll() is None:
            self.poll_job = self.after(300, self._check_activity)
            return
        self._return_home()

    def _return_home(self):
        try:
            self.app.deiconify()
            self.app.lift()
        except tk.TclError:
            return
        if self.on_exit:
            self.on_exit()