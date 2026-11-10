# YempEdTechServer

YempEdTechServer ist eine Flask-Webanwendung zur Bereitstellung von
Kursinhalten für konkrete Klassen. Lehrkräfte können die für eine Klasse
konfigurierten Stunden, Lernmaterialien und Lehrerbereiche über
eine gemeinsame Oberfläche öffnen.

## Was die App kann

- Startet mit einer interaktiven Auswahl der Klassen, die im Verzeichnis den
  Status `running` haben.
- Zeigt eine klassenbezogene Kursübersicht mit den zugehörigen Informationen
  und den für diese Klasse ausgewählten Inhalten.
- Stellt Inhalte in einer Navigation nach Stunden, Lernmaterialien und
  Lehrerbereichen bereit.
- Bietet im Lehrerbereich eine Downloadseite: Dateien und Ordner stammen aus
  dem `files/`-Verzeichnis des zur Klasse gehörenden Kurses und können als
  gemeinsames ZIP heruntergeladen werden.
- Trennt Anwendungslogik vom Dateispeicher. Aktuell werden Klassen aus CSV und
  Inhalte aus JSON geladen; die Repository-Schnittstelle hält einen späteren
  Wechsel des Datenspeichers von Services und Routen fern.

## Lokal starten

Voraussetzung ist Python 3.9 oder neuer. Abhängigkeiten installieren und den
Server starten:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Beim Start in der Konsole eine angezeigte Klassen-ID eingeben. Die App startet
anschließend auf `http://127.0.0.1:5000`. Die Server- und Datenpfad-Einstellungen
sind in [settings.py](settings.py) beschrieben und können über
Umgebungsvariablen überschrieben werden.

## Mit Docker starten

Voraussetzung ist Docker mit Docker Compose v2 (`docker compose`). Im
Projektordner die Beispielkonfiguration kopieren und starten:

```bash
cp .env.example .env
docker compose up --build -d
```

Die Beispielkonfiguration öffnet die Klasse `D4E5F6`. Für eine andere Klasse
ändere `YEMP_DEFAULT_CLASS_ID` in `.env`; die ID muss in
`data/classes/classes.csv` stehen und den Status `running` haben. Eine
ungültige oder nicht startbare ID wird beim Anwendungsstart als Fehler
gemeldet. Die Inhalte bleiben im Projektordner unter `data/` und werden
schreibgeschützt in den Container eingebunden.

Auf dem Docker-Gerät öffnet sich die Anwendung unter
`http://localhost:5000`. Mit `docker compose logs -f` lassen sich die Logs
anzeigen; `docker compose down` stoppt und entfernt den Container. Die Daten
unter `data/` bleiben dabei erhalten. Nach Code- oder Abhängigkeitsänderungen
den Container mit `docker compose up --build -d` neu bauen.

### Von anderen Geräten im selben Netzwerk zugreifen

1. Das Docker-Gerät und das andere Gerät müssen mit demselben lokalen Netzwerk
   (z. B. demselben WLAN) verbunden sein.
2. Ermittle die lokale IP-Adresse des Docker-Geräts, zum Beispiel mit
   `hostname -I` unter Linux oder `ipconfig` unter Windows.
3. Öffne auf dem anderen Gerät `http://<IP-Adresse>:5000`, zum Beispiel
   `http://192.168.1.25:5000`.
4. Falls die Seite nicht erreichbar ist, prüfe, ob die Firewall des
   Docker-Geräts eingehende Verbindungen auf TCP-Port `5000` aus dem lokalen
   Netzwerk erlaubt. Manche Gäste-WLANs sperren Geräte untereinander.

Das ist für ein vertrauenswürdiges lokales Netzwerk gedacht. Port `5000` nicht
direkt ins Internet weiterleiten. Für Zugriff von außerhalb des Netzwerks
brauchst du eine abgesicherte Veröffentlichung, z. B. über VPN oder einen
Reverse Proxy mit TLS und Authentifizierung.

## Inhalte pflegen

Kursvorlagen und Klassen sind getrennt: Eine Klasse verweist auf einen Kurs
und bestimmt, welche Inhalte in ihrer Navigation erscheinen. Die detaillierten
Anleitungen und Dateiformate stehen bei den jeweiligen Datenbereichen:

- [Klassen anlegen und konfigurieren](data/classes/README.md)
- [Kurse anlegen und konfigurieren](data/courses/README.md)
- Kursbezogene Stunden und weitere Hinweise befinden sich jeweils im
  entsprechenden Kursordner unter [data/courses/](data/courses/).

Diese Dokumente sind die maßgeblichen Pflegeanleitungen; Details zu IDs,
JSON-Feldern und Verzeichnisinhalten werden hier nicht dupliziert.

## Projektstruktur

```text
app.py                      App-Factory und Serverstart
settings.py                 zentrale Server- und Datenpfad-Konfiguration
src/
  classes/                  Klassenkontext und Startdialog
  content/                  Repository-Vertrag und Datei-Adapter für Inhalte
  courses/                  Kursbezogene Dateiliste und ZIP-Erstellung
  routes/                   HTTP-Routen
static/
  css/                      Styles nach gemeinsamem UI und Inhaltsbereich
  js/                       JavaScript nach gemeinsamem UI und Inhaltsbereich
templates/
  lessons/                  Vorlagen für Stunden
  learning_materials/       Vorlagen für Lernmaterialien
  teacher_pages/             Vorlagen für Lehrerbereiche
  base.html                  gemeinsames Layout
data/                       Klassen, Kurse und wiederverwendbare Inhalte
tests/                      automatisierte Tests
```

Die Vorlagenordner heißen `lessons`, `learning_materials` und `teacher_pages`.
Die Ordner unter `static/css/` und `static/js/` folgen denselben
Inhaltsbereichen; gemeinsame Navigation und Grundstyles liegen unter `shared`.
Kurs- und Klassendaten werden unter `data/` gepflegt, die zugehörigen
HTML-Vorlagen unter `templates/`.

## Farben anpassen

Die Farbpalette der gesamten Oberfläche ist zentral in
[`static/css/shared/colors.css`](static/css/shared/colors.css) definiert.
Farben sind dort als beschriftete CSS-Variablen gruppiert und kommentiert;
Seiten- und Komponentenstylesheets verwenden diese Variablen statt eigener
Farbwerte. Um das Erscheinungsbild anzupassen, ändere die passende Variable
in `:root` (zum Beispiel `--color-page` für den Seitenhintergrund oder
`--color-accent` für den warmen Akzent). Neue Farben sollen ebenfalls dort
benannt und dokumentiert werden, damit die Palette zentral und konsistent
bleibt.

## Tests

Die Tests laufen mit dem Python-Standardtest-Runner:

```bash
python -m unittest discover -s tests -v
```
