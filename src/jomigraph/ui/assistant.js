/**
 * JomiGraph AI — Offline Rule-Based Assistant UI Component (Phase 13)
 * ===================================================================
 * 100% Client-side coordination with POST /assistant endpoint.
 * Zero external calls, zero LLMs, zero tracking.
 */
(function () {
  "use strict";

  const STRINGS = {
    bn: {
      btn_label: "সহায়ক",
      panel_title: "জমিগ্রাফ সহায়ক",
      close_btn: "বন্ধ করুন",
      input_placeholder: "প্রশ্ন লিখুন (যেমন: আর১ নিয়ম কী?)...",
      send_btn: "পাঠান",
      footer_notice: "নিয়মভিত্তিক সহায়ক। কোনো এআই মডেল ফলাফল নির্ধারণ করে না।",
      welcome_msg: "নমস্কার/সালাম! আমি জমিগ্রাফ সহকারী। জমির রেকর্ড ধারাবাহিকতা, ফলাফল বা নিয়ম বুঝতে আপনাকে সাহায্য করতে পারি।",
      sugg_red: "লাল দাগ কেন?",
      sugg_lab: "সিমুলেশন ল্যাব কী?",
      sugg_rules: "নিয়মগুলো কী কী?",
      status_contradiction: "অসঙ্গতি পাওয়া গেছে",
      status_review: "পর্যালোচনা প্রয়োজন",
      status_consistent: "সঙ্গতিপূর্ণ"
    },
    en: {
      btn_label: "Assistant",
      panel_title: "JomiGraph Assistant",
      close_btn: "Close",
      input_placeholder: "Ask a question (e.g. What is R1?)...",
      send_btn: "Send",
      footer_notice: "Rule-based assistant. No AI model is used to decide results.",
      welcome_msg: "Hello! I am the JomiGraph assistant. I can help explain land record consistency, rules, and results.",
      sugg_red: "Why Red Status?",
      sugg_lab: "What is Simulation Lab?",
      sugg_rules: "Explain Rules",
      status_contradiction: "Contradiction Found",
      status_review: "Review Required",
      status_consistent: "Consistent"
    }
  };

  function getLang() {
    return (typeof currentLang !== "undefined" && currentLang) ? currentLang : "bn";
  }

  function getRole() {
    return (typeof currentRole !== "undefined" && currentRole) ? currentRole : "citizen";
  }

  function getActiveParcelId() {
    const hash = window.location.hash || "";
    if (hash.startsWith("#/parcel/")) {
      return decodeURIComponent(hash.replace("#/parcel/", "").split("#")[0].split("?")[0]);
    }
    return null;
  }

  let fab = null;
  let panel = null;
  let isOpen = false;

  function initAssistant() {
    if (document.getElementById("jg-assistant-fab")) return;

    // 1. Create Floating Action Button
    fab = document.createElement("button");
    fab.id = "jg-assistant-fab";
    fab.className = "assistant-fab interactive-lift";
    fab.type = "button";
    fab.setAttribute("aria-label", "Open land record assistant");
    fab.innerHTML = `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2C6.48 2 2 6.48 2 12c0 1.85.5 3.58 1.38 5.08L2 22l5.09-1.35C8.54 21.48 10.22 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.61 0-3.1-.47-4.36-1.28l-.31-.2-3.04.81.82-2.96-.2-.33A7.94 7.94 0 0 1 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8zm-1-5h2v2h-2zm0-8h2v6h-2z"/>
      </svg>
      <span id="jg-assistant-fab-text">${STRINGS[getLang()].btn_label}</span>
    `;
    document.body.appendChild(fab);

    // 2. Create Chat Panel
    panel = document.createElement("div");
    panel.id = "jg-assistant-panel";
    panel.className = "assistant-panel";
    panel.style.display = "none";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Assistant dialogue panel");

    panel.innerHTML = `
      <div class="assistant-header">
        <h2 class="assistant-header-title">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="#15803d" aria-hidden="true">
            <path d="M12 2C6.48 2 2 6.48 2 12c0 1.85.5 3.58 1.38 5.08L2 22l5.09-1.35C8.54 21.48 10.22 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.61 0-3.1-.47-4.36-1.28l-.31-.2-3.04.81.82-2.96-.2-.33A7.94 7.94 0 0 1 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8zm-1-5h2v2h-2zm0-8h2v6h-2z"/>
          </svg>
          <span id="jg-assistant-title">${STRINGS[getLang()].panel_title}</span>
        </h2>
        <button id="jg-assistant-close" class="assistant-close-btn" type="button" aria-label="Close assistant">✕</button>
      </div>
      <div class="assistant-messages" id="jg-assistant-messages" role="log" aria-live="polite"></div>
      <form class="assistant-input-area" id="jg-assistant-form">
        <input type="text" id="jg-assistant-input" maxlength="300" autocomplete="off" placeholder="${STRINGS[getLang()].input_placeholder}" aria-label="Message input">
        <button type="submit" class="assistant-send-btn" id="jg-assistant-send">${STRINGS[getLang()].send_btn}</button>
      </form>
      <div class="assistant-footer-notice" id="jg-assistant-footer">
        ${STRINGS[getLang()].footer_notice}
      </div>
    `;
    document.body.appendChild(panel);

    // Event listeners
    fab.addEventListener("click", toggleAssistant);
    document.getElementById("jg-assistant-close").addEventListener("click", closeAssistant);

    const form = document.getElementById("jg-assistant-form");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const input = document.getElementById("jg-assistant-input");
      const text = input.value.trim();
      if (!text) return;
      input.value = "";
      handleUserQuery(text);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen) {
        closeAssistant();
      }
    });

    // Update fab label when language changes
    window.addEventListener("hashchange", updateAssistantContext);
  }

  function updateAssistantContext() {
    const s = STRINGS[getLang()] || STRINGS.bn;
    const fabText = document.getElementById("jg-assistant-fab-text");
    if (fabText) fabText.textContent = s.btn_label;
    const title = document.getElementById("jg-assistant-title");
    if (title) title.textContent = s.panel_title;
    const input = document.getElementById("jg-assistant-input");
    if (input) input.placeholder = s.input_placeholder;
    const send = document.getElementById("jg-assistant-send");
    if (send) send.textContent = s.send_btn;
    const footer = document.getElementById("jg-assistant-footer");
    if (footer) footer.textContent = s.footer_notice;
  }

  function toggleAssistant() {
    if (isOpen) {
      closeAssistant();
    } else {
      openAssistant();
    }
  }

  function openAssistant() {
    isOpen = true;
    updateAssistantContext();
    panel.style.display = "flex";
    fab.style.display = "none";
    const input = document.getElementById("jg-assistant-input");
    if (input) input.focus();

    const msgList = document.getElementById("jg-assistant-messages");
    if (msgList && msgList.children.length === 0) {
      // Add initial greeting
      const s = STRINGS[getLang()];
      addBotMessage({
        answer: s.welcome_msg,
        suggestions: [
          { label: s.sugg_red, action: "query:" + s.sugg_red },
          { label: s.sugg_lab, action: "query:" + s.sugg_lab },
          { label: s.sugg_rules, action: "query:" + s.sugg_rules }
        ]
      });
    }
  }

  function closeAssistant() {
    isOpen = false;
    panel.style.display = "none";
    fab.style.display = "flex";
    fab.focus();
  }

  function addUserMessage(text) {
    const list = document.getElementById("jg-assistant-messages");
    const msg = document.createElement("div");
    msg.className = "assistant-msg user motion-fade-slide";
    msg.textContent = text;
    list.appendChild(msg);
    list.scrollTop = list.scrollHeight;
  }

  function addBotMessage(data) {
    const list = document.getElementById("jg-assistant-messages");
    const msg = document.createElement("div");
    msg.className = "assistant-msg bot motion-fade-slide";

    // Optional status pill
    if (data.status) {
      const pill = document.createElement("span");
      pill.className = "assistant-status-pill " + data.status;
      const s = STRINGS[getLang()] || STRINGS.bn;
      const statusKey = "status_" + data.status.toLowerCase();
      pill.textContent = s[statusKey] || data.status;
      msg.appendChild(pill);
    }

    // Answer text
    const textNode = document.createElement("div");
    textNode.textContent = data.answer || "";
    msg.appendChild(textNode);

    // Suggestion chips
    if (data.suggestions && data.suggestions.length) {
      const chipContainer = document.createElement("div");
      chipContainer.className = "assistant-chips";

      data.suggestions.forEach(function (sugg) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "assistant-chip";
        chip.textContent = sugg.label;

        chip.addEventListener("click", function () {
          if (sugg.action.startsWith("nav:")) {
            const targetHash = sugg.action.replace("nav:", "");
            window.location.hash = targetHash;
            if (window.innerWidth <= 560) closeAssistant();
          } else if (sugg.action.startsWith("query:")) {
            const query = sugg.action.replace("query:", "");
            handleUserQuery(query);
          }
        });

        chipContainer.appendChild(chip);
      });

      msg.appendChild(chipContainer);
    }

    list.appendChild(msg);
    list.scrollTop = list.scrollHeight;
  }

  async function handleUserQuery(text) {
    addUserMessage(text);

    const list = document.getElementById("jg-assistant-messages");
    const typing = document.createElement("div");
    typing.className = "assistant-typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    list.appendChild(typing);
    list.scrollTop = list.scrollHeight;

    const reducedMotion = document.body.classList.contains("reduce-motion") ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const delay = reducedMotion ? 10 : 380;

    try {
      const lang = getLang();
      const role = getRole();
      const parcelId = getActiveParcelId();

      const response = await fetch(`/assistant?lang=${encodeURIComponent(lang)}&role=${encodeURIComponent(role)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text, parcel_id: parcelId })
      });

      if (!response.ok) throw new Error("Server status " + response.status);
      const data = await response.json();

      setTimeout(function () {
        if (typing.parentNode) typing.remove();
        addBotMessage(data);
      }, delay);
    } catch (err) {
      setTimeout(function () {
        if (typing.parentNode) typing.remove();
        addBotMessage({
          answer: getLang() === "bn"
            ? "সার্ভারের সাথে যোগাযোগ করা যায়নি। অনুগ্রহ করে সংযোগ দেখে পুনরায় চেষ্টা করুন।"
            : "Could not communicate with the server. Please check connection and try again.",
          suggestions: []
        });
      }, delay);
    }
  }

  // Auto initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAssistant);
  } else {
    initAssistant();
  }
})();
