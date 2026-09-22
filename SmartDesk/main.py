
import tkinter as tk

from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT
from database import initialize_database


class SmartDeskApp(tk.Tk):
    """Main SmartDesk application window."""

    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 600)

        # Initialize persistent storage
        initialize_database()

        self.configure(bg="#0B1020")

        self.create_startup_screen()

    def create_startup_screen(self):
        """Temporary startup screen until the UI modules are added."""

        container = tk.Frame(
            self,
            bg="#0B1020"
        )
        container.pack(
            expand=True,
            fill="both"
        )

        title = tk.Label(
            container,
            text="SmartDesk",
            font=("Segoe UI", 36, "bold"),
            fg="#FFFFFF",
            bg="#0B1020"
        )
        title.pack(pady=(180, 5))

        subtitle = tk.Label(
            container,
            text="Learn • Create • Achieve",
            font=("Segoe UI", 13),
            fg="#38BDF8",
            bg="#0B1020"
        )
        subtitle.pack()

        version = tk.Label(
            container,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 10),
            fg="#64748B",
            bg="#0B1020"
        )
        version.pack(pady=15)

        start_button = tk.Button(
            container,
            text="Open SmartDesk",
            font=("Segoe UI", 12, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.open_application
        )
        start_button.pack(pady=20)

    def open_application(self):
        """
        Start the main interface.

        The Home screen will be connected here once
        screens/home.py is created.
        """

        for widget in self.winfo_children():
            widget.destroy()

        container = tk.Frame(
            self,
            bg="#0B1020"
        )
        container.pack(
            expand=True,
            fill="both"
        )

        title = tk.Label(
            container,
            text="SmartDesk",
            font=("Segoe UI", 30, "bold"),
            fg="white",
            bg="#0B1020"
        )
        title.pack(pady=(150, 10))

        message = tk.Label(
            container,
            text="Your workspace is ready.",
            font=("Segoe UI", 14),
            fg="#94A3B8",
            bg="#0B1020"
        )
        message.pack()

        info = tk.Label(
            container,
            text="Home screen modules will be connected here.",
            font=("Segoe UI", 10),
            fg="#64748B",
            bg="#0B1020"
        )
        info.pack(pady=10)


def main():
    """Application entry point."""

    app = SmartDeskApp()
    app.mainloop()


if __name__ == "__main__":
    main()