"""
SmartDesk Cloud Synchronization

Provides the cloud-sync interface for SmartDesk.

The local project remains usable when offline.
A cloud provider can later be connected to these methods.
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, PROJECTS_DIR


SYNC_FOLDER = DATA_DIR / "cloud"


def initialize_cloud_storage():
    """Create the local cloud-sync storage."""

    SYNC_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )


def get_file_hash(file_path):
    """Return a SHA-256 hash for a file."""

    file_path = Path(file_path)

    if not file_path.exists():
        return None

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def create_sync_manifest():
    """
    Create a manifest describing local project files.
    """

    initialize_cloud_storage()

    manifest = {
        "created_at": datetime.now().isoformat(),
        "files": []
    }

    if PROJECTS_DIR.exists():

        for file_path in PROJECTS_DIR.rglob("*"):

            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(
                PROJECTS_DIR
            )

            manifest["files"].append({
                "path": str(relative_path),
                "size": file_path.stat().st_size,
                "hash": get_file_hash(file_path),
                "modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat()
            })

    manifest_path = SYNC_FOLDER / "manifest.json"

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=4
        ),
        encoding="utf-8"
    )

    return manifest


def save_to_cloud(file_path):
    """
    Save a local project file to SmartDesk's
    sync storage.

    This acts as the local cloud adapter until
    a real provider is connected.
    """

    initialize_cloud_storage()

    file_path = Path(file_path)

    if not file_path.exists():
        return False

    try:
        relative_path = file_path.relative_to(
            PROJECTS_DIR
        )

        destination = (
            SYNC_FOLDER /
            "projects" /
            relative_path
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            file_path,
            destination
        )

        create_sync_manifest()

        return True

    except ValueError:
        return False

    except Exception:
        return False


def download_from_cloud(relative_path):
    """
    Restore a project file from sync storage.
    """

    initialize_cloud_storage()

    relative_path = Path(relative_path)

    source = (
        SYNC_FOLDER /
        "projects" /
        relative_path
    )

    destination = (
        PROJECTS_DIR /
        relative_path
    )

    if not source.exists():
        return False

    try:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            source,
            destination
        )

        return True

    except Exception:
        return False


def sync_project():
    """
    Synchronize all project files.

    Returns a summary of the operation.
    """

    initialize_cloud_storage()

    uploaded = 0
    failed = 0

    if PROJECTS_DIR.exists():

        for file_path in PROJECTS_DIR.rglob("*"):

            if not file_path.is_file():
                continue

            if save_to_cloud(file_path):
                uploaded += 1
            else:
                failed += 1

    manifest = create_sync_manifest()

    return {
        "success": failed == 0,
        "uploaded": uploaded,
        "failed": failed,
        "files": len(manifest["files"]),
        "synced_at": datetime.now().isoformat()
    }


def get_sync_status():
    """Return the current synchronization status."""

    initialize_cloud_storage()

    manifest_path = SYNC_FOLDER / "manifest.json"

    if not manifest_path.exists():
        return {
            "synced": False,
            "files": 0,
            "last_sync": None
        }

    try:
        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )

        return {
            "synced": True,
            "files": len(
                manifest.get("files", [])
            ),
            "last_sync": manifest.get(
                "created_at"
            )
        }

    except Exception:
        return {
            "synced": False,
            "files": 0,
            "last_sync": None
        }