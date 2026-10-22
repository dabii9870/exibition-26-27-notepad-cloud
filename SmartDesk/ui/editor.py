import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import keyword
import re

import database
from core.python_runner import run_python_code, validate_python_source


class EditorScreen(tk.Frame):

    def __init__(
        self,
        parent,
        file_path=None,
        project_id=None,
        on_close=None,
        **kwargs
    ):
        super().__init__(
            parent,
            bg="#0B1020",
            **kwargs
        )

        self.parent = parent
        self.file_path = file_path
        self.project_id = project_id
        self.on_close = on_close

        self.project_name = "Untitled"
        self.autosave_job = None
        self.modified = False

        self.setup_tags()
        self.build_ui()

        self.bind_events()

        if self.project_id is not None:
            self.load_project()

        elif self.file_path:
            self.load_file(self.file_path)

        else:
            self.editor.insert(
                "1.0",
                ""
            )

        self.update_line_numbers()
        self.highlight_syntax()

        self.editor.focus_set()

        self.start_autosave()

    # ========================================================
    # COLORS
    # ========================================================

    BG = "#0B1020"
    PANEL = "#111827"
    PANEL2 = "#172033"
    TEXT = "#E5E7EB"
    MUTED = "#94A3B8"
    BLUE = "#2563EB"
    GREEN = "#16A34A"
    RED = "#DC2626"
    BORDER = "#1E293B"

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # TOP HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self,
            bg=self.BG,
            height=105
        )

        header.pack(
            fill="x",
            padx=12,
            pady=(8, 0)
        )

        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Editor",
            font=("Segoe UI", 20, "bold"),
            fg="#FFFFFF",
            bg=self.BG
        )

        title.pack(
            side="left",
            padx=(8, 20),
            pady=18
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        button_frame = tk.Frame(
            header,
            bg=self.BG
        )

        button_frame.pack(
            side="left",
            pady=18
        )

        self.make_button(
            button_frame,
            "📄 New",
            self.new_file
        ).pack(
            side="left",
            padx=4
        )

        self.make_button(
            button_frame,
            "📂 Open",
            self.open_file
        ).pack(
            side="left",
            padx=4
        )

        self.make_button(
            button_frame,
            "💾 Save",
            self.save
        ).pack(
            side="left",
            padx=4
        )

        self.make_button(
            button_frame,
            "📤 Export",
            self.export_file
        ).pack(
            side="left",
            padx=4
        )

        run_button = self.make_button(
            button_frame,
            "▶ Run",
            self.run_code,
            self.GREEN
        )

        run_button.pack(
            side="left",
            padx=4
        )

        # ----------------------------------------------------
        # RIGHT SIDE
        # ----------------------------------------------------

        self.file_label = tk.Label(
            header,
            text="📄 Untitled",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT,
            bg=self.BG
        )

        self.file_label.pack(
            side="right",
            padx=12
        )

        close_button = self.make_button(
            header,
            "✕ Close",
            self.close_editor
        )

        close_button.pack(
            side="right",
            padx=4
        )

        # ----------------------------------------------------
        # EDITOR AREA
        # ----------------------------------------------------

        editor_container = tk.Frame(
            self,
            bg=self.BG
        )

        editor_container.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 6)
        )

        # Line numbers
        self.line_numbers = tk.Text(
            editor_container,
            width=5,
            bg="#0D1526",
            fg="#64748B",
            insertbackground="#64748B",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 11),
            padx=8,
            pady=8,
            state="disabled",
            takefocus=0
        )

        self.line_numbers.pack(
            side="left",
            fill="y"
        )

        # Scrollbar
        scrollbar = tk.Scrollbar(
            editor_container
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Main editor
        self.editor = tk.Text(
            editor_container,
            bg="#0B1020",
            fg="#E5E7EB",
            insertbackground="#FFFFFF",
            selectbackground="#264F78",
            selectforeground="#FFFFFF",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 11),
            padx=10,
            pady=8,
            undo=True,
            wrap="none"
        )

        self.editor.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.editor.config(
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(
            command=self.on_scroll
        )

        # ----------------------------------------------------
        # OUTPUT PANEL
        # ----------------------------------------------------

        output_frame = tk.Frame(
            self,
            bg=self.BG,
            height=145
        )

        output_frame.pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

        output_frame.pack_propagate(False)

        output_title = tk.Label(
            output_frame,
            text="Terminal / Output",
            font=("Segoe UI", 10, "bold"),
            fg="#CBD5E1",
            bg=self.BG,
            anchor="w"
        )

        output_title.pack(
            fill="x",
            padx=4,
            pady=(0, 5)
        )

        self.output = tk.Text(
            output_frame,
            bg="#020617",
            fg="#E2E8F0",
            insertbackground="#FFFFFF",
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            wrap="word",
            height=7
        )

        self.output.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # BUTTON
    # ========================================================

    def make_button(
        self,
        parent,
        text,
        command,
        color=None
    ):

        if color is None:
            color = "#1E293B"

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#FFFFFF",
            activebackground="#334155",
            activeforeground="#FFFFFF",
            relief="flat",
            borderwidth=0,
            padx=14,
            pady=7,
            cursor="hand2",
            font=("Segoe UI", 9)
        )

    # ========================================================
    # TAGS
    # ========================================================

    def setup_tags(self):

        self.tag_config = {
            "keyword": {
                "foreground": "#C084FC"
            },
            "string": {
                "foreground": "#86EFAC"
            },
            "comment": {
                "foreground": "#64748B"
            },
            "number": {
                "foreground": "#FBBF24"
            },
            "builtin": {
                "foreground": "#67E8F9"
            },
            "function": {
                "foreground": "#60A5FA"
            }
        }

    # ========================================================
    # EVENTS
    # ========================================================

    def bind_events(self):

        self.editor.bind(
            "<KeyRelease>",
            self.on_key_release
        )

        self.editor.bind(
            "<Return>",
            self.handle_enter
        )

        self.editor.bind(
            "<Tab>",
            self.handle_tab
        )

        self.editor.bind(
            "<Shift-Tab>",
            self.handle_shift_tab
        )

        self.editor.bind(
            "<Control-s>",
            self.handle_ctrl_s
        )

        self.editor.bind(
            "<Control-Shift-S>",
            self.handle_ctrl_shift_s
        )

        self.editor.bind(
            "<Control-r>",
            self.handle_ctrl_r
        )

        self.editor.bind(
            "<Key>",
            self.handle_auto_pairs
        )

        self.editor.bind(
            "<MouseWheel>",
            self.update_line_numbers
        )

    # ========================================================
    # KEY HANDLING
    # ========================================================

    def on_key_release(self, event=None):

        self.modified = True

        self.update_line_numbers()
        self.highlight_syntax()

    # ========================================================
    # AUTO BRACKETS / QUOTES
    # ========================================================

    def handle_auto_pairs(self, event):

        pairs = {
            "(": ")",
            "[": "]",
            "{": "}",
            '"': '"',
            "'": "'"
        }

        if event.char not in pairs:
            return

        try:

            selection = self.editor.get(
                "sel.first",
                "sel.last"
            )

            self.editor.delete(
                "sel.first",
                "sel.last"
            )

            self.editor.insert(
                "insert",
                event.char
                + selection
                + pairs[event.char]
            )

            self.editor.mark_set(
                "insert",
                "insert - 1 chars"
            )

            return "break"

        except tk.TclError:

            # No selection
            if event.char in pairs:

                closing = pairs[event.char]

                self.editor.insert(
                    "insert",
                    event.char + closing
                )

                self.editor.mark_set(
                    "insert",
                    "insert - 1 chars"
                )

                return "break"

    # ========================================================
    # ENTER
    # ========================================================

    def handle_enter(self, event):

        current_line = self.editor.get(
            "insert linestart",
            "insert"
        )

        indentation = re.match(
            r"\s*",
            current_line
        )

        spaces = (
            indentation.group()
            if indentation
            else ""
        )

        stripped = current_line.strip()

        if stripped.endswith(":"):
            spaces += "    "

        self.editor.insert(
            "insert",
            "\n" + spaces
        )

        self.modified = True

        return "break"

    # ========================================================
    # TAB
    # ========================================================

    def handle_tab(self, event):

        try:

            start = self.editor.index(
                "sel.first"
            )

            end = self.editor.index(
                "sel.last"
            )

            start_line = int(
                start.split(".")[0]
            )

            end_line = int(
                end.split(".")[0]
            )

            for line in range(
                start_line,
                end_line + 1
            ):

                self.editor.insert(
                    f"{line}.0",
                    "    "
                )

        except tk.TclError:

            self.editor.insert(
                "insert",
                "    "
            )

        self.modified = True

        return "break"

    # ========================================================
    # SHIFT TAB
    # ========================================================

    def handle_shift_tab(self, event):

        try:

            start = self.editor.index(
                "sel.first"
            )

            end = self.editor.index(
                "sel.last"
            )

            start_line = int(
                start.split(".")[0]
            )

            end_line = int(
                end.split(".")[0]
            )

            for line in range(
                start_line,
                end_line + 1
            ):

                text = self.editor.get(
                    f"{line}.0",
                    f"{line}.4"
                )

                if text.startswith("    "):

                    self.editor.delete(
                        f"{line}.0",
                        f"{line}.4"
                    )

                elif text.startswith("\t"):

                    self.editor.delete(
                        f"{line}.0",
                        f"{line}.1"
                    )

        except tk.TclError:

            line = self.editor.index(
                "insert linestart"
            )

            text = self.editor.get(
                line,
                f"{line} + 4 chars"
            )

            if text.startswith("    "):

                self.editor.delete(
                    line,
                    f"{line} + 4 chars"
                )

        self.modified = True

        return "break"

    # ========================================================
    # CTRL S
    # ========================================================

    def handle_ctrl_s(self, event=None):

        self.save()

        return "break"

    # ========================================================
    # CTRL SHIFT S
    # ========================================================

    def handle_ctrl_shift_s(self, event=None):

        self.export_file()

        return "break"

    # ========================================================
    # CTRL R
    # ========================================================

    def handle_ctrl_r(self, event=None):

        self.run_code()

        return "break"

    # ========================================================
    # LINE NUMBERS
    # ========================================================

    def update_line_numbers(self, event=None):

        if not hasattr(
            self,
            "line_numbers"
        ):
            return

        try:

            self.line_numbers.config(
                state="normal"
            )

            self.line_numbers.delete(
                "1.0",
                "end"
            )

            line_count = int(
                self.editor.index(
                    "end-1c"
                ).split(".")[0]
            )

            numbers = "\n".join(
                str(i)
                for i in range(
                    1,
                    line_count + 1
                )
            )

            self.line_numbers.insert(
                "1.0",
                numbers
            )

            self.line_numbers.config(
                state="disabled"
            )

        except Exception:
            pass

    # ========================================================
    # SCROLL
    # ========================================================

    def on_scroll(self, *args):

        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    # ========================================================
    # SYNTAX HIGHLIGHTING
    # ========================================================

    def highlight_syntax(self):

        if not hasattr(
            self,
            "editor"
        ):
            return

        try:

            text = self.editor.get(
                "1.0",
                "end-1c"
            )

            for tag in self.tag_config:

                self.editor.tag_remove(
                    tag,
                    "1.0",
                    "end"
                )

                self.editor.tag_config(
                    tag,
                    **self.tag_config[tag]
                )

            # ------------------------------------------------
            # Keywords
            # ------------------------------------------------

            for word in keyword.kwlist:

                pattern = (
                    r"\b"
                    + re.escape(word)
                    + r"\b"
                )

                self.highlight_pattern(
                    pattern,
                    "keyword"
                )

            # ------------------------------------------------
            # Strings
            # ------------------------------------------------

            string_pattern = (
                r"(['\"])(?:\\.|(?!\1).)*\1"
            )

            self.highlight_pattern(
                string_pattern,
                "string"
            )

            # ------------------------------------------------
            # Comments
            # ------------------------------------------------

            self.highlight_pattern(
                r"#.*",
                "comment"
            )

            # ------------------------------------------------
            # Numbers
            # ------------------------------------------------

            self.highlight_pattern(
                r"\b\d+(?:\.\d+)?\b",
                "number"
            )

            # ------------------------------------------------
            # Common built-ins
            # ------------------------------------------------

            builtins = [
                "print",
                "len",
                "range",
                "str",
                "int",
                "float",
                "list",
                "dict",
                "set",
                "tuple",
                "open",
                "input",
                "sum",
                "min",
                "max",
                "type",
                "super",
                "self"
            ]

            for word in builtins:

                self.highlight_pattern(
                    r"\b"
                    + word
                    + r"\b",
                    "builtin"
                )

            # ------------------------------------------------
            # Function names
            # ------------------------------------------------

            self.highlight_pattern(
                r"\b[a-zA-Z_]\w*(?=\s*\()",
                "function"
            )

        except Exception:
            pass

    def highlight_pattern(
        self,
        pattern,
        tag
    ):

        try:

            start = "1.0"

            while True:

                index = self.editor.search(
                    pattern,
                    start,
                    stopindex="end",
                    regexp=True
                )

                if not index:
                    break

                end = (
                    index
                    + "+"
                    + str(
                        len(
                            self.editor.get(
                                index,
                                index + " wordend"
                            )
                        )
                    )
                    + "c"
                )

                match = re.search(
                    pattern,
                    self.editor.get(
                        index,
                        index + " lineend"
                    )
                )

                if match:

                    length = len(
                        match.group()
                    )

                    end = (
                        index
                        + "+"
                        + str(length)
                        + "c"
                    )

                self.editor.tag_add(
                    tag,
                    index,
                    end
                )

                start = end

        except Exception:
            pass

    # ========================================================
    # NEW
    # ========================================================

    def new_file(self):

        if self.modified:

            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save your current project before creating a new one?"
            )

            if answer is None:
                return

            if answer:
                self.save()

        self.editor.delete(
            "1.0",
            "end"
        )

        self.output.delete(
            "1.0",
            "end"
        )

        self.file_path = None
        self.project_id = None
        self.project_name = "Untitled"
        self.modified = False

        self.update_title()
        self.update_line_numbers()

        self.editor.focus_set()

    # ========================================================
    # OPEN
    # ========================================================

    def open_file(self):

        path = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[
                (
                    "Python files",
                    "*.py"
                ),
                (
                    "Text files",
                    "*.txt"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        self.load_file(path)

    def load_file(self, path):

        try:

            path = str(path)

            file = Path(path)

            if not file.exists():

                messagebox.showerror(
                    "Open Error",
                    "The selected file does not exist."
                )

                return

            content = file.read_text(
                encoding="utf-8"
            )

            self.editor.delete(
                "1.0",
                "end"
            )

            self.editor.insert(
                "1.0",
                content
            )

            self.file_path = path
            self.project_name = file.stem
            self.modified = False

            # Store recent file.
            try:

                database.add_recent_file(
                    path
                )

            except Exception:
                pass

            # Find existing SmartDesk project.
            try:

                project = database.get_project_by_path(
                    path
                )

                if project:

                    self.project_id = project["id"]

            except Exception:
                pass

            self.update_title()
            self.update_line_numbers()
            self.highlight_syntax()

        except Exception as error:

            messagebox.showerror(
                "Open Error",
                str(error)
            )

    # ========================================================
    # LOAD PROJECT FROM DATABASE
    # ========================================================

    def load_project(self):

        try:

            project = database.get_project(
                self.project_id
            )

            if not project:

                return

            self.project_name = (
                project["name"]
                or "Untitled"
            )

            self.file_path = project["path"]

            content = (
                project["content"]
                or ""
            )

            self.editor.delete(
                "1.0",
                "end"
            )

            self.editor.insert(
                "1.0",
                content
            )

            self.modified = False

            self.update_title()
            self.update_line_numbers()
            self.highlight_syntax()

        except Exception as error:

            self.show_error(
                "Load Error",
                error
            )

    # ========================================================
    # SAVE
    # ========================================================

    def save(self):

        content = self.editor.get(
            "1.0",
            "end-1c"
        )

        # ----------------------------------------------------
        # Determine project name
        # ----------------------------------------------------

        if self.file_path:

            project_name = Path(
                self.file_path
            ).stem

        else:

            project_name = self.project_name

            if (
                not project_name
                or project_name == "Untitled"
            ):

                project_name = "Untitled"

        try:

            # ------------------------------------------------
            # Existing project
            # ------------------------------------------------

            if self.project_id is not None:

                database.save_project(
                    name=project_name,
                    path=self.file_path,
                    content=content,
                    language="python"
                )

            # ------------------------------------------------
            # Existing path
            # ------------------------------------------------

            elif self.file_path:

                project = (
                    database.get_project_by_path(
                        self.file_path
                    )
                )

                if project:

                    self.project_id = project["id"]

                else:

                    self.project_id = (
                        database.save_project(
                            name=project_name,
                            path=self.file_path,
                            content=content,
                            language="python"
                        )
                    )

            # ------------------------------------------------
            # New internal SmartDesk project
            # ------------------------------------------------

            else:

                self.project_id = (
                    database.save_project(
                        name=project_name,
                        path=None,
                        content=content,
                        language="python"
                    )
                )

            self.project_name = project_name
            self.modified = False

            try:
                database.increment_stat(
                    "files_saved",
                    1
                )
            except Exception:
                pass

            try:
                database.log_activity(
                    "Saved project",
                    project_name
                )
            except Exception:
                pass

            self.update_title()

            self.show_output(
                "✓ Saved successfully.\n"
                "Project stored inside SmartDesk."
            )

        except Exception as error:

            self.show_output(
                "SAVE ERROR:\n"
                + str(error)
            )

            messagebox.showerror(
                "Save Error",
                str(error)
            )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_file(self):

        content = self.editor.get(
            "1.0",
            "end-1c"
        )

        default_name = (
            self.project_name
            if self.project_name
            else "untitled"
        )

        if not default_name.endswith(
            ".py"
        ):

            default_name += ".py"

        path = filedialog.asksaveasfilename(
            title="Export Python File",
            defaultextension=".py",
            initialfile=default_name,
            filetypes=[
                (
                    "Python files",
                    "*.py"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        try:

            Path(path).write_text(
                content,
                encoding="utf-8"
            )

            self.show_output(
                "✓ Exported successfully:\n"
                + path
            )

            try:

                database.log_activity(
                    "Exported project",
                    path
                )

            except Exception:
                pass

        except Exception as error:

            messagebox.showerror(
                "Export Error",
                str(error)
            )

    # ========================================================
    # RUN
    # ========================================================

    def run_code(self):

        code = self.editor.get(
            "1.0",
            "end-1c"
        )

        if not code.strip():

            self.show_output(
                "Nothing to run."
            )

            return

        validation = validate_python_source(code)
        if not validation["success"]:
            self.show_output(
                "✗ Python syntax error\n\n"
                + validation["error"]
            )
            return

        self.show_output(
            "Running Python...\n"
        )

        try:

            result = run_python_code(
                code
            )

            if isinstance(
                result,
                dict
            ):

                success = result.get(
                    "success",
                    False
                )

                output = result.get(
                    "output",
                    ""
                )

                error = result.get(
                    "error",
                    ""
                )

                return_code = result.get(
                    "return_code",
                    0
                )

                if success:

                    text = (
                        "✓ Program finished successfully\n\n"
                        + output
                    )

                    if not output:
                        text += "(no output)"

                else:

                    text = (
                        "✗ Program failed\n\n"
                        + (
                            error
                            or output
                            or "Unknown error"
                        )
                    )

                text += (
                    "\n\nReturn code: "
                    + str(return_code)
                )

            else:

                text = str(result)

            self.show_output(
                text
            )

            try:

                database.increment_stat(
                    "python_runs",
                    1
                )

            except Exception:
                pass

            try:

                database.log_activity(
                    "Ran Python code",
                    self.project_name
                )

            except Exception:
                pass

        except Exception as error:

            self.show_output(
                "RUN ERROR:\n"
                + str(error)
            )

    # ========================================================
    # OUTPUT
    # ========================================================

    def show_output(self, text):

        self.output.delete(
            "1.0",
            "end"
        )

        self.output.insert(
            "1.0",
            str(text)
        )

        self.output.see(
            "end"
        )

    # ========================================================
    # AUTOSAVE
    # ========================================================

    def start_autosave(self):

        self.stop_autosave()

        try:

            enabled = database.get_setting(
                "autosave",
                "1"
            )

            enabled = str(
                enabled
            ).lower() in (
                "1",
                "true",
                "yes",
                "on"
            )

        except Exception:

            enabled = True

        if enabled:

            self.autosave_job = self.after(
                5000,
                self.autosave
            )

    def autosave(self):

        try:

            if self.modified:

                self.save()

        except Exception:
            pass

        self.start_autosave()

    def stop_autosave(self):

        if self.autosave_job:

            try:

                self.after_cancel(
                    self.autosave_job
                )

            except Exception:
                pass

            self.autosave_job = None

    # ========================================================
    # TITLE
    # ========================================================

    def update_title(self):

        name = (
            self.project_name
            or "Untitled"
        )

        if self.modified:
            name += " *"

        self.file_label.config(
            text="📄 " + name
        )

    # ========================================================
    # ERROR
    # ========================================================

    def show_error(
        self,
        title,
        error
    ):

        messagebox.showerror(
            title,
            str(error)
        )

        self.show_output(
            "ERROR:\n"
            + str(error)
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close_editor(self):

        try:

            if self.modified:

                answer = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    "Save your changes before closing?"
                )

                if answer is None:
                    return

                if answer:
                    self.save()

            self.stop_autosave()

        except Exception:
            pass

        if self.on_close:

            try:
                self.on_close()
            except Exception:
                pass