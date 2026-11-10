# Klassen anlegen

1. Eine eindeutige ID aus genau sechs Buchstaben oder Ziffern festlegen, z. B.
   `D4E5F6`.
2. In `classes.csv` eine Zeile mit `id`, `period`, `provider`, `course`,
   `participant` und `status` ergänzen. `course` muss der ID eines vorhandenen
   Kurses entsprechen. Nur Klassen mit `status=running` erscheinen bei der
   Serverauswahl.
3. Den Ordner `classes/<ID>/` anlegen und darin `class.json` erstellen. Die
   Kurs-ID und die Inhalte der Klasse werden dort eingetragen:

   ```json
   {
     "id": "D4E5F6",
     "name": "Name der Klasse",
     "course_id": "calliope-workshop",
     "overrides": {},
     "content": {
       "lessons": ["erste-stunde"],
       "learning_materials": [],
       "teacher_pages": []
     }
   }
   ```

   `lessons`, `learning_materials` und `teacher_pages` enthalten IDs. Eine
   Stunde muss als Kursdatensatz unter
   `data/courses/<course_id>/lessons/<id>.json` vorhanden sein; zum Beispiel
   `"lessons": ["erste-stunde"]`. Lernmaterialien und Lehrerbereiche werden
   ebenfalls per ID ausgewählt, zum Beispiel
   `"teacher_pages": ["download"]`. Ihre Datensätze liegen unter
   `data/learning_materials/` bzw. `data/teacher_pages/`. Semester und Anbieter
   werden nur in der CSV gepflegt; der Zeitraum steht in der Spalte `period`.
