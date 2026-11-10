from io import BytesIO

from flask import (
    Blueprint,
    abort,
    current_app,
    render_template,
    request,
    send_file,
)

from ..classes.service import ClassContentService
from ..content.repository import ContentNotFound
from ..courses.files import CourseFileService
from ..courses.file_storage import (
    CourseFilesNotFound,
    InvalidCourseFileSelection,
)
from ..courses.images import CourseImageNotFound

pages = Blueprint("pages", __name__)


def _service() -> ClassContentService:
    return ClassContentService(current_app.extensions["content_repository"])


def _course_file_service() -> CourseFileService:
    return CourseFileService(current_app.extensions["course_file_storage"])


def _course_image_storage():
    return current_app.extensions["course_image_storage"]


def _render_class_page(class_id: str, content_type: str, content_id: str):
    service = _service()
    try:
        context = service.get_class_context(class_id)
        resource = service.get_resource(context, content_type, content_id)
    except ContentNotFound:
        abort(404)

    template_context = {
        "course": context["course"],
        "class_record": context["class_record"],
        "sidebar_sections": context["sidebar_sections"],
        "lesson": resource,
    }
    if content_type == "teacher-pages" and content_id == "download":
        try:
            template_context["course_files"] = _course_file_service().list_files(
                context["course"]["id"]
            )
        except ContentNotFound:
            abort(404)
        except CourseFilesNotFound:
            abort(404)

    template_name = (
        "lessons/master.html"
        if content_type == "lessons"
        else resource["template"]
    )
    return render_template(template_name, **template_context)


@pages.get("/classes/<class_id>/lessons/images/<path:filename>")
def course_lesson_image(class_id: str, filename: str):
    try:
        context = _service().get_class_context(class_id)
        image_path = _course_image_storage().get_image_path(
            context["course"]["id"], filename
        )
    except ContentNotFound:
        abort(404)
    except CourseImageNotFound:
        abort(404)

    return send_file(image_path)


@pages.post("/classes/<class_id>/teacher-pages/download/files")
def download_course_files(class_id: str):
    try:
        context = _service().get_class_context(class_id)
        _service().get_resource(context, "teacher-pages", "download")
        selected_paths = request.form.getlist("selected_paths")
        archive = _course_file_service().create_download(
            context["course"]["id"], selected_paths
        )
    except ContentNotFound:
        abort(404)
    except CourseFilesNotFound:
        abort(404)
    except InvalidCourseFileSelection as error:
        abort(400, description=str(error))

    return send_file(
        BytesIO(archive),
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{context['course']['id']}-dateien.zip",
    )


@pages.get("/")
def index():
    """Zeigt die Startseite der konfigurierten Standardklasse."""
    return render_template_class_home(current_app.config["DEFAULT_CLASS_ID"])


@pages.get("/classes/<class_id>")
def class_home(class_id: str):
    """Zeigt die Kursinformationen mit den Auswahlen einer konkreten Klasse."""
    return render_template_class_home(class_id)


def render_template_class_home(class_id: str):
    try:
        context = _service().get_class_context(class_id)
    except ContentNotFound:
        abort(404)
    return render_template(
        "mainpage.html",
        course=context["course"],
        class_record=context["class_record"],
        sidebar_sections=context["sidebar_sections"],
    )


@pages.get("/classes/<class_id>/<content_type>/<content_id>")
def class_content(class_id: str, content_type: str, content_id: str):
    return _render_class_page(class_id, content_type, content_id)


@pages.get("/<page_id>")
def default_class_content(page_id: str):
    """Behält bisherige Inhalts-URLs für die Standardklasse bei."""
    class_id = current_app.config["DEFAULT_CLASS_ID"]
    try:
        context = _service().get_class_context(class_id)
    except ContentNotFound:
        abort(404)

    for content_type, items in context["resources"].items():
        if page_id in items:
            return _render_class_page(class_id, content_type, page_id)
    abort(404)
