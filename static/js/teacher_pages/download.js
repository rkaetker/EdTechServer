const form = document.querySelector("[data-download-form]");

if (form) {
    const checkboxes = Array.from(
        form.querySelectorAll('input[name="selected_paths"]')
    );
    const folderCheckboxes = checkboxes.filter((checkbox) =>
        checkbox.hasAttribute("data-folder-checkbox")
    );
    const countLabel = form.querySelector("[data-selection-count]");
    const downloadButton = form.querySelector("[data-download-button]");

    const updateSelectionSummary = () => {
        const selectedCount = checkboxes.filter((checkbox) => checkbox.checked).length;
        countLabel.textContent = `${selectedCount} ausgewählt`;
        downloadButton.disabled = selectedCount === 0;
    };

    const updateFolderStates = () => {
        folderCheckboxes
            .slice()
            .sort(
                (left, right) =>
                    right.dataset.filePath.length - left.dataset.filePath.length
            )
            .forEach((folderCheckbox) => {
                const folderPath = `${folderCheckbox.dataset.filePath}/`;
                const descendants = checkboxes.filter(
                    (checkbox) =>
                        checkbox !== folderCheckbox &&
                        checkbox.dataset.filePath.startsWith(folderPath)
                );
                if (descendants.length === 0) {
                    return;
                }
                const selectedDescendants = descendants.filter(
                    (checkbox) => checkbox.checked
                ).length;

                folderCheckbox.checked = selectedDescendants === descendants.length;
                folderCheckbox.indeterminate =
                    selectedDescendants > 0 &&
                    selectedDescendants < descendants.length;
            });
    };

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            if (checkbox.hasAttribute("data-folder-checkbox")) {
                const folderPath = `${checkbox.dataset.filePath}/`;
                checkboxes
                    .filter((childCheckbox) =>
                        childCheckbox.dataset.filePath.startsWith(folderPath)
                    )
                    .forEach((childCheckbox) => {
                        childCheckbox.checked = checkbox.checked;
                        childCheckbox.indeterminate = false;
                    });
            }

            updateFolderStates();
            updateSelectionSummary();
        });
    });

    updateSelectionSummary();
}
