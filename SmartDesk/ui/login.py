"""
SmartDesk Login and Account Creation UI.
"""

import tkinter as tk
from tkinter import messagebox

from database import get_connection
from core.security import generate_password_hash, verify_password


class LoginScreen(tk.Frame):
    """Login/account creation screen."""

    def __init__(self, master, on_login=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.on_login = on_login
        self.show_password = False
        self._build()

    def _build(self):
        card = tk.Frame(self, bg="#111827", padx=45, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card, text="SmartDesk", font=("Segoe UI", 30, "bold"),
            fg="white", bg="#111827"
        ).pack(pady=(0, 5))

        tk.Label(
            card, text="Sign in to your workspace",
            font=("Segoe UI", 11), fg="#94A3B8", bg="#111827"
        ).pack(pady=(0, 5))

        tk.Label(
            card,
            text="✓ Verified admin access",
            fg="#34D399",
            bg="#111827",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(0, 20))

        tk.Label(card, text="Username", fg="#CBD5E1", bg="#111827",
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.username = tk.Entry(
            card, width=32, font=("Segoe UI", 12),
            bg="#1E293B", fg="white", insertbackground="white",
            relief="flat"
        )
        self.username.pack(pady=(5, 15), ipady=8)

        tk.Label(card, text="Password", fg="#CBD5E1", bg="#111827",
                 font=("Segoe UI", 10)).pack(anchor="w")
        password_row = tk.Frame(card, bg="#111827")
        password_row.pack(fill="x", pady=(5, 20))

        self.password = tk.Entry(
            password_row, width=25, show="•", font=("Segoe UI", 12),
            bg="#1E293B", fg="white", insertbackground="white",
            relief="flat"
        )
        self.password.pack(side="left", ipady=8)

        tk.Button(
            password_row, text="Show", command=self.toggle_password,
            bg="#334155", fg="white", relief="flat", cursor="hand2"
        ).pack(side="left", padx=(6, 0), ipady=7)

        tk.Button(
            card, text="Sign In", command=self.login,
            bg="#2563EB", fg="white", activebackground="#1D4ED8",
            relief="flat", font=("Segoe UI", 11, "bold"),
            cursor="hand2", padx=25, pady=10
        ).pack(fill="x")

        tk.Button(
            card, text="Create Account", command=self.create_account,
            bg="#1E293B", fg="#38BDF8", activebackground="#334155",
            relief="flat", font=("Segoe UI", 10),
            cursor="hand2", pady=9
        ).pack(fill="x", pady=(10, 0))

        self.username.focus_set()

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password.config(show="" if self.show_password else "•")

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            messagebox.showwarning("SmartDesk", "Enter your username and password.")
            return

        connection = get_connection()
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        connection.close()

        if row and verify_password(password, row["password_hash"]):
            if self.on_login:
                self.on_login(row)
        else:
            messagebox.showerror("SmartDesk", "Invalid username or password.")

    def create_account(self):
        username = self.username.get().strip()
        password = self.password.get()

        if len(username) < 3:
            messagebox.showwarning("SmartDesk", "Username must be at least 3 characters.")
            return

        if len(password) < 4:
            messagebox.showwarning("SmartDesk", "Password must be at least 4 characters.")
            return

        try:
            connection = get_connection()
            connection.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, datetime('now'))",
                (username, generate_password_hash(password))
            )
            connection.commit()
            connection.close()
            messagebox.showinfo("SmartDesk", "Account created. You can now sign in.")
        except Exception as error:
            messagebox.showerror("SmartDesk", f"Could not create account:\n{error}")
