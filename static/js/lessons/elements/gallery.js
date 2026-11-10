const dialog = document.querySelector(".lesson-image-dialog");

if (dialog instanceof HTMLDialogElement) {
    const image = dialog.querySelector(".lesson-image-dialog-image");
    const heading = dialog.querySelector("#lesson-image-dialog-heading");
    const text = dialog.querySelector(".lesson-image-dialog-caption p");
    const closeButton = dialog.querySelector(".lesson-image-dialog-close");

    document.querySelectorAll(".lesson-image-zoom").forEach((button) => {
        button.addEventListener("click", () => {
            image.src = button.dataset.imageSrc;
            image.alt = button.dataset.imageAlt;
            heading.textContent = button.dataset.imageHeading;
            text.textContent = button.dataset.imageText;
            dialog.showModal();
            closeButton.focus();
        });
    });

    closeButton.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) {
            dialog.close();
        }
    });
}
