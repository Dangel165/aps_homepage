// Keep JavaScript minimal: only enhance static text without handling input.
(() => {
  "use strict";

  const yearElement = document.getElementById("current-year");

  if (yearElement) {
    yearElement.textContent = String(new Date().getFullYear());
  }

  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");

    if (!link || motionQuery.matches) {
      return;
    }

    const nextUrl = new URL(link.href, window.location.href);
    const currentUrl = new URL(window.location.href);

    if (
      nextUrl.origin !== currentUrl.origin ||
      nextUrl.pathname === currentUrl.pathname ||
      link.target ||
      link.hasAttribute("download")
    ) {
      return;
    }

    event.preventDefault();
    document.body.classList.add("page-leaving");

    window.setTimeout(() => {
      window.location.href = nextUrl.href;
    }, 220);
  });
})();
