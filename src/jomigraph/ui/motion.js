/**
 * JomiGraph AI — Motion & Accessibility Controller (Phase 14)
 * ==========================================================
 * Manages accessibility settings, user animation preferences,
 * ARIA announcements, and keyboard skip-link handling.
 */
(function () {
  "use strict";

  const STORAGE_KEY = "jg_reduce_motion";

  function getLang() {
    return (typeof currentLang !== "undefined" && currentLang) ? currentLang : "bn";
  }

  function isReducedMotion() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored !== null) return stored === "true";
    } catch (e) {}
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function setReducedMotion(enable) {
    try {
      localStorage.setItem(STORAGE_KEY, enable ? "true" : "false");
    } catch (e) {}
    document.body.classList.toggle("reduce-motion", enable);
    updateButtonText();
    announceStatus(enable);
  }

  function announceStatus(enable) {
    const live = document.getElementById("a11y-status");
    if (!live) return;
    const lang = getLang();
    if (lang === "bn") {
      live.textContent = enable ? "অ্যানিমেশন বা গতিবিধি বন্ধ করা হয়েছে।" : "অ্যানিমেশন বা গতিবিধি চালু করা হয়েছে।";
    } else {
      live.textContent = enable ? "Motion animations disabled." : "Motion animations enabled.";
    }
  }

  function updateButtonText() {
    const btn = document.getElementById("motion-toggle-btn");
    if (!btn) return;
    const isReduced = document.body.classList.contains("reduce-motion");
    btn.setAttribute("aria-pressed", isReduced ? "true" : "false");
    const lang = getLang();
    if (lang === "bn") {
      btn.textContent = isReduced ? "গতিবিধি: বন্ধ (Animations: Off)" : "গতিবিধি: চালু (Animations: On)";
    } else {
      btn.textContent = isReduced ? "Animations: Off" : "Animations: On";
    }
  }

  function initMotion() {
    // Apply initial state
    if (isReducedMotion()) {
      document.body.classList.add("reduce-motion");
    }
    updateButtonText();

    const btn = document.getElementById("motion-toggle-btn");
    if (btn) {
      btn.addEventListener("click", function () {
        const currentlyReduced = document.body.classList.contains("reduce-motion");
        setReducedMotion(!currentlyReduced);
      });
    }

    // Skip link focus handler
    const skipLink = document.getElementById("skip-link");
    if (skipLink) {
      skipLink.addEventListener("click", function () {
        const target = document.getElementById("app-root");
        if (target) {
          target.setAttribute("tabindex", "-1");
          target.focus();
        }
      });
    }

    window.addEventListener("hashchange", updateButtonText);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMotion);
  } else {
    initMotion();
  }
})();
