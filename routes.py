from flask import Blueprint, abort, current_app, render_template

pages = Blueprint("pages", __name__)


@pages.get("/")
def index():
    """Zeigt die Startseite des in app.py ausgewählten Kurses."""
    return render_template(
        "mainpage.html",
        course=current_app.config["MAINPAGE_DATA"],
    )


@pages.get("/<page_id>")
def course_page(page_id):
    """Rendert eine Seite aus der Konfiguration des aktuell gewählten Kurses."""
    course = current_app.config["MAINPAGE_DATA"]
    page = current_app.config["SIDEBAR_DATA"].get("pages", {}).get(page_id)
    if page is None:
        abort(404)
    return render_template(page["template"], course=course, page=page)