from datetime import date

from flask import Flask

from src.classes.selector import (
    ClassSelectionCancelled,
    NoRunningClassesError,
    select_running_class,
)
from src.content.repository import FileContentRepository
from src.courses.file_storage import LocalCourseFileStorage
from src.courses.images import LocalCourseImageStorage
from src.routes.pages import pages
from settings import (
    CONTENT_DATA_DIR,
    DEFAULT_CLASS_ID,
    DEBUG,
    SERVER_HOST,
    SERVER_PORT,
)


def create_app(repository=None):
    app = Flask(__name__)
    app.extensions["content_repository"] = repository or FileContentRepository(
        CONTENT_DATA_DIR
    )
    app.extensions["course_file_storage"] = LocalCourseFileStorage(
        CONTENT_DATA_DIR
    )
    app.extensions["course_image_storage"] = LocalCourseImageStorage(
        CONTENT_DATA_DIR
    )
    app.config["DEFAULT_CLASS_ID"] = DEFAULT_CLASS_ID
    if DEFAULT_CLASS_ID:
        running_class_ids = {
            item["id"]
            for item in app.extensions[
                "content_repository"
            ].list_running_classes()
        }
        if DEFAULT_CLASS_ID not in running_class_ids:
            raise ValueError(
                f"YEMP_DEFAULT_CLASS_ID={DEFAULT_CLASS_ID!r} must match "
                "a class with status 'running'."
            )
    app.register_blueprint(pages)

    @app.context_processor
    def add_common_template_values():
        return {"current_date": date.today().strftime("%d.%m.%Y")}

    return app


app = create_app()


def main():
    """Choose a running class before starting the development server."""
    repository = app.extensions["content_repository"]
    try:
        selected_class_id = select_running_class(repository)
    except (ClassSelectionCancelled, NoRunningClassesError) as error:
        print(error)
        return 1

    app.config["DEFAULT_CLASS_ID"] = selected_class_id
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG,
        use_reloader=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
