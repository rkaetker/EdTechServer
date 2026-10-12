const shortcutSelect = document.querySelector("#shortcut-select");
const keyboard = document.querySelector(".keyboard");
const combinationLabel = document.querySelector("#shortcut-combination");

if (shortcutSelect && keyboard && combinationLabel) {
    const keycaps = [...keyboard.querySelectorAll("[data-key]")];
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let animationTimers = [];

    function clearKeyAnimation() {
        animationTimers.forEach(window.clearTimeout);
        animationTimers = [];
        keycaps.forEach((keycap) => keycap.classList.remove("is-pressing"));
    }

    function showShortcut(option) {
        clearKeyAnimation();
        combinationLabel.textContent = option.dataset.combination;
        const activeKeys = new Set(option.dataset.keys.split(" "));
        const matchingKeys = keycaps.filter((keycap) => activeKeys.has(keycap.dataset.key));

        keycaps.forEach((keycap) => {
            keycap.classList.toggle("is-active", activeKeys.has(keycap.dataset.key));
        });

        if (reducedMotion) {
            return;
        }

        matchingKeys.forEach((keycap, index) => {
            animationTimers.push(window.setTimeout(() => {
                keycap.classList.add("is-pressing");
                animationTimers.push(window.setTimeout(() => {
                    keycap.classList.remove("is-pressing");
                }, 180));
            }, index * 130));
        });
    }

    shortcutSelect.addEventListener("change", () => {
        showShortcut(shortcutSelect.selectedOptions[0]);
    });

    showShortcut(shortcutSelect.selectedOptions[0]);
}