import json
from datetime import date

from flask import Flask
from routes import pages
from settings import (
    DEBUG,
    MAINPAGE_DATA_FILE,
    SCRIPT_STORAGE_DIR,
    SERVER_HOST,
    SERVER_PORT,
    SIDEBAR_DATA_FILE,
)

# Flask sucht HTML-Vorlagen im Ordner "templates" und CSS-Dateien in "static".
app = Flask(__name__)

# Kursstartseite und Navigation kommen aus dem in settings.py gewählten Ordner.
with MAINPAGE_DATA_FILE.open(encoding="utf-8") as mainpage_file:
    MAINPAGE_DATA = json.load(mainpage_file)

with SIDEBAR_DATA_FILE.open(encoding="utf-8") as sidebar_file:
    SIDEBAR_DATA = json.load(sidebar_file)

app.config["MAINPAGE_DATA"] = MAINPAGE_DATA
app.config["SIDEBAR_DATA"] = SIDEBAR_DATA
app.config["SCRIPT_STORAGE_DIR"] = SCRIPT_STORAGE_DIR
app.register_blueprint(pages)


@app.context_processor
def add_sidebar_sections():
    """Stellt gemeinsame Navigations- und Datumswerte in HTML-Vorlagen bereit."""
    return {
        "sidebar_sections": app.config["SIDEBAR_DATA"]["sections"],
        "current_date": date.today().strftime("%d.%m.%Y"),
    }


if __name__ == "__main__":
    # Startet den Entwicklungsserver und macht ihn im lokalen Netzwerk erreichbar.
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)