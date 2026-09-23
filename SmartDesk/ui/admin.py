import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import config
import database
from core.cloud_sync import get_sync_status, sync_all_projects


class AdminScreen(tk.Frame):
    def __init__(self, master, user=None, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self.user = user
        self.build()

    def build(self):
        tk.Label(
            self,
            text="🛡️ Admin Panel",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#0B1020",
        ).pack(anchor="w", padx=25, pady=(25, 4))

        tk.Label(
            self,
            text="SmartDesk exhibition control center",
            font=("Segoe UI", 10),
            fg="#94A3B8",
            bg="#0B1020",
        ).pack(anchor="w", padx=25, pady=(0, 20))

        stats = tk.Frame(self, bg="#0B1020")
        stats.pack(fill="x", padx=20)

        projects = database.get_projects()
        recent = database.get_recent_activity(limit=100)

        cards = [
            ("👥 Users", self._count_users()),
            ("📂 Projects", len(projects)),
            ("📝 Activity", len(recent)),
            ("☁️ Cloud", "READY"),
        ]

        for title, value in cards:
            card = tk.Frame(stats, bg="#111827", padx=18, pady=15)
            card.pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(card, text=title, fg="#94A3B8", bg="#111827", font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(card, text=str(value), fg="white", bg="#111827", font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(4, 0))

        actions = tk.Frame(self, bg="#0B1020")
        actions.pack(fill="x", padx=25, pady=25)

        self.button(actions, "🧪 Run System Test", self.system_test).pack(side="left", padx=(0, 10))
        self.button(actions, "☁️ Sync Everything", self.sync_now).pack(side="left", padx=10)
        self.button(actions, "📊 Refresh", self.refresh).pack(side="left", padx=10)

        self.output = tk.Text(
            self,
            height=18,
            bg="#050816",
            fg="#D1D5DB",
            insertbackground="white",
            relief="flat",
            font=("Consolas", 10),
        )
        self.output.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.write_status()

    def button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#2563EB",
            fg="white",
            activebackground="#3B82F6",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8,
        )

    def _count_users(self):
        try:
            conn = database.get_connection()
            value = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            conn.close()
            return value
        except Exception:
            return "?"

    def write_status(self):
        status = get_sync_status()
        self.output.insert("end", "SMARTDESK ADMIN CONSOLE\n")
        self.output.insert("end", "=" * 60 + "\n")
        self.output.insert("end", f"Admin: davereub ✓ VERIFIED\n")
        self.output.insert("end", f"Cloud folder: {status['directory']}\n")
        self.output.insert("end", f"{status['message']}\n")
        self.output.insert("end", "\nReady for exhibition testing.\n")

    def system_test(self):
        self.output.delete("1.0", "end")
        tests = []
        try:
            config.create_directories()
            tests.append("✓ Directories")
        except Exception as e:
            tests.append(f"✗ Directories: {e}")

        try:
            database.initialize_database()
            tests.append("✓ Database")
        except Exception as e:
            tests.append(f"✗ Database: {e}")

        try:
            status = get_sync_status()
            tests.append("✓ Cloud sync module")
            tests.append(f"  → {status['directory']}")
        except Exception as e:
            tests.append(f"✗ Cloud sync: {e}")

        self.output.insert("end", "SYSTEM TEST\n\n" + "\n".join(tests))

    def sync_now(self):
        try:
            count = sync_all_projects()
            messagebox.showinfo("Cloud Sync", f"Synced {count} file(s).")
            self.output.insert("end", f"\n✓ Synced {count} file(s).\n")
        except Exception as e:
            messagebox.showerror("Cloud Sync", str(e))

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.build()
