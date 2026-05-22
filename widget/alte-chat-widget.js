(function () {
  "use strict";

  const STORAGE_KEY = "alteChatWidgetSession";
  const LANG_KEY = "alteChatWidgetLanguage";
  const DEFAULT_CONFIG = {
    apiBaseUrl: "http://127.0.0.1:8000",
    sourceDomain: null,
    defaultLanguage: null,
    proactiveEnabled: false,
    proactiveDelayMs: 30000,
  };

  const TEXT = {
    ka: {
      title: "Alte Assistant",
      greeting: "გამარჯობა, რით დაგეხმაროთ?",
      input: "მოწერეთ კითხვა...",
      send: "გაგზავნა",
      open: "ჩატი",
      close: "დახურვა",
      loading: "წერს...",
      error: "ჩატი დროებით მიუწვდომელია. გთხოვთ სცადოთ მოგვიანებით.",
      consent: "საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის.",
      proactive: "გჭირდებათ დახმარება მიღებასთან დაკავშირებით?",
      handover: "ადამიანთან დაკავშირება",
      quickReplies: ["პროგრამები", "მიღება", "საფასური", "საერთაშორისო სტუდენტები", "ადამიანთან საუბარი"],
    },
    en: {
      title: "Alte Assistant",
      greeting: "Hello, how can I help?",
      input: "Write your question...",
      send: "Send",
      open: "Chat",
      close: "Close",
      loading: "Typing...",
      error: "Chat is temporarily unavailable. Please try again later.",
      consent: "We use your contact details only to provide consultation.",
      proactive: "Need help with admission?",
      handover: "Talk to a person",
      quickReplies: ["Programs", "Admission", "Tuition", "International Students", "Talk to a person"],
    },
  };

  const state = {
    config: normalizeConfig(window.AlteChatWidgetConfig || {}),
    language: "ka",
    isOpen: false,
    isLoading: false,
    session: null,
    messages: [],
    elements: {},
  };

  init();

  function init() {
    state.language = detectLanguage();
    state.session = loadSession();
    state.messages = [{ sender: "bot", text: t("greeting") }];
    injectStyles();
    render();
    bindEvents();
    scheduleProactivePrompt();
  }

  function normalizeConfig(config) {
    const merged = Object.assign({}, DEFAULT_CONFIG, config);
    merged.apiBaseUrl = String(merged.apiBaseUrl || DEFAULT_CONFIG.apiBaseUrl).replace(/\/$/, "");
    merged.sourceDomain = merged.sourceDomain || detectSourceDomain();
    if (!merged.defaultLanguage && merged.sourceDomain === "join.alte.edu.ge") {
      merged.defaultLanguage = "en";
    }
    return merged;
  }

  function detectSourceDomain() {
    const host = window.location.hostname || "";
    return host.includes("join.alte.edu.ge") ? "join.alte.edu.ge" : "alte.edu.ge";
  }

  function detectLanguage() {
    const stored = localStorage.getItem(LANG_KEY);
    if (stored === "ka" || stored === "en") return stored;
    if (state.config.defaultLanguage === "ka" || state.config.defaultLanguage === "en") {
      return state.config.defaultLanguage;
    }
    const browserLang = (navigator.language || "").toLowerCase();
    if (browserLang.startsWith("en")) return "en";
    if (browserLang.startsWith("ka")) return "ka";
    return "ka";
  }

  function t(key) {
    return TEXT[state.language][key];
  }

  function injectStyles() {
    if (document.getElementById("alte-chat-widget-styles")) return;
    const style = document.createElement("style");
    style.id = "alte-chat-widget-styles";
    style.textContent = `
      .alte-chat-root{position:fixed;right:22px;bottom:22px;z-index:2147483000;font-family:Georgia,"Times New Roman",serif;color:#1f2933}
      .alte-chat-button{width:64px;height:64px;border-radius:50%;border:0;background:#7a1f2b;color:#fff;box-shadow:0 14px 32px rgba(31,41,51,.25);cursor:pointer;font-weight:700}
      .alte-chat-panel{position:absolute;right:0;bottom:78px;width:min(372px,calc(100vw - 32px));height:min(580px,calc(100vh - 120px));background:#f7f1e8;border:1px solid #dccfbd;box-shadow:0 22px 70px rgba(31,41,51,.28);display:flex;flex-direction:column;overflow:hidden}
      .alte-chat-hidden{display:none}
      .alte-chat-header{background:#efe4d4;border-bottom:1px solid #dccfbd;padding:14px 14px 12px;display:flex;align-items:center;justify-content:space-between;gap:12px}
      .alte-chat-title{font-size:17px;font-weight:700;color:#301f1d}
      .alte-chat-actions{display:flex;align-items:center;gap:8px}
      .alte-lang-toggle{display:flex;border:1px solid #c8b8a4;background:#fffaf3}
      .alte-lang-toggle button,.alte-chat-close{border:0;background:transparent;cursor:pointer;color:#4a4038;font-family:inherit}
      .alte-lang-toggle button{padding:5px 8px;font-size:12px}
      .alte-lang-toggle button.active{background:#7a1f2b;color:#fff}
      .alte-chat-close{font-size:22px;line-height:1;padding:0 2px}
      .alte-chat-messages{flex:1;overflow:auto;padding:16px;background:linear-gradient(#fbf7f0,#f7f1e8)}
      .alte-chat-message{max-width:84%;margin:0 0 10px;padding:10px 12px;border:1px solid #ded2c2;font-size:14px;line-height:1.42;white-space:pre-wrap}
      .alte-chat-message.bot{background:#fffaf3;margin-right:auto}
      .alte-chat-message.user{background:#7a1f2b;color:#fff;border-color:#7a1f2b;margin-left:auto}
      .alte-chat-quick{display:flex;flex-wrap:wrap;gap:7px;padding:10px 14px;border-top:1px solid #dccfbd;background:#f3eadc}
      .alte-chat-quick button{border:1px solid #c8b8a4;background:#fffaf3;color:#332822;padding:7px 9px;font-family:inherit;font-size:13px;cursor:pointer}
      .alte-chat-consent{padding:9px 14px;color:#6b5f52;font-size:12px;border-top:1px solid #dccfbd;background:#fffaf3}
      .alte-chat-form{display:flex;gap:8px;padding:12px 14px;background:#efe4d4;border-top:1px solid #dccfbd}
      .alte-chat-input{flex:1;min-width:0;border:1px solid #c8b8a4;background:#fffaf3;padding:10px 11px;font-family:inherit;font-size:14px;color:#1f2933}
      .alte-chat-send{border:0;background:#7a1f2b;color:#fff;padding:0 14px;font-family:inherit;font-weight:700;cursor:pointer}
      .alte-chat-send:disabled,.alte-chat-input:disabled{opacity:.6;cursor:not-allowed}
      .alte-proactive{position:absolute;right:0;bottom:78px;max-width:270px;background:#fffaf3;border:1px solid #dccfbd;box-shadow:0 12px 28px rgba(31,41,51,.2);padding:10px 12px;font-size:14px;cursor:pointer}
    `;
    document.head.appendChild(style);
  }

  function render() {
    const root = document.createElement("div");
    root.className = "alte-chat-root";
    root.innerHTML = `
      <div class="alte-proactive alte-chat-hidden" data-role="proactive"></div>
      <section class="alte-chat-panel alte-chat-hidden" data-role="panel" aria-label="Alte chat">
        <header class="alte-chat-header">
          <div class="alte-chat-title">${escapeHtml(t("title"))}</div>
          <div class="alte-chat-actions">
            <div class="alte-lang-toggle" aria-label="Language">
              <button type="button" data-lang="ka">KA</button>
              <button type="button" data-lang="en">EN</button>
            </div>
            <button class="alte-chat-close" type="button" aria-label="${escapeHtml(t("close"))}" data-role="close">×</button>
          </div>
        </header>
        <div class="alte-chat-messages" data-role="messages"></div>
        <div class="alte-chat-quick" data-role="quick"></div>
        <div class="alte-chat-consent" data-role="consent"></div>
        <form class="alte-chat-form" data-role="form">
          <input class="alte-chat-input" data-role="input" autocomplete="off" />
          <button class="alte-chat-send" type="submit" data-role="send"></button>
        </form>
      </section>
      <button class="alte-chat-button" type="button" data-role="button">${escapeHtml(t("open"))}</button>
    `;
    document.body.appendChild(root);
    state.elements = {
      root,
      panel: root.querySelector('[data-role="panel"]'),
      button: root.querySelector('[data-role="button"]'),
      close: root.querySelector('[data-role="close"]'),
      form: root.querySelector('[data-role="form"]'),
      input: root.querySelector('[data-role="input"]'),
      send: root.querySelector('[data-role="send"]'),
      messages: root.querySelector('[data-role="messages"]'),
      quick: root.querySelector('[data-role="quick"]'),
      consent: root.querySelector('[data-role="consent"]'),
      proactive: root.querySelector('[data-role="proactive"]'),
      langButtons: root.querySelectorAll("[data-lang]"),
    };
    refreshText();
  }

  function bindEvents() {
    state.elements.button.addEventListener("click", togglePanel);
    state.elements.close.addEventListener("click", closePanel);
    state.elements.form.addEventListener("submit", function (event) {
      event.preventDefault();
      sendCurrentInput();
    });
    state.elements.langButtons.forEach((button) => {
      button.addEventListener("click", function () {
        setLanguage(button.getAttribute("data-lang"));
      });
    });
    state.elements.proactive.addEventListener("click", openPanel);
  }

  function refreshText() {
    state.elements.input.placeholder = t("input");
    state.elements.send.textContent = t("send");
    state.elements.consent.textContent = t("consent");
    state.elements.button.textContent = t("open");
    state.elements.proactive.textContent = t("proactive");
    state.elements.langButtons.forEach((button) => {
      button.classList.toggle("active", button.getAttribute("data-lang") === state.language);
    });
    renderQuickReplies();
    renderMessages();
  }

  function renderQuickReplies() {
    state.elements.quick.innerHTML = "";
    t("quickReplies").forEach((label) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.addEventListener("click", () => sendMessage(label));
      state.elements.quick.appendChild(button);
    });
  }

  function renderMessages() {
    state.elements.messages.innerHTML = "";
    state.messages.forEach((message) => {
      const node = document.createElement("div");
      node.className = `alte-chat-message ${message.sender}`;
      node.textContent = message.text;
      state.elements.messages.appendChild(node);
    });
    if (state.isLoading) {
      const loading = document.createElement("div");
      loading.className = "alte-chat-message bot";
      loading.textContent = t("loading");
      state.elements.messages.appendChild(loading);
    }
    state.elements.messages.scrollTop = state.elements.messages.scrollHeight;
    state.elements.input.disabled = state.isLoading;
    state.elements.send.disabled = state.isLoading;
  }

  function togglePanel() {
    state.isOpen ? closePanel() : openPanel();
  }

  function openPanel() {
    state.isOpen = true;
    state.elements.panel.classList.remove("alte-chat-hidden");
    state.elements.proactive.classList.add("alte-chat-hidden");
    ensureSession();
    setTimeout(() => state.elements.input.focus(), 0);
  }

  function closePanel() {
    state.isOpen = false;
    state.elements.panel.classList.add("alte-chat-hidden");
  }

  function setLanguage(language) {
    if (language !== "ka" && language !== "en") return;
    state.language = language;
    localStorage.setItem(LANG_KEY, language);
    state.messages = [{ sender: "bot", text: t("greeting") }].concat(state.messages.filter((item, index) => index > 0));
    refreshText();
  }

  function sendCurrentInput() {
    const value = state.elements.input.value.trim();
    if (!value) return;
    state.elements.input.value = "";
    sendMessage(value);
  }

  async function ensureSession() {
    if (state.session && state.session.conversation_id) return state.session;
    try {
      const response = await postJson("/chat/session/start", {
        channel: "website_chat",
        source_domain: state.config.sourceDomain,
        language: state.language,
      });
      state.session = {
        conversation_id: response.conversation_id,
        session_id: response.session_id,
        source_domain: response.source_domain || state.config.sourceDomain,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.session));
      return state.session;
    } catch (error) {
      appendBotError();
      throw error;
    }
  }

  async function sendMessage(text) {
    if (state.isLoading) return;
    state.messages.push({ sender: "user", text });
    state.isLoading = true;
    renderMessages();
    try {
      const session = await ensureSession();
      const response = await postJson("/chat/message", {
        conversation_id: session.conversation_id,
        session_id: session.session_id,
        message: text,
        source_domain: state.config.sourceDomain,
        language: state.language,
      });
      state.messages.push({ sender: "bot", text: response.reply || t("error") });
    } catch (error) {
      appendBotError();
    } finally {
      state.isLoading = false;
      renderMessages();
    }
  }

  async function postJson(path, payload) {
    const response = await fetch(`${state.config.apiBaseUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  }

  function appendBotError() {
    state.messages.push({ sender: "bot", text: t("error") });
  }

  function loadSession() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (parsed && parsed.conversation_id) return parsed;
    } catch (error) {
      localStorage.removeItem(STORAGE_KEY);
    }
    return null;
  }

  function scheduleProactivePrompt() {
    if (!state.config.proactiveEnabled) return;
    window.setTimeout(() => {
      if (!state.isOpen) {
        state.elements.proactive.textContent = t("proactive");
        state.elements.proactive.classList.remove("alte-chat-hidden");
      }
    }, Number(state.config.proactiveDelayMs) || 30000);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
})();
