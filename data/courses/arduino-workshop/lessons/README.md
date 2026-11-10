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
