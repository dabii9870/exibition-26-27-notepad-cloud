from pathlib import Path
import hashlib
import json
import os
import shutil
import time

import config


def _candidate_cloud_dirs():
    candidates = []

    env = os.environ.get("SMARTDESK_CLOUD_DIR")
    if env:
        candidates.append(Path(env).expanduser())

    for env_name in ("OneDrive", "OneDriveCommercial", "Dropbox", "GOOGLE_DRIVE"):
        value = os.environ.get(env_name)
        if value:
            candidates.append(Path(value).expanduser())

    home = Path.home()
    candidates += [
        home / "OneDrive",
        home / "Dropbox",
        home / "Google Drive",
        home / "GoogleDrive",
    ]

    return candidates


def get_cloud_directory():
    """Use a real locally-synced cloud folder when available.

    If none is installed, fall back to data/cloud so SmartDesk still works.
    """
    for candidate in _candidate_cloud_dirs():
        if candidate.exists() and candidate.is_dir():
            folder = candidate / "SmartDesk"
            folder.mkdir(parents=True, exist_ok=True)
            return folder

    fallback = Path(config.DATA_DIR) / "cloud"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def get_file_hash(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_to_cloud(file_path, relative_path=None):
    source = Path(file_path)
    if not source.exists() or not source.is_file():
        return False

    cloud = get_cloud_directory()
    if relative_path is None:
        relative_path = source.name

    destination = cloud / Path(relative_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def sync_project(project_path):
    project = Path(project_path)
    if not project.exists():
        return 0

    cloud = get_cloud_directory()
    count = 0

    if project.is_file():
        relative = project.name
        return 1 if save_to_cloud(project, relative) else 0

    # Keep project folder structure intact.
    for file in project.rglob("*"):
        if not file.is_file():
            continue
        try:
            relative = file.relative_to(project.parent)
        except ValueError:
            relative = Path(project.name) / file.name
        if save_to_cloud(file, relative):
            count += 1

    manifest = {
        "project": str(project),
        "synced_at": time.time(),
        "files": count,
    }
    manifest_path = cloud / project.name / ".smartdesk_sync.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return count


def sync_all_projects():
    projects_dir = Path(config.PROJECTS_DIR)
    if not projects_dir.exists():
        return 0

    total = 0
    for item in projects_dir.iterdir():
        total += sync_project(item)
    return total


def get_sync_status():
    cloud = get_cloud_directory()
    is_fallback = cloud == Path(config.DATA_DIR) / "cloud"
    return {
        "directory": str(cloud),
        "real_cloud_provider_detected": not is_fallback,
        "message": (
            "A locally-synced cloud folder is active."
            if not is_fallback
            else "No OneDrive/Dropbox/Google Drive folder detected; using SmartDesk local cloud cache."
        ),
    }
