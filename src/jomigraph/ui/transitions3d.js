/**
 * JomiGraph AI — Accessible 3D Transitions Module (Phase 15)
 * ==========================================================
 * Provides go3d(fromEl, toEl, kind, direction) with graceful fallback,
 * reduced-motion respect, focus management, and deadlock prevention.
 */
(function () {
  "use strict";

  let isTransitioning = false;

  function isReducedMotion() {
    return (
      document.body.classList.contains("reduce-motion") ||
      (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)
    );
  }

  /**
   * Transition smoothly between two views using 3D perspective transforms.
   * @param {HTMLElement} fromEl Current view element
   * @param {HTMLElement} toEl Incoming view element
   * @param {string} kind 'slide' | 'zoom' | 'flip'
   * @param {string} direction 'forward' | 'back'
   * @returns {Promise<void>}
   */
  window.go3d = function (fromEl, toEl, kind = "slide", direction = "forward") {
    return new Promise(function (resolve) {
      if (!fromEl || !toEl || fromEl === toEl || isReducedMotion()) {
        if (fromEl) fromEl.style.display = "none";
        if (toEl) {
          toEl.style.display = "";
          focusHeading(toEl);
        }
        resolve();
        return;
      }

      // Prevent concurrent transition conflicts
      if (isTransitioning) {
        if (fromEl) fromEl.style.display = "none";
        if (toEl) {
          toEl.style.display = "";
          focusHeading(toEl);
        }
        resolve();
        return;
      }

      isTransitioning = true;
      const parent = fromEl.parentElement || document.getElementById("app-root");
      if (parent && !parent.classList.contains("view-3d-stage")) {
        parent.classList.add("view-3d-stage");
      }

      toEl.style.display = "";

      let outClass = "";
      let inClass = "";

      if (kind === "flip") {
        outClass = "view-3d-flip-out";
        inClass = "view-3d-flip-in";
      } else if (kind === "zoom") {
        outClass = "view-3d-slide-out-" + direction;
        inClass = "view-3d-zoom-in";
      } else {
        // default: slide
        outClass = "view-3d-slide-out-" + direction;
        inClass = "view-3d-slide-in-" + direction;
      }

      fromEl.classList.add(outClass);
      toEl.classList.add(inClass);

      const duration = (kind === "zoom" ? 550 : 450) + 50;
      let cleaned = false;

      function cleanup() {
        if (cleaned) return;
        cleaned = true;
        fromEl.classList.remove(outClass);
        toEl.classList.remove(inClass);
        fromEl.style.display = "none";
        toEl.style.display = "";
        focusHeading(toEl);
        isTransitioning = false;
        resolve();
      }

      // Safety timer fallback to guarantee no lockup
      const timer = setTimeout(cleanup, duration);

      toEl.addEventListener("animationend", function onEnd(e) {
        if (e.target === toEl) {
          toEl.removeEventListener("animationend", onEnd);
          clearTimeout(timer);
          cleanup();
        }
      });
    });
  };

  function focusHeading(container) {
    const heading = container.querySelector("h1, h2, [tabindex]");
    if (heading) {
      if (!heading.hasAttribute("tabindex")) {
        heading.setAttribute("tabindex", "-1");
      }
      heading.focus({ preventScroll: true });
    }
  }
})();
