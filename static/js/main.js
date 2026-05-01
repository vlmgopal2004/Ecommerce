document.addEventListener("DOMContentLoaded", () => {

    const navbar = document.querySelector(".eshop-navbar");
    if (!navbar) return;

    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.classList.add("shadow-lg");
        } else {
            navbar.classList.remove("shadow-lg");
        }
    });

});
