from collections.abc import Callable
from typing import Any

from ..content.repository import ContentNotFound, ContentRepository


class ClassContentService:
    def __init__(self, repository: ContentRepository):
        self.repository = repository

    def get_class_context(self, class_id: str) -> dict[str, Any]:
        class_record = self.repository.get_class(class_id)
        course = self.repository.get_course(class_record["course_id"])
        effective_course = {**course, **class_record.get("overrides", {})}
        content = class_record.get("content", {})

        resources = {
            "lessons": self._selected_resources(
                content.get("lessons", []),
                lambda lesson_id: self.repository.get_lesson(
                    course["id"], lesson_id
                ),
            ),
            "learning-materials": self._selected_resources(
                content.get("learning_materials", []),
                self.repository.get_learning_material,
            ),
            "teacher-pages": self._selected_resources(
                content.get("teacher_pages", []),
                self.repository.get_teacher_page,
            ),
        }

        section_labels = (
            ("lessons", "Stunde"),
            ("learning-materials", "Lernmaterial"),
            ("teacher-pages", "Lehrerbereich"),
        )
        sidebar_sections = [
            {
                "heading": heading,
                "content_type": content_type,
                "links": [
                    {"id": resource_id, "label": resource["label"]}
                    for resource_id, resource in resources[content_type].items()
                ],
            }
            for content_type, heading in section_labels
            if resources[content_type]
        ]

        return {
            "class_record": class_record,
            "course": effective_course,
            "sidebar_sections": sidebar_sections,
            "resources": resources,
        }

    def _selected_resources(
        self,
        selected_ids: list[str],
        load_resource: Callable[[str], dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        resolved: dict[str, dict[str, Any]] = {}
        for resource_id in selected_ids:
            record = load_resource(resource_id)
            resolved[resource_id] = {
                key: value
                for key, value in record.items()
                if key
                in {
                    "label",
                    "template",
                    "title",
                    "subtitle",
                    "description",
                    "number",
                    "elements",
                }
            }
        return resolved

    def get_resource(
        self, context: dict[str, Any], content_type: str, resource_id: str
    ) -> dict[str, str]:
        resource = context["resources"].get(content_type, {}).get(resource_id)
        if resource is None:
            raise ContentNotFound(
                f"'{resource_id}' is not available in this class as {content_type}"
            )
        return resource
