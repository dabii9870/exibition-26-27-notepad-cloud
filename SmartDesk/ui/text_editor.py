import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import database


class TextEditorScreen(tk.Frame):
    BG = "#0B1020"
    PANEL = "#111827"
    TEXT = "#E5E7EB"
    MUTED = "#94A3B8"

    def __init__(self, parent, file_path=None, project_id=None, on_close=None, **kwargs):
        super().__init__(parent, bg=self.BG, **kwargs)
        self.file_path = str(file_path) if file_path else None
        self.project_id = project_id
        self.project_name = "Untitled"
        self.on_close = on_close
        self.modified = False

        self._build_ui()
        self.editor.bind("<<Modified>>", self._on_modified)
        self.editor.bind("<Control-o>", self._open_shortcut)
        self.editor.bind("<Control-s>", self._save_shortcut)

        if self.project_id is not None:
            self._load_project()
        elif self.file_path:
            self.load_file(self.file_path)
        self.editor.edit_modified(False)
        self.editor.focus_set()

    def _build_ui(self):
        header = tk.Frame(self, bg=self.BG, height=74)
        header.pack(fill="x", padx=12, pady=(8, 0))
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Text Editor",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=self.BG,
        ).pack(side="left", padx=(8, 18))

        buttons = tk.Frame(header, bg=self.BG)
        buttons.pack(side="left")
        for label, command in (
            ("New", self.new_file),
            ("Open TXT", self.open_file),
            ("Save", self.save),
            ("Save As", self.save_as),
        ):
            tk.Button(
                buttons,
                text=label,
                command=command,
                bg="#1E293B",
                fg="white",
                activebackground="#334155",
                relief="flat",
                padx=12,
                pady=7,
            ).pack(side="left", padx=3)

        tk.Button(
            header,
            text="Close",
            command=self.close_editor,
            bg="#334155",
            fg="white",
            activebackground="#475569",
            relief="flat",
            padx=12,
            pady=7,
        ).pack(side="right", padx=4)

        self.file_label = tk.Label(
            header,
            text="Untitled.txt",
            font=("Segoe UI", 10),
            fg=self.MUTED,
            bg=self.BG,
        )
        self.file_label.pack(side="right", padx=12)

        editor_area = tk.Frame(self, bg=self.BG)
        editor_area.pack(fill="both", expand=True, padx=12, pady=10)

        scrollbar = tk.Scrollbar(editor_area)
        scrollbar.pack(side="right", fill="y")

        self.editor = tk.Text(
            editor_area,
            bg=self.PANEL,
            fg=self.TEXT,
            insertbackground="white",
            selectbackground="#264F78",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 11),
            padx=12,
            pady=10,
            undo=True,
            wrap="word",
            yscrollcommand=scrollbar.set,
        )
        self.editor.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.editor.yview)

    def _on_modified(self, event=None):
        if self.editor.edit_modified():
            self.modified = True
            self.update_title()
            self.editor.edit_modified(False)

    def _open_shortcut(self, event=None):
        self.open_file()
        return "break"

    def _save_shortcut(self, event=None):
        self.save()
        return "break"

    def _confirm_discard_or_save(self):
        if not self.modified:
            return True
        answer = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Save your changes before continuing?",
        )
        if answer is None:
            return False
        if answer:
            return self.save()
        return True

    def new_file(self):
        if not self._confirm_discard_or_save():
            return
        self.editor.delete("1.0", "end")
        self.file_path = None
        self.project_id = None
        self.project_name = "Untitled"
        self.modified = False
        self.editor.edit_modified(False)
        self.update_title()

    def open_file(self):
        if not self._confirm_discard_or_save():
            return
        path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=(("Text files", "*.txt"),),
        )
        if path:
            self.load_file(path)

    def load_file(self, path):
        file_path = Path(path)
        if file_path.suffix.lower() != ".txt":
            messagebox.showerror("Open Error", "Only .txt files can be opened here.")
            return False
        try:
            content = file_path.read_text(encoding="utf-8")
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self.file_path = str(file_path)
            self.project_name = file_path.stem
            self.project_id = None
            project = database.get_project_by_path(self.file_path)
            if project:
                self.project_id = project["id"]
            database.add_recent_file(self.file_path)
            self.modified = False
            self.editor.edit_modified(False)
            self.update_title()
            return True
        except Exception as error:
            messagebox.showerror("Open Error", str(error))
            return False

    def _load_project(self):
        try:
            project = database.get_project(self.project_id)
            if not project:
                return
            if project["language"] not in ("text", "txt", ""):
                messagebox.showerror(
                    "Open Error",
                    "This editor only opens text projects and .txt files.",
                )
                return
            self.file_path = project["path"]
            self.project_name = project["name"] or "Untitled"
            self.editor.insert("1.0", project["content"] or "")
            self.modified = False
            self.update_title()
        except Exception as error:
            messagebox.showerror("Load Error", str(error))

    def save(self):
        if not self.file_path:
            return self.save_as()
        is_internal_project = self.file_path.startswith("smartdesk://")
        if not is_internal_project and Path(self.file_path).suffix.lower() != ".txt":
            messagebox.showerror("Save Error", "Only .txt files can be saved here.")
            return False
        content = self.editor.get("1.0", "end-1c")
        try:
            if not is_internal_project:
                Path(self.file_path).write_text(content, encoding="utf-8")
            self.project_id = database.save_project(
                name=self.project_name if is_internal_project else Path(self.file_path).stem,
                path=self.file_path,
                content=content,
                language="text",
            )
            if not is_internal_project:
                self.project_name = Path(self.file_path).stem
            self.modified = False
            self.editor.edit_modified(False)
            self.update_title()
            return True
        except Exception as error:
            messagebox.showerror("Save Error", str(error))
            return False

    def save_as(self):
        default_name = self.project_name or "Untitled"
        if not default_name.lower().endswith(".txt"):
            default_name += ".txt"
        path = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=(("Text files", "*.txt"),),
        )
        if not path:
            return False
        if Path(path).suffix.lower() != ".txt":
            messagebox.showerror("Save Error", "The file name must end in .txt.")
            return False
        self.file_path = path
        return self.save()

    def update_title(self):
        name = Path(self.file_path).name if self.file_path and not self.file_path.startswith("smartdesk://") else f"{self.project_name}.txt"
        if self.modified:
            name += " *"
        self.file_label.config(text=name)

    def close_editor(self):
        if not self._confirm_discard_or_save():
            return
        if self.on_close:
            self.on_close()