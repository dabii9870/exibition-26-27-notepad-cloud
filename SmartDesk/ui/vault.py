"""
SmartDesk Private Vault UI.

Provides the vault interface. Actual encryption/storage can
be connected to a dedicated encrypted-file service later.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path

import database
from config import VAULT_DIR
from core.security import generate_password_hash, verify_password


class VaultScreen(tk.Frame):
    """Private vault interface."""

    def __init__(self, master, on_open_file=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.unlocked = False
        self.password_hash = database.get_setting("vault_password_hash")
        self.on_open_file = on_open_file
        self._build()

    def _build(self):
        tk.Label(
            self, text="🔐 Private Vault",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(anchor="w", padx=30, pady=25)

        self.status = tk.Label(
            self, text="Vault locked",
            font=("Segoe UI", 12),
            fg="#F59E0B", bg="#0B1020"
        )
        self.status.pack(anchor="w", padx=30)

        card = tk.Frame(self, bg="#111827", padx=25, pady=25)
        card.pack(fill="x", padx=30, pady=20)

        tk.Label(
            card, text="Vault Password",
            fg="#CBD5E1", bg="#111827"
        ).pack(anchor="w")

        self.password = tk.Entry(
            card, show="•", font=("Segoe UI", 12),
            bg="#1E293B", fg="white",
            insertbackground="white", relief="flat"
        )
        self.password.pack(fill="x", pady=8, ipady=8)

        buttons = tk.Frame(card, bg="#111827")
        buttons.pack(fill="x", pady=10)

        self.set_password_button = tk.Button(
            buttons, text="Set Password",
            command=self.set_password,
            bg="#7C3AED", fg="white", relief="flat",
            cursor="hand2", padx=15, pady=8
        )
        self.set_password_button.pack(side="left", padx=(0, 6))
        if self.password_hash:
            self.set_password_button.config(state="disabled")

        tk.Button(
            buttons, text="Unlock",
            command=self.unlock,
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=15, pady=8
        ).pack(side="left")

        self.content = tk.Frame(self, bg="#111827", padx=25, pady=25)
        self.content.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        tk.Label(
            self.content,
            text="Unlock the vault to view private files.",
            fg="#64748B", bg="#111827"
        ).pack(pady=30)

    def set_password(self):
        if self.password_hash:
            messagebox.showinfo("Vault", "A vault password has already been set and cannot be changed.")
            return

        password = self.password.get()

        if len(password) < 4:
            messagebox.showwarning("Vault", "Password must be at least 4 characters.")
            return

        password_hash = generate_password_hash(password)
        try:
            database.set_setting("vault_password_hash", password_hash)
        except Exception as error:
            messagebox.showerror("Vault", f"Could not save the vault password:\n\n{error}")
            return

        self.password_hash = password_hash
        self.set_password_button.config(state="disabled")
        self.unlocked = True
        self._show_unlocked()

    def unlock(self):
        if not self.password_hash:
            messagebox.showinfo("Vault", "Set a vault password first.")
            return

        if verify_password(self.password.get(), self.password_hash):
            self.unlocked = True
            self._show_unlocked()
        else:
            messagebox.showerror("Vault", "Incorrect password.")

    def _show_unlocked(self):
        self.status.config(
            text="Vault unlocked",
            fg="#22C55E"
        )

        for widget in self.content.winfo_children():
            widget.destroy()

        VAULT_DIR.mkdir(parents=True, exist_ok=True)

        tk.Button(
            self.content, text="Add Private File",
            command=self.add_file,
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=15, pady=8
        ).pack(anchor="w")

        tk.Label(
            self.content,
            text=f"Private storage: {VAULT_DIR}",
            fg="#94A3B8", bg="#111827"
        ).pack(anchor="w", pady=15)

        tk.Label(
            self.content,
            text="Saved files",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#111827"
        ).pack(anchor="w", pady=(0, 8))

        files = sorted(
            (path for path in VAULT_DIR.iterdir() if path.is_file()),
            key=lambda path: path.name.casefold(),
        )
        if not files:
            tk.Label(
                self.content,
                text="No files in the vault yet.",
                fg="#64748B", bg="#111827"
            ).pack(anchor="w")

        for path in files:
            row = tk.Frame(self.content, bg="#1E293B", padx=10, pady=6)
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=path.name,
                fg="#CBD5E1", bg="#1E293B",
                anchor="w",
            ).pack(side="left", fill="x", expand=True)
            tk.Button(
                row,
                text="Open",
                command=lambda file_path=path: self.open_file(file_path),
                bg="#2563EB", fg="white", relief="flat",
                cursor="hand2", padx=12, pady=5,
            ).pack(side="right")

    def open_file(self, path):
        if not self.unlocked or self.on_open_file is None:
            return
        self.on_open_file(path)

    def add_file(self):
        if not self.unlocked:
            return

        source = filedialog.askopenfilename(
            title="Choose private file"
        )

        if not source:
            return

        try:
            source_path = Path(source)
            destination = VAULT_DIR / source_path.name
            destination.write_bytes(source_path.read_bytes())
            messagebox.showinfo("Vault", "File added to the vault.")
            self._show_unlocked()
        except Exception as error:
            messagebox.showerror("Vault", str(error))
