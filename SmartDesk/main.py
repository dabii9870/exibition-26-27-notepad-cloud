import tkinter as tk
from tkinter import messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

import config
import database

from core.admin_bootstrap import ensure_admin_account, is_admin

from ui.login import LoginScreen
from ui.loading import LoadingScreen
from ui.home import HomeScreen
from ui.editor import EditorScreen
from ui.file_manager import FileManagerScreen
from ui.study import StudyScreen
from ui.focus import FocusScreen
from ui.tools import ToolsScreen
from ui.statistics import StatisticsScreen
from ui.vault import VaultScreen
from ui.settings import SettingsScreen
from ui.admin import AdminScreen


class SmartDesk(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SmartDesk")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)

        self.current_user = None
        self.current_screen = None
        self.content = None
        self.nav_buttons = {}
        self.icon_image = None
        self.logo_image = None

        try:
            config.create_directories()
            database.initialize_database()
            ensure_admin_account(database)
            self.load_app_icon()
        except Exception as error:
            messagebox.showerror(
                "SmartDesk",
                f"SmartDesk could not initialize:\n\n{error}"
            )
            self.destroy()
            return

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_loading()

    def load_app_icon(self):
        icon_path = Path(config.ICON_PATH)
        if not icon_path.exists():
            return

        try:
            self.icon_image = tk.PhotoImage(file=str(icon_path))
            self.iconphoto(True, self.icon_image)
        except Exception:
            pass

    def load_logo(self, size=(180, 145)):
        logo_path = Path(config.LOGO_PATH)
        if not logo_path.exists() or Image is None:
            return None

        try:
            image = Image.open(logo_path).convert("RGBA")
            image.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception:
            return None

    def show_loading(self):
        self.clear_window()
        loading = LoadingScreen(self, on_complete=self.show_login)
        loading.pack(fill="both", expand=True)
        self.current_screen = loading

    def show_login(self):
        self.clear_window()
        login = LoginScreen(self, on_login=self.login_success)
        login.pack(fill="both", expand=True)
        self.current_screen = login

    def login_success(self, user):
        try:
            username = user["username"]
        except Exception:
            try:
                username = user[1]
            except Exception:
                username = user

        if hasattr(user, "keys"):
            self.current_user = {key: user[key] for key in user.keys()}
        else:
            self.current_user = {"username": username}

        self.current_user.setdefault("username", username)
        self.build_workspace()

    def build_workspace(self):
        self.clear_window()
        self.configure(bg="#0B1020")

        sidebar = tk.Frame(self, bg="#111827", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo = self.load_logo((195, 155))
        if logo:
            self.logo_image = logo
            tk.Label(
                sidebar,
                image=logo,
                bg="#111827",
                bd=0,
            ).pack(pady=(12, 0))
        else:
            tk.Label(
                sidebar,
                text="💻 SmartDesk",
                font=("Segoe UI", 17, "bold"),
                fg="white",
                bg="#111827",
            ).pack(pady=22)

        username = "User"
        try:
            username = self.current_user["username"]
        except Exception:
            pass

        verified = False
        try:
            verified = bool(self.current_user["verified"])
        except Exception:
            pass

        user_text = f"👤 {username}"
        if verified:
            user_text += "  ✓"

        tk.Label(
            sidebar,
            text=user_text,
            font=("Segoe UI", 10, "bold" if verified else "normal"),
            fg="#60A5FA" if verified else "#94A3B8",
            bg="#111827",
        ).pack(anchor="w", padx=20, pady=(0, 16))

        navigation = [
            ("🏠  Home", "home"),
            ("📝  Editor", "editor"),
            ("📂  Files", "files"),
            ("📚  Study", "study"),
            ("⏱️  Focus", "focus"),
            ("🔎  Search & Tools", "tools"),
            ("📊  Statistics", "statistics"),
            ("🔐  Private Vault", "vault"),
            ("⚙️  Settings", "settings"),
        ]

        if is_admin(self.current_user.get("username") if isinstance(self.current_user, dict) else self.current_user):
            navigation.append(("🛡️  Admin Panel ✓", "admin"))

        for text, page in navigation:
            button = tk.Button(
                sidebar,
                text=text,
                command=lambda p=page: self.navigate(p),
                anchor="w",
                bg="#111827",
                fg="#CBD5E1",
                activebackground="#1E293B",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 10),
                padx=20,
                pady=9,
            )
            button.pack(fill="x", padx=10, pady=1)
            self.nav_buttons[page] = button

        tk.Frame(sidebar, bg="#111827").pack(fill="both", expand=True)

        tk.Button(
            sidebar,
            text="🚪  Log Out",
            command=self.logout,
            anchor="w",
            bg="#111827",
            fg="#F87171",
            activebackground="#1E293B",
            activeforeground="#FCA5A5",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10),
            padx=20,
            pady=12,
        ).pack(fill="x", padx=10, pady=10)

        right_side = tk.Frame(self, bg="#0B1020")
        right_side.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(right_side, bg="#111827", height=58)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.page_title = tk.Label(
            topbar,
            text="Home",
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg="#111827",
        )
        self.page_title.pack(side="left", padx=20)

        tk.Button(
            topbar,
            text="🔎 Search",
            command=lambda: self.navigate("tools"),
            bg="#1E293B",
            fg="#CBD5E1",
            activebackground="#334155",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=7,
        ).pack(side="right", padx=15)

        self.content = tk.Frame(right_side, bg="#0B1020")
        self.content.pack(fill="both", expand=True)

        self.navigate("home")

    def background_cloud_sync(self):
        return

    def navigate(self, page, **kwargs):
        if self.content is None:
            return

        for widget in self.content.winfo_children():
            widget.destroy()

        titles = {
            "home": "Home",
            "editor": "Editor",
            "files": "File Manager",
            "study": "Study Center",
            "focus": "Focus Timer",
            "tools": "Search & Tools",
            "statistics": "Statistics",
            "vault": "Private Vault",
            "settings": "Settings",
            "admin": "Admin Panel",
        }
        self.page_title.config(text=titles.get(page, "SmartDesk"))

        if page == "home":
            screen = HomeScreen(self.content, on_open=self.handle_home_open)
        elif page == "editor":
            screen = EditorScreen(
                self.content,
                file_path=kwargs.get("file_path"),
                on_close=self.close_editor,
            )
        elif page == "files":
            screen = FileManagerScreen(self.content, on_open=self.handle_project_open)
        elif page == "study":
            screen = StudyScreen(self.content)
        elif page == "focus":
            screen = FocusScreen(self.content)
        elif page == "tools":
            screen = ToolsScreen(self.content)
        elif page == "statistics":
            screen = StatisticsScreen(self.content)
        elif page == "vault":
            screen = VaultScreen(self.content)
        elif page == "settings":
            screen = SettingsScreen(self.content, on_theme_change=self.change_theme)
        elif page == "admin" and is_admin(self.current_user):
            screen = AdminScreen(self.content, user=self.current_user)
        else:
            screen = HomeScreen(self.content, on_open=self.handle_home_open)

        screen.pack(fill="both", expand=True)
        self.current_screen = screen

    def handle_home_open(self, item):
        if item == "files":
            self.navigate("files")
            return

        try:
            path = item["path"]
        except (TypeError, KeyError, IndexError):
            path = item if isinstance(item, str) else None

        if path:
            self.open_path(path)

    def handle_project_open(self, project):
        try:
            path = project["path"]
        except (TypeError, KeyError, IndexError):
            return
        self.open_path(path)

    def open_path(self, path):
        path = Path(path)
        if path.is_dir():
            self.navigate("files")
        elif path.is_file():
            self.navigate("editor", file_path=str(path))
        else:
            messagebox.showwarning(
                "SmartDesk",
                f"File or project could not be found:\n\n{path}",
            )

    def close_editor(self):
        self.navigate("home")

    def change_theme(self, theme):
        try:
            database.set_setting("theme", theme)
        except Exception:
            pass
        self.build_workspace()

    def logout(self):
        if not messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            return
        self.current_user = None
        self.show_login()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.current_screen = None
        self.content = None
        self.nav_buttons = {}

    def on_close(self):
        try:
            if self.current_screen:
                save_method = getattr(self.current_screen, "save_file", None)
                if callable(save_method) and getattr(self.current_screen, "file_path", None):
                    try:
                        save_method()
                    except Exception:
                        pass
        finally:
            self.destroy()


def main():
    app = SmartDesk()
    app.mainloop()


if __name__ == "__main__":
    main()
