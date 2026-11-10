# Stunden: Calliope Workshop

Jede konkrete Stunde dieses Kurses wird als `<id>.json` in diesem Ordner
definiert. Der Datensatz enthält `id`, `label`, `title`, `subtitle`,
`description`, `number` (manuell gepflegt, z. B. `01/12`) und `elements`.
Eine Klasse wählt Stunden in ihrer `class.json` anhand der IDs unter
`content.lessons` aus.

`elements` ist eine geordnete Liste von wiederverwendbaren Inhalten. Jedes
Element hat einen `type`, eine `heading` und optional einen `subtitle`. Die
gemeinsame Elementvorlage stellt weiße Karten mit Überschrift und Untertitel
bereit. Für `type: "gallery"` enthält das Element zusätzlich `images` mit
Bildblöcken. Jeder Bildblock enthält `image` (Dateiname aus dem Kursordner
`images/`), `alt`, `heading` und `text`. Siehe
[`erste-stunde.json`](erste-stunde.json) als Beispiel.
