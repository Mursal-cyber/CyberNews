document.addEventListener("DOMContentLoaded", function () {
    const search = document.getElementById("search");
    const container = document.getElementById("news-container");
    const filters = document.querySelectorAll("nav a[data-category]");
    const noResults = document.getElementById("no-results");

    let activeCategory = "all";

    function filterNews() {
        const query = search.value.trim().toLowerCase();
        const cards = container.querySelectorAll(".news-card");
        let visibleCount = 0;

        cards.forEach(function (card) {
            const category = (card.dataset.category || "").toLowerCase();
            const text = card.textContent.toLowerCase();

            const matchesCategory =
                activeCategory === "all" ||
                category === activeCategory;

            const matchesSearch = text.includes(query);
            const visible = matchesCategory && matchesSearch;

            card.style.display = visible ? "" : "none";

            if (visible) visibleCount++;
        });

        if (noResults) {
            noResults.hidden = visibleCount > 0;
        }
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

    async function loadNews() {
        try {
            const response = await fetch("/api/articles");

            if (!response.ok) {
                throw new Error("Failed to load articles");
            }

            const articles = await response.json();

            container.replaceChildren();

            articles.forEach(function (article) {
                const card = document.createElement("div");
                card.className = "news-card";
                card.dataset.category = article.category;

                const heading = document.createElement("h3");
                const link = document.createElement("a");

                link.href = "/article/" + article.id;
                link.textContent = article.title;

                heading.appendChild(link);

                const description = document.createElement("p");
                description.textContent = article.content.slice(0, 180);

                const category = document.createElement("small");
                category.textContent = article.category;

                card.appendChild(heading);
                card.appendChild(description);
                card.appendChild(category);

                container.appendChild(card);
            });

            filterNews();
        } catch (error) {
            console.error("Error loading news:", error);
            filterNews();
        }
    }

    filterNews();
    loadNews();
});
