import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import app as flask_app, create_app, main
from src.classes.selector import (
    ClassSelectionCancelled,
    NoRunningClassesError,
    select_running_class,
)
from src.content.repository import FileContentRepository


class ClassSelectorTests(unittest.TestCase):
    def test_app_uses_configured_default_running_class(self):
        with patch("app.DEFAULT_CLASS_ID", "D4E5F6"):
            configured_app = create_app()

        self.assertEqual(configured_app.config["DEFAULT_CLASS_ID"], "D4E5F6")

    def test_app_rejects_configured_class_that_is_not_running(self):
        with patch("app.DEFAULT_CLASS_ID", "NOTRUN"):
            with self.assertRaisesRegex(ValueError, "status 'running'"):
                create_app()

    def test_server_uses_selected_class_before_starting(self):
        with (
            patch("app.select_running_class", return_value="D4E5F6"),
            patch.object(flask_app, "run") as run_server,
        ):
            result = main()

        self.assertEqual(result, 0)
        self.assertEqual(flask_app.config["DEFAULT_CLASS_ID"], "D4E5F6")
        run_server.assert_called_once_with(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False,
        )

    def test_repository_returns_only_running_classes_and_normalizes_csv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_dir = Path(temporary_directory)
            classes_dir = data_dir / "classes"
            classes_dir.mkdir()
            (classes_dir / "classes.csv").write_text(
                "id,period,provider,course,participant,status \n"
                "A1B2C3,WiSe 2026/27,Junior Uni,arduino-workshop,12,running \n"
                "D4E5F6,SoSe 2027,Other Provider,web-course,10,planned\n",
                encoding="utf-8",
            )
            repository = FileContentRepository(data_dir)

            classes = repository.list_running_classes()

        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0]["id"], "A1B2C3")
        self.assertEqual(classes[0]["course"], "arduino-workshop")
        self.assertEqual(classes[0]["status"], "running")

    def test_selector_displays_options_and_repeats_until_running_id_entered(self):
        class Catalog:
            def list_running_classes(self):
                return [
                    {
                        "id": "A1B2C3",
                        "course": "arduino-workshop",
                        "provider": "Junior Uni",
                    }
                ]

        entered_ids = iter(("D4E5F6", "A1B2C3"))
        prompts = []
        output = []

        selected_id = select_running_class(
            Catalog(),
            read_input=lambda prompt: (prompts.append(prompt), next(entered_ids))[1],
            write_output=output.append,
        )

        self.assertEqual(selected_id, "A1B2C3")
        self.assertEqual(len(prompts), 2)
        self.assertTrue(any("arduino-workshop" in line for line in output))
        self.assertTrue(any("Junior Uni" in line for line in output))
        self.assertTrue(any("Ungültige Auswahl" in line for line in output))

    def test_selector_fails_when_no_classes_are_running(self):
        class EmptyCatalog:
            def list_running_classes(self):
                return []

        with self.assertRaises(NoRunningClassesError):
            select_running_class(EmptyCatalog(), write_output=lambda _: None)

    def test_selector_reports_closed_input(self):
        class Catalog:
            def list_running_classes(self):
                return [{"id": "A1B2C3", "course": "course", "provider": "provider"}]

        def closed_input(_prompt):
            raise EOFError(_prompt)

        with self.assertRaises(ClassSelectionCancelled):
            select_running_class(
                Catalog(),
                read_input=closed_input,
                write_output=lambda _: None,
            )


if __name__ == "__main__":
    unittest.main()
