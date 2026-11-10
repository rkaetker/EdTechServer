from collections.abc import Callable
from typing import Protocol


class RunningClassCatalog(Protocol):
    """Data access needed by the startup class selector."""

    def list_running_classes(self) -> list[dict[str, str]]: ...


class NoRunningClassesError(RuntimeError):
    """Raised when the catalog has no classes eligible for startup."""


class ClassSelectionCancelled(RuntimeError):
    """Raised when stdin closes before a class can be selected."""


def select_running_class(
    catalog: RunningClassCatalog,
    read_input: Callable[[str], str] = input,
    write_output: Callable[[str], None] = print,
) -> str:
    """Display running classes and return the ID entered by the operator."""
    classes = catalog.list_running_classes()
    if not classes:
        raise NoRunningClassesError("Keine Klassen mit Status 'running' gefunden.")

    id_width = max(len("ID"), *(len(item["id"]) for item in classes))
    course_width = max(
        len("Kurs"), *(len(item.get("course", "")) for item in classes)
    )
    provider_width = max(
        len("Anbieter"), *(len(item.get("provider", "")) for item in classes)
    )
    header = (
        f"{'ID':<{id_width}}  "
        f"{'Kurs':<{course_width}}  "
        f"{'Anbieter':<{provider_width}}"
    )
    write_output("Startbare Klassen:")
    write_output(header)
    write_output("-" * len(header))
    for item in classes:
        write_output(
            f"{item['id']:<{id_width}}  "
            f"{item.get('course', ''):<{course_width}}  "
            f"{item.get('provider', ''):<{provider_width}}"
        )

    running_ids = {item["id"] for item in classes}
    while True:
        try:
            selected_id = read_input("Klassen-ID eingeben: ").strip()
        except EOFError as error:
            raise ClassSelectionCancelled(
                "Eingabe wurde vor der Klassenauswahl beendet."
            ) from error
        if selected_id in running_ids:
            return selected_id
        write_output("Ungültige Auswahl. Bitte eine angezeigte ID eingeben.")
