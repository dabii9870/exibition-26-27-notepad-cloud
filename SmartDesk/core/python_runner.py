"""
SmartDesk Python Runner
Runs Python files safely in a separate process.
"""

import subprocess
import sys
from pathlib import Path


DEFAULT_TIMEOUT = 30


def validate_python_source(source, filename="<input>"):
    """Compile Python source and return a structured syntax error result."""
    try:
        compile(source, filename, "exec")
        return {"success": True, "error": None}
    except SyntaxError as error:
        return {
            "success": False,
            "error": f"Syntax error on line {error.lineno}: {error.msg}",
            "line": error.lineno,
        }
    except Exception as error:
        return {"success": False, "error": str(error), "line": None}


def run_python_file(file_path, timeout=DEFAULT_TIMEOUT):
    """
    Run a Python file and return its output.

    Returns:
        dict:
            success
            output
            error
            return_code
    """

    file_path = Path(file_path)

    if not file_path.exists():
        return {
            "success": False,
            "output": "",
            "error": "File does not exist.",
            "return_code": -1
        }

    if file_path.suffix.lower() != ".py":
        return {
            "success": False,
            "output": "",
            "error": "Only Python files can be executed.",
            "return_code": -1
        }

    try:
        process = subprocess.run(
            [
                sys.executable,
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(file_path.parent)
        )

        return {
            "success": process.returncode == 0,
            "output": process.stdout,
            "error": process.stderr,
            "return_code": process.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Program stopped after {timeout} seconds.",
            "return_code": -1
        }

    except Exception as error:
        return {
            "success": False,
            "output": "",
            "error": str(error),
            "return_code": -1
        }


def run_python_code(code, timeout=DEFAULT_TIMEOUT):
    """
    Run Python code directly without creating a file.
    """

    validation = validate_python_source(code)
    if not validation["success"]:
        return {
            "success": False,
            "output": "",
            "error": validation["error"],
            "return_code": 1,
        }

    try:
        process = subprocess.run(
            [
                sys.executable,
                "-c",
                code
            ],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "success": process.returncode == 0,
            "output": process.stdout,
            "error": process.stderr,
            "return_code": process.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Program stopped after {timeout} seconds.",
            "return_code": -1
        }

    except Exception as error:
        return {
            "success": False,
            "output": "",
            "error": str(error),
            "return_code": -1
        }


def validate_python_file(file_path):
    """
    Check whether a Python file can be compiled.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        return False, "File does not exist."

    try:
        source = file_path.read_text(
            encoding="utf-8"
        )

        compile(
            source,
            str(file_path),
            "exec"
        )

        return True, "No syntax errors found."

    except SyntaxError as error:
        return False, (
            f"Syntax error on line "
            f"{error.lineno}: {error.msg}"
        )

    except Exception as error:
        return False, str(error)