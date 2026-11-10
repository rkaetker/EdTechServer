import io
import os
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


class LocalCourseFileStorage:
    """Reads course files from data/courses/<course-id>/files."""

    _course_identifier = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def list_course_files(self, course_id: str) -> list[dict[str, Any]]:
        files_dir = self._course_files_dir(course_id)
        entries: list[dict[str, Any]] = []

        for directory, directory_names, file_names in os.walk(
            files_dir, followlinks=False
        ):
            current_dir = Path(directory)
            directory_names[:] = sorted(
                name
                for name in directory_names
                if name != ".gitkeep" and not (current_dir / name).is_symlink()
            )
            for name in directory_names:
                entries.append(
                    self._file_entry(files_dir, current_dir / name, is_dir=True)
                )
            for name in sorted(file_names):
                path = current_dir / name
                if name == ".gitkeep" or path.is_symlink() or not path.is_file():
                    continue
                entries.append(self._file_entry(files_dir, path, is_dir=False))

        return sorted(
            entries,
            key=lambda entry: (entry["path"].casefold(), entry["is_dir"]),
        )

    def create_course_files_archive(
        self, course_id: str, selected_paths: list[str]
    ) -> bytes:
        if not selected_paths:
            raise InvalidCourseFileSelection(
                "Mindestens eine Datei oder ein Ordner muss ausgewählt werden."
            )

        files_dir = self._course_files_dir(course_id)
        selected = self._resolve_selected_paths(files_dir, selected_paths)
        archive_buffer = io.BytesIO()
        written: set[str] = set()

        with zipfile.ZipFile(
            archive_buffer, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for _, path in selected:
                if path.is_file():
                    self._add_file_to_archive(archive, files_dir, path, written)
                else:
                    self._add_directory_to_archive(
                        archive, files_dir, path, written
                    )

        return archive_buffer.getvalue()

    def _course_files_dir(self, course_id: str) -> Path:
        if not self._course_identifier.fullmatch(course_id):
            raise CourseFilesNotFound(f"Unknown course: {course_id}")

        courses_dir = (self.data_dir / "courses").resolve()
        course_dir = courses_dir / course_id
        if course_dir.is_symlink():
            raise ValueError("Course directories must not be symlinks.")
        try:
            resolved_course_dir = course_dir.resolve(strict=True)
            resolved_course_dir.relative_to(courses_dir)
            files_dir = resolved_course_dir / "files"
            if files_dir.is_symlink():
                raise ValueError("Course files directories must not be symlinks.")
            resolved_files_dir = files_dir.resolve(strict=True)
        except FileNotFoundError as error:
            raise CourseFilesNotFound(
                f"Course files directory not found for '{course_id}'."
            ) from error
        except ValueError as error:
            raise ValueError("Course files directory resolves outside its course.") from error

        if not resolved_files_dir.is_dir():
            raise CourseFilesNotFound(
                f"Course files directory not found for '{course_id}'."
            )
        return resolved_files_dir

    @staticmethod
    def _file_entry(
        files_dir: Path, path: Path, *, is_dir: bool
    ) -> dict[str, Any]:
        relative_path = path.relative_to(files_dir).as_posix()
        return {
            "path": relative_path,
            "name": path.name,
            "is_dir": is_dir,
            "depth": len(PurePosixPath(relative_path).parts) - 1,
            "size": None if is_dir else path.stat().st_size,
        }

    @staticmethod
    def _resolve_selected_paths(
        files_dir: Path, selected_paths: list[str]
    ) -> list[tuple[str, Path]]:
        resolved: dict[str, Path] = {}
        for selected_path in selected_paths:
            if not isinstance(selected_path, str) or "\\" in selected_path:
                raise InvalidCourseFileSelection("Ungültiger Dateipfad.")
            path_parts = selected_path.split("/")
            if (
                not selected_path
                or selected_path.startswith("/")
                or any(part in {"", ".", ".."} for part in path_parts)
            ):
                raise InvalidCourseFileSelection("Ungültiger Dateipfad.")

            path = files_dir.joinpath(*path_parts)
            current_path = files_dir
            for part in path_parts:
                current_path = current_path / part
                if current_path.is_symlink():
                    raise InvalidCourseFileSelection(
                        "Symlinks können nicht heruntergeladen werden."
                    )
            try:
                resolved_path = path.resolve(strict=True)
                resolved_path.relative_to(files_dir)
            except (FileNotFoundError, ValueError) as error:
                raise InvalidCourseFileSelection(
                    "Die Auswahl enthält einen unbekannten Pfad."
                ) from error
            if not (resolved_path.is_file() or resolved_path.is_dir()):
                raise InvalidCourseFileSelection(
                    "Ausgewählt werden können nur Dateien und Ordner."
                )
            resolved[selected_path] = resolved_path

        sorted_paths = sorted(
            resolved.items(), key=lambda item: (item[0].count("/"), item[0])
        )
        roots: list[tuple[str, Path]] = []
        for relative_path, path in sorted_paths:
            if any(
                path.is_relative_to(parent_path) and parent_path.is_dir()
                for _, parent_path in roots
            ):
                continue
            roots.append((relative_path, path))
        return roots

    @staticmethod
    def _add_file_to_archive(
        archive: zipfile.ZipFile,
        files_dir: Path,
        path: Path,
        written: set[str],
    ) -> None:
        archive_path = path.relative_to(files_dir).as_posix()
        if archive_path not in written:
            archive.write(path, archive_path)
            written.add(archive_path)

    def _add_directory_to_archive(
        self,
        archive: zipfile.ZipFile,
        files_dir: Path,
        directory: Path,
        written: set[str],
    ) -> None:
        for current_directory, directory_names, file_names in os.walk(
            directory, followlinks=False
        ):
            current_path = Path(current_directory)
            directory_names[:] = sorted(
                name
                for name in directory_names
                if name != ".gitkeep" and not (current_path / name).is_symlink()
            )
            visible_files = [
                name
                for name in sorted(file_names)
                if name != ".gitkeep"
                and not (current_path / name).is_symlink()
                and (current_path / name).is_file()
            ]
            archive_directory = current_path.relative_to(files_dir).as_posix()
            if not directory_names and not visible_files:
                archive_path = f"{archive_directory.rstrip('/')}/"
                if archive_path not in written:
                    archive.writestr(archive_path, "")
                    written.add(archive_path)
            for name in visible_files:
                self._add_file_to_archive(
                    archive, files_dir, current_path / name, written
                )


class InvalidCourseFileSelection(ValueError):
    pass


class CourseFilesNotFound(LookupError):
    pass
