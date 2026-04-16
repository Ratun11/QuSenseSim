document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const toggle = document.getElementById("themeToggle");
    const savedTheme = localStorage.getItem("qusensesim-theme") || "light";

    body.classList.remove("light-theme", "dark-theme");
    body.classList.add(savedTheme === "dark" ? "dark-theme" : "light-theme");

    if (toggle) {
        toggle.checked = savedTheme === "dark";
        toggle.addEventListener("change", () => {
            const theme = toggle.checked ? "dark" : "light";
            body.classList.remove("light-theme", "dark-theme");
            body.classList.add(`${theme}-theme`);
            localStorage.setItem("qusensesim-theme", theme);
        });
    }
});
