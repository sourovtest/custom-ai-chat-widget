(() => {
  const hostId = "site-chatbot-widget";
  if (document.getElementById(hostId)) return;

  const script = document.currentScript;
  const globalConfig = window.ChatbotConfig && typeof window.ChatbotConfig === "object"
    ? window.ChatbotConfig
    : {};
  const configuredValue = (key, dataKey, fallback) => {
    const value = globalConfig[key] ?? script?.dataset[dataKey];
    return typeof value === "string" && value.trim() ? value.trim() : fallback;
  };
  let scriptOrigin = window.location.origin;
  try {
    if (script?.src) scriptOrigin = new URL(script.src, window.location.href).origin;
  } catch {
    scriptOrigin = window.location.origin;
  }
  const configuredApiUrl = configuredValue("apiUrl", "apiUrl", scriptOrigin);
  const brandName = configuredValue("brandName", "brandName", "Support").slice(0, 80);
  const welcomeMessage = configuredValue(
    "welcomeMessage",
    "welcomeMessage",
    `Welcome to ${brandName}. How can we help you today?`,
  ).slice(0, 500);
  const defaultRoleCandidate = configuredValue("defaultRole", "defaultRole", "support").toLowerCase();
  const defaultRole = new Set(["sales", "support", "faq", "vendor"]).has(defaultRoleCandidate)
    ? defaultRoleCandidate
    : "support";
  const defaultPrimaryColor = "#174b3e";
  const primaryColorCandidate = configuredValue("primaryColor", "primaryColor", defaultPrimaryColor);
  const colorProbe = document.createElement("span");
  colorProbe.style.color = primaryColorCandidate;
  const primaryColor = colorProbe.style.color ? primaryColorCandidate : defaultPrimaryColor;
  let apiBaseUrl = null;

  if (configuredApiUrl) {
    try {
      apiBaseUrl = new URL(configuredApiUrl, window.location.href).href.replace(/\/$/, "");
    } catch {
      apiBaseUrl = null;
    }
  }

  const host = document.createElement("div");
  host.id = hostId;
  host.setAttribute("data-chatbot-widget", "");
  const shadow = host.attachShadow({ mode: "open" });

  shadow.innerHTML = `
    <style>
      :host {
        all: initial;
        --cb-primary: #174b3e;
        color: #20372f;
        font-family: "Noto Sans Bengali", "Hind Siliguri", "Nirmala UI", "Segoe UI", sans-serif;
        font-synthesis: none;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        position: fixed;
        right: 0;
        bottom: 0;
        width: 0;
        height: 0;
        z-index: 2147483000;
      }

      *, *::before, *::after { box-sizing: border-box; }
      button, input { font: inherit; }
      button { -webkit-tap-highlight-color: transparent; }
      [hidden] { display: none !important; }

      .launcher {
        position: fixed;
        right: 22px;
        bottom: 22px;
        display: inline-flex;
        align-items: center;
        gap: 11px;
        min-height: 60px;
        padding: 8px 19px 8px 9px;
        border: 1px solid rgba(255,255,255,.24);
        border-radius: 999px;
        color: #fffdf6;
        background: var(--cb-primary);
        box-shadow: 0 9px 28px rgba(20, 54, 43, .23), 0 2px 6px rgba(20, 54, 43, .14);
        cursor: pointer;
        font-size: 15px;
        font-weight: 700;
        transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
      }

      .launcher:hover {
        background: var(--cb-primary);
        box-shadow: 0 12px 30px rgba(20, 54, 43, .28);
        filter: brightness(.9);
        transform: translateY(-2px);
      }

      .launcher:focus-visible, .close:focus-visible, .suggestion:focus-visible,
      .send:focus-visible, .message-input:focus-visible {
        outline: 3px solid #e8ad47;
        outline-offset: 3px;
      }

      .brand-mark {
        display: grid;
        place-items: center;
        flex: 0 0 42px;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        color: var(--cb-primary);
        background: #f0c66f;
      }

      .launcher svg { width: 22px; height: 22px; }

      .panel {
        position: fixed;
        right: 22px;
        bottom: 96px;
        display: flex;
        flex-direction: column;
        width: min(386px, calc(100vw - 32px));
        height: min(620px, calc(100dvh - 122px));
        min-height: 390px;
        overflow: hidden;
        border: 1px solid #dfe5dc;
        border-radius: 22px;
        background: #fffdf8;
        box-shadow: 0 24px 70px rgba(25, 50, 39, .24), 0 4px 14px rgba(25, 50, 39, .1);
        transform-origin: bottom right;
        animation: arrive 180ms ease-out;
      }

      @keyframes arrive {
        from { opacity: 0; transform: translateY(8px) scale(.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
      }

      .topbar {
        position: relative;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 18px 17px 17px;
        color: #fffdf6;
        background: var(--cb-primary);
      }

      .topbar::after {
        content: "";
        position: absolute;
        right: 62px;
        top: -25px;
        width: 100px;
        height: 100px;
        border: 1px solid rgba(242, 205, 132, .18);
        border-radius: 50%;
        pointer-events: none;
      }

      .seal {
        display: grid;
        place-items: center;
        flex: 0 0 46px;
        width: 46px;
        height: 46px;
        border: 1px solid rgba(255,255,255,.32);
        border-radius: 15px;
        color: var(--cb-primary);
        background: #f0c66f;
        font-family: Georgia, serif;
        font-size: 21px;
        font-weight: 700;
        transform: rotate(-3deg);
      }

      .identity { min-width: 0; flex: 1; }
      .identity h2 {
        margin: 0;
        font-size: 18px;
        line-height: 1.25;
        font-weight: 750;
        letter-spacing: .1px;
      }

      .identity p {
        margin: 4px 0 0;
        color: #d3e2d9;
        font-size: 12px;
        line-height: 1.4;
      }

      .close {
        display: grid;
        place-items: center;
        flex: 0 0 36px;
        width: 36px;
        height: 36px;
        border: 1px solid rgba(255,255,255,.24);
        border-radius: 50%;
        color: #fffdf6;
        background: transparent;
        cursor: pointer;
        transition: background 150ms ease;
      }

      .close:hover { background: rgba(255,255,255,.12); }
      .close svg { width: 17px; height: 17px; }

      .connection {
        display: flex;
        align-items: center;
        gap: 8px;
        min-height: 38px;
        padding: 8px 18px;
        border-bottom: 1px solid #e7e9e1;
        color: #5d7065;
        background: #f5f4ec;
        font-size: 12px;
      }

      .connection-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #9caa9e;
        box-shadow: 0 0 0 3px rgba(156,170,158,.18);
      }

      .connection[data-state="online"] .connection-dot {
        background: #34855b;
        box-shadow: 0 0 0 3px rgba(52,133,91,.16);
      }

      .connection[data-state="offline"] .connection-dot {
        background: #bc654b;
        box-shadow: 0 0 0 3px rgba(188,101,75,.16);
      }

      .messages {
        display: flex;
        flex: 1;
        flex-direction: column;
        gap: 14px;
        overflow-y: auto;
        padding: 19px 16px 14px;
        overscroll-behavior: contain;
        background-color: #fffdf8;
        background-image: radial-gradient(#e8e4d8 0.65px, transparent 0.65px);
        background-size: 15px 15px;
        scrollbar-color: #c9d2c8 transparent;
        scrollbar-width: thin;
      }

      .day-label {
        align-self: center;
        padding: 5px 10px;
        border: 1px solid #e7e3d8;
        border-radius: 999px;
        color: #7a8178;
        background: #fffdf8;
        font-size: 10px;
      }

      .message {
        display: flex;
        flex-direction: column;
        gap: 5px;
        max-width: 86%;
      }

      .message--assistant { align-self: flex-start; }
      .message--user { align-self: flex-end; align-items: flex-end; }

      .bubble {
        padding: 11px 13px;
        border: 1px solid #e2e5dc;
        border-radius: 15px 15px 15px 4px;
        color: #284238;
        background: #fff;
        font-size: 14px;
        line-height: 1.58;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
      }

      .message--user .bubble {
        border-color: var(--cb-primary);
        border-radius: 15px 15px 4px 15px;
        color: #fffdf6;
        background: var(--cb-primary);
      }

      .time {
        padding: 0 4px;
        color: #849087;
        font-size: 10px;
        line-height: 1.2;
      }

      .suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        padding: 0 16px 12px;
        background: #fffdf8;
      }

      .suggestion {
        padding: 7px 10px;
        border: 1px solid #d9e2d7;
        border-radius: 999px;
        color: #285447;
        background: #f7faf4;
        cursor: pointer;
        font-size: 11px;
        transition: border-color 150ms ease, background 150ms ease;
      }

      .suggestion:hover {
        border-color: #9bb9a4;
        background: #edf4e9;
      }

      .composer {
        display: flex;
        align-items: flex-end;
        gap: 9px;
        padding: 12px;
        border-top: 1px solid #e7e9e1;
        background: #fffdf8;
      }

      .message-input {
        width: 100%;
        min-width: 0;
        height: 44px;
        padding: 11px 13px;
        border: 1px solid #d8ded5;
        border-radius: 13px;
        color: #20372f;
        background: #fff;
        font-size: 14px;
        outline: none;
        transition: border-color 150ms ease, box-shadow 150ms ease;
      }

      .message-input::placeholder { color: #89938b; }
      .message-input:focus {
        border-color: #4c8069;
        box-shadow: 0 0 0 3px rgba(76,128,105,.13);
      }

      .send {
        display: grid;
        place-items: center;
        flex: 0 0 44px;
        width: 44px;
        height: 44px;
        border: 0;
        border-radius: 14px;
        color: #fffdf6;
        background: #d79132;
        cursor: pointer;
        transition: transform 150ms ease, background 150ms ease;
      }

      .send:hover:not(:disabled) {
        background: #bd7624;
        transform: translateY(-1px);
      }

      .send:disabled { cursor: not-allowed; opacity: .58; }
      .send svg { width: 19px; height: 19px; }

      .send-spinner {
        width: 18px;
        height: 18px;
        border: 2px solid rgba(255,255,255,.45);
        border-top-color: #fff;
        border-radius: 50%;
        animation: spin 650ms linear infinite;
      }

      @keyframes spin { to { transform: rotate(360deg); } }
      .footnote {
        padding: 0 14px 12px;
        color: #8a9289;
        background: #fffdf8;
        text-align: center;
        font-size: 10px;
        line-height: 1.4;
      }

      @media (max-width: 480px) {
        .launcher { right: 15px; bottom: 15px; }
        .panel {
          inset: 10px 10px 86px;
          width: auto;
          height: auto;
          min-height: 0;
          border-radius: 20px;
          transform-origin: bottom center;
        }
      }

      @media (max-height: 520px) and (min-width: 481px) {
        .panel { height: calc(100dvh - 105px); min-height: 0; }
      }

      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
          animation-duration: .01ms !important;
          animation-iteration-count: 1 !important;
          scroll-behavior: auto !important;
          transition-duration: .01ms !important;
        }
      }
    </style>

    <button class="launcher" type="button" aria-label="Open chat" aria-controls="chatbot-chat-panel" aria-expanded="false">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M5 6.75A2.75 2.75 0 0 1 7.75 4h8.5A2.75 2.75 0 0 1 19 6.75v6.5A2.75 2.75 0 0 1 16.25 16H11l-4.5 3v-3.3A2.75 2.75 0 0 1 5 13.25v-6.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M8.5 8.5h7M8.5 12h4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </span>
      <span>সাহায্য লাগবে?</span>
    </button>

    <section class="panel" id="chatbot-chat-panel" role="dialog" aria-modal="false" aria-labelledby="chatbot-chat-title" hidden>
      <header class="topbar">
        <span class="seal" aria-hidden="true">ব</span>
        <div class="identity">
          <h2 id="chatbot-chat-title">Support</h2>
          <p>ক্রেতা ও বিক্রেতা সহায়তা</p>
        </div>
        <button class="close" type="button" aria-label="চ্যাট বন্ধ করুন">
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m5 5 10 10M15 5 5 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </button>
      </header>
      <div class="connection" data-state="checking" role="status" aria-live="polite">
        <span class="connection-dot" aria-hidden="true"></span>
        <span class="connection-label">চ্যাট সংযোগ পরীক্ষা হচ্ছে…</span>
      </div>
      <div class="messages" role="log" aria-label="চ্যাট বার্তা" aria-live="polite" aria-relevant="additions">
        <span class="day-label">আজ</span>
        <article class="message message--assistant">
          <div class="bubble"></div>
          <time class="time"></time>
        </article>
      </div>
      <div class="suggestions" aria-label="দ্রুত প্রশ্ন">
        <button class="suggestion" type="button" data-prompt="আমার অর্ডারটি কীভাবে ট্র্যাক করব?">অর্ডার ট্র্যাকিং</button>
        <button class="suggestion" type="button" data-prompt="একটি পণ্য সম্পর্কে জানতে চাই">পণ্য সম্পর্কে</button>
      </div>
      <form class="composer">
        <label class="sr-only" for="chatbot-message-input">আপনার বার্তা</label>
        <input class="message-input" id="chatbot-message-input" name="message" type="text" maxlength="1000" autocomplete="off" placeholder="আপনার প্রশ্ন লিখুন…" required>
        <button class="send" type="submit" aria-label="বার্তা পাঠান">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="m4 5 16 7-16 7 2.6-7L4 5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
            <path d="M6.6 12H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </button>
      </form>
      <p class="footnote">ব্যক্তিগত তথ্য বা পাসওয়ার্ড এখানে লিখবেন না।</p>
    </section>
  `;

  const style = shadow.querySelector("style");
  style.textContent += "\n.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }\n";

  document.body.append(host);
  host.style.setProperty("--cb-primary", primaryColor);

  const launcher = shadow.querySelector(".launcher");
  const panel = shadow.querySelector(".panel");
  const closeButton = shadow.querySelector(".close");
  const messages = shadow.querySelector(".messages");
  const form = shadow.querySelector(".composer");
  const input = shadow.querySelector(".message-input");
  const sendButton = shadow.querySelector(".send");
  const connection = shadow.querySelector(".connection");
  const connectionLabel = shadow.querySelector(".connection-label");
  const sendIcon = sendButton.innerHTML;
  const title = shadow.querySelector("#chatbot-chat-title");
  const welcomeBubble = shadow.querySelector(".message--assistant .bubble");
  title.textContent = brandName;
  welcomeBubble.textContent = welcomeMessage;
  launcher.setAttribute("aria-label", `${brandName} chat খুলুন`);
  const storageNamespace = brandName.toLowerCase().replace(/[^a-z0-9]+/g, "-") || "support";
  const sessionStorageKey = `${storageNamespace}.chat.session.v1`;
  const sessionCreatedAtKey = `${storageNamespace}.chat.session.created.v1`;
  const sessionLifetimeMs = 30 * 24 * 60 * 60 * 1000;
  const processedRulesKey = `${storageNamespace}.chat.processed-rules.v1`;
  const sessionId = getSessionId();
  let requestInFlight = false;
  let personaRole = null;

  function getSessionId() {
    let storedId = null;
    let createdAt = null;
    try {
      storedId = window.localStorage.getItem(sessionStorageKey);
      createdAt = window.localStorage.getItem(sessionCreatedAtKey);
    } catch {
      setConnection("এই ব্রাউজারে সেশন সংরক্ষণ করা যাচ্ছে না।", "offline");
    }

    if (storedId && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(storedId)) {
      const now = Date.now();
      const parsedCreatedAt = Number(createdAt);
      const hasValidCreatedAt = Number.isSafeInteger(parsedCreatedAt)
        && parsedCreatedAt > 0
        && parsedCreatedAt <= now;

      if (hasValidCreatedAt && now - parsedCreatedAt > sessionLifetimeMs) {
        try {
          window.localStorage.removeItem(sessionStorageKey);
          window.localStorage.removeItem(sessionCreatedAtKey);
        } catch {
          setConnection("এই ব্রাউজারে পুরনো সেশন মুছে ফেলা যায়নি।", "offline");
        }
        storedId = null;
      } else if (!hasValidCreatedAt) {
        try {
          window.localStorage.setItem(sessionCreatedAtKey, String(now));
        } catch {
          setConnection("এই ব্রাউজারে সেশন সংরক্ষণ করা যাচ্ছে না।", "offline");
        }
        return storedId;
      } else {
        return storedId;
      }
    }

    if (storedId) {
      try {
        window.localStorage.removeItem(sessionStorageKey);
        window.localStorage.removeItem(sessionCreatedAtKey);
      } catch {
        setConnection("এই ব্রাউজারে সেশন সংরক্ষণ করা যাচ্ছে না।", "offline");
      }
      storedId = null;
    }

    if (!window.crypto?.getRandomValues) {
      return storedId;
    }

    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const generatedId = [...bytes].map((byte, index) => {
      const hex = byte.toString(16).padStart(2, "0");
      return [4, 6, 8, 10].includes(index) ? `-${hex}` : hex;
    }).join("");

    try {
      window.localStorage.setItem(sessionStorageKey, generatedId);
      window.localStorage.setItem(sessionCreatedAtKey, String(Date.now()));
    } catch {
      setConnection("এই ব্রাউজারে সেশন সংরক্ষণ করা যাচ্ছে না।", "offline");
    }
    return generatedId;
  }

  function setConnection(message, state) {
    connection.dataset.state = state;
    connectionLabel.textContent = message;
  }

  function addMessage(text, sender) {
    const article = document.createElement("article");
    article.className = `message message--${sender}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    const time = document.createElement("time");
    time.className = "time";
    time.dateTime = new Date().toISOString();
    time.textContent = new Intl.DateTimeFormat("bn-BD", {
      hour: "numeric",
      minute: "2-digit",
    }).format(new Date());

    article.append(bubble, time);
    messages.append(article);
    messages.scrollTop = messages.scrollHeight;
  }

  async function fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  async function checkConnection() {
    if (!apiBaseUrl) {
      setConnection("চ্যাট সার্ভার এখনো কনফিগার করা হয়নি।", "offline");
      return;
    }
    if (!navigator.onLine) {
      setConnection("ইন্টারনেট সংযোগ নেই। আবার চেষ্টা করুন।", "offline");
      return;
    }

    try {
      const response = await fetchWithTimeout(`${apiBaseUrl}/health`, { method: "GET" }, 4000);
      if (!response.ok) throw new Error("Health check failed");
      setConnection("সহায়তা সার্ভারে সংযোগ আছে", "online");
    } catch {
      setConnection("এখন সংযোগ পাওয়া যাচ্ছে না। পরে আবার চেষ্টা করুন।", "offline");
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const text = input.value.trim();
    if (!text || requestInFlight) return;

    if (!apiBaseUrl || !sessionId) {
      setConnection(!sessionId ? "সেশন তৈরি করা যায়নি। পেজটি আবার খুলুন।" : "চ্যাট সার্ভার এখনো কনফিগার করা হয়নি।", "offline");
      return;
    }
    if (!navigator.onLine) {
      setConnection("ইন্টারনেট সংযোগ নেই। বার্তাটি আবার পাঠান।", "offline");
      return;
    }

    addMessage(text, "user");
    input.value = "";
    requestInFlight = true;
    sendButton.disabled = true;
    sendButton.setAttribute("aria-label", "বার্তা পাঠানো হচ্ছে");
    sendButton.setAttribute("aria-busy", "true");
    sendButton.innerHTML = '<span class="send-spinner" aria-hidden="true"></span>';
    setConnection("বার্তা পাঠানো হচ্ছে…", "checking");

    try {
      const response = await fetchWithTimeout(`${apiBaseUrl}/api/chat/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_token: sessionId,
          message: text,
          page_path: personaRole
            ? `${window.location.pathname}?persona_role=${encodeURIComponent(personaRole)}`
            : window.location.pathname,
          default_role: personaRole || defaultRole,
        }),
      });

      if (!response.ok) throw new Error(`Chat request failed: ${response.status}`);
      const result = await response.json();
      if (typeof result.reply !== "string" || !result.reply.trim()) {
        throw new Error("Chat response did not contain a reply");
      }

      addMessage(result.reply.trim(), "assistant");
      setConnection("সহায়তা সার্ভারে সংযোগ আছে", "online");
    } catch {
      input.value = text;
      setConnection(
        navigator.onLine
          ? "বার্তাটি পাঠানো যায়নি। একটু পরে আবার চেষ্টা করুন।"
          : "ইন্টারনেট সংযোগ নেই। সংযোগ ফিরে এলে আবার পাঠান।",
        "offline",
      );
    } finally {
      requestInFlight = false;
      sendButton.disabled = false;
      sendButton.removeAttribute("aria-busy");
      sendButton.setAttribute("aria-label", "বার্তা পাঠান");
      sendButton.innerHTML = sendIcon;
      input.focus();
    }
  }

  function openPanel() {
    panel.hidden = false;
    launcher.setAttribute("aria-expanded", "true");
    launcher.setAttribute("aria-label", `${brandName} chat বন্ধ করুন`);
    input.focus();
  }

  function closePanel() {
    panel.hidden = true;
    launcher.setAttribute("aria-expanded", "false");
    launcher.setAttribute("aria-label", `${brandName} chat খুলুন`);
    launcher.focus();
  }

  launcher.addEventListener("click", () => {
    if (panel.hidden) openPanel();
    else closePanel();
  });
  closeButton.addEventListener("click", closePanel);
  form.addEventListener("submit", sendMessage);

  shadow.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", () => {
      input.value = button.dataset.prompt || "";
      input.focus();
    });
  });

  shadow.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) closePanel();
  });
  window.addEventListener("online", checkConnection);
  window.addEventListener("offline", () => setConnection("ইন্টারনেট সংযোগ নেই। আবার চেষ্টা করুন।", "offline"));
  const welcomeTime = shadow.querySelector(".message--assistant .time");
  welcomeTime.dateTime = new Date().toISOString();
  welcomeTime.textContent = new Intl.DateTimeFormat("bn-BD", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date());

  async function executeActiveRules() {
    if (!apiBaseUrl) return;
    try {
      const response = await fetchWithTimeout(`${apiBaseUrl}/api/rules/active`, { method: "GET" }, 4000);
      if (!response.ok) return;
      const result = await response.json();
      const rules = Array.isArray(result.rules) ? result.rules : [];
      let processed = {};
      try {
        processed = JSON.parse(window.localStorage.getItem(processedRulesKey) || "{}");
      } catch {
        processed = {};
      }

      [...rules]
        .sort((left, right) => Number(left.priority || 0) - Number(right.priority || 0))
        .forEach((rule) => {
          const ruleId = String(rule.id);
          if (rule.execution_frequency === "once_per_session" && processed[ruleId]) return;

          const config = rule.trigger_config && typeof rule.trigger_config === "object"
            ? rule.trigger_config
            : {};
          let matches = false;
          if (rule.trigger_event === "on_first_visit") {
            matches = true;
          } else if (rule.trigger_event === "url_match") {
            const urlPattern = String(config.url_match || config.url || "");
            matches = Boolean(urlPattern) && window.location.pathname.includes(urlPattern);
          } else if (rule.trigger_event === "time_on_page") {
            const delaySeconds = Math.max(0, Number(config.delay_seconds || 0));
            window.setTimeout(() => executeRule(rule, processed, ruleId), delaySeconds * 1000);
            return;
          }
          if (matches) executeRule(rule, processed, ruleId);
        });
    } catch {
      setConnection("অ্যাক্টিভ রুল লোড করা যায়নি।", "offline");
    }
  }

  function executeRule(rule, processed, ruleId) {
    if (rule.execution_frequency === "once_per_session" && processed[ruleId]) return;
    if (rule.action_type === "Static Message" && rule.static_message) {
      addMessage(rule.static_message, "assistant");
      openPanel();
    } else if (rule.action_type === "AI Persona") {
      personaRole = rule.assigned_role || null;
      openPanel();
    }
    processed[ruleId] = true;
    try {
      window.localStorage.setItem(processedRulesKey, JSON.stringify(processed));
    } catch {
      // The widget remains usable when localStorage is unavailable.
    }
  }

  executeActiveRules();

  checkConnection();
})();
