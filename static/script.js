
document.addEventListener("DOMContentLoaded", function () {
    const search = document.getElementById("search");
    const cards = document.querySelectorAll(".news-card");
    const filters = document.querySelectorAll("nav a[data-category]");
    const noResults = document.getElementById("no-results");

    let activeCategory = "all";

    function filterNews() {
        const query = search.value.trim().toLowerCase();
        let visibleCount = 0;

        cards.forEach(function (card) {
            const category = card.dataset.category.toLowerCase();
            const text = card.textContent.toLowerCase();

            const matchesCategory =
                activeCategory === "all" ||
                category === activeCategory;

            const matchesSearch = text.includes(query);

            const visible = matchesCategory && matchesSearch;
            card.style.display = visible ? "" : "none";

            if (visible) visibleCount++;
        });

        noResults.hidden = visibleCount > 0;
    }

    filters.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();

            activeCategory = link.dataset.category.toLowerCase();

            filters.forEach(function (item) {
                item.classList.remove("active");
            });

            link.classList.add("active");
            filterNews();
        });
    });

    search.addEventListener("input", filterNews);
    filterNews();
});
