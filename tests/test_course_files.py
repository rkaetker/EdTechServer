import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from app import create_app
from src.courses.file_storage import (
    CourseFilesNotFound,
    InvalidCourseFileSelection,
    LocalCourseFileStorage,
)


class CourseFileTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary_directory.name)
        self.storage = LocalCourseFileStorage(self.data_dir)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_course_file(self, course_id: str, relative_path: str, content: str):
        file_path = self.data_dir / "courses" / course_id / "files" / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_file_browser_is_scoped_to_the_requested_course(self):
        self.create_course_file("arduino-workshop", "code/main.ino", "arduino")
        self.create_course_file("calliope-workshop", "code/main.py", "calliope")

        arduino_files = self.storage.list_course_files("arduino-workshop")
        calliope_files = self.storage.list_course_files("calliope-workshop")

        self.assertEqual(
            {entry["path"] for entry in arduino_files},
            {"code", "code/main.ino"},
        )
        self.assertEqual(
            {entry["path"] for entry in calliope_files},
            {"code", "code/main.py"},
        )

    def test_selected_file_and_folder_are_downloaded_as_one_archive(self):
        self.create_course_file("arduino-workshop", "single.txt", "single file")
        self.create_course_file("arduino-workshop", "examples/one.txt", "one")
        self.create_course_file("arduino-workshop", "examples/nested/two.txt", "two")

        archive_bytes = self.storage.create_course_files_archive(
            "arduino-workshop",
            ["single.txt", "examples"],
        )

        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            self.assertEqual(
                set(archive.namelist()),
                {
                    "single.txt",
                    "examples/one.txt",
                    "examples/nested/two.txt",
                },
            )
            self.assertEqual(archive.read("examples/nested/two.txt"), b"two")

    def test_archive_rejects_paths_outside_course_files(self):
        self.create_course_file("arduino-workshop", "visible.txt", "safe")

        with self.assertRaises(InvalidCourseFileSelection):
            self.storage.create_course_files_archive(
                "arduino-workshop", ["../secret.txt"]
            )

    def test_browser_reports_missing_course_files_folder(self):
        with self.assertRaises(CourseFilesNotFound):
            self.storage.list_course_files("arduino-workshop")

    def test_download_page_uses_active_class_course_files_directory(self):
        self.create_course_file("arduino-workshop", "lesson.txt", "arduino file")
        app = create_app()
        app.extensions["course_file_storage"] = self.storage
        app.config["TESTING"] = True
        app.config["DEFAULT_CLASS_ID"] = "A1B2C3"
        client = app.test_client()

        page = client.get("/classes/A1B2C3/teacher-pages/download")
        download = client.post(
            "/classes/A1B2C3/teacher-pages/download/files",
            data={"selected_paths": ["lesson.txt"]},
        )

        self.assertEqual(page.status_code, 200)
        self.assertIn(b"arduino-workshop/files", page.data)
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.mimetype, "application/zip")
        with zipfile.ZipFile(io.BytesIO(download.data)) as archive:
            self.assertEqual(archive.read("lesson.txt"), b"arduino file")

    def test_download_endpoint_rejects_empty_and_traversal_selections(self):
        self.create_course_file("arduino-workshop", "visible.txt", "safe")
        app = create_app()
        app.config["TESTING"] = True
        app.config["DEFAULT_CLASS_ID"] = "A1B2C3"
        app.extensions["course_file_storage"] = self.storage
        client = app.test_client()

        empty_selection = client.post(
            "/classes/A1B2C3/teacher-pages/download/files"
        )
        traversal_selection = client.post(
            "/classes/A1B2C3/teacher-pages/download/files",
            data={"selected_paths": ["../../outside.txt"]},
        )

        self.assertEqual(empty_selection.status_code, 400)
        self.assertEqual(traversal_selection.status_code, 400)


if __name__ == "__main__":
    unittest.main()
