function toggleFavorite(btn) {
    btn.classList.toggle("active");

    const icon = btn.querySelector("i");
    if (btn.classList.contains("active")) {
        icon.classList.remove("bi-heart");
        icon.classList.add("bi-heart-fill");
    } else {
        icon.classList.remove("bi-heart-fill");
        icon.classList.add("bi-heart");
    }
}
