import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def configured_path(environment_name, default):
    """Löst konfigurierbare relative Pfade stabil vom Projektordner aus auf."""
    path = Path(os.environ.get(environment_name, default)).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


# Auf diesen Ordner mit mainpage.json, sidebar.json und weiteren Kursdaten zeigen.
COURSE_DATA_DIR = configured_path(
    "YEMP_COURSE_DATA_DIR", "courses/arduino-workshop"
)
MAINPAGE_DATA_FILE = COURSE_DATA_DIR / "mainpage.json"
SIDEBAR_DATA_FILE = COURSE_DATA_DIR / "sidebar.json"

# Speicherort für später hochgeladene Skriptdateien.
SCRIPT_STORAGE_DIR = configured_path("YEMP_SCRIPT_STORAGE_DIR", "storage/scripts")

# Einstellungen für den lokalen Flask-Entwicklungsserver.
SERVER_HOST = os.environ.get("YEMP_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("YEMP_SERVER_PORT", "5000"))
DEBUG = os.environ.get("YEMP_DEBUG", "false").lower() in {"1", "true", "yes"}