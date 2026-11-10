# Stunden: Arduino Workshop

Jede konkrete Stunde dieses Kurses wird als `<id>.json` in diesem Ordner
definiert. Neben `id` und `label` enthält sie den Titel,
Untertitel, die Stundenbeschreibung und die manuell gepflegte Nummer im Format
`01/12` sowie eine Liste von `elements`. Beispiel:

```json
{
  "id": "erste-stunde",
  "label": "Erste Stunde",
  "title": "Titel der Stunde",
  "subtitle": "Untertitel der Stunde",
  "description": "Kurze Beschreibung der Lernziele und des Ablaufs.",
  "number": "01/12",
  "elements": [
    {
      "type": "gallery",
      "heading": "Bildergalerie",
      "subtitle": "Eine kurze Einführung.",
      "images": []
    },
    {
      "type": "table",
      "heading": "Bauteile im Vergleich",
      "subtitle": "Die wichtigsten Eigenschaften auf einen Blick.",
      "headers": ["Bauteil", "Aufgabe"],
      "rows": [
        ["LED", "Leuchtet, wenn Strom fließt."],
        ["Widerstand", "Begrenzt den Strom."]
      ]
    },
    {
      "type": "instructions",
      "heading": "So gehst du vor",
      "subtitle": "Arbeite die Schritte der Reihe nach ab.",
      "steps": [
        {
          "heading": "Vorbereiten",
          "text": "Schalte den Arduino aus, bevor du Kabel verbindest."
        }
      ]
    }
  ]
}
```

Jedes Element wird über `type` ausgewählt und verwendet die gemeinsame
Elementvorlage mit weißem Kasten, Überschrift und Untertitel. Weitere
Elementtypen können als eigene HTML- und CSS-Dateien unter
`templates/lessons/elements/` und `static/css/lessons/elements/` ergänzt
werden. Die Lesson-Mastervorlage zeigt Stundenmetadaten und bindet die Elemente
in der JSON-Reihenfolge ein. In der `class.json` einer Klasse wird die Stunde
anschließend nur über ihre ID ausgewählt, zum Beispiel
`"lessons": ["erste-stunde"]`.

Bei einem `table`-Element bestimmt `headers` die Anzahl und Beschriftung der
Spalten. Füge dort für weitere Spalten weitere Einträge hinzu und ergänze in
jeder Zeile unter `rows` den passenden Zellenwert. Die Kopfzeile wird
hervorgehoben dargestellt; fehlende Zellen bleiben leer.

Ein `instructions`-Element zeigt nummerierte Schritte mit jeweils einer
Überschrift und einem erklärenden Text. Nutze es zum Beispiel für
Schritt-für-Schritt-Anleitungen.
