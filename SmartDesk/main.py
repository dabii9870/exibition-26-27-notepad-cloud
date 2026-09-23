import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import config
import database

from core.admin_bootstrap import create_admin_account

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


class SmartDesk(tk.Tk):
    """Main SmartDesk application."""

    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------
        # Window
        # ---------------------------------------------------------

        self.title("SmartDesk")

        window_width = getattr(
            config,
            "WINDOW_WIDTH",
            1280
        )

        window_height = getattr(
            config,
            "WINDOW_HEIGHT",
            800
        )

        min_width = getattr(
            config,
            "MIN_WINDOW_WIDTH",
            1000
        )

        min_height = getattr(
            config,
            "MIN_WINDOW_HEIGHT",
            650
        )

        self.geometry(
            f"{window_width}x{window_height}"
        )

        self.minsize(
            min_width,
            min_height
        )

        # ---------------------------------------------------------
        # Application state
        # ---------------------------------------------------------

        self.current_user = None
        self.current_screen = None
        self.content = None
        self.nav_buttons = {}

        # ---------------------------------------------------------
        # Try to set application icon
        # ---------------------------------------------------------

        self.set_application_icon()

        # ---------------------------------------------------------
        # Initialize application
        # ---------------------------------------------------------

        try:

            # Create SmartDesk directories.
            config.create_directories()

            # Create/update database.
            database.initialize_database()

            # Create/repair the automatic admin account.
            create_admin_account()

        except Exception as error:

            messagebox.showerror(
                "SmartDesk",
                "SmartDesk could not initialize:\n\n"
                f"{error}"
            )

            self.destroy()
            return

        # ---------------------------------------------------------
        # Window close event
        # ---------------------------------------------------------

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        # ---------------------------------------------------------
        # Start loading screen
        # ---------------------------------------------------------

        self.show_loading()

    # =============================================================
    # APPLICATION ICON
    # =============================================================

    def set_application_icon(self):

        try:

            icon_path = getattr(
                config,
                "ICON_PATH",
                Path("assets") / "icon.png"
            )

            icon_path = Path(icon_path)

            if icon_path.exists():

                try:
                    from PIL import Image, ImageTk

                    image = Image.open(icon_path)

                    self.app_icon = ImageTk.PhotoImage(
                        image
                    )

                    self.iconphoto(
                        True,
                        self.app_icon
                    )

                except Exception:
                    pass

        except Exception:
            pass

    # =============================================================
    # LOADING SCREEN
    # =============================================================

    def show_loading(self):

        self.clear_window()

        loading = LoadingScreen(
            self,
            on_complete=self.show_login
        )

        loading.pack(
            fill="both",
            expand=True
        )

        self.current_screen = loading

    # =============================================================
    # LOGIN SCREEN
    # =============================================================

    def show_login(self):

        self.clear_window()

        login = LoginScreen(
            self,
            on_login=self.login_success
        )

        login.pack(
            fill="both",
            expand=True
        )

        self.current_screen = login

    # =============================================================
    # LOGIN SUCCESS
    # =============================================================

    def login_success(self, user):

        self.current_user = user

        self.build_workspace()

    # =============================================================
    # MAIN WORKSPACE
    # =============================================================

    def build_workspace(self):

        self.clear_window()

        self.configure(
            bg="#0B1020"
        )

        # ---------------------------------------------------------
        # Sidebar
        # ---------------------------------------------------------

        sidebar = tk.Frame(
            self,
            bg="#111827",
            width=230
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        # ---------------------------------------------------------
        # Logo
        # ---------------------------------------------------------

        logo_container = tk.Frame(
            sidebar,
            bg="#111827"
        )

        logo_container.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        self.load_logo(
            logo_container
        )

        # ---------------------------------------------------------
        # Username
        # ---------------------------------------------------------

        username = "User"

        try:
            username = self.current_user["username"]
        except Exception:
            pass

        verified = False
        role = "user"

        try:
            verified = bool(
                self.current_user["verified"]
            )
        except Exception:
            pass

        try:
            role = self.current_user["role"]
        except Exception:
            pass

        user_text = f"👤 {username}"

        if verified:
            user_text += "  ✓"

        if role == "admin":
            user_text += "  🛡️"

        tk.Label(
            sidebar,
            text=user_text,
            font=("Segoe UI", 10),
            fg="#94A3B8",
            bg="#111827"
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 20)
        )

        # ---------------------------------------------------------
        # Navigation
        # ---------------------------------------------------------

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
                pady=10
            )

            button.pack(
                fill="x",
                padx=10,
                pady=2
            )

            self.nav_buttons[page] = button

        # ---------------------------------------------------------
        # Admin panel
        # ---------------------------------------------------------

        if role == "admin":

            admin_button = tk.Button(
                sidebar,
                text="🛡️  Admin Panel ✓",
                command=self.open_admin_panel,
                anchor="w",
                bg="#172554",
                fg="#93C5FD",
                activebackground="#1E3A8A",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 10, "bold"),
                padx=20,
                pady=10
            )

            admin_button.pack(
                fill="x",
                padx=10,
                pady=(10, 2)
            )

        # ---------------------------------------------------------
        # Spacer
        # ---------------------------------------------------------

        tk.Frame(
            sidebar,
            bg="#111827"
        ).pack(
            fill="both",
            expand=True
        )

        # ---------------------------------------------------------
        # Logout
        # ---------------------------------------------------------

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
            pady=12
        ).pack(
            fill="x",
            padx=10,
            pady=10
        )

        # ---------------------------------------------------------
        # Right side
        # ---------------------------------------------------------

        right_side = tk.Frame(
            self,
            bg="#0B1020"
        )

        right_side.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ---------------------------------------------------------
        # Top bar
        # ---------------------------------------------------------

        topbar = tk.Frame(
            right_side,
            bg="#111827",
            height=60
        )

        topbar.pack(
            fill="x"
        )

        topbar.pack_propagate(False)

        self.page_title = tk.Label(
            topbar,
            text="Home",
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg="#111827"
        )

        self.page_title.pack(
            side="left",
            padx=20
        )

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
            pady=7
        ).pack(
            side="right",
            padx=15
        )

        # ---------------------------------------------------------
        # Content
        # ---------------------------------------------------------

        self.content = tk.Frame(
            right_side,
            bg="#0B1020"
        )

        self.content.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------------------------------
        # Start Home
        # ---------------------------------------------------------

        self.navigate("home")

    # =============================================================
    # LOAD LOGO
    # =============================================================

    def load_logo(self, parent):

        try:

            logo_path = getattr(
                config,
                "LOGO_PATH",
                Path("assets") / "logo.png"
            )

            logo_path = Path(logo_path)

            if logo_path.exists():

                from PIL import Image, ImageTk

                image = Image.open(
                    logo_path
                )

                image.thumbnail(
                    (190, 110)
                )

                self.logo_image = ImageTk.PhotoImage(
                    image
                )

                tk.Label(
                    parent,
                    image=self.logo_image,
                    bg="#111827"
                ).pack(
                    pady=5
                )

                return

        except Exception:
            pass

        # Fallback if logo cannot be loaded.

        tk.Label(
            parent,
            text="💻",
            font=("Segoe UI Emoji", 30),
            fg="white",
            bg="#111827"
        ).pack()

        tk.Label(
            parent,
            text="SmartDesk",
            font=("Segoe UI", 17, "bold"),
            fg="white",
            bg="#111827"
        ).pack()

    # =============================================================
    # NAVIGATION
    # =============================================================

    def navigate(self, page, **kwargs):

        if self.content is None:
            return

        # Remove old screen.

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
        }

        self.page_title.config(
            text=titles.get(
                page,
                "SmartDesk"
            )
        )

        # ---------------------------------------------------------
        # Home
        # ---------------------------------------------------------

        if page == "home":

            screen = HomeScreen(
                self.content,
                on_open=self.handle_home_open
            )

        # ---------------------------------------------------------
        # Editor
        # ---------------------------------------------------------

        elif page == "editor":

            screen = EditorScreen(
                self.content,
                file_path=kwargs.get(
                    "file_path"
                ),
                on_close=self.close_editor
            )

        # ---------------------------------------------------------
        # File manager
        # ---------------------------------------------------------

        elif page == "files":

            screen = FileManagerScreen(
                self.content,
                on_open=self.handle_project_open
            )

        # ---------------------------------------------------------
        # Study
        # ---------------------------------------------------------

        elif page == "study":

            screen = StudyScreen(
                self.content
            )

        # ---------------------------------------------------------
        # Focus
        # ---------------------------------------------------------

        elif page == "focus":

            screen = FocusScreen(
                self.content
            )

        # ---------------------------------------------------------
        # Tools
        # ---------------------------------------------------------

        elif page == "tools":

            screen = ToolsScreen(
                self.content
            )

        # ---------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------

        elif page == "statistics":

            screen = StatisticsScreen(
                self.content
            )

        # ---------------------------------------------------------
        # Vault
        # ---------------------------------------------------------

        elif page == "vault":

            screen = VaultScreen(
                self.content
            )

        # ---------------------------------------------------------
        # Settings
        # ---------------------------------------------------------

        elif page == "settings":

            screen = SettingsScreen(
                self.content,
                on_theme_change=self.change_theme
            )

        else:

            screen = HomeScreen(
                self.content,
                on_open=self.handle_home_open
            )

        screen.pack(
            fill="both",
            expand=True
        )

        self.current_screen = screen

    # =============================================================
    # ADMIN PANEL
    # =============================================================

    def open_admin_panel(self):

        try:

            from ui.admin import AdminScreen

            for widget in self.content.winfo_children():
                widget.destroy()

            self.page_title.config(
                text="Admin Panel"
            )

            admin_screen = AdminScreen(
                self.content
            )

            admin_screen.pack(
                fill="both",
                expand=True
            )

            self.current_screen = admin_screen

        except ImportError:

            messagebox.showerror(
                "Admin Panel",
                "ui/admin.py could not be found."
            )

        except Exception as error:

            messagebox.showerror(
                "Admin Panel",
                f"Could not open Admin Panel:\n\n{error}"
            )

    # =============================================================
    # HOME OPEN
    # =============================================================

    def handle_home_open(self, item):

        if item == "files":

            self.navigate("files")
            return

        try:

            path = item["path"]

        except (TypeError, KeyError, IndexError):

            path = None

        if not path:

            if isinstance(item, str):
                path = item
            else:
                return

        self.open_path(path)

    # =============================================================
    # PROJECT OPEN
    # =============================================================

    def handle_project_open(self, project):

        try:

            path = project["path"]

        except (TypeError, KeyError, IndexError):

            return

        self.open_path(path)

    # =============================================================
    # OPEN PATH
    # =============================================================

    def open_path(self, path):

        path = Path(path)

        if path.is_dir():

            self.navigate("files")
            return

        if path.is_file():

            self.navigate(
                "editor",
                file_path=str(path)
            )

            return

        messagebox.showwarning(
            "SmartDesk",
            "File or project could not be found:\n\n"
            f"{path}"
        )

    # =============================================================
    # CLOSE EDITOR
    # =============================================================

    def close_editor(self):

        self.navigate("home")

    # =============================================================
    # THEME
    # =============================================================

    def change_theme(self, theme):

        try:

            database.set_setting(
                "theme",
                theme
            )

        except Exception:
            pass

        self.build_workspace()

    # =============================================================
    # LOGOUT
    # =============================================================

    def logout(self):

        result = messagebox.askyesno(
            "Log Out",
            "Are you sure you want to log out?"
        )

        if not result:
            return

        self.current_user = None

        self.show_login()

    # =============================================================
    # CLEAR WINDOW
    # =============================================================

    def clear_window(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.current_screen = None
        self.content = None
        self.nav_buttons = {}

    # =============================================================
    # CLOSE APPLICATION
    # =============================================================

    def on_close(self):

        # Try to save the current editor.

        try:

            if self.current_screen:

                save_method = getattr(
                    self.current_screen,
                    "save_file",
                    None
                )

                if callable(save_method):

                    file_path = getattr(
                        self.current_screen,
                        "file_path",
                        None
                    )

                    if file_path:

                        try:
                            save_method()
                        except Exception:
                            pass

        except Exception:
            pass

        # Try cloud synchronization.

        try:

            from core.cloud_sync import sync_project

            try:
                sync_project()
            except Exception:
                pass

        except Exception:
            pass

        self.destroy()


# ================================================================
# START
# ================================================================

def main():

    app = SmartDesk()

    app.mainloop()


if __name__ == "__main__":
    main()