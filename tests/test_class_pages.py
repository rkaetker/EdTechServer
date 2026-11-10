import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote
from unittest.mock import Mock

from app import create_app
from src.classes.service import ClassContentService
from src.content.repository import FileContentRepository
from src.courses.images import CourseImageNotFound, LocalCourseImageStorage


class ClassPageTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["DEFAULT_CLASS_ID"] = "D4E5F6"
        self.client = self.app.test_client()
        self.class_id = "D4E5F6"

    def test_class_home_uses_course_data_and_selected_content(self):
        response = self.client.get(f"/classes/{self.class_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div class="page page--main">', response.data)
        self.assertIn(b"Calliope Workshop", response.data)
        self.assertIn("🤖".encode(), response.data)
        self.assertIn(b"WiSe 2026/27", response.data)
        self.assertIn(
            f"/classes/{self.class_id}/lessons/erste-stunde".encode(),
            response.data,
        )
        self.assertIn(
            f"/classes/{self.class_id}/learning-materials/shortcut".encode(),
            response.data,
        )

    def test_selected_content_pages_render(self):
        urls = (
            f"/classes/{self.class_id}/lessons/erste-stunde",
            f"/classes/{self.class_id}/learning-materials/shortcut",
            f"/classes/{self.class_id}/teacher-pages/download",
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'<div class="page">', response.data)

    def test_lesson_uses_master_template_header_and_footer(self):
        response = self.client.get(
            f"/classes/{self.class_id}/lessons/erste-stunde"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"01 - Befehle, die Calliope", response.data)
        self.assertIn(b"Dein Programm herunterladen und \xc3\xbcbertragen", response.data)
        self.assertIn(b"Download_1.png", response.data)
        self.assertIn(b"Download_2.png", response.data)
        for image_name in (
            "Download_3.jpg",
            "Download_4.png",
            "Download_5.png",
            "Download_6.png",
            "Anschlüsse.jpg",
            "NeuesProjekt_1.png",
            "NeuesProjekt_2.png",
            "NeuesProjekt_3.png",
            "NeuesProjekt_4.png",
            "NeuesProjekt_5.png",
            "NeuesProjekt_6.png",
        ):
            with self.subTest(image_name=image_name):
                self.assertIn(quote(image_name).encode(), response.data)
        self.assertIn(b"Die MakeCode-Oberfl\xc3\xa4che kennenlernen", response.data)
        self.assertIn(b"Dein erstes Calliope-Projekt starten", response.data)
        self.assertIn(b"Calliope anschlie\xc3\x9fen und mit Strom versorgen", response.data)
        self.assertIn(b"lesson-element", response.data)
        self.assertIn(b"lesson-image-dialog", response.data)
        self.assertIn(b"Bild vergr", response.data)
        self.assertIn(quote("Übersicht_1.png").encode(), response.data)
        self.assertIn(b"01/12", response.data)
        self.assertIn(b"lesson-date", response.data)

    def test_unselected_content_is_not_available(self):
        response = self.client.get(
            f"/classes/{self.class_id}/lessons/not-selected"
        )

        self.assertEqual(response.status_code, 404)

    def test_class_is_the_only_runtime_source_for_content_selection(self):
        repository = self.app.extensions["content_repository"]
        context = ClassContentService(repository).get_class_context(self.class_id)

        self.assertNotIn("lessons", context["course"])
        self.assertEqual(
            list(context["resources"]["lessons"]),
            ["erste-stunde"],
        )
        self.assertEqual(
            list(context["resources"]["learning-materials"]),
            ["shortcut"],
        )
        self.assertEqual(
            list(context["resources"]["teacher-pages"]),
            ["download"],
        )

    def test_lesson_id_is_resolved_from_course_content(self):
        repository = Mock()
        repository.get_class.return_value = {
            "id": self.class_id,
            "course_id": "calliope-workshop",
            "content": {"lessons": ["erste-stunde"]},
        }
        repository.get_course.return_value = {"id": "calliope-workshop"}
        repository.get_lesson.return_value = {
            "label": "Meine erste Calliope-Stunde",
            "elements": [{"type": "gallery"}],
        }

        context = ClassContentService(repository).get_class_context(self.class_id)

        self.assertEqual(
            context["resources"]["lessons"]["erste-stunde"]["label"],
            "Meine erste Calliope-Stunde",
        )
        repository.get_lesson.assert_called_once_with(
            "calliope-workshop", "erste-stunde"
        )

    def test_lessons_are_loaded_from_their_course_folder(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_dir = Path(temporary_directory)
            for course_id, label in (
                ("arduino-workshop", "Arduino Beispielstunde"),
                ("calliope-workshop", "Calliope Beispielstunde"),
            ):
                lessons_dir = data_dir / "courses" / course_id / "lessons"
                lessons_dir.mkdir(parents=True)
                (lessons_dir / "erste-stunde.json").write_text(
                    json.dumps(
                        {
                            "id": "erste-stunde",
                            "label": label,
                            "elements": [{"type": "gallery"}],
                        }
                    ),
                    encoding="utf-8",
                )

            repository = FileContentRepository(data_dir)

            arduino_lesson = repository.get_lesson("arduino-workshop", "erste-stunde")
            calliope_lesson = repository.get_lesson("calliope-workshop", "erste-stunde")

        self.assertEqual(arduino_lesson["label"], "Arduino Beispielstunde")
        self.assertEqual(calliope_lesson["label"], "Calliope Beispielstunde")

    def test_legacy_content_url_uses_default_class(self):
        self.assertEqual(self.client.get("/erste-stunde").status_code, 200)

    def test_course_images_are_served_from_the_active_courses_images_folder(self):
        image_names = (
            "Download_1.png",
            "Download_2.png",
            "Download_3.jpg",
            "Download_4.png",
            "Download_5.png",
            "Download_6.png",
            "Anschlüsse.jpg",
            "Übersicht_1.png",
        )

        for image_name in image_names:
            with self.subTest(image_name=image_name):
                response = self.client.get(
                    f"/classes/{self.class_id}/lessons/images/"
                    f"{quote('erste-stunde/' + image_name, safe='/')}"
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(response.mimetype, ("image/png", "image/jpeg"))
                response.close()

        self.assertEqual(
            self.client.get(
                "/classes/A1B2C3/lessons/images/Download_1.png"
            ).status_code,
            404,
        )

    def test_course_image_storage_rejects_paths_outside_images_folder(self):
        storage = LocalCourseImageStorage(Path("/tmp/course-images"))

        with self.assertRaises(CourseImageNotFound):
            storage.get_image_path("calliope-workshop", "../files/secret.png")

    def test_course_image_storage_accepts_images_in_lesson_subfolders(self):
        image_path = (
            Path(__file__).parents[1]
            / "data/courses/calliope-workshop/images/erste-stunde/Anschlüsse.jpg"
        )
        storage = LocalCourseImageStorage(Path(__file__).parents[1] / "data")

        self.assertEqual(
            storage.get_image_path(
                "calliope-workshop", "erste-stunde/Anschlüsse.jpg"
            ),
            image_path.resolve(),
        )

    def test_feature_grouped_static_assets_are_available(self):
        assets = (
            "css/shared/colors.css",
            "css/shared/style.css",
            "css/shared/sidebar.css",
            "css/classes/mainpage.css",
            "css/lessons/page.css",
            "css/lessons/elements/master.css",
            "css/lessons/elements/gallery.css",
            "js/lessons/elements/gallery.js",
            "css/learning_materials/shortcut.css",
            "css/teacher_pages/lehrerbereich.css",
            "js/shared/sidebar.js",
            "js/learning_materials/shortcut.js",
            "js/teacher_pages/download.js",
        )

        for asset in assets:
            with self.subTest(asset=asset):
                response = self.client.get(f"/static/{asset}")
                self.assertEqual(response.status_code, 200)
                response.close()


if __name__ == "__main__":
    unittest.main()
