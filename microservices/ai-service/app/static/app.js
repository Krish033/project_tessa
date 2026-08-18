document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const messagesContainer = document.getElementById("messages-container");
  const welcomeScreen = document.getElementById("welcome-screen");
  const statusDot = document.getElementById("status-dot");

  const statusText = document.getElementById("status-text");
  const modelName = document.getElementById("model-name");
  const clearBtn = document.getElementById("clear-btn");
  const newChatBtn = document.getElementById("new-chat-btn");
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebar = document.getElementById("sidebar");
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  const chatHistoryList = document.getElementById("chat-history-list");
  const promptCards = document.querySelectorAll(".prompt-card");

  let isGenerating = false;
  let conversations = [];
  let activeConvId = null;

  // Initialize Marked
  if (window.marked) {
    marked.setOptions({
      highlight: function (code, lang) {
        if (window.hljs && hljs.getLanguage(lang)) {
          return hljs.highlight(code, { language: lang }).value;
        }
        return code;
      },
      breaks: true,
    });
  }

  // Load conversations state from LocalStorage
  function loadLocalState() {
    try {
      const saved = localStorage.getItem("tessa_conversations");
      if (saved) {
        conversations = JSON.parse(saved);
      }
    } catch (e) {
      conversations = [];
    }

    if (!conversations || conversations.length === 0) {
      const initialConv = {
        id: "conv-" + Date.now(),
        title: "New Chat",
        messages: [],
      };
      conversations = [initialConv];
    }

    activeConvId = conversations[0].id;
    saveLocalState();
    renderSidebarChats();
    loadActiveConversation();
  }

  function saveLocalState() {
    try {
      localStorage.setItem("tessa_conversations", JSON.stringify(conversations));
    } catch (e) {
      console.error("Could not save to LocalStorage:", e);
    }
  }

  function getActiveConv() {
    return conversations.find((c) => c.id === activeConvId) || conversations[0];
  }

  // Render Sidebar Conversation List
  function renderSidebarChats() {
    chatHistoryList.innerHTML = "";
    conversations.forEach((conv) => {
      const li = document.createElement("li");
      li.className = `chat-history-item ${conv.id === activeConvId ? "active" : ""}`;
      li.innerHTML = `
        <div class="chat-title-group">
          <i class="fa-regular fa-message"></i>
          <span>${escapeHtml(conv.title)}</span>
        </div>
        <button class="delete-chat-btn" title="Delete conversation">
          <i class="fa-solid fa-xmark"></i>
        </button>
      `;

      // Switch conversation
      li.querySelector(".chat-title-group").addEventListener("click", () => {
        if (conv.id !== activeConvId && !isGenerating) {
          activeConvId = conv.id;
          saveLocalState();
          renderSidebarChats();
          loadActiveConversation();
        }
      });

      // Delete conversation
      li.querySelector(".delete-chat-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        if (isGenerating) return;
        deleteConversation(conv.id);
      });

      chatHistoryList.appendChild(li);
    });
  }

  // Delete Conversation
  async function deleteConversation(id) {
    conversations = conversations.filter((c) => c.id !== id);
    if (conversations.length === 0) {
      const newConv = {
        id: "conv-" + Date.now(),
        title: "New Chat",
        messages: [],
      };
      conversations = [newConv];
    }
    if (activeConvId === id) {
      activeConvId = conversations[0].id;
    }
    saveLocalState();
    renderSidebarChats();
    loadActiveConversation();
    await fetch("/api/chat/reset", { method: "POST" });
  }

  // Create New Chat
  async function createNewChat() {
    if (isGenerating) return;
    const newConv = {
      id: "conv-" + Date.now(),
      title: "New Chat",
      messages: [],
    };
    conversations.unshift(newConv);
    activeConvId = newConv.id;
    saveLocalState();
    renderSidebarChats();
    loadActiveConversation();
    await fetch("/api/chat/reset", { method: "POST" });
  }

  newChatBtn.addEventListener("click", createNewChat);

  // Helper for formatting timestamp
  function formatTimestamp(timestampStr) {
    const d = timestampStr ? new Date(timestampStr) : new Date();
    if (isNaN(d.getTime())) return "";
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    });
  }

  // Load Active Conversation View
  function loadActiveConversation() {
    const conv = getActiveConv();
    messagesContainer.innerHTML = "";

    if (!conv.messages || conv.messages.length === 0) {
      welcomeScreen.style.display = "flex";
    } else {
      welcomeScreen.style.display = "none";
      conv.messages.forEach((msg) => {
        if (msg.role === "user") {
          appendUserMessage(msg.text, false, msg.timestamp);
        } else if (msg.role === "assistant") {
          renderSavedAgentMessage(msg);
        }
      });
    }
    scrollToBottom();
  }

  function getOrCreateToolContainer(responseArea, contentElement) {
    let container = responseArea.querySelector(".tool-pills-container");
    if (!container) {
      container = document.createElement("div");
      container.className = "tool-pills-container";
      responseArea.insertBefore(container, contentElement);
    }
    return container;
  }

  function renderSavedAgentMessage(msg) {
    const { responseArea, reasoningBody, reasoningBox, rawBox, rawBody, contentElement } = appendAgentMessageSkeleton(msg.timestamp);
    if (msg.rawResponse) {
      rawBox.style.display = "block";
      const codeElem = rawBody.querySelector("code");
      codeElem.textContent = msg.rawResponse;
      if (window.hljs) hljs.highlightElement(codeElem);
    }
    if (msg.reasoning) {
      reasoningBox.style.display = "block";
      reasoningBody.textContent = msg.reasoning;
    }
    if (msg.tools && msg.tools.length > 0) {
      const container = getOrCreateToolContainer(responseArea, contentElement);
      msg.tools.forEach((t) => {
        const pill = document.createElement("div");
        pill.className = "tool-pill completed";
        pill.innerHTML = `
          <i class="fa-solid fa-check"></i>
          <span>${escapeHtml(t)}</span>
        `;
        container.appendChild(pill);
      });
    }
    renderMarkdown(contentElement, msg.content || "");
  }

  // Textarea auto-resize
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 180) + "px";

    if (userInput.value.trim().length > 0) {
      sendBtn.classList.add("active");
      sendBtn.disabled = false;
    } else {
      sendBtn.classList.remove("active");
      sendBtn.disabled = true;
    }
  });

  // Enter to send
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled && !isGenerating) {
        sendMessage();
      }
    }
  });

  // Prompt card clicks
  promptCards.forEach((card) => {
    card.addEventListener("click", () => {
      const prompt = card.getAttribute("data-prompt");
      if (prompt) {
        userInput.value = prompt;
        userInput.dispatchEvent(new Event("input"));
        sendMessage();
      }
    });
  });

  sendBtn.addEventListener("click", () => {
    if (!sendBtn.disabled && !isGenerating) {
      sendMessage();
    }
  });

  if (clearBtn) {
    clearBtn.addEventListener("click", async () => {
      const conv = getActiveConv();
      conv.messages = [];
      saveLocalState();
      loadActiveConversation();
      await fetch("/api/chat/reset", { method: "POST" });
    });
  }

  // Sidebar Toggles
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  mobileMenuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("mobile-open");
  });

  // Load Health Status
  async function loadBackendInfo() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      if (data.status === "healthy") {
        if (statusDot) statusDot.classList.add("online");
        if (statusText) statusText.textContent = "SYSTEM READY";
      } else {
        if (statusDot) statusDot.classList.remove("online");
        if (statusText) statusText.textContent = "OFFLINE";
      }
      if (data.model && modelName) {
        modelName.textContent = data.model;
      }
    } catch (err) {
      if (statusDot) statusDot.classList.remove("online");
      if (statusText) statusText.textContent = "OFFLINE";
    }
  }

  // Send Message Logic
  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text || isGenerating) return;

    isGenerating = true;
    welcomeScreen.style.display = "none";

    const conv = getActiveConv();
    const userTimestamp = new Date().toISOString();

    // Auto title if first message
    if (conv.messages.length === 0 && conv.title === "New Chat") {
      conv.title = text.length > 26 ? text.substring(0, 26) + "..." : text;
      saveLocalState();
      renderSidebarChats();
    }

    // Record user message
    conv.messages.push({ role: "user", text: text, timestamp: userTimestamp });
    saveLocalState();
    appendUserMessage(text, false, userTimestamp);

    // Reset input
    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.classList.remove("active");
    sendBtn.disabled = true;

    // Create Agent Skeleton
    const agentTimestamp = new Date().toISOString();
    const { responseArea, reasoningBody, reasoningBox, rawBox, rawBody, contentElement } = appendAgentMessageSkeleton(agentTimestamp);

    let fullContent = "";
    let fullReasoning = "";
    let fullRawResponse = "";
    let executedTools = [];

    try {
      const response = await fetch(`/api/chat/stream?prompt=${encodeURIComponent(text)}`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataJson = line.substring(6).trim();
            if (!dataJson) continue;

            try {
              const event = JSON.parse(dataJson);

              if (event.type === "raw_response") {
                fullRawResponse = event.raw || "";
                rawBox.style.display = "block";
                const codeElem = rawBody.querySelector("code");
                codeElem.textContent = fullRawResponse;
                if (window.hljs) hljs.highlightElement(codeElem);
              } else if (event.type === "reasoning") {
                fullReasoning += event.chunk || "";
                reasoningBox.style.display = "block";
                reasoningBox.classList.add("streaming");
                reasoningBody.style.display = "block";
                reasoningBox.classList.add("open");
                const headerSpan = reasoningBox.querySelector(".reasoning-header span");
                if (headerSpan) headerSpan.textContent = "Thinking...";
                reasoningBody.textContent = fullReasoning;
                reasoningBody.scrollTop = reasoningBody.scrollHeight;
              } else if (event.type === "tool_start") {
                reasoningBox.classList.remove("streaming");
                const headerSpan = reasoningBox.querySelector(".reasoning-header span");
                if (headerSpan) headerSpan.textContent = "Thinking";
                fullContent = "";
                contentElement.innerHTML = "";
                executedTools.push(event.tool);
                const container = getOrCreateToolContainer(responseArea, contentElement);
                const pill = document.createElement("div");
                pill.className = "tool-pill";
                pill.id = `tool-${event.tool}`;
                pill.innerHTML = `
                  <i class="fa-solid fa-spinner tool-spinner"></i>
                  <span>${escapeHtml(event.tool)}</span>
                `;
                container.appendChild(pill);
              } else if (event.type === "tool_result") {
                const pill = responseArea.querySelector(`#tool-${event.tool}`);
                if (pill) {
                  pill.classList.add("completed");
                  pill.innerHTML = `
                    <i class="fa-solid fa-check"></i>
                    <span>${escapeHtml(event.tool)}</span>
                  `;
                }
              } else if (event.type === "content") {
                reasoningBox.classList.remove("streaming");
                const headerSpan = reasoningBox.querySelector(".reasoning-header span");
                if (headerSpan) headerSpan.textContent = "Thinking";
                fullContent += event.chunk || "";
                const cleaned = cleanMarkdownText(fullContent);
                if (cleaned) {
                  renderMarkdown(contentElement, cleaned);
                }
              } else if (event.type === "final") {
                reasoningBox.classList.remove("streaming");
                const headerSpan = reasoningBox.querySelector(".reasoning-header span");
                if (headerSpan) headerSpan.textContent = "Thinking";
                if (event.raw) {
                  fullRawResponse = event.raw;
                  rawBox.style.display = "block";
                  const codeElem = rawBody.querySelector("code");
                  codeElem.textContent = fullRawResponse;
                  if (window.hljs) hljs.highlightElement(codeElem);
                }
                if (event.answer) {
                  fullContent = event.answer;
                  renderMarkdown(contentElement, cleanMarkdownText(fullContent));
                }
              } else if (event.type === "error") {
                contentElement.innerHTML += `<div style="color: #ff5555; margin-top: 6px;"><i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(event.message)}</div>`;
              }
            } catch (jsonErr) {
              console.error("JSON parse error:", jsonErr);
            }
          }
        }
      }
    } catch (err) {
      contentElement.innerHTML += `<div style="color: #ff5555;">Error: ${escapeHtml(err.message)}</div>`;
    } finally {
      isGenerating = false;
      reasoningBox.classList.remove("streaming");
      const headerSpan = reasoningBox.querySelector(".reasoning-header span");
      if (headerSpan) headerSpan.textContent = "Thinking";

      // Save assistant message to session history
      conv.messages.push({
        role: "assistant",
        content: cleanMarkdownText(fullContent),
        reasoning: fullReasoning,
        rawResponse: fullRawResponse,
        tools: executedTools,
        timestamp: agentTimestamp,
      });
      saveLocalState();
      scrollToBottom();
    }
  }

  function appendUserMessage(text, scroll = true, timestampStr = null) {
    const formattedTime = formatTimestamp(timestampStr);
    const row = document.createElement("div");
    row.className = "message-row user-row";
    row.innerHTML = `
      <div class="message-content-wrapper">
        <div class="user-bubble">${escapeHtml(text)}</div>
        <div class="message-timestamp user-time">${escapeHtml(formattedTime)}</div>
      </div>
    `;
    messagesContainer.appendChild(row);
    if (scroll) scrollToBottom();
  }

  function appendAgentMessageSkeleton(timestampStr = null) {
    const formattedTime = formatTimestamp(timestampStr);
    const row = document.createElement("div");
    row.className = "message-row agent-row";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar agent-avatar-msg";
    avatar.innerHTML = `<i class="fa-solid fa-sparkles"></i>`;

    const wrapper = document.createElement("div");
    wrapper.className = "message-content-wrapper";

    const responseArea = document.createElement("div");
    responseArea.className = "agent-response-area";

    // Raw Model Response Box with minimal chevron trigger
    const rawBox = document.createElement("div");
    rawBox.className = "raw-response-box";
    rawBox.style.display = "none";
    rawBox.innerHTML = `
      <div class="raw-response-header">
        <i class="fa-solid fa-chevron-right chevron-icon"></i>
        <span>Raw output</span>
      </div>
      <div class="raw-response-body" style="display: none;">
        <pre><code class="language-json"></code></pre>
      </div>
    `;

    const rawHeader = rawBox.querySelector(".raw-response-header");
    const rawBody = rawBox.querySelector(".raw-response-body");
    rawHeader.addEventListener("click", () => {
      const isOpen = rawBody.style.display !== "none";
      rawBody.style.display = isOpen ? "none" : "block";
      rawBox.classList.toggle("open", !isOpen);
    });

    // Reasoning Box with minimal chevron trigger
    const reasoningBox = document.createElement("div");
    reasoningBox.className = "reasoning-box";
    reasoningBox.style.display = "none";
    reasoningBox.innerHTML = `
      <div class="reasoning-header">
        <i class="fa-solid fa-chevron-right chevron-icon"></i>
        <span>Thinking</span>
      </div>
      <div class="reasoning-body" style="display: none;"></div>
    `;

    const reasoningHeader = reasoningBox.querySelector(".reasoning-header");
    const reasoningBody = reasoningBox.querySelector(".reasoning-body");
    reasoningHeader.addEventListener("click", () => {
      const isOpen = reasoningBody.style.display !== "none";
      reasoningBody.style.display = isOpen ? "none" : "block";
      reasoningBox.classList.toggle("open", !isOpen);
    });

    const contentElement = document.createElement("div");
    contentElement.className = "markdown-body";

    const timestampElement = document.createElement("div");
    timestampElement.className = "message-timestamp agent-time";
    timestampElement.textContent = formattedTime;

    responseArea.appendChild(rawBox);
    responseArea.appendChild(reasoningBox);
    responseArea.appendChild(contentElement);
    wrapper.appendChild(responseArea);
    wrapper.appendChild(timestampElement);
    row.appendChild(avatar);
    row.appendChild(wrapper);

    messagesContainer.appendChild(row);
    scrollToBottom();

    return { responseArea, reasoningBox, reasoningBody, rawBox, rawBody, contentElement, timestampElement };
  }

  // String unescaping and sanitization helper
  function cleanMarkdownText(str) {
    if (!str) return "";
    let text = str.trim();

    // Handle JSON answer object structure during streaming
    if (text.startsWith("{") && (text.includes('"answer"') || text.includes('"action"'))) {
      try {
        const parsed = JSON.parse(text);
        if (parsed.answer) {
          text = parsed.answer;
        } else if (parsed.action) {
          return "";
        }
      } catch (e) {
        // Regex extraction for incremental streaming
        const match = text.match(/"answer"\s*:\s*"([\s\S]*?)"?\s*\}?\s*$/);
        if (match && match[1]) {
          text = match[1];
        } else {
          return "";
        }
      }
    }

    if (text.includes("\\n")) text = text.replace(/\\n/g, "\n");
    if (text.includes("\\t")) text = text.replace(/\\t/g, "\t");
    if (text.includes('\\"')) text = text.replace(/\\"/g, '"');

    text = text.trim();
    if (text.startsWith('"') && text.endsWith('"') && text.length > 2) {
      text = text.slice(1, -1);
    }

    return text;
  }


  function renderMarkdown(element, content) {
    const cleaned = cleanMarkdownText(content);
    if (window.marked) {
      element.innerHTML = marked.parse(cleaned);
      element.querySelectorAll("pre code").forEach((block) => {
        if (window.hljs) hljs.highlightElement(block);
      });
    } else {
      element.textContent = cleaned;
    }
    scrollToBottom();
  }

  function scrollToBottom() {
    const chatView = document.getElementById("chat-view");
    chatView.scrollTop = chatView.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Initialize Local State and Load Backend
  loadLocalState();
  loadBackendInfo();
});
