from typing import Any, Protocol


class CourseFileStorage(Protocol):
    def list_course_files(self, course_id: str) -> list[dict[str, Any]]: ...

    def create_course_files_archive(
        self, course_id: str, selected_paths: list[str]
    ) -> bytes: ...


class CourseFileService:
    """Application service for browsing and downloading course-owned files."""

    def __init__(self, storage: CourseFileStorage):
        self.storage = storage

    def list_files(self, course_id: str) -> list[dict[str, Any]]:
        return self.storage.list_course_files(course_id)

    def create_download(
        self, course_id: str, selected_paths: list[str]
    ) -> bytes:
        return self.storage.create_course_files_archive(course_id, selected_paths)
