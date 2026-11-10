import csv
import json
import re
from pathlib import Path
from typing import Any, Protocol


class ContentNotFound(LookupError):
    pass


class ContentRepository(Protocol):
    def get_course(self, course_id: str) -> dict[str, Any]: ...

    def get_class(self, class_id: str) -> dict[str, Any]: ...

    def list_running_classes(self) -> list[dict[str, str]]: ...

    def get_learning_material(self, material_id: str) -> dict[str, Any]: ...

    def get_lesson(self, course_id: str, lesson_id: str) -> dict[str, Any]: ...

    def get_teacher_page(self, page_id: str) -> dict[str, Any]: ...


class FileContentRepository:
    """CSV/JSON-backed content store implementing the repository contract."""

    _resource_identifier = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
    _class_identifier = re.compile(r"[A-Za-z0-9]{6}\Z")

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def get_course(self, course_id: str) -> dict[str, Any]:
        if not self._resource_identifier.fullmatch(course_id):
            raise ContentNotFound(f"Invalid course identifier: {course_id}")
        return self._load_json(
            self.data_dir / "courses" / course_id / "course.json"
        )

    def get_class(self, class_id: str) -> dict[str, Any]:
        if not self._class_identifier.fullmatch(class_id):
            raise ContentNotFound(f"Invalid class identifier: {class_id}")

        class_metadata = next(
            (
                row
                for row in self._read_class_catalog()
                if row["id"] == class_id
            ),
            None,
        )
        if class_metadata is None:
            raise ContentNotFound(f"No class found for '{class_id}'")

        class_data = self._load_json(
            self.data_dir / "classes" / class_id / "class.json"
        )
        return {**class_data, **class_metadata}

    def list_running_classes(self) -> list[dict[str, str]]:
        """Return the catalog entries marked as running, in CSV order."""
        return [
            row
            for row in self._read_class_catalog()
            if row["status"].casefold() == "running"
        ]

    def get_learning_material(self, material_id: str) -> dict[str, Any]:
        return self._load_resource("learning_materials", material_id)

    def get_lesson(self, course_id: str, lesson_id: str) -> dict[str, Any]:
        if not self._resource_identifier.fullmatch(course_id):
            raise ContentNotFound(f"Invalid course identifier: {course_id}")
        if not self._resource_identifier.fullmatch(lesson_id):
            raise ContentNotFound(f"Invalid lesson identifier: {lesson_id}")
        return self._load_json(
            self.data_dir
            / "courses"
            / course_id
            / "lessons"
            / f"{lesson_id}.json"
        )

    def get_teacher_page(self, page_id: str) -> dict[str, Any]:
        return self._load_resource("teacher_pages", page_id)

    def _load_resource(self, collection: str, resource_id: str) -> dict[str, Any]:
        if not self._resource_identifier.fullmatch(resource_id):
            raise ContentNotFound(f"Invalid {collection} identifier: {resource_id}")
        return self._load_json(
            self.data_dir / collection / f"{resource_id}.json"
        )

    def _read_class_catalog(self) -> list[dict[str, str]]:
        catalog_path = self.data_dir / "classes" / "classes.csv"
        try:
            catalog_file = catalog_path.open(encoding="utf-8", newline="")
        except FileNotFoundError as error:
            raise ContentNotFound(
                f"Class catalog not found: {catalog_path}"
            ) from error

        with catalog_file:
            reader = csv.DictReader(catalog_file)
            if reader.fieldnames is None:
                raise ValueError("Class catalog is missing its header row")

            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            required_columns = {"id", "period", "provider", "course", "status"}
            if not required_columns.issubset(reader.fieldnames):
                raise ValueError(
                    "Class catalog must contain id, period, provider, course, "
                    "and status columns"
                )

            seen_ids: set[str] = set()
            rows = []
            for row in reader:
                normalized_row = {
                    key.strip(): (value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }
                row_id = normalized_row.get("id", "")
                if not self._class_identifier.fullmatch(row_id):
                    raise ValueError(
                        f"Class catalog contains an invalid class ID: {row_id!r}"
                    )
                if row_id in seen_ids:
                    raise ValueError(f"Duplicate class ID in catalog: {row_id}")
                seen_ids.add(row_id)
                rows.append(normalized_row)
        return rows

    @staticmethod
    def _load_json(file_path: Path) -> dict[str, Any]:
        try:
            with file_path.open(encoding="utf-8") as content_file:
                record = json.load(content_file)
        except FileNotFoundError as error:
            raise ContentNotFound(f"Content record not found: {file_path}") from error
        if not isinstance(record, dict):
            raise ValueError(f"Expected a JSON object in {file_path}")
        return record
