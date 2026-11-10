// Steuert das Ein- und Ausklappen der Sidebar auf allen Seiten.
const layout = document.querySelector("#page-layout");
const sidebar = document.querySelector("#sidebar");
const toggle = document.querySelector("#sidebar-toggle");
const toggleIcon = document.querySelector(".sidebar-toggle-icon");
const storageKey = "yemp-sidebar-collapsed";

function setSidebarCollapsed(collapsed) {
    layout.classList.toggle("is-sidebar-collapsed", collapsed);
    sidebar.classList.toggle("is-collapsed", collapsed);
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.setAttribute("aria-label", collapsed ? "Sidebar ausklappen" : "Sidebar einklappen");
    toggle.title = collapsed ? "Sidebar ausklappen" : "Sidebar einklappen";
    toggleIcon.textContent = collapsed ? "\u203A" : "\u2039";
}

let isCollapsed = false;
try {
    isCollapsed = localStorage.getItem(storageKey) === "true";
} catch {
    // Die Sidebar funktioniert auch, wenn der Browser lokalen Speicher blockiert.
}

setSidebarCollapsed(isCollapsed);

toggle.addEventListener("click", () => {
    isCollapsed = !sidebar.classList.contains("is-collapsed");
    setSidebarCollapsed(isCollapsed);
    try {
        localStorage.setItem(storageKey, String(isCollapsed));
    } catch {
        // Der Zustand gilt bis zum Neuladen der Seite.
    }
});