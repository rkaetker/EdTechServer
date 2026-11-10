import re
from pathlib import Path


class CourseImageNotFound(LookupError):
    pass


class LocalCourseImageStorage:
    """Resolves image files from data/courses/<course-id>/images."""

    _course_identifier = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
    _allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def get_image_path(self, course_id: str, filename: str) -> Path:
        if not self._course_identifier.fullmatch(course_id):
            raise CourseImageNotFound(f"Unknown course: {course_id}")
        path_parts = filename.split("/")
        if (
            not filename
            or filename.startswith("/")
            or "\\" in filename
            or any(part in {"", ".", ".."} for part in path_parts)
            or Path(path_parts[-1]).suffix.casefold() not in self._allowed_extensions
        ):
            raise CourseImageNotFound("Unknown course image.")

        courses_dir = (self.data_dir / "courses").resolve()
        course_dir = courses_dir / course_id
        images_dir = course_dir / "images"
        image_path = images_dir.joinpath(*path_parts)
        path_to_check = images_dir
        has_symlink = course_dir.is_symlink() or images_dir.is_symlink()
        for part in path_parts:
            path_to_check = path_to_check / part
            has_symlink = has_symlink or path_to_check.is_symlink()
        if has_symlink:
            raise CourseImageNotFound("Course image path is not available.")

        try:
            resolved_course = course_dir.resolve(strict=True)
            resolved_course.relative_to(courses_dir)
            resolved_images = (resolved_course / "images").resolve(strict=True)
            resolved_images.relative_to(resolved_course)
            resolved_image = resolved_images.joinpath(*path_parts).resolve(strict=True)
            resolved_image.relative_to(resolved_images)
        except (FileNotFoundError, ValueError) as error:
            raise CourseImageNotFound("Course image not found.") from error

        if not resolved_image.is_file():
            raise CourseImageNotFound("Course image not found.")
        return resolved_image
