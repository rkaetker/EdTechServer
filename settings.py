import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def configured_path(environment_name, default):
    """Löst konfigurierbare relative Pfade stabil vom Projektordner aus auf."""
    path = Path(os.environ.get(environment_name, default)).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


# Strukturierter JSON-Datenspeicher mit Kursen, Klassen und Inhaltsbausteinen.
CONTENT_DATA_DIR = configured_path("YEMP_CONTENT_DATA_DIR", "data")

# Standardklasse für nicht-interaktive Starts, z. B. in Docker/Gunicorn.
DEFAULT_CLASS_ID = os.environ.get("YEMP_DEFAULT_CLASS_ID")

# Einstellungen für den lokalen Flask-Entwicklungsserver.
SERVER_HOST = os.environ.get("YEMP_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("YEMP_SERVER_PORT", "5000"))
DEBUG = os.environ.get("YEMP_DEBUG", "false").lower() in {"1", "true", "yes"}