# Kurse anlegen

1. Eine eindeutige Kurs-ID als kleingeschriebenen Bezeichner mit Bindestrichen
   wählen, z. B. `web-workshop`.
2. Den Ordner `courses/<Kurs-ID>/` anlegen und darin `course.json` mit den
   Kurs-Grunddaten erstellen:

   ```json
   {
     "id": "web-workshop",
     "title": "Web Workshop",
     "symbol": "🤖",
     "description": "Kursbeschreibung",
     "properties": [],
     "footer": "Yemp EdTech"
   }
   ```
   `symbol` bestimmt das Symbol auf der Mainpage und wird direkt im Kursdatensatz
   gepflegt.

3. In `classes.csv` beim Klassenfeld `course` diese Kurs-ID eintragen. Die
   konkrete Inhaltsauswahl wird ausschließlich in der jeweiligen
   `classes/<ID>/class.json` unter `content` gepflegt.
4. Den Unterordner `lessons/` anlegen. Jede konkrete Stunde des Kurses erhält
   dort eine `<id>.json`-Datei mit `id`, `label`, `title`, `subtitle`,
   `description`, `number` und `elements`. `number` wird manuell gepflegt
   (z. B. `01/12`). Jedes Element hat einen `type`, eine `heading` und
   optional einen `subtitle`. Für Bildsammlungen kann `type: "gallery"` mit
   einer `images`-Liste verwendet werden. Bilder der Stunde liegen im
   Kursordner `images/`; in der JSON-Stunde referenziert `image` nur den
   Dateinamen. In `class.json` werden anschließend nur die Stunden-IDs
   ausgewählt.
5. Den Unterordner `files/` anlegen. Dateien und Unterordner darin werden auf
   der Downloadseite der zugehörigen Klassen automatisch angeboten.
6. Die Kurs-README kann weitere Hinweise zu den Stunden enthalten. Die
   JSON-Datensätze in `lessons/` sind die Laufzeitquelle für ihre Metadaten.
